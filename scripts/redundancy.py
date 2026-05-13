#!/usr/bin/env python3
"""Shared redundancy-toggle checker.

Used by scripts/hooks/pre-push and .github/workflows/build_blog.yml to
decide whether the `blog` CLI's pre-flight makes the legacy lint runs
redundant for this push.

CLI:
    python scripts/redundancy.py <toggle>

Exits 0 if the caller should *skip* the legacy check, 1 if it should
run. The convention matches `if python scripts/redundancy.py foo; then
SKIP; fi` in bash.

Config:   scripts/blog.config.yaml -- `redundancy.<toggle>` key.
          Values: "always" (run) or "skip-if-cli-linted" (skip when the
          HEAD commit message contains a `Blog-CLI-Linted:` trailer).

Detection: parses the output of `git log -1 --format=%B HEAD` for the
trailer. In CI, `HEAD` is the triggering push commit, so the trailer
present == this push was made by `blog publish`.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "scripts" / "blog.config.yaml"

KNOWN_TOGGLES = ("prepush_lint", "ci_blog_lint", "ci_portfolio_lint")
VALID_VALUES = ("always", "skip-if-cli-linted")

TRAILER_RE = re.compile(r"^Blog-CLI-Linted:\s+\S+", re.MULTILINE)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def toggle_value(toggle: str) -> str:
    """Return the toggle's current value, defaulting to 'always' if the
    config file is missing or malformed."""
    if toggle not in KNOWN_TOGGLES:
        return "always"
    cfg = load_config()
    section = cfg.get("redundancy", {}) or {}
    value = section.get(toggle, "always")
    return value if value in VALID_VALUES else "always"


def head_has_trailer() -> bool:
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%B", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    if r.returncode != 0:
        return False
    return bool(TRAILER_RE.search(r.stdout))


def should_skip(toggle: str) -> bool:
    """True if the caller should skip the legacy check for this toggle."""
    value = toggle_value(toggle)
    if value != "skip-if-cli-linted":
        return False
    return head_has_trailer()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            f"usage: {Path(__file__).name} <toggle>\n"
            f"known toggles: {', '.join(KNOWN_TOGGLES)}",
            file=sys.stderr,
        )
        return 2
    toggle = argv[1]
    if toggle not in KNOWN_TOGGLES:
        print(
            f"unknown toggle: {toggle}\n"
            f"known: {', '.join(KNOWN_TOGGLES)}",
            file=sys.stderr,
        )
        return 2
    return 0 if should_skip(toggle) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
