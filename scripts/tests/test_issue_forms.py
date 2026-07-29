"""_issue_forms.parse_issue_form -- shared GitHub issue-form body parser.

Shared by blog_ideas_intake.py and blog_draft_edit_intake.py. The
known_labels restriction is load-bearing for the latter: a submitted post
body routinely contains its own markdown headings, which would otherwise be
misread as new form fields and silently truncate everything after them.
"""

from __future__ import annotations

from _issue_forms import parse_issue_form


def test_basic_sections_and_no_response_dropped():
    body = "### Title\n\nMy Title\n\n### Angle\n\n_No response_\n\n### Tags\n\na, b\n"
    sections = parse_issue_form(body)
    assert sections == {"title": "My Title", "tags": "a, b"}


def test_without_known_labels_any_heading_starts_a_new_section():
    """Historical (default) behavior, kept for blog_ideas_intake.py, whose
    fields are unlikely to contain heading-shaped lines."""
    body = "### New body (markdown)\n\n## TL;DR\n\n- point\n"
    sections = parse_issue_form(body)
    # The embedded "## TL;DR" heading swallowed the rest of the value.
    assert "new body (markdown)" not in sections
    assert sections.get("tl;dr") == "- point"


def test_known_labels_prevents_embedded_headings_from_truncating_a_value():
    body = "### New body (markdown)\n\n## TL;DR\n\n- point\n\n### Subsection\n\nmore\n"
    sections = parse_issue_form(body, known_labels={"new body (markdown)"})
    assert sections["new body (markdown)"] == "## TL;DR\n\n- point\n\n### Subsection\n\nmore"


def test_known_labels_still_recognizes_a_real_boundary():
    body = "### Slug\n\nmy-slug\n\n### New body (markdown)\n\nbody text\n"
    sections = parse_issue_form(body, known_labels={"slug", "new body (markdown)"})
    assert sections == {"slug": "my-slug", "new body (markdown)": "body text"}


def test_empty_body_returns_no_sections():
    assert parse_issue_form("") == {}
    assert parse_issue_form(None) == {}
