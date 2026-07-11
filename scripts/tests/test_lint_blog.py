"""Layer 2 -- lint_blog violation detection.

Feeds check_post() minimal bad posts covering each of the four storage-side
rules and asserts each is reported; plus a clean post that returns no
violations. check_post(path) reads the file and honors draft/underscore
skips, so fixtures are written to tmp_path with draft:false frontmatter.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import lint_blog

FM = "---\ntitle: Fixture Post\ndraft: false\n---\n\n"


def _post(tmp_path: Path, body: str, name: str = "fixture.md") -> Path:
    p = tmp_path / name
    p.write_text(FM + body, encoding="utf-8")
    return p


def test_html_comment_flagged(tmp_path):
    v = lint_blog.check_post(_post(tmp_path, "Intro.\n\n<!-- TODO fill this in -->\n\nMore.\n"))
    assert any("HTML comment in a published post" in s for s in v), v


def test_fenced_block_inside_comment_flagged(tmp_path):
    body = "Intro.\n\n<!--\n```python\nx = 1\n```\n-->\n\nMore.\n"
    v = lint_blog.check_post(_post(tmp_path, body))
    assert any("fenced code block inside an HTML comment" in s for s in v), v


def test_blockquote_mermaid_flagged(tmp_path):
    body = "Intro.\n\n> flowchart LR\n> A --> B\n\nMore.\n"
    v = lint_blog.check_post(_post(tmp_path, body))
    assert any("blockquote-as-diagram" in s for s in v), v


def test_blank_line_inside_svg_flagged(tmp_path):
    body = 'Intro.\n\n<svg viewBox="0 0 10 10">\n\n<line x1="0" y1="0" x2="10" y2="10"/>\n</svg>\n'
    v = lint_blog.check_post(_post(tmp_path, body))
    assert any("blank line" in s and "<svg>" in s for s in v), v


def test_clean_post_has_no_violations(tmp_path):
    body = (
        "A normal paragraph with prose.\n\n"
        "```python\n# a <!-- literal --> example is fine inside a fence\nx = 1\n```\n\n"
        '<svg viewBox="0 0 10 10"><line x1="0" y1="0" x2="10" y2="10"/></svg>\n'
    )
    assert lint_blog.check_post(_post(tmp_path, body)) == []


def test_draft_post_is_skipped(tmp_path):
    p = tmp_path / "draft.md"
    p.write_text("---\ntitle: D\ndraft: true\n---\n\n<!-- leaked comment -->\n", encoding="utf-8")
    assert lint_blog.check_post(p) == []


def test_underscore_post_is_skipped(tmp_path):
    p = tmp_path / "_wip.md"
    p.write_text(FM + "<!-- leaked comment -->\n", encoding="utf-8")
    assert lint_blog.check_post(p) == []
