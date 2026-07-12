#!/usr/bin/env python3
"""lint_links.py

Internal link and anchor integrity for the homepage and the sitemap.
README §Before pushing used to ask a human to click every internal
anchor; this is the mechanical part of that check, automated.

Three checks:

  1. ANCHORS: every fragment href (`href="#..."`) in index.html resolves
     to a real `id=` in index.html. Ids and hrefs inside HTML comments,
     `<style>`, or `<script>` blocks are ignored on BOTH sides -- an id
     mentioned in a CSS comment is grep-visible but not a jump target,
     so it must not satisfy an anchor.

  2. BLOG LINKS: every `/blog/...` href in index.html resolves to built
     blog output on disk (`/blog/<slug>/` -> `blog/<slug>/index.html`;
     `/blog/feed.xml` -> the literal file). Deliberately scoped to
     `/blog/` for homepage file links: other root-relative targets
     include `/medicare-advantage-insight-engine/`, which is served by a
     SEPARATE repo's GitHub Pages under the shared custom domain
     (CLAUDE.md §Links) and has no directory here, so a wider check
     would false-positive by design.

  3. SITEMAP: every `<loc>` in sitemap.xml resolves to a real file in
     the repo (URL path relative to the domain root; a trailing slash
     resolves to that directory's index.html).

GATE (hard fail, blocks push). Wired into scripts/hooks/pre-push and
.github/workflows/lint.yml. If a check fails, fix the content (the
dead link, the missing built output, the stale sitemap entry) -- do
not weaken the linter.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _common import install_git_hooks

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent

INDEX = "index.html"
SITEMAP = "sitemap.xml"

# Comments and style/script bodies are inert for anchor purposes: an id
# quoted in a CSS comment is not a jump target, and a fragment href in a
# commented-out block is not a live link.
_INERT_RE = re.compile(
    r"<!--.*?-->|<style[^>]*>.*?</style>|<script[^>]*>.*?</script>",
    re.DOTALL | re.IGNORECASE,
)

# (?<![-\w]) keeps attribute tails like data-sid="PMID:..." from being
# read as id="..." -- the hyphen/word char before "id" disqualifies it.
_ID_RE = re.compile(r"""(?<![-\w])id=["']([^"']+)["']""")
_FRAGMENT_HREF_RE = re.compile(r"""href=["']#([^"']*)["']""")
# Path capture stops at a fragment or query; href="/blog/x/#y" checks /blog/x/.
_BLOG_HREF_RE = re.compile(r"""href=["'](/blog/[^"'#?]*)[^"']*["']""")
_LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
_SCHEME_HOST_RE = re.compile(r"^https?://[^/]+")


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def blank_inert(html: str) -> str:
    """Blank comments / <style> / <script> bodies, preserving line numbers."""
    return _INERT_RE.sub(lambda m: "\n" * m.group().count("\n"), html)


def check_anchors(html: str, rel: str = INDEX) -> tuple[int, list[str]]:
    """Every live fragment href must match a live id. Returns (checked, failures)."""
    visible = blank_inert(html)
    ids = {m.group(1) for m in _ID_RE.finditer(visible)}
    checked = 0
    failures: list[str] = []
    for m in _FRAGMENT_HREF_RE.finditer(visible):
        checked += 1
        frag = m.group(1)
        if frag not in ids:
            failures.append(
                f'{rel}:{_line_of(visible, m.start())}: href="#{frag}" has '
                f"no matching id= in {rel}."
            )
    return checked, failures


def _target_file(root: Path, url_path: str) -> Path:
    """The repo file a site-root-relative URL path serves."""
    rel = url_path.lstrip("/")
    if rel == "" or url_path.endswith("/"):
        return root / rel / "index.html"
    return root / rel


def check_blog_links(
    html: str, root: Path, rel: str = INDEX
) -> tuple[int, list[str]]:
    """Every /blog/... href must resolve to built output on disk."""
    visible = blank_inert(html)
    checked = 0
    failures: list[str] = []
    for m in _BLOG_HREF_RE.finditer(visible):
        checked += 1
        href = m.group(1)
        target = _target_file(root, href)
        if not target.is_file():
            failures.append(
                f'{rel}:{_line_of(visible, m.start())}: href="{href}" does '
                f"not resolve to {target.relative_to(root)} (post not built, "
                f"or slug drifted from the built output)."
            )
    return checked, failures


def check_sitemap(
    xml_text: str, root: Path, rel: str = SITEMAP
) -> tuple[int, list[str]]:
    """Every <loc> must resolve to a real file in the repo."""
    checked = 0
    failures: list[str] = []
    for m in _LOC_RE.finditer(xml_text):
        checked += 1
        loc = m.group(1)
        path = _SCHEME_HOST_RE.sub("", loc)
        target = _target_file(root, path)
        if not target.is_file():
            failures.append(
                f"{rel}:{_line_of(xml_text, m.start())}: <loc> {loc} does "
                f"not resolve to {target.relative_to(root)}."
            )
    return checked, failures


def run() -> int:
    failures: list[str] = []
    counts: list[str] = []

    index_path = ROOT / INDEX
    if index_path.is_file():
        html = index_path.read_text(encoding="utf-8")
        n_anchors, anchor_failures = check_anchors(html)
        n_blog, blog_failures = check_blog_links(html, ROOT)
        failures.extend(anchor_failures)
        failures.extend(blog_failures)
        counts.append(f"{n_anchors} anchors")
        counts.append(f"{n_blog} /blog/ links")

    sitemap_path = ROOT / SITEMAP
    if sitemap_path.is_file():
        n_locs, loc_failures = check_sitemap(
            sitemap_path.read_text(encoding="utf-8"), ROOT
        )
        failures.extend(loc_failures)
        counts.append(f"{n_locs} sitemap locs")

    if failures:
        print("Link lint found problems:\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(
            f"\n{len(failures)} dead internal link(s). Fix the link, the "
            f"built output, or the sitemap entry -- see CLAUDE.md "
            f"§Pre-push checks.",
            file=sys.stderr,
        )
        return 1

    print(f"link lint: {', '.join(counts)} all resolve")
    return 0


if __name__ == "__main__":
    sys.exit(run())
