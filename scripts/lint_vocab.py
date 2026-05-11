#!/usr/bin/env python3
"""
lint_vocab.py

Source-side checks for canonical program-name capitalization across
content surfaces. Enforces the canonicals declared in CLAUDE.md
§Vocabulary, anchored externally to the CMS 2025 MA & Part D Star
Ratings fact sheet:

  https://www.cms.gov/newsroom/fact-sheets/2025-medicare-advantage-part-d-star-ratings

Surfaces scanned:
  - src/content/blog/*.md (skipping drafts and `_`-prefixed files)
  - src/content/resume.md
  - index.html

Out of scope: CLAUDE.md, README.md, AGENTS.md, scripts/, archive/,
generated /blog/ output. Sources are the truth; CI regenerates the
rest.

Matches inside fenced code blocks are skipped so a post can show a
literal example like ```text\nSTAR Ratings\n``` without tripping the
rule.

Runs in CI (.github/workflows/build_blog.yml) before the build step,
and locally via `python scripts/lint_vocab.py` and the pre-push hook.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import frontmatter

from _common import install_git_hooks
from lint_blog import fence_spans, line_of

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "src" / "content" / "blog"
RESUME = ROOT / "src" / "content" / "resume.md"
INDEX = ROOT / "index.html"


@dataclass(frozen=True)
class Rule:
    canonical: str
    pattern: re.Pattern[str]
    cite: str


RULES: list[Rule] = [
    Rule(
        canonical="Star Ratings",
        # All-caps "STAR" before " Ratings" is never the CMS form.
        # Word boundaries keep "STARs" / "STAR-rated" from matching.
        pattern=re.compile(r"\bSTAR Ratings?\b"),
        cite="CMS 2025 MA & Part D Star Ratings fact sheet; CLAUDE.md §Vocabulary",
    ),
    Rule(
        canonical="Centers for Medicare & Medicaid Services",
        # The agency's official name uses an ampersand. "and" is the
        # common wrong form. Match either with or without the trailing
        # " Services" so partial mentions also flag.
        pattern=re.compile(r"\bCenters for Medicare and Medicaid(?: Services)?\b"),
        cite="CMS official name; CLAUDE.md §Vocabulary",
    ),
    Rule(
        canonical="Medicare Advantage",
        # All-caps is never correct in prose; the legitimate acronym is "MA".
        pattern=re.compile(r"\bMEDICARE ADVANTAGE\b"),
        cite="CMS 2025 MA & Part D Star Ratings fact sheet",
    ),
]


def is_skipped_post(path: Path) -> bool:
    """Drafts and `_`-prefixed files are skipped (matches lint_blog)."""
    if path.stem.startswith("_"):
        return True
    post = frontmatter.load(path)
    return bool(post.metadata.get("draft", False))


def check_text(path: Path, text: str, *, fenced: bool) -> list[str]:
    """Return violation strings for `text` against every rule.

    `fenced=True` means the file uses ``` fenced code blocks (markdown);
    matches inside those are skipped. For non-markdown files (index.html,
    plain html), pass fenced=False — every match is reported.
    """
    fences = fence_spans(text) if fenced else []

    def inside_fence(offset: int) -> bool:
        return any(start <= offset < end for start, end in fences)

    violations: list[str] = []
    for rule in RULES:
        for match in rule.pattern.finditer(text):
            if inside_fence(match.start()):
                continue
            line = line_of(text, match.start())
            violations.append(
                f'{path.name}:{line}: vocab: "{match.group(0)}" should be '
                f'"{rule.canonical}" ({rule.cite})'
            )
    return violations


def iter_surfaces() -> list[tuple[Path, bool]]:
    """Yield (path, is_markdown) for every surface to scan."""
    surfaces: list[tuple[Path, bool]] = []
    if POSTS_DIR.exists():
        for path in sorted(POSTS_DIR.glob("*.md")):
            if is_skipped_post(path):
                continue
            surfaces.append((path, True))
    if RESUME.exists():
        surfaces.append((RESUME, True))
    if INDEX.exists():
        surfaces.append((INDEX, False))
    return surfaces


def main() -> int:
    surfaces = iter_surfaces()
    if not surfaces:
        print("error: no content surfaces found to scan", file=sys.stderr)
        return 1

    all_violations: list[str] = []
    for path, is_markdown in surfaces:
        text = path.read_text(encoding="utf-8")
        all_violations.extend(check_text(path, text, fenced=is_markdown))

    if all_violations:
        print("Vocab lint found violations:\n", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        print(
            f"\n{len(all_violations)} violation(s) across "
            f"{len(surfaces)} scanned file(s). "
            f"See CLAUDE.md §Vocabulary for canonical forms.",
            file=sys.stderr,
        )
        return 1

    print(f"vocab lint: {len(surfaces)} file(s) clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
