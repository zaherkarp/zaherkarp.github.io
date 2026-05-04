#!/usr/bin/env python3
"""
build_resume.py

Reads resume.md at the repo root, renders it through a Jinja2 template,
and produces resume.pdf via WeasyPrint.

Design notes:
- Markdown source drives content. Re-run on every resume.md change.
- The markdown role blocks follow this shape:

      **Company** | Role Title
      Month YYYY – Month YYYY
      *Stack line*

      - bullet
      - bullet

  Markdown-it produces a single <p> with <br>-separated inlines for the
  three header lines. A regex post-pass here replaces that with a
  structured <header class="role"> block so the template can style
  each line distinctly.
- Print CSS targets US Letter at 10.5pt EB Garamond body, Courier New
  for data specimens (dates, stack lines), #1a5fa8 rule color.
- EB Garamond font files are bundled under scripts/fonts/ (OFL license).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt
from weasyprint import HTML

from _common import install_git_hooks

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "content" / "resume.md"
OUT = ROOT / "resume.pdf"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
FONT_DIR = Path(__file__).resolve().parent / "fonts"

# Matches the 3-line role header block as rendered by markdown-it with
# linkify/html enabled and breaks=True. We run a targeted regex because
# writing a markdown-it plugin for this one shape is overkill.
ROLE_BLOCK_RE = re.compile(
    r"<p><strong>([^<]+?)</strong>\s*\|\s*([^<\n]+?)<br\s*/?>\s*"
    r"([^<\n]+?)<br\s*/?>\s*<em>([^<]+?)</em></p>",
    re.MULTILINE,
)


def make_markdown() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": True, "breaks": True, "typographer": True})
    md.enable(["table"])
    return md


def wrap_sections(html: str) -> str:
    """
    Add class-bearing wrappers around the sections that want specific CSS
    treatment (experience bullets, skills, education, awards). We identify
    sections by their h2 text and wrap the following siblings up to the
    next h2.
    """
    section_classes = {
        "Experience": "exp",
        "Skills": "skills",
        "Education": "education",
        "Awards and Recognition": "awards",
    }

    def replace_section(match: re.Match) -> str:
        title = match.group(1).strip()
        body = match.group(2)
        cls = section_classes.get(title)
        if not cls:
            return match.group(0)
        return f'<h2>{title}</h2>\n<section class="{cls}">{body}</section>'

    # Walk one section at a time: from an <h2>…</h2> to the next <h2> or EOF.
    section_re = re.compile(
        r"<h2>([^<]+)</h2>\s*(.*?)(?=<h2>|\Z)", re.DOTALL
    )
    return section_re.sub(replace_section, html)


def transform_role_blocks(html: str) -> str:
    """
    Replace markdown-rendered role-header paragraphs with a structured
    <header class="role"> element.
    """
    def replace(match: re.Match) -> str:
        org = match.group(1).strip()
        title = match.group(2).strip()
        date = match.group(3).strip()
        stack = match.group(4).strip()
        return (
            '<header class="role">'
            '<div class="role-line">'
            f'<span class="role-where">'
            f'<span class="role-org">{org}</span>'
            '<span class="role-sep">|</span>'
            f'<span class="role-title">{title}</span>'
            '</span>'
            f'<span class="role-date">{date}</span>'
            '</div>'
            f'<div class="role-stack">{stack}</div>'
            '</header>'
        )
    return ROLE_BLOCK_RE.sub(replace, html)


def split_header(body_html: str) -> tuple[str, str, str]:
    """
    Extract the leading <h1>NAME</h1> and the contact paragraph that
    follows it. Return (name, contact_html, remaining_body).
    """
    h1 = re.match(r"<h1>([^<]+)</h1>\s*", body_html)
    if not h1:
        raise ValueError("Resume markdown must start with '# Name'")
    name = h1.group(1).strip()
    rest = body_html[h1.end():]

    # The next block is the contact paragraph.
    p = re.match(r"<p>(.+?)</p>\s*", rest, re.DOTALL)
    if not p:
        raise ValueError("Expected a contact paragraph after the name")
    contact = p.group(1).strip()
    remaining = rest[p.end():]
    return name, contact, remaining


def render() -> None:
    if not SRC.exists():
        print(f"error: {SRC} not found", file=sys.stderr)
        sys.exit(1)

    md_text = SRC.read_text(encoding="utf-8")
    md = make_markdown()
    raw_html = md.render(md_text)

    name, contact, remaining = split_header(raw_html)
    remaining = transform_role_blocks(remaining)
    remaining = wrap_sections(remaining)

    body = (
        f'<div class="hdr-name">{name}</div>\n'
        f'<div class="hdr-contact">{contact}</div>\n'
        f'{remaining}'
    )

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape([]),  # body is pre-rendered HTML
    )
    template = env.get_template("resume/resume.html")
    html = template.render(
        name=name,
        body=body,
        font_dir=str(FONT_DIR),
    )

    # Render to PDF
    pdf_bytes = HTML(string=html, base_url=str(ROOT)).write_pdf()
    OUT.write_bytes(pdf_bytes)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(pdf_bytes):,} bytes)")


if __name__ == "__main__":
    render()
