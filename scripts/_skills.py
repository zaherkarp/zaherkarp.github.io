#!/usr/bin/env python3
"""_skills.py

Shared skills data layer, the structural twin of _publications.py. Owns the
src/content/skills.yaml schema (see that file's header for the field contract)
so the loader and renderers live in one place rather than in either consumer.

Consumers:
  - scripts/build_jobsearch.py  -> the private job-fit matrix + packets.
  - scripts/lint_jobfit.py      -> the evidence-gap report.
  - scripts/build_resume.py     -> the resume "## Skills" section. DEFERRED:
                                   render_resume_skills() is written and
                                   exercised here, but not wired into the
                                   resume build until explicitly turned on.

This module is leaf-level: it imports only stdlib, yaml, and the matcher
primitives in _common, so nothing it touches can create an import cycle.
"""

from __future__ import annotations

import html as html_lib
import re
from pathlib import Path

import yaml

from _common import tokens_of

ROOT = Path(__file__).resolve().parent.parent
SKILLS_YAML = ROOT / "src" / "content" / "skills.yaml"

# Minimal stoplist for matching a skill against a job-description "want".
# Deliberately tiny (unlike the recognition lints): skill names are short and
# every real token carries signal, so we only drop pure connectives.
JOBFIT_STOP = {"and", "or", "the", "of", "with", "a", "an", "to", "in", "for", "on"}


def _esc(s: str) -> str:
    """HTML-escape text (matches the other build scripts: no quote escaping)."""
    return html_lib.escape(str(s), quote=False)


def load_skills(path: Path = SKILLS_YAML) -> dict:
    """Parse skills.yaml into {skills, archetypes, categories_order}.

    Tolerates a bare top-level list (forward-compat): it is treated as the
    skills list with no archetypes and a category order derived from first
    appearance.
    """
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if isinstance(data, list):
        data = {"skills": data}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a top-level mapping or list")
    skills = data.get("skills") or []
    if not isinstance(skills, list):
        raise ValueError(f"{path}: 'skills' must be a list")
    order = data.get("categories_order")
    if not order:
        seen: list[str] = []
        for s in skills:
            cat = s.get("category", "")
            if cat and cat not in seen:
                seen.append(cat)
        order = seen
    return {
        "skills": skills,
        "archetypes": data.get("archetypes") or [],
        "categories_order": order,
    }


# ─── resume Skills renderer (DEFERRED wire-in) ─────────────────────────────

def render_resume_skills(data: dict) -> str:
    """Regenerate the resume "## Skills" body from skills.yaml.

    One `**Category:** a · b · c` line per category in
    `categories_order`, skills in file order within each category, blank line
    between categories. Seeded byte-exact to the current resume.md lines, so
    the first regeneration is a no-op diff. Em-dash-clean by construction
    (names are em-dash-clean and the separator is a middot).
    """
    skills = data["skills"]
    lines: list[str] = []
    for cat in data["categories_order"]:
        names = [s["name"] for s in skills if s.get("category") == cat]
        if not names:
            continue
        lines.append(f"**{cat}:** " + " · ".join(names))
    return "\n\n".join(lines)


# ─── evidence index ────────────────────────────────────────────────────────

def skill_evidence_index(skills: list[dict]) -> dict[str, list[dict]]:
    """Map skill id -> its list of {kind, ref} evidence refs (possibly empty)."""
    index: dict[str, list[dict]] = {}
    for s in skills:
        refs = s.get("evidence") or []
        index[s["id"]] = [r for r in refs if isinstance(r, dict) and r.get("ref")]
    return index


# ─── want matching ─────────────────────────────────────────────────────────

def _whole(needle: str, hay: str) -> bool:
    """True if `needle` occurs in `hay` on alphanumeric boundaries, so a short
    token like "r" or "git" cannot match inside "medicare" or "digital"."""
    return re.search(
        r"(?<![a-z0-9])" + re.escape(needle) + r"(?![a-z0-9])", hay
    ) is not None


def skill_matches_want(skill: dict, want: str) -> bool:
    """True if `skill` plausibly satisfies a job-description `want`.

    Exact, then whole-word containment either way (length-guarded so a
    one-letter name like "R" cannot match inside "medicare"), against the
    skill name and its aliases, with a shared-token fallback. This is the
    deliberate divergence flagged in the plan: skills and wants carry no year,
    so the year-gated recognition matcher in _common is the wrong tool here;
    we name-match first and only fall back to token overlap.
    """
    w = " ".join(str(want).strip().lower().split())
    if not w:
        return False
    cands = [skill.get("name", "")] + list(skill.get("aliases") or [])
    cands = [" ".join(str(c).strip().lower().split()) for c in cands if str(c).strip()]
    for c in cands:
        if w == c:
            return True
        if len(w) >= 3 and len(c) >= 3 and (_whole(c, w) or _whole(w, c)):
            return True
    wt = tokens_of(w, JOBFIT_STOP)
    if wt:
        for c in cands:
            if wt & tokens_of(c, JOBFIT_STOP):
                return True
    return False


def match_want(skills: list[dict], want: str) -> dict | None:
    """Return the first skill that satisfies `want`, or None."""
    for s in skills:
        if skill_matches_want(s, want):
            return s
    return None


# ─── job-fit matrix renderer (Markdown) ────────────────────────────────────

def render_jobfit_matrix(
    data: dict,
    proven: set[str] | None = None,
    weights: dict[str, float] | None = None,
) -> str:
    """Render the private job-fit matrix as Markdown.

    `proven` is the set of skill ids with at least one resolving public
    artifact; `weights` maps skill id -> recency weight in [0, 1]. Both are
    computed by the caller via lint_jobfit (to avoid an import cycle). The
    recency-weighted coverage counts a met want by its skill's weight rather
    than 1.0, so a target met only by stale skills scores below one met by
    fresh ones. When `proven`/`weights` are None the annotations are omitted.
    """
    skills = data["skills"]
    archetypes = data["archetypes"]

    def weight_of(skill: dict) -> float:
        if weights is None:
            return 1.0
        return weights.get(skill["id"], 0.0)

    def mark(skill: dict | None) -> str:
        if skill is None:
            return "no matching skill"
        if proven is None:
            return skill["name"]
        tag = "proven" if skill["id"] in proven else "unproven"
        if weights is not None:
            tag += f", recency {weight_of(skill):.2f}"
        return f'{skill["name"]} ({tag})'

    out: list[str] = ["# Job-fit matrix", ""]
    out.append("Generated from src/content/skills.yaml by "
               "`scripts/build_jobsearch.py matrix`. Private; do not commit.")
    if weights is not None:
        out.append("")
        out.append("_Coverage is recency-weighted: a want met by a skill last "
                   "shown years ago counts for less than one shown recently._")
    out.append("")

    if not archetypes:
        out.append("_No archetypes defined in skills.yaml._")
        return "\n".join(out) + "\n"

    # Summary table.
    out.append("## Coverage by target archetype")
    out.append("")
    out.append("| Archetype | Wants met | Proven | Weighted | Total | Coverage |")
    out.append("| --- | --- | --- | --- | --- | --- |")
    detail: list[str] = []
    for arc in archetypes:
        wants = arc.get("wants") or []
        matched = [(w, match_want(skills, w)) for w in wants]
        met = [m for _, m in matched if m is not None]
        proven_met = [m for m in met
                      if proven is not None and m["id"] in proven]
        weighted = sum(weight_of(m) for m in met)
        total = len(wants) or 1
        pct = round(100 * len(met) / total)
        wpct = round(100 * weighted / total)
        out.append(
            f'| {arc.get("label", arc.get("id", "?"))} '
            f'| {len(met)} | {len(proven_met) if proven is not None else "?"} '
            f'| {wpct if weights is not None else "?"}% '
            f'| {len(wants)} | {pct}% |'
        )
        # Per-archetype detail block.
        detail.append("")
        detail.append(f'## {arc.get("label", arc.get("id", "?"))}')
        detail.append(f'Wants: {", ".join(wants)}')
        detail.append("")
        for w, m in matched:
            box = "x" if m is not None else " "
            detail.append(f"- [{box}] {w} → {mark(m)}")

    out.extend(detail)
    return "\n".join(out) + "\n"
