"""Layer 2 -- lint_palette contract-violation detection.

main() runs three independent checks against the palette single-source
contract (see CLAUDE.md "Palette pipeline"): drift (a target's committed
marker-span body no longer matches what build_palette.spans_for() renders
from palette.yaml), containment (an --accent: assignment sitting outside a
palette:* marker span in a managed file), and post-figure parity (the two
self-contained blog-post figures' hardcoded accent hexes must equal the
canonical screen accent). Each is exercised here against a synthetic tree
built under tmp_path, with bp.TARGETS / bp.ROOT and lint_palette.ROOT /
POST_FIGURES monkeypatched to point at it.

ROOT is an import-time alias (`lint_palette.ROOT = bp.ROOT`, set once when
lint_palette.py is first imported), so patching one module's copy does NOT
move the other's. check_drift() delegates to bp.apply_target(), which reads
bp.ROOT; check_containment() and check_post_figures() read lint_palette.ROOT
directly. A scenario touching either family must patch both. Canonical
accent values come from the real palette.yaml via bp.load_palette() rather
than being hardcoded, so these tests survive a repalette.

The clean-repo pass case lives in test_baseline_clean.py, per the division
test_lint_html.py documents; this module covers a synthetic-tree pass
control plus each check's violation path.
"""

from __future__ import annotations

import build_palette as bp
import lint_palette


def _screen_target(path: str = "palette-fixture.css") -> dict:
    """A minimal 'screen'-kind target: one file, five roles, both modes."""
    return {
        "path": path,
        "kind": "screen",
        "map": {
            "bg": "--paper", "ink": "--ink", "muted": "--muted",
            "rule": "--rule", "accent": "--accent",
        },
    }


def _render_fixture(target: dict, pal: dict, *, stray_accent: bool = False, corrupt: bool = False) -> str:
    """Build synthetic CSS text carrying `target`'s two palette:* spans.

    With both flags False the span bodies are exactly what
    bp.spans_for(target, pal) renders, so the file is drift- and
    containment-clean (the pass control).

    corrupt=True mismatches the light span's rendered body against what
    spans_for() would produce -- a Check A (drift) violation.
    stray_accent=True adds an --accent: assignment outside both marker
    spans -- a Check B (containment) violation.
    """
    (ls, le, lbody), (ds, de, dbody) = bp.spans_for(target, pal)
    if corrupt:
        lbody = lbody.replace(pal["screen"]["light"]["accent"], "#ff0000")
    stray = "  .rogue { --accent: #ff0000; }\n" if stray_accent else ""
    return (
        "/* fixture: synthetic palette-consuming file, not a real target */\n"
        f"{stray}"
        ":root {\n"
        f"  {ls}{lbody}{le}\n"
        "}\n\n"
        "@media (prefers-color-scheme: dark) {\n"
        "  :root {\n"
        f"    {ds}{dbody}{de}\n"
        "  }\n"
        "}\n"
    )


def _install(monkeypatch, tmp_path, *, targets, files, post_figures=None):
    """Write `files` (rel path -> text) under tmp_path, then repoint bp/lint_palette at it."""
    for rel, content in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    monkeypatch.setattr(bp, "ROOT", tmp_path)
    monkeypatch.setattr(lint_palette, "ROOT", tmp_path)
    monkeypatch.setattr(bp, "TARGETS", targets)
    monkeypatch.setattr(lint_palette, "POST_FIGURES", [] if post_figures is None else post_figures)


# ── synthetic-tree pass control ─────────────────────────────────────────────

def test_synthetic_tree_clean_passes(monkeypatch, tmp_path, capsys):
    pal = bp.load_palette()
    target = _screen_target()
    fixture = _render_fixture(target, pal)
    _install(monkeypatch, tmp_path, targets=[target], files={target["path"]: fixture})
    rc = lint_palette.main()
    assert rc == 0, capsys.readouterr().out


# ── Check A: drift ───────────────────────────────────────────────────────────

def test_drift_stale_span_fails(monkeypatch, tmp_path, capsys):
    pal = bp.load_palette()
    target = _screen_target()
    fixture = _render_fixture(target, pal, corrupt=True)
    _install(monkeypatch, tmp_path, targets=[target], files={target["path"]: fixture})
    rc = lint_palette.main()
    out = capsys.readouterr().out
    assert rc == 1
    assert "stale in" in out, out


# ── Check B: containment ────────────────────────────────────────────────────

def test_containment_stray_accent_fails(monkeypatch, tmp_path, capsys):
    pal = bp.load_palette()
    target = _screen_target()
    fixture = _render_fixture(target, pal, stray_accent=True)
    _install(monkeypatch, tmp_path, targets=[target], files={target["path"]: fixture})
    rc = lint_palette.main()
    out = capsys.readouterr().out
    assert rc == 1
    assert "assigned outside a palette:* span" in out, out


# ── Check C: self-contained post figures ────────────────────────────────────

def test_post_figure_off_palette_accent_fails(monkeypatch, tmp_path, capsys):
    fixture_rel = "src/content/blog/off-palette-fixture.md"
    fixture = "some prose\n\n```css\n--pc-accent: #ff0000;\n```\n"
    _install(
        monkeypatch, tmp_path,
        targets=[],
        files={fixture_rel: fixture},
        post_figures=[fixture_rel],
    )
    rc = lint_palette.main()
    out = capsys.readouterr().out
    assert rc == 1
    assert "does not match" in out, out


def test_post_figure_on_palette_accent_passes(monkeypatch, tmp_path, capsys):
    pal = bp.load_palette()
    light = pal["screen"]["light"]["accent"]
    fixture_rel = "src/content/blog/on-palette-fixture.md"
    fixture = f"some prose\n\n```css\n--pc-accent: {light};\n```\n"
    _install(
        monkeypatch, tmp_path,
        targets=[],
        files={fixture_rel: fixture},
        post_figures=[fixture_rel],
    )
    rc = lint_palette.main()
    assert rc == 0, capsys.readouterr().out
