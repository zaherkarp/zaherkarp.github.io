#!/usr/bin/env python3
"""lint_gantt.py

Keeps the homepage Education + Service Gantt figure
(index.html `figure.gantt-figure`) in lockstep with the two prose
sections it summarizes, WITHOUT a shared data file. The figure is a
hand-coded SVG; this script reads it and the sections and compares.

The figure has two lanes that mirror two sections:

  education lane (y < 135)   <->  <section id="education">
  service lane   (y > 135)   <->  <section id="service">  (#service)

Each data mark encodes its year(s) positionally, via the chart's own
coordinate transform x(year) = 90 + (year - 2003) * 19:

  - a single-year credential is a <rect ... fill="#111"/> square; its
    year is read back from the square's centre x.
  - a multi-year range is a <line ... stroke-width="4"/> bar; its start
    and end years are read back from x1 and x2.

Each mark is paired with the <text> label that immediately follows it
in source.

GATE (hard fail, blocks push): every Education-section entry must have a
matching mark in the education lane, and every #service entry a matching
mark in the service lane. "Matching" = share at least one year AND at
least two significant tokens between the section entry (title + org) and
the figure label, which tolerates the figure's terse labels ("UG
research mentor" vs the section's "Undergraduate Research Mentor") with
no synonym table. A failure means a section entry was added or renamed
without updating the figure -- exactly the drift this guards.

A reverse coverage note (figure marks with no section entry) prints on a
manual run; it never fails.

This is the "pipeline, not a redraw-by-memory" answer to the figure
falling out of date when the Service and Recognition section grows.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from _common import install_git_hooks

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

MIN_SHARED_TOKENS = 2
LANE_DIVIDER_Y = 135
X0 = 90
PX_PER_YEAR = 19
BASE_YEAR = 2003

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
    s = normalize(s).lower()
    out: set[str] = set()
    for t in re.split(r"[^a-z0-9]+", s):
        if len(t) < 3 or t in STOP or t.isdigit():
            continue
        out.add(t)
    return frozenset(out)


def years_in(s: str) -> frozenset[int]:
    return frozenset(int(m.group()) for m in re.finditer(r"\b(?:19|20)\d{2}\b", s))


def year_at_x(x: float) -> int:
    return round(BASE_YEAR + (x - X0) / PX_PER_YEAR)


@dataclass(frozen=True)
class Item:
    label: str
    lane: str                 # "education" | "service"
    years: frozenset[int]
    tokens: frozenset[str]
    source: str

    def matches(self, other: "Item") -> bool:
        if self.lane != other.lane:
            return False
        if not (self.years & other.years):
            return False
        return len(self.tokens & other.tokens) >= MIN_SHARED_TOKENS


# ─── figure parser ────────────────────────────────────────────────────────

FIGURE_RE = re.compile(r'<figure class="gantt-figure">(?P<body>.*?)</figure>',
                       re.DOTALL)
# A data mark (rect square or thick-line bar) immediately followed by its
# <text> label. Axis ticks (stroke-width 0.6/0.8), the divider (0.5) and
# standalone labels are excluded by the stroke-width / fill filter below.
MARK_RE = re.compile(
    r'(?P<mark><(?:rect|line)\b[^>]*/>)\s*<text\b[^>]*>(?P<label>[^<]*)</text>',
    re.DOTALL,
)


def _attr(mark: str, name: str) -> float | None:
    m = re.search(rf'\b{name}="(-?\d+(?:\.\d+)?)"', mark)
    return float(m.group(1)) if m else None


def parse_figure(text: str) -> list[Item]:
    fig = FIGURE_RE.search(text)
    if not fig:
        return []
    base = fig.start("body")
    items: list[Item] = []
    for m in MARK_RE.finditer(fig.group("body")):
        mark = m.group("mark")
        label = normalize(m.group("label")).strip()
        line = text.count("\n", 0, base + m.start()) + 1
        if mark.startswith("<rect"):
            if 'fill="#111"' not in mark:
                continue
            x = _attr(mark, "x")
            y = _attr(mark, "y")
            if x is None or y is None:
                continue
            years = frozenset({year_at_x(x + 3)})   # square is 6 wide
        else:  # <line>
            if 'stroke-width="4"' not in mark:
                continue
            x1, x2, y = _attr(mark, "x1"), _attr(mark, "x2"), _attr(mark, "y1")
            if x1 is None or x2 is None or y is None:
                continue
            years = frozenset({year_at_x(x1), year_at_x(x2)})
        lane = "education" if y < LANE_DIVIDER_Y else "service"
        items.append(Item(
            label=label or "(unlabeled)",
            lane=lane,
            years=years,
            tokens=tokens_of(label),
            source=f"index.html:{line}",
        ))
    return items


# ─── section parser ───────────────────────────────────────────────────────

ROW_ENTRY_RE = re.compile(
    r'<div class="row-entry">(?P<row>.*?)</div>\s*</div>', re.DOTALL
)
ROW_DATE_RE = re.compile(r'<div class="row-date">(?P<v>[^<]*)</div>')
ROW_TITLE_RE = re.compile(r'<span class="row-title">(?P<v>[^<]*)</span>')
ROW_ORG_RE = re.compile(r'<span class="row-org">(?P<v>[^<]*)</span>')


def _section_body(text: str, section_id: str) -> tuple[str, int] | None:
    m = re.search(rf'<section id="{section_id}">(?P<body>.*?)</section>',
                  text, re.DOTALL)
    if not m:
        return None
    return m.group("body"), m.start("body")


def _field(pattern: re.Pattern, row: str) -> str:
    mm = pattern.search(row)
    return mm.group("v") if mm else ""


def parse_section(text: str, section_id: str, lane: str) -> list[Item]:
    found = _section_body(text, section_id)
    if not found:
        return []
    body, base = found
    items: list[Item] = []
    for m in ROW_ENTRY_RE.finditer(body):
        row = m.group("row")
        date = _field(ROW_DATE_RE, row)
        title = _field(ROW_TITLE_RE, row)
        org = _field(ROW_ORG_RE, row)
        if not title:
            continue
        line = text.count("\n", 0, base + m.start()) + 1
        items.append(Item(
            label=f"{normalize(title).strip()} ({normalize(date).strip()})",
            lane=lane,
            years=years_in(date),
            tokens=tokens_of(f"{title} {org}"),
            source=f"index.html:{line}",
        ))
    return items


# ─── main ─────────────────────────────────────────────────────────────────

def run() -> int:
    if not INDEX.exists():
        print(f"error: {INDEX} not found", file=sys.stderr)
        return 1
    text = INDEX.read_text(encoding="utf-8")

    marks = parse_figure(text)
    education = parse_section(text, "education", "education")
    service = parse_section(text, "service", "service")
    sections = education + service

    if not marks:
        print("error: no data marks parsed from figure.gantt-figure",
              file=sys.stderr)
        return 1
    if not sections:
        print("error: no entries parsed from #education / #service sections",
              file=sys.stderr)
        return 1

    failures: list[str] = []
    for s in sections:
        if not any(s.matches(mk) for mk in marks):
            failures.append(
                f"{s.source}: {s.lane} entry \"{s.label}\" has no matching "
                f"mark in the Gantt figure (figure.gantt-figure). Add a "
                f"{'square' if len(s.years) <= 1 else 'bar'} for it, or "
                f"reconcile the label/year so the surfaces agree."
            )

    # Reverse coverage (informational): figure marks with no section entry.
    orphans = [mk for mk in marks if not any(mk.matches(s) for s in sections)]

    if failures:
        print("Gantt figure lint found drift:\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(f"\n{len(failures)} section entry(ies) missing from the "
              f"Gantt figure.", file=sys.stderr)
        return 1

    print(f"gantt lint: {len(sections)} section entry(ies) "
          f"({len(education)} education + {len(service)} service) reconciled "
          f"against {len(marks)} figure mark(s)")
    if orphans:
        print("  (informational) figure marks with no section entry:")
        for mk in orphans:
            print(f"    - {mk.label}  [{mk.source}]")
    return 0


if __name__ == "__main__":
    sys.exit(run())
