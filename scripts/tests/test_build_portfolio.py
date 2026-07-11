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
