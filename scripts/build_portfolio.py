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
# Activity sparkline window: 24 weeks ending at the most recent Sunday.
# Tufte-inspired inline sparkline that replaces the prior 52-week heatmap
# grid. The pre-2025 journalism pieces live in the blog but aren't part
# of this cadence story; PRE_BLOG_CUTOFF excludes them from the cadence
# total when computing the trailing post count.
SPARKLINE_WEEKS = 24
SPARKLINE_X0 = 10        # left x-coordinate of the first dot in the SVG
SPARKLINE_DX = 11        # spacing between dots; matches the demo's geometry
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
    """Emit the 24-week inline cadence sparkline.

    Tufte's last-point-label pattern: a small numeric annotation at the
    end of the sparkline gives the trailing total so the chart is self-
    legending. The marginnote text is fixed copy describing the post-
    hiatus return; treating it as content keeps the script's only job
    the visual update.
    """
    anchor = last_sunday(date.today())
    cadence_posts = [p for p in posts if p[0] >= PRE_BLOG_CUTOFF]
    if not cadence_posts:
        return ""

    dots: list[str] = []
    cadence_total_in_window = 0
    for i in range(SPARKLINE_WEEKS - 1, -1, -1):
        week_end = anchor - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        n = sum(1 for p in posts if week_start <= p[0] <= week_end and p[0] >= PRE_BLOG_CUTOFF)
        cadence_total_in_window += n
        cx = SPARKLINE_X0 + (SPARKLINE_WEEKS - 1 - i) * SPARKLINE_DX
        # Filled = publication week, empty = silent week. The hardcoded
        # hex values are intentional: index.html's <style> block has CSS
        # attribute selectors that map them to var(--ink) and var(--rule)
        # so the same SVG renders correctly in both light and dark mode.
        fill = "#111" if n > 0 else "#d0d0c8"
        dots.append(f'        <circle cx="{cx}" cy="10" r="2" fill="{fill}"/>')

    label = "post" if cadence_total_in_window == 1 else "posts"
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
        '<span class="marginnote">Writing resumed in late 2025 after a multi-year pause. '
        'The early weeks of the window are sparse by design, not by neglect; recent weeks '
        'show a steady run.</span>\n'
        '    </p>'
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
