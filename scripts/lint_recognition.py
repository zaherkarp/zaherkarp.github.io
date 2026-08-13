#!/usr/bin/env python3
"""lint_recognition.py

Cross-surface recognition lint. Keeps what the homepage SHOWS of the
awards / fellowships / service record aligned with the comprehensive
record in the CV (src/content/cv.md), WITHOUT a shared data file. Both
surfaces stay hand-authored; this script parses both and compares them.

WHAT THIS USED TO READ, AND WHY IT MOVED. Until 2026-08-13 the homepage
surface was `<section id="service">`, a list of .row-entry blocks. That
section was commented out on 2026-07-30, and this lint went on reading
it THROUGH the comment because its slicer matched raw text. The section
was DELETED on 2026-08-13, which retired that trick along with the
markup. The homepage's remaining view into this record is the SERVICE
LANE of the Education + Service Gantt figure, so that is what this lint
now reads. The guarantee is unchanged in direction and meaning:

  BEFORE  every #service entry needs a CV record
  AFTER   every service-lane Gantt mark needs a CV record

Two surfaces, three CV sections reconciled:

  homepage  index.html  figure.gantt-figure, service lane (y > 135)
  CV        cv.md       ## Awards and Honors
                        ### Fellowships and Training  (under ## Education)
                        ## Service and Professional Activities (all ###)

Two outputs:

  1. SUBSET GATE (hard fail, blocks push): every service-lane mark must
     have a counterpart somewhere in the CV's awards / fellowships /
     service record. The homepage is a curated highlight reel, so it is
     allowed to show FEWER items than the CV, but it must not show
     anything the comprehensive CV omits. A failure here means the two
     surfaces have drifted (something shown publicly with no CV record,
     or a renamed entry that no longer matches).

  2. COVERAGE REPORT (informational, never fails): CV recognition
     entries with no homepage counterpart, so genuine gaps surface as a
     reminder. This is the check that would have caught the Digital
     Fellow / IPM award gaps. Most CV-only items (training short
     courses, individual mentees, minor service) are EXPECTED to stay
     CV-only; the report is an advisory list to scan, not a to-do.

RELATIONSHIP TO lint_gantt.py, which now also reads this figure against
this CV. The overlap is deliberate, and the two are not redundant. That
lint checks EVERY mark, in both lanes, against the whole Education /
Service / Awards record, and its job is that the chart's geometry
decodes to years the CV agrees with. This one checks the SERVICE lane
against the RECOGNITION sections specifically, so a service mark backed
only by, say, a degree in `## Education` fails here while passing there.
It also owns the recognition-side coverage report. If the two ever have
to be merged, the property to preserve is that tighter scoping.

Matching: unlike lint_facts.py (which demands strict equality between
surfaces authored in lockstep), these surfaces are phrased
independently -- the CV says "Undergraduate Research Scholar Mentor"
where the chart says "UG research mentor". So an entry matches when
they share at least one year AND at least two significant tokens
(stopwords, short tokens, and bare years dropped). This tolerates
wording differences without a hand-maintained synonym table, while
still being specific enough that unrelated same-year entries do not
collide.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from _common import (
    alignment_match,
    cv_items,
    gantt_marks,
    install_git_hooks,
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
#
# This list SHRANK on 2026-08-13, and the old "do not share the two
# stoplists" note against lint_gantt is retired with it. The aggressive
# version below dropped generic institutional words ("university", "health",
# "research", ...) because it compared two VERBOSE surfaces -- a homepage
# .row-entry against a CV line -- where those words were noise that let
# unrelated same-year entries collide. The homepage surface is now the Gantt's
# terse chart labels, so those words are no longer noise but the entire
# signal: dropping "research" makes "UG research mentor" share nothing with
# "Undergraduate Research Scholar Mentor". The two lints therefore read the
# same kind of label and now carry the same minimal stoplist. Verified by
# removing them and watching the service lane go from 2 unmatched marks to 0.
STOP = {
    "of", "and", "the", "for", "at", "in", "to", "a", "an", "on", "by",
    "with", "from", "as", "two", "terms", "elected", "raised", "early",
    "ongoing", "madison", "chicago", "illinois", "heber", "city", "wi",
    "il", "ut", "utah", "north", "america",
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
# The Gantt SVG slicing and the x-to-year decode come from _common (shared
# with lint_gantt); this lint keeps only the SERVICE lane, which is the
# homepage's remaining view into the awards / fellowships / service record.


def parse_homepage(text: str) -> list[Entry]:
    return [
        Entry(
            label=normalize(mk.label).strip(),
            years=mk.years,
            tokens=frozenset(tokens_of(mk.label)),
            source=f"index.html:{mk.line}",
        )
        for mk in gantt_marks(text)
        if mk.lane == "service"
    ]


# ─── CV parser ────────────────────────────────────────────────────────────
# cv.md list-item slicing comes from _common (shared with lint_gantt). The
# three sections here are the RECOGNITION record specifically, which is what
# scopes this lint more tightly than its sibling; see the module docstring.

CV_SECTIONS = (
    (r"^(?P<hashes>##)\s+Awards and Honors\s*$", "Awards and Honors"),
    (r"^(?P<hashes>###)\s+Fellowships and Training\s*$", "Fellowships and Training"),
    (r"^(?P<hashes>##)\s+Service and Professional Activities\s*$",
     "Service and Professional Activities"),
)


def parse_cv(text: str) -> list[Entry]:
    entries: list[Entry] = []
    for pattern, name in CV_SECTIONS:
        for it in cv_items(text, pattern, name):
            # Readable label: first sentence, but fall back to the first
            # several words when the leading "sentence" is just an initial
            # (e.g. CV mentee lines begin "G. Padgett. ...").
            first = re.split(r"\.\s", it.body, maxsplit=1)[0].strip().rstrip(".")
            if len(first.split()) < 3:
                first = " ".join(it.body.split()[:8]).rstrip(".,;")
            entries.append(Entry(
                label=f"{first} ({it.range})",
                years=frozenset(years_of(it.range)),
                # The subsection heading joins the body: the `### Peer Review`
                # entries name journals and never state the role, so the body
                # alone shares nothing with a "peer reviewer" chart label.
                tokens=frozenset(tokens_of(f"{it.body} {it.section}")),
                source=f"cv.md:{it.line} §{it.section}",
            ))
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
        print("error: no service-lane marks parsed from index.html "
              "figure.gantt-figure", file=sys.stderr)
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
