#!/usr/bin/env python3
"""
build_blog.py

Reads markdown + YAML frontmatter from src/content/blog/*.md,
renders each to blog/<slug>/index.html using Jinja2 templates,
rebuilds blog/index.html listing, regenerates sitemap.xml.

Design notes:
- Math uses LaTeX-style delimiters: \(...\) for inline and \[...\]
  for display. Dollar signs are deliberately not supported — posts
  mix currency amounts with prose, and $...$ pairs would collide.
  Math is stashed before markdown parsing so backslashes and other
  LaTeX syntax aren't mangled, then restored verbatim for KaTeX
  auto-render to pick up client-side.
- Fenced `mermaid` blocks are rewritten to <pre class="mermaid">
  so Mermaid.js picks them up.
- draft: true posts are excluded from both output and listing.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import frontmatter
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.deflist import deflist_plugin

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "src" / "content" / "blog"
OUT_DIR = ROOT / "blog"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
SITE_URL = "https://zaherkarp.com"

MATH_DISPLAY_RE = re.compile(r"\\\[(.+?)\\\]", re.DOTALL)
MATH_INLINE_RE = re.compile(r"\\\((.+?)\\\)", re.DOTALL)
# Fenced code blocks and inline code — regions where math delimiters must NOT
# be interpreted (a shell tutorial can legitimately contain `\(` or `\[`).
CODE_REGION_RE = re.compile(r"(?:^```[\s\S]*?^```)|(?:`[^`\n]+`)", re.MULTILINE)
MERMAID_PRE_RE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>',
    re.DOTALL,
)


def protect_math(text: str) -> tuple[str, list[str]]:
    """
    Replace \\(...\\) / \\[...\\] math with placeholders, but only in prose
    regions. Code fences and inline code are passed through untouched so
    examples that legitimately contain backslash-paren or backslash-bracket
    aren't mis-read as math.
    """
    stash: list[str] = []

    def stash_it(match: re.Match) -> str:
        stash.append(match.group(0))
        return f"@@MATHSTASH{len(stash) - 1}@@"

    def protect_prose(prose: str) -> str:
        prose = MATH_DISPLAY_RE.sub(stash_it, prose)
        prose = MATH_INLINE_RE.sub(stash_it, prose)
        return prose

    parts: list[str] = []
    pos = 0
    for match in CODE_REGION_RE.finditer(text):
        parts.append(protect_prose(text[pos : match.start()]))
        parts.append(match.group(0))
        pos = match.end()
    parts.append(protect_prose(text[pos:]))
    return "".join(parts), stash


def restore_math(html: str, stash: list[str]) -> str:
    for i, raw in enumerate(stash):
        html = html.replace(f"@@MATHSTASH{i}@@", raw)
    return html


def rewrite_mermaid(html: str) -> str:
    def replace(match: re.Match) -> str:
        body = match.group(1)
        # markdown-it escapes & < > inside code; unescape for mermaid to read raw
        body = (
            body.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
        )
        return f'<pre class="mermaid">{body}</pre>'

    return MERMAID_PRE_RE.sub(replace, html)


def make_markdown() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": True})
    md.enable(["table", "strikethrough"])
    md.use(footnote_plugin)
    md.use(deflist_plugin)
    return md


def as_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    raise ValueError(f"Cannot interpret publishDate: {value!r}")


def format_human_date(d: date) -> str:
    return d.strftime("%B %-d, %Y")


def parse_post(path: Path, md: MarkdownIt) -> dict:
    post = frontmatter.load(path)
    meta = post.metadata
    title = meta.get("title")
    if not title:
        raise ValueError(f"{path.name}: missing title")
    description = meta.get("description", "")
    publish_date = as_date(meta.get("publishDate"))
    draft = bool(meta.get("draft", False))
    tags = meta.get("tags", []) or []

    body_md = post.content
    # Strip a leading H1 if it duplicates the title (Astro posts often repeat it)
    body_md = re.sub(
        r"^\s*#\s+" + re.escape(title.strip()) + r"\s*\n+",
        "",
        body_md,
        count=1,
    )

    has_mermaid = "```mermaid" in body_md

    protected, stash = protect_math(body_md)
    # Stash only contains math found in prose regions — code-region `$`s don't count.
    has_math = len(stash) > 0
    html = md.render(protected)
    html = restore_math(html, stash)
    if has_mermaid:
        html = rewrite_mermaid(html)

    # has_code: any fenced code block other than mermaid became <pre><code class="language-...">
    has_code = '<pre><code class="language-' in html

    slug = path.stem
    return {
        "slug": slug,
        "title": title,
        "description": description,
        "publish_date": publish_date,
        "publish_date_iso": publish_date.isoformat(),
        "publish_date_human": format_human_date(publish_date),
        "tags": tags,
        "draft": draft,
        "body_html": html,
        "has_math": has_math,
        "has_mermaid": has_mermaid,
        "has_code": has_code,
    }


def build_article_jsonld(post: dict) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post["title"],
        "description": post["description"],
        "datePublished": f"{post['publish_date_iso']}T00:00:00Z",
        "author": {
            "@type": "Person",
            "name": "Zaher Karp",
            "url": SITE_URL,
        },
    }
    # Escape </ to prevent breaking out of the <script> tag if title/description contain it.
    return json.dumps(data).replace("</", "<\\/")


def render_post(env: Environment, post: dict, current_year: int) -> str:
    template = env.get_template("blog/post.html")
    return template.render(
        page_title=f"{post['title']} — Zaher Karp",
        page_description=post["description"],
        canonical_url=f"{SITE_URL}/blog/{post['slug']}/",
        og_type="article",
        title=post["title"],
        tags=post["tags"],
        publish_date_iso=post["publish_date_iso"],
        publish_date_human=post["publish_date_human"],
        body_html=post["body_html"],
        has_math=post["has_math"],
        has_mermaid=post["has_mermaid"],
        has_code=post["has_code"],
        article_json_ld=build_article_jsonld(post),
        current_year=current_year,
    )


# Posts published before this date are treated as archive — rendered on
# /blog/archive/ instead of /blog/. The 2009-2011 posts are undergrad-era
# writing (sustainability, education, interviews) that predate the current
# healthcare-data-engineering portfolio voice.
ARCHIVE_CUTOFF = date(2019, 1, 1)

EXPERIMENTS = [
    {
        "url": "/life-in-weeks/",
        "title": "Life in Weeks",
        "description": "A life, 4,680 weeks. Each square is one. Inspired by Tim Urban.",
    },
]

SUBPAGES = [
    "/star-rating-predictor/",
    "/life-in-weeks/",
    "/skillsprout/",
]


def render_current_index(env: Environment, posts: list[dict], archive_count: int, current_year: int) -> str:
    template = env.get_template("blog/list.html")
    archive_link = None
    if archive_count:
        archive_link = {
            "url": "/blog/archive/",
            "label": f"Earlier writing ({archive_count} posts, 2009–2011) →",
        }
    return template.render(
        page_title="Writing — Zaher Karp",
        page_description="Long-form writing on healthcare data engineering, Medicare Advantage Stars methodology, and production analytics.",
        canonical_url=f"{SITE_URL}/blog/",
        section_label="Writing",
        intro="Long-form writing on healthcare data engineering, Medicare Advantage Stars methodology, and the places where CMS Technical Notes and production reality diverge.",
        posts=posts,
        archive_link=archive_link,
        experiments=EXPERIMENTS,
        current_year=current_year,
    )


def render_archive_index(env: Environment, posts: list[dict], current_year: int) -> str:
    template = env.get_template("blog/list.html")
    return template.render(
        page_title="Archive — Zaher Karp",
        page_description="Earlier writing from 2009–2011, before the healthcare data engineering focus. Green building, education, and interviews.",
        canonical_url=f"{SITE_URL}/blog/archive/",
        section_label="Archive",
        intro="Earlier writing from 2009–2011. Green building, education, interviews — kept online for provenance, not portfolio.",
        posts=posts,
        back_link={"url": "/blog/", "label": "← Current writing"},
        current_year=current_year,
    )


def write_sitemap(current_posts: list[dict], archive_posts: list[dict]) -> None:
    urls = [f"{SITE_URL}/", f"{SITE_URL}/blog/"]
    urls.extend(f"{SITE_URL}{p}" for p in SUBPAGES)
    urls.extend(f"{SITE_URL}/blog/{p['slug']}/" for p in current_posts)
    if archive_posts:
        urls.append(f"{SITE_URL}/blog/archive/")
        urls.extend(f"{SITE_URL}/blog/{p['slug']}/" for p in archive_posts)

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        lines.append(f"  <url><loc>{url}</loc></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def clean_output_dir() -> None:
    if OUT_DIR.exists():
        for child in OUT_DIR.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        OUT_DIR.mkdir(parents=True)


def main() -> int:
    if not POSTS_DIR.exists():
        print(f"error: {POSTS_DIR} does not exist", file=sys.stderr)
        return 1

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=False,
        lstrip_blocks=False,
    )

    md = make_markdown()
    current_year = datetime.now(timezone.utc).year

    posts: list[dict] = []
    skipped_errors = 0
    for path in sorted(POSTS_DIR.glob("*.md")):
        if path.stem.startswith("_"):
            continue
        try:
            post = parse_post(path, md)
        except Exception as exc:
            print(f"warning: skipping {path.name}: {exc}", file=sys.stderr)
            skipped_errors += 1
            continue
        if post["draft"]:
            print(f"skip draft: {path.name}")
            continue
        posts.append(post)
    if skipped_errors:
        print(f"warning: {skipped_errors} post(s) skipped due to errors", file=sys.stderr)

    posts.sort(key=lambda p: p["publish_date"], reverse=True)

    current_posts = [p for p in posts if p["publish_date"] >= ARCHIVE_CUTOFF]
    archive_posts = [p for p in posts if p["publish_date"] < ARCHIVE_CUTOFF]

    clean_output_dir()

    for post in posts:
        out_dir = OUT_DIR / post["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(
            render_post(env, post, current_year), encoding="utf-8"
        )
        print(f"wrote blog/{post['slug']}/index.html")

    (OUT_DIR / "index.html").write_text(
        render_current_index(env, current_posts, len(archive_posts), current_year),
        encoding="utf-8",
    )
    print(f"wrote blog/index.html ({len(current_posts)} posts)")

    if archive_posts:
        archive_dir = OUT_DIR / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "index.html").write_text(
            render_archive_index(env, archive_posts, current_year), encoding="utf-8"
        )
        print(f"wrote blog/archive/index.html ({len(archive_posts)} posts)")

    write_sitemap(current_posts, archive_posts)
    archive_url_count = (1 + len(archive_posts)) if archive_posts else 0
    total_urls = 2 + len(SUBPAGES) + len(current_posts) + archive_url_count
    print(f"wrote sitemap.xml ({total_urls} urls)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
