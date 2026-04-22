# CLAUDE.md
# github.io-redesign — persistent context for Claude Code

This file is read at the start of every Claude Code session.
Update it when decisions change. Do not let it drift from reality.

---

## Project overview

Personal portfolio site for Zaher Karp (zaherkarp.github.io).
Redesign from Astro/TypeScript/Tailwind to pure HTML/CSS.
No framework. No npm. No build step for the main site.
Blog pipeline has a build step (Python) — see Blog section below.

**Current status:** Implementation complete and pushed to github.com/zaherkarp/github.io-redesign. Swap to zaherkarp.github.io main repo pending; project URL is blocked by the custom-domain redirect on the user site, so preview is local-only until the swap.
**Target repo:** github.io-redesign (new GitHub repo)
**Deployment:** GitHub Pages, project site at zaherkarp.github.io/github.io-redesign/
**Swap plan:** When ready, copy files into zaherkarp.github.io main repo and push.
The live site at zaherkarp.github.io stays untouched until the swap.

---

## Stack

- HTML/CSS only. No JavaScript except:
  (a) GoatCounter analytics (all pages).
  (b) The Stars Cliff Simulator at /star-rating-predictor/ — inline
      vanilla JS only, no CDN, no dependencies. Narrow exception
      because the interactivity is the whole point of that page.
      (URL path is kept stable; the page is titled "Stars Cliff
      Simulator" and focuses on the 4.0★ QBP cliff.)
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
  (e) Blog posts load KaTeX / Mermaid / Prism from CDN, conditionally,
      when the post contains the relevant syntax (see Blog section).
  (f) The stochastic epidemic simulator at /epidemic-simulation/ —
      Python (sim.py) runs in the browser via Pyodide; charts render
      via Plotly.js; both load from CDN. External files split into
      app.js (UI + Pyodide glue), data.js (CDC coverage + state
      geometry), sim.py (model), styles.css. Served under the
      Blog-experiment subpages exception below. This is the only
      subpage on the site that depends on third-party CDN runtimes
      outside blog-post conditional loads.
  (g) Tiny one-purpose inline UX script on index.html. Currently: a
      one-shot scroll-to-right on the career-arc container for viewports
      <640px, so mobile readers see the current role first instead of
      "Writing & Editing 2007." Narrow exception with the same posture
      as (b)–(d); not a general JS license.
  Do not add JS anywhere else without discussion.
- One Google Fonts import: EB Garamond (prose) + Courier New (system, data specimens).
- No external CSS frameworks.
- No preprocessors.
- No bundlers.

**Blog-experiment subpages — narrow exception:**
  One-off interactive subpages may break the inline-vanilla-JS-only
  rule when static HTML cannot reasonably express the idea — a
  stochastic simulator, a Pyodide-hosted model, a viz that genuinely
  needs a charting library. Pure HTML/CSS remains the strong default
  and the ambition for everything the rest of the site does.
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
  inline-vanilla-JS pattern — do not re-platform them without
  discussion. Do not widen the exception without discussion.

---

## Google Fonts and analytics

**Google Fonts import URL:**
```
https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap
```
Do not change this URL or swap the font without discussion.

**GoatCounter site code:** `zaher-karp`
Script format (one script tag before `</body>`, on every page):
```html
<script data-goatcounter="https://zaher-karp.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
```

---

## File structure

```
github.io-redesign/
├── CLAUDE.md                       # Project constitution
├── README.md                       # Local dev + deploy guide
├── .gitignore, .nojekyll
│
│   # SERVED CONTENT (URL-stable)
├── index.html                      # Main portfolio (inline CSS)
├── blog.css                        # Shared stylesheet for /blog/
├── favicon.svg
├── og-default.png
├── robots.txt
├── sitemap.xml                     # Generated by build_blog.py
├── resume.pdf                      # Generated by build_resume.py
├── blog/                           # Generated tree (build_blog.py)
│   ├── index.html                  # Current writing listing (2019+)
│   ├── archive/index.html          # Archive listing (pre-2019 posts)
│   └── <slug>/index.html           # Post pages (all posts, current + archive)
│
│   # INTERACTIVE SUBPAGES (served as-is, no build step)
├── star-rating-predictor/          # Stars Cliff Simulator (inline JS)
├── life-in-weeks/                  # 90-year weekly life grid (inline JS)
├── skillsprout/                    # Career trajectory explorer (vendored ES module)
├── epidemic-simulation/            # Stochastic SEIRV sim (Pyodide + Plotly, external files)
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
│   ├── build_portfolio.py          # Activity grid + citation counts
│   ├── requirements.txt
│   ├── fonts/                      # EB Garamond variable TTFs (OFL)
│   └── templates/
│       ├── blog/                   # Blog Jinja templates
│       │   ├── base.html
│       │   ├── index.html
│       │   └── post.html
│       └── resume/
│           └── resume.html
│
├── .github/workflows/
│   ├── build_blog.yml
│   └── build_resume.yml
│
└── archive/                        # Historical reference
    ├── tufte-concept-v18.html      # Canonical design mockup
    └── source-resumes/             # Pre-consolidation resume drafts
        ├── Zaher_Karp_Resume.md
        └── Zaher_Karp_Resume_Long.md
```

---

## Design decisions/tokens — locked, do not change without discussion

Palette: Tufte (cream paper and printed ink). Swapped from Scientific Paper
after mockup review. Light mode evokes Tufte's book-design heritage. Dark
mode is variant A (amped contrast) because the original dark was too gentle
against the warm-black ground.

Light mode:
  --bg:     #fffff8    /* Tufte cream. Warmer than #fafaf8. */
  --text:   #2a2a2a    /* Charcoal body. Softer than pure black on cream. */
  --muted:  #766f64    /* Warm gray: dates, metadata, stack lines. */
  --accent: #8b2e19    /* Rust: rules, links, hero-claim border, labels. */

Dark mode (variant A, amped):
  --bg:     #201b14    /* Warm near-black. Deeper than #1a1a17. */
  --text:   #f5ecd7    /* Bright cream. Brighter than #e8e4d6 so body reads. */
  --muted:  #c2b8a0    /* Warm mid-tone. AAA-contrast (8.7:1) for small text. */
  --accent: #e05e3e    /* Red-rust. Hue ≈12°, aligned with light accent (≈11°). */

  Dark-palette history (2026-04):
    The dark --accent was retuned twice in one session. Started at #e06940
    (saturated orange-rust, AA 5.1:1) — which the council judged "dominated
    the page" because --accent appears 32+ times across links, section
    labels, project numbers, details summaries, psql keywords, and activity
    dots. First retune to #d94a3a (redshift) failed AA at 4.05:1. Final
    value #e05e3e keeps the redshift and restores AA at 4.75:1.
    The dark --muted was raised from #b0a48a to #c2b8a0 (AA 6.9:1 → AAA
    8.7:1) in the same pass to ease the ~15 small-text classes that use it
    (dates, stack lines, writing descriptions, psql specimen metadata).

Single accent throughout the UI. No secondary UI color. No blue, green,
amber, cyan, or orange anywhere in the chrome. The psql status field uses
--accent (same token as all other accent use).

Typography:
  --font-body:    EB Garamond, Georgia, serif
  --font-mono:    'Courier New', ui-monospace, monospace
  Why: Garamond matches Tufte's book lineage. Courier is system-available,
  so no second Google Font request and graceful fallback on older systems.

  --size-caption: 0.78rem   /* metadata, stack lines, writing dates */
  --size-body:    1rem      /* all prose */
  --size-name:    clamp(...) /* hero name — keep the existing clamp() */

  Base: 21px. Why: Garamond reads small under 18px. 21px gives it room
  and pairs with the 640px Yau-pivot column — large type in a narrow
  column keeps line length inside the 55-75-character sweet spot.

Rules (horizontal dividers and section underlines):
  --rule-light: 2px
  --rule-dark:  3px
  Why: equivalent weights read as weaker on dark. The 1px bump preserves
  perceptual equivalence across modes. Print uses light weight (see below).

Spacing (reconcile against actual CSS; these are the intended tokens):
  --space-xs:      0.25rem   /* tight element gaps */
  --space-sm:      0.5rem    /* inline gaps between related items */
  --space-md:      1rem      /* paragraph rhythm */
  --space-lg:      2rem      /* between experience entries */
  --space-xl:      3rem      /* between major sub-sections */
  --space-section: 4rem      /* between page regions */
  Why: named tokens so changes are systematic, not ad hoc. If the current
  style.css uses raw rem values, audit and replace on next pass; do not
  rewrite in bulk without verification.

Print overrides (inside @media print):
  Force --bg: #ffffff and --text: #1a1a1a for maximum paper contrast.
  Use --rule-light weight everywhere (print reads as a light medium).
  Hide: nav, footer GoatCounter script, any animations, career arc SVG.
  Page size: auto. Margins: 0.75in.
  Why: the career arc's 800px viewBox exceeds printable column width.
  Print-lock to light tokens because paper is always a light medium
  regardless of the reader's screen mode.

**Italic policy:**
  Italic reserved for: pull quotes, testimonials, hero claim only.
  No italic on secondary text, descriptions, labels, metadata.
  In blog prose, `<em>` and `<i>` render as non-italic weighted emphasis
  (`font-weight: 500`) so the italic reservation is absolute across the
  whole site. Blockquotes in blog posts are treated as pull quotes and
  retain italic. See `.blog-body em` in `blog.css`.

**Layout:**
  Single column. Max-width 640px. Centered. No grid. No annotation margin.
  This is the Yau pivot — narrow focused column, all content in reading flow.

**Career arc SVG:**
  ViewBox 0 0 800 320. Coordinates verified and explicit.
  Direct labels above bars. Proportional time axis (42.1px/year, 19 years).
  Acquisition connector: healthfinch → Health Catalyst (dashed, arrow).
  Bar colors are mode-aware via CSS custom properties — past bars use
  `var(--muted)` with alternating fill-opacity (0.55 / 0.85) to encode
  acquisition continuity within the muted family; the BHA (current)
  bar, axis tick at 2025, and "now" label use `var(--accent)`.
  Acquisition connector (line, arrow, text) uses `var(--muted)` — the
  dashed arrow carries the acquisition signal, not its color.
  Previously (pre-2026-04) the bars used hardcoded hex fills in a warm
  palette independent of the UI scheme; the council flagged this as
  chartjunk per tufte-css precedent (which uses no color to encode data)
  and the bars were collapsed to the current two-token pattern.
  Do not change SVG coordinates without recalculating from scratch.

**Hero:**
  No h1 nameplate. Name appears in nav (anchor) only at the top of the page.
  Sequence: domain sentence → claim (italic, rust left border using --accent) → contact.
  No h1. The psql specimen that used to close the hero now lives at the
  end of the footer as a sign-off (see Footer + psql specimen sections).

**Inline stack lines:**
  Each experience entry ends with a .exp-stack Courier line.
  Tools only. No methods (stay in prose). No facts (stay in prose).
  Color: --text-dim. No accent color.

**Footer:**
  Plain Garamond. Small caps labels. Rust links (--accent). Courier is
  used only inside the psql sign-off block at the very end of the footer
  (see psql specimen); no Courier anywhere else in the footer chrome.
  The psql block sits after the copyright line and is the last visible
  element on the page — the blinking cursor reads as a sign-off.

**psql specimen:**
  Class name .hero-specimen (kept for now — renaming would touch CSS in
  three places for no functional gain). Located at the end of the footer,
  after the copyright line.
  Exact \x expanded display format. white-space: pre.
  Field alignment: name/title/focus padded to 6 chars so pipes align.
  psql prompt string: `resume_db=#` (not `zaher_resume_db=#`). The name
  appears once inside the record as a field value; it must not also
  appear in the prompt string.

**Name appearances policy:**
  "Zaher Karp" appears in exactly three visible places — nav anchor,
  footer copyright, and the psql `name` field value (now inside the
  footer psql sign-off). Each is load-bearing. Do not add additional
  visible instances. Invisible metadata instances (title tag, OG tags,
  JSON-LD, sitemap) are correct and necessary.

**Tool vs method:**
  Tools are software, platforms, languages, and libraries. Methods are
  analytical or statistical approaches. Methods stay in prose. Tools
  go in the .exp-stack line. Example: interrupted time series is a
  method — it stays in prose. Stata is a tool — it goes in the stack
  line.

**Mobile nav:**
  Nav wraps on medium screens. This is acceptable and intentional. Do
  not add a hamburger menu. If the wrap looks accidental, reduce link
  label length: Publications → Pubs, Speaking → Talks, Education →
  Edu, Service stays.

**Mobile career arc:**
  The career arc requires horizontal scroll below 580px. This is
  accepted and intentional. Do not build a simplified mobile SVG
  unless explicitly requested. The scroll affordance mask
  (fade-right gradient) is in the CSS.
  On viewports <640px the container opens scrolled to the right
  (to "now") via a small inline script — see Stack §(g). Without
  this, mobile readers landed on "Writing & Editing 2007" as the
  visible part of the chart, which inverts the chart's intent.

**Writing section update rule:**
  The writing section in index.html is hardcoded. It is not generated
  by build_blog.py. When new posts are published, update the writing
  section manually. Show the 6 most recent posts. The "View all
  writing" link points to /blog/.

**Stats table:**
  The stats table currently has five rows. Each row must have a
  defensible number. "50+ clinical organizations served" spans
  multiple roles and contexts — if this feels misleading, remove the
  row rather than inflate or deflate the number. Do not add rows
  without discussion.

  The third column carries a micro-visual (inline SVG) per row. Two
  framings are in play across the five shapes:
    - Cumulative-smooth: years experience (simple ramp 2009→2026, accent
      tick at 2020 for the research→data-eng transition).
    - Cumulative-narrative: health systems (flat 2009–2017, ramp 2017–
      2020 during healthfinch, plateau at 50+ through 2026).
    - Step: EHR platforms (flat at 1 from 2009–2017, step up to 4 in
      2017 when healthfinch joined — it already had Epic/Cerner/
      Veradigm/athena integrations).
    - Peak sparkline: publications (2012–2019, peak 2 in 2019),
      presentations (2010–2017, peak 6 in 2015).
  The `data-series` attribute on each `<tr>` encodes the series in
  machine-readable form so the markup still reads if SVG fails. Micro-
  visuals are `aria-hidden` / `role="presentation"` — the scalar and
  label carry the semantic data. Do not swap a row from narrative back
  to simple cumulative (or vice versa) without discussion; the chosen
  framing per row reflects the actual shape of that measure.

**Testimonials:**
  Two testimonials, both from Health Catalyst. This is intentional
  and complete for now. Do not treat it as a gap to fill.

**Domain sentence:**
  The current domain sentence ("16+ years building production analytics
  in regulated healthcare — where measurement errors have regulatory
  and financial consequences") is approved but flagged for potential
  revision. A proposed alternative is: "In Medicare Advantage, a
  measurement error in a HEDIS pipeline is a contractual event, not a
  data quality incident." Do not change it without explicit instruction.
  (Historical note: the phrase was originally "Sixteen years" and was
  changed to "16+ years" at some point before 2026-04; CLAUDE.md was
  not updated in lockstep. The numeric-style convention is not locked
  beyond this sentence.)

**.exp-stack contrast:**
  The .exp-stack lines use --text-dim (#787878 light / #666670 dark)
  at 0.78rem. Contrast ratio is borderline at AA for this size. Do
  not change the color. Flag it for manual accessibility testing
  before the swap.

**Experience entry expand rule:**
  The two longest experience entries (Health Catalyst and UW-Madison)
  use a `<details>`/`<summary>` expand pattern for paragraphs two
  onward. The lead paragraph of each entry stays visible always. The
  expand trigger label is "More detail" and the collapse label is
  "Less". The pattern matches the existing testimonial expand
  implementation. Do not apply this pattern to other sections without
  discussion.

---

## Content — source of truth

The v18 mockup (tufte-concept-v18.html) is the canonical content source.
All prose, dates, links, and stack lines in v18 are correct and approved.

**Live site:** zaherkarp.github.io (Astro) — use for gap analysis only.
Do not copy structure or CSS from the live site.

**Email:** me@zaherkarp.com (confirm before shipping)

**Links:**
  Stars Cliff Simulator (public demo): /star-rating-predictor/ + methodology post
  Client-Side Stars Rating Predictor (internal, BHA): no link — private source
  SkillSprout: https://zaherkarp.com/skillsprout
  Medicare Advantage Insight Engine: GitHub repo only
  ECDS Shock Index: GitHub repo only
  Epidemic simulator: /epidemic-simulation/ + /blog/two-states-one-pathogen/

**Subpages in this repo:**
  /star-rating-predictor/ — "Stars Cliff Simulator." Public, teaching-
    oriented demo focused on the 4.0★ QBP cliff. Inline vanilla JS,
    no CDN. Ordinal logistic regression with CMS 2025 weights. Hero
    readouts are P(clearing 4.0★) = P(Y≥4) and distance-to-cliff
    (E[Y] − 4.0). See the Stack section for the JS exception rationale,
    and Stars tools distinction below for how this differs from the
    internal BHA predictor.
  /life-in-weeks/ — 90-year weekly life grid (Tim Urban–style),
    inline vanilla JS, no CDN. Data (birth year, events) lives inline
    in the page. Events are hand-maintained — edit the EVENTS array
    directly in /life-in-weeks/index.html to add one.
  /skillsprout/ — career trajectory explorer. Vendors the
    @zaherkarp/skillsprout-client ES module at
    /skillsprout/lib/skillsprout-client.js (~900KB, includes O*NET 28.3
    data inline). The page shell is vanilla JS in index.html. To update
    the engine, rebuild the npm package and replace the vendored bundle
    — there is no automated sync with the upstream package.
  /epidemic-simulation/ — stochastic SEIRV epidemic simulator, companion
    to /blog/two-states-one-pathogen/. Python (sim.py) runs in the
    browser via Pyodide; charts via Plotly.js; both load from CDN.
    External files: app.js (UI + Pyodide glue), data.js (CDC coverage +
    US state geometry), sim.py (model), styles.css. Only subpage
    served under the Blog-experiment subpages exception — see Stack
    section. Has a writing entry on the homepage but no project card.

**Deprecated separate repos (as of 2026-04-19):**
  life-in-weeks and skillsprout previously had their own GitHub Pages
  repos at zaherkarp.github.io/life-in-weeks and zaherkarp.github.io/
  skillsprout. Both are now served from this repo as subpages. The
  standalone repos can be archived once the swap is complete.

**Stars tools distinction — two tools, do not conflate:**
  1. Stars Cliff Simulator — public, at /star-rating-predictor/.
     Teaching-oriented, synthetic weights, 4.0★ QBP cliff focus.
     Project card 02 on index.html. Both Stars methodology blog
     posts describe this tool.
  2. Client-Side Stars Rating Predictor — internal, built at Baltimore
     Health Analytics. Cut-point dashboard running against live measure
     feeds for contract-level remediation planning. Source is private.
     Project card 01 on index.html (intentionally no live-demo link,
     no GitHub link, no methodology post). Shares an ordinal-regression
     skeleton with the simulator because that is the right structural
     fit for Star Ratings — not because one is a rewrite of the other.
  A future agent should not "consolidate" the two project cards, cross-
  link the internal tool to the public methodology posts, or add a
  GitHub/demo link to card 01. That would misrepresent the tools.

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
  for every archive post — only the listing placement changes. Do not
  delete the archive; it is kept online for provenance. If a new post
  somehow belongs in the archive (e.g. personal essay that breaks the
  portfolio voice), tag with an explicit `archive: true` frontmatter
  field would need to be added — not currently implemented, only the
  date cutoff exists.

Experiments section:
  Rendered at the bottom of blog/index.html. Hard-coded list in
  build_blog.py (EXPERIMENTS constant) pointing to small interactive
  pages that don't fit the long-form format. Currently: /life-in-weeks/.
  /star-rating-predictor/ (Stars Cliff Simulator), /skillsprout/, and
  /epidemic-simulation/ are deliberately NOT listed here — they have
  first-class project cards or writing-section entries on the homepage,
  and adding them to an Experiments appendix would demote them.

Shared prose styles live in /blog.css (referenced by all generated pages).
Portfolio index.html keeps its CSS inline — do not extract.

Client-side CDN features on blog posts, loaded conditionally:
  KaTeX 0.16.11     — only when post contains `$...$` or `$$...$$`
  Mermaid 11        — only when post contains ```mermaid fenced blocks
  Prism 1.29.0      — only when post contains other fenced code blocks
No Python deps for any of these — they load at render time, not build time.
The main site (index.html) has no such scripts; no-build rule is intact.

Local build:
  pip install -r scripts/requirements.txt
  python scripts/lint_blog.py   # source-side lint (see below)
  python scripts/build_blog.py

GitHub Action: .github/workflows/build_blog.yml
  Triggers on: push under src/content/blog/ or scripts/ or the workflow itself,
  plus manual workflow_dispatch
  Runs lint_blog.py, then build_blog.py.
  Commits generated HTML + sitemap.xml back to the repo.
  Requires: Settings → Actions → Workflow permissions → Read and write

Lint step — scripts/lint_blog.py:
  Enforces the three storage-side rules below against
  src/content/blog/*.md (skipping drafts and `_`-prefixed files).
  Runs before build_blog.py in CI; the build fails loud if the lint
  fails. Run locally before pushing to catch issues pre-CI.
  Checks:
    1. HTML comments (`<!-- -->`) in a non-draft post — leak as
       visible `&lt;!-- --&gt;` text.
    2. A fenced code block nested inside an HTML comment — breaks
       the tail of the document into escaped text.
    3. A blockquote line starting with a Mermaid keyword
       (`> flowchart LR`, `> graph TD`, etc.) — Mermaid never sees
       it; arrows escape to `--&gt;`.
  Comments or blockquotes that appear as literal examples inside a
  fenced code block are ignored by design.
  If the linter false-positives on a legitimate construct, fix the
  post to match the rule — do not weaken the linter.

Underscore-prefix convention:
  Any src/content/blog/_*.md is skipped by the build.
  Used for fixture markers, meta-docs, and not-yet-ready drafts kept on disk.

Scaffolded drafts must stay drafts — storage-side rule:
  A post outline with `<!-- author-note -->` HTML comments (and/or a fenced
  ```mermaid / ```code block nested inside one of those comments) must ship
  with `draft: true` or an `_`-prefixed filename. Otherwise the comments
  leak onto the live page as literal `&lt;!-- ... --&gt;` text, and a nested
  fenced block causes markdown-it-py's HTML-block parser to drop into
  escaped-text mode for the rest of the document. Happened once on
  `hedis-measure-etl-patterns.md` (scaffolded with `ZAHER:` author notes,
  shipped with `draft: false`); `scripts/lint_blog.py` now fails the CI
  build if the pattern recurs.
  Fix the post, not the pipeline — `protect_math`, the HTML-comment
  handling, and the mermaid rewrite are all intentional; the bug was
  storage-side. Do not change `build_blog.py` or its markdown-it options
  to work around an unfinished scaffold. Do not weaken the linter either —
  the right response to a lint failure is always to fix the post.
  When a post is genuinely ready, remove the author-notes before
  flipping `draft: false`. Finished posts do not contain `<!-- -->`
  blocks outside of fenced code, and do not nest fenced blocks inside
  HTML comments under any circumstances.

Formula storage conventions:
  Inline math: `$...$`. Display math: `$$...$$`. KaTeX auto-renders
  both at page load (see Stack §(e), conditional CDN). `$` inside
  fenced code blocks or inline backticks is shielded by `protect_math`
  in build_blog.py — don't escape shell `$VAR`s or hand-write `\$`.
  Do not nest display math inside a list item or blockquote where
  blank lines would break the `$$...$$` pair across blocks; put
  display math in its own paragraph.

Diagram storage conventions:
  Diagrams must live in a fenced ```mermaid block. The build script
  (`rewrite_mermaid` in `scripts/build_blog.py`) detects the
  language-mermaid fence, rewrites the rendered `<pre><code>` to
  `<pre class="mermaid">`, and Jinja conditionally loads the Mermaid
  ESM runtime only on posts that have one (see Stack §(e)).
  Do NOT write a diagram as a blockquote ("> flowchart LR / > A --> B")
  to dodge the fenced-block ceremony — markdown-it renders that as
  prose with literal `--&gt;` arrows escaped on the page, and Mermaid
  never sees it. Happened once on `llm-inference-is-not-bigger-inference.md`
  and `what-llm-systems-teach-healthcare-it.md` (five diagrams across
  the two posts, all converted to fenced blocks); `scripts/lint_blog.py`
  now fails CI on any `> flowchart`, `> graph`, `> sequenceDiagram`, etc.
  ASCII or Unicode box-art is fine if a diagram is small and the post
  doesn't otherwise need Mermaid — keep it inside a plain ```text fence
  so monospace and arrows render as intended.

The portfolio writing section shows 6 recent posts with a "View all
writing" link pointing to /blog/. The writing section in index.html is
hand-maintained (see Design decisions §Writing section update rule).

---

## Resume pipeline

/resume.pdf is generated from /resume.md on every push.
Source of truth is the markdown. The PDF is a build artifact.

Build script: scripts/build_resume.py
  Uses markdown-it-py + Jinja2 + WeasyPrint
  Reads src/content/resume.md
  Applies scripts/templates/resume/resume.html (print CSS, Tufte palette)
  Regex post-pass wraps role-header blocks (org | title / date / stack)
  in a structured <header class="role"> element for CSS targeting
  Renders directly to resume.pdf at repo root
  Target: 1–2 pages, US Letter, ATS-parseable (single column, no tables)

Bundled fonts (OFL-licensed, committed):
  scripts/fonts/EBGaramond-Variable.ttf
  scripts/fonts/EBGaramond-Italic-Variable.ttf
  scripts/fonts/OFL.txt

Local dev setup (macOS, one-time):
  brew install pango            # WeasyPrint needs pango + cairo + glib
  pip install -r scripts/requirements.txt
  DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib python scripts/build_resume.py

GitHub Action: .github/workflows/build_resume.yml
  Triggers on resume.md, templates, fonts, or the build script
  Installs pango/cairo/glib on Ubuntu runner, runs build_resume.py,
  commits regenerated resume.pdf back to the repo
  Requires: Settings → Actions → Workflow permissions → Read and write

Do not rebuild resume.pdf by hand. Edit resume.md and push; CI regenerates
the PDF. If you need a local render, use the command above.

---

## Portfolio pipeline (activity grid + citation counts)

index.html is hand-maintained, with two build-time insertions:

  1. Activity grid — a 52-week dot grid above the Writing section,
     shaded by post count per week. Sourced from blog frontmatter.
  2. Citation counts — Semantic Scholar lookups for publications
     tagged with `data-sid="PMID:..."` or `data-sid="DOI:..."`.

Build script: scripts/build_portfolio.py
  Reads blog frontmatter, builds the grid HTML, injects between
    <!-- activity-grid:start --> ... <!-- activity-grid:end --> markers.
  For each <div class="pub-entry" data-sid="..."> it fetches citation
    count from Semantic Scholar's public API and appends
    <span class="pub-citations">N citations</span>.
  Graceful degradation: if the fetch fails (rate limit, network), the
    existing span is preserved. Running twice is idempotent.

GitHub Action: .github/workflows/build_portfolio.yml
  Triggers on:
    - push to index.html, scripts/build_portfolio.py, or blog posts
    - Sundays 06:00 UTC (scheduled refresh for citation counts)
    - manual workflow_dispatch
  Commits regenerated index.html back to the repo.

Semantic Scholar's public tier is aggressively rate-limited (HTTP 429).
The script retries with exponential backoff (1s between requests, 2s/4s
on retry). If a lookup still fails, the weekly cron will pick it up
on the next run. Do not add an API key without discussion.

Adding a new publication with a citation count: add
`data-sid="PMID:..."` (or `DOI:...`) to the <div class="pub-entry">,
push, and the workflow populates it.

---

## Pre-push testing checklist

Walk this list in a browser against the local preview before any
substantial push. (Originally written as a pre-swap checklist; the
swap is done, but the list remains useful as a standing ritual.)

- [ ] `python scripts/lint_blog.py` is clean (if blog sources changed)
- [ ] All internal anchor links resolve
- [ ] All external links open correctly
- [ ] Dark mode renders correctly in both Chrome and Safari
- [ ] GoatCounter fires on page load (check network tab)
- [ ] Resume PDF downloads
- [ ] Career arc SVG renders at 320px viewport width
- [ ] Scroll behavior works on nav links
- [ ] No horizontal overflow on any section except career arc
- [ ] Print: nav and footer collapse, content renders on two pages maximum
- [ ] Lighthouse accessibility score above 90
- [ ] Expand/collapse works on Health Catalyst and UW-Madison entries
- [ ] Expand/collapse works on both testimonials

---

## TO-DOs (in priority order)

1. ~~Create github.io-redesign repo and enable GitHub Pages~~ — done
2. ~~Copy v18 mockup as index.html~~ — done
3. ~~Set up blog pipeline (build_blog.py + GitHub Action)~~ — done
4. ~~Migrate blog posts from live site to src/content/blog/~~ — done
   (44 posts in src/content/blog/ on 2026-04-19; fixture marker removed)
5. ~~Add GoatCounter script tag~~ — done (site code `zaher-karp`)
6. Confirm email address (`me@zaherkarp.com`) is the right public-facing one
7. ~~Add scroll behavior to nav links (smooth scroll, active state)~~ — done
   (CSS `scroll-behavior: smooth` + `:has(:target)` active state)
8. ~~Mobile nav: test wrapping behavior, consider hamburger if needed~~ —
   decided: wrap is intentional, no hamburger (see Design decisions §Mobile nav)
9. ~~Commit `/resume.pdf`~~ — done (generated by scripts/build_resume.py from resume.md)
10. Run the testing checklist below before any major push
    (see §Pre-push testing checklist — renamed from pre-swap, now a standing ritual)
11. ~~Swap into the zaherkarp.github.io main repo~~ — done
    (this repo is zaherkarp.github.io; CNAME present; live at zaherkarp.com)
12. Implement `@media print` rules in `index.html` per Design decisions §Print
    overrides. The tokens + behavior are documented (force light, hide nav/
    footer-GoatCounter/career-arc, --rule-light weight, 0.75in margins) but no
    `@media print` block exists in `index.html` yet. The resume template has
    its own print CSS; this item is about the portfolio page only.
13. Audit `.exp-stack` contrast at 0.78rem against WCAG AA. The --text-dim
    token sits at the borderline — measure in both light and dark modes
    before the next substantive accessibility pass. See Design decisions
    §.exp-stack contrast for the flagged concern.
14. Delete merged orphan branches on GitHub:
    `claude/landing-page-redesign-hfREs` and `claude/fix-stars-demo-fdwtU`.
    Both are fully contained in `main` after PRs #1 and the CNAME commit.
    A previous attempt via git push failed with HTTP 403; delete from the
    GitHub Branches page when convenient.

---

## What NOT to do

- Do not install npm, node, or any JS build tooling
- Do not add CSS frameworks (Tailwind, Bootstrap, etc.)
- Do not add React, Vue, or any frontend framework
- Do not change the 640px max-width or reintroduce a multi-column grid
- Do not change the color scheme without discussion
- Do not change the career arc SVG coordinates without recalculating
- Do not copy CSS or structure from the live Astro site
- Do not add animations beyond the existing section reveal and cursor blink
- Do not conflate github.io-redesign (new) with zaherkarp.github.io (live, untouched)
- Do not commit the src/content/blog/*.md test fixtures as the migration — see
  src/content/blog/_FIXTURES_REMOVE_BEFORE_MIGRATION.md for the proper wipe-and-copy flow
- Do not add server-side syntax highlighting (Pygments, etc.) to the blog build;
  Prism runs client-side via CDN to keep the Python pipeline dependency-light

---

## Key people and context

Z = Zaher Karp. Lead Data Engineer at Baltimore Health Analytics.
BHA = Baltimore Health Analytics (current employer).
The portfolio targets: hiring managers for Director-level roles,
  peers in healthcare data engineering, recruiters in regulated healthcare.
Motivated reader register: long-form prose explaining decisions, not bullet scopes.

---

## Vocabulary

Stars = CMS Star Ratings (Medicare Advantage quality measurement program)
HEDIS = Healthcare Effectiveness Data and Information Set
CMS = Centers for Medicare & Medicaid Services
MA = Medicare Advantage
BHA = Baltimore Health Analytics
healthfinch = prior employer, acquired by Health Catalyst in 2020
Health Catalyst = prior employer (2020-2025)
Yau pivot = the design decision to use a single narrow column (640px)
  rather than the Tufte three-column grid. Named after Nathan Yau (FlowingData).

---

## Working agreement

If you think something looks wrong or should be improved, flag it and ask
before changing it. Do not make unrequested changes.
