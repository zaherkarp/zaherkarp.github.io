"""Layer 2 -- lint_gantt figure/section alignment detection.

Builds an index.html fixture with a gantt figure plus #education and
#service sections. The figure encodes years positionally via the chart
transform x(year) = 90 + (year - 2003) * 19. When every section entry has a
matching mark, run() passes; drop the service mark and the service entry has
no counterpart, so run() fails.
"""

from __future__ import annotations

import lint_gantt

X0, PX, BASE = 90, 19, 2003


def _square_x(year: int) -> int:
    # Parser reads the year from the square centre (x + 3), width 6.
    return X0 + (year - BASE) * PX - 3


def _bar_x(year: int) -> int:
    return X0 + (year - BASE) * PX


def _figure(include_service_mark: bool) -> str:
    # Education bar 2013-2015 in the education lane (y < 135).
    edu = (
        f'  <line x1="{_bar_x(2013)}" y1="30" x2="{_bar_x(2015)}" y2="30" '
        'stroke="#111" stroke-width="4"/>\n'
        '  <text x="322" y="34">Public Health MPH, Biostatistics</text>\n'
    )
    # Service square 2021 in the service lane (y > 135).
    svc = (
        f'  <rect x="{_square_x(2021)}" y="160" width="6" height="6" fill="#111"/>\n'
        '  <text x="439" y="166">Spirit of Charlie</text>\n'
    )
    body = edu + (svc if include_service_mark else "")
    return f'<figure class="gantt-figure">\n{body}</figure>\n'


def _sections() -> str:
    return (
        '<section id="education">\n'
        '  <div class="row-entry">\n'
        '    <div class="row-date">2013 to 2015</div>\n'
        '    <div class="row-body">\n'
        '      <span class="row-title">Master of Public Health, Biostatistics</span>\n'
        '      <span class="row-org">University of Wisconsin-Madison</span>\n'
        "    </div>\n"
        "  </div>\n"
        "</section>\n"
        '<section id="service">\n'
        '  <div class="row-entry">\n'
        '    <div class="row-date">2021</div>\n'
        '    <div class="row-body">\n'
        '      <span class="row-title">Spirit of Charlie Award</span>\n'
        '      <span class="row-org">Spirit of Charlie Foundation</span>\n'
        "    </div>\n"
        "  </div>\n"
        "</section>\n"
    )


def _page(include_service_mark: bool) -> str:
    return (
        "<!doctype html><html><body>\n"
        + _figure(include_service_mark)
        + _sections()
        + "</body></html>\n"
    )


def _install(monkeypatch, tmp_path, page):
    ip = tmp_path / "index.html"
    ip.write_text(page, encoding="utf-8")
    monkeypatch.setattr(lint_gantt, "INDEX", ip)


def test_every_entry_has_a_mark_passes(monkeypatch, tmp_path, capsys):
    _install(monkeypatch, tmp_path, _page(include_service_mark=True))
    assert lint_gantt.run() == 0, capsys.readouterr().err


def test_service_entry_without_mark_fails(monkeypatch, tmp_path, capsys):
    _install(monkeypatch, tmp_path, _page(include_service_mark=False))
    rc = lint_gantt.run()
    assert rc == 1
    assert "no matching" in capsys.readouterr().err
