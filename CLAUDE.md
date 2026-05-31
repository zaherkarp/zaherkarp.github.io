# CLAUDE.md
# zaherkarp.github.io — persistent context for Claude Code

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
  (d) Blog posts load KaTeX / Mermaid / Prism (tokenizer only) from CDN,
      conditionally, when the post contains the relevant syntax. See
      Blog section below for the conditional logic.
  (e) The stochastic epidemic simulator at /epidemic-simulation/ —
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
  Other subpages (/star-rating-predictor/, /life-in-weeks/) predate this
  lane and stay within their original inline-vanilla-JS pattern. Do not
  widen the exception without discussion.

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

The repo layout is conventional; `find` or [README.md](README.md) is
authoritative on the tree. Things not obvious from the filesystem:

- `.claude/` is gitignored — local agent settings only, never tracked.
- `index.html` carries inline CSS (~2,570 lines). Do not extract.
- `/blog/`, `/blog/archive/`, `resume.pdf`, `sitemap.xml` are GENERATED.
  Sources at `src/content/`. Do not hand-edit the generated outputs.
- Interactive subpages (`star-rating-predictor/`, `life-in-weeks/`,
  `epidemic-simulation/`) are served as-is, no build step.
- `archive/redesign/` is read-only reference from the 2026-04-25 rebuild.

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

The prior site used a 640px Yau-pivot column (single column, no margin).
The rebuild restored the Tufte three-zone layout because the sidenote
system needs the margin to live in.

Nav wraps on medium screens. Acceptable and intentional. No hamburger
menu without discussion.

### Hero

Sequence: nav, h1 (name), single plain subtitle, career arc figure.
The subtitle text itself is locked; do not edit without explicit instruction.
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
Invisible metadata (title, OG, JSON-LD, sitemap) carries it elsewhere
and is correct. Do not add additional visible instances without discussion.

A psql closer with a second visible "Zaher Karp" and a now-block sourced
from now.yaml was removed (#7, 2026-04-26). There is no current
"now / reading / building" surface; a replacement is a fresh design
decision, not a restoration.

### Tool vs method

Tools are software, platforms, languages, and libraries. Methods are
analytical or statistical approaches. Methods stay in prose. Tools go in
`.exp-stack` lines. Example: interrupted time series is a method (stays
in prose); Stata is a tool (goes in the stack line).

### Writing section update rule

The Writing section uses a featured + small-multiples-index pattern
that mirrors the Projects section (§Project numbering and layout),
both generated by `scripts/build_portfolio.py` from
`src/content/blog/*.md` frontmatter (publishDate, draft, title,
description). Do not hand-edit the entries between any of these markers;
the next CI run overwrites them. Two tiers:

  - **Featured** (`WRITING_FEATURED = 2`): the two most recent non-draft
    posts, between `<!-- writing-list:start --> ... <!-- writing-list:end -->`
    markers, inside `<section id="writing">` (60% column). Rendered as
    full `.entry` blocks (date + title + full-summary). To attach a
    margin note to a featured entry, add an optional
    `homepageMarginnote: "..."` field to that post's frontmatter; the
    build wraps it in a ⊕ toggle next to the title with id `mn-w-<slug>`.
    Margin notes are featured-only.
  - **Index** (`WRITING_TILES = 6`): the next six posts after the
    featured pair, between `<!-- writing-index:start --> ... <!-- writing-index:end -->`
    markers, inside the sibling `<div class="writing-index">` grid (90%
    max-width, `auto-fit minmax(240px, 1fr)`, collapses to 1 column at
    760px, just like `.projects-index`). Rendered as compact
    `.writing-tile` small multiples (date + smaller title + tile-summary).
    `homepageMarginnote` is intentionally ignored on tiles. The grid
    carries a `<p class="index-label">More writing</p>` header (hand-
    authored, before the `:start` marker) mirroring `.projects-index`'s
    "More projects" label, kept for visual parity even though the
    trailing "View all writing" link is also present.

Deliberately NOT reused: `.project-tile` and the `project-num` CSS
counter. Writing tiles use distinct `.writing-tile`/`.writing-index`
classes and are keyed by date, not a number; reusing the project
classes would corrupt the 01/02/… project numbering sequence.

The activity sparkline above the featured entries is generated by the
same script, between `<!-- activity-grid:start --> ... <!-- activity-grid:end -->`
markers. Its ⊕ margin note expands into a tag frequency rollup
(multi-post tags within the post-2025 cadence window, sorted count
desc then alphabetic). The "View all writing" link below the tile grid
is fixed prose (outside the markers, at the bottom of the
`.writing-index` div) and points to `/blog/`.

Em-dash policy: the homepage is em-dash-clean. Source post markdown is
not swept (preserves historical voice), so when `build_portfolio.py`
pulls a frontmatter title/description/marginnote into the homepage, it
strips em-dashes back to commas. The blog post page at
`/blog/<slug>/` keeps its em-dashes — only the homepage chrome is
sanitized.

This pipeline replaced a hand-maintained list that drifted twice
(missed the most recent post, linked to a draft slug with no `/blog/`
output). The build_portfolio workflow already triggers on
`src/content/blog/**.md`, so new posts populate the homepage on the
same CI run that publishes them.

### Testimonials

Two testimonials, both from Health Catalyst. Italic blockquote pullquote
with thin left border (1px var(--rule)), attribution flush-right below
the quote, full version behind a `<details class="fold">`.
Attribution alignment: `text-align: right` per Tufte tradition. The
prior left-aligned alignment was changed in the rebuild.
This is intentional and complete. Do not treat as a gap to fill.

### Experience entry expand rule

Four of five experience entries (BHA, Health Catalyst, healthfinch, UW)
use a `<details class="fold">`/`<summary>` expand pattern for the technical
detail. The lead paragraph stays visible always. Sustainable Clarity is a
single paragraph and doesn't fold. The summary text is "More detail" with
custom `+`/`-` prefix (`details.fold > summary::before`); browser default
disclosure markers are suppressed.

The Huber psi-function formula sits inside the BHA fold as pure HTML/CSS
math (no MathJax/KaTeX dependency for one short formula).

### Project numbering and layout

Six projects today. Numbers are NOT hand-assigned: each
`<span class="num">` is empty, and a CSS counter
(`counter-reset: project-num` on `#main`,
`counter-increment` on `.project .num` and `.project-tile .num`,
`::before { content: counter(project-num, decimal-leading-zero) }`)
generates the two-digit oldstyle figure from DOM order. The counter
is reset on the shared ancestor `#main` so featured projects and
small-multiples tiles share one continuous ascending sequence.

This means: to add, remove, reorder, promote, or demote a project,
edit the DOM and the digits follow. Do NOT hand-type a number into
a `.num` span; doing so is silently additive (the literal text
appears alongside the counter-generated digit) and will look broken.

The section uses a featured + small-multiples-index pattern:

  - **Featured** (inside `<section id="projects">`, 60% body column):
    The first two projects in DOM order — currently Stars Cliff
    Simulator and Healthcare Workforce Transition Platform. Each
    renders as a `<div class="project">` with an inline SVG figure
    (cliff-figure, sankey-figure), full prose, links row, and stack
    line. The hanging number floats left as a large oldstyle figure
    (font-size 2.2rem, color var(--muted)).
  - **Index** (outside the section, as a sibling `<div
    class="projects-index">`, 90% max-width grid): The remaining
    projects as `<div class="project-tile">` small multiples (today:
    Medicare Advantage Insight Engine, ECDS Shock Index, Care
    Delivery Workflow Changes, Practice Automation Analytics). Tiles
    use `position:absolute` for the hanging number (not float),
    a smaller h3, a `.tile-summary` paragraph (30-50 words), an
    optional `.tile-links` row, and `.stack`. The grid is
    `auto-fit, minmax(240px, 1fr)` so it renders 4 columns at
    desktop and collapses to 1 column at the 760px breakpoint.

A small italic `<p class="section-subhead">Featured</p>` label sits
between the H2 and the first featured project to cue the two-tier
structure. This label can be removed in a later pass if the visual
contrast between featured and index is sufficient on its own.

**Promotion/demotion rules**: a featured project compressed to a
tile gets its prose trimmed to 30-50 words, its link labels
shortened to tile conventions ("GitHub", "post", "demo", "paper",
"docs"), and its inline figures removed. A tile promoted to featured
expands the summary to full prose, lengthens link labels ("Live
demo", "Methodology post"), and gains inline figures if applicable.
In either case the numbering takes care of itself.

### .exp-stack contrast

The `.exp-stack` lines use `var(--muted)` at ~0.95rem. Contrast is
defensible at AA. Carry-over flag from the prior site: if you tighten
sizes elsewhere on the page, recheck this against WCAG AA in both
modes.

---

## Content — source of truth

The Tufte rebuild content was ported from a demo HTML (now removed)
with em-dashes stripped (replaced with commas, periods, or rephrased —
see Em dash policy below). Real prose adaptations are documented in
the rationale doc at archive/redesign/zaherkarp-tufte-rationale.md.

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
  Healthcare Workforce Transition Platform (SkillSprout): GitHub repo + /blog/onet-reskilling-probabilities/
  Medicare Advantage Insight Engine: GitHub repo + /blog/medicare-advantage-insight-engine/
  ECDS Shock Index: GitHub repo + /blog/ecds-shock-index/
  Care Delivery Workflow Changes: /blog/interrupted-time-series-care-redesign/
  Practice Automation Analytics (Charlie at OCHIN): /blog/practice-automation-workflow-roi/
  Epidemic simulator: /epidemic-simulation/ + /blog/two-states-one-pathogen/

The tile-link blog posts assume the four posts at
/blog/medicare-advantage-insight-engine/,
/blog/ecds-shock-index/,
/blog/interrupted-time-series-care-redesign/, and
/blog/practice-automation-workflow-roi/ have been (or will be)
drafted. If a slug changes during drafting, update the corresponding
tile-links href on index.html.

**Subpages in this repo:**
  /star-rating-predictor/ — "Stars Cliff Simulator." Public, teaching-
    oriented demo focused on the 4.0★ QBP cliff. Inline vanilla JS.
  /life-in-weeks/ — 90-year weekly life grid (Tim Urban-style),
    inline vanilla JS. EVENTS array hand-maintained in the page.
  /epidemic-simulation/ — stochastic SEIRV epidemic simulator, companion
    to /blog/two-states-one-pathogen/. Pyodide + Plotly via CDN.

**SkillSprout subpage removal (2026-05-19):** /skillsprout/ deleted from
this repo; the project survives at github.com/zaherkarp/skillsprout.
The Healthcare Workforce Transition Platform project card keeps the
slope-graph figure and links out to the standalone repo. The 900KB
vendored client was the loudest contradiction between the site's
no-bundler discipline and what it shipped; removing it eliminated that.

**Stars tools distinction — two tools, do not conflate:**
  1. Stars Cliff Simulator — public, at /star-rating-predictor/.
     Teaching-oriented, synthetic weights, 4.0★ QBP cliff focus.
     The Stars Cliff Simulator is the first featured project on
     index.html. Both Stars Cliff Simulator methodology blog posts
     (star-rating-demo-methodology.md and
     star-rating-predictor-methodology.md) describe this tool.
  2. Client-Side Stars Rating Predictor — internal, built at Baltimore
     Health Analytics. Cut-point dashboard running against live measure
     feeds for contract-level remediation planning. Source is private.
     As of the 2026-05-21 restructure, this tool no longer has its own
     project card. Two surfaces on the public site reference it:
       (a) The BHA role's "More detail" fold in the Experience section
           describes the architectural pattern ("a client-side Stars
           rating predictor where the cut-point projection runs
           entirely in the analyst's browser") as a compliance-driven
           architecture example, alongside the HEDIS hybrid measures
           paragraph.
       (b) The blog post compliance-as-architecture-stars-predictor.md
           (PR #40, merged 2026-05-21) names the tool explicitly and
           uses it as a case study for the broader thesis that some
           compliance constraints are best treated as architectural
           premises rather than bolted-on controls.
     The two surfaces are intentionally different in framing depth:
     the Experience fold treats the tool as job-history evidence;
     the blog post treats it as a methodology essay where the tool is
     the worked example. Source code remains private; the public
     artifacts describe what the tool does and why, not its
     implementation.
  Do not reconstruct a project card for this tool, do not cross-link
  the BHA fold to the Stars Cliff Simulator's methodology posts, and
  do not add the tool back as a small-multiple tile. The
  reasoning: a private internal tool reads better as job history
  plus a standalone methodology post than as a portfolio entry with
  no inspectable artifact.

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
  /star-rating-predictor/ and /epidemic-simulation/ are deliberately NOT
  listed here — they have first-class project cards or
  writing-section entries on the homepage.

Shared prose styles live in /blog.css (referenced by all generated pages).
Portfolio index.html keeps its CSS inline — do not extract.

Client-side CDN features on blog posts, loaded conditionally:
  KaTeX 0.16.11   — when post contains `\(...\)` or `\[...\]`. Both core
                    JS, auto-render JS, and KaTeX CSS load from
                    cdn.jsdelivr.net with SRI integrity hashes. The
                    auto-render onload calls `renderMathInElement` with
                    `\[...\]` and `\(...\)` delimiters.
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

Math delimiters — do not switch back to `$...$`:
  LaTeX-style `\(...\)` (inline) and `\[...\]` (display) are used instead
  of TeX-style `$...$` / `$$...$$`. Dollar signs are reserved for currency
  in prose. The original pipeline tried to auto-detect math by pairing any
  two `$` in a paragraph, which wrongly matched currency ("**$4.6 billion**
  ($1.9 billion cut)") and corrupted both the markdown (literal `**`
  surviving) and the KaTeX output (garbage rendered as math). Switching
  delimiters makes the distinction unambiguous at the source level, so
  no heuristic is needed. Posts currently using the new delimiters:
  star-rating-demo-methodology.md, star-rating-predictor-methodology.md,
  two-states-one-pathogen.md. Migration history is in the git log under
  "Migrate math delimiters to \\(...\\) / \\[...\\]".

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
  Enforces four storage-side rules against src/content/blog/*.md
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
    4. A blank line inside an `<svg>` element — markdown-it ends the
       HTML block at the blank line and wraps the rest of the SVG
       children in `<p>` tags; the chart breaks.
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
  Inline math: `\(...\)`. Display math: `\[...\]`. KaTeX auto-renders both
  at page load. Dollar signs in prose are treated as currency and are not
  parsed as math, so don't escape shell `$VAR`s or hand-write `\$`. Do not
  nest display math inside list items or blockquotes where blank lines
  would break the `\[...\]` pair across blocks.

Diagram storage conventions:
  Diagrams live in fenced ```mermaid blocks. The build script
  (`rewrite_mermaid` in build_blog.py) detects the language-mermaid fence,
  rewrites the rendered `<pre><code>` to `<pre class="mermaid">`, and
  Jinja conditionally loads the Mermaid ESM runtime. Do NOT write a
  diagram as a blockquote ("> flowchart LR / > A --> B") — markdown-it
  renders it as prose with literal `--&gt;` arrows escaped on the page,
  and the linter rejects it.

The portfolio writing section shows the 2 most recent non-draft posts as
featured entries plus the next 6 as small-multiples tiles, generated by
`scripts/build_portfolio.py` from blog frontmatter. See §Writing section
update rule above for the marker contract.

---

## Resume and CV pipeline

Two documents share one build: a 1-2 page **resume** and a comprehensive
academic **CV**. Each emits a PDF (WeasyPrint) and a web HTML page. Sources
of truth are the markdown files; all four outputs (resume.pdf, resume.html,
cv.pdf, cv.html) are build artifacts.

  resume: src/content/resume.md  -> /resume.pdf + /resume.html
  cv:     src/content/cv.md       -> /cv.pdf + /cv.html

Build script: scripts/build_resume.py
  Config-driven: the `DOCS` list names each document's source, its two
  templates, its two outputs, and whether it carries a generated
  Publications section. Adding a document is a new DOCS entry.
  Uses markdown-it-py + Jinja2 + WeasyPrint.
  Shared pipeline for both docs: make_markdown / transform_role_blocks
  (wraps `org | title / date / stack` role headers into
  <header class="role">) / wrap_sections (wraps each ## section in a
  class-bearing <section> by heading text) / split_header.
  Resume target: 1-2 pages, US Letter, ATS-parseable (single column).
  CV: a traditional academic document, deliberately NOT a long resume.
  Sourced from the real academic CV. A brief "Research Interests" replaces
  the resume's Summary, then: Education, Appointments, Past Research
  Positions, Publications (numbered citation list), Presentations, Posters,
  Grants and Funding, Awards and Honors, Service and Professional Activities.
  Appointments holds the two industry roles (BHA, Healthfinch/HC); the older
  UW academic roles live under Past Research Positions. Some sections carry
  `###` subsections (Education: Undergraduate / Graduate / Fellowships;
  Service: University / Community / Peer Review / Mentoring), rendered as
  muted small-caps labels. No tech-stack lines, no achievement-metric
  bullets. Dated entries use a left-gutter year column: each list item
  starts `- **YYYY**` / `- **YYYY–YYYY**` / `- **YYYY–present**` (the
  leading bold renders as <strong>, styled as a muted year in a hanging
  indent); the generic ul/li in the cv templates apply this to every
  section. The CV does NOT use transform_role_blocks (no `Org | Title /
  date / stack` headers). Intentionally multi-page; same Tufte palette +
  ETBook.

Templates (scripts/templates/resume/):
  resume.html / resume-web.html  — resume PDF + web
  cv.html / cv-web.html          — CV PDF + web
  The cv templates intentionally DUPLICATE the resume CSS rather than
  sharing a Jinja partial, so the resume output stays byte-stable (the
  resume.html bytes must not move when the CV is rebuilt). The cv templates
  carry the academic-CV CSS: year-gutter list items (the generic ul/li are
  styled as hanging year columns) and the numbered `.pubs ol.pub-cv-list`
  citation list. If the shared palette/typography changes, update all four
  templates by hand.

lint_facts.py parses the CV's `## Appointments` list (parse_cv_appointments)
  rather than the resume role format: it checks the CV's current ("present")
  employer matches the resume's, that Appointments has exactly one "present"
  entry, and that every resume employer appears somewhere in cv.md (full-text
  substring, since the UW employer lives under Past Research Positions, not
  Appointments). Year-only ranges mean titles/start-dates are not
  cross-checked.

Publications on the CV: cv.md carries a `<!-- publications -->` placeholder
  inside its `## Publications` section. build_resume.py replaces it with the
  list rendered from src/content/publications.yaml (the same source of truth
  the homepage uses; see Portfolio pipeline). Cached citation counts are read
  from the YAML, so the resume/CV build makes NO network calls.

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
  Triggers on resume.md, cv.md, publications.yaml, templates, fonts,
  build_resume.py, or _publications.py. Plus a weekly cron (Sundays
  07:00 UTC, one hour after build_portfolio.yml refreshes the cached
  citation counts) so the CV picks up fresh counts; a GITHUB_TOKEN push
  does not re-trigger workflows, so the cron is the coordination point,
  not a PAT. Installs pango/cairo/glib, runs build_resume.py, commits
  resume.pdf + resume.html + cv.pdf + cv.html back to the repo.

Do not rebuild the PDFs by hand. Edit resume.md / cv.md / publications.yaml
and push; CI regenerates all four artifacts. (resume.pdf is not byte-stable
across rebuilds — WeasyPrint embeds a timestamp — but resume.html is.)

---

## Portfolio pipeline (sparkline + citation counts)

index.html is hand-maintained, with three build-time insertions:

  1. Writing cadence sparkline — a 24-week dot strip above the Writing
     entries. One dot per week, filled when there's a publication that
     week, empty otherwise. Trailing total ("N posts") + a margin note
     about the post-hiatus return. Sourced from blog frontmatter.
  2. Publications block — the full Publications section, generated from
     src/content/publications.yaml between
     `<!-- pub-list:start --> ... <!-- pub-list:end -->` markers.
  3. Citation counts — Semantic Scholar lookups for each publication that
     carries a `sid` ("PMID:..." / "DOI:..."), cached in the YAML.

Publications source of truth — src/content/publications.yaml:
  ONE list of entries feeds both the homepage Publications block and the
  CV's Publications section (see Resume and CV pipeline). The shared
  loader/renderers live in scripts/_publications.py:
    load_publications()       parse the YAML
    render_homepage_entries() emit the Tufte margin-note / checkbox-hack
                              markup (links or a prose note, plus the
                              cached count) for the homepage
    render_cv_entries()       emit a flat academic listing for the CV
    save_citation_counts()    write refreshed counts back into the YAML
                              (targeted line edits; comments preserved)
  Schema and field contract are documented in the YAML header. Keep the
  file em-dash-clean so the generated homepage chrome stays compliant.

Build script: scripts/build_portfolio.py
  Reads blog frontmatter, builds the sparkline `<p>` block, injects
    between `<!-- activity-grid:start --> ... <!-- activity-grid:end -->`
    markers (the marker name is historical from the prior 52-week
    heatmap; the script now emits a Tufte-style 24-dot sparkline).
  build_publications(): loads publications.yaml, fetches a fresh Semantic
    Scholar count for each entry with a `sid`, writes the refreshed counts
    back to the YAML cache, and regenerates the homepage Publications block
    into the pub-list markers.
  Graceful degradation: if a fetch fails (rate limit, network), the cached
    count in the YAML is preserved. Running twice is idempotent.

GitHub Action: .github/workflows/build_portfolio.yml
  Triggers on push to index.html, scripts/build_portfolio.py, or blog
  posts; Sundays 06:00 UTC for citation refresh; manual dispatch.
  Commits regenerated index.html (and publications.yaml when counts move).

Semantic Scholar's public tier is aggressively rate-limited (HTTP 429).
The script retries with exponential backoff (1s between requests, 2s/4s
on retry). If a lookup still fails, the weekly cron will pick it up.
Do not add an API key without discussion.

Adding a new publication: append an entry to src/content/publications.yaml
(see the header for the field contract; set a `sid` and `citations` to
track a count, or use `links` / `note` for a static entry), push, and the
workflow regenerates the homepage block and the next CV build picks it up.
Do not hand-edit the Publications block between the pub-list markers, the
next CI run overwrites it.

---

## Site review workflow

Multi-agent feedback + iterative implementation loop, separate from
the build pipelines above. Produces no site changes by itself; it
produces feedback documents that drive hand-applied iterations.

Entry points:
- `reviews/README.md` — workflow overview, prompt recipes (the four
  multi-agent prompts), iteration pattern, summary of the 2026-05-23 run
- `scripts/review/README.md` — publish-workflow operator notes
- `.github/workflows/site-review-publish.yml` — GitHub Action that
  opens a tracking issue per review batch and carries unchecked items
  forward. No API keys; no secrets.

The 2026-05-23 run produced four reports in `critiques/`,
`evaluations/`, and `reviews/`. Five iterations of changes shipped on
`claude/multi-agent-page-critique-BYmwb`; remaining Tier 3 discussion
items documented in `reviews/2026-05-23-synthesis.md`.

The multi-agent prompts themselves are deliberately not committed to
the repo (Option A scope: publish-only pipeline, prompts live with
the generator). If you want them versioned, drop them into
`scripts/review/prompts/`.

---

## Pre-push checks (agent-runnable)

These run automatically via `scripts/hooks/pre-push`, installed by
`scripts/_common.install_git_hooks()` on first run of any project script
(no manual setup; multiple machines self-bootstrap on first script run).

Checks:
- `python scripts/lint_blog.py` clean (blog source-side mistakes)
- `python scripts/lint_vocab.py` clean (canonical CMS program-name
  capitalization across blog sources, resume.md, and index.html;
  see §Vocabulary)
- `python scripts/lint_facts.py` clean (cross-surface fact drift between
  resume.md, index.html h3+meta, and JSON-LD; playbook for failures
  at scripts/lint_facts.md)
- `grep -c '—' index.html` returns 0 (em-dash-clean chrome)
- `grep -cE -- '--accent|#7a0000' index.html` ≤ 20 (accent discipline:
  counts both CSS variable refs and SVG literal callouts, since the
  SVG palette adapter expects #7a0000 as a presentation attribute.
  Bump the cap only after discussion; ratchet it down when removing
  uses.)
- `grep -rE '<p><(text|line|polyline|circle|rect|polygon)' blog/` returns
  nothing (catches blank-line-inside-`<svg>` slips)

Not in the hook (run manually for bigger pushes):
- `python scripts/build_blog.py` runs without warnings
- `python scripts/build_resume.py` regenerates resume.pdf

Human-eyeball smoke tests (light/dark render, sidenote toggles, fold
behavior, Lighthouse, print preview, figure rendering, mobile SVG swap)
live in [README.md](README.md) §Before pushing.

---

## What NOT to do

- No npm/node/JS build tooling, CSS frameworks, or frontend frameworks.
- No 640px max-width regression and no removing the sidenote system. The
  60% column with 40% margin is a contract; the sidenotes need the margin.
- No "By the Numbers" stats table. The chart inventory replaces it.
- No sidenotes outside the homepage. Blog posts use KaTeX/Mermaid/Prism
  for technical depth.
- No server-side syntax highlighting; Prism runs client-side via CDN.
- No Prism upstream theme stylesheets (they fight Solarized in blog.css).
- No em-dash stripping in blog post markdown sources (chrome only).
- No block-level elements inside marginnote spans.

Palette, max-width, ETBook, accent discipline, italic reservation, and
career arc coordinates are stated as locked in §Design decisions. Treat
those as the authoritative copy; do not duplicate them here.

---

## Key people and context

Z = Zaher Karp. Manager of Data Science & Engineering at Baltimore Health Analytics.
BHA = Baltimore Health Analytics (current employer).
Audience: experienced practitioners and managers in healthcare data
  engineering, plus recruiters working in regulated healthcare.
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
ETBook = MIT-licensed Bembo revival by Krasny/Scranton/Tufte; bundled at fonts/et-book/.

Enforced by `scripts/lint_vocab.py` against `src/content/blog/*.md`,
`src/content/resume.md`, `src/content/cv.md`, and `index.html`. (Facts
across resume.md, cv.md, and index.html are separately cross-checked by
`scripts/lint_facts.py`.) The CMS 2025 MA & Part D Star
Ratings fact sheet
(https://www.cms.gov/newsroom/fact-sheets/2025-medicare-advantage-part-d-star-ratings)
is the external source of truth for "Star Ratings" and "Medicare
Advantage" rendering.

The linter is canonical-driven, not wrong-form-driven. Each rule lists
the accepted spelling(s) plus a matcher; any literal the matcher catches
that isn't an accepted form is flagged. One declaration thus catches
every wrong-case variant the matcher reaches without a new regex per
wrong form. Patterns are deliberately narrow: `STAR` / `STARs` / `STAR
Ratings` / `MEDICARE ADVANTAGE` / `Centers for Medicare and Medicaid
Services` get flagged; lowercase generic English ("4.0 star QBP cliff",
"5 stars", "star rating displayed in the simulator") passes because the
linter can't tell proper-noun from common-noun usage in those positions.

Skip-ranges keep the linter focused on prose: code fences, inline code
spans, markdown link URLs, HTML attribute values, HTML comments, and
`<script>`/`<style>` block contents are excluded from matching.

Two escape hatches for legitimate non-canonical literals that fall
outside the skip ranges:
  - Per-post `vocab_exempt: ["STAR Ratings", ...]` frontmatter list,
    for citations, quotes, or proper-noun product names that genuinely
    use a non-canonical form. Exact-string opt-out, scoped to that post.
  - Module-level `EXEMPTIONS` dict in `lint_vocab.py` for non-markdown
    surfaces (`index.html`, `resume.md`). Empty by default.

Add a canonical to `CANONICALS` in `lint_vocab.py` when a new program
name surfaces with a high-confidence wrong rendering in the corpus.

---

## Agent panels (Focus Group, Design Council)

Two verbal-invocation simulation patterns. Both propose changes
keyed to line ranges; neither edits without approval.

**Focus Group** — reader-reception evaluation. 3 rounds of ~4
panelists (hiring managers, peers, recruiters, UX reviewers, named
archetypes like "Director of Quality Analytics at a regional MA
plan"). One round must include antagonists: senior healthcare-data-
engineering practitioners who pressure-test claims, denominators,
and positioning. Output a synthesis table with consensus strength
(unanimous / majority / single voice).

**Design Council** — design-decision taste calls. Personas as
caricatures of schools of thought:
  - Edward — Tufte rigor (data-ink, restraint, prose+visual integration)
  - Nathan — narrative viz (annotation, direct labels, story-first)
  - Steve — cognitive usability (Krug, scanning, plain language)
  - Haben — accessibility (WCAG 2.2, screen reader, contrast). Holds
    soft veto on AA regressions; no other persona has veto power.
  - Massimo — typographic detail (baseline grid, optical spacing,
    numerals, dash discipline)
  - Bret — interactive documents (reactive representations; defends
    the existing blog-experiment lane, proposes new work for it)
  - Jess — editorial (concision, voice, brand coherence)
  - Alan — web performance (Lighthouse, LCP, bundle size, font economy)

Single-persona for in-lane calls; 2-3 for cross-lane decisions;
full council rare. Convene for: design-token changes, new subpage
proposals, hero or projects-section changes, removing/reordering
content, anything that looks like feature creep. Do NOT convene for:
copy edits inside an experience entry, blog post voice (Focus Group,
or Jess alone), build-script or Python-pipeline changes, routine
content updates (adding a talk, publication, post).

When convening: 2-4 sentences per persona in their voice on the
specific artifact (file path, line range, live URL). Then points of
agreement, points of contention with the pairing. Recommendation
ONLY if asked; otherwise present the disagreement and stop. Do not
collapse disagreement into consensus unless explicitly asked.

Constraints for both panels: do not propose changes that violate
§What NOT to do or the locked design tokens above. The current
section set is intentional; do not propose adding sections without
discussion.

---

## Working agreement

If you think something looks wrong or should be improved, flag it and
ask before changing it. Do not make unrequested changes.
