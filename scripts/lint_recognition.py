#!/usr/bin/env python3
"""lint_recognition.py

Cross-surface recognition lint. Keeps the homepage "Service and
Recognition" section (index.html #service) aligned with the
comprehensive record in the CV (src/content/cv.md), WITHOUT a shared
data file. Both surfaces stay hand-authored; this script parses both
and compares them.

Two surfaces, three CV sections reconciled:

  homepage  index.html  <section id="service"> .row-entry blocks
  CV        cv.md       ## Awards and Honors
                        ### Fellowships and Training  (under ## Education)
                        ## Service and Professional Activities (all ###)

Two outputs:

  1. SUBSET GATE (hard fail, blocks push): every entry shown in the
     homepage #service section must have a counterpart somewhere in the
     CV's awards / fellowships / service record. The homepage is a
     curated highlight reel, so it is allowed to show FEWER items than
     the CV, but it must not show anything the comprehensive CV omits.
     A failure here means the two surfaces have drifted (an award shown
     publicly with no CV record, or a renamed entry that no longer
     matches).

  2. COVERAGE REPORT (informational, never fails): CV recognition
     entries with no homepage counterpart, so genuine gaps surface as a
     reminder. This is the check that would have caught the Digital
     Fellow / IPM award gaps. Most CV-only items (training short
     courses, individual mentees, minor service) are EXPECTED to stay
     CV-only; the report is an advisory list to scan, not a to-do.

Matching: unlike lint_facts.py (which demands strict equality between
surfaces authored in lockstep), the recognition surfaces are phrased
independently -- the CV says "Undergraduate Research Scholar Mentor"
where the homepage says "Undergraduate Research Mentor", "Institute of
Industrial and Systems Engineers ..." where the homepage says "IISE
...". So an entry matches a CV entry when they share at least one year
AND at least two significant tokens (stopwords, short tokens, and bare
years dropped). This tolerates wording differences without a
hand-maintained synonym table, while still being specific enough that
unrelated same-year entries do not collide.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from _common import (
    ROW_DATE_RE,
    ROW_ENTRY_RE,
    ROW_ORG_RE,
    ROW_TITLE_RE,
    alignment_match,
    install_git_hooks,
    row_field,
    years_of,
)
from _common import tokens_of as _tokens_of

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
CV = ROOT / "src" / "content" / "cv.md"
INDEX = ROOT / "index.html"

MIN_SHARED_TOKENS = 2

# Stopwords + common geography that would otherwise let two unrelated
# same-year entries share tokens. Kept deliberately small; the year +
# two-token rule does most of the work.
STOP = {
    "of", "and", "the", "for", "at", "in", "to", "a", "an", "on", "by",
    "with", "from", "as", "two", "terms", "elected", "raised", "early",
    "madison", "chicago", "illinois", "heber", "city", "wi", "il", "ut",
    "utah", "north", "america",
    # Generic institutional / academic words: too common to be
    # distinguishing on their own (otherwise two unrelated same-year
    # entries collide on e.g. "medicine"+"health"). The distinguishing
    # tokens for real matches live in the title proper.
    "university", "school", "medicine", "health", "public", "research",
    "department", "community", "institute", "center", "program",
    "national", "college", "course", "training", "short",
}


def normalize(s: str) -> str:
    return (s.replace("&amp;", "&")
             .replace("&middot;", " ")
             .replace("&#8211;", "-")
             .replace("&#8212;", "-")
             .replace("&nbsp;", " "))


def tokens_of(s: str) -> set[str]:
    """Significant tokens in `s`, via _common with this lint's STOP + normalize."""
    return _tokens_of(s, STOP, normalize=normalize)


@dataclass(frozen=True)
class Entry:
    label: str          # human-readable, for messages
    years: frozenset[int]
    tokens: frozenset[str]
    source: str         # "index.html:NNN" or "cv.md:NNN §Section"

    def matches(self, other: "Entry") -> bool:
        return alignment_match(self.years, self.tokens,
                               other.years, other.tokens,
                               min_shared=MIN_SHARED_TOKENS)


# ─── homepage parser ──────────────────────────────────────────────────────
# The .row-entry field regexes + row_field come from _common (shared with
# lint_gantt); only the #service section slice is local here.

SERVICE_SECTION_RE = re.compile(
    r'<section id="service">(?P<body>.*?)</section>', re.DOTALL
)


def parse_homepage(text: str) -> list[Entry]:
    sec = SERVICE_SECTION_RE.search(text)
    if not sec:
        return []
    base = sec.start("body")
    entries: list[Entry] = []
    for m in ROW_ENTRY_RE.finditer(sec.group("body")):
        row = m.group("row")
        date = row_field(ROW_DATE_RE, row)
        title = row_field(ROW_TITLE_RE, row)
        org = row_field(ROW_ORG_RE, row)
        if not title:
            continue
        line = text.count("\n", 0, base + m.start()) + 1
        entries.append(Entry(
            label=f"{normalize(title).strip()} ({normalize(date).strip()})",
            years=frozenset(years_of(date)),
            # Match on title + org only; the optional row-note is descriptive
            # prose and would add spurious token overlap.
            tokens=frozenset(tokens_of(f"{title} {org}")),
            source=f"index.html:{line}",
        ))
    return entries


# ─── CV parser ────────────────────────────────────────────────────────────

# A list item in any of the reconciled CV sections:
#   - **2016–2020** Body text. Org, City.
CV_ITEM_RE = re.compile(
    r"^-\s+\*\*(?P<range>[^*]+)\*\*\s+(?P<body>.+?)\s*$", re.MULTILINE
)


def _section_body(text: str, heading_pattern: str) -> tuple[str, int] | None:
    """Return (body, char_offset) for a `## Heading` (or `### Heading`)
    section, sliced to the next heading of equal-or-higher level."""
    m = re.search(heading_pattern, text, re.MULTILINE)
    if not m:
        return None
    level = len(m.group("hashes"))
    # Stop at the next heading whose level is <= this one.
    rest = text[m.end():]
    stop = re.search(rf"^#{{1,{level}}}\s", rest, re.MULTILINE)
    body = rest[: stop.start()] if stop else rest
    return body, m.end()


def _parse_cv_section(text: str, body: str, base: int, section: str) -> list[Entry]:
    entries: list[Entry] = []
    for m in CV_ITEM_RE.finditer(body):
        rng = m.group("range").strip()
        bod = m.group("body").strip()
        line = text.count("\n", 0, base + m.start()) + 1
        # Readable label: first sentence, but fall back to the first
        # several words when the leading "sentence" is just an initial
        # (e.g. CV mentee lines begin "G. Padgett. ...").
        first = re.split(r"\.\s", bod, maxsplit=1)[0].strip().rstrip(".")
        if len(first.split()) < 3:
            first = " ".join(bod.split()[:8]).rstrip(".,;")
        entries.append(Entry(
            label=f"{first} ({rng})",
            years=frozenset(years_of(rng)),
            tokens=frozenset(tokens_of(bod)),
            source=f"cv.md:{line} §{section}",
        ))
    return entries


def parse_cv(text: str) -> list[Entry]:
    entries: list[Entry] = []
    sections = [
        (r"^(?P<hashes>##)\s+Awards and Honors\s*$", "Awards and Honors"),
        (r"^(?P<hashes>###)\s+Fellowships and Training\s*$", "Fellowships and Training"),
        (r"^(?P<hashes>##)\s+Service and Professional Activities\s*$",
         "Service and Professional Activities"),
    ]
    for pat, name in sections:
        found = _section_body(text, pat)
        if not found:
            continue
        body, base = found
        entries += _parse_cv_section(text, body, base, name)
    return entries


# ─── checks ───────────────────────────────────────────────────────────────

def run() -> int:
    if not INDEX.exists():
        print(f"error: {INDEX} not found", file=sys.stderr)
        return 1
    index_text = INDEX.read_text(encoding="utf-8")
    home = parse_homepage(index_text)

    if not CV.exists():
        print("recognition lint: cv.md absent; nothing to reconcile")
        return 0
    cv_text = CV.read_text(encoding="utf-8")
    cv = parse_cv(cv_text)

    if not home:
        print('error: no .row-entry blocks parsed from index.html '
              '<section id="service">', file=sys.stderr)
        return 1
    if not cv:
        print("error: no entries parsed from cv.md recognition sections",
              file=sys.stderr)
        return 1

    # ── Gate: every homepage entry must have a CV counterpart ──
    failures: list[str] = []
    for h in home:
        if not any(h.matches(c) for c in cv):
            failures.append(
                f"{h.source}: homepage Service/Recognition entry "
                f"\"{h.label}\" has no counterpart in cv.md "
                f"(Awards / Fellowships / Service). Add it to the CV, or "
                f"reconcile the wording/year so the surfaces agree."
            )

    # ── Coverage report: CV entries not surfaced on the homepage ──
    uncovered = [c for c in cv if not any(c.matches(h) for h in home)]

    if failures:
        print("Recognition lint found drift:\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(f"\n{len(failures)} homepage entry(ies) missing from cv.md.",
              file=sys.stderr)
        return 1

    print(f"recognition lint: {len(home)} homepage entry(ies) reconciled "
          f"against {len(cv)} cv.md entry(ies); "
          f"{len(uncovered)} cv.md item(s) not on homepage")
    if uncovered:
        print("  (informational; most are expected to stay CV-only -- "
              "training, individual mentees, minor service)")
        for c in uncovered:
            print(f"    - {c.label}  [{c.source}]")
    return 0


if __name__ == "__main__":
    sys.exit(run())
