#!/usr/bin/env python3
"""
build_portfolio.py

Injects two pieces of build-time content into index.html, between marker
comments:

  <!-- activity-grid:start --> ... <!-- activity-grid:end -->
    52-week dot grid showing recent posting cadence. Sourced from the blog
    frontmatter (publishDate, draft). No external requests.

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

import json
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import date, datetime, timedelta
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
POSTS_DIR = ROOT / "src" / "content" / "blog"
# Activity grid window: from the first published post's week through the
# current week. Bounded by MAX_WEEKS so it doesn't blow out horizontally
# once the archive spans years. The pre-2025 journalism pieces live in
# the blog but aren't part of this cadence story — PRE_BLOG_CUTOFF
# excludes them from the window calculation.
MAX_WEEKS = 52
PRE_BLOG_CUTOFF = date(2025, 1, 1)
S2_TIMEOUT = 10  # seconds
S2_URL = "https://api.semanticscholar.org/graph/v1/paper/{sid}?fields=citationCount"


# ─── activity grid ────────────────────────────────────────────────────────

def load_posts() -> list[tuple[date, str, str]]:
    posts: list[tuple[date, str, str]] = []
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
        posts.append((d, fm.metadata.get("title", ""), p.stem))
    return posts


def last_sunday(today: date) -> date:
    # Python weekday(): Mon=0..Sun=6
    return today if today.weekday() == 6 else today - timedelta(days=today.weekday() + 1)


def build_activity_grid(posts: list[tuple[date, str, str]]) -> str:
    anchor = last_sunday(date.today())
    # Window starts at the first post's week within the cadence era, capped
    # by MAX_WEEKS. Leading zero-post weeks at the left edge are chartjunk
    # (Tufte panel, focus group round 1).
    cadence_posts = [p for p in posts if p[0] >= PRE_BLOG_CUTOFF]
    if not cadence_posts:
        return ""
    first_post_date = min(p[0] for p in cadence_posts)
    first_week_end = last_sunday(first_post_date)
    weeks_span = ((anchor - first_week_end).days // 7) + 1
    weeks_to_render = min(max(weeks_span, 1), MAX_WEEKS)

    dots: list[str] = []
    for i in range(weeks_to_render - 1, -1, -1):
        week_end = anchor - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        matches = [p for p in posts if week_start <= p[0] <= week_end]
        count = len(matches)
        span = f"{week_start:%b %-d}–{week_end:%b %-d}"
        if count == 0:
            cls = "act-dot act-empty"
            tip = f"{span}: no posts"
        else:
            cls = f"act-dot act-n{min(count, 3)}"
            titles = ", ".join(m[1] for m in matches)
            titles = titles.replace('"', "&quot;")
            tip = f"{span}: {titles}"
        dots.append(f'<span class="{cls}" title="{tip}"></span>')

    caption = f"{weeks_to_render} weeks of writing activity"
    return (
        f'<div class="activity-grid" aria-label="{caption}">'
        f'<div class="activity-row">{"".join(dots)}</div>'
        f'<p class="activity-caption">{caption}</p>'
        "</div>"
    )


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
    r'(<div class="pub-entry"[^>]*data-sid="([^"]+)"[^>]*>)(.*?)(</div>)',
    re.DOTALL,
)
EXISTING_CITATION_RE = re.compile(
    r'\s*<span class="pub-citations">[^<]*</span>',
    re.DOTALL,
)


def inject_citations(html: str) -> tuple[str, int, int]:
    """Return (new_html, successes, failures)."""
    successes = 0
    failures = 0

    def replace(m: re.Match) -> str:
        nonlocal successes, failures
        open_tag, sid, inner, close_tag = m.group(1), m.group(2), m.group(3), m.group(4)
        # Small inter-request delay to respect Semantic Scholar's public-tier limits.
        if successes + failures > 0:
            time.sleep(1.0)
        count = fetch_citation_count(sid)

        # Strip any existing citation span so we're idempotent.
        inner_clean = EXISTING_CITATION_RE.sub("", inner).rstrip()

        if count is None:
            failures += 1
            # Keep any pre-existing span (rollback) so we don't clobber on fetch fail.
            return open_tag + inner + close_tag
        successes += 1
        label = "citation" if count == 1 else "citations"
        new_span = f'\n    <span class="pub-citations">{count} {label}</span>\n  '
        return open_tag + inner_clean + new_span + close_tag

    new_html = PUB_ENTRY_RE.sub(replace, html)
    return new_html, successes, failures


# ─── marker replacement ───────────────────────────────────────────────────

def replace_between(text: str, marker: str, payload: str) -> str:
    pat = re.compile(
        rf'(<!--\s*{re.escape(marker)}:start\s*-->)(.*?)(<!--\s*{re.escape(marker)}:end\s*-->)',
        re.DOTALL,
    )
    if not pat.search(text):
        print(f"  WARN: marker {marker}:start/end not found; skipping", file=sys.stderr)
        return text
    return pat.sub(lambda m: f"{m.group(1)}\n{payload}\n    {m.group(3)}", text)


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
