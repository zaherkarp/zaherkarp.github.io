"""Layer 2 -- `blog preview` renders through the real template environment.

`scripts/blog preview` is the only way to see a DRAFT, since drafts are
excluded from the build by design, and it had been broken for every post on
the site: it built its own Jinja environment mirroring build_blog's, that
copy never grew the `tag_slug` filter when post.html started using it, and
`tags` is present in all 74 posts, so every preview raised "No filter named
'tag_slug'". Nothing caught it because the CLI had no test at all.

The structural fix is a shared `build_blog.make_jinja_env()`. These tests
hold both halves down: the CLI must render a real draft end to end, and the
environment must satisfy every filter the templates actually use, so the
next filter added to a template cannot reintroduce this by a different door.
"""

from __future__ import annotations

import importlib.util
import re
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

import build_blog

# `scripts/blog` is an extension-less executable, so it cannot be imported by
# name, and spec_from_file_location cannot infer a loader for it either.
_BLOG_CLI_PATH = Path(build_blog.__file__).resolve().parent / "blog"

# Jinja expression and statement regions. The filter scan is scoped to these
# on purpose: base.html carries JavaScript with `(a.textContent || a.href)`,
# and an unscoped pipe search reads that `|| a` as a filter named `a`.
_JINJA_REGION_RE = re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.S)

# `x | filtername` / `x|filtername` inside such a region.
_TEMPLATE_FILTER_RE = re.compile(r"\|\s*([a-zA-Z_][a-zA-Z0-9_]*)")

# Filters Jinja ships with, which need no registration. Only the ones the
# templates in this repo actually reach for.
_JINJA_BUILTINS = {
    "e", "escape", "safe", "trim", "striptags", "join", "length", "list",
    "lower", "upper", "title", "capitalize", "default", "first", "last",
    "int", "float", "string", "replace", "sort", "reverse", "map",
    "select", "reject", "selectattr", "rejectattr", "attr", "batch",
    "slice", "truncate", "urlencode", "tojson", "round", "abs", "wordcount",
    "indent", "center", "format", "groupby", "unique", "min", "max", "sum",
}


@pytest.fixture(scope="module")
def blog_cli():
    """Import scripts/blog as a module.

    conftest has already replaced `_common.install_git_hooks` with a no-op,
    so the import-time hook installation does not fire and git config is not
    mutated.
    """
    loader = SourceFileLoader("blog_cli", str(_BLOG_CLI_PATH))
    spec = importlib.util.spec_from_loader("blog_cli", loader)
    assert spec and spec.loader, f"cannot load {_BLOG_CLI_PATH}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _a_draft(repo_root: Path) -> Path:
    """Return some draft post, or skip if the repo currently has none."""
    import frontmatter

    from _common import iter_post_paths

    for path in iter_post_paths(repo_root / "src" / "content" / "blog"):
        if frontmatter.load(path).metadata.get("draft", False):
            return path
    pytest.skip("no draft posts in the repo to preview")


def test_preview_renders_a_draft(blog_cli, repo_root: Path, tmp_path):
    """A real draft renders to HTML, which is what the bug prevented."""
    draft = _a_draft(repo_root)
    before = draft.read_bytes()

    out = blog_cli.render_post_to_tempfile(draft)

    assert out.is_file(), f"preview produced no file for {draft.name}"
    html = out.read_text(encoding="utf-8")
    assert "<title>" in html and "</html>" in html, "preview output is not a page"
    assert draft.read_bytes() == before, (
        f"preview mutated {draft.name}; it is documented as side-effect-free"
    )


def test_preview_renders_tag_links(blog_cli, repo_root: Path):
    """The tag_slug filter resolves, rather than raising at render time.

    This is the regression itself: post.html builds /blog/tags/<slug>/ hrefs
    through `tag_slug`, and an environment missing it fails the whole render.
    """
    import frontmatter

    from _common import iter_post_paths, slugify_tag

    tagged = next(
        (
            p
            for p in iter_post_paths(repo_root / "src" / "content" / "blog")
            if frontmatter.load(p).metadata.get("draft", False)
            and frontmatter.load(p).metadata.get("tags")
        ),
        None,
    )
    if tagged is None:
        pytest.skip("no tagged draft to render")

    html = blog_cli.render_post_to_tempfile(tagged).read_text(encoding="utf-8")
    for tag in frontmatter.load(tagged).metadata["tags"]:
        # Two shapes are both correct here. Preview rewrites absolute paths to
        # file:// URIs when the target exists in the repo, so a tag whose page
        # has been built renders as file:///.../blog/tags/<slug> while one
        # whose page has not renders as /blog/tags/<slug>/. Either proves the
        # filter resolved, which is what this guards; matching the bare middle
        # accepts both without pinning preview's asset-rewrite behavior.
        assert f"blog/tags/{slugify_tag(tag)}" in html, (
            f"{tagged.name}: tag {tag!r} did not render its slugged href"
        )


def test_env_registers_every_filter_the_templates_use():
    """No template reaches for a filter the shared environment lacks.

    Catches the next tag_slug: a filter added to a template but never
    registered, which fails only at render time and only for posts that hit
    that branch.
    """
    env = build_blog.make_jinja_env()
    available = set(env.filters) | _JINJA_BUILTINS

    missing: dict[str, set[str]] = {}
    for template in sorted(Path(build_blog.TEMPLATES_DIR).rglob("*.html")):
        text = template.read_text(encoding="utf-8")
        used: set[str] = set()
        for region in _JINJA_REGION_RE.findall(text):
            used.update(_TEMPLATE_FILTER_RE.findall(region))
        unknown = used - available
        if unknown:
            missing[template.name] = unknown

    assert not missing, (
        "templates use filters the shared Jinja environment does not register: "
        + "; ".join(f"{name} -> {sorted(f)}" for name, f in sorted(missing.items()))
        + ". Register them in build_blog.make_jinja_env()."
    )
