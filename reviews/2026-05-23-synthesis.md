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

Hiring-signal additions to the Experience section. The single most
universal flag in the hiring evaluation was the absence of a
headcount line on the BHA role (5 of 8 evaluators). Some of these
require information only the author has (team size, prior-role
context, available testimonials).

- [ ] Add team-size / span-of-control line on the BHA role (line 1852 area). Five of eight hiring evaluators flagged the headcount absence as the single most universal gap.
- [ ] Add location / work-mode hint near h1 or in the About lead paragraph
- [ ] Reframe the April 2026 promotion timeline so the parenthetical does not read as "title aspiration racing ahead of experience"
- [ ] Surface one Health Catalyst outcome at platform/customer level, not pipeline level (customer count, ARR-influenced figure, contracts deployed across N plans)
- [ ] Replace one downstream-consumer testimonial with a peer-manager or direct-report quote, or annotate the existing testimonials to set expectations

### Tier 2 (queue)

Technical and domain credibility details (Group D) plus the
remaining encoding-consistency fixes (Groups F, G). None of these
are coupled to each other; ship in any order. The sparkline
regeneration (last item) touches `scripts/build_portfolio.py` and
has the broadest blast radius of the queue.

- [ ] Name 1-2 specific Stars measures (SUPD, MAH/MAC/MAD, PACR, CAHPS/HOS, MTM-CMR) in BHA fold or Stars project prose
- [ ] Defend Selenium mention with one-sentence context (HPMS scraping?) in the BHA stack line
- [ ] Add one sentence on dbt program shape (model count, layering, test coverage) somewhere in BHA or Health Catalyst fold
- [ ] Add one production-system anchor with a number (volume, schema count, DAG size, freshness SLO) inside the BHA or Health Catalyst fold
- [ ] Add CMS clustering / CAI / disaster-adjustment awareness to the BHA fold or the Stars project description
- [ ] Fix "built it under HITRUST" framing (line 1933) → "designed to HITRUST CSF controls"
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
