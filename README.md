# zaherkarp.github.io

Personal portfolio site for Zaher Karp. Pure HTML/CSS, no framework, no npm.
The main page has no build step; blog posts, the resume PDF, and portfolio
widgets (activity grid + citation counts) each have a Python build pipeline.

See [CLAUDE.md](./CLAUDE.md) for design constraints and architectural decisions
that should not drift. See [AGENTS.md](./AGENTS.md) for agent-style workflows
(focus-group simulation, review personas) that live outside the constitution.

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
skillsprout/                Career trajectory explorer
  lib/skillsprout-client.js   Vendored O*NET 28.3 engine (~900KB)

src/content/
  blog/*.md                 Blog post sources (frontmatter + markdown)
  resume.md                 Resume source

scripts/
  build_blog.py             Blog build pipeline
  lint_blog.py              Source-side lint (runs before build in CI)
  build_resume.py           Resume build pipeline (WeasyPrint)
  build_portfolio.py        Activity grid + writing list + citation counts
  requirements.txt
  fonts/                    EB Garamond variable TTFs (OFL)
  templates/
    blog/                   Jinja templates (base, list, post)
    resume/                 Resume Jinja template

.github/workflows/
  build_blog.yml            Builds blog + commits output on push
  build_resume.yml          Builds resume PDF + commits on push
  build_portfolio.yml       Refreshes activity grid, homepage writing list,
                            and citation counts (also runs weekly on a
                            schedule). Triggers on any blog post change so
                            new posts auto-populate on the homepage.

archive/                    Historical reference (not served)
  tufte-concept-v18.html    Design mockup
  source-resumes/           Pre-consolidation resume drafts
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

`lint_blog.py` catches three storage-level mistakes before they ship: HTML
comments in a non-draft post (leak as visible `&lt;!-- --&gt;` text), fenced
code blocks nested inside an HTML comment (break the tail of the document),
and blockquote-as-diagram (`> flowchart LR` — Mermaid never sees it). It runs
before `build_blog.py` in CI and blocks the build on violations. See
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

## Deploy (GitHub Pages)

Served at `https://zaherkarp.com/` (CNAME present, apex domain).

Settings that must be set manually:
- Settings → Pages → Source: Deploy from branch → `main` → `/ (root)`
- Settings → Actions → General → Workflow permissions → **Read and write**
  (required so the CI workflows can commit regenerated HTML/PDF back)

Canonical URLs point at `https://zaherkarp.com/`.

## Before pushing

CLAUDE.md §"Pre-push testing checklist" is the standing ritual for substantial
pushes (anchor resolution, dark mode, GoatCounter, print layout, expand/collapse
affordances, Lighthouse accessibility). Serve locally with `python3 -m http.server`
and walk the list in a browser.

Static checks that don't require a browser (useful before the full checklist):

```bash
# Blog source lint (catches HTML-comment leaks, blockquote-as-diagram,
# and fenced blocks nested inside HTML comments)
python3 scripts/lint_blog.py

# Balanced HTML tag structure
python3 -c "from html.parser import HTMLParser; p=HTMLParser(); p.feed(open('index.html').read())"

# Quick HTTP smoke test
python3 -m http.server 8765 &
curl -s -o /dev/null -w '%{http_code} index.html\n' http://127.0.0.1:8765/
curl -s -o /dev/null -w '%{http_code} resume.pdf\n' http://127.0.0.1:8765/resume.pdf
curl -s -o /dev/null -w '%{http_code} blog/\n'      http://127.0.0.1:8765/blog/
kill %1
```

## Maintenance rhythm

- Write a blog post: drop `src/content/blog/<slug>.md` with frontmatter, push.
  Two CI workflows run automatically: `build_blog.yml` generates `/blog/<slug>/`
  and updates the sitemap; `build_portfolio.yml` regenerates the activity-grid
  sparkline and the six most recent entries in the homepage writing section
  between the `<!-- writing-list:start --> ... <!-- writing-list:end -->`
  markers in `index.html`. To attach an editorial margin note to the homepage
  entry, add an optional `homepageMarginnote: "..."` field to the post's
  frontmatter — the build wraps it in a ⊕ toggle next to the title.
- Add a publication: add `<div class="pub-entry" data-sid="PMID:...">` to
  `index.html` and push. The portfolio workflow populates the citation count.
- Edit the resume: change `src/content/resume.md`, push. CI regenerates
  `resume.pdf`.
- Add a life-in-weeks event: edit the `EVENTS` array in
  `life-in-weeks/index.html`.

## License

MIT. See [LICENSE.md](./LICENSE.md).
