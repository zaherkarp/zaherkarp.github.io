#!/usr/bin/env python3
"""lint_facts.py

Cross-surface fact lint. Enforces consistency between the surfaces
that name the same employment facts:

  - src/content/resume.md          (canonical Markdown source)
  - src/content/cv.md              (the longer-form companion source)
  - index.html h3 + <p class="meta"> blocks (visible homepage chrome)
  - index.html <script type="application/ld+json"> (structured data)

Assertions:

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
  4. CV / resume agreement (when cv.md exists): the CV's current role
     must match the resume's, the CV must have exactly one "Present"
     role, and every resume employer must also appear on the CV (the
     CV is the comprehensive surface).

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
CV = ROOT / "src" / "content" / "cv.md"
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
# Title comma-fold: collapse the first " of " or ", " in a title to a uniform
# marker. "Manager of Data Science and Engineering" and "Manager, Data Science
# and Engineering" are the same role written two ways; this lets surfaces pick
# their preferred register without forcing one wording.
TITLE_FOLD_RE = re.compile(r"\s+of\s+|,\s+", re.IGNORECASE)


def strip_paren(s: str) -> str:
    return PAREN_RE.sub("", s).strip()


def canonical_org(s: str) -> str:
    base = strip_paren(s).split(",")[0].strip()
    return base.lower()


def canonical_title(s: str) -> str:
    base = strip_paren(s).strip()
    return TITLE_FOLD_RE.sub(" :: ", base, count=1)


def cv_appt_title(body: str) -> str:
    """Extract just the title from a CV Appointments line body.

    Body shape: "Org [(paren)], Title. Optional scope sentence."
    """
    cleaned = strip_paren(body)
    if "," not in cleaned:
        return ""
    _, rest = cleaned.split(",", 1)
    return rest.split(".", 1)[0].strip()


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


# ─── CV appointments parser ───────────────────────────────────────────────

# The CV (cv.md) is a traditional academic document: appointments live in an
# "## Appointments" section as a year-gutter list, one entry per line:
#   - **2025–present** Org, Title. Optional scope sentence.
# Year-only ranges (not month precision), so we compare on employer + the
# single "present" role, not on start dates or titles.
CV_APPT_SECTION_RE = re.compile(
    r"^##\s+Appointments\s*$(?P<body>.*?)(?=^##\s|\Z)",
    re.DOTALL | re.MULTILINE,
)
CV_APPT_LINE_RE = re.compile(
    r"^-\s+\*\*(?P<range>[^*]+)\*\*\s+(?P<body>.+?)\s*$",
    re.MULTILINE,
)


def parse_cv_appointments(text: str) -> list[Job]:
    """Parse the CV's Appointments list into Jobs (newest first by file order)."""
    sec = CV_APPT_SECTION_RE.search(text)
    if not sec:
        return []
    base = sec.start("body")
    jobs: list[Job] = []
    for m in CV_APPT_LINE_RE.finditer(sec.group("body")):
        rng = m.group("range").strip()
        body = m.group("body").strip()
        end = "Present" if "present" in rng.lower() else rng
        line = text.count("\n", 0, base + m.start()) + 1
        title_str = cv_appt_title(body)
        jobs.append(Job(
            org=canonical_org(body),
            title=canonical_title(title_str) if title_str else "",
            start="",
            end=end,
            raw_org=body.split(",")[0].strip(),
            raw_title=title_str or body,
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


def check_cv_against_resume(
    resume_jobs: list[Job], cv_jobs: list[Job], cv_text: str
) -> list[str]:
    """CV / resume employer agreement.

    The CV is a traditional academic document. Its "## Appointments" section
    holds the professional (industry) appointments as a year-gutter list
    (year-only ranges, no month precision or stack lines); earlier academic
    roles live under "## Past Research Positions". So we check: the CV's
    current ("present") appointment matches the resume's current employer,
    the Appointments list has exactly one "present" entry, and every resume
    employer appears somewhere in the CV (the CV is the comprehensive
    surface, so it must mention them all, whether under Appointments or
    Past Research Positions).
    """
    if not cv_jobs:
        return [
            "cv.md: no appointments parsed; check the '## Appointments' "
            "list format (- **YYYY–present** Org, Title.). Playbook: §G."
        ]
    failures: list[str] = []

    cp = [j for j in cv_jobs if j.end == "Present"]
    if len(cp) != 1:
        failures.append(
            f"cv.md: expected exactly 1 'present' appointment, found "
            f"{len(cp)}: {[j.raw_org for j in cp]}. Playbook: §F."
        )

    if resume_jobs:
        rj = resume_jobs[0]
        cj = cv_jobs[0]
        if cj.end != "Present":
            failures.append(
                f"cv.md:{cj.source_line}: first appointment end='{cj.end}' "
                f"(expected 'present'); newest must come first. Playbook: §F."
            )
        if rj.org != cj.org:
            failures.append(
                f"current employer mismatch: resume.md:{rj.source_line} "
                f"says '{rj.raw_org}', cv.md:{cj.source_line} "
                f"says '{cj.raw_org}'. Playbook: §A."
            )
        if cj.title and rj.title != cj.title:
            failures.append(
                f"current title mismatch: resume.md:{rj.source_line} "
                f"says '{rj.raw_title}', cv.md:{cj.source_line} "
                f"says '{cj.raw_title}'. Playbook: §B."
            )

    haystack = cv_text.lower()
    for j in resume_jobs:
        if j.org not in haystack:
            failures.append(
                f"resume.md:{j.source_line}: employer '{j.raw_org}' on "
                f"resume but not found anywhere in cv.md. Playbook: §E."
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
    cv_text = CV.read_text(encoding="utf-8") if CV.exists() else None
    cv_jobs = parse_cv_appointments(cv_text) if cv_text is not None else None

    all_failures: list[str] = []
    all_failures += check_current_role(resume_jobs, home_jobs, jsonld)
    all_failures += check_orgs_subset(resume_jobs, home_jobs)
    all_failures += check_single_present(resume_jobs, home_jobs)
    if cv_jobs is not None:
        all_failures += check_cv_against_resume(resume_jobs, cv_jobs, cv_text)

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

    cv_note = f" + {len(cv_jobs)} cv role(s)" if cv_jobs is not None else ""
    print(
        f"facts lint: {len(resume_jobs)} resume role(s) + "
        f"{len(home_jobs)} homepage job block(s){cv_note} consistent"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
