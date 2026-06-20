# Job-search tooling — local workflow

Private, local-only tooling that stacks on `src/content/skills.yaml` (the same
source the resume Skills section draws from). Nothing here is public.

## One-time setup (per machine)

The real data lives in a **gitignored** `jobsearch/` directory at the repo
root (`/jobsearch/` is in `.gitignore`), so it never reaches this public repo.
Create it from these templates:

```sh
mkdir -p jobsearch/targets jobsearch/out
cp scripts/templates/jobsearch/target.example.md   jobsearch/targets/my-first-target.md
cp scripts/templates/jobsearch/outreach.example.yaml jobsearch/outreach.yaml
# edit those two files with real (private) details
```

## Commands

```sh
python scripts/build_jobsearch.py            # status + usage
python scripts/build_jobsearch.py matrix     # skill x archetype coverage
python scripts/build_jobsearch.py packet jobsearch/targets/my-first-target.md
python scripts/build_jobsearch.py packet --all
python scripts/build_jobsearch.py outreach   # follow-ups due
python scripts/build_jobsearch.py all        # all of the above

python scripts/lint_jobfit.py                # evidence-gap report (work items)
```

All generated artifacts land in the gitignored `jobsearch/out/`.

## How recency is weighted

Each skill's public proof is dated from the artifact it points at: a blog
post's `publishDate`, or the end year of the resume role it cites (a current
role counts as today; a project card is undated). The freshest proof sets the
skill's recency weight (recent = 1.0, sliding down to 0.25 for proof older
than ten years). Coverage scores in the matrix and packets are weighted by
that factor, and `lint_jobfit.py` flags a skill whose only proof is more than
five years old as **stale** — a prompt to refresh the public evidence.

## The stack

`skills.yaml` (committed) → resume Skills line (deferred) + job-fit matrix +
application packets; `outreach.yaml` contacts link back to the skill/project
that motivated the reach-out via `motivating_skill` / `motivating_project`.
