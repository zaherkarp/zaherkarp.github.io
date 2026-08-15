"""Layer 2 -- lint_recognition subset-gate detection.

Monkeypatches INDEX and CV at tmp fixtures and calls run(): a service-lane
Gantt mark with a matching CV award passes; one with no counterpart in the
CV's recognition record fails the subset gate.

The homepage surface moved on 2026-08-13. It used to be the .row-entry blocks
in `<section id="service">`; that section was deleted, so the lint now reads
the SERVICE LANE of the Gantt figure, which is the page's remaining view into
the awards / fellowships / service record. The comment-disabled fixtures that
used to live here are gone with the section they mirrored.
"""

from __future__ import annotations

import lint_recognition
from _common import GANTT_BASE_YEAR as BASE
from _common import GANTT_PX_PER_YEAR as PX
from _common import GANTT_X0 as X0


def _square_x(year: int) -> int:
    return X0 + (year - BASE) * PX - 3


def _homepage(service_label: str = "Spirit of Charlie Award",
              service_year: int = 2021,
              include_education_mark: bool = False) -> str:
    """A gantt figure with one service-lane mark, optionally an education one.

    y=160 is below GANTT_LANE_DIVIDER_Y, so it is a service mark; y=30 is
    above it, so it is an education mark this lint must ignore. Both stay
    valid either side of a chart re-layout as long as the divider stays
    between them, which is why the number is not restated here.
    """
    edu = (
        f'  <rect x="{_square_x(2007)}" y="30" width="6" height="6" fill="#111"/>\n'
        '  <text x="200" y="36">BA, English Literature</text>\n'
    ) if include_education_mark else ""
    svc = (
        f'  <rect x="{_square_x(service_year)}" y="160" width="6" height="6" '
        'fill="#111"/>\n'
        f'  <text x="439" y="166">{service_label}</text>\n'
    )
    return (
        "<!doctype html><html><body>\n"
        f'<figure class="gantt-figure">\n{edu}{svc}</figure>\n'
        "</body></html>\n"
    )


CV_MATCH = (
    "# CV\n\n"
    "## Awards and Honors\n\n"
    "- **2021** Spirit of Charlie Award. Health Catalyst.\n"
)

CV_NO_MATCH = (
    "# CV\n\n"
    "## Awards and Honors\n\n"
    "- **2010** Best Poster Prize. Some Unrelated Conference.\n"
)


def _install(monkeypatch, tmp_path, homepage, cv):
    ip, cp = tmp_path / "index.html", tmp_path / "cv.md"
    ip.write_text(homepage, encoding="utf-8")
    cp.write_text(cv, encoding="utf-8")
    monkeypatch.setattr(lint_recognition, "INDEX", ip)
    monkeypatch.setattr(lint_recognition, "CV", cp)


def test_matching_award_passes(monkeypatch, tmp_path, capsys):
    _install(monkeypatch, tmp_path, _homepage(), CV_MATCH)
    assert lint_recognition.run() == 0, capsys.readouterr().err


def test_service_mark_without_cv_counterpart_fails(monkeypatch, tmp_path, capsys):
    _install(monkeypatch, tmp_path, _homepage(), CV_NO_MATCH)
    rc = lint_recognition.run()
    assert rc == 1
    assert "no counterpart" in capsys.readouterr().err


def test_scoped_to_recognition_sections(monkeypatch, tmp_path, capsys):
    """The property that distinguishes this lint from lint_gantt: a service
    mark backed ONLY by a non-recognition CV section must FAIL here, even
    though lint_gantt (which accepts any Education / Service / Awards entry)
    would pass it. If the two are ever merged, this scoping is what must
    survive. See the relationship note in lint_recognition's docstring."""
    cv = (
        "# CV\n\n"
        "## Education\n\n"
        "- **2021** Spirit of Charlie Award. Health Catalyst.\n\n"
        # A populated recognition section, so the run fails on the GATE and
        # not on the empty-parse guard. Without this the test would pass
        # vacuously: no Awards/Fellowships/Service section at all also
        # returns 1.
        "## Awards and Honors\n\n"
        "- **2010** Best Poster Prize. Some Unrelated Conference.\n"
    )
    _install(monkeypatch, tmp_path, _homepage(), cv)
    assert lint_recognition.run() == 1
    assert "no counterpart" in capsys.readouterr().err


def test_education_lane_marks_are_ignored(monkeypatch, tmp_path, capsys):
    """Only the service lane is this lint's business. The education mark has
    no CV record at all here and must not fail the gate."""
    _install(
        monkeypatch, tmp_path,
        _homepage(include_education_mark=True), CV_MATCH,
    )
    assert lint_recognition.run() == 0, capsys.readouterr().err


def test_subsection_heading_supplies_tokens(monkeypatch, tmp_path, capsys):
    """cv.md's `### Peer Review` entries name journals and never state the
    role, so matching on the item body alone would leave a "peer reviewer"
    chart label with nothing to match. The subsection heading travels with
    the entry to close that gap."""
    cv = (
        "# CV\n\n"
        "## Service and Professional Activities\n\n"
        "### Peer Review\n\n"
        "- **2019-present** Reviewer. Health Environments Research and "
        "Design Journal.\n"
    )
    _install(
        monkeypatch, tmp_path,
        _homepage(service_label="peer reviewer (ongoing)", service_year=2019),
        cv,
    )
    assert lint_recognition.run() == 0, capsys.readouterr().err
