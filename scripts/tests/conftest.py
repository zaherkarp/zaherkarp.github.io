"""Shared pytest fixtures and import wiring for the script test harness.

Two responsibilities, both handled at import time so they are in force
before any test module imports a script under test:

1. Put ``scripts/`` on ``sys.path``. The scripts have no package
   ``__init__.py`` and import each other by bare module name
   (``import lint_blog``, ``from _common import ...``), so the directory
   itself must be importable.

2. Neutralize ``_common.install_git_hooks``. Every gate lint runs
   ``from _common import install_git_hooks`` followed by
   ``install_git_hooks()`` at IMPORT time, and that call points git's
   ``core.hooksPath`` at ``scripts/hooks`` when it is unset -- a real
   mutation of the repo's git config. We replace it with a no-op on the
   ``_common`` module BEFORE any lint/build module is imported, so the
   ``from _common import install_git_hooks`` binding those modules grab is
   already the no-op. A session fixture additionally snapshots and restores
   ``core.hooksPath`` as a belt-and-suspenders guard.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# ── 1. make scripts/ importable ────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# ── 2. neutralize the import-time git-hook side effect ─────────────────────
# Import _common first and stub install_git_hooks so that every subsequent
# ``from _common import install_git_hooks`` (run at module import time in the
# lint/build scripts) binds to the no-op, not the real function.
import _common  # noqa: E402


def _noop_install_git_hooks() -> None:  # pragma: no cover - trivial
    return None


_common.install_git_hooks = _noop_install_git_hooks  # type: ignore[assignment]


def _current_hooks_path() -> str | None:
    """Return the local git core.hooksPath value, or None if unset."""
    try:
        r = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    out = r.stdout.strip()
    return out or None


@pytest.fixture(scope="session", autouse=True)
def _guard_git_hooks_path():
    """Assert the test run does not mutate git core.hooksPath.

    Snapshots the value before any test runs and restores it after, then
    fails loudly if it moved. This is a safety net; the primary defense is
    the install_git_hooks no-op above.
    """
    before = _current_hooks_path()
    yield
    after = _current_hooks_path()
    if after != before:
        # Restore, then surface the leak.
        if before is None:
            subprocess.run(
                ["git", "config", "--unset", "core.hooksPath"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        else:
            subprocess.run(
                ["git", "config", "core.hooksPath", before],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        raise AssertionError(
            f"git core.hooksPath was mutated during the test run "
            f"(before={before!r}, after={after!r}); a script's "
            f"install_git_hooks() side effect leaked past the conftest no-op."
        )


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def write_file():
    """Return a helper that writes text to a path (creating parents)."""

    def _write(path: Path, text: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    return _write
