#!/usr/bin/env python3
"""lint_ideas.py

Keeps the blog idea ledger (src/content/blog-ideas.yaml) and the posts
directory (src/content/blog/*.md) from drifting apart.

The ledger and the posts directory are two halves of ONE pipeline: a row is
created at capture with `status: idea`, gains a `slug` and a .md file when it
is promoted to `drafting`, and flips to `published` when the post goes live.
Nothing keeps those halves aligned except this linter. Without it a row could
claim `drafting` with no file behind it, a published post could still be
listed as in-progress, or a draft could exist that the funnel cannot see.

GATE (hard fail, blocks push) -- checks 1-7, all schema and referential
integrity in the ledger -> post direction.

REPORT (informational, never fails) -- check 8, the post -> ledger direction:
draft posts with no ledger row. Non-failing and scoped to `draft: true`
deliberately: the 60+ already-published historical posts predate the ledger
and must not be retro-registered, so they are not orphans. Same
hard-gate-one-way / report-the-other-way split as lint_recognition.py.

Skips cleanly when the ledger is absent.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

from _common import install_git_hooks
from _ideas import (
    FIELD_ORDER,
    ID_RE,
    IDEAS_PATH,
    SLUGGED_STATUSES,
    STATUSES,
    _post_is_draft,
    coerce_date,
    load_ideas,
    post_path,
    unregistered_drafts,
)

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = ("id", "title", "added", "status")

# Fields whose VALUES reach the homepage (a promoted idea's title becomes the
# post title, which build_portfolio pulls into the writing section). Comments
# in the file header are not checked: they are documentation, never rendered.
EM_DASH_FIELDS = ("title", "note")


def _display(path: Path) -> str:
    """Repo-relative path when possible, absolute otherwise (tests point this
    at a tmp dir, and a crash in the error formatter would mask the errors)."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def run(path: Path | None = None) -> int:
    """Lint the ledger at `path` (defaults to the repo's blog-ideas.yaml).

    The parameter exists so tests can point at a fixture without patching
    module globals in two places.
    """
    path = path or IDEAS_PATH
    if not path.exists():
        print("ideas lint: skipped (blog-ideas.yaml absent)")
        return 0

    failures: list[str] = []

    try:
        ideas = load_ideas(path)
    except (yaml.YAMLError, ValueError) as e:
        print(f"Ideas lint: {path.name} could not be parsed.\n\n  {e}",
              file=sys.stderr)
        return 1

    seen_ids: dict[str, int] = {}
    seen_slugs: dict[str, str] = {}
    today = date.today()

    for i, entry in enumerate(ideas):
        where = f"entry {i + 1}"
        if not isinstance(entry, dict):
            failures.append(f"{where}: expected a mapping, got {type(entry).__name__}")
            continue

        eid = str(entry.get("id", "")).strip()
        label = f"{where} ({eid})" if eid else where

        # 1. required fields
        for field in REQUIRED:
            if not str(entry.get(field, "")).strip():
                failures.append(f"{label}: missing required field `{field}`")

        # 1b. unknown keys -- catches `tag:` for `tags:`, `status :` typos, etc.
        for key in entry:
            if key not in FIELD_ORDER:
                failures.append(
                    f"{label}: unknown field `{key}` "
                    f"(known: {', '.join(FIELD_ORDER)})"
                )

        # 2. id shape + uniqueness
        if eid:
            if not ID_RE.match(eid):
                failures.append(
                    f"{label}: id must be slug-form [a-z0-9-]+, got {eid!r}"
                )
            if eid in seen_ids:
                failures.append(
                    f"{label}: duplicate id, already used by entry {seen_ids[eid]}"
                )
            else:
                seen_ids[eid] = i + 1

        # 2b. added parses and is not in the future
        added = coerce_date(entry.get("added"))
        if entry.get("added") is not None and added is None:
            failures.append(
                f"{label}: `added` is not a YYYY-MM-DD date "
                f"({entry.get('added')!r})"
            )
        elif added and added > today:
            failures.append(
                f"{label}: `added` is in the future ({added}); it is the "
                f"capture date, not a target date"
            )

        # 7. em-dash policy on rendered fields. Checked BEFORE the status
        # bail-out below so a bad status does not mask a content problem.
        for field in EM_DASH_FIELDS:
            value = entry.get(field)
            if isinstance(value, str) and "—" in value:
                failures.append(
                    f"{label}: em-dash in `{field}`. This value reaches the "
                    f"homepage via the promoted post's frontmatter; use a "
                    f"comma or a period (CLAUDE.md em-dash policy)."
                )

        # 3. status is one of the four stages
        status = str(entry.get("status", "")).strip()
        if status and status not in STATUSES:
            failures.append(
                f"{label}: status {status!r} is not one of {', '.join(STATUSES)}"
            )
            continue

        slug = str(entry.get("slug") or "").strip()

        # 4/5. slugged stages must point at a real post in the right state
        if status in SLUGGED_STATUSES:
            if not slug:
                failures.append(
                    f"{label}: status `{status}` requires a `slug` naming its "
                    f"post (set by `blog promote`)"
                )
            else:
                if slug in seen_slugs:
                    failures.append(
                        f"{label}: slug {slug!r} already claimed by "
                        f"{seen_slugs[slug]!r}; one post, one ledger row"
                    )
                else:
                    seen_slugs[slug] = eid or where

                post = post_path(slug)
                if not post.exists():
                    failures.append(
                        f"{label}: status `{status}` but "
                        f"src/content/blog/{slug}.md does not exist"
                    )
                else:
                    is_draft = _post_is_draft(post)
                    if status == "drafting" and is_draft is False:
                        failures.append(
                            f"{label}: status `drafting` but {slug}.md is "
                            f"`draft: false` (published). Set status to "
                            f"`published`."
                        )
                    if status == "published" and is_draft is True:
                        failures.append(
                            f"{label}: status `published` but {slug}.md is "
                            f"still `draft: true`. Set status back to "
                            f"`drafting`, or publish the post."
                        )

        # 6. non-slugged stages must not carry one
        elif slug:
            failures.append(
                f"{label}: status `{status}` must not carry a `slug` "
                f"(got {slug!r}); a slug is only spent at the drafting stage"
            )

    if failures:
        print(
            f"Ideas lint found {len(failures)} problem(s) in "
            f"{_display(path)}:\n",
            file=sys.stderr,
        )
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print(
            "\nThe ledger and src/content/blog/ are two halves of one "
            "pipeline. Move items between stages with the CLI "
            "(`blog promote`, `blog publish`, `blog idea drop`) rather than "
            "by hand. See CLAUDE.md §Blog idea backlog.",
            file=sys.stderr,
        )
        return 1

    # 8. informational: the post -> ledger direction.
    orphans = unregistered_drafts(ideas)
    counts = {s: sum(1 for e in ideas if str(e.get("status", "")) == s) for s in STATUSES}
    print(
        "ideas lint: ledger consistent "
        f"({counts['idea']} idea, {counts['drafting']} drafting, "
        f"{counts['published']} published, {counts['dropped']} dropped)"
    )
    if orphans:
        print(
            f"\n  note: {len(orphans)} draft post(s) have no ledger row, so "
            f"they are invisible to `blog queue` and the weekly digest:"
        )
        for slug in orphans:
            print(f"    - {slug}")
        print("  register with: blog idea adopt <slug>")
    return 0


if __name__ == "__main__":
    sys.exit(run())
