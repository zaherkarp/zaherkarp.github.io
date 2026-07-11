"""Layer 2 -- lint_vocab violation detection.

Exercises check_text() directly with wrong-case CMS program names (flagged)
and their accepted canonical forms (clean). The path argument only feeds the
message, so a dummy Path is fine.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import lint_vocab

DUMMY = Path("fixture.md")


def _check(text, *, fenced=True):
    return lint_vocab.check_text(DUMMY, text, fenced=fenced, exemptions=frozenset())


def test_all_caps_star_ratings_flagged():
    v = _check("The plan improved its STAR Ratings this year.")
    assert any('"STAR Ratings"' in s for s in v), v


def test_all_caps_medicare_advantage_flagged():
    v = _check("Enrollment in MEDICARE ADVANTAGE plans grew.")
    assert any('"MEDICARE ADVANTAGE"' in s for s in v), v


def test_agency_name_without_ampersand_flagged():
    v = _check("Guidance from the Centers for Medicare and Medicaid Services.")
    assert any("agency name uses an ampersand" in s for s in v), v


def test_bare_all_caps_star_stem_flagged():
    v = _check("A STARs remediation plan.")
    assert v, "expected the bare STARs stem to be flagged"


def test_accepted_forms_are_clean():
    text = (
        "The plan's Star Ratings improved. Medicare Advantage enrollment rose. "
        "Per the Centers for Medicare & Medicaid Services, a 4.0 star cliff "
        "affects 5 stars overall."
    )
    assert _check(text) == []


def test_exemption_suppresses_flag():
    v = lint_vocab.check_text(
        DUMMY,
        "As cited: STAR Ratings (verbatim).",
        fenced=True,
        exemptions=frozenset({"STAR Ratings"}),
    )
    assert v == []


def test_skip_range_inline_code_not_flagged():
    # A wrong-case form inside an inline code span is a skip range.
    assert _check("Use the `STAR Ratings` column name.") == []
