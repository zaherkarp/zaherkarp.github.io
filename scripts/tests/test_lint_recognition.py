"""Layer 2 -- lint_recognition subset-gate detection.

Monkeypatches INDEX and CV at tmp fixtures and calls run(): a homepage
#service entry with a matching CV award passes; one with no CV counterpart
fails the subset gate.
"""

from __future__ import annotations

import lint_recognition


def _homepage() -> str:
    return (
        "<!doctype html><html><body>\n"
        '<section id="service">\n'
        '  <div class="row-entry">\n'
        '    <div class="row-date">2021</div>\n'
        '    <div class="row-body">\n'
        '      <span class="row-title">Spirit of Charlie Award</span>\n'
        '      <span class="row-org">Spirit of Charlie Foundation</span>\n'
        "    </div>\n"
        "  </div>\n"
        "</section>\n"
        "</body></html>\n"
    )


CV_MATCH = (
    "# CV\n\n"
    "## Awards and Honors\n\n"
    "- **2021** Spirit of Charlie Award. Spirit of Charlie Foundation.\n"
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


def test_homepage_entry_without_cv_counterpart_fails(monkeypatch, tmp_path, capsys):
    _install(monkeypatch, tmp_path, _homepage(), CV_NO_MATCH)
    rc = lint_recognition.run()
    assert rc == 1
    assert "no counterpart" in capsys.readouterr().err
