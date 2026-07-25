"""Layer 2 -- lint_ideas: idea-ledger schema and referential integrity.

The ledger (src/content/blog-ideas.yaml) and the posts directory are two
halves of one pipeline, joined by `slug`. These tests pin the gate that keeps
them aligned: a pass against the real repo tree, plus one violation case per
rule, plus the informational (never-failing) orphan report.

lint_ideas.run() takes an optional path, so fixtures point at tmp_path
directly rather than patching module globals.
"""

from __future__ import annotations

import textwrap

import pytest

import _ideas
import lint_ideas


def write_ledger(tmp_path, body: str):
    p = tmp_path / "blog-ideas.yaml"
    p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return p


# ── pass cases ─────────────────────────────────────────────────────────────


def test_real_repo_ledger_passes(capsys):
    """The committed ledger must be clean, like every other gate lint."""
    assert lint_ideas.run() == 0, capsys.readouterr().err


def test_absent_ledger_skips_cleanly(tmp_path):
    assert lint_ideas.run(tmp_path / "nope.yaml") == 0


def test_empty_ledger_passes(tmp_path):
    p = tmp_path / "blog-ideas.yaml"
    p.write_text("# header only\n", encoding="utf-8")
    assert lint_ideas.run(p) == 0


def test_idea_row_without_slug_passes(tmp_path, capsys):
    p = write_ledger(tmp_path, """
        - id: some-idea
          title: Some idea
          note: the angle
          added: 2026-01-01
          status: idea
    """)
    assert lint_ideas.run(p) == 0, capsys.readouterr().err


# ── violation cases, one per rule ──────────────────────────────────────────


@pytest.mark.parametrize(
    "body,needle",
    [
        # required field missing
        ("""
         - id: no-title
           added: 2026-01-01
           status: idea
         """, "missing required field `title`"),
        # id shape
        ("""
         - id: Not_A_Slug
           title: T
           added: 2026-01-01
           status: idea
         """, "slug-form"),
        # duplicate id
        ("""
         - id: dup
           title: One
           added: 2026-01-01
           status: idea
         - id: dup
           title: Two
           added: 2026-01-01
           status: idea
         """, "duplicate id"),
        # unknown key (typo guard)
        ("""
         - id: typo
           title: T
           added: 2026-01-01
           status: idea
           tag: singular
         """, "unknown field `tag`"),
        # bad status
        ("""
         - id: bad-status
           title: T
           added: 2026-01-01
           status: someday
         """, "is not one of"),
        # added in the future
        ("""
         - id: future
           title: T
           added: 2099-01-01
           status: idea
         """, "in the future"),
        # drafting with no slug
        ("""
         - id: no-slug
           title: T
           added: 2026-01-01
           status: drafting
         """, "requires a `slug`"),
        # drafting pointing at a nonexistent post
        ("""
         - id: ghost
           title: T
           added: 2026-01-01
           status: drafting
           slug: definitely-not-a-real-post
         """, "does not exist"),
        # idea carrying a slug
        ("""
         - id: slugged
           title: T
           added: 2026-01-01
           status: idea
           slug: how-this-site-builds-itself
         """, "must not carry a `slug`"),
        # em-dash in a rendered field
        ("""
         - id: emdash
           title: "A title with an em dash — here"
           added: 2026-01-01
           status: idea
         """, "em-dash in `title`"),
    ],
)
def test_violation_fails(tmp_path, capsys, body, needle):
    p = write_ledger(tmp_path, body)
    assert lint_ideas.run(p) == 1
    assert needle in capsys.readouterr().err


def test_two_rows_cannot_claim_one_post(tmp_path, capsys):
    p = write_ledger(tmp_path, """
        - id: first
          title: First
          added: 2026-01-01
          status: drafting
          slug: how-this-site-builds-itself
        - id: second
          title: Second
          added: 2026-01-01
          status: drafting
          slug: how-this-site-builds-itself
    """)
    assert lint_ideas.run(p) == 1
    assert "one post, one ledger row" in capsys.readouterr().err


def test_published_row_pointing_at_a_draft_fails(tmp_path, capsys):
    """The stage must match the post's actual draft flag, or `blog queue`
    would report an in-progress post as shipped."""
    p = write_ledger(tmp_path, """
        - id: claims-published
          title: Claims published
          added: 2026-01-01
          status: published
          slug: how-this-site-builds-itself
    """)
    assert lint_ideas.run(p) == 1
    assert "still `draft: true`" in capsys.readouterr().err


def test_malformed_yaml_fails(tmp_path, capsys):
    p = tmp_path / "blog-ideas.yaml"
    p.write_text("- id: x\n   bad indentation: [\n", encoding="utf-8")
    assert lint_ideas.run(p) == 1
    assert "could not be parsed" in capsys.readouterr().err


def test_non_list_document_fails(tmp_path, capsys):
    p = tmp_path / "blog-ideas.yaml"
    p.write_text("ideas:\n  - id: x\n", encoding="utf-8")
    assert lint_ideas.run(p) == 1
    assert "must be a list" in capsys.readouterr().err


# ── the informational direction ────────────────────────────────────────────


def test_orphan_draft_reports_but_does_not_fail(tmp_path, capsys, monkeypatch):
    """A draft post with no ledger row is reported, never fatal.

    Non-failing on purpose: the published historical posts predate the ledger,
    and the check is scoped to `draft: true` so only funnel-relevant posts
    surface. Same split as lint_recognition's coverage report.
    """
    posts = tmp_path / "blog"
    posts.mkdir()
    (posts / "unregistered.md").write_text(
        "---\ntitle: Loose\ndraft: true\n---\n\nbody\n", encoding="utf-8"
    )
    (posts / "already-live.md").write_text(
        "---\ntitle: Live\ndraft: false\n---\n\nbody\n", encoding="utf-8"
    )
    monkeypatch.setattr(_ideas, "POSTS_DIR", posts)

    p = write_ledger(tmp_path, """
        - id: some-idea
          title: Some idea
          added: 2026-01-01
          status: idea
    """)
    assert lint_ideas.run(p) == 0
    out = capsys.readouterr().out
    assert "unregistered" in out
    # A published post without a row is NOT an orphan.
    assert "already-live" not in out
