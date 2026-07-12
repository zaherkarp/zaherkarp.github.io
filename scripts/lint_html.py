#!/usr/bin/env python3
"""lint_html.py

HTML structural well-formedness for the hand-authored homepage and the
generated blog / resume / cv pages. README §Before pushing used to ask a
human to run a lenient `html.parser` balanced-tag smoke check; this
replaces it with a real HTML5-spec parse via tinyhtml5 (already in
requirements.txt, transitively through WeasyPrint) and fails on genuinely
malformed element structure.

Scope decision -- structural errors only. tinyhtml5, like every
html5lib-derived parser, always recovers and always yields a tree; its
`errors` list mixes two kinds:

  * TREE-BUILDER errors -- a tag closes something it did not open, an
    element is left unclosed at EOF, a `<td>` appears outside a table,
    two `<head>`s, content after `</body>`. These mean the DOM tree came
    out different from what the markup says. THESE are what this gate
    fails on (STRUCTURAL_CODES below).

  * TOKENIZER / character-level errors -- a bare `&` that is not a named
    entity, a `--` inside a comment, doctype-syntax quirks. These do NOT
    break the tree, and they occur in legitimate content this repo ships:
    raw KaTeX LaTeX source (`&=` alignment, `\\[ ... \\]`) in blog posts,
    and an inline CSS-documentation comment in index.html mentioning a
    `--custom-property`. Failing on them would false-positive on valid
    math/code and tempt weakening the linter, so they are deliberately
    out of scope.

This split is why the gate passes clean on the current repo (0 tree-builder
errors across every parsed page) while still catching the misnested /
unclosed structure the old lenient smoke check silently accepted.

GATE (hard fail, blocks push). Wired into scripts/hooks/pre-push and
.github/workflows/lint.yml. If it fails, fix the markup -- for the
homepage by hand, for a generated page by fixing the post source or
template and rebuilding. Do not add a structural code to the ignore
side to make a real break pass.
"""

from __future__ import annotations

import sys
from pathlib import Path

from tinyhtml5.parser import HTMLParser

from _common import install_git_hooks

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent

# Files parsed. index.html is hand-authored; the rest are generated
# (build_blog / build_resume) but a template or post-source slip can still
# emit malformed structure, which lint.yml's weekly bot-commit audit is the
# backstop for. Missing files are skipped (a fresh checkout may not have
# built blog/ or the resume yet).
STATIC_TARGETS = ["index.html", "resume.html", "cv.html"]
GLOB_TARGETS = ["blog/**/*.html"]

# Tree-builder (structural) error codes: the element tree came out wrong.
# Grouped by kind. Everything tinyhtml5 can emit that is NOT here is a
# tokenizer / character-level error and is intentionally ignored (see the
# module docstring). Pinned against tinyhtml5==2.1.0 (requirements.txt); a
# renamed code in a future bump would under-catch (the safe direction),
# never false-positive.
STRUCTURAL_CODES: frozenset[str] = frozenset(
    {
        # orphan / misnested / unclosed element tags
        "unexpected-end-tag",
        "unexpected-end-tag-after-body-innerhtml",
        "unexpected-end-tag-before-html",
        "unexpected-end-tag-treated-as",
        "end-tag-too-early",
        "end-tag-too-early-named",
        "end-tag-too-early-ignored",
        "end-tag-after-implied-root",
        "expected-one-end-tag-but-got-another",
        "expected-closing-tag-but-got-eof",
        "expected-closing-tag-but-got-char",
        "expected-named-closing-tag-but-got-eof",
        "no-end-tag",
        "unexpected-start-tag-implies-end-tag",
        # unclosed construct at EOF
        "eof-in-table",
        "eof-in-select",
        "eof-in-frameset",
        # table / select / caption / frameset structural violations
        "unexpected-cell-end-tag",
        "unexpected-cell-in-table-body",
        "unexpected-form-in-table",
        "unexpected-hidden-input-in-table",
        "unexpected-implied-end-tag-in-table",
        "unexpected-implied-end-tag-in-table-row",
        "unexpected-end-tag-in-table-body",
        "unexpected-end-tag-in-table-row",
        "unexpected-end-tag-implies-table-voodoo",
        "unexpected-start-tag-implies-table-voodoo",
        "unexpected-start-tag-out-of-table",
        "unexpected-start-tag-out-of-table-cell",
        "unexpected-table-start-tag-in-caption",
        "unexpected-table-end-tag-in-caption",
        "unexpected-select-in-select",
        "unexpected-input-in-select",
        "unexpected-end-tag-in-select",
        "unexpected-frameset-in-frameset-innerhtml",
        "unexpected-start-tag-in-frameset",
        "unexpected-end-tag-in-frameset",
        "unexpected-char-in-frameset",
        # document shape: two heads, no html root, content after body
        "two-heads-are-not-better-than-one",
        "non-html-root",
        "unexpected-char-after-body",
        "unexpected-char-after-frameset",
        "expected-eof-but-got-char",
        "expected-eof-but-got-end-tag",
        "expected-eof-but-got-start-tag",
        "unexpected-doctype",
    }
)


def iter_targets(root: Path):
    for rel in STATIC_TARGETS:
        p = root / rel
        if p.is_file():
            yield p
    for pattern in GLOB_TARGETS:
        yield from sorted(root.glob(pattern))


def structural_errors(markup: bytes):
    """Return the (position, code) structural errors for one document.

    Non-structural (tokenizer-level) errors are filtered out here, so the
    caller sees only genuine tree malformedness.
    """
    parser = HTMLParser()
    parser.parse(markup)
    return [
        (pos, code)
        for pos, code, _vars in parser.errors
        if code in STRUCTURAL_CODES
    ]


def run() -> int:
    failures: list[str] = []
    checked = 0
    for path in iter_targets(ROOT):
        checked += 1
        rel = path.relative_to(ROOT)
        for (line, col), code in structural_errors(path.read_bytes()):
            failures.append(f"{rel}:{line}:{col}: {code}")

    if failures:
        print("HTML structural lint found malformed markup:\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(
            f"\n{len(failures)} structural problem(s) across {checked} "
            f"page(s). Fix the markup (hand-edit index.html; for a "
            f"generated page fix the post source or template and rebuild). "
            f"Tokenizer-level nits (bare & in KaTeX, -- in a comment) are "
            f"out of scope by design; see lint_html.py.",
            file=sys.stderr,
        )
        return 1

    print(f"html lint: {checked} page(s) structurally well-formed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
