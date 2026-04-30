#!/usr/bin/env python3
"""
lint_blog.py

Source-side checks for src/content/blog/*.md that catch storage-level
mistakes documented in CLAUDE.md §Blog pipeline:

  1. HTML comments (`<!-- ... -->`) in a post that will ship
     (`draft: false`, no `_` prefix). Comments render as visible
     `&lt;!-- --&gt;` text; they must be stripped before publishing.
  2. A fenced code block (```lang) nested inside an HTML comment.
     The markdown-it HTML-block parser bails out of HTML mode at the
     fence and renders the rest of the document as literal text.
  3. A blockquote line starting with a Mermaid keyword
     (`> flowchart LR`, `> graph TD`, etc.). Markdown renders this
     as prose with literal `--&gt;` arrows; Mermaid never sees it.
     Use a fenced ```mermaid block instead.
  4. A blank line inside an `<svg>` element. markdown-it terminates
     the HTML block at the blank line and re-parses the rest of the
     SVG as markdown, wrapping `<text>`/`<line>`/`<polyline>`/etc. in
     `<p>` tags. The browser drops or mangles the chart.

Runs in CI (.github/workflows/build_blog.yml) before the build step,
and locally via `python scripts/lint_blog.py`.

Exits non-zero if any violation is found. Inside fenced code blocks
is safe by design — a post showing a literal `<!-- -->` example or
an example of blockquote syntax can keep it inside ```text / ```html.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "src" / "content" / "blog"

# Mermaid diagram keywords that commonly appear as the first token
# on the first line of a diagram. If we find one of these after a
# leading `> ` (blockquote), it's a blockquote-as-diagram.
MERMAID_KEYWORDS = (
    "flowchart",
    "graph",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "gantt",
    "pie",
    "journey",
    "gitGraph",
    "mindmap",
    "timeline",
    "quadrantChart",
    "xychart-beta",
    "sankey-beta",
    "block-beta",
)

BLOCKQUOTE_MERMAID_RE = re.compile(
    r"^>\s*(" + "|".join(MERMAID_KEYWORDS) + r")\b",
    re.MULTILINE,
)

FENCE_RE = re.compile(r"^```", re.MULTILINE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
SVG_OPEN_RE = re.compile(r"<svg[\s>]", re.IGNORECASE)
SVG_CLOSE_RE = re.compile(r"</svg>", re.IGNORECASE)


def split_fenced(text: str) -> list[tuple[str, str, int]]:
    """
    Split markdown into ("prose", text, start_offset) and
    ("fence", text, start_offset) chunks so callers can apply
    prose-only checks. Fence chunks include the opening and
    closing ``` lines.
    """
    chunks: list[tuple[str, str, int]] = []
    pos = 0
    in_fence = False
    fence_start = 0

    for match in FENCE_RE.finditer(text):
        # Only treat ``` that starts at column 0 as a fence boundary.
        if match.start() != 0 and text[match.start() - 1] != "\n":
            continue
        if not in_fence:
            if match.start() > pos:
                chunks.append(("prose", text[pos : match.start()], pos))
            fence_start = match.start()
            in_fence = True
        else:
            # Find end of this ``` line (include the trailing newline).
            line_end = text.find("\n", match.end())
            line_end = line_end + 1 if line_end != -1 else len(text)
            chunks.append(("fence", text[fence_start:line_end], fence_start))
            pos = line_end
            in_fence = False

    if in_fence:
        # Unterminated fence — treat remainder as fence for lenient handling.
        chunks.append(("fence", text[fence_start:], fence_start))
    elif pos < len(text):
        chunks.append(("prose", text[pos:], pos))

    return chunks


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def fence_spans(text: str) -> list[tuple[int, int]]:
    """Byte ranges of every fenced code block in the raw text."""
    spans: list[tuple[int, int]] = []
    for kind, chunk, start in split_fenced(text):
        if kind == "fence":
            spans.append((start, start + len(chunk)))
    return spans


def check_post(path: Path) -> list[str]:
    """
    Return a list of human-readable violation strings (empty = clean).
    Skips posts with `draft: true` or filenames starting with `_`.
    """
    if path.stem.startswith("_"):
        return []

    post = frontmatter.load(path)
    if bool(post.metadata.get("draft", False)):
        return []

    text = path.read_text(encoding="utf-8")
    violations: list[str] = []
    fences = fence_spans(text)

    def inside_fence(offset: int) -> bool:
        return any(start <= offset < end for start, end in fences)

    # 1. HTML comments. Scanned against the raw text so we catch
    #    fenced-code-inside-comment (the pattern that breaks the
    #    tail of the document). Comments that are themselves inside
    #    a fenced code block are literal example text and skipped.
    for match in HTML_COMMENT_RE.finditer(text):
        if inside_fence(match.start()):
            continue
        line = line_of(text, match.start())
        if "```" in match.group(0):
            violations.append(
                f"{path.name}:{line}: fenced code block inside an HTML "
                f"comment — markdown-it bails into escaped-text mode for "
                f"the rest of the document. Strip the comment or move "
                f"the fenced block outside it."
            )
        else:
            violations.append(
                f"{path.name}:{line}: HTML comment in a published post "
                f"(draft: false). Comments render as visible `&lt;!-- "
                f"--&gt;` text. Remove the comment or keep the post at "
                f"draft: true until the scaffold is filled in."
            )

    # 2. Blockquote-as-diagram. Only checked in prose (code-block
    #    examples of blockquote syntax are fine).
    for kind, chunk, start in split_fenced(text):
        if kind != "prose":
            continue
        for match in BLOCKQUOTE_MERMAID_RE.finditer(chunk):
            abs_offset = start + match.start()
            line = line_of(text, abs_offset)
            keyword = match.group(1)
            violations.append(
                f"{path.name}:{line}: blockquote-as-diagram "
                f"(`> {keyword}`). Markdown renders this as prose with "
                f"literal `--&gt;` arrows; Mermaid never sees it. "
                f"Use a fenced ```mermaid block."
            )

    # 3. Blank line inside an <svg>. markdown-it terminates the HTML
    #    block at the blank line and wraps subsequent SVG children
    #    (<text>, <line>, <polyline>, ...) in <p> tags, which the
    #    browser drops. Prose-only so a fenced ```html example with
    #    a multi-line <svg> stays untouched.
    for kind, chunk, start in split_fenced(text):
        if kind != "prose":
            continue
        depth = 0
        offset = start
        for line_text in chunk.split("\n"):
            if depth > 0 and line_text.strip() == "":
                violations.append(
                    f"{path.name}:{line_of(text, offset)}: blank line "
                    f"inside <svg>. markdown-it ends the HTML block at "
                    f"the blank line and wraps the rest of the SVG "
                    f"children in <p> tags; the chart breaks. Remove "
                    f"the blank line."
                )
            depth += len(SVG_OPEN_RE.findall(line_text))
            depth -= len(SVG_CLOSE_RE.findall(line_text))
            if depth < 0:
                depth = 0
            offset += len(line_text) + 1

    return violations


def main() -> int:
    if not POSTS_DIR.exists():
        print(f"error: {POSTS_DIR} does not exist", file=sys.stderr)
        return 1

    all_violations: list[str] = []
    checked = 0
    for path in sorted(POSTS_DIR.glob("*.md")):
        violations = check_post(path)
        if path.stem.startswith("_"):
            continue
        checked += 1
        all_violations.extend(violations)

    if all_violations:
        print("Blog lint found violations:\n", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        print(
            f"\n{len(all_violations)} violation(s) across "
            f"{checked} checked post(s). "
            f"See CLAUDE.md §Blog pipeline for storage-side rules.",
            file=sys.stderr,
        )
        return 1

    print(f"blog lint: {checked} post(s) clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
