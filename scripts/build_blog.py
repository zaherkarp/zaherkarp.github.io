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

import email.utils
import json
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path

import frontmatter
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.deflist import deflist_plugin

from _common import install_git_hooks

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "src" / "content" / "blog"
OUT_DIR = ROOT / "blog"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
SITE_URL = "https://zaherkarp.com"
FEED_MAX_ITEMS = 30
WORDS_PER_MINUTE = 250

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


def format_rfc822(d: date) -> str:
    """RFC 822 date format for RSS pubDate, anchored at 00:00 UTC."""
    return email.utils.format_datetime(datetime.combine(d, time.min, tzinfo=timezone.utc))


_WORD_STRIP_RE = re.compile(
    r"(?:^```[\s\S]*?^```)"          # fenced code blocks
    r"|(?:`[^`\n]+`)"                 # inline code
    r"|(?:\\\[[\s\S]+?\\\])"          # display math \[...\]
    r"|(?:\\\(.+?\\\))"                # inline math \(...\)
    r"|(?:<!--[\s\S]*?-->)",          # html comments
    re.MULTILINE,
)
_WORD_TOKEN_RE = re.compile(r"[A-Za-z0-9'’]+")


def count_words(markdown_body: str) -> int:
    """Approximate word count, excluding code, math, and comments."""
    prose = _WORD_STRIP_RE.sub(" ", markdown_body)
    return len(_WORD_TOKEN_RE.findall(prose))


def reading_time_minutes(word_count: int) -> int:
    return max(1, round(word_count / WORDS_PER_MINUTE))


def git_iso_lastmod(path: Path) -> str | None:
    """Last commit date for `path` as an ISO 8601 string, or None outside a git repo / on first commit."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    out = result.stdout.strip()
    return out or None


def git_short_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    out = result.stdout.strip()
    return out or None


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
    word_count = count_words(body_md)
    minutes = reading_time_minutes(word_count)
    return {
        "slug": slug,
        "title": title,
        "description": description,
        "publish_date": publish_date,
        "publish_date_iso": publish_date.isoformat(),
        "publish_date_human": format_human_date(publish_date),
        "publish_date_rfc822": format_rfc822(publish_date),
        "modified_iso": git_iso_lastmod(path) or f"{publish_date.isoformat()}T00:00:00Z",
        "tags": tags,
        "draft": draft,
        "body_html": html,
        "has_math": has_math,
        "has_mermaid": has_mermaid,
        "has_code": has_code,
        "word_count": word_count,
        "reading_minutes": minutes,
        "reading_iso": f"PT{minutes}M",
    }


def build_article_jsonld(post: dict) -> str:
    post_url = f"{SITE_URL}/blog/{post['slug']}/"
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": post["description"],
        "url": post_url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": post_url},
        "datePublished": f"{post['publish_date_iso']}T00:00:00Z",
        "dateModified": post["modified_iso"],
        "author": {
            "@type": "Person",
            "name": "Zaher Karp",
            "url": SITE_URL,
        },
        "publisher": {
            "@type": "Person",
            "name": "Zaher Karp",
            "url": SITE_URL,
        },
        "image": f"{SITE_URL}/og-default.png",
        "wordCount": post["word_count"],
        "timeRequired": post["reading_iso"],
        "inLanguage": "en-US",
    }
    if post.get("tags"):
        data["keywords"] = ", ".join(post["tags"])
    # Escape </ to prevent breaking out of the <script> tag if title/description contain it.
    return json.dumps(data).replace("</", "<\\/")


def render_post(env: Environment, post: dict, current_year: int, build_info: dict) -> str:
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
        word_count=post["word_count"],
        reading_minutes=post["reading_minutes"],
        body_html=post["body_html"],
        has_math=post["has_math"],
        has_mermaid=post["has_mermaid"],
        has_code=post["has_code"],
        article_json_ld=build_article_jsonld(post),
        current_year=current_year,
        build_info=build_info,
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
    "/epidemic-simulation/",
]


def render_current_index(env: Environment, posts: list[dict], archive_count: int, current_year: int, build_info: dict, totals: dict) -> str:
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
        build_info=build_info,
        totals=totals,
    )


def render_archive_index(env: Environment, posts: list[dict], current_year: int, build_info: dict) -> str:
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
        build_info=build_info,
    )


def render_feed(env: Environment, posts: list[dict], build_info: dict) -> str:
    template = env.get_template("blog/feed.xml.j2")
    return template.render(
        site_url=SITE_URL,
        feed_url=f"{SITE_URL}/blog/feed.xml",
        blog_url=f"{SITE_URL}/blog/",
        posts=posts[:FEED_MAX_ITEMS],
        build_date_rfc822=build_info["build_date_rfc822"],
    )


def _subpage_lastmod(subpage_path: str) -> str | None:
    candidate = ROOT / subpage_path.strip("/") / "index.html"
    return git_iso_lastmod(candidate)


def write_sitemap(current_posts: list[dict], archive_posts: list[dict]) -> None:
    homepage_lastmod = git_iso_lastmod(ROOT / "index.html")
    newest_post_iso = (
        f"{current_posts[0]['publish_date_iso']}T00:00:00Z" if current_posts else None
    )

    urls: list[dict] = [
        {"loc": f"{SITE_URL}/", "lastmod": homepage_lastmod},
        {"loc": f"{SITE_URL}/blog/", "lastmod": newest_post_iso},
    ]
    for p in SUBPAGES:
        urls.append({"loc": f"{SITE_URL}{p}", "lastmod": _subpage_lastmod(p)})
    for p in current_posts:
        urls.append({
            "loc": f"{SITE_URL}/blog/{p['slug']}/",
            "lastmod": p["modified_iso"],
        })
    if archive_posts:
        urls.append({"loc": f"{SITE_URL}/blog/archive/", "lastmod": None})
        for p in archive_posts:
            urls.append({
                "loc": f"{SITE_URL}/blog/{p['slug']}/",
                "lastmod": p["modified_iso"],
            })

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        if u["lastmod"]:
            lines.append(f"  <url><loc>{u['loc']}</loc><lastmod>{u['lastmod']}</lastmod></url>")
        else:
            lines.append(f"  <url><loc>{u['loc']}</loc></url>")
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
    now_utc = datetime.now(timezone.utc)
    current_year = now_utc.year
    build_info = {
        "build_iso": now_utc.isoformat(timespec="seconds"),
        "build_date_human": now_utc.strftime("%Y-%m-%d"),
        "build_date_rfc822": email.utils.format_datetime(now_utc),
        "build_sha": git_short_sha(),
    }

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

    totals = {
        "post_count": len(current_posts),
        "word_count": sum(p["word_count"] for p in current_posts),
        "archive_post_count": len(archive_posts),
    }

    clean_output_dir()

    for post in posts:
        out_dir = OUT_DIR / post["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(
            render_post(env, post, current_year, build_info), encoding="utf-8"
        )
        print(f"wrote blog/{post['slug']}/index.html")

    (OUT_DIR / "index.html").write_text(
        render_current_index(env, current_posts, len(archive_posts), current_year, build_info, totals),
        encoding="utf-8",
    )
    print(f"wrote blog/index.html ({len(current_posts)} posts)")

    if archive_posts:
        archive_dir = OUT_DIR / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "index.html").write_text(
            render_archive_index(env, archive_posts, current_year, build_info), encoding="utf-8"
        )
        print(f"wrote blog/archive/index.html ({len(archive_posts)} posts)")

    (OUT_DIR / "feed.xml").write_text(
        render_feed(env, current_posts, build_info), encoding="utf-8"
    )
    print(f"wrote blog/feed.xml ({min(len(current_posts), FEED_MAX_ITEMS)} items)")

    write_sitemap(current_posts, archive_posts)
    archive_url_count = (1 + len(archive_posts)) if archive_posts else 0
    total_urls = 2 + len(SUBPAGES) + len(current_posts) + archive_url_count
    print(f"wrote sitemap.xml ({total_urls} urls)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
