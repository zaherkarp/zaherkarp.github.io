"""Shared helpers for scripts in this directory.

Exposes install_git_hooks(), called at the top of each project script so a
fresh clone wires up the pre-push hook automatically without a manual setup
step, and slugify_tag(), the single source of truth for turning a blog tag
into the URL slug used by the per-tag archive pages (blog/tags/<slug>/).
Both build_blog.py (which emits the pages) and build_portfolio.py (which
links to them from the homepage cadence rollup) import slugify_tag so the
two surfaces can never disagree on a slug. Also exposes REPO_ROOT, the
repo's top-level path, resolved once here so every script (e.g.
edit_blog.py, for its posts directory) can import it instead of
re-deriving `Path(__file__).resolve().parent.parent` locally.

Also exposes the blog-post loading conventions shared by every
src/content/blog/*.md consumer: iter_post_paths() (a sorted, `_`-prefixed-
file-skipping glob, imported by build_blog.py, build_portfolio.py,
lint_blog.py, lint_vocab.py, lint_notes.py, and lint_jobfit.py) and
coerce_date() (a lenient datetime/date/ISO-string coercion, imported by
lint_jobfit.py and build_jobsearch.py for the private job-search tooling's
date fields). Draft filtering is deliberately NOT part of iter_post_paths:
consumers differ on whether they skip, count, or print drafts, so each
applies that after loading frontmatter.

Also exposes the cross-surface alignment matcher (years_of / tokens_of /
token_overlap / alignment_match) and the cv.md section item parser
(cv_section_body / cv_items / CvItem), the single source of truth shared by
lint_recognition.py, lint_gantt.py, and lint_jobfit.py. Each lint passes its
OWN stoplist to tokens_of (the `stop` parameter is required), so the
stoplists stay per-lint.

The cv.md parser replaced a homepage .row-entry HTML parser on 2026-08-13,
when index.html's #education and #service sections were deleted; see the
comment above cv_items for why the subsection heading travels with each item.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR_REL = "scripts/hooks"

# Any run of non-alphanumeric characters collapses to a single hyphen, so
# "Medicare Stars" / "medicare-stars" / "Medicare  Stars" all slug to
# "medicare-stars" and "CI/CD" slugs to "ci-cd". Tags that differ only in
# case or separator therefore share one tag page, which is the intended
# merge; genuinely different tags ("medicare" vs "medicare-stars") stay
# separate.
_TAG_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify_tag(tag: str) -> str:
    """Normalize a blog tag to its URL slug (lowercase, hyphen-separated)."""
    return _TAG_SLUG_RE.sub("-", str(tag).strip().lower()).strip("-")


# ─── blog-post loading ─────────────────────────────────────────────────────
# The two conventions every src/content/blog/*.md consumer shares, in one
# place. Draft handling is deliberately NOT here: consumers differ (some skip
# draft:true, some count drafts, some print), so each applies its own after
# loading frontmatter.


def iter_post_paths(posts_dir: Path):
    """Yield each buildable blog-post path under `posts_dir`, sorted.

    Encapsulates the two shared conventions: the glob is SORTED (same-date
    posts tie-break deterministically on filename, so auto-committed outputs
    do not reorder run-to-run) and `_`-prefixed files are skipped (the
    fixture / scaffold-marker convention).
    """
    for path in sorted(posts_dir.glob("*.md")):
        if path.stem.startswith("_"):
            continue
        yield path


def coerce_date(value):
    """Coerce a datetime / date / ISO string to a `date`, or None.

    The date part of a string is read from the first 10 chars, so a full
    timestamp works too. Returns None on anything else. This is the lenient
    form shared by the private job-search tooling (publishDate + outreach
    dates); the build scripts deliberately do NOT use it -- build_blog raises
    on a bad publishDate (fail-loud) and build_portfolio parses strictly.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


# ─── cross-surface alignment matcher ───────────────────────────────────────
# The single home for the year + token machinery shared by lint_recognition,
# lint_gantt, and lint_jobfit. `stop` is a REQUIRED parameter (no default), so
# each lint passes its own stoplist explicitly and one caller's tuning can
# never silently shift another's -- the reason the three keep distinct STOP
# sets while sharing this code.

_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_NON_TOKEN_RE = re.compile(r"[^a-z0-9]+")


def years_of(s: str) -> set[int]:
    """The four-digit 19xx/20xx years mentioned in a string."""
    return {int(m.group()) for m in _YEAR_RE.finditer(s)}


def tokens_of(s, stop, *, min_len=3, normalize=None):
    """Significant lowercase tokens in `s`.

    Splits on non-alphanumerics, drops tokens shorter than `min_len`, pure
    digits (years are handled by years_of), and anything in `stop`. `stop` is
    required so each call site states its own stoplist explicitly. `normalize`
    is an optional pre-pass (e.g. HTML-entity decoding) applied before casefold.
    """
    if normalize is not None:
        s = normalize(s)
    out: set[str] = set()
    for t in _NON_TOKEN_RE.split(s.lower()):
        if len(t) < min_len or t.isdigit() or t in stop:
            continue
        out.add(t)
    return out


def token_overlap(a, b, *, min_shared=2) -> bool:
    """True if token sets `a` and `b` share at least `min_shared` members.

    The year-free predicate, for surfaces that do not both carry dates (a
    skill vs. a job description). lint_jobfit / packet matching use this; the
    recognition/gantt lints use alignment_match below.
    """
    return len(a & b) >= min_shared


def alignment_match(a_years, a_tokens, b_years, b_tokens, *, min_shared=2) -> bool:
    """Year overlap AND >= min_shared shared tokens.

    The recognition/gantt predicate, faithfully extracted for reuse. Requires
    both sides to share a year, so it suits dated-vs-dated surfaces only.
    """
    if not (a_years & b_years):
        return False
    return token_overlap(a_tokens, b_tokens, min_shared=min_shared)


# ─── cv.md section item parser ─────────────────────────────────────────────
# Replaces the homepage .row-entry field parser that lived here until
# 2026-08-13. That parser read the <div class="row-entry"> blocks inside
# index.html's #education and #service sections; those sections were
# commented out 2026-07-30 and DELETED 2026-08-13, leaving the Gantt figure
# as the page's only surface for that record and src/content/cv.md as the
# comprehensive one. Both lint_recognition and lint_gantt now reconcile the
# figure against the CV, so the shared shape is a CV list item, not an HTML
# row. Each lint still owns its own stoplist and tokenizer.

CV_ITEM_RE = re.compile(
    r"^-\s+\*\*(?P<range>[^*]+)\*\*\s+(?P<body>.+?)\s*$", re.MULTILINE
)
_CV_HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")


# ─── Gantt figure mark parser ─────────────────────────────────────────────
# The homepage Education + Service Gantt is a hand-coded SVG whose marks
# encode their year(s) positionally, through the chart's own transform
# x(year) = 180 + (year - 2003) * 38. Reading the year back from the geometry
# is what makes the alignment lints more than a text diff: a mark drawn at
# the wrong x decodes to the wrong year and stops matching its CV entry.
#
# These four values ARE the chart's transform, so they move with it. The
# figure was re-laid-out onto a 1200-unit viewBox on 2026-08-15 (x0 90 -> 180,
# 19 -> 38 per year, lane divider 135 -> 130) to render at the same width as
# the career band and the dot plot. Tests import these rather than restating
# them, so the next re-layout does not need a second edit in three files.

GANTT_LANE_DIVIDER_Y = 130   # education rows top out at 102, service starts 162
GANTT_X0 = 180
GANTT_PX_PER_YEAR = 38
GANTT_BASE_YEAR = 2003

_GANTT_FIGURE_RE = re.compile(
    r'<figure class="gantt-figure">(?P<body>.*?)</figure>', re.DOTALL
)
# The figure holds TWO renderings of the same data: svg.gantt-wide (desktop)
# and svg.gantt-narrow (<=760px), which use DIFFERENT transforms. Only the
# wide one is decoded; running the narrow one's 600-unit coordinates through
# the wide transform would misdate every mark. lint_gantt separately checks
# that the two carry the same labels, so scoping here cannot hide drift.
# Falls back to the whole figure body when no .gantt-wide svg is present, so
# a fixture can supply bare marks with no <svg> wrapper at all.
_GANTT_WIDE_RE = re.compile(
    r'<svg class="gantt-wide"[^>]*>(?P<body>.*?)</svg>', re.DOTALL
)
# A data mark (rect square or thick-line bar) immediately followed by its
# <text> label.
_GANTT_MARK_RE = re.compile(
    r'(?P<mark><(?:rect|line)\b[^>]*/>)\s*<text\b[^>]*>(?P<label>[^<]*)</text>',
    re.DOTALL,
)


def gantt_year_at_x(x: float) -> int:
    return round(GANTT_BASE_YEAR + (x - GANTT_X0) / GANTT_PX_PER_YEAR)


@dataclass(frozen=True)
class GanttMark:
    """One data mark in the homepage Gantt figure."""

    label: str                # raw <text> label, not entity-normalized
    lane: str                 # "education" (y < GANTT_LANE_DIVIDER_Y) | "service"
    years: frozenset[int]     # decoded from the mark's x-coordinate(s)
    line: int                 # 1-indexed line in index.html


@dataclass(frozen=True)
class CvItem:
    """One `- **years** body` line in a cv.md section."""

    range: str        # "2016-2020", "2019-present", "2016, 2017"
    body: str
    section: str      # nearest ### subsection, else the ## section name
    line: int         # 1-indexed line in cv.md, for error messages


def cv_section_body(text: str, heading_pattern: str) -> tuple[str, int] | None:
    """(body, char_offset) for a `## Heading` / `### Heading` section, sliced
    to the next heading of equal-or-higher level. `heading_pattern` must
    capture a `hashes` group so the level is known."""
    m = re.search(heading_pattern, text, re.MULTILINE)
    if not m:
        return None
    level = len(m.group("hashes"))
    rest = text[m.end():]
    stop = re.search(rf"^#{{1,{level}}}\s", rest, re.MULTILINE)
    body = rest[: stop.start()] if stop else rest
    return body, m.end()


def _gantt_attr(mark: str, name: str) -> float | None:
    m = re.search(rf'\b{name}="(-?\d+(?:\.\d+)?)"', mark)
    return float(m.group(1)) if m else None


def gantt_marks(text: str) -> list[GanttMark]:
    """Every data mark in index.html's `figure.gantt-figure`, with its year(s)
    decoded from its own x-coordinate.

    Shared by lint_gantt (which reconciles all marks against cv.md) and
    lint_recognition (which reconciles the service lane against the CV's
    recognition record). Labels are returned RAW; each lint applies its own
    HTML-entity normalization and stoplist.

    Axis ticks (stroke-width 0.6/0.8) and the lane divider (0.5) are excluded
    by the fill / stroke-width filters, so only real data marks come back.
    """
    fig = _GANTT_FIGURE_RE.search(text)
    if not fig:
        return []
    body, base = fig.group("body"), fig.start("body")
    wide = _GANTT_WIDE_RE.search(body)
    if wide:
        base += wide.start("body")
        body = wide.group("body")
    marks: list[GanttMark] = []
    for m in _GANTT_MARK_RE.finditer(body):
        mark = m.group("mark")
        line = text.count("\n", 0, base + m.start()) + 1
        if mark.startswith("<rect"):
            if 'fill="#111"' not in mark:
                continue
            x, y = _gantt_attr(mark, "x"), _gantt_attr(mark, "y")
            if x is None or y is None:
                continue
            years = frozenset({gantt_year_at_x(x + 3)})   # square is 6 wide
        else:  # <line>
            if 'stroke-width="4"' not in mark:
                continue
            x1 = _gantt_attr(mark, "x1")
            x2 = _gantt_attr(mark, "x2")
            y = _gantt_attr(mark, "y1")
            if x1 is None or x2 is None or y is None:
                continue
            years = frozenset({gantt_year_at_x(x1), gantt_year_at_x(x2)})
        marks.append(GanttMark(
            label=m.group("label").strip() or "(unlabeled)",
            lane="education" if y < GANTT_LANE_DIVIDER_Y else "service",
            years=years,
            line=line,
        ))
    return marks


def cv_items(text: str, heading_pattern: str, section_name: str) -> list[CvItem]:
    """Every dated list item under a cv.md section, tagged with its nearest
    subsection heading.

    The subsection is carried because it holds meaning the item body omits:
    the entries under `### Peer Review` name journals and never say what the
    role was, so a caller matching against a terse chart label should
    tokenize `body + " " + section` rather than the body alone.
    """
    found = cv_section_body(text, heading_pattern)
    if not found:
        return []
    body, base = found
    items: list[CvItem] = []
    current = section_name
    cursor = 0                      # running offset into `body`, so repeated
    for line in body.split("\n"):   # line text can't misreport a line number
        head = _CV_HEADING_RE.match(line)
        if head:
            current = head.group("title")
        else:
            item = CV_ITEM_RE.match(line)
            if item:
                items.append(CvItem(
                    range=item.group("range").strip(),
                    body=item.group("body").strip(),
                    section=current,
                    line=text.count("\n", 0, base + cursor) + 1,
                ))
        cursor += len(line) + 1
    return items


def install_git_hooks() -> None:
    """Point git's core.hooksPath at scripts/hooks/ if it is unset.

    Idempotent. Silently no-ops outside a git work tree (tarball, CI
    sparse checkout, missing git binary). Prints a one-line notice on
    first install so the user knows hooks are now active.

    Polite: if core.hooksPath is already set to a DIFFERENT value (the
    user's own hooks, a pre-commit framework, etc.), it is NOT clobbered.
    We print how to opt in and leave their config alone, so running a
    build never silently hijacks a contributor's git setup. The CI
    backstop (.github/workflows/lint.yml) is the real gate regardless,
    so a machine that declines the local hook still cannot push drift.
    """
    hooks_dir = REPO_ROOT / HOOKS_DIR_REL
    if not hooks_dir.is_dir():
        return
    try:
        current = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        existing = current.stdout.strip()
        if existing == HOOKS_DIR_REL:
            return
        if existing:
            print(
                f"hooks: core.hooksPath is already set to {existing!r}; "
                f"leaving it as-is. To enable this project's pre-push lint "
                f"gate, run: git config core.hooksPath {HOOKS_DIR_REL}",
                file=sys.stderr,
            )
            return
        result = subprocess.run(
            ["git", "config", "core.hooksPath", HOOKS_DIR_REL],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return
    if result.returncode == 0:
        print(
            f"hooks: installed (core.hooksPath -> {HOOKS_DIR_REL}); "
            "pre-push checks now active",
            file=sys.stderr,
        )
