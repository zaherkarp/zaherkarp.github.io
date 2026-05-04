"""Shared helpers for scripts in this directory.

Currently exposes install_git_hooks(), called at the top of each project
script so a fresh clone wires up the pre-push hook automatically without
a manual setup step.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR_REL = "scripts/hooks"


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
