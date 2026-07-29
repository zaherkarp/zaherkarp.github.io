# Homepage iteration and design record — 2026-07-26

A design-director refinement of the **Timeline Split** opening (merged
2026-07-26, commits `77db71e` / PR #108). The Timeline Split's gains were
accepted and preserved; this pass fixed the one thing it left open, the
**opening composition**, and applied the surrounding structural cleanups the
brief called for.

Companion planning artifact: `.claude/plans/` (session plan, this branch).
This doc is the human-readable record: diagnosis, the three directions
considered, the Design Council review, the chosen direction, and an honest
self-critique.

---

## 1. Diagnosis

The Timeline Split opening was a **three-column `.split-hero` grid** — recent
writing, a narrow vertical career rail, and a technically dense project
scorecard — with a three-card `.teaser-row` beneath it. All three columns were
treated as equally primary but demanded different kinds of attention, so the
opening established no single proposition and no clear reading order before
asking the visitor to parse several dense forms of evidence.

Accepted and carried forward (not reversed): the Lichen palette, warm paper,
ETBook, writing as a primary surface, the qualitative transition timeline, real
content only, one featured project plus varied supporting formats, reduced nav,
folded archival material, no headshot, no orange, no dashboard styling.

Fixed:
1. No Tier-1 proposition stating the through-line.
2. Three co-primary columns competing; the rail cramped at 250px; the scorecard
   an "instrument panel" forcing actual/approx/illustrative parsing.
3. `.teaser-row` functioned as a second navigation.
4. Six of eight recent posts hidden behind a "More writing" fold.
5. The academic dot plot interrupted the professional narrative (it floated
   right after About).
6. The page ended on a certification inventory, with testimonials stranded
   mid-page.

---

## 2. Three directions considered

All three shared a Tier-1 proposition, a full-width timeline **below** the
columns, the teaser row replaced by one "More:" line, ≥4 extra writing titles
surfaced, and a simplified project figure. They differed in how Tier 2 was
composed.

- **A — Two-Up (the brief's literal hypothesis).** Two ~equal columns, writing
  left, work right. Faithful, but partially reproduces the "two dense things
  competing / no reading order" fault the brief itself raised.
- **B — Writing-led asymmetric (chosen).** A two-column Writing | Work opening,
  but writing gets the wide (~62%) editorial column and the project is a compact
  ~38% "what I'm building now" summary. Satisfies the two-column hypothesis
  while resolving the equal-weight problem, and maximizes writing primacy.
- **C — Stacked editorial bands.** Proposition, then full-width Writing band,
  then full-width Work band, then the timeline. Cleanest reading order and best
  desktop↔mobile parity, but departs most from the two-column hypothesis.

## 3. Design Council review (summary)

- **Edward (Tufte):** the current opening has no single entry point; a
  proposition on top is right *if it is prose, not a slogan*. Removing the
  scorecard is correct. Prefers a single dominant element (B or C over A). The
  full-width horizontal timeline is fine so long as it stays qualitative.
- **Steve (usability):** reading order is the deliverable. A still asks "which
  column first?"; **B answers it** (the wide writing column wins the eye); C
  answers it best. The "More:" line beats the teaser row (a fake second nav).
- **Jess (editorial):** writing is the brand; B/C protect its primacy, A dilutes
  it. The proposition must sound like Zaher and be additive to the locked
  subtitle. Prefers **B**.
- **Massimo (typography):** the proposition is a set-piece, sized between body
  and h1; ETBook roman, not italic.
- **Luke (mobile):** promote the vertical `tl-rail` to serve mobile and give
  desktop a new wide horizontal band — that is the intentional mobile version,
  not a shrunk desktop. Keep 24px+ touch overlays.
- **Haben (accessibility):** the proposition is a `<p>`, not a heading (heading
  order stays h1→h2→h3). Restoring `prefers-reduced-motion` would reverse a
  locked owner decision, so it must be an explicit owner call.
- **Val (motion):** reuse the trace primitive; no new easing. The timeline is
  now a full-width centerpiece, so it earns the first-paint draw.

**Recommendation → Direction B**, adopted by the owner. C was the strong
alternative; A the Council's weakest.

---

## 4. What changed (Direction B, as shipped)

- **Nav** → `writing · work · about · contact`. `Work` targets a new empty
  `#work` anchor placed just before `#experience` (the section keeps its own id
  for `lint_facts`); Publications/Speaking leave the top bar, still reachable via
  the "More:" line and the relocated dot plot.
- **Proposition** — a new `<p class="proposition">` below the nameplate: *"I
  build and write about auditable analytics systems for regulated healthcare."*
  Additive to the locked subtitle (a category label); a `<p>`, not a heading.
- **`.split-hero`** — two-column asymmetric grid
  (`minmax(0,1.6fr) minmax(0,1fr)`, ~62/38). DOM order writing → project →
  band → more, matching the stacked mobile order.
- **Writing surfaced** — the two featured entries (writing-list markers) plus
  the six-title index (writing-index markers, **moved into the hero** from the
  former "More writing" fold and compacted to a dated title list via
  `.hero-index`). "View all writing →" now points to `/blog/`. The `#writing`
  section keeps its cadence sparkline and tag-rollup margin note.
- **Project simplified** — the two-card accept-vs-reject `scorecard-figure` was
  retired for a small `funnel-figure` (~200 news items/week ▸ ~5 that matter,
  both numbers already in the adjacent prose). The worked example lives in the
  methodology post (linked). Removing the scorecard freed its two accent uses
  (18 → 16 occurrences).
- **Timeline full-width** — moved out of the centre rail to a
  `figure.timeline.career-band` below the grid. **Desktop:** the wide horizontal
  `svg.tl-horizontal` (viewBox 1200×440), **restored verbatim from the
  pre-Timeline-Split hero arc** (`77db71e^`) rather than authored from scratch —
  tested coordinates, 26pt italic labels, three qualitative lanes on a dated
  x-axis, the calmed 2020 acquisition inflection, plus the two era annotations
  (news-wire syndication 2008, MPH Biostatistics 2014) the narrow rail had
  dropped; no accent. (An earlier from-scratch `tl-band` sketch was replaced by
  the tested original at the owner's suggestion — reuse over reinvention.)
  **Mobile (≤760px):** the vertical `svg.tl-rail`, reused (no era annotations,
  matching the original narrow-frame rationale). The former mobile `tl-compact`
  was retired. All five `#exp-*` band links, touch overlays, and `<title>`s
  preserved. The load-draw (§18.2) traces both `tl-horizontal` (stroke-width 10)
  and `tl-rail` (stroke-width 9), so every viewport gets the first-paint draw.
- **Teaser row → "More:" line** — one restrained
  `More: projects · publications · presentations · full experience`.
- **Dot plot moved** — the academic publication/presentation dot plot moved
  from after About to a `#main` sibling immediately before `#publications` (kept
  a sibling so `.fullwidth` still resolves to full width, not 90% of the 60%
  column). Its `#pub-*` links resolve to the adjacent section.
- **Ending reordered** — testimonials moved to sit after Certifications and
  before Contact: … → Education → Service → Certifications → Testimonials →
  Contact. The Education+Service Gantt figure stayed with its pair.

Verification (all green): the nine index-relevant linters, the full
`scripts/tests/` suite (112 passed, 1 skipped), `build_portfolio.py`
(byte-identical marker output — idempotent), em-dash 0, accent 16/20. Rendered
and screenshot-checked at desktop light/dark and mobile.

---

## 5. Declined: `prefers-reduced-motion`

The brief asked to restore `prefers-reduced-motion`. The owner **declined**,
keeping the 2026-06-13 site-wide no-gate decision: all motion stays ungated
(short, one-shot, data-tracing, well inside WCAG 2.2.2's five-second line), and
no `@media (prefers-reduced-motion)` block was added. The full-width timeline's
load-draw therefore runs for every reader, like the rest of the page's motion.
This is the one part of the brief not implemented, recorded here deliberately.

---

## 6. Self-critique / next iteration

- **Writing-column length.** With two full summaries plus six dated titles, the
  writing column is tall, so on a wide desktop the full-width timeline sits well
  below the fold. This is a deliberate Tier-3 placement (writing leads), but a
  future pass could tighten the featured summaries or cap the index at four
  titles if the timeline should surface sooner.
- **`#writing` section is now thin** (cadence sparkline + margin note only), the
  cost of moving the article list up into the hero. It still earns its place as
  the "writing rhythm" lens and the nav anchor, but watch it in the next review.
- **Proposition copy is provisional.** The shipped line is the brief's
  illustrative one; the owner may refine it. It is worded to be additive to the
  locked subtitle, not a restatement.
- **Funnel numbers are approximate** (`~200`, `~5`) and match the adjacent
  prose; no fabricated performance metric was introduced.
- **The "Work" nav target** lands on the Experience heading (via `#work`), which
  is followed by Projects; if a combined "Work" landing surface is ever wanted,
  the anchor is the place to grow it.

---

## Superseded 2026-07-28

This record stands as written; the note below only marks what has since changed.

The two-band funnel described at L106-110 and L166-167 is now three-band
(`~200 news items / week` ▸ `~20 screened` ▸ `~5 that matter`), matching a prose
rewrite that separates a three-tier simulation estimate from early production
data and keeps a caveat on each. The numbers are still approximate and still
match the adjacent prose, so the self-critique at L166-167 holds; what changed is
that the figcaption now states outright that they are modeled rather than
measured. The figure remains accent-free, so the accent count is unaffected.

**Follow-up the same day: the description was trimmed back for column balance.**
The rewrite above took the hero card's prose from 61 to 129 words in the ~38%
column, and the grid's `align-items: start` turned the difference into visible
dead space: 488px under the writing column at 1440px, 822px at 900px, measured
in headless Chromium. The three-band SVG was not the cause (worth about 6px); the
prose was. It is now ~62 words, keeping all three tiers and a modeled-not-measured
marker, with the six-feature list, the assumed-parameters elaboration, and the
early-production-data reading moved into the methodology post. Measured after:
84px at 1440px, 155px at 900px. The figcaption keeps its caveat clause
deliberately, so the figure carries its own scope if read alone.

This is the first concrete instance of the §6 writing-column-length item
(L156-159) biting from the *other* direction: that note anticipated the writing
column being too tall, and the balance is in fact set by whichever column is
allowed to grow unchecked. The ~38% column is the constrained one and should be
treated as having a prose budget.
