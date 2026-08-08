"""Layer 2 -- lint_recognition subset-gate detection.

Monkeypatches INDEX and CV at tmp fixtures and calls run(): a homepage
#service entry with a matching CV award passes; one with no CV counterpart
fails the subset gate.
"""

from __future__ import annotations

import lint_recognition


def _homepage(commented: bool = False) -> str:
    section = (
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
    if commented:
        # Mirrors index.html's real disable pattern: a bare `<!--` on its
        # own line before the section, a bare `-->` on its own line after.
        section = "<!--\n" + section + "-->\n"
    return (
        "<!doctype html><html><body>\n"
        + section
        + "</body></html>\n"
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


def test_comment_disabled_section_still_parsed(monkeypatch, tmp_path, capsys):
    """#service is wrapped in an HTML comment in index.html (2026-07-30);
    SERVICE_SECTION_RE must still find and parse it there, or this gate
    goes silently vacuous. See CLAUDE.md §Recognition alignment lint."""
    _install(monkeypatch, tmp_path, _homepage(commented=True), CV_MATCH)
    assert lint_recognition.run() == 0, capsys.readouterr().err


def test_comment_disabled_section_still_detects_drift(monkeypatch, tmp_path, capsys):
    """Same property as above, proven non-vacuously: a commented-out
    #service entry with no CV counterpart must still fail the subset
    gate. See CLAUDE.md §Recognition alignment lint."""
    _install(monkeypatch, tmp_path, _homepage(commented=True), CV_NO_MATCH)
    rc = lint_recognition.run()
    assert rc == 1
    assert "no counterpart" in capsys.readouterr().err
