#!/usr/bin/env python3
"""lint_skills.py

Keeps the resume's Skills block in lockstep with its source of truth,
src/content/skills.yaml, WITHOUT trusting that a build ran.

build_resume.py regenerates resume.md's `<!-- skills:start --> ... <!--
skills:end -->` block in place from skills.yaml (regenerate_resume_skills,
via _skills.render_resume_skills) and commits resume.md back. So on the
default branch the two stay in sync automatically. But that build only
runs on push to main + the portfolio workflow_run chain -- NOT on pull
requests -- so a PR that hand-edits the resume Skills block, or edits
skills.yaml without regenerating resume.md, would merge a resume.md that
disagrees with its own source and only get silently overwritten by the
next main build. skills.yaml also feeds the private job-fit tooling, so a
drifted resume Skills line means the public resume and that tooling
disagree.

GATE (hard fail, blocks push). The committed resume.md Skills block must
equal render_resume_skills(load_skills()). Same lockstep contract as
lint_facts (resume vs homepage) and lint_recognition (homepage vs CV):
when you change skills.yaml, regenerate resume.md in the same change
(`python scripts/build_resume.py`, or reconcile the block by hand).

Skips cleanly when skills.yaml or the markers are absent.
"""

from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

from _common import install_git_hooks
from _skills import SKILLS_YAML, load_skills, render_resume_skills

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
RESUME = ROOT / "src" / "content" / "resume.md"

_BLOCK_RE = re.compile(
    r"<!-- skills:start -->\n(.*?)\n<!-- skills:end -->", re.DOTALL
)


def run() -> int:
    if not SKILLS_YAML.exists() or not RESUME.exists():
        print("skills lint: skipped (skills.yaml or resume.md absent)")
        return 0

    text = RESUME.read_text(encoding="utf-8")
    m = _BLOCK_RE.search(text)
    if not m:
        print("skills lint: skipped (no <!-- skills:start/end --> block "
              "in resume.md)")
        return 0

    in_file = m.group(1).strip()
    expected = render_resume_skills(load_skills()).strip()

    if in_file == expected:
        print("skills lint: resume.md Skills block in sync with skills.yaml")
        return 0

    diff = "\n".join(
        difflib.unified_diff(
            expected.splitlines(),
            in_file.splitlines(),
            fromfile="render_resume_skills(skills.yaml)",
            tofile="resume.md <!-- skills --> block",
            lineterm="",
        )
    )
    print(
        "Skills lint found drift: resume.md's Skills block does not match "
        "what skills.yaml would generate.\n\n"
        f"{diff}\n\n"
        "skills.yaml is the source of truth. Reconcile by editing skills.yaml "
        "and regenerating (`python scripts/build_resume.py`), or fix the "
        "resume.md block to match. See CLAUDE.md §Resume and CV pipeline.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(run())
