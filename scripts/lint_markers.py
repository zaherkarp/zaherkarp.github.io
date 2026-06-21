#!/usr/bin/env python3
"""lint_markers.py

Validates the integrity of the build-time injection markers that the
generator scripts splice their output between. The marker-injection
pattern (CLAUDE.md / docs/pipelines.md) lets build_portfolio.py,
build_cliff.py, and build_resume.py write into otherwise hand-authored
files by replacing only the text between a

    <!-- NAME:start -->  ...  <!-- NAME:end -->

comment pair (or the `// NAME:start` / `// NAME:end` JS form in
life-in-weeks/index.html). Nothing else guards those markers, so a
stray hand edit that deletes one end, duplicates a start, crosses two
pairs, or removes a marker a generator depends on would either corrupt
the host file on the next build or make a generator silently no-op.
This linter is the cheap structural check that closes that gap.

Two checks per file:

  1. STRUCTURE (generic): every `:start` / `:end` token found in the
     file pairs cleanly. Regions are sequential and never nested, so at
     most one region may be open at a time. Catches orphan starts/ends,
     duplicate opens, crossed pairs, and unterminated regions.

  2. PRESENCE (named): each marker a generator targets must still be
     present as a completed pair, so an accidental deletion is caught
     before the generator runs against a file that no longer has its
     injection point.

Plus a placeholder check: cv.md must carry exactly one
`<!-- publications -->` placeholder (build_resume.py replaces it in
place; it is not a start/end pair).

GATE (hard fail, blocks push). Wired into scripts/hooks/pre-push and
.github/workflows/lint.yml. To add a new injected region, add its name
to PAIR_MARKERS below in the same change that adds the markers to the
file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _common import install_git_hooks

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent

# Files with start/end marker pairs -> the marker names a generator
# injects into. Presence of each (as a completed pair) is required.
PAIR_MARKERS: dict[str, list[str]] = {
    "index.html": [
        "activity-grid",
        "writing-list",
        "writing-index",
        "cliff-path",
        "pub-list",
        "updated",
    ],
    "life-in-weeks/index.html": [
        "blog-thoughts",
    ],
    "src/content/resume.md": [
        "skills",
    ],
}

# Files with a single replace-in-place placeholder -> required count.
PLACEHOLDER_MARKERS: dict[str, dict[str, int]] = {
    "src/content/cv.md": {"publications": 1},
}

# A marker line is the marker alone on its line, in either comment form:
#   <!-- name:start -->   (HTML)        // name:start   (JS)
_MARKER_RE = re.compile(
    r"^\s*(?:<!--\s*([a-z0-9-]+):(start|end)\s*-->|//\s*([a-z0-9-]+):(start|end))\s*$"
)
_PLACEHOLDER_RE_TMPL = r"<!--\s*{name}\s*-->"


def _scan_pairs(text: str) -> tuple[list[tuple[int, str, str]], set[str]]:
    """Return (tokens, completed_names).

    tokens: ordered (lineno, name, kind) for every marker line.
    """
    tokens: list[tuple[int, str, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        m = _MARKER_RE.match(line)
        if not m:
            continue
        name = m.group(1) or m.group(3)
        kind = m.group(2) or m.group(4)
        tokens.append((i, name, kind))
    return tokens, set()


def _check_structure(rel: str, tokens: list[tuple[int, str, str]]) -> tuple[list[str], set[str]]:
    """Single-open-at-a-time walk. Returns (failures, completed_names)."""
    failures: list[str] = []
    completed: set[str] = set()
    open_name: str | None = None
    open_line = 0
    for lineno, name, kind in tokens:
        if kind == "start":
            if open_name is not None:
                failures.append(
                    f"{rel}:{lineno}: '{name}:start' opens while "
                    f"'{open_name}:start' (line {open_line}) is still open "
                    f"-- marker regions must not nest or overlap."
                )
            open_name = name
            open_line = lineno
        else:  # end
            if open_name is None:
                failures.append(
                    f"{rel}:{lineno}: '{name}:end' with no open '{name}:start'."
                )
            elif open_name != name:
                failures.append(
                    f"{rel}:{lineno}: '{name}:end' closes the wrong region "
                    f"-- '{open_name}:start' (line {open_line}) is open."
                )
                open_name = None
            else:
                completed.add(name)
                open_name = None
    if open_name is not None:
        failures.append(
            f"{rel}:{open_line}: '{open_name}:start' is never closed."
        )
    return failures, completed


def run() -> int:
    failures: list[str] = []
    checked = 0

    for rel, required in PAIR_MARKERS.items():
        path = ROOT / rel
        if not path.exists():
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        tokens, _ = _scan_pairs(text)
        struct_failures, completed = _check_structure(rel, tokens)
        failures.extend(struct_failures)
        for name in required:
            if name not in completed:
                failures.append(
                    f"{rel}: required marker pair '{name}:start' / "
                    f"'{name}:end' is missing or malformed -- a generator "
                    f"injects here (see docs/pipelines.md)."
                )

    for rel, names in PLACEHOLDER_MARKERS.items():
        path = ROOT / rel
        if not path.exists():
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        for name, want in names.items():
            got = len(re.findall(_PLACEHOLDER_RE_TMPL.format(name=re.escape(name)), text))
            if got != want:
                failures.append(
                    f"{rel}: expected {want} '<!-- {name} -->' placeholder(s), "
                    f"found {got}."
                )

    if failures:
        print("Marker-integrity lint found problems:\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(
            f"\n{len(failures)} marker problem(s). See docs/pipelines.md "
            f"§marker-injection pattern.",
            file=sys.stderr,
        )
        return 1

    print(f"marker lint: injection markers intact across {checked} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(run())
