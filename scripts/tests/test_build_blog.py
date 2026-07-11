"""Layer 3 -- build_blog smoke test.

Builds a couple of fixture posts into a tmp output tree (module ROOT /
POSTS_DIR / OUT_DIR monkeypatched; templates stay real) and asserts:
  - each blog/<slug>/index.html is produced,
  - sitemap.xml and feed.xml parse as well-formed XML,
  - no <p>-wrapped SVG children slipped into the output.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

import build_blog

CURRENT_1 = """---
title: "First Fixture Post"
description: "A first post used only by the test harness."
publishDate: 2026-01-15
tags: [data, testing]
---

A normal paragraph of prose.

<svg viewBox="0 0 10 10"><line x1="0" y1="0" x2="10" y2="10"/></svg>

Closing paragraph.
"""

CURRENT_2 = """---
title: "Second Fixture Post"
description: "Another harness post."
publishDate: 2026-02-20
tags: [data]
---

Second body paragraph.
"""

ARCHIVE_1 = """---
title: "Old Fixture Post"
description: "Archive-era harness post."
publishDate: 2010-05-01
tags: [interview]
---

An older body paragraph.
"""


@pytest.fixture
def built_site(monkeypatch, tmp_path):
    root = tmp_path
    posts_dir = root / "src" / "content" / "blog"
    out_dir = root / "blog"
    posts_dir.mkdir(parents=True)
    (posts_dir / "first-fixture-post.md").write_text(CURRENT_1, encoding="utf-8")
    (posts_dir / "second-fixture-post.md").write_text(CURRENT_2, encoding="utf-8")
    (posts_dir / "old-fixture-post.md").write_text(ARCHIVE_1, encoding="utf-8")

    monkeypatch.setattr(build_blog, "ROOT", root)
    monkeypatch.setattr(build_blog, "POSTS_DIR", posts_dir)
    monkeypatch.setattr(build_blog, "OUT_DIR", out_dir)

    rc = build_blog.main()
    assert rc == 0
    return root, out_dir


def test_post_pages_are_written(built_site):
    _, out_dir = built_site
    for slug in ("first-fixture-post", "second-fixture-post", "old-fixture-post"):
        assert (out_dir / slug / "index.html").is_file(), slug
    assert (out_dir / "index.html").is_file()
    assert (out_dir / "archive" / "index.html").is_file()


def test_sitemap_is_well_formed_xml(built_site):
    root, _ = built_site
    sitemap = root / "sitemap.xml"
    assert sitemap.is_file()
    tree = ET.parse(sitemap)  # raises on malformed XML
    assert tree.getroot().tag.endswith("urlset")


def test_feed_is_well_formed_xml(built_site):
    _, out_dir = built_site
    feed = out_dir / "feed.xml"
    assert feed.is_file()
    tree = ET.parse(feed)  # raises on malformed XML
    assert tree.getroot().tag == "rss"


def test_no_p_wrapped_svg_children(built_site):
    import re

    _, out_dir = built_site
    pat = re.compile(r"<p><(?:text|line|polyline|circle|rect|polygon)")
    offenders = [
        str(p) for p in out_dir.rglob("*.html") if pat.search(p.read_text(encoding="utf-8"))
    ]
    assert not offenders, offenders
