"""Layer 2 -- lint_links check functions.

The four checks (fragment anchors, inbound /#... anchors from other pages,
/blog/ hrefs, sitemap <loc>s) are pure functions over text and a root path,
so violation cases are fed synthetic HTML/XML and tmp_path trees directly.
The pass case against the real repo lives in test_baseline_clean.py alongside
the other gate linters.
"""

from __future__ import annotations

import lint_links


def check_inbound(root, index_html):
    """check_inbound_anchors with the argument order the tests read best."""
    return lint_links.check_inbound_anchors(root, index_html)


# ── anchors ─────────────────────────────────────────────────────────────────


def test_resolving_anchor_is_clean():
    html = '<a href="#about">About</a>\n<section id="about"></section>\n'
    checked, failures = lint_links.check_anchors(html)
    assert checked == 1
    assert failures == []


def test_missing_anchor_flagged():
    html = '<a href="#nope">dead</a>\n<section id="about"></section>\n'
    _, failures = lint_links.check_anchors(html)
    assert len(failures) == 1
    assert '#nope' in failures[0]


def test_id_inside_comment_does_not_satisfy_anchor():
    html = '<a href="#ghost">x</a>\n<!-- <div id="ghost"> -->\n'
    _, failures = lint_links.check_anchors(html)
    assert len(failures) == 1


def test_id_inside_style_does_not_satisfy_anchor():
    html = '<a href="#ghost">x</a>\n<style>/* id="ghost" */</style>\n'
    _, failures = lint_links.check_anchors(html)
    assert len(failures) == 1


def test_href_inside_comment_is_not_checked():
    html = '<!-- <a href="#gone">x</a> -->\n<p>no live links</p>\n'
    checked, failures = lint_links.check_anchors(html)
    assert checked == 0
    assert failures == []


def test_data_sid_attribute_is_not_an_id():
    html = '<a href="#PMID:123">x</a>\n<div data-sid="PMID:123"></div>\n'
    _, failures = lint_links.check_anchors(html)
    assert len(failures) == 1


def test_failure_reports_line_number():
    html = 'line one\nline two\n<a href="#nope">x</a>\n'
    _, failures = lint_links.check_anchors(html, rel="index.html")
    assert failures[0].startswith("index.html:3:")


# ── inbound /#... anchors from other pages ──────────────────────────────────
# The regression these exist for: ~250 generated blog pages carried
# /#education and /#service in their nav while those homepage sections were
# commented out and then deleted, and no gate could see it.


def _page(root, rel, body):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_inbound_anchor_resolving_is_clean(tmp_path):
    _page(tmp_path, "blog/post/index.html", '<a href="/#about">About</a>')
    pages, checked, failures = check_inbound(tmp_path, '<section id="about">')
    assert (pages, checked, failures) == (1, 1, [])


def test_inbound_anchor_to_missing_homepage_id_flagged(tmp_path):
    _page(tmp_path, "blog/post/index.html", '<a href="/#service">Service</a>')
    _, _, failures = check_inbound(tmp_path, '<section id="about">')
    assert len(failures) == 1
    assert "/#service" in failures[0]
    assert "blog/post/index.html" in failures[0]


def test_blog_template_is_checked(tmp_path):
    """The template is linted alongside the output, so a bad fragment fails on
    the commit that introduces it, not on the CI run that propagates it."""
    _page(tmp_path, lint_links.BLOG_TEMPLATE, '<a href="/#gone">x</a>')
    _, _, failures = check_inbound(tmp_path, '<section id="about">')
    assert len(failures) == 1
    assert lint_links.BLOG_TEMPLATE in failures[0]


def test_same_page_fragment_is_not_checked_against_homepage(tmp_path):
    """`href="#x"` on another page points at that page's OWN id. Only the
    root-relative `/#x` form is a link into the homepage."""
    _page(tmp_path, "colophon/index.html",
          '<a href="#local">x</a><h2 id="local">local</h2>')
    _, checked, failures = check_inbound(tmp_path, "<section id='about'>")
    assert checked == 0
    assert failures == []


def test_index_html_itself_is_not_double_checked(tmp_path):
    """check_anchors already owns index.html; counting it here too would
    report every homepage anchor twice."""
    _page(tmp_path, "index.html", '<a href="/#about">x</a>')
    pages, checked, _ = check_inbound(tmp_path, '<section id="about">')
    assert (pages, checked) == (0, 0)


def test_build_input_directories_are_skipped(tmp_path):
    """src/ holds post markdown and docs/ holds prose about the site; neither
    ships, so a fragment quoted there is not a live link."""
    _page(tmp_path, "docs/notes.html", '<a href="/#gone">x</a>')
    _page(tmp_path, "src/content/draft.html", '<a href="/#gone">x</a>')
    pages, _, failures = check_inbound(tmp_path, '<section id="about">')
    assert (pages, failures) == (0, [])


def test_inbound_href_inside_comment_is_not_checked(tmp_path):
    _page(tmp_path, "blog/post/index.html", '<!-- <a href="/#gone">x</a> -->')
    _, checked, failures = check_inbound(tmp_path, '<section id="about">')
    assert checked == 0
    assert failures == []


def test_inbound_anchor_against_commented_homepage_id_flagged(tmp_path):
    """An id that survives only inside an HTML comment is not a jump target,
    so it must not satisfy an inbound link either. This is the exact shape of
    the 2026-07-30 state: the sections were commented out, the ids went with
    them, and the blog nav still pointed at them."""
    _page(tmp_path, "blog/post/index.html", '<a href="/#service">x</a>')
    _, _, failures = check_inbound(tmp_path, '<!-- <section id="service"> -->')
    assert len(failures) == 1


# ── /blog/ hrefs ────────────────────────────────────────────────────────────


def test_blog_dir_link_resolves(tmp_path):
    (tmp_path / "blog" / "post").mkdir(parents=True)
    (tmp_path / "blog" / "post" / "index.html").write_text("x")
    html = '<a href="/blog/post/">post</a>\n'
    checked, failures = lint_links.check_blog_links(html, tmp_path)
    assert checked == 1
    assert failures == []


def test_blog_dir_link_to_unbuilt_post_flagged(tmp_path):
    (tmp_path / "blog").mkdir()
    html = '<a href="/blog/never-drafted/">x</a>\n'
    _, failures = lint_links.check_blog_links(html, tmp_path)
    assert len(failures) == 1
    assert "/blog/never-drafted/" in failures[0]


def test_blog_file_link_resolves(tmp_path):
    (tmp_path / "blog").mkdir()
    (tmp_path / "blog" / "feed.xml").write_text("<feed/>")
    html = '<a href="/blog/feed.xml">feed</a>\n'
    _, failures = lint_links.check_blog_links(html, tmp_path)
    assert failures == []


def test_blog_link_fragment_suffix_checks_the_path(tmp_path):
    (tmp_path / "blog" / "post").mkdir(parents=True)
    (tmp_path / "blog" / "post" / "index.html").write_text("x")
    html = '<a href="/blog/post/#section">x</a>\n'
    checked, failures = lint_links.check_blog_links(html, tmp_path)
    assert checked == 1
    assert failures == []


def test_non_blog_root_links_are_ignored(tmp_path):
    # /medicare-advantage-insight-engine/ is served by a separate repo
    # (CLAUDE.md §Links); the check is scoped to /blog/ so it must not look.
    html = '<a href="/medicare-advantage-insight-engine/">x</a>\n'
    checked, failures = lint_links.check_blog_links(html, tmp_path)
    assert checked == 0
    assert failures == []


# ── sitemap <loc>s ──────────────────────────────────────────────────────────


def test_sitemap_loc_resolves(tmp_path):
    (tmp_path / "index.html").write_text("x")
    (tmp_path / "blog" / "post").mkdir(parents=True)
    (tmp_path / "blog" / "post" / "index.html").write_text("x")
    xml = (
        "<urlset>"
        "<url><loc>https://example.com/</loc></url>"
        "<url><loc>https://example.com/blog/post/</loc></url>"
        "</urlset>"
    )
    checked, failures = lint_links.check_sitemap(xml, tmp_path)
    assert checked == 2
    assert failures == []


def test_sitemap_loc_missing_file_flagged(tmp_path):
    xml = "<urlset><url><loc>https://example.com/gone/</loc></url></urlset>"
    _, failures = lint_links.check_sitemap(xml, tmp_path)
    assert len(failures) == 1
    assert "https://example.com/gone/" in failures[0]


def test_sitemap_plain_file_loc_resolves(tmp_path):
    (tmp_path / "resume.html").write_text("x")
    xml = "<urlset><url><loc>https://example.com/resume.html</loc></url></urlset>"
    _, failures = lint_links.check_sitemap(xml, tmp_path)
    assert failures == []
