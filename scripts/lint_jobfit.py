#!/usr/bin/env python3
"""lint_jobfit.py — evidence-gap report for the private job search.

Checks each skill in src/content/skills.yaml against the site's PUBLIC
artifacts, and dates each proof so recency can be weighted:

  - project cards in index.html   (.project / .project-tile <h3>)   [undated]
  - blog posts under src/content/blog/*.md   (slug + publishDate)   [dated]
  - employers in resume.md ## Experience     (org + end year)       [dated]

Two kinds of generated work-search item:

  1. UNPROVEN - a skill whose evidence refs resolve to no public artifact.
     Write or ship something before leaning on the claim.
  2. STALE    - a skill that IS proven, but only by artifacts older than
     STALE_YEARS. This is the "weight recency" signal: the public proof has
     aged, so refresh it (a recent post, a current-role mention).

Informational only: ALWAYS exits 0. It is a personal work-queue, not a
repo-integrity gate, so it is deliberately kept out of scripts/hooks/pre-push
and out of CI. Its inputs are all committed, so it is safe to run anywhere; it
simply has no reason to gate a push.

Importable: build_jobsearch.py reuses scan_artifacts(), resolve_skills(),
proven_ids(), and recency_weight() so the matrix and packets share one notion
of "proven" and "recent".
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import frontmatter

from _common import coerce_date, install_git_hooks, iter_post_paths
from _skills import SKILLS_YAML, load_skills

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
RESUME = ROOT / "src" / "content" / "resume.md"
POSTS_DIR = ROOT / "src" / "content" / "blog"

# Recency tiers: (years-since-most-recent-public-proof boundary, weight).
# Evaluated in order; older than the last boundary gets RECENCY_FLOOR. Tunable.
RECENCY_TIERS = ((2, 1.0), (5, 0.75), (10, 0.5))
RECENCY_FLOOR = 0.25
RECENCY_UNDATED = 0.5      # proven, but only by an undated artifact (a project)
STALE_YEARS = 5            # proven-but-stale threshold for a soft work-item

PROJECT_RE = re.compile(
    r'<div class="project(?:-tile)?">.*?<h3[^>]*>(?P<title>.*?)</h3>',
    re.DOTALL,
)
# A resume Experience role header: **Org** | Title  /  date line beneath it.
ROLE_RE = re.compile(
    r'^\*\*(?P<org>[^*]+)\*\*\s*\|[^\n]*\n(?P<dates>[^\n]*\d{4}[^\n]*)$',
    re.MULTILINE,
)
_TAG_RE = re.compile(r"<[^>]+>")
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")


def _strip_tags(s: str) -> str:
    return _TAG_RE.sub("", s).strip()


def _role_end_date(dates_line: str, today: date) -> date | None:
    if "present" in dates_line.lower():
        return today
    years = [int(m.group()) for m in _YEAR_RE.finditer(dates_line)]
    return date(max(years), 12, 31) if years else None


# ─── public-artifact scan ──────────────────────────────────────────────────

def scan_artifacts(today: date | None = None) -> dict:
    """Build the public-proof pools: project titles, {post slug: date},
    {role org: end date}. Reads only committed files."""
    today = today or date.today()
    projects: list[str] = []
    if INDEX.exists():
        text = INDEX.read_text(encoding="utf-8")
        projects = [_strip_tags(m.group("title")) for m in PROJECT_RE.finditer(text)]

    roles: dict[str, date | None] = {}
    if RESUME.exists():
        rtext = RESUME.read_text(encoding="utf-8")
        for m in ROLE_RE.finditer(rtext):
            roles[m.group("org").strip()] = _role_end_date(m.group("dates"), today)

    posts: dict[str, date | None] = {}
    if POSTS_DIR.is_dir():
        for p in iter_post_paths(POSTS_DIR):
            try:
                fm = frontmatter.load(p)
            except Exception:
                continue
            if fm.metadata.get("draft"):
                continue
            posts[p.stem] = coerce_date(fm.metadata.get("publishDate"))
    return {"projects": projects, "roles": roles, "posts": posts}


def _resolve_ref(kind: str, ref: str, artifacts: dict) -> tuple[bool, date | None]:
    """Resolve one evidence ref to (resolved?, date-of-proof-or-None)."""
    ref = (ref or "").strip()
    if not ref:
        return False, None
    if kind == "post":
        if ref in artifacts["posts"]:
            return True, artifacts["posts"][ref]
        return False, None
    if kind == "project":
        low = ref.lower()
        for title in artifacts["projects"]:
            if low in title.lower() or title.lower() in low:
                return True, None      # project cards carry no machine date
        return False, None
    if kind == "role":
        low = ref.lower()
        for org, when in artifacts["roles"].items():
            if low in org.lower():
                return True, when
        return False, None
    return False, None


def resolve_skills(skills: list[dict], artifacts: dict) -> dict[str, dict]:
    """Per skill id -> {proven, last, has_undated, resolved, unresolved}."""
    out: dict[str, dict] = {}
    for s in skills:
        resolved: list[tuple] = []
        unresolved: list[tuple] = []
        for ev in s.get("evidence") or []:
            if not isinstance(ev, dict):
                continue
            ok, when = _resolve_ref(ev.get("kind", ""), ev.get("ref", ""), artifacts)
            (resolved if ok else unresolved).append(
                (ev.get("kind", ""), ev.get("ref", ""), when)
            )
        dated = [w for _, _, w in resolved if w is not None]
        out[s["id"]] = {
            "proven": bool(resolved),
            "last": max(dated) if dated else None,
            "has_undated": any(w is None for *_, w in resolved),
            "resolved": resolved,
            "unresolved": unresolved,
        }
    return out


def proven_ids(info: dict[str, dict]) -> set[str]:
    return {sid for sid, i in info.items() if i["proven"]}


def years_since(d: date, today: date) -> float:
    return (today - d).days / 365.25


def recency_weight(skill_info: dict, today: date | None = None) -> float:
    """Recency factor in [0, 1] for one skill's strongest, freshest proof."""
    if not skill_info["proven"]:
        return 0.0
    last = skill_info["last"]
    if last is None:
        return RECENCY_UNDATED
    today = today or date.today()
    yrs = years_since(last, today)
    for boundary, weight in RECENCY_TIERS:
        if yrs <= boundary:
            return weight
    return RECENCY_FLOOR


def is_stale(skill_info: dict, today: date) -> bool:
    last = skill_info["last"]
    if not skill_info["proven"] or last is None:
        return False
    return years_since(last, today) > STALE_YEARS


# ─── report ────────────────────────────────────────────────────────────────

def run() -> int:
    if not SKILLS_YAML.exists():
        print(f"jobfit lint: {SKILLS_YAML} absent; nothing to check")
        return 0
    data = load_skills()
    skills = data["skills"]
    today = date.today()
    artifacts = scan_artifacts(today)
    info = resolve_skills(skills, artifacts)

    by_id = {s["id"]: s for s in skills}
    unproven = [s for s in skills if not info[s["id"]]["proven"]]
    undated = [s for s in skills
               if info[s["id"]]["proven"] and info[s["id"]]["last"] is None]
    stale = [s for s in skills if is_stale(info[s["id"]], today)]
    proven_dated = len(skills) - len(unproven) - len(undated)

    print(f"jobfit lint: {len(skills)} skills; {proven_dated} proven (dated), "
          f"{len(undated)} proven (undated), {len(unproven)} unproven, "
          f"{len(stale)} stale (>{STALE_YEARS}y).")

    if unproven:
        print("\n  Work-search items (UNPROVEN: no public artifact yet):")
        for s in unproven:
            bad = info[s["id"]]["unresolved"]
            why = ("evidence refs do not resolve: "
                   + ", ".join(f"{k}:{r}" for k, r, _ in bad)) if bad \
                  else "no evidence listed"
            print(f"    - {s['name']}  ({why})")

    if stale:
        print(f"\n  Work-search items (STALE: proven, last shown >{STALE_YEARS}y ago):")
        for s in sorted(stale, key=lambda s: info[s["id"]]["last"]):
            last = info[s["id"]]["last"]
            print(f"    - {s['name']}  (last public proof {last.year}, "
                  f"weight {recency_weight(info[s['id']], today):.2f})")

    if undated:
        print("\n  Note (proven, but only by an undated project card):")
        for s in undated:
            print(f"    - {s['name']}")

    if not (unproven or stale):
        print("  No gaps: every skill has fresh public proof.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
