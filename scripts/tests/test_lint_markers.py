"""Layer 2 -- lint_markers structure detection.

The generic structure walk (_scan_pairs + _check_structure) is a pure text
function, so it is fed marker strings directly: a well-formed pair is clean,
and orphan / unterminated / crossed / duplicate pairs each produce a failure.
"""

from __future__ import annotations

import lint_markers


def _structure_failures(text: str):
    tokens = lint_markers._scan_pairs(text)
    failures, completed = lint_markers._check_structure("fixture", tokens)
    return failures, completed


def test_well_formed_pair_is_clean():
    text = "<!-- foo:start -->\ncontent\n<!-- foo:end -->\n"
    failures, completed = _structure_failures(text)
    assert failures == []
    assert "foo" in completed


def test_unterminated_start_flagged():
    text = "<!-- foo:start -->\ncontent, no end\n"
    failures, _ = _structure_failures(text)
    assert any("never closed" in f for f in failures), failures


def test_orphan_end_flagged():
    text = "content\n<!-- foo:end -->\n"
    failures, _ = _structure_failures(text)
    assert any("no open" in f for f in failures), failures


def test_nested_start_flagged():
    text = "<!-- foo:start -->\n<!-- bar:start -->\n<!-- bar:end -->\n<!-- foo:end -->\n"
    failures, _ = _structure_failures(text)
    assert any("must not nest or overlap" in f for f in failures), failures


def test_crossed_pairs_flagged():
    text = "<!-- foo:start -->\n<!-- bar:end -->\n"
    failures, _ = _structure_failures(text)
    assert any("wrong region" in f for f in failures), failures


def test_js_marker_form_recognized():
    text = "// blog-thoughts:start\nstuff\n// blog-thoughts:end\n"
    failures, completed = _structure_failures(text)
    assert failures == []
    assert "blog-thoughts" in completed
