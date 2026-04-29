#!/usr/bin/env python3
"""
build_portfolio.py

Injects three pieces of build-time content into index.html, between marker
comments:

  <!-- activity-grid:start --> ... <!-- activity-grid:end -->
    24-week dot sparkline showing recent posting cadence. Sourced from the
    blog frontmatter (publishDate, draft). No external requests.

  <!-- writing-list:start --> ... <!-- writing-list:end -->
    The six most recent non-draft posts, rendered as the homepage Writing
    section's entries. Sourced from the same blog frontmatter; the
    optional `homepageMarginnote` field renders an inline margin note
    next to the entry title.

  <div class="pub-entry" data-sid="..."> ... </div>
    Semantic Scholar citation counts. Fetched per `data-sid` attribute;
    injected as <span class="pub-citations"> inside each entry. On fetch
    failure the existing text is left untouched (so a flaky network or
    rate-limit doesn't wipe prior values).

The script is idempotent: running it twice with the same inputs produces
the same output. See .github/workflows/build_portfolio.yml for the CI
trigger.
"""

from __future__ import annotations

import html as html_lib
import json
import re
import sys
import time
import urllib.request
import urllib.error
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
POSTS_DIR = ROOT / "src" / "content" / "blog"
WRITING_LIST_LIMIT = 6
# Activity sparkline window: 24 weeks ending at the most recent Sunday.
# Tufte-inspired inline sparkline that replaces the prior 52-week heatmap
# grid. The pre-2025 journalism pieces live in the blog but aren't part
# of this cadence story; PRE_BLOG_CUTOFF excludes them from the cadence
# total when computing the trailing post count.
SPARKLINE_WEEKS = 24
SPARKLINE_X0 = 10        # left x-coordinate of the first dot in the SVG
SPARKLINE_DX = 11        # spacing between dots; matches the demo's geometry
PRE_BLOG_CUTOFF = date(2025, 1, 1)
# Cadence-marginnote tag list: tags appearing in at least this many cadence-
# window posts qualify for the frequency rollup. Single-occurrence tags are
# filtered out so the long tail of one-offs doesn't drown the multi-post
# signal. Fallback: if fewer than CADENCE_TAGS_MIN_FLOOR tags qualify, the
# top CADENCE_TAGS_MIN_FLOOR by frequency are shown regardless.
CADENCE_TAG_MIN_COUNT = 2
CADENCE_TAGS_MIN_FLOOR = 8
S2_TIMEOUT = 10  # seconds
S2_URL = "https://api.semanticscholar.org/graph/v1/paper/{sid}?fields=citationCount"


# ─── activity grid ────────────────────────────────────────────────────────

def _esc(s: str) -> str:
    return html_lib.escape(s, quote=False)


def load_posts() -> list[dict]:
    posts: list[dict] = []
    for p in POSTS_DIR.glob("*.md"):
        if p.stem.startswith("_"):
            continue
        fm = frontmatter.load(p)
        if fm.metadata.get("draft"):
            continue
        d = fm.metadata.get("publishDate")
        if isinstance(d, str):
            d = date.fromisoformat(d)
        elif isinstance(d, datetime):
            d = d.date()
        if not isinstance(d, date):
            continue
        raw_tags = fm.metadata.get("tags") or []
        tags = [str(t).strip().lower() for t in raw_tags if str(t).strip()]
        posts.append({
            "date": d,
            "title": fm.metadata.get("title", ""),
            "description": fm.metadata.get("description", ""),
            "slug": p.stem,
            "marginnote": fm.metadata.get("homepageMarginnote", ""),
            "tags": tags,
        })
    return posts


def last_sunday(today: date) -> date:
    # Python weekday(): Mon=0..Sun=6
    return today if today.weekday() == 6 else today - timedelta(days=today.weekday() + 1)


def build_cadence_marginnote(cadence_posts: list[dict]) -> str:
    """Render the cadence ⊕ margin note as a tag frequency rollup.

    Aggregates tags across the cadence window (post-2025), keeps tags
    appearing in ≥ CADENCE_TAG_MIN_COUNT posts, and falls back to the
    top CADENCE_TAGS_MIN_FLOOR by count if too few qualify. Sorted by
    count desc, then alphabetic. Rendered as compact `tag (n)` pairs
    separated by middle dots.
    """
    counter: Counter[str] = Counter()
    for p in cadence_posts:
        for t in p["tags"]:
            counter[t] += 1
    if not counter:
        return ""

    qualifying = [(t, n) for t, n in counter.items() if n >= CADENCE_TAG_MIN_COUNT]
    if len(qualifying) < CADENCE_TAGS_MIN_FLOOR:
        qualifying = counter.most_common(CADENCE_TAGS_MIN_FLOOR)
    qualifying.sort(key=lambda kv: (-kv[1], kv[0]))

    pairs = " · ".join(f"{_esc(tag)} ({n})" for tag, n in qualifying)
    return pairs


def build_activity_grid(posts: list[dict]) -> str:
    """Emit the 24-week inline cadence sparkline.

    Tufte's last-point-label pattern: a small numeric annotation at the
    end of the sparkline gives the trailing total so the chart is self-
    legending. The ⊕ margin note expands into a tag frequency rollup
    (multi-post tags within the cadence window).
    """
    anchor = last_sunday(date.today())
    cadence_posts = [p for p in posts if p["date"] >= PRE_BLOG_CUTOFF]
    if not cadence_posts:
        return ""

    dots: list[str] = []
    cadence_total_in_window = 0
    for i in range(SPARKLINE_WEEKS - 1, -1, -1):
        week_end = anchor - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        n = sum(1 for p in posts if week_start <= p["date"] <= week_end and p["date"] >= PRE_BLOG_CUTOFF)
        cadence_total_in_window += n
        cx = SPARKLINE_X0 + (SPARKLINE_WEEKS - 1 - i) * SPARKLINE_DX
        # Filled = publication week, empty = silent week. The hardcoded
        # hex values are intentional: index.html's <style> block has CSS
        # attribute selectors that map them to var(--ink) and var(--rule)
        # so the same SVG renders correctly in both light and dark mode.
        fill = "#111" if n > 0 else "#d0d0c8"
        dots.append(f'        <circle cx="{cx}" cy="10" r="2" fill="{fill}"/>')

    label = "post" if cadence_total_in_window == 1 else "posts"
    tag_rollup = build_cadence_marginnote(cadence_posts)
    marginnote_html = (
        f'<span class="marginnote">{tag_rollup}</span>' if tag_rollup else ""
    )
    return (
        '<p style="color: var(--muted); font-size: 1.05rem; margin-bottom: 1.4rem;">\n'
        '      24 weeks of activity\n'
        '      <svg class="cadence" viewBox="0 0 280 20" width="280" height="20" '
        'aria-label="writing cadence sparkline, 24 weeks">\n'
        '        <line x1="10" y1="16" x2="263" y2="16" stroke="#d0d0c8" stroke-width="0.5"/>\n'
        + "\n".join(dots) + "\n"
        '      </svg>\n'
        f'      <span style="font-variant-numeric: oldstyle-nums; color: var(--ink); '
        f'margin-left: 0.3rem;">{cadence_total_in_window} {label}</span>'
        '<label for="mn-cadence" class="margin-toggle">&#8853;</label>'
        '<input type="checkbox" id="mn-cadence" class="margin-toggle"/>'
        f'{marginnote_html}\n'
        '    </p>'
    )


# ─── homepage writing list ────────────────────────────────────────────────

# Em-dash policy (CLAUDE.md): the homepage must be em-dash-clean, but
# blog post markdown sources are deliberately not swept (preserves
# historical voice). When the writing list pulls a frontmatter
# description into the homepage, strip em-dashes back to commas so the
# generated chrome stays compliant. Source posts keep their em-dashes
# in /blog/<slug>/.
EM_DASH_RE = re.compile(r"\s*—\s*")


def _strip_em_dashes(s: str) -> str:
    return EM_DASH_RE.sub(", ", s)


def build_writing_list(posts: list[dict]) -> str:
    """Emit the homepage Writing section's six most recent post entries.

    Sorted by publishDate desc. Drafts and `_`-prefixed sources are
    already filtered out in load_posts(). Optional `homepageMarginnote`
    frontmatter renders an inline ⊕ margin note next to the title; the
    toggle id is `mn-w-<slug>` so it stays unique across entries.
    """
    recent = sorted(posts, key=lambda p: p["date"], reverse=True)[:WRITING_LIST_LIMIT]
    blocks: list[str] = []
    for p in recent:
        date_str = p["date"].isoformat()
        title = _esc(_strip_em_dashes(p["title"]))
        desc = _esc(_strip_em_dashes(p["description"]))
        slug = p["slug"]
        marginnote = _strip_em_dashes((p["marginnote"] or "").strip())
        if marginnote:
            mn_id = f"mn-w-{slug}"
            margin_html = (
                f'\n        <label for="{mn_id}" class="margin-toggle">&#8853;</label>'
                f'<input type="checkbox" aria-label="Toggle margin note" id="{mn_id}" class="margin-toggle"/>'
                f'<span class="marginnote">{_esc(marginnote)}</span>'
            )
        else:
            margin_html = ""
        blocks.append(
            '    <div class="entry">\n'
            '      <div>\n'
            f'        <span class="date">{date_str}</span>\n'
            f'        <span class="title"><a href="/blog/{slug}/">{title}</a></span>'
            f'{margin_html}\n'
            '      </div>\n'
            f'      <p class="summary">{desc}</p>\n'
            '    </div>'
        )
    return "\n\n".join(blocks)


# ─── Semantic Scholar citation counts ─────────────────────────────────────

def fetch_citation_count(sid: str, retries: int = 3) -> int | None:
    url = S2_URL.format(sid=sid)
    req = urllib.request.Request(url, headers={"User-Agent": "zaherkarp-site-build"})
    backoff = 2
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=S2_TIMEOUT) as resp:
                data = json.load(resp)
                count = data.get("citationCount")
                return int(count) if isinstance(count, int) else None
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 2
                continue
            print(f"  semantic-scholar fetch failed for {sid}: {e}", file=sys.stderr)
            return None
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            print(f"  semantic-scholar fetch failed for {sid}: {e}", file=sys.stderr)
            return None
    return None


PUB_ENTRY_RE = re.compile(
    # Match any class attribute that contains the token "pub-entry";
    # the new index.html uses class="entry pub-entry" so the leading
    # word may be different.
    r'(<div class="[^"]*pub-entry[^"]*"[^>]*data-sid="([^"]+)"[^>]*>)(.*?)(</div>)',
    re.DOTALL,
)
INNER_CITATION_RE = re.compile(r'(<span class="pub-citations">)([^<]*)(</span>)')


def inject_citations(html: str) -> tuple[str, int, int]:
    """Return (new_html, successes, failures).

    In-place updates only. The static markup decides where the
    citation span lives (inside the marginnote in the new design);
    the script just keeps the count current. Entries without an
    existing pub-citations span are left untouched.
    """
    successes = 0
    failures = 0

    def replace(m: re.Match) -> str:
        nonlocal successes, failures
        open_tag, sid, inner, close_tag = m.group(1), m.group(2), m.group(3), m.group(4)
        if not INNER_CITATION_RE.search(inner):
            return open_tag + inner + close_tag
        if successes + failures > 0:
            time.sleep(1.0)
        count = fetch_citation_count(sid)
        if count is None:
            failures += 1
            return open_tag + inner + close_tag
        successes += 1
        label = "citation" if count == 1 else "citations"
        new_inner = INNER_CITATION_RE.sub(
            lambda im: f'{im.group(1)}{count} {label}{im.group(3)}',
            inner,
        )
        return open_tag + new_inner + close_tag

    new_html = PUB_ENTRY_RE.sub(replace, html)
    return new_html, successes, failures


# ─── marker replacement ───────────────────────────────────────────────────

def replace_between(text: str, marker: str, payload: str, end_indent: str = "    ") -> str:
    pat = re.compile(
        rf'(<!--\s*{re.escape(marker)}:start\s*-->)(.*?)(<!--\s*{re.escape(marker)}:end\s*-->)',
        re.DOTALL,
    )
    if not pat.search(text):
        print(f"  WARN: marker {marker}:start/end not found; skipping", file=sys.stderr)
        return text
    return pat.sub(lambda m: f"{m.group(1)}\n{payload}\n{end_indent}{m.group(3)}", text)


# ─── main ─────────────────────────────────────────────────────────────────

def main() -> int:
    if not INDEX.exists():
        print(f"ERROR: {INDEX} not found", file=sys.stderr)
        return 1

    original = INDEX.read_text()
    text = original

    posts = load_posts()
    print(f"loaded {len(posts)} non-draft posts")

    grid_html = build_activity_grid(posts)
    text = replace_between(text, "activity-grid", grid_html)
    print("activity grid injected")

    writing_html = build_writing_list(posts)
    text = replace_between(text, "writing-list", writing_html)
    print(f"writing list injected ({min(len(posts), WRITING_LIST_LIMIT)} entries)")

    text, ok, fail = inject_citations(text)
    print(f"citation counts: {ok} updated, {fail} skipped (fetch failed)")

    if text != original:
        INDEX.write_text(text)
        print("index.html updated")
    else:
        print("no changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
