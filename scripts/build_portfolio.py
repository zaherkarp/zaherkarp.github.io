#!/usr/bin/env python3
"""
build_portfolio.py

Injects four pieces of build-time content into index.html, between marker
comments:

  <!-- activity-grid:start --> ... <!-- activity-grid:end -->
    24-week dot sparkline showing recent posting cadence. Sourced from the
    blog frontmatter (publishDate, draft). No external requests.

  <!-- writing-list:start --> ... <!-- writing-list:end -->
    The two most recent non-draft posts, rendered as the homepage Writing
    section's featured entries (full summary). Sourced from the blog
    frontmatter; the optional `homepageMarginnote` field renders an inline
    margin note next to the entry title.

  <!-- writing-index:start --> ... <!-- writing-index:end -->
    The next six posts after the featured pair, rendered as compact
    .writing-tile small multiples in the sibling .writing-index grid.
    Same frontmatter source; margin notes are featured-only, so tiles
    omit homepageMarginnote.

  <!-- pub-list:start --> ... <!-- pub-list:end -->
    The Publications block, generated from src/content/publications.yaml
    (the single source of truth shared with the CV build). Semantic Scholar
    citation counts are refreshed per entry `sid` and written back into the
    YAML cache; on fetch failure the cached value is preserved (so a flaky
    network or rate-limit doesn't wipe prior values).

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

from _common import install_git_hooks, slugify_tag
from _publications import (
    load_publications,
    render_homepage_entries,
    save_citation_counts,
)

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
LIFE_WEEKS = ROOT / "life-in-weeks" / "index.html"
POSTS_DIR = ROOT / "src" / "content" / "blog"
# Acronyms that should render uppercase when a blog "thought" topic is derived
# from a tag slug (the lowercase tag "aws" -> "AWS"). A per-post
# `lifeweek_topic:` frontmatter field overrides the derived topic entirely.
TOPIC_ACRONYMS = {
    "aws", "sql", "ci", "cd", "etl", "elt", "roi", "hedis", "cms", "ma",
    "ecds", "mph", "ml", "ai", "llm", "api", "pdf", "csv", "id", "kpi",
    "hcc", "hipaa", "hitrust", "qbp", "cahps", "dbt", "ux",
}
# Dated citation snapshots: one file per build day that actually fetched fresh
# counts. The YAML cache only ever holds the latest count; these snapshots
# accrete the longitudinal series the cache discards. Append-only by date,
# idempotent within a day (a re-run overwrites the same file).
SNAPSHOTS_DIR = ROOT / "data" / "snapshots"
WRITING_FEATURED = 2     # most-recent posts shown as full featured entries
WRITING_TILES = 6        # next posts shown as compact .writing-tile multiples
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
    # Sort the glob so same-date posts tie-break on filename deterministically;
    # an unordered glob lets the auto-committed outputs reorder run-to-run.
    for p in sorted(POSTS_DIR.glob("*.md")):
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
            "lifeweek_topic": str(fm.metadata.get("lifeweek_topic", "")).strip(),
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
    separated by middle dots, each tag linking to its /blog/tags/<slug>/
    archive page (the slug rule is shared with build_blog.py via
    _common.slugify_tag, so the homepage link and the generated page can
    never disagree). Links inherit the muted marginnote color and the
    site's standard underline treatment; no accent, per accent discipline.
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

    pairs = " · ".join(
        f'<a href="/blog/tags/{slugify_tag(tag)}/">{_esc(tag)}</a> ({n})'
        for tag, n in qualifying
    )
    return pairs


def build_activity_grid(posts: list[dict]) -> str:
    """Emit the 24-week inline cadence sparkline as per-week stems.

    Each week with N posts renders as a vertical line of height N * UNIT
    pixels (capped at the SVG top so stems don't overflow the viewBox).
    Weeks with no posts render as empty space; the faint baseline rule
    provides visual continuity across the time axis. This carries
    actual cadence variance ("burst weeks vs. quiet weeks") that the
    earlier binary-dot encoding flattened away.

    Tufte's last-point-label pattern: a small numeric annotation at the
    end of the sparkline gives the trailing total so the chart is self-
    legending. The ⊕ margin note expands into a tag frequency rollup
    (multi-post tags within the cadence window).
    """
    anchor = last_sunday(date.today())
    cadence_posts = [p for p in posts if p["date"] >= PRE_BLOG_CUTOFF]
    if not cadence_posts:
        return ""

    # Stem geometry. Baseline at y=16, top of usable area at y=2; 14
    # SVG units of vertical room. UNIT=2 means 7 posts/week hits the
    # ceiling, which is a sensible cap given observed cadence.
    BASE_Y = 16
    TOP_Y = 2
    UNIT = 2

    stems: list[str] = []
    cadence_total_in_window = 0
    for i in range(SPARKLINE_WEEKS - 1, -1, -1):
        week_end = anchor - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        n = sum(1 for p in posts if week_start <= p["date"] <= week_end and p["date"] >= PRE_BLOG_CUTOFF)
        cadence_total_in_window += n
        if n == 0:
            continue
        cx = SPARKLINE_X0 + (SPARKLINE_WEEKS - 1 - i) * SPARKLINE_DX
        y_top = max(TOP_Y, BASE_Y - n * UNIT)
        # Hardcoded #111 is intentional; index.html's <style> block has
        # CSS attribute selectors that map it to var(--ink) so the same
        # markup renders correctly in light and dark mode.
        stems.append(
            f'        <line x1="{cx}" y1="{BASE_Y}" x2="{cx}" y2="{y_top}" '
            f'stroke="#111" stroke-width="1.2"/>'
        )

    stems_block = ("\n".join(stems) + "\n") if stems else ""
    label = "post" if cadence_total_in_window == 1 else "posts"
    tag_rollup = build_cadence_marginnote(cadence_posts)
    marginnote_html = (
        f'<span class="marginnote">{tag_rollup}</span>' if tag_rollup else ""
    )
    return (
        '<p style="color: var(--muted); font-size: 1.05rem; margin-bottom: 1.4rem;">\n'
        '      24 weeks\n'
        '      <svg class="cadence" viewBox="0 0 280 20" width="280" height="20" '
        'aria-label="writing cadence sparkline showing posts per week over the last 24 weeks">\n'
        '        <line x1="10" y1="16" x2="263" y2="16" stroke="#d0d0c8" stroke-width="0.5"/>\n'
        + stems_block +
        '      </svg>\n'
        f'      <span style="font-variant-numeric: oldstyle-nums; color: var(--ink); '
        f'margin-left: 0.3rem;">{cadence_total_in_window} {label}</span>'
        '<label for="mn-cadence" class="margin-toggle">&#8853;</label>'
        '<input type="checkbox" aria-label="Show tag frequency breakdown" id="mn-cadence" class="margin-toggle"/>'
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
    """Emit the homepage Writing section's two most recent featured entries.

    Sorted by publishDate desc. Drafts and `_`-prefixed sources are
    already filtered out in load_posts(). These are the prominent
    entries: the title is an h3 (heading parity with project tiles and a
    screen-reader nav anchor) and the summary is the frontmatter
    `description`, the same curated, standard-length blurb the tiles use,
    so featured and tile text stay visually uniform. The featured/tile
    distinction is carried by title size and layout, not blurb length.
    Optional `homepageMarginnote` frontmatter renders an inline ⊕ margin
    note next to the title; the toggle id is `mn-w-<slug>` so it stays
    unique across entries.
    """
    recent = sorted(posts, key=lambda p: p["date"], reverse=True)[:WRITING_FEATURED]
    blocks: list[str] = []
    for p in recent:
        date_str = p["date"].isoformat()
        title = _esc(_strip_em_dashes(p["title"]))
        summary = _esc(_strip_em_dashes(p["description"]))
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
            f'        <h3 class="title"><a href="/blog/{slug}/">{title}</a></h3>'
            f'{margin_html}\n'
            '      </div>\n'
            f'      <p class="summary">{summary}</p>\n'
            '    </div>'
        )
    return "\n\n".join(blocks)


def build_writing_index(posts: list[dict]) -> str:
    """Emit the .writing-index small-multiples grid: the WRITING_TILES posts
    immediately after the featured pair.

    Mirrors the projects-index tile pattern but keys each tile by date
    (the `.writing-tile` class deliberately has no `.num` span, so the
    project CSS counter is untouched). Margin notes are a featured-only
    affordance, so `homepageMarginnote` is intentionally ignored here to
    keep tiles compact.
    """
    by_date = sorted(posts, key=lambda p: p["date"], reverse=True)
    tiles = by_date[WRITING_FEATURED:WRITING_FEATURED + WRITING_TILES]
    blocks: list[str] = []
    for p in tiles:
        date_str = p["date"].isoformat()
        title = _esc(_strip_em_dashes(p["title"]))
        desc = _esc(_strip_em_dashes(p["description"]))
        slug = p["slug"]
        blocks.append(
            '    <div class="writing-tile">\n'
            f'      <span class="date">{date_str}</span>\n'
            f'      <h3 class="title"><a href="/blog/{slug}/">{title}</a></h3>\n'
            f'      <p class="tile-summary">{desc}</p>\n'
            '    </div>'
        )
    return "\n\n".join(blocks)


# ─── Semantic Scholar citation counts ─────────────────────────────────────

def _gha_warn(msg: str) -> None:
    """Emit a GitHub Actions warning annotation (a plain line when run
    locally). Used to surface citation-fetch failures in the weekly run
    summary instead of leaving them buried in stderr."""
    print(f"::warning::{msg}")


def fetch_citation_count(sid: str, retries: int = 3) -> tuple[int | None, str]:
    """Return (count, status). status is one of:
      "ok"           count fetched.
      "rate_limited" HTTP 429 after all retries (transient; next run retries).
      "unresolved"   the id did not resolve to a count -- a non-429 HTTP error
                     (e.g. 404) or a 200 with no citationCount. Likely a bad or
                     dropped PMID/DOI worth checking, NOT a rate limit.
      "error"        network / timeout / parse failure (transient).
    On any non-"ok" status the caller keeps the cached count (graceful
    degradation); the status only drives how loudly the failure is reported.
    """
    url = S2_URL.format(sid=sid)
    req = urllib.request.Request(url, headers={"User-Agent": "zaherkarp-site-build"})
    backoff = 2
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=S2_TIMEOUT) as resp:
                data = json.load(resp)
                count = data.get("citationCount")
                if isinstance(count, int):
                    return count, "ok"
                return None, "unresolved"
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 2
                continue
            print(f"  semantic-scholar fetch failed for {sid}: {e}", file=sys.stderr)
            return None, ("rate_limited" if e.code == 429 else "unresolved")
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            print(f"  semantic-scholar fetch failed for {sid}: {e}", file=sys.stderr)
            return None, "error"
    return None, "rate_limited"


def build_publications() -> tuple[str, int, int]:
    """Refresh citation counts and render the homepage Publications markup.

    Loads publications.yaml (the source of truth shared with the CV build),
    fetches a fresh Semantic Scholar count for each entry with a `sid`,
    writes the refreshed counts back into the YAML cache, and returns
    (homepage_entries_html, successes, failures) rendered from the refreshed
    list. Entries without a `sid`, or whose fetch fails, keep their cached
    count (graceful degradation). A 1s pause between live requests stays
    under the public-tier rate limit.
    """
    pubs = load_publications()
    successes = 0
    failures = 0
    fetched = 0
    unresolved: list[str] = []   # likely bad/dropped id -- worth fixing
    transient: list[str] = []    # 429 / network -- next run retries
    for pub in pubs:
        sid = pub.get("sid")
        if not sid:
            continue
        if fetched > 0:
            time.sleep(1.0)
        fetched += 1
        count, status = fetch_citation_count(sid)
        if status == "ok":
            pub["citations"] = count
            successes += 1
            continue
        failures += 1
        (unresolved if status == "unresolved" else transient).append(sid)

    save_citation_counts(pubs)
    if successes:
        write_citation_snapshot(pubs)

    # Surface failures distinguishably so a permanently-broken id cannot hide
    # behind the same silent "cached value preserved" as a transient rate
    # limit. Cached counts are still shown either way (graceful degradation);
    # this only makes the failure visible in the weekly Actions run.
    if unresolved:
        _gha_warn(
            f"citation: {len(unresolved)} id(s) did not resolve to a count "
            f"({', '.join(unresolved)}). NOT a rate limit -- check the "
            f"PMID/DOI in publications.yaml; the cached count is shown meanwhile."
        )
    if transient:
        _gha_warn(
            f"citation: {len(transient)} lookup(s) failed transiently "
            f"({', '.join(transient)}); cached counts preserved, the weekly "
            f"run will retry."
        )

    return (
        render_homepage_entries(pubs),
        successes,
        failures,
    )


def write_citation_snapshot(pubs: list[dict]) -> None:
    """Record today's observed citation counts to data/snapshots/<date>.json.

    Only called when at least one fresh fetch succeeded this run, so a fully
    rate-limited build never lays down a misleading all-cached snapshot. The
    file maps each sid to its current count (fresh where the fetch landed,
    cached otherwise) so the series stays gap-free. Same-day re-runs overwrite.
    """
    counts = {p["sid"]: p["citations"] for p in pubs if p.get("sid") and "citations" in p}
    if not counts:
        return
    # Record-on-change: skip if identical to the most recent snapshot. ISO-dated
    # filenames sort chronologically, so the last one is the latest observation.
    # Keeps the series to one file per actual movement instead of one per run.
    if SNAPSHOTS_DIR.exists():
        prior = sorted(SNAPSHOTS_DIR.glob("*.json"))
        if prior:
            try:
                last = json.loads(prior[-1].read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                last = {}
            if last.get("citations") == counts:
                print(f"  citation counts unchanged since {last.get('date')}; no snapshot")
                return
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    snap = {
        "date": date.today().isoformat(),
        "source": "Semantic Scholar graph/v1 citationCount",
        "citations": counts,
    }
    path = SNAPSHOTS_DIR / f"{snap['date']}.json"
    path.write_text(json.dumps(snap, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"  wrote citation snapshot {path.relative_to(ROOT)} ({len(counts)} entries)")


# ─── marker replacement ───────────────────────────────────────────────────

# ─── page closer (Updated YYYY-MM) ────────────────────────────────────────

def build_updated_footer() -> str:
    """Render the page closer date stamp.

    Month-precision (not day) because the page doesn't typically change
    day-to-day in ways a reader cares about; the activity grid already
    carries day-precision for posting cadence. The hairline rule and
    .page-footer styling live in index.html's <style> block.
    """
    today = date.today()
    return f"    Updated {today.year:04d}-{today.month:02d}."


# ─── life-in-weeks blog "thoughts" ────────────────────────────────────────

def prettify_topic(slug: str) -> str:
    """Turn a tag slug into display text: 'healthcare-data' -> 'healthcare data',
    'aws' -> 'AWS'. Known acronyms uppercase; everything else stays lowercase."""
    words = slug.replace("_", "-").replace("-", " ").split()
    return " ".join(w.upper() if w in TOPIC_ACRONYMS else w for w in words)


def resolve_topic(post: dict) -> str:
    """The blog 'thought' topic for a post: explicit lifeweek_topic frontmatter
    wins; otherwise the prettified first tag. Empty if the post has neither."""
    override = post.get("lifeweek_topic", "")
    if override:
        return _strip_em_dashes(override)
    tags = post.get("tags") or []
    return prettify_topic(tags[0]) if tags else ""


def build_life_thoughts(posts: list[dict]) -> str:
    """Render the generated EVENTS entries for the life-in-weeks grid: one
    `{ date, topic, kind: 'thought' }` per non-draft post that resolves a topic,
    oldest first. The grid's JS merges same-week thoughts into one dot."""
    lines = []
    for post in sorted(posts, key=lambda p: p["date"]):
        topic = resolve_topic(post)
        if not topic:
            continue
        # Single-quoted JS string literals; escape backslash and quote.
        safe = topic.replace("\\", "\\\\").replace("'", "\\'")
        lines.append(
            f"    {{ date: '{post['date'].isoformat()}', topic: '{safe}', kind: 'thought' }},"
        )
    return "\n".join(lines)


def replace_between_js(text: str, marker: str, payload: str) -> str:
    """Marker replace for `// marker:start` / `// marker:end` JS comments
    (the HTML-comment replace_between can't reach inside a <script> array)."""
    pat = re.compile(
        rf'(//\s*{re.escape(marker)}:start[^\n]*)(.*?)(\n[ \t]*//\s*{re.escape(marker)}:end)',
        re.DOTALL,
    )
    if not pat.search(text):
        print(f"  WARN: JS marker {marker}:start/end not found; skipping", file=sys.stderr)
        return text
    body = f"\n{payload}" if payload else ""
    return pat.sub(lambda m: f"{m.group(1)}{body}{m.group(3)}", text)


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
    print(f"writing list injected ({min(len(posts), WRITING_FEATURED)} featured entries)")

    index_html = build_writing_index(posts)
    text = replace_between(text, "writing-index", index_html)
    n_tiles = max(0, min(len(posts) - WRITING_FEATURED, WRITING_TILES))
    print(f"writing index injected ({n_tiles} tiles)")

    pub_html, ok, fail = build_publications()
    text = replace_between(text, "pub-list", pub_html)
    print(f"publications injected (citation counts: {ok} updated, {fail} skipped)")

    footer_html = build_updated_footer()
    text = replace_between(text, "updated", footer_html, end_indent="  ")
    print("page footer date injected")

    if text != original:
        INDEX.write_text(text)
        print("index.html updated")
    else:
        print("no changes")

    # Life-in-weeks: drop a "💭 Thought about X" onto the grid for every post.
    if LIFE_WEEKS.exists():
        lw_original = LIFE_WEEKS.read_text()
        thoughts = build_life_thoughts(posts)
        lw_text = replace_between_js(lw_original, "blog-thoughts", thoughts)
        if lw_text != lw_original:
            LIFE_WEEKS.write_text(lw_text)
            n = thoughts.count("\n") + 1 if thoughts else 0
            print(f"life-in-weeks thoughts injected ({n} posts)")
        else:
            print("life-in-weeks: no changes")
    else:
        print(f"  WARN: {LIFE_WEEKS} not found; skipping life-in-weeks", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
