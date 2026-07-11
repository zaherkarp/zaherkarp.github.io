"""Layer 3 -- build_resume.regenerate_resume_skills smoke test.

The whole module is skipped when WeasyPrint's native deps (libpango, ...)
are unavailable, because importing build_resume imports weasyprint. CI runs
this job WITHOUT pango installed, so the skip path is exercised on purpose.

regenerate_resume_skills() rewrites resume.md's <!-- skills --> block from
the real skills.yaml. The test points CONTENT_DIR at a tmp resume.md with a
deliberately-wrong block and asserts the rewrite lands the skills.yaml
render.
"""

from __future__ import annotations

import re

import pytest

# Importing build_resume pulls in weasyprint, which loads libpango/cairo via
# cffi AT IMPORT TIME. Without those native libs the import raises OSError
# (not ImportError), which pytest.importorskip would NOT catch -- so guard
# both the weasyprint and build_resume imports and skip the whole module on
# either an ImportError or a native-lib OSError. CI runs this job without
# pango installed on purpose, exercising this skip path.
try:
    import weasyprint  # noqa: F401
    import build_resume
except (ImportError, OSError) as exc:  # pragma: no cover - env-dependent skip
    pytest.skip(
        f"WeasyPrint native deps (libpango/cairo) unavailable: {exc}",
        allow_module_level=True,
    )

import _skills  # noqa: E402

BLOCK_RE = re.compile(r"<!-- skills:start -->\n(.*?)\n<!-- skills:end -->", re.DOTALL)


def _resume(block_body: str) -> str:
    return (
        "# Zaher Karp\n\n"
        "## Skills\n\n"
        "<!-- skills:start -->\n"
        f"{block_body}\n"
        "<!-- skills:end -->\n"
    )


def test_regenerate_rewrites_block_from_skills_yaml(monkeypatch, tmp_path):
    rp = tmp_path / "resume.md"
    rp.write_text(_resume("**Wrong:** stale content"), encoding="utf-8")
    monkeypatch.setattr(build_resume, "CONTENT_DIR", tmp_path)

    build_resume.regenerate_resume_skills()

    after = rp.read_text(encoding="utf-8")
    block = BLOCK_RE.search(after).group(1)
    expected = _skills.render_resume_skills(_skills.load_skills())
    assert block == expected


def test_already_in_sync_is_noop(monkeypatch, tmp_path):
    expected = _skills.render_resume_skills(_skills.load_skills())
    rp = tmp_path / "resume.md"
    rp.write_text(_resume(expected), encoding="utf-8")
    monkeypatch.setattr(build_resume, "CONTENT_DIR", tmp_path)

    before = rp.read_text(encoding="utf-8")
    build_resume.regenerate_resume_skills()
    assert rp.read_text(encoding="utf-8") == before


def test_missing_marker_leaves_file_untouched(monkeypatch, tmp_path, capsys):
    rp = tmp_path / "resume.md"
    original = "# Zaher Karp\n\nNo skills markers here.\n"
    rp.write_text(original, encoding="utf-8")
    monkeypatch.setattr(build_resume, "CONTENT_DIR", tmp_path)

    build_resume.regenerate_resume_skills()
    assert rp.read_text(encoding="utf-8") == original
    assert "WARN" in capsys.readouterr().err
