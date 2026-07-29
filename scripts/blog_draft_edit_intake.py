#!/usr/bin/env python3
"""blog_draft_edit_intake.py — apply a phone-submitted draft edit.

The mobile draft-edit path, one stage past blog_ideas_intake.py's capture
step. .github/ISSUE_TEMPLATE/blog-draft-edit.yml renders a native form in the
GitHub mobile app; submitting it opens an issue labelled `blog-draft-edit`;
.github/workflows/blog-draft-edit-intake.yml runs this script to replace the
draft's body (plus any requested frontmatter overrides), optionally publish
it, then commits and closes the issue. This is the phone equivalent of
`blog edit <slug>` followed by `blog publish <slug>`.

Reads from the environment (the workflow passes the issue through untouched):

    ISSUE_NUMBER   the issue number; used only in the workflow's commit message
    ISSUE_BODY     the rendered issue-form body

Prints, on success, exactly three `key=value` lines to stdout for the
workflow to capture (`slug=`, `title=`, `published=`); prints nothing to
stdout on failure. Failures go to stderr as `::error::`-prefixed lines and
the process exits 1 before anything is written to disk.

This script never touches a post that is already published (draft: false) —
that is the CLI's job (`blog edit` at a terminal), not this pipeline's — with
one narrow exception: a templated issue fires BOTH `opened` and `labeled` at
creation (the template applies its own label), so every submission runs this
script twice. If the second run finds the post already published with
content identical to what it would itself produce, that's the harmless
duplicate fire, not a hostile retry, and it exits 0 without writing anything.
Any other post-already-published case (a different actual publish landed in
between, or this pipeline is being pointed at a live post with new content)
is refused loudly.

Does NOT strip em-dashes from the submitted body or frontmatter overrides.
CLAUDE.md's em-dash policy exempts blog post sources (unlike the idea
ledger and homepage chrome, which blog_ideas_intake.strip_em_dashes and
build_portfolio.py sweep) so historical voice is preserved. Do not "fix"
this into consistency with that stripping.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml

import _ideas
from _ideas import _post_is_draft, flip_draft_false, ledger_set_status, post_path
from _issue_forms import parse_issue_form
from lint_blog import check_post as lint_blog_check_post
from lint_vocab import (
    check_text as lint_vocab_check_text,
    post_exemptions as lint_vocab_post_exemptions,
)

# Form field labels -> intake fields. Matching is case-insensitive, same
# convention as blog_ideas_intake.SECTION_ALIASES.
SECTION_ALIASES = {
    "draft slug": "slug",
    "new body (markdown)": "body",
    "title override (optional)": "title",
    "description override (optional)": "description",
    "tags override (optional)": "tags",
    "publish": "publish",
}

SLUG_RE = re.compile(r"^[a-z0-9-]+$")
# Splits a file's leading `---`/`---` block from its body. maxsplit=2 means
# only the first two delimiter LINES are treated as frontmatter boundaries;
# a later `---` horizontal rule in body prose is left untouched in parts[2].
FRONTMATTER_SPLIT_RE = re.compile(r"(?m)^---\s*$")
CHECKED_RE = re.compile(r"-\s*\[[xX]\]")


def resolve_draft(slug: str) -> Path:
    """Resolve `slug` to an existing post file. Exact match only.

    Unlike scripts/blog's find_post_with_provenance, there is no fuzzy
    fragment matching: that command has an interactive confirm step before
    acting on a fuzzy match, and an unattended workflow has no equivalent of
    "confirm". A slug either names an existing post exactly, or this raises
    ValueError and nothing is read or written beyond this check.

    Deliberately does NOT check the draft flag here — main() does, because
    the correct handling (refuse vs. tolerate-if-identical) depends on the
    computed replacement text, not just the file's current state.

    The containment check is defense in depth, not the primary guard: the
    `SLUG_RE` shape check above already rules out `/` and `.` entirely, so
    `POSTS_DIR / f"{slug}.md"` cannot resolve outside POSTS_DIR by
    construction. Kept anyway, matching the belt-and-suspenders pattern
    scripts/blog's own path-handling already uses elsewhere in this repo.
    Reads `_ideas.POSTS_DIR` (module attribute, not a re-imported name) so
    a test can monkeypatch a single point and have both this check and
    `post_path()` agree on the same directory.
    """
    if not SLUG_RE.match(slug):
        raise ValueError(f"{slug!r} is not a valid slug (expected [a-z0-9-]+)")
    path = post_path(slug)
    if not path.resolve().is_relative_to(_ideas.POSTS_DIR.resolve()):
        raise ValueError("slug resolves outside src/content/blog/")
    if not path.exists():
        raise ValueError(
            f"no post at src/content/blog/{slug}.md — check the slug for typos"
        )
    return path


def split_frontmatter(text: str) -> tuple[str, str]:
    """Split `text` into (frontmatter block incl. --- delimiters, body).

    Raises ValueError if the file doesn't open with a --- block.
    """
    parts = FRONTMATTER_SPLIT_RE.split(text, maxsplit=2)
    if len(parts) < 3 or parts[0].strip():
        raise ValueError("post does not open with a --- frontmatter block")
    return f"---{parts[1]}---", parts[2]


def _frontmatter_title(frontmatter_block: str) -> str:
    """Read `title:` out of a block via real YAML parsing (not a regex),
    so a title containing a colon or quotes is reported correctly.

    yaml.safe_load errors on a stream with two `---` document markers, so
    the delimiter lines are stripped first; the interior may still contain
    `# homepageMarginnote: ...` / `# vocab_exempt: []` hint comments (see
    scripts/blog's build_frontmatter_block) — those parse as ordinary YAML
    comments and are ignored.
    """
    lines = frontmatter_block.splitlines()
    inner = "\n".join(lines[1:-1])
    data = yaml.safe_load(inner) or {}
    return str(data.get("title", ""))


def override_scalar(frontmatter_block: str, field: str, value: str) -> str:
    """Replace the `field: ...` line inside `frontmatter_block` only.

    Scoped to the frontmatter block, not the whole file (unlike _ideas.py's
    flip_draft_false/flip_draft_true, which rely on "first match in the
    whole file" being safe for a fixed boolean line). `value` here is
    arbitrary phone-submitted text that could itself contain a line
    starting with e.g. `title:` — a code sample showing frontmatter syntax
    is exactly the kind of thing this site's own meta posts contain — so
    isolating the frontmatter block first designs that risk out rather
    than relying on convention.

    Uses yaml.safe_dump for the replacement line so quoting/escaping of
    `"`, `:`, backslashes, and Unicode is handled the same way
    scripts/blog's build_frontmatter_block already trusts it.

    Raises ValueError if `field:` isn't found — a malformed post is a real
    problem to surface, not to silently skip.
    """
    line_re = re.compile(rf"^{re.escape(field)}:\s*.*$", re.MULTILINE)
    replacement = yaml.safe_dump(
        {field: value}, default_flow_style=False, allow_unicode=True
    ).rstrip("\n")
    new_block, n = line_re.subn(replacement, frontmatter_block, count=1)
    if n == 0:
        raise ValueError(f"no `{field}:` line found in frontmatter to override")
    return new_block


def override_tags(frontmatter_block: str, tags: list[str]) -> str:
    """Replace the `tags: [...]` flow-sequence line.

    Refuses (raises ValueError) if the tags line isn't already single-line
    flow style. No post in the repo uses block-style tags today, so this
    is a safety net against guessing at a rewrite, not a real limitation.
    """
    line_re = re.compile(r"^tags:\s*\[.*\]\s*$", re.MULTILINE)
    flow = yaml.safe_dump(tags, default_flow_style=True, allow_unicode=True).strip()
    replacement = f"tags: {flow}"
    new_block, n = line_re.subn(replacement, frontmatter_block, count=1)
    if n == 0:
        raise ValueError(
            "tags: line is not a single-line flow sequence; refusing to guess at a rewrite"
        )
    return new_block


def build_updated_post(
    original_text: str,
    *,
    new_body: str,
    title: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Return the post's full new text: original frontmatter (with any
    requested overrides applied) followed by the submitted body."""
    frontmatter_block, _old_body = split_frontmatter(original_text)
    if title is not None:
        frontmatter_block = override_scalar(frontmatter_block, "title", title)
    if description is not None:
        frontmatter_block = override_scalar(frontmatter_block, "description", description)
    if tags is not None:
        frontmatter_block = override_tags(frontmatter_block, tags)
    return f"{frontmatter_block}\n\n{new_body.strip()}\n"


def main() -> int:
    number = (os.environ.get("ISSUE_NUMBER") or "").strip()
    body = os.environ.get("ISSUE_BODY") or ""
    if not number:
        print("ISSUE_NUMBER is required", file=sys.stderr)
        return 2

    # known_labels is load-bearing here, not defensive polish: the "New body
    # (markdown)" field's value is a real post body, which routinely
    # contains its own `##`/`###` headings ("## TL;DR", "### The shape",
    # ...). Without restricting boundary recognition to the form's actual
    # labels, the first such heading inside the submitted body would be
    # misread as a new form field and silently truncate everything after it.
    sections = parse_issue_form(body, known_labels=set(SECTION_ALIASES))
    fields: dict[str, str] = {}
    for label, value in sections.items():
        key = SECTION_ALIASES.get(label)
        if key:
            fields[key] = value

    slug = fields.get("slug", "").strip()
    new_body = fields.get("body", "")
    publish_requested = bool(CHECKED_RE.search(sections.get("publish", "")))

    if not slug or not new_body:
        print("::error::slug and body are both required", file=sys.stderr)
        return 1

    try:
        path = resolve_draft(slug)
    except ValueError as e:
        print(f"::error::{e}", file=sys.stderr)
        return 1

    original_text = path.read_text(encoding="utf-8")
    was_draft = _post_is_draft(path)

    # Single-line fields only: title/description are `type: input` in the
    # issue form, but a pasted value could still carry an embedded newline,
    # which would make yaml.safe_dump emit a multi-line block scalar and
    # break override_scalar's single-line regex replace. Collapse defensively.
    title = fields.get("title", "").strip().replace("\n", " ") or None
    description = fields.get("description", "").strip().replace("\n", " ") or None
    tags_raw = fields.get("tags", "").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else None

    try:
        target_text = build_updated_post(
            original_text,
            new_body=new_body,
            title=title,
            description=description,
            tags=tags,
        )
    except ValueError as e:
        print(f"::error::{e}", file=sys.stderr)
        return 1

    if was_draft is not True:
        # Already draft: false (or missing the draft line entirely). Tolerate
        # this ONLY when it's an exact repeat of a request already applied —
        # see the module docstring's note on the guaranteed opened+labeled
        # double fire. Anything that would actually CHANGE an already-
        # published post is refused.
        if target_text == original_text:
            frontmatter_block, _ = split_frontmatter(original_text)
            reported_title = title if title is not None else _frontmatter_title(frontmatter_block)
            print(f"slug={slug}")
            print(f"title={reported_title}")
            print("published=true")
            return 0
        print(
            f"::error::{slug}.md is not draft: true (already published, or "
            f"missing the draft line) — this pipeline only edits drafts. "
            f"Use `blog edit {slug}` at a terminal for a published post.",
            file=sys.stderr,
        )
        return 1

    path.write_text(target_text, encoding="utf-8")

    if publish_requested:
        flip_draft_false(path)  # no-op-safe: already draft: true here

    # Scoped lint against the file's CURRENT on-disk state. Meaningful when
    # publish_requested (the post is now draft: false, so lint_blog.check_post
    # / lint_vocab.check_text actually inspect it); a documented no-op
    # otherwise, since both linters unconditionally skip draft: true posts
    # (existing behavior shared with `blog lint <slug>`, not a gap introduced
    # here — drafts render nowhere public regardless).
    final_text = path.read_text(encoding="utf-8")
    violations = lint_blog_check_post(path) + lint_vocab_check_text(
        path, final_text, fenced=True, exemptions=lint_vocab_post_exemptions(path)
    )
    if violations:
        print("::error::scoped lint failed:", file=sys.stderr)
        for v in violations:
            print(f"::error::  {v}", file=sys.stderr)
        return 1

    if publish_requested:
        ledger_set_status(slug, "published")

    frontmatter_block, _ = split_frontmatter(final_text)
    real_title = title if title is not None else _frontmatter_title(frontmatter_block)
    print(f"slug={slug}")
    print(f"title={real_title}")
    print(f"published={'true' if publish_requested else 'false'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
