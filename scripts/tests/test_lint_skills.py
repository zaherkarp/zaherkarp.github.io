"""Layer 2 -- lint_skills drift detection.

run() compares resume.md's <!-- skills --> block against what
render_resume_skills(load_skills()) produces from the real skills.yaml. A
fixture resume whose block matches that render passes; a divergent block
fails.
"""

from __future__ import annotations

import _skills
import lint_skills


def _resume_with_block(block_body: str) -> str:
    return (
        "# Zaher Karp\n\n"
        "## Skills\n\n"
        "<!-- skills:start -->\n"
        f"{block_body}\n"
        "<!-- skills:end -->\n"
    )


def test_matching_block_passes(monkeypatch, tmp_path, capsys):
    expected = _skills.render_resume_skills(_skills.load_skills())
    rp = tmp_path / "resume.md"
    rp.write_text(_resume_with_block(expected), encoding="utf-8")
    monkeypatch.setattr(lint_skills, "RESUME", rp)
    assert lint_skills.run() == 0, capsys.readouterr().err


def test_divergent_block_fails(monkeypatch, tmp_path, capsys):
    rp = tmp_path / "resume.md"
    rp.write_text(_resume_with_block("**Wrong:** this does not match skills.yaml"), encoding="utf-8")
    monkeypatch.setattr(lint_skills, "RESUME", rp)
    rc = lint_skills.run()
    assert rc == 1
    assert "drift" in capsys.readouterr().err.lower()


def test_missing_block_skips_cleanly(monkeypatch, tmp_path, capsys):
    rp = tmp_path / "resume.md"
    rp.write_text("# Zaher Karp\n\nNo skills markers here.\n", encoding="utf-8")
    monkeypatch.setattr(lint_skills, "RESUME", rp)
    # No block -> documented graceful skip (returns 0).
    assert lint_skills.run() == 0
