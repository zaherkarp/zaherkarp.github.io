"""Layer 2 -- lint_gantt figure/CV alignment detection.

Builds an index.html fixture holding a gantt figure, plus a cv.md fixture.
The figure encodes years positionally via the chart transform
x(year) = GANTT_X0 + (year - GANTT_BASE_YEAR) * GANTT_PX_PER_YEAR, so each
mark's year is read back from its x-coordinate rather than from any text.

Those constants are IMPORTED, not restated. The chart was re-laid-out onto a
wider viewBox on 2026-08-15 and the hardcoded copies here would have gone
stale silently: a fixture built on the old transform still decodes to
consistent years among itself, so these tests would have kept passing while
testing a geometry the page no longer uses.

The gate direction flipped on 2026-08-13, when index.html's #education and
#service sections were deleted and cv.md became the record: every figure
MARK must now have a CV counterpart (figure subset of CV), where it used to
be every section entry needing a mark. The reverse direction is the
informational coverage report and never fails.

The comment-disabled fixtures that used to live here are gone with the
sections they mirrored.
"""

from __future__ import annotations

import lint_gantt
from _common import GANTT_BASE_YEAR as BASE
from _common import GANTT_PX_PER_YEAR as PX
from _common import GANTT_X0 as X0


def _square_x(year: int) -> int:
    # Parser reads the year from the square centre (x + 3), width 6.
    return X0 + (year - BASE) * PX - 3


def _bar_x(year: int) -> int:
    return X0 + (year - BASE) * PX


def _figure(include_service_mark: bool = True, service_year: int = 2021) -> str:
    # Education bar 2013-2015 in the education lane (above the divider).
    edu = (
        f'  <line x1="{_bar_x(2013)}" y1="30" x2="{_bar_x(2015)}" y2="30" '
        'stroke="#111" stroke-width="4"/>\n'
        '  <text x="322" y="34">Public Health MPH, Biostatistics</text>\n'
    )
    # Service square in the service lane (below the divider).
    svc = (
        f'  <rect x="{_square_x(service_year)}" y="160" width="6" height="6" '
        'fill="#111"/>\n'
        '  <text x="439" y="166">Spirit of Charlie Award</text>\n'
    )
    body = edu + (svc if include_service_mark else "")
    return f'<figure class="gantt-figure">\n{body}</figure>\n'


def _page(**kwargs) -> str:
    return "<!doctype html><html><body>\n" + _figure(**kwargs) + "</body></html>\n"


CV_MATCH = (
    "# CV\n\n"
    "## Education\n\n"
    "- **2013-2015** Master of Public Health, Biostatistics. "
    "University of Wisconsin-Madison.\n\n"
    "## Awards and Honors\n\n"
    "- **2021** Spirit of Charlie Award. Health Catalyst.\n"
)

# Same education record, but the award is missing from the CV entirely.
CV_NO_AWARD = (
    "# CV\n\n"
    "## Education\n\n"
    "- **2013-2015** Master of Public Health, Biostatistics. "
    "University of Wisconsin-Madison.\n\n"
    "## Awards and Honors\n\n"
    "- **2010** Best Poster Prize. Some Unrelated Conference.\n"
)


def _install(monkeypatch, tmp_path, page, cv=CV_MATCH):
    ip, cp = tmp_path / "index.html", tmp_path / "cv.md"
    ip.write_text(page, encoding="utf-8")
    cp.write_text(cv, encoding="utf-8")
    monkeypatch.setattr(lint_gantt, "INDEX", ip)
    monkeypatch.setattr(lint_gantt, "CV", cp)


def test_every_mark_has_a_cv_counterpart_passes(monkeypatch, tmp_path, capsys):
    _install(monkeypatch, tmp_path, _page())
    assert lint_gantt.run() == 0, capsys.readouterr().err


def test_mark_without_cv_counterpart_fails(monkeypatch, tmp_path, capsys):
    _install(monkeypatch, tmp_path, _page(), cv=CV_NO_AWARD)
    rc = lint_gantt.run()
    assert rc == 1
    assert "no counterpart in cv.md" in capsys.readouterr().err


def test_mark_drawn_at_wrong_x_fails(monkeypatch, tmp_path, capsys):
    """The years come from the GEOMETRY, so a mark drawn at the wrong
    x-coordinate decodes to the wrong year and stops matching its CV entry.
    This is what makes the lint more than a text diff: the label below is
    still spelled exactly right."""
    _install(monkeypatch, tmp_path, _page(service_year=2018))
    rc = lint_gantt.run()
    assert rc == 1
    err = capsys.readouterr().err
    assert "Spirit of Charlie Award" in err


def test_matching_is_lane_agnostic(monkeypatch, tmp_path, capsys):
    """A SERVICE-lane mark backed by a CV entry filed under ## Education must
    pass. cv.md files fellowships under Education while the chart draws them
    in the service lane (the real case is "Digital Fellow"), and failing that
    pair would be a disagreement about filing, not about facts. See the
    lane-agnostic note in lint_gantt's docstring."""
    cv = (
        "# CV\n\n"
        "## Education\n\n"
        "- **2013-2015** Master of Public Health, Biostatistics. "
        "University of Wisconsin-Madison.\n\n"
        "### Fellowships and Training\n\n"
        "- **2021** Spirit of Charlie Award. Health Catalyst.\n"
    )
    _install(monkeypatch, tmp_path, _page(), cv=cv)
    assert lint_gantt.run() == 0, capsys.readouterr().err


def test_cv_only_entries_are_informational(monkeypatch, tmp_path, capsys):
    """The chart is a curated subset, so CV entries with no mark report but
    never fail -- the reverse of the gate direction."""
    cv = CV_MATCH + (
        "\n## Service and Professional Activities\n\n"
        "### Mentoring\n\n"
        "- **2016-2017** G. Padgett. Undergraduate Research Scholar Program.\n"
    )
    _install(monkeypatch, tmp_path, _page(), cv=cv)
    assert lint_gantt.run() == 0
    out = capsys.readouterr().out
    assert "not on the chart" in out
    assert "Padgett" in out


# ─── wide/narrow variant drift ────────────────────────────────────────────
#
# The figure carries two renderings of one dataset (svg.gantt-wide for
# desktop, svg.gantt-narrow at <=760px) on different coordinate transforms.
# Only the wide one is decoded against cv.md, so without these the narrow
# copy could drift from the record with every gate green.

def _two_variants(narrow_label: str = "Spirit of Charlie Award") -> str:
    """A figure with both SVG variants. The narrow one deliberately uses the
    old 600-unit transform, which is the point: its geometry is NOT
    comparable, only its labels are."""
    wide = (
        f'  <line x1="{_bar_x(2013)}" y1="30" x2="{_bar_x(2015)}" y2="30" '
        'stroke="#111" stroke-width="4"/>\n'
        '  <text x="644" y="34">Public Health MPH, Biostatistics</text>\n'
        f'  <rect x="{_square_x(2021)}" y="160" width="6" height="6" fill="#111"/>\n'
        '  <text x="874" y="166">Spirit of Charlie Award</text>\n'
    )
    narrow = (
        '  <line x1="280" y1="30" x2="318" y2="30" stroke="#111" stroke-width="4"/>\n'
        '  <text x="322" y="34">Public Health MPH, Biostatistics</text>\n'
        '  <rect x="429" y="160" width="6" height="6" fill="#111"/>\n'
        f'  <text x="439" y="166">{narrow_label}</text>\n'
    )
    return (
        '<figure class="gantt-figure">\n'
        f'<svg class="gantt-wide" viewBox="0 0 1200 334">\n{wide}</svg>\n'
        f'<svg class="gantt-narrow" viewBox="0 0 600 292">\n{narrow}</svg>\n'
        "</figure>\n"
    )


def test_only_the_wide_variant_is_decoded():
    """The narrow variant's marks must NOT reach the year decoder. Its 600-unit
    coordinates run through the wide transform would misdate every one of them,
    so a figure with both variants must yield exactly the wide one's marks."""
    from _common import gantt_marks

    marks = gantt_marks(_two_variants())
    assert len(marks) == 2
    assert {mk.label for mk in marks} == {
        "Public Health MPH, Biostatistics",
        "Spirit of Charlie Award",
    }
    spirit = next(mk for mk in marks if mk.label == "Spirit of Charlie Award")
    assert spirit.years == frozenset({2021})


def test_matching_variants_report_no_drift():
    assert lint_gantt.variant_label_drift(_two_variants()) == []


def test_variant_label_drift_is_detected():
    """The paired negative: scoping the decoder to the wide SVG is only safe
    because a narrow copy that says something else fails here."""
    drift = lint_gantt.variant_label_drift(_two_variants("Spirit of Charley Award"))
    assert len(drift) == 2
    assert any("Spirit of Charlie Award" in d and "gantt-wide" in d for d in drift)
    assert any("Spirit of Charley Award" in d and "gantt-narrow" in d for d in drift)


def test_variant_drift_fails_the_gate(monkeypatch, tmp_path, capsys):
    _install(monkeypatch, tmp_path, _two_variants("Spirit of Charley Award"),
             cv=CV_MATCH)
    assert lint_gantt.run() == 1
    assert "variants" in capsys.readouterr().err


def test_single_variant_figure_is_exempt():
    """A figure with one SVG (or none, as the other fixtures here have) must
    not trip the drift check."""
    assert lint_gantt.variant_label_drift(_figure()) == []
