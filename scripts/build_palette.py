#!/usr/bin/env python3
"""Regenerate every consuming file's palette token block from palette.yaml.

Single source of truth: src/content/palette.yaml. Each target file carries a
marker pair around its color tokens (CSS `/* palette:start */ ... */` in
stylesheets and <style> blocks, XML `<!-- palette:start -->` in favicon.svg);
this script rewrites the span between them from the YAML.

Roles are semantic (bg / surface / ink / ink_sec / muted / rule / accent).
Each target maps roles to its own local custom-property names via TARGETS, so
one YAML change propagates into `--paper` on the homepage, `--text` in the
blog, `--bg`/`--surface` in the subpages, and so on.

Out of scope by design (see palette.yaml header): blog.css Solarized palette,
the print neutrals in the resume/cv PDF templates (only their --accent is
managed here), the two self-contained blog-post figures, and the epidemic
simulator's Plotly series colors.

Usage:
    python scripts/build_palette.py            # rewrite all targets
    python scripts/build_palette.py --check     # exit 1 if any target is stale

lint_palette.py imports render_target() so the check and the build agree.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    sys.exit("build_palette: PyYAML required (pip install -r scripts/requirements.txt)")

ROOT = Path(__file__).resolve().parent.parent
PALETTE_YAML = ROOT / "src" / "content" / "palette.yaml"

# Canonical emit order for the screen roles.
ROLE_ORDER = ["bg", "surface", "ink", "ink_sec", "muted", "rule", "accent"]

# Markers wrap DECLARATION LINES only, sitting inside whatever :root the file
# already has, so a file that mixes color tokens with sizing/Solarized (blog.css)
# works the same as one whose :root is colors-only (index.html). Screen targets
# carry two spans (light + dark); single-mode targets carry one.
#
# Each target: path, kind, and (for screen/accent kinds) a role->localname map.
# `kind`:
#   "screen"      -> two spans: palette:light and palette:dark (decl lines only)
#   "accent_only" -> one span:  a single --accent line (PDF templates; the rest
#                    of the print palette is calibrated and stays outside)
#   "favicon"     -> one span:  the <rect> fill (XML comment markers)
TARGETS = [
    {"path": "index.html", "kind": "screen",
     "map": {"bg": "--paper", "ink": "--ink", "muted": "--muted", "rule": "--rule", "accent": "--accent"}},
    # index.html @media print keeps its print-calibrated neutrals (white paper,
    # near-black ink) but its accent tracks the palette so no teal is orphaned.
    {"path": "index.html", "kind": "accent_only", "indent": "    ", "map": {"accent": "--accent"}},
    {"path": "blog.css", "kind": "screen",
     "map": {"bg": "--bg", "ink": "--text", "muted": "--muted", "rule": "--rule", "accent": "--accent"}},
    {"path": "404.html", "kind": "screen",
     "map": {"bg": "--bg", "ink": "--text", "ink_sec": "--text-sec", "muted": "--muted", "rule": "--rule", "accent": "--accent"}},
    {"path": "star-rating-predictor/index.html", "kind": "screen",
     "map": {"bg": "--bg", "surface": "--surface", "ink": "--text", "ink_sec": "--text-sec", "muted": "--muted", "rule": "--rule", "accent": "--accent"}},
    {"path": "epidemic-simulation/styles.css", "kind": "screen",
     "map": {"bg": "--bg", "surface": "--surface", "ink": "--text", "ink_sec": "--text-sec", "muted": "--muted", "rule": "--rule", "accent": "--accent"}},
    {"path": "life-in-weeks/index.html", "kind": "screen",
     "map": {"bg": "--bg", "surface": "--surface", "ink": "--text", "ink_sec": "--text-sec", "muted": "--muted", "rule": "--rule", "accent": "--accent"}},
    {"path": "scripts/templates/resume/resume-web.html", "kind": "screen",
     "map": {"bg": "--paper", "ink": "--ink", "muted": "--muted", "rule": "--rule", "accent": "--accent"}},
    {"path": "scripts/templates/resume/cv-web.html", "kind": "screen",
     "map": {"bg": "--paper", "ink": "--ink", "muted": "--muted", "rule": "--rule", "accent": "--accent"}},
    {"path": "scripts/templates/resume/resume.html", "kind": "accent_only", "map": {"accent": "--accent"}},
    {"path": "scripts/templates/resume/cv.html", "kind": "accent_only", "map": {"accent": "--accent"}},
    {"path": "favicon.svg", "kind": "favicon", "map": {}},
]

def _css(name: str) -> tuple[str, str]:
    return f"/* palette:{name}:start */", f"/* palette:{name}:end */"


def load_palette() -> dict:
    return yaml.safe_load(PALETTE_YAML.read_text())


def _decls(mapping: dict, mode_colors: dict, indent: str) -> str:
    """Declaration lines only, on their own lines between the markers."""
    lines = [f"{indent}{mapping[r]}: {mode_colors[r]};" for r in ROLE_ORDER if r in mapping]
    return "\n" + "\n".join(lines) + "\n"


def spans_for(target: dict, pal: dict) -> list[tuple[str, str, str]]:
    """Return [(start_marker, end_marker, body)] for every span in the target."""
    kind = target["kind"]
    if kind == "screen":
        ls, le = _css("light")
        ds, de = _css("dark")
        return [
            (ls, le, _decls(target["map"], pal["screen"]["light"], "  ")),
            (ds, de, _decls(target["map"], pal["screen"]["dark"], "    ")),
        ]
    if kind == "accent_only":
        s, e = _css("print")
        indent = target.get("indent", "  ")
        return [(s, e, f"\n{indent}--accent: {pal['print']['accent']};\n")]
    if kind == "favicon":
        # Standalone asset: can't use CSS vars, so the generator writes the
        # literals. Both derive from screen.light (rect = accent, glyph = bg),
        # so the favicon tracks the palette with no separate value to sync.
        light = pal["screen"]["light"]
        return [("<!-- palette:start -->", "<!-- palette:end -->",
                 f'\n  <rect width="32" height="32" rx="6" fill="{light["accent"]}"/>\n'
                 f"  <text x=\"16\" y=\"24\" font-family=\"Palatino, 'Palatino Linotype', Georgia, 'Book Antiqua', serif\" "
                 f'font-size="22" font-weight="normal" text-anchor="middle" fill="{light["bg"]}" letter-spacing="-0.5">ZK</text>\n')]
    raise ValueError(f"unknown target kind: {kind}")


def apply_target(target: dict, pal: dict, *, write: bool) -> bool:
    """Return True if the target is already up to date; rewrite it if write."""
    path = ROOT / target["path"]
    text = path.read_text()
    for start, end, body in spans_for(target, pal):
        if start not in text or end not in text:
            raise SystemExit(f"build_palette: markers {start!r}/{end!r} not found in {target['path']}")
        pre, _, rest = text.partition(start)
        _, _, post = rest.partition(end)
        text = pre + start + body + end + post
    original = path.read_text()
    if text == original:
        return True
    if write:
        path.write_text(text)
    return False


def render_target(target: dict, pal: dict) -> str:
    """Concatenated span bodies — used by lint_palette for a quick digest."""
    return "".join(body for _, _, body in spans_for(target, pal))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if any target is stale, write nothing")
    args = ap.parse_args()
    pal = load_palette()
    stale = []
    for target in TARGETS:
        up_to_date = apply_target(target, pal, write=not args.check)
        if not up_to_date:
            stale.append(target["path"])
    if args.check:
        if stale:
            print("palette blocks stale (run scripts/build_palette.py):")
            for p in stale:
                print(f"  - {p}")
            return 1
        print("palette: all blocks match palette.yaml")
        return 0
    if stale:
        print(f"palette: rewrote {len(stale)} file(s):")
        for p in stale:
            print(f"  - {p}")
    else:
        print("palette: no changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
