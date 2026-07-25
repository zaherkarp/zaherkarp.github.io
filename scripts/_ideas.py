#!/usr/bin/env python3
"""_ideas.py — shared loader/writer for the blog idea ledger.

src/content/blog-ideas.yaml is the LEDGER for the idea -> draft -> publish
pipeline: one row per item, created once at capture and carried through every
stage. An idea and a draft are the same row at different `status:` values,
not two records. The `.md` file under src/content/blog/ is the artifact that
appears at the `drafting` stage, joined to its row by `slug`.

This module is the single reader/writer, mirroring the role _publications.py
plays for publications.yaml. Four consumers share it, so the ledger can never
be interpreted two different ways:

    scripts/blog                `blog idea ...` / `blog promote` / `blog queue`
    scripts/lint_ideas.py       the pre-push + CI gate
    scripts/blog_backlog.py     the weekly digest issue body
    scripts/blog_ideas_intake.py  rows captured from the phone

backlog_snapshot() in particular is deliberately shared: the terminal view and
the digest issue render the SAME snapshot, so the two surfaces cannot disagree
about what is stale.
"""

from __future__ import annotations

import re
import subprocess
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
IDEAS_PATH = ROOT / "src" / "content" / "blog-ideas.yaml"
POSTS_DIR = ROOT / "src" / "content" / "blog"

# The four stages. Order matters: it is the funnel order used to sort the
# `blog queue` table and the digest sections.
STATUSES = ("idea", "drafting", "published", "dropped")

# Stages where a `slug` (and therefore a .md file) must exist.
SLUGGED_STATUSES = ("drafting", "published")

# Canonical key order for a written entry. Anything not listed is dropped on
# write, which is what makes lint_ideas' unknown-key check safe to enforce.
FIELD_ORDER = ("id", "title", "note", "tags", "added", "status", "slug", "source")

# Staleness thresholds, in days since the file was last touched. Shared by the
# CLI buckets and the digest so both tell the same story.
FRESH_DAYS = 14
AGING_DAYS = 45

# Notification thresholds for the digest workflow: a comment is posted only
# when an item NEWLY crosses one of these.
DRAFT_NUDGE_DAYS = 30
IDEA_NUDGE_DAYS = 90

ID_RE = re.compile(r"^[a-z0-9-]+$")
_SLUGIFY_RE = re.compile(r"[^a-z0-9]+")


# ── load / save ────────────────────────────────────────────────────────────


def load_ideas(path: Path | None = None) -> list[dict]:
    """Parse the ledger. Returns [] when the file is absent or empty.

    Raises yaml.YAMLError on a malformed file and ValueError when the
    top-level document is not a list -- both are lint_ideas' problem to
    report, not this module's to paper over.
    """
    path = path or IDEAS_PATH
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return []
    if not isinstance(data, list):
        raise ValueError(
            f"{path.name}: top-level document must be a list of entries, "
            f"got {type(data).__name__}"
        )
    return data


def _header(path: Path) -> str:
    """Return the leading comment block, verbatim, up to the first entry.

    Everything above the first `- ` line is authored documentation (the field
    contract); everything below is data we re-dump. Splitting there is what
    lets save_ideas() round-trip without a comment-preserving YAML library.
    """
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    header: list[str] = []
    for line in lines:
        if line.startswith("- "):
            break
        header.append(line)
    # Trim trailing blank lines, then re-add exactly one separator.
    while header and not header[-1].strip():
        header.pop()
    return "\n".join(header) + "\n\n" if header else ""


def _ordered(entry: dict) -> dict:
    """Project an entry onto FIELD_ORDER, dropping empty optional fields.

    Empty `slug`/`note`/`tags`/`source` are omitted rather than written as
    `""` / `[]`, so an `idea` row stays visually minimal and lint_ideas'
    "idea must not carry a slug" check has nothing ambiguous to read.
    """
    out: dict = {}
    for key in FIELD_ORDER:
        if key not in entry:
            continue
        value = entry[key]
        if key in ("note", "tags", "slug", "source") and not value:
            continue
        out[key] = value
    return out


def save_ideas(ideas: list[dict], path: Path | None = None) -> None:
    """Rewrite the ledger: preserved header comment + re-dumped list.

    Unlike _publications.save_citation_counts (targeted line edits, because
    publications.yaml carries per-entry inline comments worth keeping), this
    file is machine-written far more often than hand-edited and carries no
    per-entry comments by design. A whole-list re-dump under a preserved
    header is simpler and has no partial-write failure mode.
    """
    path = path or IDEAS_PATH
    body = ""
    if ideas:
        blocks = [
            yaml.safe_dump(
                [_ordered(entry)],
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                width=10_000,  # never wrap; a wrapped note is painful to diff
            )
            for entry in ideas
        ]
        body = "\n".join(blocks)
    path.write_text(_header(path) + body, encoding="utf-8")


# ── lookup / creation ──────────────────────────────────────────────────────


def slugify(text: str) -> str:
    """Mirror of the `blog` CLI's slugify, so an id and its eventual post
    slug are derived by identical rules."""
    s = _SLUGIFY_RE.sub("-", text.lower()).strip("-")
    return s or "untitled"


ID_MAX_LEN = 48


def _truncate_slug(s: str, limit: int = ID_MAX_LEN) -> str:
    """Trim a slug to `limit` chars on a word boundary.

    Ids are typed by hand (`blog promote <id>`), so a 60-character slugified
    sentence is a usability problem. Truncating on a hyphen keeps the result
    readable; `find_idea` accepts fragments anyway.
    """
    if len(s) <= limit:
        return s
    cut = s[:limit]
    if "-" in cut:
        cut = cut.rsplit("-", 1)[0]
    return cut.strip("-") or s[:limit]


def new_id(title: str, existing: list[dict]) -> str:
    """Slugify a title into an unused id, suffixing -2, -3, ... on collision."""
    taken = {str(e.get("id", "")) for e in existing}
    base = _truncate_slug(slugify(title))
    if base not in taken:
        return base
    n = 2
    while f"{base}-{n}" in taken:
        n += 1
    return f"{base}-{n}"


def find_idea(ideas: list[dict], key: str) -> dict | None:
    """Resolve an exact id, then a unique substring match. None on miss or
    on an ambiguous fragment (the caller decides how loudly to complain)."""
    for entry in ideas:
        if str(entry.get("id", "")) == key:
            return entry
    matches = [e for e in ideas if key in str(e.get("id", ""))]
    return matches[0] if len(matches) == 1 else None


def idea_for_slug(ideas: list[dict], slug: str) -> dict | None:
    """Reverse lookup: the ledger row that owns a post slug."""
    for entry in ideas:
        if entry.get("slug") and str(entry["slug"]) == slug:
            return entry
    return None


# ── dates ──────────────────────────────────────────────────────────────────


def _git_date(args: list[str], path: Path) -> date | None:
    try:
        r = subprocess.run(
            ["git", "log", *args, "--format=%cs", "--", str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if not lines:
        return None
    try:
        return date.fromisoformat(lines[0].strip())
    except ValueError:
        return None


def last_touched(path: Path) -> date | None:
    """Date of the last commit touching `path`, falling back to mtime.

    This, not `publishDate`, is what staleness is measured from. publishDate
    is the INTENDED publication date: a draft dated in the future looks
    permanently fresh, which is exactly how drafts go unnoticed. mtime is the
    fallback for an uncommitted new file (and is checkout time in a fresh
    clone, which is why git is asked first).
    """
    d = _git_date(["-1"], path)
    if d:
        return d
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).date()
    except OSError:
        return None


def first_commit_date(path: Path) -> date | None:
    """Date the file was first added. Used to backfill `added` on adopt."""
    return _git_date(["--diff-filter=A"], path)


def coerce_date(value) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def days_since(d, today: date | None = None) -> int | None:
    d = coerce_date(d)
    if d is None:
        return None
    return ((today or date.today()) - d).days


def bucket(days: int | None) -> str:
    """Staleness bucket for a draft. Shared by the CLI and the digest."""
    if days is None:
        return "unknown"
    if days < FRESH_DAYS:
        return "fresh"
    if days < AGING_DAYS:
        return "aging"
    return "stale"


# ── the shared snapshot ────────────────────────────────────────────────────


def post_path(slug: str) -> Path:
    return POSTS_DIR / f"{slug}.md"


def _post_is_draft(path: Path) -> bool | None:
    """Read just the `draft:` flag without importing frontmatter.

    Deliberately dependency-free: lint_ideas and the intake script run in CI
    jobs that should not need the full markdown toolchain to answer a
    yes/no question about one frontmatter line.
    """
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"^draft:\s*(true|false)\s*$", text, re.MULTILINE)
    if not m:
        return False
    return m.group(1) == "true"


def unregistered_drafts(ideas: list[dict]) -> list[str]:
    """Draft posts on disk with no ledger row.

    Scoped to `draft: true` on purpose. The 60+ already-published historical
    posts predate the ledger and must NOT be retro-registered, so they are
    not orphans; only items the funnel would actually act on are.
    """
    known = {str(e["slug"]) for e in ideas if e.get("slug")}
    out = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        if path.stem.startswith("_") or path.stem in known:
            continue
        if _post_is_draft(path):
            out.append(path.stem)
    return out


def backlog_snapshot(ideas: list[dict] | None = None, today: date | None = None) -> dict:
    """One funnel view, rendered by both `blog queue` and the digest.

    Every row carries `stage`, `days` (time in the current stage's terms) and,
    for drafts, a staleness `bucket`. Rows are the LEDGER rows enriched with
    on-disk facts, never a separate list -- which is what keeps the single-
    pipeline model true in the tooling and not just in the YAML.
    """
    ideas = load_ideas() if ideas is None else ideas
    today = today or date.today()
    rows = []
    for entry in ideas:
        status = str(entry.get("status", "")) or "idea"
        slug = str(entry.get("slug") or "")
        path = post_path(slug) if slug else None
        if status == "drafting" and path is not None:
            days = days_since(last_touched(path), today)
            measure = "untouched"
        else:
            days = days_since(entry.get("added"), today)
            measure = "in backlog" if status == "idea" else "since capture"
        rows.append(
            {
                "id": str(entry.get("id", "")),
                "title": str(entry.get("title", "")),
                "note": str(entry.get("note") or ""),
                "stage": status,
                "slug": slug,
                "added": coerce_date(entry.get("added")),
                "days": days,
                "measure": measure,
                "bucket": bucket(days) if status == "drafting" else "",
                "source": str(entry.get("source") or ""),
                "exists": bool(path and path.exists()),
            }
        )

    # Longest-stuck first within each stage: the point of the view is to put
    # whatever has been sitting the longest at the top.
    rows.sort(key=lambda r: (STATUSES.index(r["stage"]) if r["stage"] in STATUSES else 9,
                             -(r["days"] if r["days"] is not None else -1)))

    by_stage = {s: [r for r in rows if r["stage"] == s] for s in STATUSES}
    return {
        "rows": rows,
        "by_stage": by_stage,
        "orphans": unregistered_drafts(ideas),
        "counts": {s: len(by_stage[s]) for s in STATUSES},
        "today": today,
    }


def nudge_items(snapshot: dict) -> list[dict]:
    """Rows that have crossed a notification threshold.

    The digest workflow diffs this against the previous run's set and comments
    only on what is NEW, so a weekly message means something changed rather
    than that a week passed.
    """
    out = []
    for row in snapshot["by_stage"]["drafting"]:
        if row["days"] is not None and row["days"] >= DRAFT_NUDGE_DAYS:
            out.append(row)
    for row in snapshot["by_stage"]["idea"]:
        if row["days"] is not None and row["days"] >= IDEA_NUDGE_DAYS:
            out.append(row)
    return out
