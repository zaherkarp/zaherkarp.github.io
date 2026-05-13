#!/usr/bin/env python3
"""Shared redundancy-toggle checker.

Used by scripts/hooks/pre-push and .github/workflows/build_blog.yml to
decide whether the `blog` CLI's pre-flight makes the legacy lint runs
redundant for this push.

CLI:
    python scripts/redundancy.py <toggle>
    python scripts/redundancy.py <toggle> --range <before> <after> [<before> <after> ...]

Exits 0 if the caller should *skip* the legacy check, 1 if it should
run. The convention matches `if python scripts/redundancy.py foo; then
SKIP; fi` in bash.

Config:   scripts/blog.config.yaml -- `redundancy.<toggle>` key.
          Values: "always" (run) or "skip-if-cli-linted" (skip when the
          relevant commit messages contain a `Blog-CLI-Linted:` trailer).

Detection:
  - With --range: every commit in `git rev-list <before>..<after>` (for
    each (before, after) pair) must carry the trailer, AND at least one
    commit must exist across all ranges. Any all-zeros sha, missing
    commit, or unresolvable range falls back to "run lints" -- the
    safe default that closes the multi-commit-push hole called out in
    the original commit message.
  - Without --range: falls back to checking HEAD only. Used for
    workflow_dispatch, schedule, or manual invocation outside a hook
    context.
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

ZERO_SHA = "0" * 40


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


def _git(args: list[str], timeout: int = 10) -> tuple[int, str]:
    try:
        r = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 1, ""
    return r.returncode, r.stdout


def head_has_trailer() -> bool:
    code, out = _git(["log", "-1", "--format=%B", "HEAD"], timeout=5)
    if code != 0:
        return False
    return bool(TRAILER_RE.search(out))


def _commit_has_trailer(sha: str) -> bool:
    code, out = _git(["log", "-1", "--format=%B", sha], timeout=5)
    if code != 0:
        return False
    return bool(TRAILER_RE.search(out))


def range_all_trailered(ranges: list[tuple[str, str]]) -> bool:
    """True iff every commit across all (before, after) ranges carries the
    trailer AND at least one commit exists.

    Returns False (i.e. "run lints") on any of:
      - empty ranges list
      - any range whose `before` is all-zeros (new branch -- no base to
        bound against)
      - any range whose `after` is all-zeros (deletion -- nothing to lint,
        but we can't claim "all trailered" either)
      - any `git rev-list` failure (missing commit, shallow clone, etc.)
      - any commit in any range whose message lacks the trailer
      - all ranges resolve but contain zero commits (nothing to verify)
    """
    if not ranges:
        return False

    any_commits = False
    for before, after in ranges:
        if not after or after == ZERO_SHA:
            # Deletion. Nothing to lint, but also nothing we've verified.
            continue
        if not before or before == ZERO_SHA:
            # New branch -- no remote base. Can't bound the range.
            return False
        code, out = _git(["rev-list", f"{before}..{after}"])
        if code != 0:
            return False
        shas = [s for s in out.split() if s]
        if not shas:
            continue
        any_commits = True
        for sha in shas:
            if not _commit_has_trailer(sha):
                return False
    return any_commits


def should_skip(toggle: str, ranges: list[tuple[str, str]] | None = None) -> bool:
    """True if the caller should skip the legacy check for this toggle."""
    if toggle_value(toggle) != "skip-if-cli-linted":
        return False
    if ranges is not None:
        return range_all_trailered(ranges)
    return head_has_trailer()


def _parse_ranges(rest: list[str]) -> list[tuple[str, str]] | None:
    """Parse `--range A B [A B ...]` trailing args.
    Returns None if `--range` is absent; an empty list is treated as a
    parse error by the caller."""
    if not rest:
        return None
    if rest[0] != "--range":
        return None
    pairs = rest[1:]
    if len(pairs) == 0 or len(pairs) % 2 != 0:
        return []
    return [(pairs[i], pairs[i + 1]) for i in range(0, len(pairs), 2)]


def main(argv: list[str]) -> int:
    usage = (
        f"usage: {Path(__file__).name} <toggle> [--range <before> <after> ...]\n"
        f"known toggles: {', '.join(KNOWN_TOGGLES)}"
    )
    if len(argv) < 2:
        print(usage, file=sys.stderr)
        return 2
    toggle = argv[1]
    if toggle not in KNOWN_TOGGLES:
        print(f"unknown toggle: {toggle}\nknown: {', '.join(KNOWN_TOGGLES)}", file=sys.stderr)
        return 2

    rest = argv[2:]
    if rest:
        ranges = _parse_ranges(rest)
        if ranges is None or len(ranges) == 0:
            print(usage, file=sys.stderr)
            return 2
        return 0 if should_skip(toggle, ranges) else 1
    return 0 if should_skip(toggle) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
