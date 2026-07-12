"""Layer 2 -- lint_html structural well-formedness.

structural_errors() is a pure function over a bytes document, so both paths
are exercised directly: malformed nesting flags, and the tokenizer-level
nits this repo legitimately ships (bare & in KaTeX math, -- in an HTML
comment) do NOT flag. The clean-repo pass case lives in test_baseline_clean.
"""

from __future__ import annotations

import lint_html

_HEAD = b"<!doctype html><html><head><title>t</title></head><body>"
_TAIL = b"</body></html>"


def _codes(markup: bytes):
    return [code for _pos, code in lint_html.structural_errors(markup)]


# ── structural malformedness flags ─────────────────────────────────────────

def test_misnested_div_p_flagged():
    assert _codes(_HEAD + b"<div><p>x</div></p>" + _TAIL)


def test_orphan_end_tag_flagged():
    assert _codes(_HEAD + b"</span>text" + _TAIL)


def test_loose_table_cell_flagged():
    assert _codes(_HEAD + b"<td>loose cell</td>" + _TAIL)


def test_content_after_body_flagged():
    codes = _codes(_HEAD + b"<p>ok</p>" + _TAIL + b"stray text")
    assert "expected-eof-but-got-char" in codes, codes


# ── legitimate content does NOT flag ───────────────────────────────────────

def test_clean_document_passes():
    assert _codes(_HEAD + b"<p>ok</p>" + _TAIL) == []


def test_katex_bare_ampersand_not_structural():
    # \[ a &= b \] is raw KaTeX LaTeX source; the bare & is a tokenizer nit,
    # not malformed structure, and must not flag (this repo ships it).
    assert _codes(_HEAD + b"<p>\\[ a &= b \\]</p>" + _TAIL) == []


def test_double_dash_in_comment_not_structural():
    # index.html's inline CSS docs mention --custom-property inside a comment.
    assert _codes(_HEAD + b"<!-- a --v custom prop --><p>ok</p>" + _TAIL) == []


def test_katex_display_math_delimiters_pass():
    body = b"<p>\\[\n\\tfrac{dS}{dt} &= -\\beta S I / N \\\\\n\\]</p>"
    assert _codes(_HEAD + body + _TAIL) == []


# ── the code set is honestly a filter, not empty ───────────────────────────

def test_structural_codes_is_nonempty_and_excludes_tokenizer_codes():
    assert "unexpected-end-tag" in lint_html.STRUCTURAL_CODES
    # tokenizer-level codes seen on the real clean repo must be excluded,
    # or the gate would false-positive on valid KaTeX/CSS-doc content.
    for benign in ("expected-named-entity", "unexpected-char-in-comment",
                   "expected-tag-name"):
        assert benign not in lint_html.STRUCTURAL_CODES
