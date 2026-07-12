"""Layer 2 -- lint_links check functions.

The three checks (fragment anchors, /blog/ hrefs, sitemap <loc>s) are pure
functions over text and a root path, so violation cases are fed synthetic
HTML/XML and tmp_path trees directly. The pass case against the real repo
lives in test_baseline_clean.py alongside the other gate linters.
"""

from __future__ import annotations

import lint_links


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
