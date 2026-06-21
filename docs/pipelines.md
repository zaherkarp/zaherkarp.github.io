# Pipelines, content model, and how to add things

The reference for *how this site is built*: every pipeline, the content
model that feeds them, how the pieces relate, and a cookbook for adding
each kind of content.

This document is navigational and conceptual. It does **not** restate the
locked design tokens, palette, or editorial rules — those live in
[CLAUDE.md](../CLAUDE.md) and are authoritative. When a section here says
"see CLAUDE.md §X," that section is the source of truth and this one is the
map. [README.md](../README.md) carries the operator-facing quickstart
(local preview, `scripts/blog` CLI, deploy, analytics); this document is the
architecture behind it.

---

## The thesis

This is a personal portfolio that argues its own competence by construction.

The visible artifact is a Tufte-inspired static site — pure HTML/CSS, no
framework, no bundler, no npm, almost no JavaScript. That austerity is a
claim: the author builds healthcare data systems for a living, and the site
demonstrates the same discipline it talks about. A motivated reader (a
hiring manager, a peer practitioner, a recruiter in regulated healthcare)
should come away believing the prose because the object delivering it is
itself well-engineered.

The tension that the pipelines resolve: a hand-authored static site drifts.
Facts diverge across the homepage, the resume, and the CV. The publications
list goes stale. A new award lands on the CV but never reaches the homepage.
A blog post ships but the front page never learns about it. The usual fix is
a CMS or a framework — exactly the dependency this site refuses.

So instead the site keeps **one source of truth per fact** and lets small,
single-purpose Python scripts project that truth into the hand-authored
surfaces, then a web of linters *fails the push* when a surface drifts from
its source. The pipelines are the build system; the linters are the type
system. Together they let the site stay hand-authored and pure-HTML at the
surface while behaving like a maintained application underneath.

Three principles fall out of that and recur everywhere below:

1. **One source of truth per fact.** Publications live in one YAML file and
   feed both the homepage and the CV. Recognition lives in `cv.md` and the
   homepage is checked to be a subset. Skills live in one YAML. A fact is
   authored once and projected, never copied.
2. **Generate into markers, never hand-edit generated regions.** Build
   scripts splice output between `<!-- name:start --> ... <!-- name:end -->`
   comment pairs in otherwise hand-authored files. The surrounding prose
   stays human; the marked region is owned by a script and overwritten on
   the next run.
3. **Lint the drift you can't prevent.** Where two surfaces are authored
   independently for editorial reasons (homepage voice vs. CV completeness),
   a linter reconciles them on every push instead of a shared data file.

Everything that follows is an application of those three ideas.

---

## Concepts and their relation

### Sources of truth

Every fact on the site traces to exactly one of these:

| Source | Feeds | Authoritative for |
| --- | --- | --- |
| `src/content/blog/*.md` | blog pages, homepage writing list, sparkline, life-in-weeks "thoughts", sitemap, feed | every blog post + its metadata |
| `src/content/publications.yaml` | homepage Publications block, CV Publications section, citation snapshots | the publication list + cached citation counts |
| `src/content/resume.md` | `resume.pdf`, `resume.html` | the 1–2 page resume |
| `src/content/cv.md` | `cv.pdf`, `cv.html`; the reconciliation target for recognition/facts lints | the comprehensive academic record |
| `src/content/skills.yaml` | the resume's `## Skills` block (regenerated into resume.md, gated by `lint_skills`) + the private job-search tooling (matrix, packets, job-fit report) | the canonical skill list |
| `src/data/cms-ma-pd-stars-2025.csv` | the homepage Star Ratings cliff curve | the CMS rating distribution |
| `index.html` (hand-authored prose + marked regions) | the homepage itself | experience, projects, speaking, service, certifications, the hero |
| `og-default.png` design tokens (inlined in `build_og.py`) | the Open Graph card | the social share image |

Note `index.html` is *both* a hand-authored source (its prose) and a
generated target (its marked regions). That dual role is why it appears on
both sides of the diagram below.

### Three kinds of script

- **Generators** (`build_*.py`) read a source and write an output — either
  whole files (`blog/`, the PDFs) or marked regions inside a hand-authored
  file (the homepage insertions).
- **Guards** (`lint_*.py`) read sources and outputs and *refuse the push* if
  a rule is violated. They write nothing.
- **Shared libraries** (`_common.py`, `_publications.py`, `_skills.py`,
  `redundancy.py`) hold the logic two or more of the above share, so there's
  one notion of "a publication," "a skill," "is this push CLI-linted."

### The marker-injection pattern

Generators that target hand-authored files never rewrite the whole file.
They locate a `start`/`end` comment pair and replace only what's between it:

```
<!-- activity-grid:start -->   …24-dot writing sparkline…        <!-- activity-grid:end -->
<!-- writing-list:start -->    …2 featured posts…                <!-- writing-list:end -->
<!-- writing-index:start -->   …6 tile posts…                    <!-- writing-index:end -->
<!-- pub-list:start -->        …Publications block…              <!-- pub-list:end -->
<!-- cliff-path:start -->      …Star Ratings density SVG path…   <!-- cliff-path:end -->
// blog-thoughts:start         …💭 dots in life-in-weeks EVENTS… // blog-thoughts:end
<!-- publications -->          …(single placeholder in cv.md)…
```

Rule: **never hand-edit between a start/end pair.** The next build
overwrites it. Edit the *source* (the YAML, the blog frontmatter, the CSV)
and re-run the generator. The lint-notes pipeline explicitly exempts these
regions from its additivity checks for the same reason.

### CI choreography and the commit-back loop

The build pipelines run in GitHub Actions and **commit their output back to
`main`** using the `github-actions[bot]` identity. The runner needs
Settings → Actions → Workflow permissions → **Read and write** for this to
work (see README §Deploy).

A single push can trigger two workflows that both commit to `main` (a blog
push fires both `build_blog.yml` and `build_portfolio.yml`).
`build_portfolio.yml` therefore rebases-and-retries if it loses the race.

A bot `GITHUB_TOKEN` push does **not** re-trigger workflows (GitHub's
anti-recursion rule). Two consequences shape the rest of the design:

- **The citation → CV handoff can't chain on a commit.** `build_portfolio`
  refreshes citation counts into `publications.yaml` weekly, and the CV
  needs those fresh counts. Since portfolio's commit can't fire
  `build_resume`, the dependency is wired as a **`workflow_run` edge**:
  `build_resume` runs when `build_portfolio` *completes*, gated to a
  succeeded scheduled (weekly) **or manually dispatched** portfolio run.
  That makes the ordering a real edge, not a wall-clock guess (the earlier
  design used a 07:00 cron that hoped portfolio had finished by 07:00). The
  gate excludes the frequent push-triggered portfolio runs so they don't
  churn the timestamped resume/CV PDFs; allowing `workflow_dispatch`
  through also makes the chain rehearsable on demand (manually run Build
  portfolio → the CV rebuild chains off it). Note `workflow_run` triggers
  always run the **default-branch** workflow file, so this edge can only be
  exercised after the change is on `main`, never from a PR branch.
- **Bot-committed output isn't seen by the push-triggered lint.** The lint
  that runs on your source push lints the *pre-build* tree; the generated
  output the bot commits afterward doesn't re-trigger anything. So
  `lint.yml` also carries a **weekly `schedule:`** that audits whatever is
  actually on `main`, bot commits included.

### The dependency map

```
  SOURCES (authored once)                GENERATORS              OUTPUTS (committed back)
  ─────────────────────────              ──────────              ────────────────────────
  src/content/blog/*.md ──┬────────────▶ build_blog    ───────▶ blog/<slug>/, blog/index.html,
                          │                                     blog/archive/, blog/feed.xml,
                          │                                     sitemap.xml
                          │
                          ├────────────▶ build_portfolio ─────▶ index.html  (sparkline,
                          │              (+ publications.yaml)   writing list, pub block),
                          │                                     life-in-weeks/index.html (💭),
                          │                                     data/snapshots/<date>.json
                          │
                          └───────────── (read by lints + jobfit)

  src/content/resume.md ──┬────────────▶ build_resume ───────▶ resume.pdf, resume.html
  src/content/cv.md ──────┤              (+ publications.yaml   cv.pdf, cv.html
  publications.yaml ──────┘               via _publications)

  src/data/…stars…csv ─────────────────▶ build_cliff ────────▶ index.html (cliff SVG path)
  (inlined tokens) ────────────────────▶ build_og ───────────▶ og-default.png
  skills.yaml + jobsearch/ (gitignored) ▶ build_jobsearch ────▶ jobsearch/out/ (gitignored)

  GUARDS (write nothing; fail the push / build)
  ─────────────────────────────────────────────
  lint.yml (CI) ─▶ ALL eight linters + grep guards, on every PR + push,
                   unconditionally (the server-side backstop)
  pre-push hook ─▶ lint_blog · lint_vocab · lint_facts · lint_notes ·
                   lint_recognition · lint_gantt · lint_markers ·
                   lint_skills + grep guards
  CI (build_blog) ─▶ lint_vocab · lint_blog   (before build; trailer can skip)
  manual only ─▶ lint_jobfit   (informational, always exits 0)
```

---

## The build pipelines

Nine pipelines stand behind the static surface. Five are wired to CI; four
are run by hand. Each section gives source → output → trigger → what it does.

### 1. Blog — `scripts/build_blog.py`

- **Source:** `src/content/blog/*.md` (markdown + YAML frontmatter)
- **Output:** `blog/<slug>/index.html`, `blog/index.html`,
  `blog/archive/index.html`, `blog/feed.xml`, `sitemap.xml`
- **CI:** `.github/workflows/build_blog.yml` — push under
  `src/content/blog/**`, `scripts/**`, or the workflow; plus
  `workflow_dispatch`. Runs `lint_vocab.py` then `lint_blog.py` first;
  either failure aborts the build.

markdown-it-py + mdit-py-plugins + Jinja2 + python-frontmatter. Math
(`\(...\)` / `\[...\]`) is stashed before parsing and restored verbatim for
client-side KaTeX (dollar signs stay currency). Fenced ` ```mermaid `
blocks become `<pre class="mermaid">`. Posts split at the 2019 archive
cutoff so the main listing reads as a coherent healthcare-data portfolio;
2009–2011 journalism lands in `/blog/archive/`. Drafts (`draft: true`) and
`_`-prefixed files are skipped. Templates in `scripts/templates/blog/`
(`base.html`, `post.html`, `list.html`, `feed.xml.j2`). Full rules:
CLAUDE.md §Blog pipeline.

### 2. Portfolio — `scripts/build_portfolio.py`

- **Source:** blog frontmatter + `publications.yaml` + `index.html` markers
- **Output:** in-place `index.html` (sparkline, writing list, Publications
  block), `life-in-weeks/index.html` (💭 thought dots), and
  `data/snapshots/<date>.json` on any run where a fresh citation count lands
- **CI:** `.github/workflows/build_portfolio.yml` — push to `index.html`,
  the script, `scripts/requirements.txt`, or blog posts; Sundays 06:00 UTC
  (citation refresh); manual dispatch.

Four insertions:
- `activity-grid` markers → 24-week posting-cadence sparkline (no network).
- `writing-list` / `writing-index` markers → 2 featured posts + 6 tiles.
  Em-dashes stripped on import. Optional `homepageMarginnote` frontmatter
  wraps a ⊕ margin note on featured entries only.
- `pub-list` markers → the Publications block, rendered by
  `_publications.render_homepage_entries()` from `publications.yaml`,
  including a Semantic Scholar citation count per entry with a `sid`.
- `blog-thoughts` JS markers in life-in-weeks → one 💭 dot per post.

Semantic Scholar's public tier rate-limits (HTTP 429); the script retries
with backoff and preserves the cached count on failure. To keep a
permanently-broken id from hiding behind the same silence as a transient
429, the build distinguishes failure kinds and emits a GitHub Actions
`::warning::` separating "unresolved" ids (a non-429 error or a 200 with no
count — a likely bad/dropped PMID/DOI to fix) from transient failures (which
the weekly run retries). The YAML holds only the latest count;
`data/snapshots/` accretes the longitudinal series (record-on-change). A
per-entry last-fetch date was deliberately not added — it would force a
weekly `publications.yaml` commit even when no count changed. See CLAUDE.md
§Portfolio pipeline.

### 3. Resume + CV — `scripts/build_resume.py`

- **Source:** `src/content/resume.md`, `src/content/cv.md`,
  `publications.yaml`
- **Output:** `resume.pdf`, `resume.html`, `cv.pdf`, `cv.html`
- **CI:** `.github/workflows/build_resume.yml` — push to either markdown
  source, `publications.yaml`, the templates, the bundled fonts, the script,
  or `_publications.py`; plus a `workflow_run` edge that fires after the
  weekly **Build portfolio** run completes successfully, so the CV picks up
  the citation counts that run just refreshed (see §CI choreography).

One config-driven pipeline emits both documents (the `DOCS` list names each
source, its two templates, and its two outputs). markdown-it-py + Jinja2 +
WeasyPrint. The resume targets 1–2 pages, single-column, ATS-parseable; the
CV is a deliberately multi-page academic document. `cv.md` carries a
`<!-- publications -->` placeholder that the build replaces with the list
rendered from `publications.yaml` (no network — counts come from the YAML
cache). The CV templates duplicate the resume CSS on purpose so the resume
output stays byte-stable. ETBook (MIT) is bundled under
`scripts/fonts/et-book/`. Do not rebuild the PDFs by hand. See CLAUDE.md
§Resume and CV pipeline.

### 4. Cliff curve — `scripts/build_cliff.py` (manual, annual)

- **Source:** `src/data/cms-ma-pd-stars-2025.csv`
- **Output:** `index.html` between `cliff-path` markers
- **Trigger:** none — run by hand after updating the CSV (typically once a
  year when CMS releases the new ratings in October).

Renders the Medicare Advantage Star Rating density curve from the canonical
CMS distribution using a pure-Python Gaussian KDE (stdlib only, no deps).
Geometry is locked to the cliff figure's `600 × 240` viewBox; if that
viewBox or the axis layout in `index.html` changes, update the constants in
the script to match.

### 5. OG image — `scripts/build_og.py` (manual)

- **Source:** design tokens inlined in the script (name, subtitle, domain)
- **Output:** `og-default.png` (1200×630)
- **Trigger:** none — the card is essentially static.

```bash
pip install Pillow
python scripts/build_og.py
```

### 6. Critique — `.github/workflows/critique.yml`

- **Source:** a target file (default `index.html`)
- **Output:** `critiques/critique-<slug>-<YYYY-MM-DD>.md`
- **Trigger:** `workflow_dispatch` (optional `target` input) + monthly cron
  on the 1st. Deliberately **not** push-triggered (avoids a commit loop on
  the artifact).

Runs the six-camp "seance symposium" critique end-to-end via the Claude Code
Action, using `docs/critique/playbook.md` as its prompt and
`docs/critique/methodology.md` as the rubric. It does **not** edit the
target — every finding is a prescription (`APPLY_CHANGES=false`).
Independence contract: no `import anthropic`, no `ANTHROPIC_API_KEY`; it
authenticates via `CLAUDE_CODE_OAUTH_TOKEN`. See CLAUDE.md §Critique
pipeline.

### 7. Site review — `.github/workflows/site-review-*.yml`

A multi-agent feedback + iteration loop that produces *feedback documents*,
not site changes.

- `site-review-publish.yml` — push under `critiques/`, `evaluations/`, or
  `reviews/` (or manual) opens/updates a tracking issue per review batch and
  carries unchecked items forward.
- `site-review-check.yml` — `workflow_dispatch` to flip checklist items on a
  tracking issue.

Operator notes: `scripts/review/README.md` and `reviews/README.md`. The
multi-agent prompts live under `scripts/review/prompts/`. See CLAUDE.md
§Site review workflow.

### 8. Lighthouse — `.github/workflows/lighthouse.yml`

CI-only quality gate (no script, no committed output). Runs on
`pull_request` touching `index.html`, `blog.css`, blog sources, the blog
build, blog templates, or the workflow. Use it to catch accessibility/perf
regressions before merge.

### 9. Job search — `scripts/build_jobsearch.py` (private, local-only)

- **Source:** committed `skills.yaml` + the **gitignored** `jobsearch/`
  directory (`targets/*.md`, `outreach.yaml`)
- **Output:** the **gitignored** `jobsearch/out/` only — never a tracked
  file
- **Trigger:** none, ever — deliberately kept out of CI.

Stacks on the same `skills.yaml` the resume draws from: one skill
declaration feeds the resume Skills section (regenerated into resume.md by
build_resume, gated by `lint_skills`), the job-fit matrix,
the application packets, and (via an FK) the outreach tracker. Coverage is
recency-weighted. Subcommands: `matrix`, `packet <target.md>` / `--all`,
`outreach`, `all`. Safe on a fresh clone (still emits the matrix from
committed inputs; never errors on absent private data). Its companion guard
`lint_jobfit.py` is informational and always exits 0.

---

## The linters (the integrity web)

Guards write nothing; they fail the push or build. Three tiers by where they
run.

**Pre-push hook** (`scripts/hooks/pre-push`, self-installed by
`_common.install_git_hooks()` on first run of any project script):

| Linter | Guards |
| --- | --- |
| `lint_blog.py` | HTML-comment leaks in non-draft posts, fenced code nested in a comment, blockquote-as-Mermaid, blank line inside `<svg>` |
| `lint_vocab.py` | canonical CMS program-name casing (Star Ratings, Medicare Advantage, HEDIS…) across blog, resume, cv, homepage |
| `lint_facts.py` | cross-surface fact drift between `resume.md`, `cv.md`, `index.html` h3+meta, and JSON-LD (playbook: `scripts/lint_facts.md`) |
| `lint_notes.py` | sidenote / margin-note additivity; `homepageMarginnote` additive to title+description; `publications.yaml` `note` free of venue/year repeats |
| `lint_recognition.py` | homepage `#service` ⊆ `cv.md` Awards/Fellowships/Service (year + token overlap, no shared YAML) |
| `lint_gantt.py` | the homepage Education+Service Gantt carries a mark for every `#education` and `#service` entry |
| `lint_markers.py` | the build-time injection markers pair cleanly (no orphan/crossed/nested/unterminated pairs) and are still present, so a stray hand edit can't corrupt a host file or make a generator no-op |
| `lint_skills.py` | resume.md's generated `<!-- skills -->` block equals what `skills.yaml` renders, so the public resume's Skills line can't drift from its source (shared with the private job-fit tooling); `build_resume` regenerates it on main but not on PRs |

Plus grep guards: em-dash-clean chrome (`index.html`, `resume.md`, `cv.md`,
life-in-weeks); accent discipline (`grep -cE -- '--accent|#7a0000'
index.html` ≤ 20); no `<p>`-wrapped SVG children in built `blog/`; critique
independence (no `import anthropic` / `ANTHROPIC_API_KEY`).

**CI backstop** (`.github/workflows/lint.yml`): the **full** suite above
(all eight linters + the four grep guards) runs on every `pull_request`,
every `push` to the default branch, and on a **weekly `schedule:`**
(auditing whatever bot commits have landed on `main`), **unconditionally** —
it never consults the `Blog-CLI-Linted:` redundancy trailer. The pre-push
hook only fires for
contributors who push from a machine that has run a project script (which
installs it); web-UI edits, fresh clones, the `draft: false` bypass, and the
workflows' own bot commits all skip it. `lint.yml` is what makes the
integrity guarantees hold regardless of how a change reaches `main`; the hook
is the fast local echo. A check added to one belongs in the other.

**CI (build)** (`build_blog.yml`): `lint_vocab` then `lint_blog` before the
build (these two can be short-circuited by the redundancy trailer; `lint.yml`
is the unconditional version).

**Manual / informational:** `lint_jobfit.py` (evidence-gap report, always
exits 0), `redundancy.py` (the `Blog-CLI-Linted:` trailer logic that lets
the hook and CI skip lints the `scripts/blog` CLI already ran).

Design note on `lint_recognition` vs `lint_facts`: job surfaces
(`resume.md` ↔ `index.html`) are authored in lockstep, so `lint_facts` uses
strict equality. Recognition surfaces (homepage ↔ CV) are phrased
independently, so `lint_recognition` and `lint_gantt` match on year +
significant-token overlap instead. Don't share their stoplists — see
CLAUDE.md §Recognition alignment lint / §Gantt figure alignment lint.

---

## Cookbook: adding each type

Each recipe names the **one source to edit** and what happens after. Unless
noted, "push" means push to `main`; CI regenerates outputs and commits them
back. Never hand-edit a generated file or a marked region.

### Add a blog post

Use the CLI (full walkthrough in README §Writing blog posts and
`scripts/blog.md`):

```bash
./scripts/blog new "My Post Title"      # scaffolds src/content/blog/my-post-title.md, draft: true
./scripts/blog preview my-post          # browser preview
./scripts/blog publish my-post          # lint, flip draft:false, commit, push
```

`build_blog.yml` renders `/blog/<slug>/` + listing + sitemap + feed;
`build_portfolio.yml` adds it to the homepage sparkline and writing list on
the same push. Optional frontmatter: `homepageMarginnote` (⊕ note on the
featured homepage entry, must be additive to title+description),
`lifeweek_topic` (label for the life-in-weeks 💭 dot), `vocab_exempt` (per-
post non-canonical literals). Direct-edit fallback: drop the `.md` with
`draft: false` and push — CI runs the same linters.

### Add a publication

Edit `src/content/publications.yaml` (see its header for the field
contract). Set `sid` (`PMID:…` / `DOI:…`) and `citations` to track a live
count, or use `links` / `note` for a static entry. Push.
`build_portfolio.yml` regenerates the homepage Publications block (between
`pub-list` markers) and the next CV build picks it up. **Do not** add a
`<div class="pub-entry">` to `index.html` by hand — that region is
generated. Keep the file em-dash-clean; keep `note` free of the venue/year
already in the citation line (`lint_notes` enforces).

### Add a project

Hand-edit `index.html`. Projects use a featured + small-multiples-index
pattern with a CSS counter for the `01`/`02` numbers — **leave each
`<span class="num">` empty**; the number follows DOM order. To add/reorder/
promote/demote, edit the DOM and the digits follow. See CLAUDE.md §Project
numbering and layout for the featured-vs-tile rules and the promotion/
demotion checklist.

### Add a talk / presentation

Hand-edit the homepage Speaking section (`index.html`) and/or `cv.md`
Presentations. There is no pipeline here — it's prose. If the talk is a
recognition-worthy item, it goes through the recognition path below instead.
The Speaking `.stat-num` margin stat (peak-year talks) is hand-authored; only
add margin stats where a genuinely buried number exists.

### Add an award / recognition

Two surfaces, reconciled by two linters:

1. Add the full record to `cv.md` (`## Awards and Honors`,
   `### Fellowships and Training`, or `## Service and Professional
   Activities`).
2. If it should appear publicly, add a `.row-entry` to the homepage
   `<section id="service">` **and** a mark to the Education+Service Gantt
   (`figure.gantt-figure`): compute `x = 90 + (year - 2003) * 19`, add the
   square (`<rect fill="#111">`) or bar (`<line stroke-width="4">`) + label,
   extend the lane/axis if rows run out.
3. Run `python scripts/lint_recognition.py` and `python scripts/lint_gantt.py`.

The homepage is a curated subset of the CV (homepage ⊆ CV), so CV-only items
are fine; a public item with no CV record fails the push. See CLAUDE.md
§Recognition alignment lint and §Gantt figure alignment lint.

### Add a certification

Hand-sync two surfaces (no linter covers this pair): the homepage
`<section id="certifications">` one-line prose list and `cv.md`
`## Certifications`. Keep them in sync by hand. See CLAUDE.md §Recognition
alignment lint (Certifications note).

### Edit the resume or CV

Edit `src/content/resume.md` or `src/content/cv.md` and push;
`build_resume.yml` regenerates all four artifacts. `lint_facts` cross-checks
employer/title/date facts against `index.html`; keep the current ("present")
employer consistent across resume, CV Appointments, and the homepage. Tools
go in `.exp-stack` / stack lines; methods stay in prose (CLAUDE.md §Tool vs
method).

### Add a life-in-weeks milestone

Hand-edit the `EVENTS` array in `life-in-weeks/index.html`. Do **not** edit
between the `// blog-thoughts:start/end` markers — those 💭 dots are
generated from blog frontmatter by `build_portfolio.py`. Milestones are
solid dots; blog thoughts are hollow 💭.

### Refresh citation counts (off-cycle)

`python scripts/build_portfolio.py`, or wait for the Sunday 06:00 UTC cron.
Graceful on rate-limit (keeps cached counts); idempotent. A run that lands a
fresh count writes a `data/snapshots/<date>.json`.

### Refresh the cliff curve (annual)

Update `src/data/cms-ma-pd-stars-<year>.csv` (and the path/markers if the
year changes), then `python scripts/build_cliff.py`. Verify the figure's
viewBox still matches the script constants.

### Run a critique

`workflow_dispatch` on `critique.yml` with an optional `target`, or wait for
the monthly cron. To support a new target *type*, extend **both**
`docs/critique/playbook.md` §Supported targets and
`docs/critique/methodology.md` §Archetype weightings in the same change.

### Add a new generated (marker-injected) region

When a generator gains a new injection point, add the
`<!-- name:start --> ... <!-- name:end -->` pair to the host file **and**
register the name in `PAIR_MARKERS` in `scripts/lint_markers.py` in the same
change. `lint_markers` then guarantees the pair stays balanced and present;
forgetting to register it means the linter won't notice if the pair is later
deleted or crossed.

### Add a skill or job-search target (private)

Add the skill to `src/content/skills.yaml` (committed) — it is the source of
truth for the resume's `## Skills` block too. Then regenerate the resume so
its block matches (`python scripts/build_resume.py`, or let CI do it on
merge); `lint_skills` will fail the push if the committed resume.md block
and `skills.yaml` disagree. Job targets and outreach live in the gitignored
`jobsearch/`. Run `python scripts/build_jobsearch.py all`; outputs land in
the gitignored `jobsearch/out/`. `python scripts/lint_jobfit.py` reports
skills with no public proof (informational).

---

## Local setup

```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt

# Resume/CV also need pango/cairo/glib (macOS):
brew install pango
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib .venv/bin/python scripts/build_resume.py
```

Serve the site with `python3 -m http.server 8765` (no build step for the
main page). See README §Local preview and §Before pushing for the full
smoke-test checklist.
