# zaherkarp.github.io

Personal portfolio site for Zaher Karp. Pure HTML/CSS, no framework, no npm.
The main page has no build step; blog posts, the resume PDF, and portfolio
widgets (activity grid + citation counts) each have a Python build pipeline.

See [docs/pipelines.md](./docs/pipelines.md) for the full architecture: the
site's thesis, every build pipeline and linter, how the content model fits
together, and a cookbook for adding each kind of content. See
[CLAUDE.md](./CLAUDE.md) for design constraints and architectural decisions
that should not drift, including the agent-style workflows (focus-group
simulation, review personas) under §Agent panels.

## Repository shape

```
index.html                  Main portfolio page (inline CSS, Tufte palette)
blog.css                    Shared stylesheet for /blog/
blog/                       Generated blog output — do not hand-edit
resume.pdf                  Generated resume — do not hand-edit
sitemap.xml                 Generated (by build_blog.py)
favicon.svg, og-default.png SEO / social assets
robots.txt, .nojekyll, CNAME GitHub Pages config

star-rating-predictor/      Interactive Medicare Star Rating predictor
                            (inline vanilla JS)
life-in-weeks/              90-year life-in-weeks grid (inline vanilla JS)

src/content/
  blog/*.md                 Blog post sources (frontmatter + markdown)
  resume.md                 Resume source
  cv.md                     Comprehensive academic CV source
  publications.yaml         Publications (one source for homepage + CV)
  skills.yaml               Skill list (private job-search tooling)
src/data/
  cms-ma-pd-stars-*.csv     CMS Star Ratings distribution (cliff curve)

scripts/
  blog                      Authoring CLI (new/preview/publish; see blog.md)
  build_blog.py             Blog build pipeline
  build_resume.py           Resume + CV build pipeline (WeasyPrint)
  build_portfolio.py        Activity grid + writing list + citation counts
  build_cliff.py            Star Ratings density curve (manual, annual)
  build_og.py               Open Graph card renderer (manual)
  build_jobsearch.py        Private, local-only job-search driver
  lint_*.py                 Guards (blog, vocab, facts, notes, recognition,
                            gantt, markers, skills, jobfit) — see docs/pipelines.md
  _common / _publications / _skills.py   Shared libraries
  hooks/pre-push            Self-installed lint gate
  requirements.txt
  fonts/et-book/            ETBook TTFs (MIT, roman + italic)
  templates/
    blog/                   Jinja templates (base, list, post, feed)
    resume/                 Resume + CV Jinja templates

docs/
  pipelines.md              Full architecture + add-each-type cookbook
  critique/                 Critique pipeline methodology + playbook

.github/workflows/
  build_blog.yml            Builds blog + commits output on push
  build_resume.yml          Builds resume PDF + commits on push
  build_portfolio.yml       Refreshes activity grid, homepage writing list,
                            and citation counts (also runs weekly on a
                            schedule). Triggers on any blog post change so
                            new posts auto-populate on the homepage.

archive/                    Historical reference (not served)
  redesign/                 Tufte rebuild rationale doc
```

## Pipelines

Pure HTML/CSS at the surface, but several Python pipelines stand behind it.
Each reads a source under `src/content/` (or `index.html`), transforms it,
and commits the output back to the repo. The only network call at build
time is Semantic Scholar for citation counts; everything else is local. All
are idempotent: re-running them against unchanged inputs is a no-op. The
three core build pipelines are sketched below; the resume **and CV** share
one build, and the cliff curve, OG card, critique, site-review, and private
job-search pipelines are documented in full in
[docs/pipelines.md](./docs/pipelines.md).

```
  src/content/blog/*.md  ──▶ lint_vocab + lint_blog ──▶ build_blog
                                                          │
                                                          ▼
                                            blog/<slug>/index.html
                                            blog/index.html
                                            blog/archive/index.html
                                            sitemap.xml

  src/content/resume.md  ─────────────────────────────▶ build_resume
                                                          │
                                                          ▼
                                                resume.pdf, resume.html

  src/content/blog/*.md  ──┐
  index.html (markers)   ──┴──────────────────────────▶ build_portfolio
                                                          │
                                                          ▼
                                            index.html (activity grid,
                                                       writing list,
                                                       citations)

  git push  ──▶  scripts/hooks/pre-push  ──▶ 8 linters + grep guards
                                              (blog, vocab, facts, notes,
                                               recognition, gantt, markers,
                                               skills)
                 (self-installed via _common.install_git_hooks)
                 + .github/workflows/lint.yml runs the full suite in CI
                   unconditionally (PR + push + weekly)
```

### Blog (`scripts/build_blog.py`)

- **Source:** `src/content/blog/*.md` (markdown + YAML frontmatter)
- **Output:** `blog/<slug>/index.html`, `blog/index.html`,
  `blog/archive/index.html`, `sitemap.xml`
- **CI:** [build_blog.yml](.github/workflows/build_blog.yml) on push to
  `src/content/blog/**`, `scripts/build_blog.py`,
  `scripts/templates/blog/**`, or `scripts/requirements.txt`

CI runs `lint_vocab.py` and `lint_blog.py` first; either failure aborts
the build. The build uses markdown-it-py + mdit-py-plugins + Jinja2.
Math (`\(...\)` inline, `\[...\]` display) is stashed before parsing
and restored verbatim for client-side KaTeX. Fenced ` ```mermaid `
blocks are rewritten to `<pre class="mermaid">` so the Mermaid runtime
picks them up. Posts split at the 2019 archive cutoff: 2009–2011
journalism pieces land in `/blog/archive/` so the main listing reads
as a coherent data-engineering portfolio. Drafts (`draft: true`) and
`_`-prefixed files are skipped. The CI job commits regenerated HTML
back to the repo.

### Resume (`scripts/build_resume.py`)

- **Source:** `src/content/resume.md`
- **Output:** `resume.pdf` (US Letter, single column, ATS-parseable),
  `resume.html`
- **CI:** [build_resume.yml](.github/workflows/build_resume.yml) on push
  to `src/content/resume.md`, `scripts/build_resume.py`,
  `scripts/templates/resume/**`, `scripts/fonts/**`, or
  `scripts/requirements.txt`. (It also builds the CV from
  `src/content/cv.md` + `publications.yaml`, and re-runs via a
  `workflow_run` edge after the weekly **Build portfolio** run so the CV
  picks up freshly refreshed citation counts — see
  [docs/pipelines.md](./docs/pipelines.md).)

Markdown renders through a Jinja2 template; WeasyPrint prints the PDF.
A regex post-pass converts the three-line role block (`**Company** |
Title` / `Date` / `*Stack*`) into a structured `<header class="role">`
element so the print CSS can style each line distinctly. ETBook (MIT)
is bundled under `scripts/fonts/et-book/` and embedded in the PDF so
the resume matches the site's body face.

The CI Ubuntu runner installs `libpango-1.0-0` + `libpangoft2-1.0-0`
for WeasyPrint. Locally on macOS: `brew install pango` and prefix
runs with `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`.

### Portfolio (`scripts/build_portfolio.py`)

- **Source:** `src/content/blog/*.md` frontmatter + `index.html` marker
  comments
- **Output:** in-place updates to `index.html` (no new files)
- **CI:** [build_portfolio.yml](.github/workflows/build_portfolio.yml)
  on push to `index.html`, `scripts/build_portfolio.py`,
  `scripts/requirements.txt`, or `src/content/blog/**.md`. Also Sundays
  06:00 UTC. Manual dispatch supported.

Three insertions land between marker comments in `index.html`:

- `<!-- activity-grid:start --> ... :end -->` — a 24-week Tufte-style
  dot sparkline showing recent posting cadence. No external requests.
- `<!-- writing-list:start --> ... :end -->` — the two most recent
  non-draft posts as full featured entries, and
  `<!-- writing-index:start --> ... :end -->` — the next six as compact
  tiles. Em-dashes are stripped on import; homepage chrome stays
  em-dash-clean even when source markdown isn't.
- `<span class="pub-citations">` inside each `<div class="pub-entry"
  data-sid="...">` — Semantic Scholar citation count. The public tier
  rate-limits aggressively (HTTP 429); the script retries with
  exponential backoff and preserves the existing value on failure.

New posts populate the homepage on the same CI run that publishes
them, because the workflow triggers on the blog path too. Both
`build_blog` and `build_portfolio` commit during a blog-source push,
so `build_portfolio.yml` does a rebase-and-retry loop in case of a
race with `build_blog.yml`.

### Pre-push lints (`scripts/hooks/pre-push`)

- **Source:** `src/content/blog/*.md`, `src/content/resume.md`,
  `src/content/cv.md`, `index.html`
- **Output:** no files — the push proceeds or aborts with stderr from
  the failed check
- **Trigger:** every `git push`

Installed automatically by `scripts/_common.install_git_hooks()`, which
runs at the top of every `build_*.py` and `lint_*.py` script. On first
run after a clone the hook points git's `core.hooksPath` at
`scripts/hooks/` and prints a one-line notice; subsequent runs are
no-ops. The hook runs eight linters:

- `lint_blog.py` — HTML comments leaking from non-draft posts, fenced
  code nested in an HTML comment, blockquote-as-Mermaid, blank lines
  inside `<svg>`.
- `lint_vocab.py` — canonical CMS program-name capitalization (Star
  Ratings, Medicare Advantage, HEDIS, etc.) across blog, resume, CV,
  and homepage.
- `lint_facts.py` — cross-surface fact drift between `resume.md`,
  `index.html` h3+meta, and the JSON-LD block. Failure playbook at
  [scripts/lint_facts.md](./scripts/lint_facts.md).
- `lint_notes.py` — sidenote/margin-note additivity (a note may not
  restate a number or phrase already in the page prose).
- `lint_recognition.py` — the homepage "Service and Recognition"
  section must stay a subset of the comprehensive record in `cv.md`.
- `lint_gantt.py` — the homepage Education + Service Gantt figure must
  carry a mark for every `#education` and `#service` entry.
- `lint_markers.py` — the build-time injection markers a generator
  splices into (activity-grid, writing-list, pub-list, cliff-path,
  blog-thoughts, the resume.md skills block, the cv.md publications
  placeholder) must pair cleanly and still be present, so a stray hand
  edit can't corrupt a host file on the next build.
- `lint_skills.py` — resume.md's generated `<!-- skills -->` block must
  match what `src/content/skills.yaml` (the source of truth, shared with
  the private job-fit tooling) renders. `build_resume` regenerates it on
  main but not on PRs, so this gate keeps them in sync.

Plus a few `grep` guards: em-dash-clean chrome (`index.html`,
`resume.md`, `cv.md`, life-in-weeks), accent discipline in
`index.html`, no `<p>`-wrapped SVG children in built `blog/`, and the
critique-pipeline independence contract. Note the scope difference from
the CLI: `blog lint` / `blog publish` pre-flight run the **three**
content linters (`lint_blog`, `lint_vocab`, `lint_facts`); the **eight**
above plus the guards run in the pre-push hook on every `git push`.

**Server-side backstop.** The pre-push hook only fires for contributors
who push from a machine that has run a project script (which installs
it); web-UI edits, fresh clones, the `draft: false` bypass, and the
workflows' own bot commits all skip it. So
[lint.yml](.github/workflows/lint.yml) runs the **full suite** (all
eight linters + the four grep guards) on every `pull_request` and every
`push` to the default branch, unconditionally — it never consults the
`Blog-CLI-Linted:` redundancy trailer. The hook is the fast local echo;
`lint.yml` is the guarantee.

Both the pre-push hook and `build_blog.yml` can short-circuit via a
`Blog-CLI-Linted:` commit trailer written by `scripts/blog publish`.
The behavior is gated by toggles in `scripts/blog.config.yaml`
(`prepush_lint`, `ci_blog_lint`; both default to `always`). When a
toggle is `skip-if-cli-linted` AND every commit in the push range
carries the trailer, lints are skipped — the CLI already ran them on
the same content. Otherwise lints run.

### OG image (`scripts/build_og.py`, manual)

Rebuilds `og-default.png` (1200×630, Open Graph canonical size) from
inlined design tokens via Pillow. Not on a CI trigger because the card
content (name, subtitle, domain) changes rarely. Run locally when the
design changes:

```bash
pip install Pillow
.venv/bin/python scripts/build_og.py
```

## Local preview

No build step for the main site. Serve the repo root:

```bash
python3 -m http.server 8765
# open http://localhost:8765/
```

Blog URLs use trailing-slash paths (e.g. `/blog/concurrency/`), which
`http.server` resolves to `<slug>/index.html`. GitHub Pages behaves the same.

## Building the content pipelines

```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt

.venv/bin/python scripts/lint_blog.py        # source-side lint (see below)
.venv/bin/python scripts/build_blog.py       # rebuilds /blog/ + sitemap.xml
.venv/bin/python scripts/build_portfolio.py  # injects activity grid + citations

# Resume requires pango/cairo/glib:
#   brew install pango
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib \
  .venv/bin/python scripts/build_resume.py   # regenerates /resume.pdf
```

`lint_blog.py` catches four storage-level mistakes before they ship: HTML
comments in a non-draft post (leak as visible `&lt;!-- --&gt;` text), fenced
code blocks nested inside an HTML comment (break the tail of the document),
blockquote-as-diagram (`> flowchart LR` — Mermaid never sees it), and a blank
line inside an `<svg>` (markdown-it ends the HTML block and `<p>`-wraps the
rest of the chart). It runs before `build_blog.py` in CI and blocks the build
on violations. See
[CLAUDE.md](./CLAUDE.md) §Blog pipeline for the rule text.

Drafts (`draft: true`) and files whose names start with `_` are skipped by the
blog build (and by the linter). Citation lookups hit Semantic Scholar and may
be rate-limited; the script degrades gracefully (keeps existing values) and
the weekly cron will retry.

Blog posts use client-side CDN loads, conditional on content:

- `\(...\)` / `\[...\]` math → KaTeX (dollar signs are deliberately
  not treated as math delimiters — currency amounts in prose collide)
- ` ```mermaid ` fenced blocks → Mermaid
- Language-tagged fenced code → Prism syntax highlighting

## Writing blog posts

`scripts/blog` is the canonical entry point for authoring. It wraps the
lint, preview, and publish flow so a post moves from idea to live with
one terminal-side command. Two companion docs:

- [scripts/blog-cheatsheet.md](./scripts/blog-cheatsheet.md) — task-oriented
  ("I want to start a new post", "push was rejected", etc.) with
  copy-pasteable commands. **Start here if you're new to the CLI.**
- [scripts/blog.md](./scripts/blog.md) — comprehensive playbook with
  architecture diagram, redundancy toggles, security footguns, file map.

The section below is the one-paragraph orientation.

**One-time setup:**

```bash
uv venv && uv pip install -r scripts/requirements.txt   # or python3 -m venv
export EDITOR='code --wait'                              # in ~/.zshrc, for VS Code
```

**Every new shell session, activate the venv first.** Without it, the
CLI shebang resolves to a system Python that lacks the deps and the
pre-push lint hook can't find `python`:

```bash
cd ~/git/zaherkarp.github.io
source .venv/bin/activate
```

**From draft to live — the happy path is four commands:**

```bash
./scripts/blog new "My Post Title"        # 1. scaffold a draft (draft: true), open in $EDITOR
./scripts/blog preview my-post            # 2. render to a browser tab (no rebuild, no flag change)
./scripts/blog publish my-post --dry-run  # 3. show exactly what publish will do, change nothing
./scripts/blog publish my-post            # 4. lint, flip draft, commit, push to main
```

`blog new` bakes in `draft: true` and slugifies the title into the
filename. Write the body, `preview` as you go (slug fragments work, e.g.
`blog preview my-po`), then `publish` when it's ready.

**What `blog publish` does, in order:**

1. **Branch guard.** Refuses to run from a non-`main` branch unless you
   pass `--force-branch`, and even then only pushes when the publish
   commit is the single thing ahead of `origin/main` — so it can't sweep
   unrelated commits onto production. The simple path is to publish from
   `main`.
2. **Pre-flight lint.** Runs the three content linters (`lint_blog`,
   `lint_vocab`, `lint_facts`). Any failure aborts before anything
   changes on disk.
3. **Commit.** Flips `draft: true` → `false`, `git add`s the post, and
   commits with a `Blog-CLI-Linted:` trailer (the provenance token that
   lets later lint stages skip redundant work).
4. **Push to `main`.** This fires the **pre-push hook** (the six linters
   (eight of them) plus grep guards described under [Pre-push lints](#pre-push-lints-scriptshookspre-push)
   above), then hands off to CI.

After the push, two GitHub Actions runs finish the job with no further
action from you: `build_blog.yml` renders the post into
`blog/<slug>/index.html` and regenerates the listing, sitemap, and feed;
`build_portfolio.yml` regenerates the homepage sparkline and writing
list so the post appears on the front page on the same run. Both commit
their output back to `main`. (Because two workflows commit to `main`
from one push, `build_portfolio.yml` rebases-and-retries if its push
loses the race — you don't have to do anything.)

**Full command reference:**

```bash
./scripts/blog new "My Post Title"     # scaffold draft, open in $EDITOR
./scripts/blog list --drafts           # see what's in flight
./scripts/blog edit my-post            # reopen a draft (slug fragment works)
./scripts/blog lint my-post            # scoped lint (lint_blog + lint_vocab + lint_facts)
./scripts/blog preview my-post         # browser preview (no KaTeX/Mermaid/Prism — see §2d)
./scripts/blog publish my-post --dry-run   # show the plan, change nothing
./scripts/blog publish my-post             # lint, flip draft, commit, push to main
./scripts/blog status                  # drafts + last 5 published + git state
```

**Less common:** `blog draft <slug>` un-publishes (no commit; see §2h),
`blog rename old new` renames (does NOT rewrite inbound links; see §2i),
`blog config show` inspects redundancy toggles. Symlink `scripts/blog`
into `~/.local/bin/blog` if you'd rather type `blog` than `./scripts/blog`.

The bypass path still works: drop `src/content/blog/<slug>.md` with
`draft: false` frontmatter and `git push`. CI runs the same linters, so
a bypass that violates [scripts/lint_blog.py](./scripts/lint_blog.py)
fails the build rather than shipping silently.

## Deploy (GitHub Pages)

Served at `https://zaherkarp.com/` (CNAME present, apex domain).

Settings that must be set manually:
- Settings → Pages → Source: Deploy from branch → `main` → `/ (root)`
- Settings → Actions → General → Workflow permissions → **Read and write**
  (required so the CI workflows can commit regenerated HTML/PDF back)

Canonical URLs point at `https://zaherkarp.com/`.

## Analytics (GoatCounter)

GoatCounter (site code `zaher-karp`) is on every page, plus a custom
`404.html` whose recorded hits are prefixed `404` so broken URLs cluster
under one group in the dashboard (the requested path is preserved after the
prefix, so you can see exactly what people and crawlers failed to find).

### Exclude yourself

GoatCounter has no IP exclusion (it stores no IPs by design). The supported
way to drop your own visits is a per-browser `localStorage` flag that
`count.js` checks before sending. It is **per browser, per device** — you
have to set it once in every browser you use to view the live site.

**Desktop (console):**

1. Open `https://zaherkarp.com/` in the browser (the flag is scoped to that
   origin, so you must be on the site).
2. Open DevTools → Console (`Cmd+Opt+J` Chrome / `Cmd+Opt+C` Safari after
   enabling the Develop menu / `F12` elsewhere).
3. Run:
   ```js
   localStorage.setItem('skipgc', 't')
   ```
4. Confirm: `localStorage.getItem('skipgc')` returns `"t"`. Reload and check
   the Network tab — there should be no request to `gc.zgo.at/count`.

To re-enable counting on that browser: `localStorage.removeItem('skipgc')`.

**Non-desktop (phones, tablets):** mobile browsers have no console, so use a
bookmarklet that runs the same command. One-time setup per device:

1. Bookmark any page (e.g. `https://zaherkarp.com/`).
2. Edit the bookmark and replace its URL with:
   ```
   javascript:(function(){localStorage.setItem('skipgc','t');alert('GoatCounter: this browser is now excluded.');})()
   ```
   Name it e.g. "skip gc".
3. Navigate to `https://zaherkarp.com/`, then open that bookmark. The alert
   confirms it ran. (iOS Safari: tap it from the bookmarks list while on the
   site. Android Chrome: type the bookmark name in the address bar and pick
   it — Chrome runs the `javascript:` payload in the current tab.)

The flag lives in site-data `localStorage`, so it survives until you clear
this site's data for that browser; clearing data means redoing the step.

## Before pushing

Two passes: static checks (terminal) and a browser walk-through.

### Static checks

```bash
# Blog source lint (HTML-comment leaks, blockquote-as-diagram, nested fences)
python3 scripts/lint_blog.py

# SVG mangling in built blog output (blank-line-inside-<svg> slips)
grep -rE '<p><(text|line|polyline|circle|rect|polygon)' blog/

# Em-dash-clean chrome
grep -c '—' index.html        # expect 0

# Accent discipline (counts --accent var refs + the #7a0000 SVG sentinel)
grep -cE -- '--accent|#7a0000' index.html   # expect ≤ 20

# Balanced HTML tag structure
python3 -c "from html.parser import HTMLParser; p=HTMLParser(); p.feed(open('index.html').read())"

# HTTP smoke test
python3 -m http.server 8765 &
curl -s -o /dev/null -w '%{http_code} index.html\n' http://127.0.0.1:8765/
curl -s -o /dev/null -w '%{http_code} resume.pdf\n' http://127.0.0.1:8765/resume.pdf
curl -s -o /dev/null -w '%{http_code} blog/\n'      http://127.0.0.1:8765/blog/
kill %1
```

### Browser walk-through

Serve locally (`python3 -m http.server 8765`) and check:

- All internal anchor links resolve; external links open.
- Light + dark mode render correctly in Chrome and Safari.
- GoatCounter fires on page load (network tab).
- Resume PDF downloads, ATS-parseable, 1–2 pages.
- Career arc swaps from horizontal SVG to vertical SVG below 760px (no
  horizontal scroll).
- All 7 `<details>` folds open/close (4 experience + speaking + 2 testimonials).
- All sidenote/margin-note toggles fire on a narrow viewport (DevTools at
  600px; click superscripts and ⊕ labels).
- Stars cliff figure renders inside the Stars Cliff Simulator project body.
- SkillSprout slope graph renders inside the Healthcare Workforce Transition Platform project body.
- Academic dot plot renders above publication entries; mobile compressed
  version fires below 760px.
- Education + Service Gantt renders between Testimonials and Education.
- Print preview: nav and career arc hidden, GoatCounter absent, content
  fits two pages, light tokens forced.
- Lighthouse accessibility ≥ 90 in both modes.
- Keyboard Tab: focus outline visible on each sidenote label and each
  fold summary as you traverse.

## Maintenance rhythm

- Write a blog post: use `./scripts/blog new "Title"` (see [§Writing blog posts](#writing-blog-posts)
  above; full playbook in [scripts/blog.md](./scripts/blog.md)). The CLI handles
  scaffolding, lint, preview, and the publish commit + push. Direct-edit fallback:
  drop `src/content/blog/<slug>.md` with frontmatter and push.
  Two CI workflows then run automatically: `build_blog.yml` generates `/blog/<slug>/`
  and updates the sitemap; `build_portfolio.yml` regenerates the activity-grid
  sparkline and the six most recent entries in the homepage writing section
  between the `<!-- writing-list:start --> ... <!-- writing-list:end -->`
  markers in `index.html`. To attach an editorial margin note to the homepage
  entry, add an optional `homepageMarginnote: "..."` field to the post's
  frontmatter — the build wraps it in a ⊕ toggle next to the title.
- Add a publication: append an entry to `src/content/publications.yaml`
  (set a `sid` to track a live citation count, or use `links` / `note` for a
  static entry) and push. `build_portfolio.yml` regenerates the homepage
  Publications block between the `<!-- pub-list:start --> ... :end -->`
  markers, and the next CV build picks it up. Do not hand-edit the generated
  `<div class="pub-entry">` markup in `index.html`.
- Edit the resume: change `src/content/resume.md`, push. CI regenerates
  `resume.pdf`.
- Add a life-in-weeks event: edit the `EVENTS` array in
  `life-in-weeks/index.html`.

## License

MIT. See [LICENSE.md](./LICENSE.md).
