# CLAUDE.md
# zaherkarp.github.io — persistent context for Claude Code

This file is read at the start of every Claude Code session.
Update it when decisions change. Do not let it drift from reality.

---

## Project overview

Personal portfolio site for Zaher Karp (zaherkarp.com / zaherkarp.github.io).
Pure HTML/CSS, no framework. The blog and resume have Python build steps;
the homepage and subpages are hand-authored static files.

**Current status:** Tufte-inspired rebuild merged on 2026-04-25 (claude/tufte-rebuild
branch). The site went through three eras: Astro/TypeScript/Tailwind, then
a first pure-HTML Tufte-cream redesign (EB Garamond, 640px Yau pivot, italic
hero claim, stats table), and now this rigorous Tufte-CSS rebuild (ETBook
self-hosted, 1400px+60% column with sidenotes in the margin, h1 hero, six
substantive figures, no stats table). The rationale doc for the current
design lives at archive/redesign/zaherkarp-tufte-rationale.md.

**Deployment:** GitHub Pages, served at zaherkarp.com via CNAME.

---

## Stack

- HTML/CSS only. No JavaScript except:
  (a) GoatCounter analytics (all pages).
  (b) The Stars Cliff Simulator at /star-rating-predictor/ — inline
      vanilla JS only, no CDN, no dependencies. Narrow exception
      because the interactivity is the whole point of that page.
  (c) The life-in-weeks grid at /life-in-weeks/ — inline vanilla JS
      only, no CDN. Renders the 4,680-week grid client-side so the
      "current week" stays accurate without a rebuild.
  (d) The SkillSprout career trajectory explorer at /skillsprout/ —
      loads the vendored @zaherkarp/skillsprout-client ES module
      (/skillsprout/lib/skillsprout-client.js, ~900KB, bundled O*NET
      28.3 data inside). Page shell is inline vanilla JS (~80 lines).
      Vendored, not linked from a CDN, to keep the site self-hosted
      and to avoid a third-party dependency surface. Do not swap to
      a CDN without discussion.
  (e) Blog posts load KaTeX / Mermaid / Prism (tokenizer only) from CDN,
      conditionally, when the post contains the relevant syntax. See
      Blog section below for the conditional logic.
  (f) The stochastic epidemic simulator at /epidemic-simulation/ —
      Python (sim.py) runs in the browser via Pyodide; charts render
      via Plotly.js; both load from CDN. External files split into
      app.js (UI + Pyodide glue), data.js (CDC coverage + state
      geometry), sim.py (model), styles.css. Served under the
      Blog-experiment subpages exception below. This is the only
      subpage on the site that depends on third-party CDN runtimes
      outside blog-post conditional loads.
  Sidenote toggling on the homepage uses the CSS checkbox-hack
  pattern; no JavaScript involved. See §Sidenote system below.
  Do not add JS anywhere else without discussion.
- ETBook self-hosted under /fonts/et-book/. License: MIT. Two weights
  (roman + italic, no bold). Subpages, blog, and resume share
  /fonts/et-book/et-book.css; index.html declares @font-face inline
  for first-paint speed.
- No external CSS frameworks.
- No preprocessors.
- No bundlers.
- No Google Fonts (removed in the rebuild; the prior site used
  EB Garamond from Google Fonts).

**Blog-experiment subpages — narrow exception:**
  One-off interactive subpages may break the inline-vanilla-JS-only
  rule when static HTML cannot reasonably express the idea — a
  stochastic simulator, a Pyodide-hosted model, a viz that genuinely
  needs a charting library. Pure HTML/CSS remains the strong default.
  Rules for the lane:
    - URL-scoped to its own subdirectory. No cross-contamination with
      index.html, blog chrome, or other subpages.
    - External JS/CSS files live only inside that subpage's directory.
    - CDN dependencies allowed only when the page cannot reasonably
      work without them. Document the dependency and why in the Stack
      list above.
    - GoatCounter script still appears on every page.
    - The lane does NOT apply to index.html, the blog pipeline
      templates, or any chrome-bearing page. Those stay pure HTML/CSS.
  Currently served under this exception: /epidemic-simulation/.
  Other subpages (/star-rating-predictor/, /life-in-weeks/,
  /skillsprout/) predate this lane and stay within their original
  inline-vanilla-JS pattern. Do not widen the exception without
  discussion.

---

## Analytics

**GoatCounter site code:** `zaher-karp`
Script format (one tag before `</body>`, on every page including blog and
subpages):
```html
<script data-goatcounter="https://zaher-karp.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
```

The Tufte rebuild's reference doc argues for "no client-side analytics."
We kept GoatCounter explicitly during the per-conflict resolution; it's
privacy-respecting, self-hosted-style, and the user actively uses it.

---

## File structure

```
zaherkarp.github.io/
├── CLAUDE.md                       # Project constitution
├── README.md                       # Local dev + deploy guide
├── CNAME, .gitignore, .nojekyll
│
│   # SERVED CONTENT (URL-stable)
├── index.html                      # Main portfolio (inline CSS, ~2570 lines)
├── blog.css                        # Shared stylesheet for /blog/
├── favicon.svg
├── og-default.png
├── robots.txt
├── sitemap.xml                     # Generated by build_blog.py
├── resume.pdf                      # Generated by build_resume.py
├── fonts/
│   └── et-book/                    # MIT-licensed ETBook woffs + LICENSE + et-book.css
├── blog/                           # Generated tree (build_blog.py)
│   ├── index.html                  # Current writing listing (2019+)
│   ├── archive/index.html          # Archive listing (pre-2019 posts)
│   └── <slug>/index.html           # Post pages (current + archive)
│
│   # INTERACTIVE SUBPAGES (served as-is, no build step)
├── star-rating-predictor/          # Stars Cliff Simulator (inline JS)
├── life-in-weeks/                  # 90-year weekly life grid (inline JS)
├── skillsprout/                    # Career trajectory explorer (vendored ES module)
├── epidemic-simulation/            # Stochastic SEIRV sim (Pyodide + Plotly)
│
│   # SOURCE CONTENT
├── src/content/
│   ├── blog/*.md                   # Blog post sources (frontmatter + markdown)
│   └── resume.md                   # Resume source
│
│   # BUILD TOOLING
├── scripts/
│   ├── build_blog.py
│   ├── build_resume.py
│   ├── build_portfolio.py          # Activity sparkline + citation counts
│   ├── lint_blog.py
│   ├── requirements.txt
│   ├── fonts/
│   │   └── et-book/                # ETBook TTFs for WeasyPrint (resume)
│   └── templates/
│       ├── blog/                   # Blog Jinja templates
│       │   ├── base.html
│       │   ├── list.html
│       │   └── post.html
│       └── resume/
│           └── resume.html
│
├── .github/workflows/
│   ├── build_blog.yml
│   ├── build_resume.yml
│   └── build_portfolio.yml
│
└── archive/
    ├── redesign/                   # Tufte-rebuild reference materials
    │   ├── zaherkarp-tufte-demo.html
    │   ├── zaherkarp-tufte-rationale.md
    │   └── zaherkarp-tufte-prompt.md
    ├── tufte-concept-v18.html      # Prior design mockup (pre-rebuild)
    └── source-resumes/              # Pre-consolidation resume drafts
```

---

## Design decisions/tokens — locked, do not change without discussion

The current design follows the Tufte rebuild rationale at
archive/redesign/zaherkarp-tufte-rationale.md. The summary below codifies
what's locked.

### Palette

Tufte cream paper, near-black ink, oxford red accent. Mode-symmetric
warmth lineage. The accent retunes for dark-mode AA contrast.

Light mode:
  --paper:  #fffff8    /* Tufte cream */
  --ink:    #111       /* Near-black body */
  --muted:  #6a6a6a    /* Neutral gray: dates, metadata, stack lines, sidenote bodies */
  --rule:   #d0d0c8    /* Hairline rule */
  --accent: #7a0000    /* Deep oxford red. Used 1-2x per chart maximum, never decoratively */

Dark mode (`@media (prefers-color-scheme: dark)`):
  --paper:  #201b14    /* Warm near-black, ported from prior pass */
  --ink:    #f5ecd7    /* Bright cream so body reads at 21px */
  --muted:  #c2b8a0    /* AAA contrast warm mid-tone */
  --rule:   #3a3024    /* Faint warm hairline */
  --accent: #e05e3e    /* Council-tuned dark accent (AA 4.75:1). Holds over from prior pass — do not swap to #7a0000, which fails contrast against #f5ecd7 */

**Accent discipline.** The Tufte rule is one or two accent uses per chart,
never decoratively. On the homepage that's roughly: the 2020 acquisition
callout in the career arc, the 4.0 cliff line + $50M label in the cliff
curve, the 2014–2015 cluster annotation in the Gantt. A handful of total
uses on the page. Subpages, blog post links, buttons, and other chrome use
--ink or --muted, not --accent. The prior site used --accent 32+ times
across links/section labels/project numbers/details summaries/activity
dots — that's the pattern to NOT re-grow.

**SVG palette adaptation.** Figure SVGs hardcode hex values
(fill="#111", "#6a6a6a", "#7a0000", "#d0d0c8") as presentation
attributes. CSS attribute selectors at the bottom of the inline `<style>`
block override these to var(--ink), var(--muted), var(--accent),
var(--rule) — so the same SVG markup adapts to light/dark without
per-element edits. Do not rewrite SVGs to use CSS classes; the attribute-
selector approach is the locked contract.

### Typography

  Body font: ETBook self-hosted at fonts/et-book/. Two weights only
    (roman + italic, no bold). License: MIT, by Krasny/Scranton/Tufte.
    Why: matches Tufte's book lineage; only widely-available digital
    revival of the type Tufte used in print.
  Fallback stack: `'et-book', Palatino, "Palatino Linotype", "Book Antiqua", Georgia, serif`.
  Mono: `'Courier New', Courier, monospace`. System-available, no font request.

  Size scale (homepage inline CSS):
    html: 17px                /* root unit */
    body: 1.4rem (~24px)      /* Tufte body comfort target */
    h1:   3.2rem              /* page title */
    h2:   2.2rem italic       /* section headings, only running italic */
    h3:   1.5rem              /* subsection / role title */

  No bold body text anywhere. One weight (regular) plus italic for the
  reservations listed in §Italic policy.

  Code blocks (blog posts only) use Solarized — see §Solarized code blocks.

### Italic policy

Italic reserved for:
  - H2 section headings (the only running italic style)
  - Sidenote numerals
  - The `.newthought` opener
  - Chart annotations and axis labels
  - Figure captions
  - Publication titles and journal names
  - Testimonial pullquote bodies
  - Formula variables

Italic is decoration on anything else and not used. In blog post prose,
`<em>` and `<i>` render as non-italic weighted emphasis (`font-weight: 500`)
so the italic reservation is absolute across the whole site.

### Small caps policy

Reserved for: nav items, contact field labels, the `.newthought` opener.
Not on stack tags, citation counts, dates, project numbers, or anything
else.

### Layout

Article max-width 1400px, body column at 60% (~840px on a wide viewport),
leaves 40% for floating sidenotes and margin notes. Below 760px the
column collapses to 100% and sidenotes become inline toggles via the
checkbox-hack pattern.

The prior site used a 640px Yau-pivot column with no margin. That was a
reductive choice; the rebuild restored the Tufte three-zone layout
because the sidenote system needs the margin to live in. Yau pivot is
historical — see Vocabulary.

### Hero

Sequence: nav, h1 (name), single plain subtitle, career arc figure.
No epigraph, no italic claim block, no rust border, no manifesto framing.
The career arc carries the "what I do" visually and the About section
carries the "who I am" narratively; two framing statements above the
chart was self-absorbed (rationale doc §Hero).

### Career arc SVG

Two SVGs swap at 760px:
  - Horizontal `viewBox="0 0 1200 440"` for desktop. Three rows: editorial
    & writing 2007-2014, research UW-Madison 2009-2018, data engineering
    sequence 2017-now (healthfinch / HC / BHA on a single row, abutting).
    One loud callout: red dashed line + filled circle + red text at 2020
    marking the Health Catalyst acquisition. Two quiet annotations
    (news-wire syndication 2008, MPH Biostatistics 2014).
  - Vertical `viewBox="0 0 440 1120"` for mobile (native redesign, NOT a
    rotated copy). Same data, same callout, but the era annotations are
    dropped because they crowd the narrower layout.

Bars use `--muted` (resolved via the SVG palette adaptation rule); the
single accent callout is the 2020 dashed line. Do not change SVG
coordinates without recalculating from scratch — they're tested.

The prior site had a single 800×320 SVG that scrolled horizontally on
mobile. The rebuild dropped that pattern (and its scroll-to-right inline
JS exception) because horizontal scroll violates Tufte's same-frame rule.

### Sidenote system (homepage only)

CSS checkbox-hack, no JavaScript:

```html
<label for="sn-X" class="margin-toggle sidenote-number"></label>
<input type="checkbox" id="sn-X" class="margin-toggle"/>
<span class="sidenote">…body…</span>
```

Two flavors:
  - **Sidenotes** (numbered): citations, methodological glosses, things a
    reader would reference back to. Auto-numbered via CSS counter on
    `.sidenote-number` labels.
  - **Margin notes** (unnumbered, ⊕ toggle label): tangential facts,
    asides. The choice between sidenote vs margin note is editorial.

Naming convention: `sn-<topic>` for numbered, `mn-<topic>` for unnumbered.

The hidden checkbox is sr-only positioned (1px wide, clip rect, off-screen)
rather than `display: none` so it stays in the keyboard tab order.
Focus from the (invisible) checkbox is projected onto the visible label
via `label:has(+ input:focus-visible) { outline: ... }`. Without this,
keyboard users couldn't reach or activate sidenote toggles.

Mobile (≤760px): the sidenote/margin-note span hides; tapping the label
reveals it as an indented inline block with a left rule.

Margin block discipline: marginnote spans must contain inline-only
content (no `<p>`, `<ul>`, `<ol>`, `<blockquote>`, `<table>`, `<div>`,
`<pre>`). At narrow viewports a block-level child either renders badly
or breaks the toggle layout. `scripts/lint_blog.py` does NOT enforce
this — it's a homepage-only rule; check via grep on content changes.

Sidenotes are homepage-only. Blog posts use KaTeX/Mermaid/Prism for
technical depth, not sidenotes.

### Solarized code blocks (blog posts)

Blog post code blocks use the Solarized palette via CSS variables in
`blog.css`. The base bg/fg flips with `prefers-color-scheme`; the eight
selective-contrast hues stay constant (Solarized is mode-symmetric by
design).

  --sol-bg:        #fdf6e3 light / #002b36 dark   /* base3 / base03 */
  --sol-fg:        #657b83 light / #839496 dark   /* base00 / base0 */
  --sol-fg-muted:  #93a1a1 light / #586e75 dark   /* base1 / base01 */
  Eight hues (constant across modes):
  --sol-yellow #b58900, --sol-orange #cb4b16, --sol-red #dc322f,
  --sol-magenta #d33682, --sol-violet #6c71c4, --sol-blue #268bd2,
  --sol-cyan #2aa198, --sol-green #859900

Prism's tokenizer (core + autoloader) loads from CDN when the post has
fenced code; the upstream Prism theme stylesheets are NOT loaded. All
`.token.*` styling comes from blog.css so there's no cascade fight.

Code blocks have a 1px `var(--rule)` border, 0.55rem 0.85rem padding,
1.5 line-height, 1rem 0 margin, and font-size `calc(var(--size-caption) * 0.95)`
(~16px at root 21px). No accent-color left-border (that's chart-callout
territory).

### Print overrides

`@media print` block in `index.html`:
  - Force --paper: #ffffff, --ink: #1a1a1a, --muted: #555, --rule: #c8c8c8
  - Hide nav.top, .timeline, figure.timeline (career arc viewBox doesn't
    fit a printable column)
  - Force all `<details>` folds open so the printed page contains
    everything
  - Sidenotes/margin notes print inline (float: none, italic muted) next
    to their reference
  - Page size auto, margins 0.75in
  - Hide checkbox toggles entirely

The resume template has its own print CSS in scripts/templates/resume/
resume.html.

### Name appearances policy

"Zaher Karp" appears once visibly on the homepage: the h1 nameplate.
Invisible metadata (title tag, OG tags, JSON-LD, sitemap) carries the
name elsewhere and is correct and necessary. Do not add additional
visible instances without discussion.

The page previously closed with a psql-style record (`resume_db=# SELECT
* FROM zaher;`) that carried a second visible "Zaher Karp" plus build-
time "currently" rows fed by `src/content/now.yaml`. That closer was
removed; its CSS (`pre.postgres`, `.prompt`), the now-block markers, the
yaml source, and the `build_now_block()` injection in
`scripts/build_portfolio.py` are all gone with it. There is no
"currently / now / reading / building" surface on the page now. If a
replacement is wanted, it's a fresh design decision, not a restoration.

### Tool vs method

Tools are software, platforms, languages, and libraries. Methods are
analytical or statistical approaches. Methods stay in prose. Tools go in
`.exp-stack` lines. Example: interrupted time series is a method (stays
in prose); Stata is a tool (goes in the stack line).

### Mobile nav

Nav wraps on medium screens. Acceptable and intentional. No hamburger
menu without discussion.

### Writing section update rule

The 6 most recent posts in the homepage Writing section are hand-
maintained. Activity sparkline above the entries is generated by
`scripts/build_portfolio.py` between `<!-- activity-grid:start --> ...
<!-- activity-grid:end -->` markers. The "View all writing" link points
to `/blog/`.

### Testimonials

Two testimonials, both from Health Catalyst. Italic blockquote pullquote
with thin left border (1px var(--rule)), attribution flush-right below
the quote, full version behind a `<details class="fold">`.
Attribution alignment: `text-align: right` per Tufte tradition. The
prior left-aligned alignment was changed in the rebuild.
This is intentional and complete. Do not treat as a gap to fill.

### Domain sentence

Current subtitle: "Healthcare data engineering and Medicare Advantage
analytics." Ported from the demo verbatim. The prior site had a longer
domain sentence with a parenthetical about "16+ years"; that was
absorbed into the broader About section copy. Do not change without
explicit instruction.

### Experience entry expand rule

Four of five experience entries (BHA, Health Catalyst, healthfinch, UW)
use a `<details class="fold">`/`<summary>` expand pattern for the technical
detail. The lead paragraph stays visible always. Sustainable Clarity is a
single paragraph and doesn't fold. The summary text is "More detail" with
custom `+`/`-` prefix (`details.fold > summary::before`); browser default
disclosure markers are suppressed.

The Huber psi-function formula sits inside the BHA fold as pure HTML/CSS
math (no MathJax/KaTeX dependency for one short formula).

### Project numbering

Seven projects, numbered 01 through 07. The number `<span class="num">`
floats left as a hanging old-style figure (font-size 2.2rem, color
var(--muted)). The h3 title and body sit to the right.

### .exp-stack contrast

The `.exp-stack` lines use `var(--muted)` at ~0.95rem. Contrast is
defensible at AA. Carry-over flag from the prior site: if you tighten
sizes elsewhere on the page, recheck this against WCAG AA in both
modes.

---

## Content — source of truth

The Tufte rebuild content was ported from `archive/redesign/
zaherkarp-tufte-demo.html` with em-dashes stripped (replaced with
commas, periods, or rephrased — see Em dash policy below). Real prose
adaptations are documented in the rationale doc.

**Live site:** zaherkarp.com (= this repo).
**Email:** me@zaherkarp.com.

**Em dash policy:** Stripped throughout. Every em dash was either
replaced with a comma (parenthetical asides), a period (sentence
breaks), or rephrased entirely. En-dashes preserved in compound proper
nouns (UW-Madison, AWS-to-Azure). This is a personal preference, not a
Tufte requirement. Blog post markdown sources are NOT swept (preserves
historical voice); only chrome and the homepage are em-dash-clean.

**Links:**
  Stars Cliff Simulator (public demo): /star-rating-predictor/ + methodology post
  Client-Side Stars Rating Predictor (internal, BHA): no link, private
  SkillSprout: /skillsprout/
  Medicare Advantage Insight Engine: GitHub repo only
  ECDS Shock Index: GitHub repo only
  Epidemic simulator: /epidemic-simulation/ + /blog/two-states-one-pathogen/

**Subpages in this repo:**
  /star-rating-predictor/ — "Stars Cliff Simulator." Public, teaching-
    oriented demo focused on the 4.0★ QBP cliff. Inline vanilla JS.
  /life-in-weeks/ — 90-year weekly life grid (Tim Urban-style),
    inline vanilla JS. EVENTS array hand-maintained in the page.
  /skillsprout/ — career trajectory explorer. Vendors the
    @zaherkarp/skillsprout-client ES module (~900KB, includes O*NET 28.3
    data inline). Page shell is vanilla JS in index.html.
  /epidemic-simulation/ — stochastic SEIRV epidemic simulator, companion
    to /blog/two-states-one-pathogen/. Pyodide + Plotly via CDN.

**Stars tools distinction — two tools, do not conflate:**
  1. Stars Cliff Simulator — public, at /star-rating-predictor/.
     Teaching-oriented, synthetic weights, 4.0★ QBP cliff focus.
     Project card 02 on index.html. Both Stars methodology blog
     posts describe this tool.
  2. Client-Side Stars Rating Predictor — internal, built at Baltimore
     Health Analytics. Cut-point dashboard running against live measure
     feeds for contract-level remediation planning. Source is private.
     Project card 01 on index.html (intentionally no live-demo link,
     no GitHub link, no methodology post).
  Do not "consolidate" the two project cards, cross-link the internal
  tool to the public methodology posts, or add a GitHub/demo link to
  card 01. That would misrepresent the tools.

---

## Blog pipeline

Blog posts live at src/content/blog/*.md (markdown + frontmatter).
Build script: scripts/build_blog.py
  Reads markdown files (skips any whose stem starts with `_`)
  Uses markdown-it-py + mdit-py-plugins + Jinja2 + python-frontmatter
  Applies templates in scripts/templates/blog/ (base.html, post.html, list.html)
  Outputs to blog/<slug>/index.html (pretty URLs)
  Splits posts at ARCHIVE_CUTOFF (2019-01-01):
    - Current posts → blog/index.html (with an "Experiments" appendix
      listing /life-in-weeks/ and a link to the archive)
    - Archive posts → blog/archive/index.html (with a back-link)
  Regenerates sitemap.xml with homepage + subpages + all non-draft posts
  + /blog/archive/ (if archive is non-empty)

Archive policy:
  Posts from 2009–2011 (the 19 undergrad-era pieces on green building,
  education, sustainability, interviews) are split out to /blog/archive/
  so the main /blog/ listing reads as a coherent healthcare-data-
  engineering portfolio. Individual post URLs (/blog/<slug>/) still work
  for every archive post — only the listing placement changes.

Experiments section:
  Rendered at the bottom of blog/index.html. Hard-coded list in
  build_blog.py (EXPERIMENTS constant) pointing to small interactive
  pages that don't fit the long-form format. Currently: /life-in-weeks/.
  /star-rating-predictor/, /skillsprout/, and /epidemic-simulation/ are
  deliberately NOT listed here — they have first-class project cards or
  writing-section entries on the homepage.

Shared prose styles live in /blog.css (referenced by all generated pages).
Portfolio index.html keeps its CSS inline — do not extract.

Client-side CDN features on blog posts, loaded conditionally:
  KaTeX 0.16.11   — when post contains `$...$` or `$$...$$`. Both core
                    JS, auto-render JS, and KaTeX CSS load from
                    cdn.jsdelivr.net with SRI integrity hashes. The
                    auto-render onload calls `renderMathInElement` with
                    `$$` and `$` delimiters.
                    NOTE: when bumping KaTeX versions, always recompute
                    the SRI hashes (`curl -fsSL <url> | openssl dgst
                    -sha384 -binary | openssl base64 -A`); a stale hash
                    silently blocks the script and math fails to render.
                    This bit us once on auto-render.min.js — caught
                    during the rebuild.
  Mermaid 11      — when post contains ```mermaid fenced blocks
  Prism 1.29.0    — when post contains other fenced code blocks. Only
                    the tokenizer (core + autoloader) loads; the upstream
                    theme stylesheets are explicitly NOT loaded. Token
                    colors come from the Solarized rules in blog.css —
                    see §Solarized code blocks.

The main site (index.html) has no client-side CDN dependencies; the
no-build rule for the homepage is intact.

Local build:
  pip install -r scripts/requirements.txt
  python scripts/lint_blog.py   # source-side lint (see below)
  python scripts/build_blog.py

GitHub Action: .github/workflows/build_blog.yml
  Triggers on push under src/content/blog/ or scripts/ or the workflow
  itself, plus manual workflow_dispatch.
  Runs lint_blog.py, then build_blog.py.
  Commits generated HTML + sitemap.xml back to the repo.
  Requires: Settings → Actions → Workflow permissions → Read and write.

Lint step — scripts/lint_blog.py:
  Enforces three storage-side rules against src/content/blog/*.md
  (skipping drafts and `_`-prefixed files). Runs before build_blog.py
  in CI; the build fails loud if the lint fails.
  Checks:
    1. HTML comments (`<!-- -->`) in a non-draft post — leak as visible
       `&lt;!-- --&gt;` text.
    2. A fenced code block nested inside an HTML comment — breaks the
       tail of the document into escaped text.
    3. A blockquote line starting with a Mermaid keyword
       (`> flowchart LR`, `> graph TD`, etc.) — Mermaid never sees it;
       arrows escape to `--&gt;`.
  If the linter false-positives on a legitimate construct, fix the
  post — do not weaken the linter.

Underscore-prefix convention:
  Any src/content/blog/_*.md is skipped by the build.
  Used for fixture markers, meta-docs, and not-yet-ready drafts.

Scaffolded drafts must stay drafts — storage-side rule:
  A post outline with `<!-- author-note -->` HTML comments (or fenced
  ```mermaid / ```code blocks nested inside one of those comments) must
  ship with `draft: true` or an `_`-prefixed filename. Otherwise the
  comments leak as literal `&lt;!-- ... --&gt;` text. Happened once on
  hedis-measure-etl-patterns.md; the linter now fails CI on the pattern.
  Fix the post, not the pipeline.

Formula storage conventions:
  Inline math: `$...$`. Display math: `$$...$$`. KaTeX auto-renders both
  at page load. `$` inside fenced code blocks or inline backticks is
  shielded by `protect_math` in build_blog.py — don't escape shell
  `$VAR`s or hand-write `\$`. Do not nest display math inside list items
  or blockquotes where blank lines would break the `$$...$$` pair across
  blocks.

Diagram storage conventions:
  Diagrams live in fenced ```mermaid blocks. The build script
  (`rewrite_mermaid` in build_blog.py) detects the language-mermaid fence,
  rewrites the rendered `<pre><code>` to `<pre class="mermaid">`, and
  Jinja conditionally loads the Mermaid ESM runtime. Do NOT write a
  diagram as a blockquote ("> flowchart LR / > A --> B") — markdown-it
  renders it as prose with literal `--&gt;` arrows escaped on the page,
  and the linter rejects it.

The portfolio writing section shows 6 recent posts, hand-maintained
in index.html. The activity sparkline above the entries IS generated by
`scripts/build_portfolio.py`; the entries themselves are not.

---

## Resume pipeline

/resume.pdf is generated from /src/content/resume.md on every push.
Source of truth is the markdown. The PDF is a build artifact.

Build script: scripts/build_resume.py
  Uses markdown-it-py + Jinja2 + WeasyPrint
  Reads src/content/resume.md
  Applies scripts/templates/resume/resume.html (print CSS, Tufte palette
  + ETBook bundle)
  Regex post-pass wraps role-header blocks (org | title / date / stack)
  in a structured <header class="role"> element for CSS targeting
  Renders directly to resume.pdf at repo root
  Target: 1–2 pages, US Letter, ATS-parseable (single column, no tables)

Bundled fonts (committed):
  scripts/fonts/et-book/et-book-roman-line-figures.ttf
  scripts/fonts/et-book/et-book-display-italic-old-style-figures.ttf
  scripts/fonts/et-book/LICENSE                                  /* MIT */

The prior site used EB Garamond Variable TTFs in scripts/fonts/. Those
were removed in the rebuild.

Local dev setup (macOS, one-time):
  brew install pango            # WeasyPrint needs pango + cairo + glib
  pip install -r scripts/requirements.txt
  DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib python scripts/build_resume.py

GitHub Action: .github/workflows/build_resume.yml
  Triggers on resume.md, templates, fonts, or the build script.
  Installs pango/cairo/glib on Ubuntu runner, runs build_resume.py,
  commits regenerated resume.pdf back to the repo.

Do not rebuild resume.pdf by hand. Edit resume.md and push; CI
regenerates the PDF.

---

## Portfolio pipeline (sparkline + citation counts)

index.html is hand-maintained, with two build-time insertions:

  1. Writing cadence sparkline — a 24-week dot strip above the Writing
     entries. One dot per week, filled when there's a publication that
     week, empty otherwise. Trailing total ("N posts") + a margin note
     about the post-hiatus return. Sourced from blog frontmatter.
  2. Citation counts — Semantic Scholar lookups for publications tagged
     with `data-sid="PMID:..."` or `data-sid="DOI:..."`.

Build script: scripts/build_portfolio.py
  Reads blog frontmatter, builds the sparkline `<p>` block, injects
    between `<!-- activity-grid:start --> ... <!-- activity-grid:end -->`
    markers (the marker name is historical from the prior 52-week
    heatmap; the script now emits a Tufte-style 24-dot sparkline).
  For each `<div class="… pub-entry …" data-sid="...">` it fetches the
    citation count from Semantic Scholar's public API and updates the
    existing `<span class="pub-citations">N citations</span>` IN PLACE.
    The static markup decides where the span lives (inside the
    marginnote in the new design); the script just keeps the count
    current. Entries without an existing pub-citations span are left
    untouched.
  Graceful degradation: if the fetch fails (rate limit, network), the
    existing span is preserved. Running twice is idempotent.

GitHub Action: .github/workflows/build_portfolio.yml
  Triggers on push to index.html, scripts/build_portfolio.py, or blog
  posts; Sundays 06:00 UTC for citation refresh; manual dispatch.
  Commits regenerated index.html.

Semantic Scholar's public tier is aggressively rate-limited (HTTP 429).
The script retries with exponential backoff (1s between requests, 2s/4s
on retry). If a lookup still fails, the weekly cron will pick it up.
Do not add an API key without discussion.

Adding a new publication with a citation count: add
`data-sid="PMID:..."` (or `DOI:...`) to the `<div class="entry pub-entry">`
AND a `<span class="pub-citations">…</span>` placeholder inside its
marginnote, push, and the workflow populates the count.

---

## Pre-push testing checklist

Walk this list in a browser against the local preview before any
substantial push.

- [ ] `python scripts/lint_blog.py` is clean (if blog sources changed)
- [ ] `python scripts/build_blog.py` runs without warnings
- [ ] All internal anchor links resolve
- [ ] All external links open correctly
- [ ] Light + dark mode render correctly in Chrome and Safari
- [ ] GoatCounter fires on page load (check network tab)
- [ ] Resume PDF downloads (ATS-parseable, 1-2 pages)
- [ ] Career arc swaps from horizontal SVG to vertical SVG below 760px
      (no horizontal scroll affordance)
- [ ] All 8 `<details>` folds open/close (4 experience + speaking +
      2 testimonials + any new ones)
- [ ] All sidenote/margin-note toggles fire on narrow viewport
      (DevTools resize to 600px, click superscripts and ⊕ labels)
- [ ] Stars cliff figure renders inside Project 02 body
- [ ] SkillSprout slope graph renders inside Project 03 body
- [ ] Academic dot plot renders above publication entries; mobile
      compressed version fires below 760px
- [ ] Education+Service Gantt renders between Testimonials and
      Education sections
- [ ] Print preview: nav and career arc hidden, GoatCounter absent,
      content fits on two pages, light tokens forced
- [ ] Lighthouse accessibility ≥ 90 in both modes
- [ ] Keyboard Tab: focus outline visible on each sidenote label and
      each fold summary as you traverse
- [ ] Em-dash count: `grep -c '—' index.html` returns 0
      (chrome should be em-dash-clean; blog post markdown is not swept)
- [ ] `--accent` token usage in index.html: target ≤ 8 occurrences
      (the rationale's accent-discipline rule)

---

## What NOT to do

- Do not install npm, node, or any JS build tooling
- Do not add CSS frameworks (Tailwind, Bootstrap, etc.)
- Do not add React, Vue, or any frontend framework
- Do not change the 1400px article max-width or the 60% body column
  without discussion (the sidenote system depends on the margin)
- Do not change the Tufte palette (--paper / --ink / --muted / --rule /
  --accent) or the ETBook font without discussion
- Do not re-add a 640px max-width or remove the sidenote system
- Do not change career arc SVG coordinates without recalculating
- Do not re-introduce a "By the Numbers" stats table (the chart inventory
  replaces it)
- Do not add an italic claim/epigraph above the career arc (the rebuild
  explicitly removed it)
- Do not load Prism upstream theme stylesheets (the cascade fights with
  the Solarized rules in blog.css); only the tokenizer JS loads
- Do not promote `--accent` to decoration (links, buttons, project
  numbers, section labels). Reserve for chart callouts — see Accent
  discipline.
- Do not add server-side syntax highlighting (Pygments, etc.) to the
  blog build; Prism runs client-side via CDN to keep the Python
  pipeline dependency-light
- Do not strip em dashes from blog post markdown sources (the policy
  applies to chrome only)
- Do not nest block-level elements (`<p>`, `<ul>`, `<blockquote>`, etc.)
  inside marginnote spans

---

## Key people and context

Z = Zaher Karp. Manager of Data Science & Engineering at Baltimore Health Analytics.
BHA = Baltimore Health Analytics (current employer).
The portfolio targets: hiring managers for Director-level roles,
  peers in healthcare data engineering, recruiters in regulated healthcare.
Motivated reader register: long-form prose explaining decisions, not
  bullet scopes.

---

## Vocabulary

Stars = CMS Star Ratings (Medicare Advantage quality measurement program)
HEDIS = Healthcare Effectiveness Data and Information Set
CMS = Centers for Medicare & Medicaid Services
MA = Medicare Advantage
BHA = Baltimore Health Analytics
healthfinch = prior employer, acquired by Health Catalyst in 2020
Health Catalyst = prior employer (2020-2025)
Yau pivot = historical. The prior site used a single 640px column
  (no margin), named after Nathan Yau. The Tufte rebuild restored the
  three-zone margin layout (60% column + 40% margin) because the
  sidenote system needs the margin.
ETBook = the digital revival of the Bembo-derived type Tufte used in
  print. MIT-licensed by Krasny/Scranton/Tufte. Bundled at fonts/et-book/.
Tufte rebuild = the redesign merged 2026-04-25 on claude/tufte-rebuild;
  reference materials at archive/redesign/.

---

## Working agreement

If you think something looks wrong or should be improved, flag it and
ask before changing it. Do not make unrequested changes.
