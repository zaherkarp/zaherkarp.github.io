"""Shared helpers for scripts in this directory.

Exposes install_git_hooks(), called at the top of each project script so a
fresh clone wires up the pre-push hook automatically without a manual setup
step, and slugify_tag(), the single source of truth for turning a blog tag
into the URL slug used by the per-tag archive pages (blog/tags/<slug>/).
Both build_blog.py (which emits the pages) and build_portfolio.py (which
links to them from the homepage cadence rollup) import slugify_tag so the
two surfaces can never disagree on a slug.

Also exposes the cross-surface alignment matcher (years_of / tokens_of /
token_overlap / alignment_match) and the homepage .row-entry field parser,
the single source of truth now shared by lint_recognition.py, lint_gantt.py,
and lint_jobfit.py. Each lint passes its OWN stoplist to tokens_of (the
`stop` parameter is required), so the stoplists stay per-lint and their
matching behavior is unchanged.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR_REL = "scripts/hooks"

# Any run of non-alphanumeric characters collapses to a single hyphen, so
# "Medicare Stars" / "medicare-stars" / "Medicare  Stars" all slug to
# "medicare-stars" and "CI/CD" slugs to "ci-cd". Tags that differ only in
# case or separator therefore share one tag page, which is the intended
# merge; genuinely different tags ("medicare" vs "medicare-stars") stay
# separate.
_TAG_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify_tag(tag: str) -> str:
    """Normalize a blog tag to its URL slug (lowercase, hyphen-separated)."""
    return _TAG_SLUG_RE.sub("-", str(tag).strip().lower()).strip("-")


# ─── cross-surface alignment matcher ───────────────────────────────────────
# The single home for the year + token machinery shared by lint_recognition,
# lint_gantt, and lint_jobfit. `stop` is a REQUIRED parameter (no default), so
# each lint passes its own stoplist explicitly and one caller's tuning can
# never silently shift another's -- the reason the three keep distinct STOP
# sets while sharing this code.

_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_NON_TOKEN_RE = re.compile(r"[^a-z0-9]+")


def years_of(s: str) -> set[int]:
    """The four-digit 19xx/20xx years mentioned in a string."""
    return {int(m.group()) for m in _YEAR_RE.finditer(s)}


def tokens_of(s, stop, *, min_len=3, normalize=None):
    """Significant lowercase tokens in `s`.

    Splits on non-alphanumerics, drops tokens shorter than `min_len`, pure
    digits (years are handled by years_of), and anything in `stop`. `stop` is
    required so each call site states its own stoplist explicitly. `normalize`
    is an optional pre-pass (e.g. HTML-entity decoding) applied before casefold.
    """
    if normalize is not None:
        s = normalize(s)
    out: set[str] = set()
    for t in _NON_TOKEN_RE.split(s.lower()):
        if len(t) < min_len or t.isdigit() or t in stop:
            continue
        out.add(t)
    return out


def token_overlap(a, b, *, min_shared=2) -> bool:
    """True if token sets `a` and `b` share at least `min_shared` members.

    The year-free predicate, for surfaces that do not both carry dates (a
    skill vs. a job description). lint_jobfit / packet matching use this; the
    recognition/gantt lints use alignment_match below.
    """
    return len(a & b) >= min_shared


def alignment_match(a_years, a_tokens, b_years, b_tokens, *, min_shared=2) -> bool:
    """Year overlap AND >= min_shared shared tokens.

    The recognition/gantt predicate, faithfully extracted for reuse. Requires
    both sides to share a year, so it suits dated-vs-dated surfaces only.
    """
    if not (a_years & b_years):
        return False
    return token_overlap(a_tokens, b_tokens, min_shared=min_shared)


# ─── homepage .row-entry field parser ──────────────────────────────────────
# Both lint_recognition and lint_gantt read the homepage #service / #education
# <div class="row-entry"> blocks with the same four regexes and field getter.
# Shared here so the .row-entry contract has one update point; each lint still
# owns its own section slicing (the CV-markdown vs HTML-section difference).

ROW_ENTRY_RE = re.compile(
    r'<div class="row-entry">(?P<row>.*?)</div>\s*</div>', re.DOTALL
)
ROW_DATE_RE = re.compile(r'<div class="row-date">(?P<v>[^<]*)</div>')
ROW_TITLE_RE = re.compile(r'<span class="row-title">(?P<v>[^<]*)</span>')
ROW_ORG_RE = re.compile(r'<span class="row-org">(?P<v>[^<]*)</span>')


def row_field(pattern: re.Pattern, row: str) -> str:
    """The captured `v` group of `pattern` in `row`, or "" if absent."""
    m = pattern.search(row)
    return m.group("v") if m else ""


def install_git_hooks() -> None:
    """Point git's core.hooksPath at scripts/hooks/ if it is unset.

    Idempotent. Silently no-ops outside a git work tree (tarball, CI
    sparse checkout, missing git binary). Prints a one-line notice on
    first install so the user knows hooks are now active.

    Polite: if core.hooksPath is already set to a DIFFERENT value (the
    user's own hooks, a pre-commit framework, etc.), it is NOT clobbered.
    We print how to opt in and leave their config alone, so running a
    build never silently hijacks a contributor's git setup. The CI
    backstop (.github/workflows/lint.yml) is the real gate regardless,
    so a machine that declines the local hook still cannot push drift.
    """
    hooks_dir = REPO_ROOT / HOOKS_DIR_REL
    if not hooks_dir.is_dir():
        return
    try:
        current = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        existing = current.stdout.strip()
        if existing == HOOKS_DIR_REL:
            return
        if existing:
            print(
                f"hooks: core.hooksPath is already set to {existing!r}; "
                f"leaving it as-is. To enable this project's pre-push lint "
                f"gate, run: git config core.hooksPath {HOOKS_DIR_REL}",
                file=sys.stderr,
            )
            return
        result = subprocess.run(
            ["git", "config", "core.hooksPath", HOOKS_DIR_REL],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return
    if result.returncode == 0:
        print(
            f"hooks: installed (core.hooksPath -> {HOOKS_DIR_REL}); "
            "pre-push checks now active",
            file=sys.stderr,
        )
