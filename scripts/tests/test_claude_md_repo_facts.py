"""Layer 2 -- CLAUDE.md §Thalia "Repo facts" drift.

The Repo facts block restates two things that live elsewhere: a verbatim
frontmatter paste from one named post, and the set of frontmatter keys the
tooling understands. Both are hand-maintained second copies, and this repo
has learned twice that a hand-maintained copy drifts silently (the homepage
writing list before build_portfolio.py, the Education/Service Gantt before
lint_gantt.py). This module is that alarm, for the one surface a fresh
session reads first and trusts most.

It caught its own premise on the way in: `homepageSelected` had been live
in build_portfolio.select_writing() and named nowhere in CLAUDE.md.

Deliberately NOT checked: whether the pasted post is the MOST RECENT
published post. The block is a dated snapshot whose job is to show the
SHAPE of a post's frontmatter, and a shape does not go stale the moment a
newer post appears. Asserting freshness would also turn main red on every
publication, since `blog publish` pushes straight to main and tests.yml
runs on that push. What has to stay true is narrower: the paste is a
truthful copy of a real published post (tests 1 and 2), and the documented
key set is still complete (test 3).

Drafts are scanned along with published posts in test 3 on purpose. A key
introduced in a draft reaches main the moment that draft is published, and
by then the failure lands on main rather than on a branch. Genuine
frontmatter experiments belong under the `_` filename prefix, which every
tool in this repo already ignores.
"""

from __future__ import annotations

import re
from pathlib import Path

import frontmatter
import pytest

from _common import iter_post_paths

SECTION_HEADING = "## Thalia (blog muse and editor)"

# The fenced block, at whatever indentation the surrounding list gives it.
_FENCE_RE = re.compile(r"^([ \t]*)```yaml\n(.*?)^\1```[ \t]*$", re.M | re.S)

# A named post file: `src/content/blog/<slug>.md`. The glob form used
# elsewhere in the section (`src/content/blog/*.md`) cannot match, since `*`
# is outside the character class.
_SOURCE_RE = re.compile(r"`(src/content/blog/[A-Za-z0-9._-]+\.md)`")

# A backticked bare identifier in prose, e.g. `homepageSelected`. Anything
# carrying a slash, colon, or space fails to match, so paths and code
# fragments do not count as documenting a key.
_BACKTICK_TOKEN_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")


def _section(repo_root: Path) -> str:
    """Return §Thalia's text, from its heading to the next top-level one."""
    text = (repo_root / "CLAUDE.md").read_text(encoding="utf-8")
    start = text.find(SECTION_HEADING)
    assert start != -1, f"CLAUDE.md no longer has a {SECTION_HEADING!r} section"
    rest = text[start + len(SECTION_HEADING) :]
    nxt = re.search(r"^## ", rest, flags=re.M)
    return rest[: nxt.start()] if nxt else rest


def _pasted_block(section: str) -> str:
    """Return the fenced frontmatter paste, dedented to column zero."""
    m = _FENCE_RE.search(section)
    assert m, "§Repo facts no longer contains a ```yaml frontmatter block"
    indent, body = m.group(1), m.group(2)
    lines = [ln[len(indent) :] if ln.startswith(indent) else ln for ln in body.splitlines()]
    return "".join(ln + "\n" for ln in lines)


def _named_source(repo_root: Path, section: str) -> Path:
    """Return the post the paste says it came from.

    Takes the last match before the fence, so the reference adjacent to the
    block wins over any earlier mention in the section.
    """
    m = _FENCE_RE.search(section)
    assert m, "§Repo facts no longer contains a ```yaml frontmatter block"
    matches = _SOURCE_RE.findall(section[: m.start()])
    assert matches, "§Repo facts does not name the post its paste came from"
    return repo_root / matches[-1]


def _raw_frontmatter(path: Path) -> str:
    """Return a post's frontmatter block verbatim, delimiters included."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    assert lines and lines[0].strip() == "---", f"{path.name} does not open with ---"
    out = [lines[0]]
    for line in lines[1:]:
        out.append(line)
        if line.strip() == "---":
            return "".join(out)
    raise AssertionError(f"{path.name} has an unterminated frontmatter block")


@pytest.fixture
def section(repo_root: Path) -> str:
    return _section(repo_root)


def test_pasted_frontmatter_matches_its_source(repo_root: Path, section: str):
    """The paste is byte-identical to the frontmatter it claims to quote."""
    source = _named_source(repo_root, section)
    assert source.is_file(), f"§Repo facts names {source.name}, which does not exist"

    pasted = _pasted_block(section)
    actual = _raw_frontmatter(source)
    assert pasted == actual, (
        f"CLAUDE.md §Repo facts quotes {source.name} verbatim, and the two have "
        f"drifted. Re-copy the frontmatter block from the post, or point the "
        f"section at a different post.\n\n"
        f"--- CLAUDE.md ---\n{pasted}\n--- {source.name} ---\n{actual}"
    )


def test_source_post_is_still_published(repo_root: Path, section: str):
    """The quoted post is still a real, published, buildable post.

    A rename, a deletion, or a flip back to `draft: true` would leave the
    section illustrating the schema with something no reader can look up.
    """
    source = _named_source(repo_root, section)
    posts_dir = repo_root / "src" / "content" / "blog"
    buildable = set(iter_post_paths(posts_dir))
    assert source in buildable, (
        f"§Repo facts quotes {source.name}, which is no longer a buildable post "
        f"(renamed, deleted, or `_`-prefixed)."
    )
    assert not frontmatter.load(source).metadata.get("draft", False), (
        f"§Repo facts quotes {source.name} as its published-post example, but "
        f"that post is now a draft."
    )


def test_every_frontmatter_key_in_use_is_documented(repo_root: Path, section: str):
    """Every key any post actually uses is named in §Repo facts.

    Required keys are covered for free by the verbatim paste; optional ones
    have to be named in the prose. This is the check that fires when a post
    introduces a key the section never mentions.
    """
    documented = set(frontmatter.loads(_pasted_block(section)).metadata)
    documented |= set(_BACKTICK_TOKEN_RE.findall(section))

    posts_dir = repo_root / "src" / "content" / "blog"
    undocumented: dict[str, list[str]] = {}
    for path in iter_post_paths(posts_dir):
        for key in frontmatter.load(path).metadata:
            if key not in documented:
                undocumented.setdefault(key, []).append(path.name)

    assert not undocumented, (
        "Frontmatter keys are in use that CLAUDE.md §Repo facts does not name: "
        + "; ".join(
            f"{key} ({len(files)} post{'s' if len(files) != 1 else ''}, e.g. {files[0]})"
            for key, files in sorted(undocumented.items())
        )
        + ". Document the key in §Repo facts, or drop it from the posts."
    )
