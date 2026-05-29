#!/usr/bin/env python3
"""
build_resume.py

Reads the document sources under src/content/ (resume.md and cv.md),
renders each through its Jinja2 templates, and produces a PDF (via
WeasyPrint) plus a web HTML page for each.

The builder is config-driven: the DOCS list below names the source, the
PDF/web templates, the output paths, and whether the document carries a
generated Publications section. Both documents share the same rendering
pipeline (make_markdown / transform_role_blocks / wrap_sections /
split_header), so the resume output is unchanged by the addition of the CV.

Design notes:
- Markdown source drives content. Re-run on every source change.
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
- The CV carries a `<!-- publications -->` placeholder inside its
  `## Publications` section; the build replaces it with the publication
  list rendered from src/content/publications.yaml (the same source of
  truth the homepage uses). Cached citation counts are read from the YAML
  so the resume/CV build makes no network calls.
- Print CSS targets US Letter at 10.5pt ETBook body, hairline #d0d0c8
  rule color. No bold weight is loaded; any <strong> in the source
  renders as small-caps via the template's global strong rule.
- ETBook font files are bundled under scripts/fonts/et-book/ (MIT license).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt
from weasyprint import HTML

from _common import install_git_hooks
from _publications import load_publications, render_cv_entries

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "src" / "content"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
FONT_DIR = Path(__file__).resolve().parent / "fonts"

# Each document: markdown source, the two templates, the two outputs, and
# whether the body carries a <!-- publications --> placeholder to fill from
# publications.yaml. Adding a document is a new entry here.
DOCS = [
    {
        "name": "resume",
        "src": CONTENT_DIR / "resume.md",
        "pdf_template": "resume/resume.html",
        "web_template": "resume/resume-web.html",
        "out_pdf": ROOT / "resume.pdf",
        "out_html": ROOT / "resume.html",
        "publications": False,
    },
    {
        "name": "cv",
        "src": CONTENT_DIR / "cv.md",
        "pdf_template": "resume/cv.html",
        "web_template": "resume/cv-web.html",
        "out_pdf": ROOT / "cv.pdf",
        "out_html": ROOT / "cv.html",
        "publications": True,
    },
]

PUBLICATIONS_PLACEHOLDER = "<!-- publications -->"

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
        # CV-only sections (resume.md never emits these, so the resume
        # rendering is unaffected):
        "Research Interests": "interests",
        "Appointments": "appointments",
        "Publications": "pubs",
        "Presentations": "talks",
        "Grants and Funding": "grants",
        "Service and Professional Activities": "service",
        "Awards and Honors": "awards",
        "Technical Skills": "skills",
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


def inject_publications(body_html: str) -> str:
    """Replace the <!-- publications --> placeholder with the CV pub list.

    Reads cached citation counts from publications.yaml (no network call).
    """
    if PUBLICATIONS_PLACEHOLDER not in body_html:
        print(
            f"  WARN: {PUBLICATIONS_PLACEHOLDER} not found; "
            f"skipping publications injection",
            file=sys.stderr,
        )
        return body_html
    entries = render_cv_entries(load_publications())
    return body_html.replace(PUBLICATIONS_PLACEHOLDER, entries)


def render(doc: dict, env: Environment) -> None:
    src = doc["src"]
    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr)
        sys.exit(1)

    md_text = src.read_text(encoding="utf-8")
    md = make_markdown()
    raw_html = md.render(md_text)

    name, contact, remaining = split_header(raw_html)
    remaining = transform_role_blocks(remaining)
    remaining = wrap_sections(remaining)
    if doc["publications"]:
        remaining = inject_publications(remaining)

    pdf_body = (
        f'<div class="hdr-name">{name}</div>\n'
        f'<div class="hdr-contact">{contact}</div>\n'
        f'{remaining}'
    )
    web_body = (
        f'<h1>{name}</h1>\n'
        f'<p class="contact">{contact}</p>\n'
        f'{remaining}'
    )

    out_pdf = doc["out_pdf"]
    pdf_html = env.get_template(doc["pdf_template"]).render(
        name=name,
        body=pdf_body,
        font_dir=str(FONT_DIR),
    )
    pdf_bytes = HTML(string=pdf_html, base_url=str(ROOT)).write_pdf()
    out_pdf.write_bytes(pdf_bytes)
    print(f"wrote {out_pdf.relative_to(ROOT)} ({len(pdf_bytes):,} bytes)")

    out_html = doc["out_html"]
    web_html = env.get_template(doc["web_template"]).render(
        name=name,
        body=web_body,
    )
    out_html.write_text(web_html, encoding="utf-8")
    print(f"wrote {out_html.relative_to(ROOT)} ({len(web_html):,} bytes)")


def main() -> None:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape([]),  # body is pre-rendered HTML
    )
    for doc in DOCS:
        render(doc, env)


if __name__ == "__main__":
    main()
