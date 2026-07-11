"""Layer 2 -- lint_notes additivity detection.

Two seams:
  - collisions(): the pure predicate for number and shingle overlap.
  - check_index(): the end-to-end homepage scan, driven by a monkeypatched
    INDEX fixture holding a note that restates page prose.
"""

from __future__ import annotations

import lint_notes


# ── pure predicate ─────────────────────────────────────────────────────────

def test_collisions_flags_shared_significant_number():
    problems = lint_notes.collisions("this repeats 373,000 gaps", "context has 373,000 elsewhere")
    assert any('repeats number "373000"' in p for p in problems), problems


def test_collisions_flags_shared_five_word_shingle():
    phrase = "the refill turnaround dropped sharply overnight"
    problems = lint_notes.collisions(phrase, "prose where the refill turnaround dropped sharply too")
    assert any("shares phrase" in p for p in problems), problems


def test_collisions_ignores_years_and_small_numbers():
    # 2020 is a year (excluded); 42 is < 1000 (excluded).
    assert lint_notes.collisions("in 2020 there were 42 items", "also 2020 and 42") == []


def test_collisions_clean_when_additive():
    assert lint_notes.collisions("see CMS Technical Notes for the cut point", "the cliff matters") == []


# ── end-to-end index scan ──────────────────────────────────────────────────

def _index_page(note_body: str, prose: str) -> str:
    return (
        "<!doctype html><html><body>\n"
        f"<p>{prose}</p>\n"
        '<label for="sn-x" class="margin-toggle sidenote-number"></label>\n'
        '<input type="checkbox" id="sn-x" class="margin-toggle"/>\n'
        f'<span class="sidenote">{note_body}</span>\n'
        "</body></html>\n"
    )


def test_check_index_flags_number_restatement(monkeypatch, tmp_path):
    p = tmp_path / "index.html"
    p.write_text(
        _index_page(
            "The platform surfaced 373,000 gaps.",
            "In practice the platform surfaced 373,000 care gaps in six months.",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(lint_notes, "INDEX", p)
    violations, checked = lint_notes.check_index()
    assert checked == 1
    assert any("373000" in v for v in violations), violations


def test_check_index_clean_when_additive(monkeypatch, tmp_path):
    p = tmp_path / "index.html"
    p.write_text(
        _index_page(
            "See the CMS Technical Notes for the exact cut point.",
            "The cliff is where the bonus payment turns on.",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(lint_notes, "INDEX", p)
    violations, checked = lint_notes.check_index()
    assert checked == 1
    assert violations == []


def test_check_index_stat_num_note_is_exempt(monkeypatch, tmp_path):
    # A .stat-num note deliberately surfaces a buried number; it is exempt.
    page = (
        "<!doctype html><html><body>\n"
        "<p>The platform surfaced 373,000 care gaps.</p>\n"
        '<span class="marginnote"><span class="stat-num">373,000</span> care gaps</span>\n'
        "</body></html>\n"
    )
    p = tmp_path / "index.html"
    p.write_text(page, encoding="utf-8")
    monkeypatch.setattr(lint_notes, "INDEX", p)
    violations, checked = lint_notes.check_index()
    assert violations == []
    assert checked == 0  # the stat-num note is skipped before counting
