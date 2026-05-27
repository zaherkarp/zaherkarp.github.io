# Site review synthesis — 2026-05-23

Cross-report synthesis of the data-viz craft critique, its alignment
companion, and the eight-evaluator hiring evaluation. This is the
artifact the publish workflow at `.github/workflows/site-review-publish.yml`
reads to populate the action checklist on the tracking issue.

The **Recently shipped** sections are not parsed by the workflow;
they document what landed in each batch this synthesis has covered.
The parser only picks up `- [ ]` lines under `### Tier N` headings.

---

## Recently shipped

### Iteration 3 — Group C: hiring-signal additions to Experience

Landed as commit `site-review iteration 3` on `claude/multi-agent-page-critique-BYmwb`.

- BHA role meta line restructured to surface team size and work mode: `Baltimore Health Analytics · remote · team of two data scientists · Nov 2025 to Present (Lead Data Engineer through Apr 2026)`. The Lead-through-Apr-2026 parenthetical defuses the "April 2026 promotion + May 2026 page = title aspiration racing ahead" reading the director-track HM flagged, while staying within the format the `lint_facts.py` parser accepts (org first, date range last; modifiers in between).
- Added a Health Catalyst platform-outcomes paragraph with three real customer case studies, each as an inline anchor to the published Health Catalyst success story: Community Health Network (>373,000 care gaps closed in six months at 4X value realization), St. Joseph Heritage Healthcare (37,000 monthly refills, turnaround dropping from 72 hours to 12, supporting 200 PCPs), Valley Medical Group (60% reduction in provider-bound refill requests). The executive's "five-year tenure with no platform-level outcome" flag and the manager-track HM's "five years that may have been IC work in practice" flag both addressed by concrete platform-level customer metrics.
- Added a third testimonial from William Barber (copy editor reporting directly to Z at Sustainable Clarity, 2013). Speaks to specific management craft: prompt and constructive feedback, project assignments matched to ability and growth. Addresses the manager-track HM's "no testimonial from a direct report" flag, and corroborates the Sustainable Clarity entry's claim of having "Managed up to eight copy editors, graphic designers, and photographers" with a quote from one of those reports.
- Updated the testimonials-section comment from "Two testimonials" to "Three testimonials" describing the new split (two HC-era downstream-consumer quotes plus one Sustainable Clarity-era direct-report quote).
- Pre-push checks green after restructuring the BHA meta line to put the date range last (required by the `lint_facts.py` parser which uses `parts[-1]` as the date chunk).

### Iteration 2 — Group B: cliff figure honesty pass

Landed as commit `site-review iteration 2` on `claude/multi-agent-page-critique-BYmwb`.

- New canonical data file at `src/data/cms-ma-pd-stars-2025.csv` carrying the CMS 2025 MA-PD Star Ratings distribution (412 contracts across 8 rating bins), with citation header pointing at CMS's October 2024 release.
- New build script at `scripts/build_cliff.py` that reads the CSV, computes a Gaussian-kernel-smoothed density curve (pure-Python KDE, no numpy/scipy dependency), and writes two SVG paths between the new `<!-- cliff-path:start -->` / `<!-- cliff-path:end -->` markers in `index.html`. Idempotent; re-run annually after the CMS October release.
- Cliff figure SVG: replaced the hand-drawn bezier with the data-driven path. Curve peaks at rating 3.5 (140 contracts) and remains high at 4.0 right against the cliff line, then drops sharply for 4.5/5.0. Honest representation of the underlying distribution; "most cluster just below the 4.0 cutoff" is now a measurable claim, not an editorial sketch.
- Figcaption rewritten from descriptive ("Approximate distribution... showing the 4.0 QBP threshold") to claim-stating: "Most Medicare Advantage contracts in the CMS 2025 Star Ratings cluster just below the 4.0 cutoff that triggers $50M in QBP bonus payments. Data from the CMS October 2024 release."
- Stars Cliff Simulator project card prose: tightened "ordinal logistic regression calibrated to CMS 2025 weights" → "ordinal logistic regression, parameterized to match the CMS 2025 weighting scheme for teaching purposes." Honest about the teaching scope without overclaiming methodological alignment with the CMS process.
- Added GitHub Source link to the Stars Cliff Simulator project card pointing at the in-repo simulator directory. The page's headline featured project is now inspectable, addressing the peer engineer's "I want to read the JS" credibility flag.
- Added a small non-color triangle marker (`fill="#111"`) bridging the cliff line and the +$50M label so the callout reads under color-vision constraints. Net accent count unchanged.
- Raised the "no QBP" hatch contrast from `stroke-width="0.4" opacity="0.4"` to `stroke-width="0.7" opacity="0.6"`. Hatched zone now clears AA non-text contrast on cream paper.
- Updated SVG aria-label to reflect the new data narrative.
- Pre-push checks green: em-dash count 0, accent budget 19/20, no `<p>`-wrapped SVG children.

### Iteration 1 — Groups A + E: accessibility floor + chart anchors

Landed as commit `site-review iteration 1` on `claude/multi-agent-page-critique-BYmwb`.

- Removed unused Bing verification TODO comment block from production HTML.
- Added `@media (prefers-reduced-motion: reduce)` block to the inline stylesheet.
- Tightened the `dp-mobile` SVG's `aria-label` to match the `dp-wide` data narrative. Diverged from the original A3 proposal (which would have broken either desktop or mobile screen-reader users) — `display:none` already cascades to the AT tree in modern screen readers.
- Replaced 13 generic `aria-label="Toggle sidenote"` / `aria-label="Toggle margin note"` with content-specific labels.
- Added `id="pub-{herd,acadmed,acos,implsci,jihi,wcel}"` to the 6 publication entry divs.
- Wrapped the 12 publication `<circle>` elements (6 in `dp-wide`, 6 in `dp-mobile`) in `<a href="#pub-X" aria-label="...">` anchors. The chart converts from thumbnail to interface.

---

## Action items

Check items as you ship them. To defer or skip an item, leave a
comment on the tracking issue starting with `defer: <reason>` or
`wontfix: <reason>`. The next review run picks those up.

### Tier 1 (ship now)

Technical and domain credibility deepening in the Experience
section. All small-surface prose additions (one sentence each)
inside the BHA or HC entries. None coupled.

- [ ] Name 1-2 specific Stars measures (SUPD, MAH/MAC/MAD, PACR, CAHPS/HOS, MTM-CMR) in BHA fold or Stars project prose
- [ ] Defend Selenium mention with one-sentence context (HPMS scraping?) in the BHA stack-line prose
- [ ] Add one sentence on dbt program shape (model count, layering, test coverage) somewhere in BHA or Health Catalyst fold
- [ ] Add one production-system anchor with a number (volume, schema count, DAG size, freshness SLO) inside the BHA or Health Catalyst fold
- [ ] Add CMS clustering / CAI / disaster-adjustment awareness to the BHA fold or the Stars project description
- [ ] Fix "built it under HITRUST" framing (line 1933) → "designed to HITRUST CSF controls"

### Tier 2 (queue)

Encoding-consistency and chart-fix items. Independent of each
other; the sparkline regeneration is the largest piece (touches
`scripts/build_portfolio.py`).

- [ ] Rewrite slope-graph figcaption (lines 2167-2169) to limit claim to the one worked example
- [ ] Mobile dot plot: replace bar encoding with scaled-down stacked dots (Data humanists' hill-to-die + Encoding rigorists' viewport-consistency rule)
- [ ] Add non-color marker to 2020 acquisition callout in career arc (both SVGs, lines 1334-1336 and 1416-1419)
- [ ] Replace 24 identical sparkline dots with per-week stem heights, regenerated by `scripts/build_portfolio.py` from `src/content/blog/*.md` frontmatter

### Tier 3 (defer or discuss)

Each of these touches a locked design token or sits in an "explicit
author go-ahead" zone. Not iteration candidates without a separate
conversation.

- [ ] Subtitle rewrite (line 1253). Editorial-clarity and hiring-panel both flagged it. `CLAUDE.md` §Hero: "The subtitle text itself is locked; do not edit without explicit instruction."
- [ ] Career arc redesign (Encoding rigorists' structural critique). `CLAUDE.md` marks the coordinate system as locked.
- [ ] Delete "Featured" / "More projects" subhead labels (lines 1996, 2283) — Editorial clarity wants delete, System designers cite as wayfinding
- [ ] Hand-shaped marks / per-byline glyphs on career arc — Data humanists; Encoding, Pipeline, and Access floor opposed
- [ ] Replace dot-area citation encoding with a numeric y-axis or printed integers — Encoding rigorists; System and Data humanists opposed
- [ ] Full data-driven build pipeline for every figure (`scripts/build_figures.py` from YAML/CSV) — Pipeline's hill-to-die. The cliff figure proved the pattern; revisit when a second chart visibly drifts out of truth.
- [ ] Interactive slope-graph widget (CSS `:checked` multi-state) — touches the locked "no JavaScript anywhere else without discussion" rule in spirit
- [ ] Add current-section nav indicator — `IntersectionObserver` scrollspy violates "no JS" rule; `:target` fallback only fires on hash-link navigation
