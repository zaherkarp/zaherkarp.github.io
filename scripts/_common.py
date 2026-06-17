"""Shared helpers for scripts in this directory.

Exposes install_git_hooks(), called at the top of each project script so a
fresh clone wires up the pre-push hook automatically without a manual setup
step, and slugify_tag(), the single source of truth for turning a blog tag
into the URL slug used by the per-tag archive pages (blog/tags/<slug>/).
Both build_blog.py (which emits the pages) and build_portfolio.py (which
links to them from the homepage cadence rollup) import slugify_tag so the
two surfaces can never disagree on a slug.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR_REL = "scripts/hooks"

# Any run of non-alphanumeric characters collapses to a single hyphen, so
# "Medicare Stars" / "medicare-stars" / "Medicare  Stars" all slug to
# "medicare-stars" and "CI/CD" slugs to "ci-cd". Tags that differ only in
# case or separator therefore share one tag page, which is the intended
# merge; genuinely different tags ("medicare" vs "medicare-stars") stay
# separate.
_TAG_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify_tag(tag: str) -> str:
    """Normalize a blog tag to its URL slug (lowercase, hyphen-separated)."""
    return _TAG_SLUG_RE.sub("-", str(tag).strip().lower()).strip("-")


def install_git_hooks() -> None:
    """Point git's core.hooksPath at scripts/hooks/ if not already set.

    Idempotent. Silently no-ops outside a git work tree (tarball, CI
    sparse checkout, missing git binary). Prints a one-line notice on
    first install so the user knows hooks are now active.
    """
    hooks_dir = REPO_ROOT / HOOKS_DIR_REL
    if not hooks_dir.is_dir():
        return
    try:
        current = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if current.stdout.strip() == HOOKS_DIR_REL:
            return
        result = subprocess.run(
            ["git", "config", "core.hooksPath", HOOKS_DIR_REL],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return
    if result.returncode == 0:
        print(
            f"hooks: installed (core.hooksPath -> {HOOKS_DIR_REL}); "
            "pre-push checks now active",
            file=sys.stderr,
        )
