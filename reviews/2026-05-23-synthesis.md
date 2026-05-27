# Site review synthesis — 2026-05-23

Cross-report synthesis of the data-viz craft critique, its alignment
companion, and the eight-evaluator hiring evaluation. This is the
artifact the publish workflow at `.github/workflows/site-review-publish.yml`
reads to populate the action checklist on the tracking issue.

**Recently shipped (Iteration 1)** is not part of the parsed checklist;
it documents what landed in the batch this synthesis represents. The
parser only picks up `- [ ]` lines under `### Tier N` headings.

---

## Recently shipped (Iteration 1)

**Group A — Accessibility floor sweep** and **Group E — Chart operability** landed together in batch 1. Committed to `index.html` on `claude/multi-agent-page-critique-BYmwb`.

- Removed unused Bing verification TODO comment block from production HTML (lines 13-17 in pre-edit numbering).
- Added `@media (prefers-reduced-motion: reduce)` block to the inline stylesheet, alongside the existing `@media print` and dark-mode blocks. Zeroes out animation, transition, and `scroll-behavior` for vestibular-sensitive readers.
- Tightened the `dp-mobile` SVG's `aria-label` to match the `dp-wide` data narrative ("Academic activity dot plot showing 6 publications and 17 presentations across 2010 to 2019, mobile layout"). **Diverged from the original A3 proposal**: hardcoding `aria-hidden="true"` on whichever viewport copy is `display:none` would break either desktop or mobile screen-reader users (whichever copy is hidden by aria-hidden becomes inaccessible to that viewport's users; the other CSS-hidden copy is already invisible to AT via `display:none` cascade). Equalizing the aria-labels is the actual accessibility win.
- Replaced 13 generic `aria-label="Toggle sidenote"` / `aria-label="Toggle margin note"` with content-specific labels (e.g. `"Show note on CMS Technical Notes annual revisions"`, `"Show PubMed link and citation count for JIHI 2014 paper"`). The 14th toggle (`mn-cadence`) already had `"Toggle tag breakdown"`, kept as-is.
- Added `id="pub-{herd,acadmed,acos,implsci,jihi,wcel}"` to the 6 publication entry divs.
- Wrapped the 12 publication `<circle>` elements (6 in `dp-wide`, 6 in `dp-mobile`) in `<a href="#pub-X" aria-label="...">` anchors so each dot becomes a navigable link to its publication entry in the section below. No JavaScript; pure SVG-anchor semantics. Per the System designers camp's hill-to-die-on, this converts the chart from a thumbnail into an interface.

Pre-push checks: all six green (lint_blog, lint_vocab, lint_facts, em-dash chrome, accent discipline at 19/20, no `<p>`-wrapped SVG children).

---

## Action items

Check items as you ship them. To defer or skip an item, leave a
comment on the tracking issue starting with `defer: <reason>` or
`wontfix: <reason>`. The next review run picks those up.

### Tier 1 (ship now)

Cliff figure honesty pass. **Anti-pattern flag**: the figcaption
rewrite (first item below) and the data-source decision (second item)
must ship together. Adopting the new caption alone makes a
quantitative claim the current hand-drawn bezier cannot support.

- [ ] Fetch CMS Star Ratings public-use contract distribution and rebuild the cliff curve from real data (a small `scripts/build_cliff.py` writing the SVG path into the `cliff-figure` between marker comments)
- [ ] Rewrite cliff figcaption (line 2034) from descriptive to claim-stating, e.g. "Most Medicare Advantage contracts cluster just below the 4.0 cutoff that triggers $50M in QBP bonus payments"
- [ ] Add GitHub link to Stars Cliff Simulator project card (around line 2123). The peer engineer called this the single highest-leverage detail-level fix
- [ ] Tighten "ordinal logistic regression calibrated to CMS 2025 weights" (line 2003) — either rephrase as "synthetic weights matched to the CMS 2025 weighting scheme" or commit to and document the calibration
- [ ] Add non-color marker (leading symbol or geometric mark) to the +$50M label so the callout reads under color-vision constraints
- [ ] Raise "no QBP" hatch contrast in the cliff figure: stroke-width 0.7, opacity 0.6

### Tier 2 (queue)

Hiring-signal additions to the Experience section, technical and
domain credibility details, and the remaining encoding-consistency
fixes. None of these are coupled to each other; ship in any order.

- [ ] Add team-size / span-of-control line on the BHA role (line 1852 area). Five of eight hiring evaluators flagged the headcount absence as the single most universal gap.
- [ ] Add location / work-mode hint near h1 or in the About lead paragraph
- [ ] Reframe the April 2026 promotion timeline so the parenthetical does not read as "title aspiration racing ahead of experience"
- [ ] Surface one Health Catalyst outcome at platform/customer level, not pipeline level (customer count, ARR-influenced figure, contracts deployed across N plans)
- [ ] Replace one downstream-consumer testimonial with a peer-manager or direct-report quote, or annotate the existing testimonials to set expectations
- [ ] Name 1-2 specific Stars measures (SUPD, MAH/MAC/MAD, PACR, CAHPS/HOS, MTM-CMR) in BHA fold or Stars project prose. Domain expert: "For someone forecasting Stars cutpoints, the measure portfolio is the work."
- [ ] Defend Selenium mention with one-sentence context (HPMS scraping?) in the BHA stack line
- [ ] Add one sentence on dbt program shape (model count, layering, test coverage) somewhere in BHA or Health Catalyst fold
- [ ] Add one production-system anchor with a number (volume, schema count, DAG size, freshness SLO) inside the BHA or Health Catalyst fold
- [ ] Add CMS clustering / CAI / disaster-adjustment awareness to the BHA fold or the Stars project description
- [ ] Fix "built it under HITRUST" framing (line 1933) → "designed to HITRUST CSF controls"
- [ ] Rewrite slope-graph figcaption (lines 2167-2169) to limit claim to the one worked example
- [ ] Mobile dot plot: replace bar encoding with scaled-down stacked dots (Data humanists' hill-to-die + Encoding rigorists' viewport-consistency rule)
- [ ] Add non-color marker to 2020 acquisition callout in career arc (both SVGs, lines 1334-1336 and 1416-1419)
- [ ] Replace 24 identical sparkline dots (lines 1747-1773) with per-week stem heights, regenerated by `scripts/build_portfolio.py` from `src/content/blog/*.md` frontmatter

### Tier 3 (defer or discuss)

Each of these touches a locked design token or sits in an "explicit
author go-ahead" zone. Not iteration candidates without a separate
conversation.

- [ ] Subtitle rewrite (line 1253). Editorial-clarity and hiring-panel both flagged it. `CLAUDE.md` §Hero: "The subtitle text itself is locked; do not edit without explicit instruction."
- [ ] Career arc redesign (Encoding rigorists' structural critique). `CLAUDE.md` marks the coordinate system as locked.
- [ ] Delete "Featured" / "More projects" subhead labels (lines 1996, 2283) — Editorial clarity wants delete, System designers cite as wayfinding
- [ ] Hand-shaped marks / per-byline glyphs on career arc — Data humanists; Encoding, Pipeline, and Access floor opposed
- [ ] Replace dot-area citation encoding with a numeric y-axis or printed integers — Encoding rigorists; System and Data humanists opposed
- [ ] Full data-driven build pipeline for every figure (`scripts/build_figures.py` from YAML/CSV) — Pipeline's hill-to-die. Substantial infrastructure; revisit when a chart visibly drifts out of truth.
- [ ] Interactive slope-graph widget (CSS `:checked` multi-state) — touches the locked "no JavaScript anywhere else without discussion" rule in spirit
- [ ] Add current-section nav indicator — `IntersectionObserver` scrollspy violates "no JS" rule; `:target` fallback only fires on hash-link navigation
