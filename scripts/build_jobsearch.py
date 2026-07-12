#!/usr/bin/env python3
"""build_jobsearch.py — private, local-only job-search driver.

Stacks onto the same skills.yaml source the resume draws from, so one skill
declaration feeds the resume, the job-fit matrix, the application packets, and
(via the outreach FK) the contact tracker.

Subcommands:
  matrix              Write the skill x archetype coverage matrix.
  packet <target.md>  Write a tailored application brief for one target.
  packet --all        A packet for every jobsearch/targets/*.md.
  outreach            Write the "follow-ups due" digest from outreach.yaml.
  all                 matrix + packet --all + outreach (skips absent inputs).
  (no subcommand)     Print local status + usage.

Coverage is RECENCY-WEIGHTED: a want met by a skill last shown years ago
counts for less than one shown recently (see lint_jobfit.recency_weight).

Privacy: reads the committed skills.yaml + public artifacts, plus the
GITIGNORED jobsearch/ data (targets, outreach.yaml). Writes ONLY into the
gitignored jobsearch/out/. It never touches a tracked file and never errors on
absent private data, so it is safe to run on a fresh clone (it still produces
the matrix from committed inputs) and is intentionally never wired into CI.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import frontmatter
import yaml

from _common import coerce_date, install_git_hooks
from _skills import (
    SKILLS_YAML,
    load_skills,
    match_want,
    render_jobfit_matrix,
    skill_matches_want,
)
from lint_jobfit import (
    proven_ids,
    recency_weight,
    resolve_skills,
    scan_artifacts,
)

install_git_hooks()

ROOT = Path(__file__).resolve().parent.parent
JOBSEARCH = ROOT / "jobsearch"
TARGETS = JOBSEARCH / "targets"
OUT = JOBSEARCH / "out"
OUTREACH = JOBSEARCH / "outreach.yaml"
TEMPLATES = ROOT / "scripts" / "templates" / "jobsearch"

DUE_STATUSES = {"open", "waiting"}


# ─── shared analysis ───────────────────────────────────────────────────────

def _analyze():
    """Load skills + resolve evidence once; return everything the commands
    need: (data, skills, info, proven, weights, today)."""
    data = load_skills()
    skills = data["skills"]
    today = date.today()
    artifacts = scan_artifacts(today)
    info = resolve_skills(skills, artifacts)
    proven = proven_ids(info)
    weights = {sid: recency_weight(i, today) for sid, i in info.items()}
    return data, skills, info, proven, weights, today


def _write_out(name: str, text: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text(text, encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}")
    return path


def _evidence_line(info_one: dict) -> str:
    refs = []
    for kind, ref, when in info_one["resolved"]:
        yr = f" {when.year}" if when else ""
        refs.append(f"{kind}:{ref}{yr}")
    return ", ".join(refs) if refs else "(no public proof)"


# ─── matrix ────────────────────────────────────────────────────────────────

def cmd_matrix() -> int:
    if not SKILLS_YAML.exists():
        print(f"  skills.yaml absent ({SKILLS_YAML}); nothing to render")
        return 0
    data, _skills, _info, proven, weights, _today = _analyze()
    md = render_jobfit_matrix(data, proven, weights)
    _write_out("jobfit-matrix.md", md)
    return 0


# ─── packet ────────────────────────────────────────────────────────────────

def _coverage_rows(skills, wantlist, info, today):
    rows = []
    for w in wantlist:
        m = match_want(skills, w)
        if m is None:
            rows.append({"want": w, "skill": None, "weight": 0.0, "proven": False})
        else:
            i = info[m["id"]]
            rows.append({
                "want": w, "skill": m,
                "weight": recency_weight(i, today), "proven": i["proven"],
            })
    return rows


def _section(title, rows, info):
    out = [f"### {title}", ""]
    if not rows:
        out.append("_none listed_")
        out.append("")
        return out
    matched = [r for r in rows if r["skill"]]
    weighted = sum(r["weight"] for r in rows)
    total = len(rows)
    out.append(f"Coverage: {len(matched)}/{total} matched, "
               f"recency-weighted {weighted:.1f}/{total} "
               f"({round(100 * weighted / total)}%).")
    out.append("")
    for r in rows:
        if not r["skill"]:
            out.append(f"- [ ] **{r['want']}** — GAP, no matching skill")
            continue
        tag = "proven" if r["proven"] else "UNPROVEN"
        line = (f"- [x] **{r['want']}** → {r['skill']['name']} "
                f"({tag}, recency {r['weight']:.2f})")
        if r["proven"]:
            line += f"\n      cite: {_evidence_line(info[r['skill']['id']])}"
        out.append(line)
    out.append("")
    return out


def _render_packet(meta, body, skills, info, today) -> str:
    label = meta.get("title", meta.get("id", "target"))
    out = [f"# Application packet: {label}", ""]
    out.append("Private; generated by `scripts/build_jobsearch.py packet`. "
               "Do not commit.")
    out.append("")
    for k in ("company", "title", "status", "source", "url"):
        if meta.get(k):
            out.append(f"- **{k}:** {meta[k]}")
    out.append("")

    must = meta.get("must_have") or []
    wants = meta.get("wants") or []
    nice = meta.get("nice_to_have") or []

    mh_rows = _coverage_rows(skills, must, info, today)
    w_rows = _coverage_rows(skills, wants, info, today)
    n_rows = _coverage_rows(skills, nice, info, today)

    all_rows = mh_rows + w_rows
    weighted = sum(r["weight"] for r in all_rows)
    total = len(all_rows) or 1
    matched = [r for r in all_rows if r["skill"]]
    mh_gaps = [r["want"] for r in mh_rows if not r["skill"]]

    out.append("## Fit summary")
    out.append("")
    out.append(f"- Matched: {len(matched)}/{len(all_rows)} "
               "(must-have + wants)")
    out.append(f"- Recency-weighted coverage: {round(100 * weighted / total)}%")
    if mh_gaps:
        out.append(f"- **Must-have gaps: {', '.join(mh_gaps)}**")
    else:
        out.append("- Must-have gaps: none")
    out.append("")

    out.append("## Coverage detail")
    out.append("")
    out += _section("Must-have", mh_rows, info)
    out += _section("Wants", w_rows, info)
    if nice:
        out += _section("Nice-to-have", n_rows, info)

    # Extra skills the free-text JD body mentions but the want-lists missed.
    named = {r["skill"]["id"] for r in all_rows + n_rows if r["skill"]}
    body_low = (body or "").lower()
    extra = []
    for s in skills:
        if s["id"] in named:
            continue
        cands = [s["name"]] + list(s.get("aliases") or [])
        if any(len(c) >= 3 and c.lower() in body_low for c in cands):
            extra.append(s)
    if extra:
        out.append("## Also mentioned in the description")
        out.append("")
        for s in extra:
            i = info[s["id"]]
            tag = "proven" if i["proven"] else "UNPROVEN"
            out.append(f"- {s['name']} ({tag}, recency "
                       f"{recency_weight(i, today):.2f})")
        out.append("")
    return "\n".join(out) + "\n"


def cmd_packet(target: str | None, do_all: bool) -> int:
    if do_all:
        files = sorted(TARGETS.glob("*.md")) if TARGETS.is_dir() else []
        if not files:
            print(f"  no targets in {TARGETS.relative_to(ROOT)}/ "
                  f"(copy {TEMPLATES.relative_to(ROOT)}/target.example.md to start)")
            return 0
    elif target:
        tp = Path(target)
        if not tp.is_absolute():
            tp = ROOT / target
        if not tp.exists():
            print(f"  target not found: {target}")
            return 0
        files = [tp]
    else:
        print("  usage: build_jobsearch.py packet <target.md> | --all")
        return 0

    _data, skills, info, _proven, _weights, today = _analyze()
    for f in files:
        fm = frontmatter.load(f)
        md = _render_packet(fm.metadata, fm.content, skills, info, today)
        slug = fm.metadata.get("id") or f.stem
        _write_out(f"packet-{slug}.md", md)
    return 0


# ─── outreach ──────────────────────────────────────────────────────────────

def cmd_outreach() -> int:
    if not OUTREACH.exists():
        print(f"  {OUTREACH.relative_to(ROOT)} absent "
              f"(copy {TEMPLATES.relative_to(ROOT)}/outreach.example.yaml to start)")
        return 0
    with OUTREACH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    contacts = data.get("contacts") or []
    today = date.today()

    due = []
    for c in contacts:
        nf = coerce_date(c.get("next_followup"))
        status = str(c.get("status", "")).lower()
        if nf and status in DUE_STATUSES and nf <= today:
            due.append((nf, c))
    due.sort(key=lambda t: t[0])

    out = ["# Follow-ups due", ""]
    out.append("Private; generated by `scripts/build_jobsearch.py outreach`. "
               "Do not commit.")
    out.append("")
    if not due:
        out.append(f"_No follow-ups due as of {today.isoformat()}._")
    else:
        out.append(f"As of {today.isoformat()}, {len(due)} due:")
        out.append("")
        for nf, c in due:
            overdue = (today - nf).days
            when = "today" if overdue == 0 else f"{overdue}d overdue"
            head = f"- **{c.get('name', '?')}**"
            if c.get("org"):
                head += f", {c['org']}"
            if c.get("role"):
                head += f" ({c['role']})"
            head += f" — due {nf.isoformat()} ({when})"
            out.append(head)
            link = []
            if c.get("motivating_skill"):
                link.append(f"skill: {c['motivating_skill']}")
            if c.get("motivating_project"):
                link.append(f"project: {c['motivating_project']}")
            if c.get("channel"):
                link.append(f"via {c['channel']}")
            if link:
                out.append(f"    - {' · '.join(link)}")
            history = c.get("history") or []
            if history:
                last = history[-1]
                ld = coerce_date(last.get("date"))
                out.append(f"    - last: {ld.isoformat() if ld else '?'} "
                           f"{last.get('kind', '')} {last.get('note', '')}".rstrip())
        out.append("")
    _write_out("followups-due.md", "\n".join(out) + "\n")
    return 0


# ─── status / all ──────────────────────────────────────────────────────────

def cmd_status() -> int:
    print("build_jobsearch.py — private job-search tooling")
    if SKILLS_YAML.exists():
        n = len(load_skills()["skills"])
        print(f"  skills.yaml: {n} skills (committed source)")
    else:
        print("  skills.yaml: ABSENT")
    n_targets = len(list(TARGETS.glob("*.md"))) if TARGETS.is_dir() else 0
    print(f"  jobsearch/ data: targets={n_targets}, "
          f"outreach.yaml={'yes' if OUTREACH.exists() else 'no'} "
          f"(gitignored, local-only)")
    print("  commands: matrix | packet <t>|--all | outreach | all")
    print(f"  templates to copy: {TEMPLATES.relative_to(ROOT)}/")
    return 0


def cmd_all() -> int:
    print("matrix:")
    cmd_matrix()
    print("packets:")
    cmd_packet(None, do_all=True)
    print("outreach:")
    cmd_outreach()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Private job-search driver.")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("matrix")
    p_packet = sub.add_parser("packet")
    p_packet.add_argument("target", nargs="?")
    p_packet.add_argument("--all", action="store_true", dest="do_all")
    sub.add_parser("outreach")
    sub.add_parser("all")
    args = parser.parse_args(argv)

    if args.cmd == "matrix":
        return cmd_matrix()
    if args.cmd == "packet":
        return cmd_packet(args.target, args.do_all)
    if args.cmd == "outreach":
        return cmd_outreach()
    if args.cmd == "all":
        return cmd_all()
    return cmd_status()


if __name__ == "__main__":
    sys.exit(main())
