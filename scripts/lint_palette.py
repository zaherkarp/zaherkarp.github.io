#!/usr/bin/env python3
"""Guard the palette single-source-of-truth contract.

Three checks, all hard failures:

  A. No drift. Every target's committed palette block matches what
     palette.yaml renders (same contract as build_palette.py --check).

  B. No off-token accent. In every pipeline-managed file, an `--accent:`
     ASSIGNMENT may appear ONLY inside a `palette:` marker span. This is the
     wall that keeps the accent from being hardcoded off-token again: a stray
     `--accent: #...` anywhere else (including a stale old value after a
     repalette) fails the build. Value-agnostic, so it catches both new
     hardcodes and leftovers from a color change.

  C. Self-contained post figures match. The two blog-post figures keep their
     own `--pc-accent` / `--rw-accent` tokens (per the blog-figure "renders
     standalone" convention), but their accent values must equal
     screen.light/dark.accent so they can't drift silently.

Run standalone: python scripts/lint_palette.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_palette as bp  # noqa: E402

ROOT = bp.ROOT

# Blog-post figures that legitimately carry their own accent tokens (Check C).
POST_FIGURES = [
    "src/content/blog/medicare-advantage-market-exits-timing.md",
    "src/content/blog/should-i-buy-ram-now.md",
]

ACCENT_ASSIGN = re.compile(r"--accent\s*:", re.IGNORECASE)


def strip_palette_spans(text: str) -> str:
    """Remove everything inside palette:* marker spans (any span name)."""
    # CSS spans: /* palette:NAME:start */ ... /* palette:NAME:end */
    text = re.sub(
        r"/\* palette:[a-z]+:start \*/.*?/\* palette:[a-z]+:end \*/",
        "", text, flags=re.DOTALL,
    )
    # favicon XML span
    text = re.sub(r"<!-- palette:start -->.*?<!-- palette:end -->", "", text, flags=re.DOTALL)
    return text


def check_drift(pal: dict) -> list[str]:
    errors = []
    for target in bp.TARGETS:
        if not bp.apply_target(target, pal, write=False):
            errors.append(f"palette block stale in {target['path']} (run scripts/build_palette.py)")
    return errors


def check_containment() -> list[str]:
    errors = []
    seen = set()
    for target in bp.TARGETS:
        path = target["path"]
        if path in seen:
            continue
        seen.add(path)
        text = (ROOT / path).read_text()
        remainder = strip_palette_spans(text)
        if ACCENT_ASSIGN.search(remainder):
            nums = [i + 1 for i, ln in enumerate(remainder.splitlines()) if ACCENT_ASSIGN.search(ln)]
            errors.append(
                f"{path}: `--accent:` assigned outside a palette:* span "
                f"(line(s) {nums}); move it into palette.yaml or a marker span"
            )
    return errors


def check_post_figures(pal: dict) -> list[str]:
    errors = []
    light = pal["screen"]["light"]["accent"].lower()
    dark = pal["screen"]["dark"]["accent"].lower()
    for rel in POST_FIGURES:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text().lower()
        # every accent hex the figure hardcodes must be a canonical accent value
        hexes = set(re.findall(r"--(?:pc|rw)-accent\s*:\s*(#[0-9a-f]{3,6})", text))
        hexes |= set(re.findall(r"const\s+accent\s*=\s*dark\s*\?\s*'(#[0-9a-f]{3,6})'\s*:\s*'(#[0-9a-f]{3,6})'", text) and
                     [m for pair in re.findall(r"const\s+accent\s*=\s*dark\s*\?\s*'(#[0-9a-f]{3,6})'\s*:\s*'(#[0-9a-f]{3,6})'", text) for m in pair])
        for h in hexes:
            if h not in (light, dark):
                errors.append(
                    f"{rel}: self-contained figure accent {h} does not match "
                    f"palette.yaml (light {light} / dark {dark})"
                )
    return errors


def main() -> int:
    pal = bp.load_palette()
    errors = check_drift(pal) + check_containment() + check_post_figures(pal)
    if errors:
        print("lint_palette: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("lint_palette: palette single-source contract intact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
