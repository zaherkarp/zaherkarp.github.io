#!/usr/bin/env python3
"""lint_gantt.py

Keeps the homepage Education + Service Gantt figure
(index.html `figure.gantt-figure`) in lockstep with the comprehensive
record in the CV (src/content/cv.md), WITHOUT a shared data file. The
figure is a hand-coded SVG; this script reads it and the CV and
compares.

WHAT THIS USED TO CHECK, AND WHY IT MOVED. Until 2026-08-13 this lint
compared the figure against two prose sections on the homepage,
`<section id="education">` and `<section id="service">`. Those sections
were commented out on 2026-07-30 (each judged redundant with this
figure once its terse labels absorbed every entry's title and date) and
the lint went on reading them THROUGH the comment, because its section
slicer matched raw text. They were DELETED on 2026-08-13, which retired
that trick along with the markup. cv.md is now the comprehensive record
and this figure is the page's only visible surface for it, so the
comparison is figure-against-CV and the gate direction flips to match:

  BEFORE  every section entry must have a mark   (section subset of figure)
  AFTER   every mark must have a CV counterpart  (figure subset of CV)

The new direction is the one that suits a curated chart. cv.md holds far
more than the chart shows (short courses, individual mentees, minor
service), and that is intended, so requiring a mark per CV entry would
fail permanently. Requiring a CV record per mark is the guarantee worth
keeping: nothing is displayed publicly that the comprehensive record
does not support. The reverse direction survives as the informational
coverage report, which is where a newly added CV award shows up as a
candidate for the chart.

Each data mark encodes its year(s) positionally, via the chart's own
coordinate transform x(year) = GANTT_X0 + (year - GANTT_BASE_YEAR) *
GANTT_PX_PER_YEAR (currently 180 + (year - 2003) * 38; the constants
live in _common.py and move with the chart):

  - a single-year credential is a <rect ... fill="#111"/> square; its
    year is read back from the square's centre x.
  - a multi-year range is a <line ... stroke-width="4"/> bar; its start
    and end years are read back from x1 and x2.

Each mark is paired with the <text> label that immediately follows it
in source. Reading the year back from the geometry is what makes this
more than a text diff: a mark drawn at the wrong x decodes to the wrong
year and stops matching its CV entry.

TWO SVG VARIANTS, ONE DECODED. Since 2026-08-15 the figure holds
svg.gantt-wide (desktop) and svg.gantt-narrow (<=760px), drawing the
same twelve marks on DIFFERENT transforms so each reads well at its own
size. _common.gantt_marks decodes only the wide one; running the
narrow one's 600-unit coordinates through the wide transform would
misdate every mark. That scoping would leave the narrow copy free to
drift, so variant_label_drift() below compares the two variants' label
sets and fails the gate when they disagree. Labels only: their
coordinate systems differ by design. Edit both variants or neither.

MATCHING IS LANE-AGNOSTIC, and that is deliberate. The figure splits
marks into an education lane and a service lane (either side of
GANTT_LANE_DIVIDER_Y),
but cv.md files things by a different taxonomy: "Digital Fellow" is
drawn in the SERVICE lane and recorded under `### Fellowships and
Training`, which is nested inside `## Education`. Constraining a mark to
its own lane's CV section would fail that pair for a disagreement about
filing, not about facts. The lane is still reported in messages.

GATE (hard fail, blocks push): every figure mark must have a counterpart
in cv.md's Education / Service / Awards record. "Matching" = share at
least one year AND at least two significant tokens, which tolerates the
figure's terse labels ("UG research mentor" vs the CV's "Undergraduate
Research Scholar Mentor") with no synonym table.

A reverse coverage note (cv.md entries with no mark) prints on a manual
run; it never fails.
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
INDEX = ROOT / "index.html"
CV = ROOT / "src" / "content" / "cv.md"

# The CV sections a Gantt mark may be backed by. Education carries the
# `### Fellowships and Training` subsection, which is where several
# service-lane marks are filed; see the lane-agnostic note in the docstring.
CV_SECTIONS = (
    (r"^(?P<hashes>##)\s+Education\s*$", "Education"),
    (r"^(?P<hashes>##)\s+Service and Professional Activities\s*$", "Service"),
    (r"^(?P<hashes>##)\s+Awards and Honors\s*$", "Awards and Honors"),
)

MIN_SHARED_TOKENS = 2

# Minimal stoplist: the figure labels are terse, so unlike
# lint_recognition.py this does NOT drop institutional words (it must
# keep "research" so "UG research mentor" still matches "Undergraduate
# Research Mentor"). Just articles, prepositions, the "(ongoing)" tag,
# and a little geography.
STOP = {
    "of", "and", "the", "for", "at", "in", "to", "a", "an", "on", "by",
    "with", "from", "as", "two", "terms", "elected", "raised", "ongoing",
    "madison", "chicago", "wi",
}


def normalize(s: str) -> str:
    return (s.replace("&amp;", "&")
             .replace("&middot;", " ")
             .replace("&ndash;", "-")
             .replace("&#8211;", "-")
             .replace("&#8212;", "-"))


def tokens_of(s: str) -> frozenset[str]:
    """Significant tokens in `s`, via _common with this lint's STOP + normalize."""
    return frozenset(_tokens_of(s, STOP, normalize=normalize))


def years_in(s: str) -> frozenset[int]:
    return frozenset(years_of(s))


@dataclass(frozen=True)
class Item:
    label: str
    lane: str                 # "education" | "service"
    years: frozenset[int]
    tokens: frozenset[str]
    source: str

    def matches(self, other: "Item") -> bool:
        # Lanes are compared only when BOTH sides are figure marks. A CV entry
        # carries lane="cv" because cv.md's filing does not track the chart's
        # two-lane split; see the lane-agnostic note in the module docstring.
        if "cv" not in (self.lane, other.lane) and self.lane != other.lane:
            return False
        return alignment_match(self.years, self.tokens,
                               other.years, other.tokens,
                               min_shared=MIN_SHARED_TOKENS)


# ─── figure parser ────────────────────────────────────────────────────────
# The SVG slicing and the x-to-year decode live in _common (shared with
# lint_recognition, which reconciles the service lane against the CV's
# recognition record); only the tokenizing is gantt-local.


def parse_figure(text: str) -> list[Item]:
    return [
        Item(
            label=normalize(mk.label).strip(),
            lane=mk.lane,
            years=mk.years,
            tokens=tokens_of(normalize(mk.label)),
            source=f"index.html:{mk.line}",
        )
        for mk in gantt_marks(text)
    ]


# ─── CV parser ────────────────────────────────────────────────────────────
# cv.md list-item slicing comes from _common (shared with lint_recognition);
# the tokenizing below is gantt-local, because this lint compares against the
# figure's terse labels and so keeps institutional words its sibling drops.


def parse_cv(text: str) -> list[Item]:
    """Every dated entry in the CV's Education / Service / Awards record.

    lane="cv" on all of them: matching is deliberately lane-agnostic (see the
    module docstring), and Item.matches only compares lanes when both sides
    carry a figure lane.
    """
    items: list[Item] = []
    for pattern, name in CV_SECTIONS:
        for it in cv_items(text, pattern, name):
            # First sentence reads as a label; fall back to the opening words
            # when it is just an initial ("G. Padgett. ...").
            first = re.split(r"\.\s", it.body, maxsplit=1)[0].strip().rstrip(".")
            if len(first.split()) < 3:
                first = " ".join(it.body.split()[:8]).rstrip(".,;")
            items.append(Item(
                label=f"{first} ({it.range})",
                lane="cv",
                years=years_in(it.range),
                # The subsection heading joins the body: the `### Peer Review`
                # entries name journals and never state the role, so the body
                # alone shares nothing with a "peer reviewer" chart label.
                tokens=tokens_of(f"{it.body} {it.section}"),
                source=f"cv.md:{it.line} §{it.section}",
            ))
    return items


# ─── variant drift ────────────────────────────────────────────────────────

_SVG_RE = re.compile(r'<svg class="(?P<cls>gantt-\w+)"[^>]*>(?P<body>.*?)</svg>',
                     re.DOTALL)
_TEXT_RE = re.compile(r"<text\b[^>]*>(?P<label>[^<]*)</text>")


def variant_label_drift(text: str) -> list[str]:
    """Labels present in one Gantt SVG variant but not the other.

    The figure carries two renderings of one dataset: svg.gantt-wide for
    desktop and svg.gantt-narrow at <=760px, on different transforms. Only
    the wide one is decoded against cv.md (see _common.gantt_marks), which
    would leave the narrow one free to drift, so its labels are checked
    against the wide one's here. Labels only: the two use different
    coordinate systems by design, so geometry cannot be compared directly.

    Returns [] when the figure has fewer than two variants, so the fixtures
    and any future single-SVG figure are unaffected.
    """
    fig = re.search(r'<figure class="gantt-figure">(.*?)</figure>', text, re.DOTALL)
    if not fig:
        return []
    found = {m.group("cls"): m.group("body") for m in _SVG_RE.finditer(fig.group(1))}
    if len(found) < 2:
        return []
    labels = {
        cls: {t.group("label").strip() for t in _TEXT_RE.finditer(body)
              if t.group("label").strip()}
        for cls, body in found.items()
    }
    wide, narrow = labels.get("gantt-wide", set()), labels.get("gantt-narrow", set())
    out = []
    for lbl in sorted(wide - narrow):
        out.append(f'"{lbl}" is in svg.gantt-wide but not svg.gantt-narrow')
    for lbl in sorted(narrow - wide):
        out.append(f'"{lbl}" is in svg.gantt-narrow but not svg.gantt-wide')
    return out


# ─── main ─────────────────────────────────────────────────────────────────

def run() -> int:
    if not INDEX.exists():
        print(f"error: {INDEX} not found", file=sys.stderr)
        return 1
    text = INDEX.read_text(encoding="utf-8")

    marks = parse_figure(text)
    if not marks:
        print("error: no data marks parsed from figure.gantt-figure",
              file=sys.stderr)
        return 1

    drift = variant_label_drift(text)
    if drift:
        print("Gantt figure lint found drift between the wide and narrow "
              "SVG variants:\n", file=sys.stderr)
        for d in drift:
            print(f"  {d}", file=sys.stderr)
        print("\nThe two variants draw the same record at different sizes; "
              "edit both or neither.", file=sys.stderr)
        return 1

    if not CV.exists():
        print("gantt lint: cv.md absent; nothing to reconcile")
        return 0
    cv = parse_cv(CV.read_text(encoding="utf-8"))
    if not cv:
        print("error: no entries parsed from cv.md Education / Service / "
              "Awards sections", file=sys.stderr)
        return 1

    # ── Gate: every figure mark must have a CV counterpart ──
    failures: list[str] = []
    for mk in marks:
        if not any(mk.matches(c) for c in cv):
            failures.append(
                f"{mk.source}: {mk.lane}-lane mark \"{mk.label}\" has no "
                f"counterpart in cv.md (Education / Service / Awards). Add it "
                f"to the CV, or reconcile the label/year so the surfaces "
                f"agree. The mark's year(s) are read back from its "
                f"x-coordinate, so check the geometry too."
            )

    # ── Coverage report (informational): CV entries not on the chart ──
    uncovered = [c for c in cv if not any(c.matches(mk) for mk in marks)]

    if failures:
        print("Gantt figure lint found drift:\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(f"\n{len(failures)} figure mark(s) missing from cv.md.",
              file=sys.stderr)
        return 1

    education = sum(1 for mk in marks if mk.lane == "education")
    service = len(marks) - education
    print(f"gantt lint: {len(marks)} figure mark(s) "
          f"({education} education + {service} service) reconciled against "
          f"{len(cv)} cv.md entry(ies); "
          f"{len(uncovered)} cv.md item(s) not on the chart")
    if uncovered:
        print("  (informational; the chart is a curated subset -- short "
              "courses, individual mentees and minor service stay CV-only)")
        for c in uncovered:
            print(f"    - {c.label}  [{c.source}]")
    return 0


if __name__ == "__main__":
    sys.exit(run())
