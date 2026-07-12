#!/usr/bin/env python3
"""
lint_vocab.py

Canonical-driven vocabulary checker for content surfaces. Each
canonical declares its accepted spelling(s) plus a matcher; any
literal the matcher catches whose form is not in the accepted set is
a violation. One canonical declaration thus catches every wrong-case
variant that the matcher reaches without a new regex per wrong form.

Anchored externally to the CMS 2025 MA & Part D Star Ratings fact
sheet:
  https://www.cms.gov/newsroom/fact-sheets/2025-medicare-advantage-part-d-star-ratings
and to CLAUDE.md §Vocabulary, where the canonicals are documented
in prose.

Surfaces scanned:
  - src/content/blog/*.md (skipping drafts and `_`-prefixed files)
  - src/content/resume.md
  - src/content/cv.md
  - index.html

Out of scope: CLAUDE.md, README.md, AGENTS.md, scripts/, archive/,
generated /blog/ output.

Patterns are deliberately narrow. "Star Ratings" / "Medicare
Advantage" rules catch ALL-CAPS and mixed-case anomalies; the
fully-lowercase rendering is tolerated because the corpus uses words
like "star" both as a proper-noun reference and as a generic English
word (a "4.0 star cliff", "star rating displayed in the simulator").
The bare "Star" stem only flags ALL-CAPS forms (STAR-linked, STARs)
for the same reason. The agency-name rule is strict — only the exact
canonical with ampersand passes.

Skip ranges for non-prose regions are honored:
  - fenced code blocks (```...```)
  - markdown inline code spans (`...`)
  - markdown link URLs (the (...) part of [label](url))
  - HTML attribute values (anything inside ="...")
  - HTML <script> and <style> block contents

Two escape hatches for legitimate non-canonical literals that fall
outside the skip-range heuristics:
  1. Per-post `vocab_exempt:` frontmatter list — exact-string opt-out
     for citations, quotes, or proper-noun product names that
     genuinely use a non-canonical form. Example:
         ---
         title: "..."
         vocab_exempt:
           - "STAR Ratings"
         ---
  2. Module-level EXEMPTIONS dict for non-markdown surfaces
     (index.html, resume.md). Empty until a real case emerges.

Phrase canonicals (multi-word) take precedence over stem canonicals
(single-word): once a longer canonical claims a byte range, shorter
canonicals skip matches inside it. So "Star Ratings" is processed as
a phrase and the embedded "Star" stem doesn't re-flag the same text.

Runs in CI (.github/workflows/build_blog.yml) before the build step,
and locally via `python scripts/lint_vocab.py` and the pre-push hook.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import frontmatter

from _common import install_git_hooks, iter_post_paths
from lint_blog import fence_spans, line_of

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "src" / "content" / "blog"
RESUME = ROOT / "src" / "content" / "resume.md"
CV = ROOT / "src" / "content" / "cv.md"
INDEX = ROOT / "index.html"


@dataclass(frozen=True)
class Canonical:
    """One vocabulary rule.

    `forms` lists the accepted exact spellings (usually one; two when a
    singular/plural pair both qualify). `pattern` is the matcher whose
    hits are checked against `forms`. `allow_lowercase` extends the
    accepted set to include the all-lowercase rendering of any form,
    for canonicals where lowercase is also a legitimate generic
    English usage. `note` is an optional short hint included in the
    violation message.
    """

    forms: tuple[str, ...]
    pattern: re.Pattern[str]
    note: str = ""
    allow_lowercase: bool = False

    @property
    def length(self) -> int:
        """Length of the longest accepted form. Used to order rules so
        phrase canonicals process before stem canonicals."""
        return max(len(f) for f in self.forms)

    def accepts(self, literal: str) -> bool:
        if literal in self.forms:
            return True
        if self.allow_lowercase and literal == literal.lower():
            if any(literal == f.lower() for f in self.forms):
                return True
        return False


CANONICALS: list[Canonical] = [
    # Agency name: strict. Exact ampersand-bearing form only. Required
    # "Services" suffix avoids false positives on "Center for Medicare
    # & Medicaid Innovation" (CMMI), a different singular sub-agency.
    Canonical(
        forms=("Centers for Medicare & Medicaid Services",),
        pattern=re.compile(
            r"\bcenters for medicare (?:&|and) medicaid services\b",
            re.IGNORECASE,
        ),
        note="agency name uses an ampersand",
    ),
    # Program name: case-insensitive scan, accept canonical Title Case
    # OR fully-lowercase (slug-y / generic). Flags MEDICARE ADVANTAGE
    # and mixed-case anomalies.
    Canonical(
        forms=("Medicare Advantage",),
        pattern=re.compile(r"\bmedicare advantage\b", re.IGNORECASE),
        note="proper-noun program name",
        allow_lowercase=True,
    ),
    # Program name: case-insensitive scan, accept canonical Title Case
    # (singular or plural) OR fully-lowercase. Flags STAR Ratings,
    # STAR Rating, STAR RATINGS, mixed forms.
    Canonical(
        forms=("Star Ratings", "Star Rating"),
        pattern=re.compile(r"\bstar ratings?\b", re.IGNORECASE),
        note="program name; CMS uses Title Case",
        allow_lowercase=True,
    ),
    # Stem: standalone "STAR" / "STARS" / "STARs" referring to the
    # program. Catches STAR-linked, STAR outcomes, STAR gates, STARs.
    # Lowercase "star" / "stars" pass — the corpus uses both as
    # generic English words ("4.0 star QBP cliff", "5 stars").
    Canonical(
        forms=("Star", "Stars"),
        pattern=re.compile(r"\bSTAR[Ss]?\b"),
        note="bare proper-noun reference; CMS uses Title Case",
    ),
]


# Per-file exemptions for non-markdown surfaces. Markdown posts use a
# `vocab_exempt:` frontmatter list instead. Each entry is the set of
# literal strings to tolerate as-is in that file.
EXEMPTIONS: dict[Path, frozenset[str]] = {
    INDEX: frozenset(),
    RESUME: frozenset(),
    CV: frozenset(),
}


# Skip-range patterns. Captured group 1 (or 2 for script/style) is the
# byte range that should be excluded from vocab matching.
INLINE_CODE_RE = re.compile(r"`([^`\n]*)`")
MARKDOWN_LINK_URL_RE = re.compile(r"\]\(([^)]*)\)")
HTML_ATTR_VALUE_RE = re.compile(r'=\s*"([^"]*)"')
HTML_COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)
SCRIPT_OR_STYLE_RE = re.compile(
    r"<(script|style)\b[^>]*>(.*?)</\1>",
    re.DOTALL | re.IGNORECASE,
)


def skip_ranges(text: str, *, fenced: bool) -> list[tuple[int, int]]:
    """Byte ranges where vocab matches should be ignored.

    Covers code fences (markdown only), inline code, markdown link
    URLs, HTML attribute values, HTML comments, and the contents of
    <script>/<style>. HTML comments are skipped because they never
    render — author-facing section markers like `<!-- STARS CLIFF -->`
    are noise to the reader, not the page.
    """
    ranges: list[tuple[int, int]] = []
    if fenced:
        ranges.extend(fence_spans(text))
    for pat in (
        INLINE_CODE_RE,
        MARKDOWN_LINK_URL_RE,
        HTML_ATTR_VALUE_RE,
        HTML_COMMENT_RE,
    ):
        for match in pat.finditer(text):
            ranges.append(match.span(1))
    for match in SCRIPT_OR_STYLE_RE.finditer(text):
        ranges.append(match.span(2))
    return ranges


def is_skipped_post(path: Path) -> bool:
    """Drafts and `_`-prefixed files are skipped (matches lint_blog)."""
    if path.stem.startswith("_"):
        return True
    post = frontmatter.load(path)
    return bool(post.metadata.get("draft", False))


def post_exemptions(path: Path) -> frozenset[str]:
    """Read the `vocab_exempt` frontmatter list from a markdown post."""
    post = frontmatter.load(path)
    raw = post.metadata.get("vocab_exempt", []) or []
    if not isinstance(raw, list):
        return frozenset()
    return frozenset(str(item) for item in raw)


def overlaps(start: int, end: int, ranges: list[tuple[int, int]]) -> bool:
    """True if [start, end) lies inside any (rstart, rend) in ranges."""
    return any(rstart <= start and end <= rend for rstart, rend in ranges)


def check_text(
    path: Path,
    text: str,
    *,
    fenced: bool,
    exemptions: frozenset[str],
) -> list[str]:
    """Return violation strings for `text` against every canonical."""
    skips = skip_ranges(text, fenced=fenced)

    def in_skip(start: int, end: int) -> bool:
        return any(s <= start < e for s, e in skips)

    # Process longer canonicals first so phrase rules claim before
    # stem rules look at the same text.
    ordered = sorted(CANONICALS, key=lambda c: -c.length)

    violations: list[str] = []
    claimed: list[tuple[int, int]] = []

    for canonical in ordered:
        for match in canonical.pattern.finditer(text):
            start, end = match.span()
            if in_skip(start, end):
                continue
            if overlaps(start, end, claimed):
                continue
            literal = match.group(0)
            claimed.append((start, end))
            if canonical.accepts(literal):
                continue
            if literal in exemptions:
                continue
            line = line_of(text, start)
            forms_str = " or ".join(f'"{f}"' for f in canonical.forms)
            note = f" — {canonical.note}" if canonical.note else ""
            violations.append(
                f'{path.name}:{line}: vocab: "{literal}" should be '
                f"{forms_str}{note}"
            )

    return violations


def iter_surfaces() -> list[tuple[Path, bool, frozenset[str]]]:
    """Yield (path, is_markdown, exemptions) for every surface."""
    surfaces: list[tuple[Path, bool, frozenset[str]]] = []
    if POSTS_DIR.exists():
        for path in iter_post_paths(POSTS_DIR):
            if is_skipped_post(path):
                continue
            surfaces.append((path, True, post_exemptions(path)))
    if RESUME.exists():
        surfaces.append((RESUME, True, EXEMPTIONS.get(RESUME, frozenset())))
    if CV.exists():
        surfaces.append((CV, True, EXEMPTIONS.get(CV, frozenset())))
    if INDEX.exists():
        surfaces.append((INDEX, False, EXEMPTIONS.get(INDEX, frozenset())))
    return surfaces


def main() -> int:
    surfaces = iter_surfaces()
    if not surfaces:
        print("error: no content surfaces found to scan", file=sys.stderr)
        return 1

    all_violations: list[str] = []
    for path, is_markdown, exemptions in surfaces:
        text = path.read_text(encoding="utf-8")
        all_violations.extend(
            check_text(path, text, fenced=is_markdown, exemptions=exemptions)
        )

    if all_violations:
        print("Vocab lint found violations:\n", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        print(
            f"\n{len(all_violations)} violation(s) across "
            f"{len(surfaces)} scanned file(s). "
            f"See CLAUDE.md §Vocabulary for canonical forms; add to "
            f"vocab_exempt frontmatter for legitimate verbatim usage.",
            file=sys.stderr,
        )
        return 1

    print(f"vocab lint: {len(surfaces)} file(s) clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
