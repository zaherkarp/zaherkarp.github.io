#!/usr/bin/env python3
"""blog_backlog.py — render the idea/draft funnel as markdown.

Feeds .github/workflows/blog-backlog-digest.yml, which keeps ONE rolling
tracking issue whose body is this output. Renders from _ideas.backlog_snapshot,
the same function `blog queue` renders, so the issue on your phone and the
table in your terminal can never disagree about what is stale.

Two outputs, selected by flag:

  --markdown   the issue body (default)
  --state      a compact JSON set of items currently past a nudge threshold

The workflow stashes --state inside an HTML comment in the issue body and
diffs it on the next run, so it can comment only when something has NEWLY
gone stale. A weekly comment regardless of change trains you to ignore it.

Usage:
    python scripts/blog_backlog.py [--markdown|--state]
"""

from __future__ import annotations

import json
import sys
from datetime import date

from _ideas import (
    AGING_DAYS,
    DRAFT_NUDGE_DAYS,
    FRESH_DAYS,
    IDEA_NUDGE_DAYS,
    backlog_snapshot,
    nudge_items,
)

STATE_MARKER = "blog-backlog-state:"

BUCKET_ICON = {"fresh": "🟢", "aging": "🟡", "stale": "🔴", "unknown": "⚪"}


def _row_line(row: dict) -> str:
    """One markdown list item for a funnel row."""
    days = row["days"]
    age = f"{days}d" if days is not None else "age unknown"
    bits = [f"**{row['title']}**"]
    if row["stage"] == "drafting":
        icon = BUCKET_ICON.get(row["bucket"], "")
        bits.append(f"{icon} {age} untouched")
        bits.append(f"`{row['slug']}`")
    else:
        bits.append(f"{age} in backlog")
        bits.append(f"`{row['id']}`")
    line = " — ".join(bits)
    if row["note"]:
        line += f"\n  {row['note']}"
    return f"- {line}"


def render_markdown(snapshot: dict | None = None) -> str:
    snap = snapshot or backlog_snapshot()
    counts = snap["counts"]
    today: date = snap["today"]
    out: list[str] = []

    out.append(
        "One ledger, one row per item, carried from capture to publication. "
        "This issue is regenerated every Monday; it is the phone-side view of "
        "`blog queue`."
    )
    out.append("")
    out.append(
        f"**{counts['idea']} idea** → **{counts['drafting']} drafting** → "
        f"**{counts['published']} published**"
        + (f" _({counts['dropped']} dropped)_" if counts["dropped"] else "")
    )
    out.append("")

    drafting = snap["by_stage"]["drafting"]
    out.append("## In progress")
    out.append("")
    if not drafting:
        out.append("_Nothing being drafted._")
    else:
        for bucket_name in ("stale", "aging", "fresh", "unknown"):
            rows = [r for r in drafting if r["bucket"] == bucket_name]
            if not rows:
                continue
            label = {
                "stale": f"Stale ({AGING_DAYS}d+ untouched)",
                "aging": f"Aging ({FRESH_DAYS}-{AGING_DAYS}d)",
                "fresh": f"Fresh (under {FRESH_DAYS}d)",
                "unknown": "Age unknown",
            }[bucket_name]
            out.append(f"### {BUCKET_ICON[bucket_name]} {label}")
            out.append("")
            out.extend(_row_line(r) for r in rows)
            out.append("")
    out.append("")

    ideas = snap["by_stage"]["idea"]
    out.append("## Backlog")
    out.append("")
    if not ideas:
        out.append(
            "_Empty._ Capture one from this phone: open a new issue with the "
            "**Blog idea** template, or run `blog idea add \"Title\"` at a terminal."
        )
    else:
        out.extend(_row_line(r) for r in ideas)
    out.append("")

    if snap["orphans"]:
        out.append("## Not in the ledger")
        out.append("")
        out.append(
            "These draft posts exist on disk but have no ledger row, so they "
            "are invisible to the funnel. Register with `blog idea adopt`:"
        )
        out.append("")
        out.extend(f"- `{slug}`" for slug in snap["orphans"])
        out.append("")

    out.append("---")
    out.append("")
    out.append(
        f"_Thresholds: a draft is flagged at {DRAFT_NUDGE_DAYS}d untouched, an "
        f"idea at {IDEA_NUDGE_DAYS}d idle. Generated {today.isoformat()} by "
        f"`scripts/blog_backlog.py`._"
    )
    return "\n".join(out)


def render_state(snapshot: dict | None = None) -> str:
    """Compact JSON of what is currently past a nudge threshold."""
    snap = snapshot or backlog_snapshot()
    return json.dumps(
        {"flagged": sorted(r["id"] for r in nudge_items(snap))},
        separators=(",", ":"),
    )


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--markdown"
    snap = backlog_snapshot()
    if mode == "--state":
        print(render_state(snap))
    elif mode == "--markdown":
        print(render_markdown(snap))
    else:
        print(f"unknown mode {mode!r}; use --markdown or --state", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
