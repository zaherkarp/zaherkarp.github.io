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

**Timeline Split redesign (2026-07-26, this branch).** The homepage opening was
restructured from a single-column scroll (nameplate + subtitle + full-width
career arc, then About-first section order; About-first survived this iteration
and every later one, ending only with the 2026-07-29 text-ordering pass above)
into a writing-led "Timeline Split":
a full-width three-column `.split-hero` grid (recent writing / a vertical dated
career rail / the featured project 01) above the usual 60% prose column, a
three-card teaser row of in-page quick-jumps, and a reduced nameplate. Nav cut
from nine items to four. Career arc re-rendered as a vertical `tl-rail` SVG (the
wide `tl-horizontal` variant retired). One botanical ornament added to the
project card (a bounded data-ink exception). Design decisions below marked
"(Timeline Split)" supersede the pre-2026-07-26 wording. Council-reviewed; the
mockup family and rationale are in the plan for branch
`claude/page-visual-design-mockups-dk17bc`.

**Writing-led two-column iteration (2026-07-26, Direction B).** A same-day
design-director refinement of the Timeline Split opening. The three-column
`.split-hero` (writing / vertical rail / project scorecard) became a **two-column
asymmetric grid** (recent writing ~62% / current work ~38%) under a new Tier-1
`.proposition` line, with the **career timeline moved to a full-width band below
the columns** (`figure.timeline.career-band`): the wide HORIZONTAL
`svg.tl-horizontal` (viewBox 1200x440, RESTORED from the pre-Timeline-Split hero
arc) on desktop, the vertical `svg.tl-rail` reused for mobile (<=760px), and
`tl-compact` retired. The three-card `.teaser-row`
collapsed to one restrained `.hero-more` line; the six-post writing index moved
into the hero (surfaced as a dated title list, no longer folded); the project's
accept-vs-reject scorecard became a small `funnel-figure`; the academic dot plot
moved to a `#main` sibling before `#publications`; testimonials moved to the
ending (Education/Service/Certifications -> Testimonials -> Contact); nav became
`writing / work / about / contact`. `prefers-reduced-motion` was NOT restored
(owner kept the 2026-06-13 no-gate policy). Where this paragraph and the
sections below conflict on the OPENING, this iteration wins; full rationale +
Council review in `docs/homepage-iteration-2026-07-26.md`. Design decisions
below tagged "(Direction B, 2026-07-26)" mark the superseding wording.

**Text-ordering pass (2026-07-29, this branch).** The opening was rebuilt three
times in four days (Timeline Split, Direction B, the owner hero rewrite) and no
pass re-stitched the prose around the blocks each one moved, so paragraphs,
figures, and labels kept referring to a layout no longer around them. This pass
fixed the reading order rather than the layout. Two approved structural moves:
**G1**, `#about` moved from directly under the hero to between the "More
projects" fold and the academic dot plot, so the four nav targets appear in
exactly nav order and About's methodology paragraph prefaces the academic
record it describes; **G2**, the nav's `writing` item retargeted at the hero
writing column via a new `id="writing-hero"`, since it previously scrolled PAST
the writing to a stub. `#writing` keeps its id, is retitled **"Writing
cadence"**, and gains a one-line lead. The nav also moved OUT of `<main>` into
`<header class="site-header">` so "Skip to main content" actually bypasses it
(WCAG 2.4.1); the header replicates the centering box `main` provided and the
nav renders pixel-identically at 1400/1000/761/600px. Plus: Education and
Service gained leads consistent to-the-word with the Gantt's "2014-15: three
credentials, two roles" annotation, the dot plot's figcaption now points at
Speaking for the Patient Choice Award, the Publications lead acknowledges the
figure above it, `#projects` explains why "Featured" opens at 02, and the hero
lede's two career nouns were swapped to match the chronology the career band
and About both tell. Design decisions below tagged "(Text ordering,
2026-07-29)" mark the superseding wording. Full findings, panel review, and
decision record in `docs/homepage-ordering-review-2026-07-29.md`. One fix
came out of verifying rather than planning: the desktop career arc's "BHA"
band carried an accessible name that never contained the abbreviation it
displays, so speech input could not activate it; see §Career arc SVG for the
band `aria-label` contract that now governs it.

**Experience text reduction, Certifications disabled (2026-07-30, this
branch).** Owner request: cut the Experience prose hard, and comment out
Certifications so it survives in the file and the pipelines but stops
rendering. The joint Focus Group / Design Council convening chose selective
fold retirement: three of the four "More detail" folds retired (BHA,
healthfinch, UW), the Health Catalyst one kept and renamed "Published
customer outcomes" because it holds the page's only third-party verification.
Experience went from 1,209 words to ~570 (−53%), with closed-fold prose from
~698 words to ~42. Both outcome figures stayed. The Huber psi formula was
PROMOTED out of the retired BHA fold into visible prose rather than cut.
`#experience` now closes with a resume/CV pointer and the hero says
"experience" rather than "full experience".

**A SECOND pass followed within the hour**, after the owner said the page was
still "too much to provide value since it probably scares people away" -
reversing the stop-here call above on reception grounds. It cut every Experience
lead to ~35-55 words, put the Huber formula back in a (named) fold, removed the
healthfinch outcome figure, dropped `sn-ehrs`, deleted the `.hero-more` "More:"
line outright, and moved the writing cadence sparkline into the hero beside the
writing list. Page 10,709px to 10,033px, 11.9 to 11.1 screens, visible words
1,834 to 1,665. The reordering question the owner raised in the same breath was
deliberately NOT acted on; it became a study instead, so no section moved.

**A THIRD pass followed**, on the owner's question of whether `#service` could
be cut while staying "active in a pipeline form but not visible", plus whether
`#education` had fluff or combinable parts. Answer: yes to the first, verified
empirically, because `lint_recognition` and `lint_gantt` both slice the section
with a raw-text regex that ignores HTML comments. `#service` is now commented
out with both gates still operating on it; its `id` moved to the Gantt figure,
which becomes the visible service record; fluff was trimmed from both sections
first. A merged single "highlights" section was costed and rejected (it would
make both gates pass vacuously for a ~55px gain). The measurement that shaped
the advice: both sections were ALREADY folded, so they cost 225px each in
closed-state chrome while every entry contributed zero pixels. Page 10,033px to
9,734px, 11.1 to 10.8 screens. Details at §Recognition alignment lint.

**Twenty minutes later the owner asked "isn't it redundant with the figure?"
about `#education`, and they were right: disabling `#service` had made
`#education` MORE redundant with the Gantt, not less, and the two sections were
now getting inconsistent treatment for the same reason.** After the trim, the
chart's labels already stated all five entries' title and date; only the
$18,000 grant and the Carayon/AHRQ detail were not in the chart, and both moved
into the figcaption before `#education` was disabled the same way as
`#service`. Disabling three consecutive sections (education, service,
certifications) also silently removed the rule between the Gantt and
Testimonials, caught by rendering rather than inspection, and restored outside
all three disabled blocks so it survives any future partial restore. Page
9,734px to **9,518px**. Details at §Gantt figure alignment lint and
§Recognition alignment lint.

**The headline number is honest but easy to misread**, so it is repeated in
§Experience entry expand rule: total content fell 53%, while the section's
rendered default height fell only ~2% (2884px to 2836px at 1400px). More than
half the section was already invisible behind closed folds, so this was a
content cut, not a page-length cut. Anyone asked for a *visibly* shorter
Experience should start from the five lead paragraphs, not the folds, and
should measure rather than estimate.

Two defects were caught by rendering and by nothing else: the Certifications
banner originally contained literal comment delimiters and an `<hr>` as prose,
which terminated the comment early and leaked live markup onto the page
(spurious rule, horizontal overflow at 761px and below) while `lint_html`
stayed green; and the trailing `<hr>` has to sit inside the disabled region or
two rules render in a row. Both are documented at §Certifications. Design
decisions below tagged "(Text reduction, 2026-07-30)" mark superseding
wording. Decision record in `docs/experience-text-reduction-2026-07-30.md`.

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
  Scroll-drawn figures (the draw-in motion on select charts) use
  CSS scroll-driven animation (`animation-timeline: view()`), which
  is also NOT JavaScript. See §Scroll-drawn figures below.
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
- `index.html` carries inline CSS (~1,740 lines, the `<style>` block). Do not extract.
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

**As of 2026-07-23 the palette is "Lichen" — moss green**, moved off the prior
petrol teal by owner decision (selected via the palette-committee workflow; see
docs/homepage-critique-2026-07-19.md §8). Pale moss-gray paper (light), deep
moss-slate (dark), a deep-forest-green accent constant in hue across both modes
and lightened for dark-mode AA. The two modes differ slightly by design, bridged
by the shared green accent.

**The palette is now generated from `src/content/palette.yaml` by
`scripts/build_palette.py` and guarded by `scripts/lint_palette.py`** — do NOT
hand-edit the token blocks; edit the YAML and rebuild. See §Palette pipeline.
The values below are the rendered result (kept here for quick reference).

Light mode:
  --paper:  #f3f6f0    /* pale moss-gray ("Lichen") */
  --ink:    #161a16    /* near-black green body */
  --muted:  #5b655c    /* moss gray: dates, metadata, stack lines, sidenote bodies (~5.6:1) */
  --rule:   #d6ddd3    /* hairline rule */
  --accent: #1d6835    /* deep forest green. Used 1-2x per chart maximum, never decoratively. ~6.2:1 */

Dark mode (`@media (prefers-color-scheme: dark)`):
  --paper:  #141915    /* deep moss-slate */
  --ink:    #e3e9e2    /* off-white green so body reads at 21px (~14:1) */
  --muted:  #a3ada4    /* moss mid-tone (~7.7:1, clears AA) */
  --rule:   #293029    /* faint hairline */
  --accent: #6fc082    /* moss green lightened for dark mode (~8.1:1, clears AA) */

Two extra roles the union of consuming files uses (subpages / 404): `--surface`
(elevated panel, light #eaf0e4 / dark #1e241d) and `--ink_sec`/`--text-sec`
(secondary text, light #3c443a / dark #c3ccc1). Both are in palette.yaml.

(History: the site was petrol teal — light `#0a5c54` / dark `#3fb0a0` on Tufte
cream `#fffff8` / cool slate `#16191d` — from the Tufte rebuild until the
2026-07-23 Lichen move.)

**Accent discipline.** The Tufte rule is one or two accent uses per chart,
never decoratively. On the homepage that's roughly: the 4.0 cliff line +
$50M label in the cliff curve, and the "after" bars in the two Experience
outcome figures. (The news-triage scorecard's two accent uses were removed
2026-07-26 when it became the accent-free `funnel-figure`; the accent
occurrence count dropped 18 -> 16.) A handful of total uses on the page.
The career arc and the Education/Service Gantt deliberately use NO accent
(see §Career arc). Subpages, blog post links, buttons, and other chrome use
--ink or --muted, not --accent. The prior site used --accent 32+ times
across links/section labels/project numbers/details summaries/activity
dots — that's the pattern to NOT re-grow.

**(Timeline Split, 2026-07-26) One decorative ornament, bounded exception.**
A single botanical sprig (`.hero-sprig`) sits at the foot of the featured-
project card: `aria-hidden`, drawn in `var(--rule)` via the `#d0d0c8` palette
sentinel (so it is faint and NOT an accent use), never near the rail axis. This
is the page's ONLY decorative (non-data-ink) mark, a deliberate, discussed
exception to the data-ink rule. Do not multiply it: no ornament in the rail,
the teasers, the footer, or elsewhere without discussion. The pre-push accent
grep is unaffected (the sprig uses `#d0d0c8`, not `--accent`/`#7a0000`).

**SVG palette adaptation.** Figure SVGs hardcode hex values
(fill="#111", "#6a6a6a", "#7a0000", "#d0d0c8") as presentation
attributes. CSS attribute selectors at the bottom of the inline `<style>`
block override these to var(--ink), var(--muted), var(--accent),
var(--rule) — so the same SVG markup adapts to light/dark without
per-element edits. Do not rewrite SVGs to use CSS classes; the attribute-
selector approach is the locked contract.

Note: `#7a0000` is now a **historical accent sentinel** only. The rendered
accent has moved twice (oxford red, then petrol teal, now Lichen moss green;
see Palette above), but the SVG presentation attributes and the attribute
selectors still key on the literal `#7a0000` string, which CSS remaps to
`var(--accent)` (currently green). This was deliberate: it keeps the SVG
markup, the attribute selectors, and the pre-push accent grep
(`grep -cE -- '--accent|#7a0000' index.html`, cap 20) untouched. So a red
sentinel renders as the accent (green) on the page — do not "fix" the sentinel
hex to match the accent, and do not interpret `#7a0000` in an SVG as an
oxford-red color.

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
column collapses to 100%. Sidenotes become inline toggles at a DIFFERENT
breakpoint, **850px**, deliberately decoupled from the 760px family (see
§Sidenote system); between 761 and 850px you get the inline note
treatment with the desktop layout otherwise.

The prior site used a 640px Yau-pivot column (single column, no margin).
The rebuild restored the Tufte three-zone layout because the sidenote
system needs the margin to live in.

Nav wraps on medium screens. Acceptable and intentional. No hamburger
menu without discussion. **(Direction B, 2026-07-26)** Nav is four items
(writing, work, about, contact) and spans full width, not the 60% column.
`work` targets a new empty `<span id="work" class="section-anchor">` placed just
before `#experience` (which keeps its own id for `lint_facts`); `contact` is
back in the bar. The un-navigated section ids (experience, projects,
publications, speaking, education, service) are still live anchors, reached via
the dot plot and the blog-post navs; do not delete them. **The `.hero-more`
"More:" line that used to reach four of them was REMOVED 2026-07-30** (see the
dated entry above): its targets sat 3 to 9 screens away, which all six
reception panelists read as a promise the scroll could not keep. `#projects` is
still reached from every blog page's nav (`/#projects`).

**(Text ordering, 2026-07-29)** `writing` targets `#writing-hero`, the id on the
hero's `.hero-writing` column, NOT `#writing` (which it scrolled past, landing
on the cadence stub below the writing). `#writing` still exists and is still a
live anchor. All four nav targets now appear in nav order down the page
(`#writing-hero` < `#work` < `#about` < `#contact`), which is what the `#about`
move (G1) bought; keep that property when reordering anything. The nav element
itself lives in `<header class="site-header">` OUTSIDE `<main>` so the skip link
bypasses it; `nav.top` rules and the print rule are selector-scoped and did not
change.

**(Direction B, 2026-07-26) `.split-hero` is a sanctioned exception to the 60%
column.** The writing-led hero is a `<div class="split-hero">` grid, deliberately
NOT a `<section>`, so `section { width: 60% }` and the floating-note margin never
apply to it. It carries no floating notes by design (see §Writing section
update rule for the two suppressed notes: the per-post one and, since
2026-07-30, the cadence tag rollup). Now **two** columns (writing
~1.6fr / current work ~1fr) above 760px, tightening to ~1.4fr/1fr at 761-1000px,
one column below 760px. The full-width `figure.timeline.career-band` sits
below the grid (also a full-width exception). The rest of
the page keeps the 60% column. CSS lives in sections 21 / 21.1 of
index.html; **§20 and §21's MORE LINE block were deleted 2026-07-30 with
`.hero-more` itself** (markup, CSS, and its `@media print` hide rule).

**(Text reduction, 2026-07-30) the writing cadence sparkline now lives INSIDE
`.hero-writing`**, after the "View all writing" line, rather than in its own
`<section id="writing">` a screen and a half down the page. It is a
build-generated region, so its `activity-grid` markers moved with it and
`build_portfolio.py` repopulates them in place. Its `mn-cadence` tag-rollup
margin note is no longer emitted at all: `.marginnote` positions itself with
`margin-right: -60%`, a value calibrated to the 60% prose column, so in the
full-width hero it lands mid-page instead of beside its anchor. Same rule and
same reason as the suppressed per-post note. `#writing` survives as a bare
`.section-anchor` span because external bookmarks may point at `/#writing`;
nothing on this site links to it.

### Hero

**(Owner rewrite, 2026-07-29.)** Sequence: nav, `.nameplate` (h1 alone), a
Tier-1 `<p class="proposition">`, a two-paragraph `.hero-lede`, then the
two-column `.split-hero` grid (recent writing ~62% / current work ~38%), then
the full-width `figure.timeline.career-band`. (A trailing `.hero-more` "More:"
line closed the sequence until 2026-07-30, when it was removed.) The
writing column also carries the cadence sparkline as of that date. The
featured project 01 block is MOVED into the hero (not copied) so the
project CSS counter still numbers it 01 in DOM order. No epigraph, no italic
claim block, no manifesto framing.

**The `.subtitle` category label was REMOVED and its lock lifted.** It read
"Healthcare data engineering and Medicare Advantage analytics." and had been
marked do-not-edit-without-explicit-instruction; the owner gave that
instruction. The proposition now says the same thing in the first person
("I work in healthcare data engineering and analytics."), so keeping both
opened the page on one fact stated twice, which is the additivity rule the rest
of the page is held to. The `p.subtitle` CSS went with it; `.nameplate` keeps
its flex baseline layout so something can sit beside the name again without
re-deriving it.

The proposition is no longer a claim ("I build and write about auditable
analytics systems for regulated healthcare") but a plain self-introduction, and
is now the page's only category statement rather than an addition to one. Its
`max-width` is **54ch, not 34ch**: the shorter line broke after "engineering",
splitting a noun phrase, so do not tighten it back without re-checking the wrap.

`.hero-lede` is the two-paragraph introduction beneath it: the prior-career
thread (public-health research, editorial production) that the career band
states qualitatively but never in words, then one line of expectation-setting.
Held to a ~62ch measure because the hero region is a full-width exception to the
60% column and would otherwise set body paragraphs at 1400px.

Known cost, accepted: the lede pushes `.split-hero` down ~160px and the career
band with it, so the timeline sits further below the fold. That compounds the
§6 writing-column-length item in `docs/homepage-iteration-2026-07-26.md`.

`scripts/build_og.py` and `og-default.png` were updated to match in the same
pass, so the social card and the page agree.

**(Text ordering, 2026-07-29.)** The nav is no longer part of the hero
sequence: it moved out of `<main>` into `<header class="site-header">` so the
skip link works, and now sits above the `<main>` that opens at the nameplate.
Everything from `.nameplate` onward is unchanged.

(Prior Timeline Split, superseded: nav, nameplate, three-column split-hero
[writing / vertical rail / project scorecard], three-card teaser row. Earlier
still, pre-2026-07-26: nav, h1 name, single plain subtitle, full-width career
arc figure; About-first section order, which outlived that layout and ended
with the 2026-07-29 text-ordering pass.)

### Career arc SVG

**(Direction B, 2026-07-26)** The career timeline is a full-width band below the
split hero (`figure.timeline.career-band`, NOT inside the grid). Two SVGs swap at
760px:
  - **Wide horizontal `tl-horizontal` `viewBox="0 0 1200 440"` for desktop
    (>760px).** RESTORED verbatim (from git, `77db71e^`) from the
    pre-Timeline-Split hero arc rather than authored from scratch: three
    qualitative lanes, editorial (y=80, 2007-2014), research (y=170, 2009-2018),
    and the continuous data-engineering line (y=260) split into healthfinch /
    Health Catalyst / BHA segments; dated x-axis at y=320; 26pt italic labels;
    muted 2020 "acquisition" annotation PLUS the two quiet era annotations
    (news-wire syndication 2008, MPH Biostatistics 2014) the narrow rail had
    dropped. Bands are `stroke-width="10"` — the section-18.2 load-draw selector
    keys on that width, so the band traces on load. NO accent. Tested
    coordinates; do not change them without recalculating from scratch.
  - **Vertical `tl-rail` `viewBox="0 0 300 470"` for mobile (<=760px).** Left
    year axis, `y(year) = 25 + (year - 2007) * 21`; three parallel bands
    (editorial x=55, research x=90, data-engineering x=125). Reused verbatim from
    the prior desktop rail; now the intentional NARROW form (dates down the left,
    bands flowing down), not a shrunk desktop. Bands `stroke-width="9"` — the
    18.2 load-draw also keys on that width, so the rail traces on mobile too.
    Carries no era annotations (matching the original narrow-frame rationale).
  Each band in BOTH SVGs is an `<a href="#exp-...">` (DIRECT child of `<svg>`, no
  wrapping `<g>`, so the `svg.tl-horizontal > a` / `svg.tl-rail > a`
  no-underline/hover/focus rules match) with a transparent `<rect>` touch overlay
  and a `<title>`.

The former mobile `tl-compact` (`viewBox="0 0 600 430"`) was RETIRED in this
iteration; `tl-horizontal` was UN-retired (it was dropped in the Timeline Split
for not fitting the narrow rail column, but the full-width band is exactly its
native context, so the tested original came back). The §11 swap rules and §18.2
load-draw selector key on `tl-horizontal` / `tl-rail`.

The 2020 callout was demoted from a loud red dashed+circle+caption accent
to the quiet muted annotation above (2026-06-07): the user wanted chart
uniformity and fewer Catalyst call-outs, and painting all bars accent would
have violated accent discipline. The career arc now uses NO accent at all —
its one former accent use is gone. Do not change SVG coordinates without
recalculating from scratch — they're tested.

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

Mobile (≤850px, NOT 760px): the sidenote/margin-note span hides; tapping
the label reveals it as an indented inline block with a left rule. The
850px threshold resolves the one formally unresolved Design Council
disagreement (§3.4 of the 2026-07-19 critique), settled 2026-07-28 by
measuring rather than arguing: the floating band runs 43ch at 1400px,
31ch at 1000px, 28ch at 900px, 26ch at 850px and 23ch at 761px, with no
overflow at any width. So the band was never broken, but below ~26ch a
two-sentence note stops earning the margin, and the inline form at that
width is ~52ch. Do not "fix" this back to 760px for consistency.

Two carve-outs inside that block:
  - The three `.stat-num` margin stats do NOT collapse. They exist to
    surface a buried number, so hiding them behind a tap inverts their
    purpose; they render in flow and their toggle (label and checkbox)
    is retired so no dead control sits in the tab order.
  - Every remaining toggle label carries a centered 24x24 hit area via
    an absolutely positioned `::before` (WCAG 2.2 §2.5.8), the same
    technique as the SVG rect overlays. `::before` rather than `::after`
    because `.sidenote-number` already spends `::after` on its counter.
    Verify this by hit-testing with `elementsFromPoint`, not by reading
    the pseudo-element's computed width: that read is flaky on inline
    elements and will intermittently report 0px on a target that is in
    fact fully clickable.

Margin block discipline: marginnote spans must contain inline-only
content (no `<p>`, `<ul>`, `<ol>`, `<blockquote>`, `<table>`, `<div>`,
`<pre>`). At narrow viewports a block-level child either renders badly
or breaks the toggle layout. Enforced by `scripts/lint_notes.py`
(check 4, since 2026-07-12; previously a by-hand grep) against BOTH
note flavors — sidenote and marginnote spans share the collapse
layout — with no exemptions (the `.stat-num` additivity escape hatch
does not cover block tags). Still homepage-only; `scripts/lint_blog.py`
does not enforce it.

Sidenotes are homepage-only. Blog posts use KaTeX/Mermaid/Prism for
technical depth, not sidenotes.

Additivity rule (2026-06-11, editorial council): a sidenote or margin
note must not restate facts, numbers, or claims already present
anywhere in the page's prose, measured against the FULL text including
closed folds, not just the default view (engaged readers expand folds
and hit the repeat). Sole exception: `.stat-num` margin stats (see
§Margin stats), which deliberately surface numbers buried inside
closed folds. A note must also be about the sentence it anchors to; an
off-topic note is removed or re-anchored, not kept for the fact's
sake. Enforced (numbers + verbatim-run overlap; semantic restatement
remains an editorial judgment) by `scripts/lint_notes.py`, see
§Pre-push checks.

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

### Scroll-drawn figures (motion)

Added 2026-06-09, after a "visually boring / wall of text" critique. This is
a deliberate, discussed departure from the page's previously static
presentation. The ethos is unchanged in spirit: motion is allowed ONLY as a
restrained, data-tracing progressive enhancement, never as decorative chrome.

Mechanism (CSS section "18. SCROLL-DRAWN FIGURES" in `index.html`):
  - Pure CSS scroll-driven animation via `animation-timeline: view()`. NO
    JavaScript, so the homepage no-JS contract is intact (see §Stack).
  - Lines trace via `stroke-dashoffset` (keyframe `fig-draw`); bars grow
    from their left edge via `scaleX` + `transform-box: fill-box`
    (`fig-grow-x`); squares/area fills fade (`fig-fade`). Keyframes declare
    only the `from` state; `animation-fill-mode: both` holds the natural
    drawn/full value as `to`, so a figure scrolled past renders complete.
  - Gated by `@supports (animation-timeline: view())` only: browsers
    without scroll-driven animation (older Safari/Firefox) get the
    static figure. No JS fallback needed. NOT reduced-motion gated:
    the `prefers-reduced-motion` wrapper (and the 18.5 global reduce
    neutralizer block) were removed SITE-WIDE 2026-06-13 by owner
    decision; all site motion is short, one-shot, data-tracing, and
    runs for every reader. Do not re-add motion gates anywhere
    without discussion.
  - Only `transform`/`opacity`/`stroke-dashoffset` animate (compositor-
    friendly, no layout cost, no LCP hit).

Career-timeline draw-on-load (CSS section "18.2"): **(Direction B, 2026-07-26)**
the timeline is now a full-width band (no longer a peripheral centre rail), so it
earns the first-paint draw on EVERY viewport. The load-draw selector keys on both
`svg.tl-horizontal > a line[stroke-width="10"]` (desktop horizontal) and
`svg.tl-rail > a line[stroke-width="9"]` (mobile vertical), so whichever SVG is
displayed traces on load. The `tl-compact` selector was removed with the variant.
The paragraph below describes the older per-variant behavior for context.
The former hero career arc was
the one figure that draws for EVERY browser, including Safari/Firefox, because
it uses a plain time-based CSS animation (`animation-duration`), not the
scroll timeline. Its bands (`line[stroke-width="10"]` desktop /
`[stroke-width="11"]` compact) trace via `stroke-dashoffset` on page load:
0.85s ease-out per band, staggered 0.35s per `--seq` cascade step (0, 1, 2,
2.3, 2.6), so the full arc settles at ~1.76s with the last label landing at
~1.86s. Each band's dasharray is sized to its own length via inline
`--arc-len`. (Retimed 2026-06-10 from a 0.5s step / ~2.2s settle, Val's
proposal: the data-engineering trio must finish inside the first-scroll
patience window.) This is the
deliberate first-impression "tantalize." Ungated (runs for every reader,
per the 2026-06-13 no-motion-gates decision); only
stroke-dashoffset animates so there is no LCP cost on the h1/subtitle above.
Rationale: the scroll-driven figures below are Chromium-only today, so Safari
readers would otherwise see no motion at all; the hero load-draw guarantees
everyone gets the effect at least once. The bands draw in a deliberate
sequence (editorial, research, then the data-engineering trio): each band's
label+line is wrapped in a per-role link (see "Clickable bands" below) that
carries its cascade index inline as `style="--seq:N"`, and the band line
carries its own length inline as `style="--arc-len:L"`. `--seq` inherits from
the link to both the line (band draw delay = `--seq * 0.35s`) and the label
`<text>` (`label-fade`, +0.45s), so the name lands as the bar arrives. No
`:nth-of-type` addressing; the per-band values live on the markup.

Clickable bands (added 2026-06-09): each career-arc band, in BOTH
`tl-horizontal` and `tl-rail` (`tl-compact` was retired 2026-07-26), is wrapped in `<a href="#exp-...">` that
jumps to its role in Experience: `#exp-bha`, `#exp-catalyst`,
`#exp-healthfinch`, `#exp-uw`, `#exp-sustainable`. Those ids sit on empty
`.role-anchor` spans placed just before each role `<h3>`, NOT on the `<h3>`
itself (an id on the heading breaks `lint_facts`'s `<h3>` regex). The links
are keyboard-focusable, so the focus-plus-context hover below fires on
`:focus` too; pointer cursor is the affordance. Touch hit areas
(2026-06-10, Luke/Haben): each band `<a>` carries a transparent `<rect>`
overlay sized to ~24px+ rendered height, and the publication-dot links get
a transparent 40-unit CSS stroke, so the targets clear WCAG 2.2 §2.5.8 on
touch without changing a visible pixel or any tested coordinate. Keep the
overlays when editing band markup.

**The two 2019 dots were separated 2026-07-29; the old "spacing exception"
note here was wrong.** It described them as merely overlapping hit areas.
They did not overlap, they OCCLUDED: at 18 units apart under the shared
40-unit stroke, Academic Medicine's hit area covered HERD's centre entirely,
and being later in source order it won. HERD was unreachable by pointer at
every viewport, clicking it navigated to `#pub-acadmed`, and hovering it
revealed the Academic Medicine label. Measure this kind of claim with
`elementsFromPoint` at the mark's centre, not by eye.

The arithmetic that governs any future edit: with the 40-unit stroke the two
hit circles have radii of 27 and 25 units, so centres must be **>= 52 units
apart** or one swallows the other. The wide chart has 105 units per year, so
the pair now straddles the 2019 tick (x=1145) at 1118 and 1172, and the axis
terminus moved 1160 -> 1180 to still run past the rightmost dot. Every wide-
chart dot now clears 24 CSS px from 1400px down to 761px.

**The mobile chart cannot match this, and that is permanent, not a TODO.** A
year is 38 units there while the full stroke needs 47 units of separation, so
compliance would require the dots to misstate their own date. They sit at
402/422 (the widest the year axis absorbs) with a narrower 12-unit stroke via
`.dp-tight`, so both are reachable but both fall under the 24px floor below a
440px viewport. Do not "fix" this by widening the gap; that trades a target-
size miss for a data error. Do not widen `.dp-tight` either, it is sized to
exactly not reach the neighbouring centre.

Measure hit areas by probing outward from a centre with `elementsFromPoint`,
NOT with `getBoundingClientRect`: the transparent stroke is excluded from the
box, so a 46px target reads as 8px and every dot looks broken.

Dot coordinates remain otherwise locked. This move was owner-approved after
the panels deadlocked (Haben refused to leave a control unreachable; the
alternative, shrinking strokes, left a target that degrades as the viewport
narrows).

**Band `aria-label` contract (2026-07-29, WCAG 2.5.3 Label in Name).** Every
band `<a>`'s `aria-label` must CONTAIN that band's visible `<text>` label
verbatim, because speech-input users activate a control by speaking the label
they can see. The desktop arc labels the current role "BHA" while its
accessible name read "Baltimore Health Analytics, ..."; saying "click BHA"
matched nothing, so the abbreviation was fronted (`"BHA, Baltimore Health
Analytics, 2025 to present. Jump to the current role."`). The mobile `tl-rail`
needed no change: it labels that band "Baltimore Health", which the name
already contains. If you rename a visible band label, update its `aria-label`
in the same edit. This is an attribute-only contract; it touches no
coordinate, no `<title>`, and no rendered pixel.

**Do not chase Lighthouse's `label-content-name-mismatch` on these bands.** It
flags all five, before and after the fix above, and always will: axe reads
"text inside the element" as `textContent`, which concatenates the visible
`<text>` label with the `<title>` nested in the band line ("BHABaltimore
Health Analytics, 2025 to present"), and that mashed string appears in no
accessible name. Four of the five bands had clean prefix labels the whole
time. Silencing it would mean moving `<title>` out of the link, which is the
documented all-browser accessible layer for these marks (see the hover/focus
section below). The audit carries weight 0, so accessibility scores 100 in
both modes with it present. Verify Label in Name by checking containment
directly, not by reading that audit.

Hover / focus, focus-plus-context + typeset reveal (CSS section "18.3"):
a Design Council pass replaced the dead native-tooltip *feel* with the chart
reacting. The native `<title>` stays on every titled mark (all-browser,
screen-reader exposed) as the accessible layer and universal fallback; on top
of it, CSS-only `:hover`/`:focus` adds, via `:has()` (Safari 15.4+):
  - **Focus-plus-context:** engaging one mark dims its siblings
    (`figure:has(mark:hover) mark:not(:hover) { opacity }`) and leads the eye
    with no popup. Applied to the career-arc bands, the Experience outcome
    bar pair, and the dot-plot dot field.
  - **Self-emphasis:** arc bands thicken; dots enlarge (`transform: scale`,
    `transform-box: fill-box`).
  - **Typeset label (dot plot only):** each of the six publication dots
    carries a hidden `.dp-label` `<text>` (journal + year, `fill="#111"` so it
    adapts via the palette selectors) that fades in on hover/focus as the
    VISUAL layer; the full paper title (sourced from `publications.yaml`)
    stays in `<title>`. **Labels are spelled out, not acronyms (2026-07-29):**
    the old `WCEL` / `JIHI` / `IJHM` / `HERD` were unreadable and contradicted
    the Publications fold summary below, which names every venue. Where a real
    short name exists it is used ("World Conference on E-Learning" drops a
    conference title's trailing sectors; "Health Environments Research &
    Design" drops HERD's trailing "Journal"); the rest are the shortest
    correct form. Do NOT switch to NLM style: it would regress Implementation
    Science to "Implement Sci" and Academic Medicine to "Acad Med", and HERD's
    registered NLM abbreviation is literally "HERD".
    Length is free here because `.dp-label` is `pointer-events: none` and only
    the hovered label is ever visible, so text never collides and no hit area
    moves. The ONLY constraint is the 1200-unit viewBox edge: a label centred
    on a right-side dot clips, so the three at x>=1040 use `text-anchor="end"`
    at x=1188. Measure with `getComputedTextLength()` before changing wording.
    Each dot `<a>`'s `aria-label` must CONTAIN its visible label verbatim
    (WCAG 2.5.3), the same contract the career-arc bands carry; the mobile
    chart has no visible labels but its `aria-label`s were spelled out in the
    same pass.
Triggered on `:hover` AND `:focus` (the publication dots are `<a>` links, so
keyboard users get the reveal; the title text covers the non-focusable marks).
Presentation dots stay unlabeled (de-emphasized) but share the dim/scale.
Only opacity/transform/stroke-width change.

Arrival cue (CSS section "18.4", added 2026-06-10): a band click jumps to
its role anchor, and `.role-anchor:target + h3` plays a one-shot 1.6s
ink-wash fade (7% ink, `role-arrive` keyframe) so the landing acknowledges
the click. Fade family only, no accent, no persistent state; sanctioned by
Val as an application of the existing fade primitive to text (the page's
one background-color animation; do not extend the pattern elsewhere
without convening her). Ungated, like all site motion since 2026-06-13.

Scroll-animated figures (Chromium-only enhancement): the two Experience
outcome bars, the Projects cliff curve (stroke traces, area fill fades), and
the Education/Service Gantt (date-range `line[stroke-width="4"]` bars trace,
single-year `rect` squares fade). Their `animation-range` ends at `entry 100%`
so a figure is fully drawn by the time it is entirely on screen; an earlier
`cover`-based end once left figures stuck mid-draw (blank) when jumped to via
an in-page anchor.

Gantt staggered cascade + cross-browser fallback (2026-06-12, CSS sections
"18" / "18.1"): the Education/Service Gantt was given the career arc's
choreographed feel. Each data mark carries an inline `style="--seq:N"` keyed
to its START YEAR (BA 2003 = seq 0 ... Spirit of Charlie 2021 = seq 8; marks
sharing a start year share a seq), so the figure draws as a left-to-right
temporal cascade rather than all at once. Because scroll timelines ignore
`animation-delay`, the scroll path staggers via `animation-range-start`
(`entry calc(5% + var(--seq) * 6%)` for bars, `35% + var(--seq) * 5%` for
squares). A sibling `@supports not (animation-timeline: view())` block (18.1)
adds a TIME-BASED load-draw so Safari/Firefox animate too, reusing the same
`fig-draw` / `fig-fade` keyframes (hoisted above both `@supports` blocks so
the negative branch can see them; keyframes declared inside a positive
`@supports` are invisible to its sibling) and the same `--seq` cascade via
`animation-delay`. Honest caveat: the Gantt
sits below the fold, so on those browsers the fallback fires on page load
while off-screen and is usually settled before it is scrolled to (the weaker,
fold-limited cousin of the hero's all-browser draw). A real on-scroll reveal
there would need JS, which the no-JS contract forbids, so this is the
contract-respecting "everyone gets some motion once" gesture. No new motion
primitive was introduced (only the existing trace + fade, plus the existing
`--seq` staggering pattern), so the three-primitive coherence rule holds. The
`style="--seq:N"` attribute is inert to `lint_gantt.py` (it reads only the
coordinate attrs and the `fill="#111"` / `stroke-width="4"` filters).

Deliberately NOT animated: the hero career arc (above the fold, no scroll-
entry to drive it; animating it would jank first paint) and the academic dot
plot (its dot field would need per-dot staggering, a motion vocabulary this
set avoids). Keep the vocabulary to these three primitives; do not add a
fourth easing/transform style without discussion (Val's coherence rule;
lane transferred from Massimo when Val was seated, 2026-06-10).

### Wall-of-text / typographic rhythm (2026-06-09)

A recurring "visually boring / wall of text" critique drove the figure and
motion work above, plus a final typographic pass. Two things a fresh session
should know:
  - **Inline sparklines were tried and REMOVED.** A presentations-per-year
    sparkline in the Speaking lead and a publications-per-year sparkline in a
    Publications lead read as confusing noise at that size and were rolled
    back. Do not re-add small inline charts to break up prose; they look like
    clutter here, not signal.
  - **The wall is treated as a typography problem, not a missing-chart
    problem** (Design Council consensus; the page already carries ~10
    figures). The applied fixes: the long About paragraph was split into two
    (a rest point between the career-arc bio and the methodology thread);
    `.newthought` small-caps openers were added to the Speaking and
    Publications leads, and a plain one-line lead was added to Publications
    (which previously jumped from `<h2>` straight to the entry list).
    `.newthought` now appears on four section leads (About, Experience,
    Speaking, Publications) — selective, not every section, per the small-caps
    policy. Parallax was considered and rejected (needs JS / Chromium-only
    motion, vestibular + perf cost, does not actually break up text).

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

### Page title convention

Comma separator, name last: `<Page>, Zaher Karp`. Applies to every page
except the homepage. Used by `404.html`, `/colophon/`,
`/star-rating-predictor/`, `/life-in-weeks/`, `/epidemic-simulation/`,
and all generated blog output (`build_blog.py`, which emits
`f"{title}, Zaher Karp"` and `f"Writing tagged {tag}, Zaher Karp"`).

**The homepage is deliberately name-FIRST** (`Zaher Karp, Healthcare Data
Engineering`), and this is not drift. The homepage IS the person; every
other page is a topic within the site. Name-first also puts the search
term at the front of the one result that should rank for it. A 2026-07-28
QA audit counted this as one of "four title variants" and it is not:
name-first-on-home plus name-last-elsewhere is a single coherent rule.
Do not "fix" the homepage to match the subpages.

Two forms were retired 2026-07-28: an em dash in all ~250 generated blog
titles (the em-dash-clean chrome rule, and the pre-push grep does not
reach `blog/`, so it went unguarded), and a pipe on
`/epidemic-simulation/`, the site's only one. That page's title was
trimmed rather than comma-joined, because it already contains a comma and
a colon and a fourth clause read as a run-on.

`resume.html` / `cv.html` keep their own credential form
(`Zaher Karp, M.P.H., Resume`), which is a document title, not a page
title.

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
    markers. **(Timeline Split, 2026-07-26)** these markers live in the
    `.split-hero` left column (`.hero-writing`), NOT inside `<section
    id="writing">`. Rendered as full `.entry` blocks (date + title +
    full-summary). **`homepageMarginnote` is NO LONGER RENDERED on the
    homepage:** the featured entries lead the split hero, which has no floating
    margin, and a second inline-toggle note idiom just in the hero was rejected
    by the Design Council (Edward "a fracture"; Haben a comprehension cost). So
    `build_writing_list()` suppresses the `mn-w-<slug>` note (test:
    `test_writing_list_suppresses_hero_marginnote`). The frontmatter field is
    still read/preserved by the blog tooling; it just no longer surfaces here.
    **(Text reduction, 2026-07-30) `<section id="writing">` was RETIRED and its
    cadence sparkline moved INTO `.hero-writing`,** after the "View all
    writing" line. The two halves of one idea had 1,400px of career band
    between them: the writing list sat at screen 0.5 and its own cadence chart
    at screen 2.3. The `activity-grid` markers moved with it and
    `build_portfolio.py` repopulates them in place, so do not hand-edit
    between them. Its one-line lead and its `<h2>Writing cadence</h2>` went
    with the section, and **`build_activity_grid()` no longer emits the
    `mn-cadence` tag rollup at all** (test:
    `test_activity_grid_suppresses_cadence_marginnote`) for the same reason
    the per-post note is suppressed: `.marginnote` uses
    `margin-right: -60%`, calibrated to the 60% prose column, so in the
    full-width hero it lands mid-page rather than beside its anchor. The tags
    stay reachable at `/blog/tags/`. `#writing` survives only as a bare
    `.section-anchor` span, kept because external bookmarks may point at
    `/#writing` (nothing on this site links to it, verified). `.hero-writing`
    still carries `id="writing-hero"`, the nav's `writing` target.
    (Superseded here: the 2026-07-29 wording that `#writing` holds the
    sparkline, is retitled "Writing cadence", and carries a lead.)
  - **Index** (`WRITING_TILES = 6`): the next six posts after the
    featured pair, between `<!-- writing-index:start --> ... <!-- writing-index:end -->`
    markers. **(Direction B, 2026-07-26)** these markers ALSO moved into the
    hero `.hero-writing` column, below the featured pair, inside a
    `<div class="writing-index hero-index">` (NOT a `<details>` fold anymore).
    `.hero-index` compacts the tiles to a DATED TITLE LIST: `.tile-summary` is
    hidden via CSS and the rows tighten, so the opening surfaces the two featured
    summaries PLUS six more dated titles instead of hiding them behind a
    disclosure (the P1 the 2026-07-19 critique flagged). The build still emits
    full `.writing-tile` markup (date + title + tile-summary) between the
    markers; only the hero CSS hides the summary. `homepageMarginnote` is still
    ignored on tiles. The old sibling "More writing" fold in `#writing` was
    removed when the markers moved.

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

`homepageMarginnote` additivity: the field must be additive to the
post's title and description (no shared numbers, no restated claims),
because the build pulls all three onto the same homepage entry, where
overlap renders as visible redundancy. Enforced source-side by
`scripts/lint_notes.py` (see §Pre-push checks and the §Sidenote system
additivity rule).

This pipeline replaced a hand-maintained list that drifted twice
(missed the most recent post, linked to a draft slug with no `/blog/`
output). The build_portfolio workflow already triggers on
`src/content/blog/**.md`, so new posts populate the homepage on the
same CI run that publishes them.

### Publications fold (2026-07-29)

The six publication entries live inside a `<details class="fold pub-fold">`,
closed by default. The `<details>` and `<summary>` sit OUTSIDE the
`pub-list:start/end` markers, so `build_portfolio.py` still rewrites the
entries and the fold survives regeneration; verified by simulating
`replace_between`. Do not move the markers inside the summary.

**The summary is deliberately not "More".** It names all six venues, so a
reader who judges the record by where the work landed never has to open the
fold, while a scanning reader spends one line instead of a screen. Author
lists and volume numbers are what the fold hides; those were never the
credibility signal. A shorter dot-plot-mirroring variant (`HERD 2019, IJHM
2018, ...`) was built, rendered side by side, and rejected: an abbreviation
the reader cannot decode does not transmit standing, which is the line's only
job. It would have saved at most 92px. Keep the venue names spelled out here
and in the dot plot; the two surfaces must agree.

Section height at 1400px: 1277px -> 254px. The summary runs 3 lines at
1400px and 6 at 390px. Note the column width is NOT monotonic in viewport:
773px at 1400, 552 at 1000, **416 at 761** (narrowest, still yielding 40% to
the sidenote margin), then 532 at 600 once the column goes full width.

**The dot plot stays OUTSIDE the fold** as the visible layer. Its twelve dot
links target `#pub-*` ids now inside it. Browsers auto-expand a `<details>`
when navigating to a fragment within it: verified in Chromium 141 for
same-page clicks, cold deep-links, and mobile. **Firefox and Safari remain
unverified** (not installable in the CI sandbox); auto-expand shipped at
different times per engine, so re-check there before treating it as settled.

**`lint_links.py` cannot guard this.** An id inside a closed `<details>` is
still a real id, so that gate stays green whether or not the jump works. A
regression here is invisible to CI by construction.

### Section lead paragraphs

The four `.newthought` section leads (About, Experience, Publications,
Speaking) are plain `<p>` and inherit body type: 1.4rem, `--ink`, 1.4rem
bottom margin. **No inline styles.** Publications carried
`style="color: var(--muted); font-size: 1.05rem; margin-bottom: 1.4rem"`
until 2026-07-29, which rendered its lead at 17.85px muted while the other
three sat at 23.8px in ink; the `margin-bottom` was a no-op duplicating the
`p` default. Removed. If you add a section lead, leave it unstyled.

Two paragraphs still carry that inline style and are NOT leads, so do not
sweep them in: the writing-cadence sparkline caption (inside the generated
`activity-grid` markers, so a hand edit is overwritten anyway; change the
generator if it ever needs to move) and the Projects note under the
`section-subhead` "Featured" explaining why the featured list opens at 02.
Both are secondary annotations where muted small type is doing real work.

### Testimonials

Three testimonials: two from Health Catalyst directors (recent technical
work) and one from a direct report at Sustainable Clarity, 2013 (the
management craft cited in that role's entry). Italic blockquote pullquote
with thin left border (1px var(--rule)), attribution flush-right below
the quote, full version behind a `<details class="fold">`.
Attribution alignment: `text-align: right` per Tufte tradition. The
prior left-aligned alignment was changed in the rebuild.
This is intentional and complete. Do not treat as a gap to fill.

### Experience entry expand rule

**(Text reduction, second pass, 2026-07-30.) TWO folds in the section, and
both name their contents.** BHA carries `<summary>The robust smoothing, in one
formula</summary>` holding only the Huber psi block; Health Catalyst carries
`<summary>Published customer outcomes</summary>`. Every lead was cut to ~35-55
words, the healthfinch outcome figure was removed, the `sn-ehrs` sidenote was
dropped (its four-EHR content is in the lead), and UW's stack line lost NVivo
and SPSS with the qualitative-methods clause. Measured result: Experience
2,836px to 2,419px, page 10,709px to 10,033px (11.9 to 11.1 screens), visible
words 1,834 to 1,665. Experience notes are now two, both `.stat-num`
(`mn-hc-caregaps`, `mn-uw-cohort`).

**The Huber formula went back into a fold**, having been promoted to visible
earlier the same day. Promoting it cost ~180px and made BHA the second-tallest
role; collapsed it costs ~34px. Deleting it was the alternative and was
rejected: ~34px was not worth losing the page's densest technical evidence and
a canonical §Calibrated claims example. If a future pass wants it gone, that is
a decision about evidence, not about height.

**Per-role heights after this pass**, so the next reader does not re-measure:
BHA 490px, Health Catalyst 684px, healthfinch 456px, UW 445px, Sustainable
Clarity 290px. Catalyst is the outlier at 29% because it alone still has a
figure; see §Outcome figures for the open lever.

**(Text reduction, first pass, 2026-07-30.) One of five entries folds now, not four.**
Only Health Catalyst keeps a `<details class="fold">`, and its summary reads
**"Published customer outcomes"**, not "More detail": with a single fold left
in the section a generic label is exactly the defect
`critiques/critique-index-2026-07-04.md:116` flagged (four identical labels
gave a scanning reader equal reason to skip all four, including the one with
the most distinctive content). What it holds is the page's only third-party
verification, the three `healthcatalyst.com` success-story links, plus the
`37,000` / `72 hours` / `12` that the refill figcaption cites, so those
numbers stay anchored in prose per the Outcome figures rule below. The `+`/`-`
prefix (`details.fold > summary::before`) and the suppressed native marker are
unchanged, and the other eight folds on the page still read "More" or a named
summary. Every lead paragraph stays visible always; Sustainable Clarity is a
single paragraph and still doesn't fold.

The BHA, healthfinch, and UW folds were retired, cutting ~698 words of
closed-fold prose to ~42. Know what this did and did not buy, because the
arithmetic is counterintuitive: the section's **total** content fell 1,209
words to ~570 (−53%), but its **rendered default height** fell only ~2%
(2884px to 2836px at 1400px, measured in headless Chromium). More than half
the section was already invisible, so retiring folds is a content cut, not a
page-length cut. If a future pass needs the section to *look* dramatically
shorter, the levers are the five lead paragraphs (~300 visible words), the two
figcaptions, the promoted formula caption, and the three margin notes. Do not
re-argue this from intuition; re-measure.

**The Huber psi-function formula is now in the VISIBLE layer**, directly under
the trimmed BHA lead, not inside a fold (the fold that held it is gone). It
stays pure HTML/CSS math, no MathJax/KaTeX. It was promoted rather than cut
because `evaluations/hiring-eval-2026-05-23.md:200` calls it "the cleanest 'I
still know what I'm doing under the hood' signal in the Experience section",
and burying the section's densest evidence two clicks deep was the one option
that earned neither restraint nor credit. Its caption is unchanged **verbatim**
and remains a canonical §Calibrated claims example.

Retiring those folds also deleted the `sn-tech-notes` and `sn-medallion`
sidenotes with their host paragraphs, taking two toggles out of the tab order.
Experience keeps three notes: `sn-ehrs` and the two `.stat-num` margin stats
(`mn-hc-caregaps`, `mn-uw-cohort`). Deleting prose is always safe for
`lint_notes` (its checks need material present in BOTH a note and the
surrounding page, so shrinking the page can only relax them). **The inverse is
the trap:** lifting note text up into a lead is what fails it, and its own
calibration comment records it was born catching a shingle that lived in the
BHA lead. Rewrite when promoting; never copy-paste.

The section now closes with a one-line pointer to `/resume.html` and
`/cv.html`. (This pass also retitled the hero's `.hero-more` link from "full
experience" to "experience", but the second pass later that day deleted the
whole line, so only the section-closing pointer survives.) A much shorter
section should not be introduced as "full", and those two documents were
previously reachable only from `#contact` and the footer at the very bottom of
the page.

**Outcome figures (added 2026-06-09; ONE remains as of 2026-07-30).** The
surviving `figure.outcome-figure` (before/after bar pair) sits on the Health
Catalyst entry after the lead paragraph and before the fold, so the densest
section shows data by default instead of pure prose. It carries the section's
only accent use; the page-wide count is now **12** of the 20 cap, down from 14.

**The healthfinch figure was REMOVED in the second 2026-07-30 pass** (the
owner asked for the page to be shorter, saying its length "probably scares
people away"). Its two facts moved into that role's lead prose, where they
still read: sevenfold growth in dashboard users absorbed, and 400+ hours of
report prep retired per quarter. Removing it saved ~180px net of the prose it
added. Note the cost, so it is not re-litigated blind: Experience now shows a
figure on one of five roles, which sharpens rather than fixes the
Catalyst-is-heaviest asymmetry the owner flagged (Catalyst measured 684px, 29%
of the section, against 445-490px for the others). Dropping the last figure
would even that out at ~504px and is the obvious next lever, but it would leave
Experience as pure prose, undoing the 2026-06-09 answer to the wall-of-text
critique. Not done without a decision.

The retained figure is Health Catalyst (refill
turnaround 72h to 12h). The removed one was healthfinch
(dashboard user growth absorbed, a 1:7 ratio). Both use the same
gray-before / accent-after pattern: the "after" bar is the `#7a0000`
accent sentinel, the "before" bar is `#6a6a6a` muted. (The healthfinch
figure was monochrome until 2026-07-23, when the owner chose visual parity
with the Health Catalyst figure over the prior single-accent-per-section
restraint.) The healthfinch figure drew endpoints (~10 to 100+) until
2026-07-28; that is a TENFOLD multiple and contradicted `resume.md`'s
`7x`, which the owner confirmed as correct. Since the true endpoints are
not on record and the counts are client-private, the figure now encodes
the multiple instead: bar widths are exactly 1:7 (50 and 350) and the
labels read `baseline` / `7x baseline`. Do not reintroduce endpoints
without a number that is both public-safe and on record. They
reuse the `.cliff-figure` sizing idiom and the `#7a0000`
accent-sentinel palette-adapter contract; a single viewBox scales each on
mobile (no SVG swap). Numbers must match the role prose exactly. BHA gets no
figure on purpose: it is a scope role too new for a headline outcome, and a
fabricated metric would break the data-honesty rule. This was the fix for a
"wall of text" critique of the Experience section.

**Margin stats (added 2026-06-09).** Three buried headline numbers are
surfaced as `.marginnote .stat-num` callouts (large oldstyle numeral + one
caption line) beside their section: Health Catalyst (373,000 care gaps in
six months, Community Health Network), UW (10,000-adult, 50-year Wisconsin
Longitudinal Study cohort), and Speaking (7 talks in 2015, the peak year,
with the Patient Choice Award). They reuse the `.marginnote` float/toggle
machinery wholesale (visible in the margin on desktop, ⊕ tap toggle on
mobile); only the numeral size is new CSS. The numeral honors the
inline-only marginnote rule. Add more only where a genuinely buried number
exists; do not invent stats to fill margin.

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
    The first two projects in DOM order — currently the Medicare
    Advantage Insight Engine and the Stars Cliff Simulator. Each
    renders as a `<div class="project">` with an inline figure
    (a small `funnel-figure` SVG on the Medicare card, ~200 items/week ▸
    ~20 screened ▸ ~5 that matter, since 2026-07-26 and three-tier since
    2026-07-28; cliff-figure SVG on Stars), full
    prose, links row, and stack line. The hanging number floats left as a large oldstyle figure
    (font-size 2.2rem, color var(--muted)).
  - **Index** (outside the section, as a sibling `<div
    class="projects-index">`, 90% max-width grid): The remaining
    projects as `<div class="project-tile">` small multiples (today:
    Healthcare Workforce Transition Platform, ECDS Shock Index, Care
    Delivery Workflow Changes, Practice Automation Analytics). Tiles
    use `position:absolute` for the hanging number (not float),
    a smaller h3, a `.tile-summary` paragraph (30-50 words), an
    optional `.tile-links` row, and `.stack`. The grid is
    `auto-fit, minmax(240px, 1fr)` so it renders 4 columns at
    desktop and collapses to 1 column at the 760px breakpoint.

A small italic `<p class="section-subhead">Featured</p>` label sits
between the H2 and the first featured project to cue the two-tier
structure. **Keep it.** Its removal was proposed in the 2026-05-23 review
and the owner resolved it `wontfix:` on 2026-06-08 (issue #43): the label
is wayfinding, and the visual contrast alone was judged insufficient. Do
not re-propose without reopening that decision.

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

**Calibrated claims (do not punch up):** The 2026-06-10 Focus Group's
antagonist round (VP of Stars, principal payer-analytics engineer, former
CMS measure developer, health-system CIO) unanimously identified the
page's precision-scoped claims as its strongest asset with expert
readers. Canonical examples: the Huber formula caption ("a tested
proposal, not a deployed customer-analytics component"), the BHA meta
line ("team of two data scientists"), and the platform-outcome
attribution on the 373,000 care-gaps margin stat ("one of the platform's
published outcomes"). The rule: scope every claim to what is verifiable,
attribute platform/customer outcomes to the platform, and name the
metric and denominator behind any ratio (no bare "7x"; client-private
numbers are stated as a labeled ratio rather than invented endpoints,
e.g. the healthfinch figure's `baseline` / `7x baseline`).
Do not edit these markers toward bigger or vaguer numbers, and hold new
figures and stats to the same standard.

**Links:**
  Stars Cliff Simulator (public demo): /star-rating-predictor/ + methodology post
  Healthcare Workforce Transition Platform (SkillSprout): GitHub repo + /blog/onet-reskilling-probabilities/
  Medicare Advantage Insight Engine: live feed at /medicare-advantage-insight-engine/ (served by the SEPARATE zaherkarp/medicare-advantage-insight-engine repo's own GitHub Pages, exposed under the shared zaherkarp.com custom domain, so it is NOT a directory in this repo and won't show up in a filesystem search here) + GitHub repo + /blog/medicare-advantage-insight-engine/
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
    inline vanilla JS. Life milestones in the EVENTS array are hand-
    maintained; blog "thoughts" (a 💭 hollow dot per post, vs the solid
    milestone dot) are generated by scripts/build_portfolio.py between the
    `// blog-thoughts:start/end` markers inside EVENTS, from post frontmatter
    (publishDate + lifeweek_topic, falling back to the prettified first tag).
    Same-week thoughts merge into one dot; milestones win a shared week. Do
    not hand-edit between those markers; the next build overwrites them.
  /epidemic-simulation/ — stochastic SEIRV epidemic simulator, companion
    to /blog/two-states-one-pathogen/. Pyodide + Plotly via CDN.

**SkillSprout subpage removal (2026-05-19):** /skillsprout/ deleted from
this repo; the project survives at github.com/zaherkarp/skillsprout.
The Healthcare Workforce Transition Platform project card links out to
the standalone repo; as of 2026-07-01 it renders as a small-multiples
tile (demoted when the Medicare Advantage Insight Engine took its
featured slot), so the slope-graph figure it carried while featured is
no longer shown. The 900KB
vendored client was the loudest contradiction between the site's
no-bundler discipline and what it shipped; removing it eliminated that.

**Stars tools distinction — two tools, do not conflate:**
  1. Stars Cliff Simulator — public, at /star-rating-predictor/.
     Teaching-oriented, synthetic weights, 4.0★ QBP cliff focus.
     The Stars Cliff Simulator is the second featured project on
     index.html. Both Stars Cliff Simulator methodology blog posts
     (star-rating-demo-methodology.md and
     star-rating-predictor-methodology.md) describe this tool.
  2. Client-Side Stars Rating Predictor — internal, built at Baltimore
     Health Analytics. Cut-point dashboard running against live measure
     feeds for contract-level remediation planning. Source is private.
     As of the 2026-05-21 restructure, this tool no longer has its own
     project card. Two surfaces on the public site reference it:
       (a) The BHA role's LEAD PARAGRAPH in the Experience section
           describes the architectural pattern ("one recent design
           runs the Stars cut-point projection entirely in the
           analyst's browser, so member-level data never leaves the
           machine")
           as a compliance-driven architecture example. This moved
           out of that role's "More detail" fold on 2026-07-30 when
           the fold was retired; the surrounding HEDIS hybrid
           measures paragraph went with it, so the pattern is now a
           single clause in visible prose rather than a paragraph.
           It was deliberately preserved rather than cut BECAUSE
           this section names it as one of only two public surfaces
           for the tool. If a future trim reaches this clause, that
           is a decision to retire a documented surface, not a copy
           edit; update this section in the same change.
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

Blog authoring — scripts/edit_blog.py:
  A small stdlib-curses TUI for creating/editing src/content/blog/*.md: a
  frontmatter form (title, date, draft, tags, description) over a scrollable
  plain-text body pane. Run:
    python scripts/edit_blog.py                 # picker: New post + existing
    python scripts/edit_blog.py --new           # blank new-post editor
    python scripts/edit_blog.py --edit <slug>   # open <slug>.md (slug == positional)
  Saves through python-frontmatter (canonical key order, title first). It is a
  plain text editor by design: no markdown/mermaid/KaTeX render, no preview, no
  syntax highlighting/search. It does have multi-level undo/redo (Ctrl-Z /
  Ctrl-Y or Ctrl-R), across the body and form fields, with same-kind keystrokes
  coalesced and a capped history. Stdlib `curses` + python-frontmatter only, no
  new deps. Dev-only: needs a real TTY, so it never runs in CI (pipe/no-tty
  exits 2). New posts default to `draft: true` (lint_blog skips drafts). Slug is
  derived from the title; editing an existing post's title does NOT rename the
  file (that would orphan /blog/<slug>/ URLs and the homepage writing list).
  Optional frontmatter keys not exposed as fields (homepageMarginnote,
  lifeweek_topic, vocab_exempt) are preserved across an edit, not dropped.

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

Blog figure conventions (inline SVG + load-draw motion):
  Posts may carry hand-coded inline `<svg>` figures inside `<figure>` /
  `<figcaption>` blocks. They use the same palette-adapter contract as
  the homepage: hardcoded presentation hexes (#111, #6a6a6a, #d0d0c8,
  and the #7a0000 accent *sentinel*, which blog.css remaps to
  var(--accent), now moss green) so one markup adapts to light/dark. Every
  figure carries a role="img" aria-label. No blank lines inside the
  `<svg>` (markdown-it HTML-block rule; lint_blog enforces).
  Motion: the load-draw style established in
  medicaid-work-requirements-arkansas.md (mwr- classes) and reused in
  lucas-critique-stars-forecasting.md (lcf- classes) is the canonical
  way to animate post figures. Rules of the pattern:
    - CSS-only, time-based on page load (NOT scroll-driven; post figures
      can sit anywhere relative to the fold). A scoped `<style>` block
      lives in the post markdown with a per-post class prefix
      (mwr-, lcf-, ...) so posts never collide; no blank lines inside
      the `<style>` block either.
    - NOT reduced-motion gated (owner decision, 2026-06-13, applies
      SITE-WIDE including the homepage; see §Scroll-drawn figures):
      figure animations are short one-shot load-draws (under ~3s,
      well inside WCAG 2.2.2's five-second line), so they run for
      every reader. The Arkansas post originally shipped with a
      `prefers-reduced-motion` gate; it was removed in the same pass
      that codified this block, and the homepage's gates (sections
      18/18.2 wrappers and the 18.5 global reduce neutralizer) were
      removed in the follow-up pass. Do not re-add motion gates
      anywhere without discussion.
    - Primitives mirror the homepage vocabulary, nothing else: trace
      (stroke-dashoffset, with the path length passed as an inline
      `--<prefix>-len` custom property), grow (scaleX/scaleY with
      transform-box: fill-box), and fade/pop (opacity, small scale).
      Stagger via inline `animation-delay` on the element. Only
      compositor-friendly properties animate.
    - Choreography is editorial: stagger marks so the figure's
      punchline (an annotation, a final bar, a closing stat) lands
      last.
  No JavaScript in post figures, ever: no D3, no Chart.js, no
  `<script>` in post markdown. The conditional CDN loads (KaTeX,
  Mermaid, Prism) are the only JS a post may trigger. An idea that
  genuinely needs scripted interactivity goes to the blog-experiment
  subpage lane (see §Stack) as its own URL, linked from the post.

The portfolio writing section shows the 2 most recent non-draft posts as
featured entries plus the next 6 as small-multiples tiles, generated by
`scripts/build_portfolio.py` from blog frontmatter. See §Writing section
update rule above for the marker contract.

---

## Blog idea backlog

The stage BEFORE drafting, added 2026-07-25. Source of truth:
`src/content/blog-ideas.yaml`. Shared reader/writer: `scripts/_ideas.py`.
Gate: `scripts/lint_ideas.py`.

**The model, and the thing not to break.** An idea and a draft are the SAME
ledger row at different `status:` values, not two records:

```
  blog idea add ─┐
                 ├──▶ status: idea ──▶ drafting ──▶ published ( ──▶ dropped)
  the phone    ──┘    (no file yet)   (.md exists)  (draft: false)
```

The `.md` file under `src/content/blog/` is not a parallel record; it is the
ARTIFACT that appears at the `drafting` stage, when the item earns a slug.
`slug` is the join key. `added:` never changes, so a live post traces back to
the day the idea was captured. Ideas deliberately carry no file: a slug is a
URL commitment that should not be spent on something that may never be
written, and a file per idea would put every capture into the build, the
linters, and the sitemap surface area.

Do NOT "simplify" this into idea-files-with-a-flag under `src/content/blog/`,
and do not add a second store for drafts. One ledger, one stage field.

**Stages.** `idea` (captured, no slug) / `drafting` (file exists, `draft:
true`) / `published` (file exists, `draft: false`) / `dropped` (retired, row
kept as history). Field contract is documented in the YAML header; the header
comment block above the first entry is preserved verbatim by
`_ideas.save_ideas()` and everything below it is re-dumped, so per-entry
inline comments do not survive a write. No section-divider comments: a stage
changes over time, so any "# --- idea" banner would start lying.

**Every draft must have a row.** Three mechanisms, because a file without a
row is invisible to the funnel (the exact failure this pipeline exists to fix,
after three drafts sat unnoticed for two months):
  - `blog new` writes a `drafting` row as well as the file.
  - `blog idea adopt <slug>` registers an existing draft, backfilling `added`
    from its first commit.
  - `lint_ideas` check 8 reports draft posts with no row. INFORMATIONAL, never
    fails, and scoped to `draft: true`: the 60+ published historical posts
    predate the ledger and must not be retro-registered. Same
    hard-gate-one-way / report-the-other-way split as `lint_recognition.py`.

**CLI** (`scripts/blog`, see scripts/blog.md): `idea add|list|drop|restore|
adopt`, `promote <id>` (the idea→draft transition), `queue` (the funnel as ONE
staged table, longest-stuck first). `publish` moves the row to `published` and
stages `blog-ideas.yaml` in the SAME commit as the post, so the two halves can
never be one commit out of step; `draft` walks it back.

**Staleness is measured from the last commit touching the file, NOT
`publishDate`.** publishDate is the intended date, so a draft dated in the
future reads as permanently fresh. Buckets: fresh <14d, aging <45d, stale 45d+
(`FRESH_DAYS` / `AGING_DAYS` in `_ideas.py`).

**Mobile capture.** `.github/ISSUE_TEMPLATE/blog-idea.yml` is a GitHub issue
form (a native form in the phone app). `.github/workflows/blog-idea-intake.yml`
runs `scripts/blog_ideas_intake.py` to append the row, lints, commits, comments
the assigned id, and closes the issue. Idempotent via `source: issue#N`, which
matters because the `labeled` trigger fires on the template's own label.
Em-dashes are stripped on the way in rather than rejected: a phone keyboard
produces them readily and a capture is not worth failing CI over.

**Weekly digest.** `.github/workflows/blog-backlog-digest.yml` (Mondays 13:00
UTC) keeps ONE rolling issue labeled `blog-backlog`, body regenerated from
`scripts/blog_backlog.py` (same `backlog_snapshot()` the CLI renders, so the
two surfaces cannot disagree). The body refreshes silently; a COMMENT is posted
only when an item NEWLY crosses a threshold (draft 30d untouched, idea 90d
idle), with prior state stashed in a trailing `<!-- blog-backlog-state: -->`
comment. Do not make it comment every week: a notification that always arrives
is one you learn to ignore.

---

## Mobile draft editing

A sibling pipeline to the idea backlog above, one funnel stage later: this
one edits an EXISTING `drafting`-stage post, not a bare idea, and (unlike
capture) can move a ledger row all the way to `published`. Model: opening a
"Blog draft edit" issue (the form at
`.github/ISSUE_TEMPLATE/blog-draft-edit.yml`, native in the phone app) hands
`scripts/blog_draft_edit_intake.py` a slug, a full replacement body, optional
title/description/tags overrides, and a "Publish this now" checkbox.
`.github/workflows/blog-draft-edit-intake.yml` runs it, lints, commits, and
closes the issue. This is the phone equivalent of `blog edit <slug>` followed,
optionally, by `blog publish <slug>`.

The script replaces frontmatter fields via targeted regex line substitution
scoped to the isolated `---`/`---` block, not a full `frontmatter.dump`
re-serialize, specifically so a hand-written `# homepageMarginnote: "..."` /
`# vocab_exempt: []` comment line (see `build_frontmatter_block()` in
`scripts/blog`) survives an edit untouched. When "Publish this now" is
checked, it flips `draft: false` and moves the ledger row to `published` in
the same commit, exactly like `blog publish` keeps the post file and the
ledger row in lockstep. `scripts/_ideas.py` now owns both the draft-flag flip
(`flip_draft_false`/`flip_draft_true`) and the ledger-transition helper
(`ledger_set_status`) that `scripts/blog` and this intake script share; see
that module's docstring.

**This pipeline never strips em-dashes**, unlike `blog_ideas_intake.py`'s
ledger-facing `strip_em_dashes`. Blog post sources are explicitly exempt from
the em-dash-clean rule (see the Em dash policy above and the "no em-dash
stripping in blog post markdown sources" line under §What NOT to do); a
mobile edit must preserve that, not regress it toward ledger-style stripping.

The pipeline refuses, loudly, to touch a post that isn't currently
`draft: true` — a typo'd slug or an attempt to edit an already-published post
fails with a comment on the issue rather than silently doing nothing or, worse,
creating the wrong file. **Known limitation:** there is no mobile
"unpublish." An accidental publish is recovered at a terminal with
`blog draft <slug>`.

See `scripts/blog.md` §2b for the phone-callout mechanics and
`docs/pipelines.md` for the full pipeline writeup.

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
  Skills source of truth: src/content/skills.yaml. build_resume's
  regenerate_resume_skills() rewrites resume.md's `<!-- skills:start --> ...
  <!-- skills:end -->` block in place from that YAML (via
  _skills.render_resume_skills) on every build and commits resume.md back,
  so the YAML is canonical, not the resume line. skills.yaml ALSO feeds the
  private job-fit tooling (build_jobsearch / lint_jobfit), so the two must
  agree; scripts/lint_skills.py is the hard gate that the committed resume.md
  block matches what skills.yaml renders (the resume build does not run on
  PRs, so this lint, not the build, is what holds them in sync there). Edit
  skills in skills.yaml and regenerate; do not hand-edit the resume block.
  Shared pipeline for both docs: make_markdown / transform_role_blocks
  (wraps `org | title / date / stack` role headers into
  <header class="role">) / wrap_sections (wraps each ## section in a
  class-bearing <section> by heading text) / split_header.
  Resume target: 1-2 pages, US Letter, ATS-parseable (single column).
  CV: a traditional academic document, deliberately NOT a long resume.
  Sourced from the real academic CV. A brief "Research Interests" replaces
  the resume's Summary, then: Education, Appointments, Past Research
  Positions, Publications (numbered citation list), Presentations, Posters,
  Grants and Funding, Awards and Honors, Certifications, Service and
  Professional Activities.
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
  build_resume.py, or _publications.py. Plus a `workflow_run` edge that
  fires when build_portfolio.yml COMPLETES, so the CV picks up the
  citation counts that run just refreshed into publications.yaml. A
  GITHUB_TOKEN push does not re-trigger workflows, so build_portfolio's
  commit can't fire this build directly; chaining off the portfolio
  workflow completing is the coordination mechanism, not a PAT and not a
  wall-clock cron. The job-level `if` gates the chain to a SCHEDULED or
  manually dispatched portfolio run that succeeded (`conclusion ==
  'success'` AND `workflow_run.event` in `schedule`/`workflow_dispatch`),
  so the frequent push-triggered portfolio rebuilds (every blog post)
  don't churn the timestamped PDFs here; the weekly cadence rides
  build_portfolio's own Sundays-06:00-UTC cron, and a manual portfolio
  dispatch chains a CV rebuild on demand (the rehearsal path, since
  `workflow_run` triggers only ever run the default-branch workflow file
  and so can't be exercised from a PR branch).
  (This replaced an earlier 07:00 cron that merely HOPED portfolio had
  finished by then and silently shipped stale counts when it hadn't.)
  Installs pango/cairo/glib, runs build_resume.py, commits resume.pdf +
  resume.html + cv.pdf + cv.html back to the repo.

Do not rebuild the PDFs by hand. Edit resume.md / cv.md / publications.yaml
and push; CI regenerates all four artifacts. (resume.pdf is not byte-stable
across rebuilds — WeasyPrint embeds a timestamp — but resume.html is.)

---

## Portfolio pipeline (sparkline + citation counts)

index.html is hand-maintained, with three build-time insertions:

  1. Writing cadence sparkline — a 24-week stem chart. One stem per week,
     height proportional to that week's post count; silent weeks render as
     empty space. Trailing total ("N posts") as Tufte's last-point label.
     Sourced from blog frontmatter. Since 2026-07-30 it renders inside the
     hero's `.hero-writing` column (NOT a separate section) and emits NO
     margin note; see §Writing section update rule.
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
  Citation snapshots: on a run where at least one fresh count lands, the
    observed counts are written to data/snapshots/<date>.json (record-on-
    change, so most runs add nothing). The YAML only holds the latest count;
    the snapshots accrete the longitudinal series it discards.
  Life-in-weeks thoughts: also injects a 💭 dot per blog post into
    /life-in-weeks/index.html between the `// blog-thoughts:start/end` JS
    markers (see Subpages above). build_life_thoughts() from frontmatter.
  Deterministic loading: load_posts() sorts the glob so same-date posts
    tie-break on filename; an unordered glob let the auto-committed outputs
    reorder run-to-run.

GitHub Action: .github/workflows/build_portfolio.yml
  Triggers on push to index.html, scripts/build_portfolio.py, or blog
  posts; Sundays 06:00 UTC for citation refresh; manual dispatch.
  Commits regenerated index.html, life-in-weeks/index.html, and any new
  data/snapshots/ (publishing the citation series), gated on the staged diff.

Semantic Scholar's public tier is aggressively rate-limited (HTTP 429).
The script retries with exponential backoff (1s between requests, 2s/4s
on retry). If a lookup still fails, the weekly cron will pick it up.
Do not add an API key without discussion.

Failure visibility: a failed fetch always preserves the cached count
(graceful degradation), but build_publications now distinguishes WHY it
failed so a permanently-broken id can't hide behind the same silence as a
transient 429. fetch_citation_count returns a status, and the build emits a
GitHub Actions `::warning::` separating "unresolved" ids (a non-429 error or
a 200 with no citationCount, i.e. a likely bad/dropped PMID/DOI to fix in
publications.yaml) from "transient" failures (429/network, which the weekly
run retries). A per-entry last-fetch DATE was deliberately NOT added: it
would advance every successful run and force a publications.yaml commit
weekly even when no count changed, the exact churn the build otherwise
avoids; the data/snapshots series already holds the longitudinal record.

Adding a new publication: append an entry to src/content/publications.yaml
(see the header for the field contract; set a `sid` and `citations` to
track a count, or use `links` / `note` for a static entry), push, and the
workflow regenerates the homepage block and the next CV build picks it up.
Do not hand-edit the Publications block between the pub-list markers, the
next CI run overwrites it.

The `note` field must not repeat the entry's venue or year; both
already render in the visible citation line directly below the margin
note. Enforced by `scripts/lint_notes.py` (see §Pre-push checks).

---

## GitHub profile README (external consumer)

The GitHub profile README at `zaherkarp/zaherkarp` (shown on
github.com/zaherkarp) is generated from THIS repo's sources of truth by a
generator that lives in THAT repo, not here. It is a fourth projection of the
same data the resume, CV, and homepage already read:

  - `src/content/skills.yaml` (categories_order + per-skill id/name/category)
    -> the profile's Tech stack badges
  - `src/content/publications.yaml` (title/venue/year/links/citations)
    -> the profile's Research block
  - `src/content/blog/*.md` frontmatter (title/publishDate/draft)
    -> the profile's Writing block (recent non-draft posts)
  - `src/content/resume.md` current "Present" role (`**Employer** | Title`)
    -> the profile's headline title

How it works (all in `zaherkarp/zaherkarp`, none of it in this repo):
`scripts/build_readme.py` reads these files from a shallow clone of THIS
public repo, regenerates four marker-bounded blocks (`title`, `stack`,
`writing`, `research`) with the same `replace_between` injection pattern the
site uses, and commits on a daily cron plus manual dispatch. A ported
`lint_markers.py` guards the marker integrity there. No token crosses repos:
the read side is public and the write side commits to the profile's own repo
with the built-in GITHUB_TOKEN, so this adds NO secret to either repo.
Documented for readers in the site colophon; full pipeline entry in
docs/pipelines.md (pipeline 10).

Implication for edits HERE: the profile is a downstream reader of the field
names above. Renaming a consumed field (a skills.yaml key, a publications.yaml
field, the resume's "Present"-role shape) can silently break the profile,
because its marker lint only catches structural marker damage, not a field
rename. If you rename a field the profile consumes, update `build_readme.py`
in `zaherkarp/zaherkarp` in the same change. This is the project's one
cross-repo coupling.

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

## Critique pipeline

Generates seance-symposium six-camp critique artifacts under
`critiques/critique-<target-slug>-<YYYY-MM-DD>.md`. The first
artifact lives at `critiques/critique-2026-05-23.md` and was produced
before this pipeline existed; treat it as the baseline shape every
subsequent run should match.

Two contract surfaces, both committed to the repo:
  - `docs/critique/methodology.md` — the six camps, voicing critics,
    archetype weightings (personal portfolio / blog post / resume /
    subpage), conflict-resolution rules, and the output structure.
  - `docs/critique/playbook.md` — the prompt-as-document Claude Code
    runs end-to-end. Local invocation: open the repo in Claude Code,
    say "Run docs/critique/playbook.md against index.html." CI
    invocation: `.github/workflows/critique.yml` ships the same
    playbook as the Claude Code Action's prompt.

GitHub Action: `.github/workflows/critique.yml`
  Triggers: `workflow_dispatch` with optional `target` input (default
  `index.html`), plus monthly cron on the 1st. Deliberately not
  push-triggered to avoid commit-loops on the artifact.
  Commits the resulting `critiques/critique-*.md` back to the branch
  via the same github-actions[bot] identity used by the other four
  pipelines.

Independence contract — "not dependent on Anthropic API" means:
  - No `import anthropic` anywhere under `scripts/`.
  - No `ANTHROPIC_API_KEY` referenced in `.github/workflows/`.
  - `scripts/requirements.txt` does not pin the `anthropic` package.
  - The workflow authenticates via `CLAUDE_CODE_OAUTH_TOKEN`
    (Claude Code subscription OAuth), not a raw API key repo secret.
  - Pre-push grep check (`grep -rE 'import anthropic|ANTHROPIC_API_KEY'
    scripts/ .github/workflows/`) returns empty; see §Pre-push checks
    below.

Worth being honest about what the independence buys you: Claude Code
Action still connects to Anthropic's infrastructure. The independence
is structural and economic, not metaphysical. The codebase has no SDK
coupling, the billing path is the existing subscription rather than
separate API credits, and the secret surface is one OAuth token
scoped to Claude Code. Full provider neutrality would require either
a LiteLLM-style Python adapter (which would put an
`anthropic`/`openai`/etc. dependency back in `requirements.txt`) or a
non-LLM rule-based linter (which can't reproduce camp critiques). The
chosen design trades those for simplicity: one runtime, one auth
path, zero codebase coupling.

What this pipeline does NOT do:
  - It does not edit the target file. Every finding is a
    prescription; `APPLY_CHANGES=false` is the contract.
  - It does not propose new sections, pages, or features. Structural
    proposals belong in the §Agent panels framework, not in a
    critique.
  - It does not read prior critique artifacts before running. Each
    run is fresh-eyes against the current state of the target;
    anchoring to the prior run would suppress new findings.

Adding a new target type: extend both `docs/critique/playbook.md`
§Supported targets and `docs/critique/methodology.md` §Archetype
weightings in the same change. Splitting them means the runtime has
to "infer reasonable defaults" the way the 2026-05-23 baseline had
to, which is exactly the failure mode this pipeline was built to
remove.

---

## Palette pipeline

The site's color palette is a single source of truth at
`src/content/palette.yaml` (added 2026-07-19). The five brand roles
(bg / surface / ink / ink_sec / muted / rule / accent, in the union across
files) are defined there for light and dark, plus a favicon fill and a print
accent. `scripts/build_palette.py` injects each file's token block between
`palette:*` marker spans; `scripts/lint_palette.py` gates drift. To change the
palette site-wide, edit the YAML and run `python scripts/build_palette.py`.

Why: the palette was duplicated across ~11 files (index.html, blog.css,
404.html, the three subpages, the four resume/cv templates, favicon.svg) with
DIFFERENT local var names (`--paper`/`--ink` on the homepage, `--bg`/`--text`
in blog + subpages, `--text-sec`/`--surface` extras). That duplication is why
changing the accent felt risky. The pipeline makes it one edit; the lint makes
uniformity enforced rather than remembered.

How the generator maps roles to each file (`TARGETS` in build_palette.py):
  - Markers wrap DECLARATION LINES only (two spans, `palette:light` +
    `palette:dark`), sitting inside whatever `:root` the file already has, so a
    file that mixes color tokens with sizing/Solarized (blog.css) works like
    one whose `:root` is colors-only (index.html).
  - Each target maps semantic roles to its own local names, so one YAML value
    lands as `--paper` on the homepage and `--bg`/`--text` in the blog.
  - Single-mode spans: `palette:print` for the PDF templates' accent and the
    index.html `@media print` accent (kind `accent_only`); `palette:start`
    (XML) for the favicon fill.

`scripts/build_og.py` READS `palette.yaml` directly (light `bg`/`ink`/`muted`)
rather than carrying its own copy. It used to inline them "because this is a
one-off renderer" and duly went stale, painting Tufte cream onto the social card
for months after the Lichen move, invisible to `lint_palette` because that only
inspects files carrying `palette:*` marker spans. Reading the source makes the
drift impossible rather than merely detectable, which is why no lint was added
for it. Re-run `python scripts/build_og.py` after a palette change and commit
the PNG; it is not wired to CI.

Deliberately NOT pipeline-managed (documented in the YAML header):
  - blog.css's Solarized code-block palette (separate, mode-symmetric system).
  - The print neutrals in the resume/cv PDF templates and index.html's
    `@media print` block (paper-calibrated white/near-black; only their
    accent tracks the palette).
  - The two self-contained blog-post figures
    (`medicare-advantage-market-exits-timing.md` `--pc-*`,
    `should-i-buy-ram-now.md` `--rw-*`): they keep their own tokens per the
    blog-figure "renders standalone" convention, but lint_palette Check C
    verifies their accent matches the canonical value so they can't drift.
  - The epidemic simulator's Plotly series colors (categorical rust/forest,
    JS-set in app.js; not the brand accent by design).

lint_palette.py enforces three things (all hard failures, wired into the
pre-push hook and lint.yml): (A) no drift from palette.yaml, (B) no `--accent:`
assigned outside a `palette:*` span in any managed file — the wall that stops
the accent being hardcoded off-token again, value-agnostic so it also catches
a stale old accent after a repalette, and (C) the two post figures match.

The `#7a0000` accent-sentinel contract (§Palette design tokens) is unaffected:
figures still hardcode `#7a0000` remapped to `var(--accent)`; only the
`--accent` VALUE now comes from palette.yaml.

## Recognition alignment lint

`scripts/lint_recognition.py` keeps the homepage "Service and Recognition"
section (`index.html` `<section id="service">`, the `.row-entry` blocks;
**that section is COMMENTED OUT as of 2026-07-30 and the linter still reads
it, deliberately, see below**)
aligned with the comprehensive record in `src/content/cv.md` — awards,
fellowships, and service — WITHOUT a shared data file. Both surfaces stay
hand-authored pure HTML/Markdown; the linter parses each and compares.
This is the deliberate "pipeline, not YAML" answer to the homepage/CV drift
that let the Spirit of Charlie award, Digital Fellow, and IPM award sit on
the CV but never reach the homepage.

Two CV sections plus one Education subsection are reconciled: `## Awards and
Honors`, `### Fellowships and Training`, and `## Service and Professional
Activities` (all `###` subsections).

Matching is intentionally NOT the strict equality `lint_facts.py` uses
(those job surfaces are authored in lockstep; these recognition surfaces are
phrased independently). An entry matches a CV entry when they share at least
one **year** AND at least **two significant tokens** (a small stopword list
drops generic institutional words like "university"/"medicine"/"health" and
bare years). This tolerates "Undergraduate Research Mentor" vs CV
"Undergraduate Research Scholar Mentor", or "IISE ..." vs CV "Institute of
Industrial and Systems Engineers ...", with no hand-maintained synonym
table. If a future entry genuinely needs help, widen `STOP` or raise
`MIN_SHARED_TOKENS` — do not add a per-entry alias map (that's the
maintenance burden this design avoids).

Two outputs:
  - **Subset gate (hard fail, blocks push):** every homepage `#service`
    entry must have a CV counterpart. The homepage is a curated highlight
    reel, so it may show *fewer* items than the CV (homepage ⊆ CV); a
    failure means something is shown publicly with no CV record, or a rename
    broke the match. Wire-up: §Pre-push checks step 3c.
  - **Coverage report (informational, never fails):** CV recognition entries
    with no homepage counterpart, printed on a manual
    `python scripts/lint_recognition.py` run (the hook swallows stdout on
    success, like the other lints). Most CV-only items — training short
    courses, individual mentees, minor service — are *expected* to stay
    CV-only; the list is an advisory scan, not a to-do. This is the
    direction that surfaces a genuine gap when a new CV award hasn't been
    promoted to the homepage.

**(Text reduction, 2026-07-30) `#service` is commented out, and this linter
still guards it.** Both gates that read the section slice it with a raw-text
regex and neither strips HTML comments: `SERVICE_SECTION_RE`
(`lint_recognition.py:122-124`) and `_section_body` (`lint_gantt.py:179-184`).
So the homepage-subset-of-CV gate and the Gantt alignment check keep operating
on the disabled markup exactly as before. Verified empirically, not assumed:
`lint_gantt` still reports "12 section entry(ies) (5 education + 7 service)
reconciled against 12 figure mark(s)". This is precisely what made hiding the
section possible without weakening a guarantee, so **do not "fix" either linter
to skip comments** without first replacing what it guards.

**The visible service surface is now the Gantt figure**, which carries a mark
for every entry (that is what `lint_gantt` enforces). Its figcaption absorbed
the retired section's lead sentence, naming the two 2014-15 roles, and points at
`/cv.html` for orgs and citations. **The `id="service"` anchor MOVED** out of
the disabled section to sit immediately before that figure, because all ~250
generated blog pages link to `/#service`
(`scripts/templates/blog/base.html:50-51`) and **`lint_links` cannot see
blog-to-homepage fragments** - it validates only index.html's own fragments and
homepage-to-blog links. Removing the id would have left 250 dead nav links with
CI green. Keep the anchor wherever the service record is visible.

Fluff was trimmed from both sections in the same pass, before `#service` was
disabled (so a restore brings back the clean version): notes that merely
restated their own titles went (Oxford, Boot Camp), the MPH committee names
became CV-only, the mentor note's six-item skill list became the fact, and the
Spirit of Charlie citation quote went as internal-recognition language. **Kept
deliberately** as recognizable field credentials: Pascale Carayon as advisor,
the AHRQ-funded SEIPS training, the $18,000 grant, and Digital Fellow's
25-of-2,000 selectivity.

**(Text reduction, third pass, same day) `#education` was disabled 20 minutes
after `#service`, for a reason `#service`'s disabling had itself created.** The
owner asked directly: "isn't it redundant with the figure?" After the service
trim, the Gantt's terse chart labels ("MPH, Biostatistics", "Oxford, qualitative
methods", "Grad Cert, Patient Safety", "Entrepreneurial Boot Camp", "BA, English
Literature") already stated all five education entries' title AND date. Checked
precisely before acting: only two facts anywhere in the fold were not already in
the chart, the MPH's $18,000 grant and the Patient Safety entry's Carayon/AHRQ
detail. Both were folded into the Gantt figcaption, then the section was
disabled exactly like `#service` (same banner shape, same restore instructions,
`id="education"` relocated beside `id="service"`'s anchor). `lint_gantt` still
reconciles both lanes against the figure (raw-text regex, no comment
stripping); `lint_recognition` never covered `#education` in the first place.

**Disabling THREE consecutive sections (education, service, certifications)
removed a rule the page's rhythm depended on**, and this was caught by
rendering, not by inspection: the Gantt originally carried no rule of its own,
because the three sections after it each supplied one on their way out. With
all three hidden, the Gantt ran straight into Testimonials with zero live
`<hr>` between them (a 48px gap from margins alone, no divider) — every other
section boundary on the page keeps one. Fixed with a single `<hr>` placed
OUTSIDE all three disabled blocks, right before the Testimonials banner, so it
is not a duplicate if any of the three is restored later and does not live
inside any one section's restore instructions.

**A merged single "highlights" section was proposed and REJECTED.** A prose-line
version (the retired Certifications pattern) would run ~170px against 450px, but
it has no `.row-entry` blocks, so `lint_recognition.parse_homepage()` returns an
empty list and BOTH gates pass vacuously - green while guarding nothing. Keeping
them meaningful means re-pointing both at `cv.md` and rewriting two test files,
and the whole exercise beats the simple comment-out by ~55px. Two variants were
also checked and fail: highlights-unfolded measures the same as
everything-folded, and nesting `<section id="service">` inside a merged fold
breaks the outer slice because `_section_body` is non-greedy.

**Certifications are out of scope (2026-06-12), and the section is now
COMMENTED OUT (owner, 2026-07-30):** homepage
`<section id="certifications">` (a deliberately small h2 + one
newest-first semicolon-separated prose line, after #service; a
details.fold version was tried and replaced the same day on Design
Council feedback) pairs with cv.md `## Certifications`.

The homepage section is wrapped in an HTML comment. It no longer renders,
but the markup is kept verbatim in place so the content survives in the
file and through every pipeline. **`cv.md` is now the live record.** An
HTML comment, not `display: none`, was the owner's instruction and is also
the correct mechanism: the content leaves the DOM entirely, so it is not
read by screen readers, not indexed, and not printed, whereas
`display: none` would still expose it to assistive tech. Restoring it means
deleting two delimiter lines; nothing else is required, because no CSS
targets the section (it carries no classes) and nothing links to
`#certifications`.

Two mechanical rules for that block, both learned the hard way in the same
pass. **The trailing `<hr>` must stay inside the disabled region** or two
adjacent rules render between `#service` and `#testimonials`. And **never
write comment delimiters, or a literal rule tag, as prose inside the
explanatory banner above it**: comments cannot nest, so a stray close
sequence ends the banner early and dumps its remaining text onto the page as
live markup. That happened while writing the banner, and it rendered a
spurious `<hr>` plus a long unbroken row of equals signs that overflowed the
page horizontally at 761px and below. **`lint_html` passed the whole time** the
bug was live, because the result was structurally valid HTML, merely wrong.
Only a headless render caught it, which is the §Agent panels
"render before arguing about a rendered thing" rule applying to verification
as much as to design.

Neither linter covers the pair; keep the two lists in sync BY HAND
(currently four entries: Databricks 2024, Sumo Logic x2 2020, Six Sigma
Yellow Belt 2015). Six Sigma moved here out of #service and the CV's
Awards and Honors; the IPM award became CV-only in the same pass; the
Gantt carries neither. DataCamp course completions are deliberately
omitted as entry-level. The section has no figure, no margin notes, and
no nav entry by design.

---

## Gantt figure alignment lint

`scripts/lint_gantt.py` keeps the homepage Education + Service Gantt
(`index.html` `figure.gantt-figure`) in lockstep with the two prose
sections it summarizes, WITHOUT a shared data file. The figure has two
lanes — education (`y < 135`) mirrors `<section id="education">` (also commented
out since 2026-07-30, for the same redundancy reason as service; see below),
service
(`y > 135`) mirrors `<section id="service">` (#service, commented out since
2026-07-30 but still parsed; see §Recognition alignment lint. The figure is now
that content's only VISIBLE surface, which raises the stakes on this lint rather
than lowering them). Each data mark
encodes its year(s) positionally through the chart's own transform
`x(year) = 90 + (year - 2003) * 19`: a single-year square's year is read
back from its centre x, a multi-year bar's start/end from x1/x2. Each
mark is paired with the `<text>` label that follows it in source.

This exists because the figure fell out of date: three recognition items
(Spirit of Charlie, Digital Fellow, IPM award) were added to `#service`
without a corresponding square/bar, and nothing caught it.

**Gate (hard fail, blocks push):** every `#education` entry must have a
matching mark in the education lane, every `#service` entry a matching
mark in the service lane. Matching = share ≥1 year AND ≥2 significant
tokens between the section entry (title + org) and the terse figure label
("UG research mentor" matches "Undergraduate Research Mentor"). A reverse
coverage note (figure marks with no section entry) prints on a manual run
and never fails. The lint uses its OWN minimal stoplist — unlike
`lint_recognition.py` it must keep "research" so the abbreviated labels
still match — so do not share the two stoplists.

**Editing the figure:** the SVG is hand-coordinated. The service lane is
7 rows at `y = 160..280` step 20, the axis sits at `y = 310`, viewBox is
`0 0 600 340`. To add an entry, compute its x from the transform above,
add the square/bar + label, extend the lane and axis if the rows run out,
and run `python scripts/lint_gantt.py`. New squares (`<rect fill="#111">`)
and bars (`<line stroke-width="4">`) inherit the scroll-draw animation
automatically (blanket selectors, no per-element staggering; see
§Scroll-drawn figures).

---

## Pre-push checks (agent-runnable)

These run automatically via `scripts/hooks/pre-push`, installed by
`scripts/_common.install_git_hooks()` on first run of any project script
(no manual setup; multiple machines self-bootstrap on first script run).
The installer is polite: it points `core.hooksPath` at `scripts/hooks/`
only when that config is UNSET, and never clobbers a contributor's
existing `core.hooksPath` (a pre-commit framework, personal hooks); if a
foreign value is found it prints the one-line opt-in command and leaves
the config alone. The local hook is the fast echo; the real, unbypassable
gate is the CI backstop below (`.github/workflows/lint.yml`), so a machine
that declines the local hook still cannot push drift.

Checks:
- `python scripts/lint_blog.py` clean (blog source-side mistakes)
- `python scripts/lint_vocab.py` clean (canonical CMS program-name
  capitalization across blog sources, resume.md, and index.html;
  see §Vocabulary)
- `python scripts/lint_facts.py` clean (cross-surface fact drift between
  resume.md, index.html h3+meta, and JSON-LD; playbook for failures
  at scripts/lint_facts.md)
- `python scripts/lint_notes.py` clean (note additivity: no significant-
  number or five-word-run overlap between a homepage sidenote/margin
  note and the page prose outside it, `homepageMarginnote` additive to
  its post's title+description, publications.yaml `note` free of
  venue/year repeats. `.stat-num` margin stats and the generated marker
  regions are exempt by design; see §Sidenote system additivity rule.
  Also enforces margin block discipline: no block-level tags inside a
  sidenote/marginnote span, no exemptions; retires the by-hand grep in
  §Sidenote system)
- `python scripts/lint_recognition.py` clean (recognition alignment: every
  homepage `#service` "Service and Recognition" entry must have a
  counterpart in cv.md's Awards / Fellowships / Service record. Both
  surfaces stay hand-authored, no shared YAML; the linter parses both and
  matches on year + significant-token overlap, so wording differences
  ("Undergraduate Research Mentor" vs CV "Undergraduate Research Scholar
  Mentor") don't trip it. The gate is one-directional (homepage ⊆ CV: the
  homepage is a curated highlight reel and may show fewer items), so a
  failure means something is shown publicly with no CV record. The
  reverse-direction coverage report of CV-only items is informational
  (never fails) and prints on a manual run. See §Recognition alignment lint)
- `python scripts/lint_gantt.py` clean (Gantt figure alignment: the
  homepage Education + Service Gantt (`figure.gantt-figure`) must carry a
  mark for every `#education` and `#service` entry. The figure is a
  hand-coded SVG; the linter reads each entry's year back from its mark's
  x-coordinate via the chart transform and matches against the section
  entries on year + token overlap, so the figure can't silently fall out
  of date when a section grows. See §Gantt figure alignment lint)
- `python scripts/lint_markers.py` clean (marker integrity: the build-time
  injection markers a generator splices into, `activity-grid`,
  `writing-list`, `writing-index`, `cliff-path`, `pub-list`, `updated`,
  the life-in-weeks `blog-thoughts` pair, and the cv.md `<!-- publications -->`
  placeholder, must pair cleanly (no orphan/crossed/nested/unterminated
  pairs) and still be present, so a stray hand edit can't corrupt a host
  file on the next build or make a generator silently no-op. Add a new
  region's name to `PAIR_MARKERS` in the same change that adds its markers)
- `python scripts/lint_skills.py` clean (skills consistency: resume.md's
  generated `<!-- skills -->` block must equal what `src/content/skills.yaml`
  renders via `render_resume_skills`. build_resume regenerates + commits
  resume.md on main, but NOT on PRs, so this gate keeps the public resume's
  Skills line from drifting from its source, `skills.yaml` (which also feeds
  the private job-fit tooling). Same lockstep contract as lint_facts. Skips
  when skills.yaml or the markers are absent. See §Resume and CV pipeline)
- `python scripts/lint_links.py` clean (internal link + anchor integrity:
  every fragment href in index.html resolves to a real `id=` there (ids
  inside HTML comments / `<style>` / `<script>` don't count as targets),
  every homepage `/blog/...` link resolves to built blog output on disk,
  and every sitemap.xml `<loc>` resolves to a real file in the repo. The
  homepage file-link check is deliberately scoped to `/blog/` because
  `/medicare-advantage-insight-engine/` is served by a separate repo's
  GitHub Pages under the shared domain (see §Links) and has no directory
  here. Retires the "all internal anchor links resolve" eyeball check)
- `python scripts/lint_html.py` clean (HTML structural well-formedness:
  index.html and the generated blog / resume.html / cv.html pages parse
  with tinyhtml5 and carry no tree-builder structural errors, i.e.
  misnested / unclosed / orphan tags, loose table cells, or content
  after `</body>`. tinyhtml5 is already in requirements.txt transitively
  via WeasyPrint. Tokenizer / character-level errors are deliberately
  OUT of scope: a bare `&` in KaTeX LaTeX source and a `--` inside an
  HTML comment do not break the DOM tree and appear in legitimate
  content, so failing on them would false-positive on valid math /
  CSS-doc markup. Replaces the lenient `html.parser` balanced-tag
  eyeball smoke check in README)
- `python scripts/lint_palette.py` clean (palette single-source contract:
  every consuming file's `palette:*` marker block matches what
  `src/content/palette.yaml` renders; no `--accent:` is assigned outside a
  `palette:*` span in any managed file; and the two self-contained blog-post
  figures' accents match the canonical value. See §Palette pipeline)
- `python scripts/lint_ideas.py` clean (blog idea ledger: schema for
  `src/content/blog-ideas.yaml` (unique slug-form ids, valid stage, no
  unknown keys, `added` not in the future, em-dash-clean title/note) plus
  referential integrity against `src/content/blog/` -- a `drafting` row
  must point at a real `draft: true` post, a `published` row at a live one,
  an `idea` row must carry no slug, and no two rows may claim one post.
  The reverse direction (draft posts with no ledger row) is an
  informational report that never fails and prints on a manual run, since
  the published historical posts predate the ledger. See §Blog idea backlog)
- `grep -c '—'` returns 0 across index.html, resume.md, cv.md, and
  life-in-weeks/index.html (em-dash-clean chrome; life-in-weeks's generated
  blog "thoughts" are stripped at the source, this guards hand-authored
  milestones)
- `grep -cE -- '--accent|#7a0000' index.html` ≤ 20 (accent discipline:
  counts both CSS variable refs and SVG literal callouts, since the
  SVG palette adapter expects #7a0000 as the accent *sentinel* presentation
  attribute (it now renders the accent, moss green, via var(--accent); see §Palette).
  Bump the cap only after discussion; ratchet it down when removing
  uses.)
- `grep -rE '<p><(text|line|polyline|circle|rect|polygon)' blog/` returns
  nothing (catches blank-line-inside-`<svg>` slips)
- `grep -rE 'import anthropic|ANTHROPIC_API_KEY' scripts/ .github/workflows/`
  returns empty (critique-pipeline independence contract: no Anthropic
  SDK import, no API-key env var in workflows; see §Critique pipeline)
- `python -m py_compile epidemic-simulation/sim.py` succeeds (the
  Pyodide-hosted simulator model is client-side Python that no build
  step imports, so a syntax error would otherwise surface only
  in-browser at page load; see §Stack blog-experiment subpages)

**Server-side backstop (`.github/workflows/lint.yml`).** The pre-push hook
only fires for contributors who push from a machine that has run a project
script (which installs it). Web-UI edits, fresh clones, the `draft: false`
bypass, and the workflows' own bot commits all skip it, and the
`Blog-CLI-Linted:` redundancy trailer can skip the two CI lints in
`build_blog.yml`. So `lint.yml` runs the FULL suite above (all twelve linters
plus the five guard steps: four greps and the sim.py py_compile) on every
`pull_request` and every `push` to the
default branch, unconditionally, and never consults the redundancy trailer.
The hook is the fast local echo; `lint.yml` is the guarantee. Keep the two in
sync: a check added to the hook belongs in `lint.yml` too (and vice versa).

Not in the hook (run manually for bigger pushes):
- `python scripts/build_blog.py` runs without warnings
- `python scripts/build_resume.py` regenerates resume.pdf

Human-eyeball smoke tests (light/dark render, sidenote toggles, fold
behavior, Lighthouse, print preview, figure rendering, mobile SVG swap)
live in [README.md](README.md) §Before pushing.

---

## Testing

A pytest suite lives at `scripts/tests/`, run with `pytest scripts/tests/`.
Its dev-only deps are pinned in `scripts/requirements-dev.in` /
`scripts/requirements-dev.txt` (separate from the runtime
`scripts/requirements.txt`); `.github/workflows/tests.yml` runs the suite in
CI.

These are **characterization tests**, not a spec: each gate
linters is exercised for both a pass case (against the clean repo tree) and a
violation case, and the build scripts get smoke tests (build_blog pages +
well-formed sitemap/feed XML; build_portfolio marker-injection idempotency;
build_resume skills-block regeneration, with the WeasyPrint PDF render
self-skipping when libpango is absent). Their purpose is to pin current
behavior so the planned script consolidation can be shown to preserve it. They
guard the code that guards the content; the integrity linters above guard the
content. The streamlining + QA program that motivates them (tests, CI tuning,
consolidation, new gates) is documented in
[docs/streamlining-qa-plan.md](docs/streamlining-qa-plan.md).

---

## What NOT to do

- No npm/node/JS build tooling, CSS frameworks, or frontend frameworks.
- No 640px max-width regression and no removing the sidenote system. The
  60% column with 40% margin is a contract for the prose sections; the
  sidenotes need the margin. (The Timeline Split `.split-hero` and
  full-width `figure.timeline.career-band` are the
  sanctioned full-width exceptions above that column; see §Layout. They host
  no floating notes, which is why both the per-post note and the cadence tag
  rollup are suppressed there, so the contract holds.)
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

**Convene them TOGETHER, always (owner decision, 2026-07-28.)** Any
question that reaches either panel goes to both. This supersedes the
previous practice of routing a question to one panel and away from the
other, which parked at least one finding for months: the "audience
question" in `docs/homepage-critique-2026-07-19.md` §4 was labeled a
Focus Group question and not a Design Council one, and then nobody
convened the Focus Group, so it sat.

What the pairing does NOT change:
  - **Lanes.** The persona lists below still say who LEADS on what.
    Reception findings are the Focus Group's; taste calls are the
    Council's. Joint convening decides who is in the room, not whose
    judgment carries on a given point.
  - **Vetoes.** Haben keeps the soft veto on AA regressions and remains
    the only persona with one. Val keeps the motion-vocabulary lane.
  - **The "do NOT convene for" lists.** Those govern whether to convene
    at ALL (copy edits inside an entry, build-script changes, routine
    content updates still need no panel), not which panel.

The point of pairing is the conflict between the two readings, so report
it. A reception objection is not answered by a design rationale, and a
design principle is not overturned by one panelist's discomfort. Where
they disagree, say so and hold both.

**Focus Group** — reader-reception evaluation. 3 rounds of ~4
panelists (hiring managers, peers, recruiters, UX reviewers, named
archetypes like "Director of Quality Analytics at a regional MA
plan"). One round must include antagonists: senior healthcare-data-
engineering practitioners who pressure-test claims, denominators,
and positioning. One round should include an emotional-register
reader (e.g., "a recruiter who reads forty portfolios a week and
remembers two"): warmth, memorability, and the recurring
"visually boring" critique are reception questions, and they live
here, not in a Design Council seat. Output a synthesis table with
consensus strength (unanimous / majority / single voice).

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
  - Val — motion design (purposeful animation, scroll-driven
    choreography, timing and easing vocabulary). Owns the
    §Scroll-drawn figures lane, including the three-primitive
    coherence rule. Convene for motion vocabulary, timing, or
    choreography changes; NOT for static figure changes.
  - Luke — mobile-first and touch ergonomics (no-hover media, thumb
    reach, felt experience at the 760px collapse). Haben keeps WCAG
    compliance, including target size, and the sole veto; Luke owns
    what compliance cannot see (e.g., hover-only reveals that leave
    sighted touch users with less information than AT users).
    Convene for breakpoint or touch-surface changes; NOT for
    desktop-only CSS.

Val and Luke were seated 2026-06-10 after antagonistic audition
rounds. An emotional-design persona (Aarron) was auditioned in the
same pass and deliberately NOT seated: under antagonism his lane
reduced to relitigating locked tokens or to reader reception, which
belongs to the Focus Group (see the emotional-register archetype
above). Do not re-add an emotional-design council seat without a new
audition.

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

Because the panels convene jointly, the synthesis has three parts, in
this order: reception findings, design findings, then the points where
the two conflict. Do not merge the first two into a single verdict.

**Render before arguing about a rendered thing.** The one formally
unresolved disagreement in this repo (the sidenote band, §3.4 of the
2026-07-19 critique) stayed open for months over a number that a
headless-browser measurement settled in one pass, and the measurement
showed both sides had partly overlapping positions and that "broken"
overstated the defect. If a question is about what something looks like
at a given viewport, measure it first and bring the numbers.

Constraints for both panels: do not propose changes that violate
§What NOT to do or the locked design tokens above. The current
section set is intentional; do not propose adding sections without
discussion.

---

## Working agreement

If you think something looks wrong or should be improved, flag it and
ask before changing it. Do not make unrequested changes.
