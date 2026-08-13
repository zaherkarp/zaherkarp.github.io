"""Layer 2 -- lint_gantt figure/CV alignment detection.

Builds an index.html fixture holding a gantt figure, plus a cv.md fixture.
The figure encodes years positionally via the chart transform
x(year) = 90 + (year - 2003) * 19, so each mark's year is read back from its
x-coordinate rather than from any text.

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

X0, PX, BASE = 90, 19, 2003


def _square_x(year: int) -> int:
    # Parser reads the year from the square centre (x + 3), width 6.
    return X0 + (year - BASE) * PX - 3


def _bar_x(year: int) -> int:
    return X0 + (year - BASE) * PX


def _figure(include_service_mark: bool = True, service_year: int = 2021) -> str:
    # Education bar 2013-2015 in the education lane (y < 135).
    edu = (
        f'  <line x1="{_bar_x(2013)}" y1="30" x2="{_bar_x(2015)}" y2="30" '
        'stroke="#111" stroke-width="4"/>\n'
        '  <text x="322" y="34">Public Health MPH, Biostatistics</text>\n'
    )
    # Service square in the service lane (y > 135).
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
