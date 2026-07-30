"""blog_draft_edit_intake -- mobile draft-edit / publish intake.

Higher blast radius than blog_ideas_intake (it can flip a post live), so
unlike that script this one gets dedicated coverage: slug resolution
refusals, the frontmatter-override regex helpers (including the em-dash
and comment-preservation guarantees CLAUDE.md documents), and the main()
integration paths -- edit-only, publish, the bad-slug refusal, the
already-published refusal, and the duplicate-fire idempotency carve-out.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

import _ideas
import blog_draft_edit_intake as intake

FM = textwrap.dedent(
    """\
    ---
    title: "Original Title"
    description: "Original description."
    publishDate: 2026-01-01
    tags: ["a", "b"]
    draft: true
    # homepageMarginnote: "A note that must survive edits untouched."
    # vocab_exempt: []
    ---

    Original body.
    """
)


@pytest.fixture
def posts_dir(tmp_path, monkeypatch):
    posts = tmp_path / "blog"
    posts.mkdir()
    monkeypatch.setattr(_ideas, "POSTS_DIR", posts)
    return posts


@pytest.fixture
def ideas_path(tmp_path, monkeypatch):
    path = tmp_path / "blog-ideas.yaml"
    monkeypatch.setattr(_ideas, "IDEAS_PATH", path)
    return path


def write_post(posts_dir: Path, slug: str, text: str = FM) -> Path:
    p = posts_dir / f"{slug}.md"
    p.write_text(text, encoding="utf-8")
    return p


def write_ledger(ideas_path: Path, slug: str, status: str = "drafting") -> None:
    ideas_path.write_text(
        textwrap.dedent(
            f"""\
            - id: {slug}
              title: Original Title
              added: 2026-01-01
              status: {status}
              slug: {slug}
            """
        ),
        encoding="utf-8",
    )


# ── resolve_draft ───────────────────────────────────────────────────────────


def test_resolve_draft_missing_slug_raises(posts_dir):
    with pytest.raises(ValueError, match="no post at"):
        intake.resolve_draft("does-not-exist")


@pytest.mark.parametrize("bad_slug", ["../resume", "Has Spaces", "UPPER", "a/b", "a.b", ""])
def test_resolve_draft_invalid_shape_raises(posts_dir, bad_slug):
    with pytest.raises(ValueError, match="not a valid slug"):
        intake.resolve_draft(bad_slug)


@pytest.mark.parametrize("draft_flag", ["true", "false"])
def test_resolve_draft_finds_existing_post_regardless_of_draft_state(posts_dir, draft_flag):
    """resolve_draft only resolves the path; main() decides what to do with
    an already-published post, not this function (see its docstring)."""
    text = FM.replace("draft: true", f"draft: {draft_flag}")
    write_post(posts_dir, "my-post", text)
    assert intake.resolve_draft("my-post") == posts_dir / "my-post.md"


# ── split_frontmatter / override_scalar / override_tags ────────────────────


def test_split_frontmatter_roundtrips():
    block, body = intake.split_frontmatter(FM)
    assert block.startswith("---\n") and block.endswith("---")
    assert "title:" in block
    assert body.strip() == "Original body."


def test_split_frontmatter_raises_without_leading_delimiter():
    with pytest.raises(ValueError, match="does not open with"):
        intake.split_frontmatter("no frontmatter here\n")


def test_override_scalar_replaces_value_with_quote_and_colon():
    block, _ = intake.split_frontmatter(FM)
    new_block = intake.override_scalar(block, "title", 'A "quoted": title')
    assert 'title:' in new_block
    assert "Original Title" not in new_block
    # round-trips through YAML correctly regardless of the exact quoting style
    import yaml

    data = yaml.safe_load("\n".join(new_block.splitlines()[1:-1]))
    assert data["title"] == 'A "quoted": title'


def test_override_scalar_preserves_em_dash():
    """CLAUDE.md's em-dash policy exempts blog post sources; a title
    containing an em-dash must survive an override untouched, unlike the
    idea ledger's strip_em_dashes."""
    block, _ = intake.split_frontmatter(FM)
    new_block = intake.override_scalar(block, "title", "A title — with an em dash")
    import yaml

    data = yaml.safe_load("\n".join(new_block.splitlines()[1:-1]))
    assert data["title"] == "A title — with an em dash"


def test_override_scalar_raises_on_missing_field():
    block, _ = intake.split_frontmatter(FM)
    with pytest.raises(ValueError, match="no `nonexistent:` line"):
        intake.override_scalar(block, "nonexistent", "value")


def test_override_tags_replaces_flow_sequence():
    block, _ = intake.split_frontmatter(FM)
    new_block = intake.override_tags(block, ["x", "y", "z"])
    assert '["x", "y", "z"]' in new_block or "[x, y, z]" in new_block
    assert '["a", "b"]' not in new_block


def test_override_tags_raises_on_non_flow_style():
    block_style = FM.replace('tags: ["a", "b"]', "tags:\n  - a\n  - b")
    block, _ = intake.split_frontmatter(block_style)
    with pytest.raises(ValueError, match="not a single-line flow sequence"):
        intake.override_tags(block, ["x"])


# ── build_updated_post ──────────────────────────────────────────────────────


def test_build_updated_post_preserves_homepage_marginnote_comment():
    result = intake.build_updated_post(FM, new_body="New body text.")
    assert '# homepageMarginnote: "A note that must survive edits untouched."' in result
    assert "# vocab_exempt: []" in result
    assert "New body text." in result
    assert "Original body." not in result


def test_build_updated_post_applies_all_overrides_together():
    result = intake.build_updated_post(
        FM,
        new_body="New body.",
        title="New Title",
        description="New description.",
        tags=["x", "y"],
    )
    frontmatter_block, body = intake.split_frontmatter(result)
    import yaml

    data = yaml.safe_load("\n".join(frontmatter_block.splitlines()[1:-1]))
    assert data["title"] == "New Title"
    assert data["description"] == "New description."
    assert data["tags"] == ["x", "y"]
    assert body.strip() == "New body."


# ── main(): integration paths ───────────────────────────────────────────────


def issue_body(slug: str, body: str, *, publish: bool = False, title: str = "") -> str:
    # Deliberately built flush-left (not textwrap.dedent'd): `body` can be a
    # multi-line string, and interpolating a multi-line value into an
    # indented triple-quoted template breaks textwrap.dedent's common-prefix
    # calculation (the substituted continuation lines carry no indentation,
    # dragging the computed common prefix to zero) -- a bug in a test helper
    # once, not worth reintroducing here.
    publish_line = "- [x] Publish this now" if publish else "- [ ] Publish this now"
    return (
        "### Draft slug\n\n"
        f"{slug}\n\n"
        "### New body (markdown)\n\n"
        f"{body}\n\n"
        "### Title override (optional)\n\n"
        f"{title or '_No response_'}\n\n"
        "### Description override (optional)\n\n"
        "_No response_\n\n"
        "### Tags override (optional)\n\n"
        "_No response_\n\n"
        "### Publish\n\n"
        f"{publish_line}\n"
    )


def run_main(monkeypatch, capsys, *, number="1", body):
    monkeypatch.setenv("ISSUE_NUMBER", number)
    monkeypatch.setenv("ISSUE_BODY", body)
    code = intake.main()
    out = capsys.readouterr()
    return code, out.out, out.err


def test_main_edit_only_success(posts_dir, ideas_path, monkeypatch, capsys):
    write_post(posts_dir, "my-post")
    write_ledger(ideas_path, "my-post", status="drafting")

    code, out, err = run_main(
        monkeypatch, capsys, body=issue_body("my-post", "## TL;DR\n\n- edited")
    )

    assert code == 0, err
    assert "slug=my-post" in out
    assert "published=false" in out
    text = (posts_dir / "my-post.md").read_text(encoding="utf-8")
    assert "draft: true" in text
    assert "## TL;DR" in text
    ideas = _ideas.load_ideas()
    assert ideas[0]["status"] == "drafting"


def test_main_publish_flips_draft_and_ledger(posts_dir, ideas_path, monkeypatch, capsys):
    write_post(posts_dir, "my-post")
    write_ledger(ideas_path, "my-post", status="drafting")

    code, out, err = run_main(
        monkeypatch,
        capsys,
        body=issue_body("my-post", "## TL;DR\n\n- published", publish=True, title="New Title"),
    )

    assert code == 0, err
    assert "slug=my-post" in out
    assert "title=New Title" in out
    assert "published=true" in out
    text = (posts_dir / "my-post.md").read_text(encoding="utf-8")
    assert "draft: false" in text
    assert 'title: New Title' in text
    ideas = _ideas.load_ideas()
    assert ideas[0]["status"] == "published"


def test_main_body_containing_headings_is_not_misread_as_form_fields(posts_dir, ideas_path, monkeypatch, capsys):
    """Regression test: a submitted body with its own ## / ### headings
    must not be truncated by the shared issue-form parser."""
    write_post(posts_dir, "my-post")
    write_ledger(ideas_path, "my-post")
    body_with_headings = "## TL;DR\n\n- point one\n\n### A subsection\n\nMore prose after the subsection."

    code, out, err = run_main(
        monkeypatch, capsys, body=issue_body("my-post", body_with_headings)
    )

    assert code == 0, err
    text = (posts_dir / "my-post.md").read_text(encoding="utf-8")
    assert "More prose after the subsection." in text


def test_main_bad_slug_writes_nothing(posts_dir, ideas_path, monkeypatch, capsys):
    code, out, err = run_main(
        monkeypatch, capsys, body=issue_body("does-not-exist", "body")
    )
    assert code == 1
    assert out == ""
    assert "::error::" in err
    assert not list(posts_dir.glob("*.md"))


def test_main_refuses_different_content_on_already_published_post(posts_dir, ideas_path, monkeypatch, capsys):
    text = FM.replace("draft: true", "draft: false")
    write_post(posts_dir, "my-post", text)
    write_ledger(ideas_path, "my-post", status="published")

    code, out, err = run_main(
        monkeypatch, capsys, body=issue_body("my-post", "a totally different body")
    )

    assert code == 1
    assert out == ""
    assert "not draft: true" in err
    # nothing was rewritten
    assert (posts_dir / "my-post.md").read_text(encoding="utf-8") == text


def test_main_tolerates_duplicate_fire_on_already_published_identical_content(
    posts_dir, ideas_path, monkeypatch, capsys
):
    """The opened+labeled double fire, replayed against a post the FIRST run
    already published with identical content, must be a quiet success, not
    a refusal."""
    already_applied = intake.build_updated_post(FM, new_body="published body").replace(
        "draft: true", "draft: false"
    )
    write_post(posts_dir, "my-post", already_applied)
    write_ledger(ideas_path, "my-post", status="published")

    code, out, err = run_main(
        monkeypatch, capsys, body=issue_body("my-post", "published body", publish=True)
    )

    assert code == 0, err
    assert "slug=my-post" in out
    assert "published=true" in out
    # unchanged -- nothing was written
    assert (posts_dir / "my-post.md").read_text(encoding="utf-8") == already_applied
