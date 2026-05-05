#!/usr/bin/env python3
"""
analyze_resume_layout.py

Render src/content/resume.md through the same pipeline as
build_resume.py, walk the WeasyPrint layout tree to extract every
rendered line in order, then group them into logical blocks by bullet
markers and y-position gaps. The last line of each multi-line block is
flagged as a "widow" when it has 1-4 words — trimming a word from the
source bullet would pull that line up and reclaim vertical space.

Output is plain text grouped by page and by block. Run before pushing
resume edits to plan trims.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from build_resume import (
    FONT_DIR,
    ROOT,
    SRC,
    TEMPLATES_DIR,
    make_markdown,
    split_header,
    transform_role_blocks,
    wrap_sections,
)
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from weasyprint.formatting_structure import boxes as wp_boxes

WIDOW_MAX_WORDS = 4
Y_GAP_BLOCK_BREAK = 4.0  # pt; bigger gap → new block
BULLET_GLYPH = "•"


def render_html() -> str:
    md_text = SRC.read_text(encoding="utf-8")
    md = make_markdown()
    raw_html = md.render(md_text)
    name, contact, remaining = split_header(raw_html)
    remaining = transform_role_blocks(remaining)
    remaining = wrap_sections(remaining)
    body = (
        f'<div class="hdr-name">{name}</div>\n'
        f'<div class="hdr-contact">{contact}</div>\n'
        f"{remaining}"
    )
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape([]),
    )
    template = env.get_template("resume/resume.html")
    return template.render(name=name, body=body, font_dir=str(FONT_DIR))


def text_of(box) -> str:
    if isinstance(box, wp_boxes.TextBox):
        return box.text or ""
    parts = []
    for child in getattr(box, "children", []) or []:
        parts.append(text_of(child))
    return "".join(parts)


def walk(box):
    yield box
    for child in getattr(box, "children", []) or []:
        yield from walk(child)


def collect_lines(page_box):
    """Return [(text, y, height)] for every non-empty LineBox on the page."""
    out = []
    for box in walk(page_box):
        if not isinstance(box, wp_boxes.LineBox):
            continue
        text = text_of(box).strip()
        if not text:
            continue
        y = getattr(box, "position_y", 0.0) or 0.0
        h = getattr(box, "height", 0.0) or 0.0
        out.append((text, y, h))
    out.sort(key=lambda r: r[1])  # ensure top-down order
    return out


def group_into_blocks(lines):
    """
    Group an ordered list of LineBox records into logical blocks.

    Heuristic:
      - A line equal to the bullet glyph starts a new block (a bullet).
        Subsequent lines belong to that bullet until the next bullet
        marker OR a y-gap larger than Y_GAP_BLOCK_BREAK.
      - Outside of bullets, a y-gap larger than Y_GAP_BLOCK_BREAK starts
        a new block (paragraph / heading break).
    """
    blocks = []
    cur = None
    prev_bottom = None

    for text, y, h in lines:
        is_marker = text == BULLET_GLYPH
        gap = (y - prev_bottom) if prev_bottom is not None else 0.0

        if is_marker:
            cur = {"kind": "bullet", "lines": []}
            blocks.append(cur)
        elif cur is None or gap > Y_GAP_BLOCK_BREAK:
            cur = {"kind": "block", "lines": []}
            blocks.append(cur)

        if not is_marker:
            cur["lines"].append(text)

        prev_bottom = y + h

    return [b for b in blocks if b["lines"]]


def analyze() -> int:
    html_str = render_html()
    document = HTML(string=html_str, base_url=str(ROOT)).render()

    total_widows = 0
    print(f"pages: {len(document.pages)}\n")

    for page_num, page in enumerate(document.pages, 1):
        print(f"=== page {page_num} ===")
        lines = collect_lines(page._page_box)
        blocks = group_into_blocks(lines)

        for b in blocks:
            kind = b["kind"]
            n = len(b["lines"])
            tag = "•" if kind == "bullet" else " "
            print(f"  {tag} [{n} line{'s' if n != 1 else ''}]")
            for i, text in enumerate(b["lines"]):
                words = len(text.split())
                is_last = i == n - 1
                is_widow = is_last and n >= 2 and words <= WIDOW_MAX_WORDS
                marker = "  >>> WIDOW" if is_widow else ""
                if is_widow:
                    total_widows += 1
                truncated = text if len(text) <= 95 else text[:92] + "..."
                print(f"      {words:>2}w  {truncated}{marker}")
            print()
        print()

    print(f"widow candidates: {total_widows}")
    return 0


if __name__ == "__main__":
    sys.exit(analyze())
