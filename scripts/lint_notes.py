#!/usr/bin/env python3
"""
lint_notes.py

Additivity checker for sidenotes and margin notes (CLAUDE.md
§Sidenote system, additivity rule). A note exists to supplement the
text, so a note that restates facts already in the prose is
redundancy, not annotation. Born from a 2026-06-11 editorial-council
review that removed five such duplications by hand.

Three checks, all deterministic and deliberately narrow (the
lint_vocab philosophy: high-precision matchers plus explicit escape
hatches, no fuzzy similarity scoring):

  1. index.html notes vs page prose. For every hand-authored
     `<span class="sidenote">` / `<span class="marginnote">`, flag:
       - significant-number collision: a numeric token of value
         >= 1000 (commas normalized, years 1900-2099 excluded) that
         also appears in the page prose outside the note;
       - shingle collision: a run of SHINGLE consecutive words shared
         with the page prose outside the note.
     The baseline is the FULL page text including closed folds, not
     the default view: engaged readers expand folds and hit the
     repeat. Notes containing `.stat-num` are exempt by design — the
     §Margin stats pattern deliberately surfaces numbers buried
     inside closed folds, and the markup self-declares the exception.
  2. Blog frontmatter: `homepageMarginnote` vs the post's title +
     description (same two collision checks). build_portfolio.py
     renders all three onto the same homepage entry, so overlap
     lands as visible redundancy.
  3. publications.yaml: a `note` field must not contain the entry's
     venue string or its publication year — both already render in
     the visible citation line directly below the note.

Generated marker regions in index.html (activity-grid, writing-list,
writing-index, pub-list) are blanked before scanning: their content
is produced from the sources that checks 2 and 3 lint directly, and
the rendered copy can be legitimately stale between a source edit
and the next CI run.

Escape hatches:
  - EXEMPT_NOTE_IDS: note ids in index.html to skip entirely. Empty
    by default.
  - `.stat-num` markup inside a note (automatic, see above).

Runs locally via `python scripts/lint_notes.py` and the pre-push
hook. If it false-positives on a legitimate construct, fix the note
or add a targeted exemption — do not weaken the matchers.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import frontmatter
import yaml

from _common import install_git_hooks

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
POSTS_DIR = ROOT / "src" / "content" / "blog"
PUBS = ROOT / "src" / "content" / "publications.yaml"

# Words per shingle. Five is the calibrated floor: long enough that a
# shared run means restatement, short enough to catch a one-word
# paraphrase swap inside a copied clause (the case that motivated the
# linter shared "cms requirements into organizational priorities"
# across an "of"/"from" substitution). Four was tested and rejected:
# it flags shared four-word domain terms ("quality bonus payment
# threshold"), which are vocabulary, not restatement.
SHINGLE = 5

# Note ids (the id on the note's margin-toggle <input>) exempt from
# check 1. Empty until a real case emerges; prefer fixing the note.
EXEMPT_NOTE_IDS: frozenset[str] = frozenset()

# Generated regions: content between these marker pairs is built by
# scripts/build_portfolio.py from blog frontmatter / publications.yaml,
# which checks 2 and 3 lint at the source.
MARKER_PAIRS: list[tuple[str, str]] = [
    ("<!-- activity-grid:start -->", "<!-- activity-grid:end -->"),
    ("<!-- writing-list:start -->", "<!-- writing-list:end -->"),
    ("<!-- writing-index:start -->", "<!-- writing-index:end -->"),
    ("<!-- pub-list:start -->", "<!-- pub-list:end -->"),
]

NOTE_OPEN_RE = re.compile(r'<span class="(?:sidenote|marginnote)">')
SPAN_TOKEN_RE = re.compile(r"<span\b[^>]*>|</span>")
INPUT_ID_RE = re.compile(r'<input[^>]*\bid="([^"]*)"')
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
SCRIPT_OR_STYLE_RE = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE
)
TAG_RE = re.compile(r"<[^>]*>")
NUMBER_RE = re.compile(r"\d[\d,]*")
WORD_RE = re.compile(r"[a-z0-9][a-z0-9'\-]*")


def blank_generated(text: str) -> str:
    """Replace generated-region content with spaces (length-preserving,
    so byte offsets and line numbers stay valid)."""
    for start_marker, end_marker in MARKER_PAIRS:
        i = text.find(start_marker)
        j = text.find(end_marker)
        if i == -1 or j == -1 or j <= i:
            continue
        body_start = i + len(start_marker)
        region = text[body_start:j]
        text = text[:body_start] + re.sub(r"\S", " ", region) + text[j:]
    return text


def note_spans(text: str) -> list[tuple[int, int]]:
    """Byte ranges of every sidenote/marginnote span, including nested
    <span> children (stat-num numerals, links)."""
    spans: list[tuple[int, int]] = []
    for m in NOTE_OPEN_RE.finditer(text):
        depth = 1
        pos = m.end()
        while depth > 0:
            token = SPAN_TOKEN_RE.search(text, pos)
            if token is None:
                pos = len(text)
                break
            depth += 1 if token.group(0).startswith("<span") else -1
            pos = token.end()
        spans.append((m.start(), pos))
    return spans


def note_id(text: str, start: int) -> str:
    """Id of the margin-toggle <input> immediately preceding the note
    span; the toggle/checkbox/span triplet is adjacent by contract."""
    window = text[max(0, start - 600) : start]
    found = None
    for m in INPUT_ID_RE.finditer(window):
        found = m.group(1)
    return found or "<unidentified>"


def strip_tags(markup: str) -> str:
    markup = HTML_COMMENT_RE.sub(" ", markup)
    markup = SCRIPT_OR_STYLE_RE.sub(" ", markup)
    markup = TAG_RE.sub(" ", markup)
    return html.unescape(markup)


def words(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def shingles(tokens: list[str]) -> set[str]:
    return {
        " ".join(tokens[i : i + SHINGLE])
        for i in range(len(tokens) - SHINGLE + 1)
    }


def significant_numbers(text: str) -> set[str]:
    """Numeric tokens worth treating as facts: value >= 1000 with
    commas normalized, excluding years (1900-2099, ubiquitous in
    dates and ranges)."""
    out: set[str] = set()
    for m in NUMBER_RE.finditer(text):
        raw = m.group(0).replace(",", "")
        value = int(raw)
        if value >= 1000 and not 1900 <= value <= 2099:
            out.add(raw)
    return out


def collisions(note_text: str, context_text: str) -> list[str]:
    """Violation descriptions for a note against its context."""
    problems: list[str] = []
    context_numbers = significant_numbers(context_text)
    for number in sorted(significant_numbers(note_text)):
        if number in context_numbers:
            problems.append(f'repeats number "{number}"')
    context_shingles = shingles(words(context_text))
    for shingle in sorted(shingles(words(note_text)) & context_shingles):
        problems.append(f'shares phrase "{shingle}"')
    return problems


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_index() -> tuple[list[str], int]:
    text = blank_generated(INDEX.read_text(encoding="utf-8"))
    violations: list[str] = []
    checked = 0
    for start, end in note_spans(text):
        body = text[start:end]
        if 'class="stat-num"' in body:
            continue  # §Margin stats exception, self-declared in markup
        nid = note_id(text, start)
        if nid in EXEMPT_NOTE_IDS:
            continue
        checked += 1
        note_text = strip_tags(body)
        outside = strip_tags(text[:start] + " " + text[end:])
        for problem in collisions(note_text, outside):
            violations.append(
                f"index.html:{line_of(text, start)}: note '{nid}' "
                f"{problem} found elsewhere in page prose"
            )
    return violations, checked


def check_posts() -> tuple[list[str], int]:
    violations: list[str] = []
    checked = 0
    if not POSTS_DIR.exists():
        return violations, checked
    for path in sorted(POSTS_DIR.glob("*.md")):
        if path.stem.startswith("_"):
            continue
        post = frontmatter.load(path)
        if post.metadata.get("draft", False):
            continue
        note = post.metadata.get("homepageMarginnote")
        if not note:
            continue
        checked += 1
        target = (
            f"{post.metadata.get('title', '')} "
            f"{post.metadata.get('description', '')}"
        )
        for problem in collisions(str(note), target):
            violations.append(
                f"{path.name}: homepageMarginnote {problem} "
                f"found in the post's title/description"
            )
    return violations, checked


def check_pubs() -> tuple[list[str], int]:
    violations: list[str] = []
    checked = 0
    if not PUBS.exists():
        return violations, checked
    entries = yaml.safe_load(PUBS.read_text(encoding="utf-8")) or []
    for entry in entries:
        note = entry.get("note")
        if not note:
            continue
        checked += 1
        note_text = strip_tags(note)
        eid = entry.get("id", "<no id>")
        venue = entry.get("venue", "")
        if venue and venue.lower() in note_text.lower():
            violations.append(
                f"publications.yaml: entry '{eid}' note repeats the "
                f"venue (already rendered in the citation line)"
            )
        year = str(entry.get("year", ""))
        if year and re.search(rf"\b{year}\b", note_text):
            violations.append(
                f"publications.yaml: entry '{eid}' note repeats the "
                f"year {year} (already rendered in the citation line)"
            )
    return violations, checked


def main() -> int:
    all_violations: list[str] = []
    index_violations, n_notes = check_index()
    post_violations, n_posts = check_posts()
    pub_violations, n_pubs = check_pubs()
    all_violations = index_violations + post_violations + pub_violations

    if all_violations:
        print("Notes lint found violations:\n", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        print(
            f"\n{len(all_violations)} violation(s). A note must add, "
            f"not restate; see CLAUDE.md §Sidenote system (additivity "
            f"rule). For a legitimate duplicate, use EXEMPT_NOTE_IDS "
            f"in lint_notes.py.",
            file=sys.stderr,
        )
        return 1

    print(
        f"notes lint: {n_notes} homepage note(s), {n_posts} post "
        f"field(s), {n_pubs} yaml note(s) clean"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
