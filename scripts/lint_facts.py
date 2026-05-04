#!/usr/bin/env python3
"""lint_facts.py

Cross-surface fact lint. Enforces consistency between three surfaces
that name the same employment facts:

  - src/content/resume.md          (canonical Markdown source)
  - index.html h3 + <p class="meta"> blocks (visible homepage chrome)
  - index.html <script type="application/ld+json"> (structured data)

Three assertions:

  1. Current role agreement: the newest entry on resume.md (end =
     "Present") must match the first homepage job block AND the
     JSON-LD jobTitle / worksFor.name. Compared on org, title,
     start date.
  2. Resume orgs subset of homepage orgs: every employer named on
     the resume must also appear on the homepage. The homepage may
     list more entries (it splits Healthfinch / Health Catalyst at
     the 2020 acquisition; the resume condenses).
  3. Exactly one current role per surface: each of resume.md and
     index.html should have exactly one entry whose end date is
     "Present".

When a check fails, see scripts/lint_facts.md for the per-failure
incident-response playbook.

No synonym dictionary, no fuzzy matching. Strict comparison after
canonicalization (parentheticals stripped, first-comma-truncated for
orgs, lowercased). When surfaces disagree, you find out.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from _common import install_git_hooks

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
RESUME = ROOT / "src" / "content" / "resume.md"
INDEX = ROOT / "index.html"
PLAYBOOK_REL = "scripts/lint_facts.md"


@dataclass(frozen=True)
class Job:
    org: str           # canonical: paren-stripped, first-comma-truncated, lowercased
    title: str         # canonical: paren-stripped
    start: str         # "Mon YYYY"
    end: str           # "Mon YYYY" or "Present"
    raw_org: str       # original spelling, for error messages
    raw_title: str
    source_line: int


# ─── canonicalization ─────────────────────────────────────────────────────

PAREN_RE = re.compile(r"\s*\([^)]*\)")


def strip_paren(s: str) -> str:
    return PAREN_RE.sub("", s).strip()


def canonical_org(s: str) -> str:
    base = strip_paren(s).split(",")[0].strip()
    return base.lower()


def canonical_title(s: str) -> str:
    return strip_paren(s).strip()


def html_decode_minimal(s: str) -> str:
    return (s.replace("&amp;", "&")
             .replace("&middot;", "·")
             .replace("&#8212;", "—")
             .replace("&#8211;", "–")
             .replace("&#8853;", "⊕")
             .replace("&lt;", "<")
             .replace("&gt;", ">"))


# ─── resume parser ────────────────────────────────────────────────────────

# **Org** | Title
# Mon YYYY – Mon YYYY      (or "Present" as the end)
RESUME_JOB_RE = re.compile(
    r"^\*\*(?P<org>[^*]+)\*\*\s*\|\s*(?P<title>.+?)\n"
    r"(?P<start>[A-Z][a-z]{2}\s+\d{4})\s*[–-]\s*(?P<end>Present|[A-Z][a-z]{2}\s+\d{4})",
    re.MULTILINE,
)


def parse_resume(text: str) -> list[Job]:
    jobs: list[Job] = []
    for m in RESUME_JOB_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        org = m.group("org").strip()
        title = m.group("title").strip()
        jobs.append(Job(
            org=canonical_org(org),
            title=canonical_title(title),
            start=m.group("start"),
            end=m.group("end"),
            raw_org=org,
            raw_title=title,
            source_line=line,
        ))
    return jobs


# ─── homepage parser ──────────────────────────────────────────────────────

# <h3>Title</h3> ... <p class="meta">Org · Date to Date</p>
# Negative lookahead on <h3> prevents the gap from spanning into the
# next h3 (so project h3s without a meta paragraph don't hijack the match).
HOMEPAGE_JOB_RE = re.compile(
    r"<h3>(?P<title>.+?)</h3>"
    r"(?:(?!<h3>).){0,3000}?"
    r'<p class="meta">(?P<meta>[^<]+)</p>',
    re.DOTALL,
)
H3_TAG_STRIP_RE = re.compile(r"<label\b[^>]*>.*?</label>|<input\b[^>]*/?>", re.DOTALL)
META_SPLIT_RE = re.compile(r"\s*·\s*")
META_DATE_RE = re.compile(
    r"(?P<start>[A-Z][a-z]{2}\s+\d{4})\s+to\s+(?P<end>Present|[A-Z][a-z]{2}\s+\d{4})"
)


def parse_homepage_jobs(text: str) -> list[Job]:
    jobs: list[Job] = []
    for m in HOMEPAGE_JOB_RE.finditer(text):
        title_inner = H3_TAG_STRIP_RE.sub("", m.group("title"))
        title_inner = re.sub(r"<[^>]+>", "", title_inner).strip()
        title_inner = html_decode_minimal(title_inner)

        meta = html_decode_minimal(m.group("meta")).strip()
        parts = META_SPLIT_RE.split(meta)
        if len(parts) < 2:
            continue
        org_raw = parts[0].strip()
        date_part = parts[-1].strip()
        date_match = META_DATE_RE.match(date_part)
        if not date_match:
            continue
        line = text.count("\n", 0, m.start()) + 1
        jobs.append(Job(
            org=canonical_org(org_raw),
            title=canonical_title(title_inner),
            start=date_match.group("start"),
            end=date_match.group("end"),
            raw_org=org_raw,
            raw_title=title_inner,
            source_line=line,
        ))
    return jobs


# ─── JSON-LD parser ───────────────────────────────────────────────────────

JSONLD_RE = re.compile(
    r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
    re.DOTALL,
)


def parse_jsonld(text: str) -> dict | None:
    m = JSONLD_RE.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


# ─── checks ───────────────────────────────────────────────────────────────

def check_current_role(
    resume_jobs: list[Job],
    home_jobs: list[Job],
    jsonld: dict | None,
) -> list[str]:
    failures: list[str] = []
    if not resume_jobs:
        return [
            f"resume.md: no jobs parsed; check format "
            f"(**Org** | Title / Date – Date). Playbook: §G."
        ]
    if not home_jobs:
        return [
            f"index.html: no jobs parsed; check <h3>...</h3> + "
            f'<p class="meta">...</p> structure. Playbook: §G.'
        ]

    rj = resume_jobs[0]
    hj = home_jobs[0]
    if rj.end != "Present":
        failures.append(
            f"resume.md:{rj.source_line}: first role end='{rj.end}' "
            f"(expected 'Present'); newest role must come first. Playbook: §F."
        )
    if hj.end != "Present":
        failures.append(
            f"index.html:{hj.source_line}: first job h3 end='{hj.end}' "
            f"(expected 'Present'); newest job must come first. Playbook: §F."
        )
    if rj.org != hj.org:
        failures.append(
            f"current employer mismatch: resume.md:{rj.source_line} "
            f"says '{rj.raw_org}', index.html:{hj.source_line} "
            f"says '{hj.raw_org}'. Playbook: §A."
        )
    if rj.title != hj.title:
        failures.append(
            f"current title mismatch: resume.md:{rj.source_line} "
            f"says '{rj.raw_title}', index.html:{hj.source_line} "
            f"says '{hj.raw_title}'. Playbook: §B."
        )
    if rj.start != hj.start:
        failures.append(
            f"current start date mismatch: resume.md:{rj.source_line} "
            f"says '{rj.start}', index.html:{hj.source_line} "
            f"says '{hj.start}'. Playbook: §C."
        )

    if jsonld is None:
        failures.append(
            'index.html: no <script type="application/ld+json"> block '
            "found (or invalid JSON). Playbook: §D."
        )
    else:
        ld_org_raw = (jsonld.get("worksFor") or {}).get("name", "")
        ld_title_raw = jsonld.get("jobTitle", "")
        ld_org = canonical_org(ld_org_raw)
        ld_title = canonical_title(ld_title_raw)
        if ld_org and ld_org != rj.org:
            failures.append(
                f"JSON-LD worksFor.name='{ld_org_raw}' does not match "
                f"resume current employer '{rj.raw_org}'. Playbook: §D."
            )
        if ld_title and ld_title != rj.title:
            failures.append(
                f"JSON-LD jobTitle='{ld_title_raw}' does not match "
                f"resume current title '{rj.raw_title}'. Playbook: §D."
            )
    return failures


def check_orgs_subset(resume_jobs: list[Job], home_jobs: list[Job]) -> list[str]:
    home_orgs = {j.org for j in home_jobs}
    if not home_orgs:
        return []  # already reported by check_current_role
    failures: list[str] = []
    for j in resume_jobs:
        if j.org not in home_orgs:
            failures.append(
                f"resume.md:{j.source_line}: employer '{j.raw_org}' on "
                f"resume but not on homepage (homepage has: "
                f"{sorted(home_orgs)}). Playbook: §E."
            )
    return failures


def check_single_present(resume_jobs: list[Job], home_jobs: list[Job]) -> list[str]:
    failures: list[str] = []
    rp = [j for j in resume_jobs if j.end == "Present"]
    hp = [j for j in home_jobs if j.end == "Present"]
    if resume_jobs and len(rp) != 1:
        failures.append(
            f"resume.md: expected exactly 1 'Present' role, found "
            f"{len(rp)}: {[j.raw_org for j in rp]}. Playbook: §F."
        )
    if home_jobs and len(hp) != 1:
        failures.append(
            f"index.html: expected exactly 1 'Present' role, found "
            f"{len(hp)}: {[j.raw_org for j in hp]}. Playbook: §F."
        )
    return failures


# ─── main ─────────────────────────────────────────────────────────────────

def main() -> int:
    if not RESUME.exists():
        print(f"error: {RESUME} not found", file=sys.stderr)
        return 1
    if not INDEX.exists():
        print(f"error: {INDEX} not found", file=sys.stderr)
        return 1

    resume_text = RESUME.read_text(encoding="utf-8")
    index_text = INDEX.read_text(encoding="utf-8")

    resume_jobs = parse_resume(resume_text)
    home_jobs = parse_homepage_jobs(index_text)
    jsonld = parse_jsonld(index_text)

    all_failures: list[str] = []
    all_failures += check_current_role(resume_jobs, home_jobs, jsonld)
    all_failures += check_orgs_subset(resume_jobs, home_jobs)
    all_failures += check_single_present(resume_jobs, home_jobs)

    if all_failures:
        print("Cross-surface fact lint found drift:\n", file=sys.stderr)
        for f in all_failures:
            print(f"  {f}", file=sys.stderr)
        print(
            f"\n{len(all_failures)} fact drift(s) across resume.md / "
            f"index.html / JSON-LD. See {PLAYBOOK_REL} for the playbook.",
            file=sys.stderr,
        )
        return 1

    print(
        f"facts lint: {len(resume_jobs)} resume role(s) + "
        f"{len(home_jobs)} homepage job block(s) consistent"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
