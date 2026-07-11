"""Layer 2 -- lint_facts cross-surface drift detection.

Builds minimal resume.md / index.html / cv.md fixtures in tmp_path,
monkeypatches lint_facts's RESUME / INDEX / CV path constants at them, and
calls main(): aligned fixtures return 0, an intentional current-employer
mismatch returns 1.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import lint_facts

TITLE = "Manager, Data Science and Engineering"


def _resume(org="Baltimore Health Analytics"):
    return (
        "# Zaher Karp\n\n"
        "me@example.com\n\n"
        "## Experience\n\n"
        f"**{org}** | {TITLE}\n"
        "Nov 2025 - Present\n"
        "*SQL, Python*\n\n"
        "- did things\n"
    )


def _index(org="Baltimore Health Analytics"):
    return (
        "<!doctype html><html><body>\n"
        '<script type="application/ld+json">\n'
        "{\n"
        '  "@type": "Person",\n'
        f'  "jobTitle": "{TITLE}",\n'
        f'  "worksFor": {{ "@type": "Organization", "name": "{org}" }}\n'
        "}\n"
        "</script>\n"
        "<section id=\"experience\">\n"
        f"<h3>{TITLE}</h3>\n"
        f'<p class="meta">{org} · remote · Nov 2025 to Present</p>\n'
        "</section>\n"
        "</body></html>\n"
    )


def _cv(org="Baltimore Health Analytics"):
    return (
        "# Zaher Karp\n\n"
        "## Appointments\n\n"
        f"- **2025–present** {org}, {TITLE}. Leads the team.\n\n"
        "## Past Research Positions\n\n"
        "- **2009–2018** University of Wisconsin-Madison, Researcher.\n"
    )


def _install(monkeypatch, tmp_path, resume, index, cv):
    rp, ip, cp = tmp_path / "resume.md", tmp_path / "index.html", tmp_path / "cv.md"
    rp.write_text(resume, encoding="utf-8")
    ip.write_text(index, encoding="utf-8")
    cp.write_text(cv, encoding="utf-8")
    monkeypatch.setattr(lint_facts, "RESUME", rp)
    monkeypatch.setattr(lint_facts, "INDEX", ip)
    monkeypatch.setattr(lint_facts, "CV", cp)


def test_aligned_surfaces_pass(monkeypatch, tmp_path, capsys):
    _install(monkeypatch, tmp_path, _resume(), _index(), _cv())
    assert lint_facts.main() == 0, capsys.readouterr().err


def test_current_employer_mismatch_fails(monkeypatch, tmp_path, capsys):
    _install(monkeypatch, tmp_path, _resume(), _index(org="Some Other Company"), _cv())
    rc = lint_facts.main()
    assert rc == 1
    assert "current employer mismatch" in capsys.readouterr().err


def test_cv_missing_resume_employer_fails(monkeypatch, tmp_path, capsys):
    # Resume/index agree on the current employer, but the CV never mentions it.
    _install(
        monkeypatch,
        tmp_path,
        _resume(),
        _index(),
        _cv(org="Baltimore Health Analytics").replace("Baltimore Health Analytics", "Ghost Corp"),
    )
    rc = lint_facts.main()
    assert rc == 1
    assert "cv.md" in capsys.readouterr().err
