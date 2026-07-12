"""Layer 1 -- baseline: the committed repo is currently lint-clean.

Each of the nine gate linters is run in-process against the REAL repo
(their module-level path constants already point at the repo root) and
asserted to return exit code 0. This is the cheapest, most stable, and
highest-value characterization: it locks in the property that a later
consolidation refactor must preserve -- the repo passes every linter.

Run in-process (not via subprocess) on purpose: a subprocess would execute
each script's top-level ``install_git_hooks()`` and mutate the repo's git
config. conftest neutralizes that call for in-process imports.

Also asserts the four grep guards that lint.yml enforces alongside the
nine linters, so the full pre-push gate is characterized as green.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# (module_name, entrypoint_attr) for each of the nine gate linters.
LINTERS = [
    ("lint_blog", "main"),
    ("lint_vocab", "main"),
    ("lint_facts", "main"),
    ("lint_notes", "main"),
    ("lint_recognition", "run"),
    ("lint_gantt", "run"),
    ("lint_markers", "run"),
    ("lint_skills", "run"),
    ("lint_links", "run"),
]


@pytest.mark.parametrize("module_name,entry", LINTERS, ids=[m for m, _ in LINTERS])
def test_linter_clean_on_real_repo(module_name, entry, capsys):
    """Every gate linter returns 0 against the current committed repo."""
    mod = __import__(module_name)
    rc = getattr(mod, entry)()
    captured = capsys.readouterr()
    assert rc == 0, (
        f"{module_name}.{entry}() returned {rc} on the real repo; "
        f"expected a clean pass.\nstdout:\n{captured.out}\n"
        f"stderr:\n{captured.err}"
    )


# ── grep guards mirrored from .github/workflows/lint.yml ───────────────────

CHROME_FILES = [
    "index.html",
    "src/content/resume.md",
    "src/content/cv.md",
    "life-in-weeks/index.html",
]


def test_chrome_is_em_dash_clean():
    """No em-dash in the hand-authored chrome surfaces (lint.yml guard)."""
    offenders = {}
    for rel in CHROME_FILES:
        p = REPO_ROOT / rel
        if not p.exists():
            continue
        n = p.read_text(encoding="utf-8").count("—")
        if n:
            offenders[rel] = n
    assert not offenders, f"em-dash found in chrome: {offenders}"


def test_accent_discipline_cap():
    """--accent + #7a0000 uses in index.html stay at or below the cap of 20."""
    text = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
    n = len(re.findall(r"--accent|#7a0000", text))
    assert n <= 20, f"accent discipline: {n} uses in index.html (cap 20)"


def test_no_p_wrapped_svg_children_in_built_blog():
    """Built blog/ has no <p>-wrapped SVG children (blank-line-inside-<svg>)."""
    blog_dir = REPO_ROOT / "blog"
    if not blog_dir.exists():
        pytest.skip("blog/ not built in this checkout")
    pat = re.compile(r"<p><(?:text|line|polyline|circle|rect|polygon)")
    offenders = [
        str(p.relative_to(REPO_ROOT))
        for p in blog_dir.rglob("*.html")
        if pat.search(p.read_text(encoding="utf-8"))
    ]
    assert not offenders, f"<p>-wrapped SVG children in: {offenders}"


def test_critique_pipeline_independence():
    """No Anthropic SDK import / API-key env var under scripts or workflows.

    Mirrors the lint.yml guard: the self-referential pre-push and lint.yml
    files are excluded, and commented lines do not count.

    The two forbidden literals are assembled from fragments so this file
    itself never contains either contiguously -- otherwise the real
    server-side lint.yml grep (which scans all of scripts/) would flag this
    test, exactly the false positive that guard warns about.
    """
    frag_sdk = "import an" + "thropic"
    frag_key = "ANTHROPIC" + "_API_KEY"
    pat = re.compile("|".join(re.escape(f) for f in (frag_sdk, frag_key)))
    hits = []
    for base in ("scripts", ".github/workflows"):
        root = REPO_ROOT / base
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.name in {"pre-push", "lint.yml"}:
                continue
            try:
                lines = p.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for i, line in enumerate(lines, 1):
                if pat.search(line) and not line.lstrip().startswith("#"):
                    hits.append(f"{p.relative_to(REPO_ROOT)}:{i}: {line.strip()}")
    assert not hits, "Anthropic SDK / API-key references found:\n" + "\n".join(hits)
