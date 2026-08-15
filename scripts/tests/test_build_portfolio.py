"""Layer 3 -- build_portfolio idempotency + graceful citation degradation.

Idempotency is the property a consolidation refactor must preserve: running
the marker injection twice against the same inputs yields byte-identical
output. The Semantic Scholar fetch is stubbed so no network call happens.

A second test exercises build_publications() directly with a monkeypatched
fetch that always fails, asserting the cached count is preserved (graceful
degradation) with no network and no real-file writes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import build_portfolio

POST_1 = """---
title: "Cadence Post One"
description: "First harness post."
publishDate: 2026-06-01
tags: [stars, python]
---

Body.
"""

POST_2 = """---
title: "Cadence Post Two"
description: "Second harness post."
publishDate: 2026-06-20
tags: [stars, sql]
---

Body.
"""

INDEX_FIXTURE = """<!doctype html><html><body>
<p>Intro chrome.</p>
<!-- activity-grid:start -->
<!-- activity-grid:end -->
<section id="writing">
<!-- writing-list:start -->
<!-- writing-list:end -->
<div class="writing-index">
<!-- writing-index:start -->
<!-- writing-index:end -->
</div>
</section>
<!-- pub-list:start -->
<!-- pub-list:end -->
<footer class="page-footer">
<!-- updated:start -->
<!-- updated:end -->
</footer>
</body></html>
"""

LIFE_FIXTURE = """<script>
const EVENTS = [
  // blog-thoughts:start
  // blog-thoughts:end
];
</script>
"""


@pytest.fixture
def portfolio_env(monkeypatch, tmp_path):
    posts_dir = tmp_path / "src" / "content" / "blog"
    posts_dir.mkdir(parents=True)
    (posts_dir / "cadence-post-one.md").write_text(POST_1, encoding="utf-8")
    (posts_dir / "cadence-post-two.md").write_text(POST_2, encoding="utf-8")

    index = tmp_path / "index.html"
    index.write_text(INDEX_FIXTURE, encoding="utf-8")
    life = tmp_path / "life-in-weeks" / "index.html"
    life.parent.mkdir(parents=True)
    life.write_text(LIFE_FIXTURE, encoding="utf-8")

    monkeypatch.setattr(build_portfolio, "POSTS_DIR", posts_dir)
    monkeypatch.setattr(build_portfolio, "INDEX", index)
    monkeypatch.setattr(build_portfolio, "LIFE_WEEKS", life)

    # No network: stub the publications step and make any raw fetch loud.
    monkeypatch.setattr(build_portfolio, "build_publications", lambda: ("<!-- pubs stub -->", 0, 0))

    def _no_network(*a, **k):
        raise AssertionError("fetch_citation_count must not be called in this test")

    monkeypatch.setattr(build_portfolio, "fetch_citation_count", _no_network)
    return index, life


def test_marker_injection_is_idempotent(portfolio_env):
    index, life = portfolio_env

    assert build_portfolio.main() == 0
    index_run1 = index.read_text(encoding="utf-8")
    life_run1 = life.read_text(encoding="utf-8")

    assert build_portfolio.main() == 0
    index_run2 = index.read_text(encoding="utf-8")
    life_run2 = life.read_text(encoding="utf-8")

    assert index_run1 == index_run2, "index.html second run differs from first"
    assert life_run1 == life_run2, "life-in-weeks second run differs from first"
    # Injection actually happened (markers still present, region populated).
    assert "activity-grid:start" in index_run1
    assert "blog-thoughts:start" in life_run1


def test_writing_list_suppresses_hero_marginnote():
    """Since the Timeline Split redesign the featured entries lead the split
    hero, which has no floating-note margin, so build_writing_list must NOT
    emit a per-post margin note even when homepageMarginnote is present."""
    import datetime

    posts = [
        {
            "date": datetime.date(2026, 7, 26),
            "title": "A Featured Post",
            "description": "Its blurb.",
            "slug": "a-featured-post",
            "marginnote": "This aside must never reach the hero.",
        }
    ]
    html = build_portfolio.build_writing_list(posts)
    assert "A Featured Post" in html
    assert "marginnote" not in html
    assert "mn-w-a-featured-post" not in html
    assert "This aside must never reach the hero." not in html


def _writing_post(day, slug, selected=False):
    import datetime

    return {
        "date": datetime.date(2026, 1, day),
        "title": f"Post {slug}",
        "description": "Blurb.",
        "slug": slug,
        "marginnote": "",
        "selected": selected,
    }


def test_select_writing_falls_back_to_recency_when_nothing_flagged():
    """With no homepageSelected anywhere, ordering must be exactly the
    reverse-chronological behavior that predated the flag. The fallback is the
    default path, not a special case."""
    posts = [_writing_post(1, "oldest"), _writing_post(9, "newest"), _writing_post(5, "middle")]
    assert [p["slug"] for p in build_portfolio.select_writing(posts)] == [
        "newest",
        "middle",
        "oldest",
    ]


def test_select_writing_promotes_flagged_posts_over_newer_unflagged():
    """The whole point of the flag: an older selected post outranks a newer
    unselected one, so publication date alone stops deciding what leads the
    page."""
    posts = [
        _writing_post(20, "recent-but-off-thesis"),
        _writing_post(2, "old-but-chosen", selected=True),
        _writing_post(15, "also-recent"),
    ]
    assert [p["slug"] for p in build_portfolio.select_writing(posts)] == [
        "old-but-chosen",
        "recent-but-off-thesis",
        "also-recent",
    ]


def test_select_writing_keeps_each_group_newest_first():
    """Both groups sort newest-first internally, so the rendered dated column
    never looks like a broken sort."""
    posts = [
        _writing_post(3, "sel-old", selected=True),
        _writing_post(8, "sel-new", selected=True),
        _writing_post(4, "plain-old"),
        _writing_post(9, "plain-new"),
    ]
    assert [p["slug"] for p in build_portfolio.select_writing(posts)] == [
        "sel-new",
        "sel-old",
        "plain-new",
        "plain-old",
    ]


def test_writing_tiers_do_not_overlap():
    """The two tiers are chosen by different orderings now, so the only thing
    stopping a flagged lead post from also filling a Recent slot is
    build_writing_index excluding the featured slugs. Pin that: every featured
    post is absent from the index, and every index post is absent from the
    featured pair."""
    posts = [_writing_post(28 - i, f"p{i}", selected=i < 4) for i in range(10)]
    featured_html = build_portfolio.build_writing_list(posts)
    index_html = build_portfolio.build_writing_index(posts)

    featured = [
        p["slug"]
        for p in build_portfolio.select_writing(posts)[: build_portfolio.WRITING_FEATURED]
    ]
    tiles = [
        p["slug"]
        for p in build_portfolio.select_recent(posts, set(featured))[
            : build_portfolio.WRITING_TILES
        ]
    ]
    assert not set(featured) & set(tiles)

    for slug in featured:
        assert f"/blog/{slug}/" in featured_html
        assert f"/blog/{slug}/" not in index_html
    for slug in tiles:
        assert f"/blog/{slug}/" in index_html
        assert f"/blog/{slug}/" not in featured_html


def test_writing_index_ignores_homepage_selected():
    """The regression this pipeline shipped: `homepageSelected` ordered the
    index too, so flagged posts filled every slot under a head that says
    "Recent" and newer unflagged posts never reached the page. A flagged post
    that is not one of the featured pair must rank purely on its date."""
    posts = [
        _writing_post(28, "lead-a", selected=True),
        _writing_post(27, "lead-b", selected=True),
        _writing_post(2, "old-but-flagged", selected=True),
        _writing_post(20, "newer-unflagged"),
    ]
    index_html = build_portfolio.build_writing_index(posts)
    assert index_html.index("/blog/newer-unflagged/") < index_html.index(
        "/blog/old-but-flagged/"
    )


def test_writing_index_is_strictly_newest_first():
    """The tiles render a visible date column, so the Recent tier must be in
    descending date order regardless of which posts carry the flag."""
    posts = [
        _writing_post(28, "lead-a", selected=True),
        _writing_post(27, "lead-b", selected=True),
        _writing_post(5, "third"),
        _writing_post(20, "first", selected=True),
        _writing_post(12, "second"),
    ]
    featured = {
        p["slug"]
        for p in build_portfolio.select_writing(posts)[: build_portfolio.WRITING_FEATURED]
    }
    assert [p["slug"] for p in build_portfolio.select_recent(posts, featured)] == [
        "first",
        "second",
        "third",
    ]


def test_activity_grid_suppresses_cadence_marginnote():
    """The cadence sparkline moved into the split hero on 2026-07-30, and the
    hero has no floating-note margin (.marginnote positions itself with
    margin-right: -60%, calibrated to the 60% prose column, so in the
    full-width hero it lands mid-page instead of beside its anchor). So
    build_activity_grid must emit the sparkline and its trailing total but no
    margin note and no toggle control. Same rule, same reason, as
    test_writing_list_suppresses_hero_marginnote above."""
    import datetime

    today = datetime.date.today()
    posts = [
        {
            "date": today - datetime.timedelta(days=7 * i),
            "title": f"Post {i}",
            "description": "blurb",
            "slug": f"post-{i}",
            "marginnote": "",
            "tags": ["data-engineering", "healthcare"],
            "lifeweek_topic": "",
        }
        for i in range(4)
    ]
    html = build_portfolio.build_activity_grid(posts)
    # the sparkline itself still renders, with its self-legending total
    assert 'class="cadence"' in html
    assert "posts</span>" in html
    # ...but nothing that needs a floating margin or a control
    assert "marginnote" not in html
    assert "mn-cadence" not in html
    assert "margin-toggle" not in html
    assert "<label" not in html
    assert "<input" not in html


def test_citation_fetch_failure_preserves_cached_count(monkeypatch):
    fake_pubs = [
        {
            "id": "demo",
            "sid": "PMID:99999",
            "citations": 42,
            "title": "A Cached Paper",
            "authors": "Karp Z",
            "venue": "Journal of Testing",
            "year": 2020,
            "toggle_aria": "toggle",
        }
    ]
    monkeypatch.setattr(build_portfolio, "load_publications", lambda: fake_pubs)
    monkeypatch.setattr(build_portfolio, "save_citation_counts", lambda pubs: None)
    monkeypatch.setattr(build_portfolio, "fetch_citation_count", lambda sid, retries=3: (None, "error"))

    html, successes, failures = build_portfolio.build_publications()
    assert successes == 0
    assert failures == 1
    # Cached count survives and is rendered.
    assert fake_pubs[0]["citations"] == 42
    assert "42 citations" in html
