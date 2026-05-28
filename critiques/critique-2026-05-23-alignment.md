# Alignment summary — six-camp critique of `index.html`

Companion to `critique-2026-05-23.md`. This document does not re-state
the camp critiques; it surfaces the alignment structure across them in
three views and combines them into one ranked top-10. Read alongside
the source critique.

- **Source critique:** `critiques/critique-2026-05-23.md`
- **Archetype:** personal portfolio
- **Camps:** Enc (Encoding rigorists), Edit (Editorial clarity), DH (Data
  humanists), Sys (System designers), Pipe (Pipeline & reproducibility),
  Acc (Access floor)

---

## Section 1 — Change-by-change consensus ranking

Net consensus score = (camps explicitly backing) − (camps explicitly
opposing). A suppressed camp's opposition is discounted per the
archetype weighting. Tied scores ordered by the source-critique
bucket (high > medium > low).

| Rank | Change (file location) | Backing | Opposing | Net | Bucket | Notes |
|-----:|------------------------|---------|----------|----:|--------|-------|
| 1 | Rewrite cliff figcaption (line 2034) | Edit, Enc, DH, Acc | — | **+4** | HC #1 | Coupled to MC #1; ship together or use non-quantitative caption |
| 1 | Sparkline as per-week count, regenerated from frontmatter (lines 1747-1773) | Edit, Enc, Pipe, DH | — | **+4** | HC #2 | DH backs the intermediate step but would prefer enrichment (suppressed) |
| 3 | Wrap publication/presentation `<circle>`s in `<a xlink:href>` (lines 1538-1611, 1678-1705) | Sys, Edit, Enc | Pipe (non-blocking) | **+3** | MC #2 | Pipe wants data-derived dots first but doesn't block the anchor wrap |
| 4 | CMS data for cliff curve OR relabel "Schematic illustration" (lines 2032-2120) | Enc, Acc | Edit (non-blocking) | **+2** | MC #1 | Structural complement to HC #1 |
| 4 | Keep stacked dots on mobile dot plot (lines 1649-1704) | DH, Enc | — | **+2** | MC #5 | Edit silent; DH's hill to die |
| 4 | Limit slope-graph figcaption to one worked example (lines 2167-2169) | Edit, Sys | — | **+2** | MC #6 | Conflict 4 resolution; widget deferred |
| 4 | Descriptive aria-labels on sidenote/marginnote toggles | Acc, Sys | — | **+2** | MC #7 | Both camps converge on the same fix from different angles |
| 8 | Non-color marker on 2020 callout (lines 1334-1336, 1416-1419) | Acc, Enc¹ | Edit (mild) | **+1** | MC #4 | ¹ Enc conditional on accent semantic being consistent across all six figures |
| 8 | `@media (prefers-reduced-motion: reduce)` block | Acc | — | **+1** | MC #3 | Acc hill to die; zero implementation cost |
| 8 | `aria-hidden="true"` on viewport-swap SVG copy (lines 1284/1390, 1512/1649) | Acc | — | **+1** | HC #3 | Quick fix; raised to HC by zero-opposition / floor-is-floor |
| 8 | Raise cliff "no QBP" hatch contrast (stroke 0.7, opacity 0.6) | Acc | — | **+1** | LC #5 | Subsumed if MC #1 redraws the figure |
| 8 | Pin `requirements.txt` to lockfile + runner OS | Pipe | — | **+1** | LC #7 | Out of scope for index.html; procedurally aligned |
| 13 | Delete "Featured" / "More projects" subheads (lines 1996, 2283) | Edit | Sys (wayfinding) | **0** | LC #4 | Editorial deletion vs system-design wayfinding |
| 13 | Current-section nav indicator (scrollspy or `:target`) | Sys | locked "no JS" rule | **0** | LC #6 | IntersectionObserver path breaks locked rule |
| 15 | Replace dot-area citation encoding with numeric y-axis or printed integers | Enc | Sys, DH | **−1** | LC #1 | Sys prefers anchor wrap (MC #2); DH defends humane texture |
| 15 | Data-driven build for every figure (`scripts/build_figures.py` + YAML/CSV) | Pipe | Sys, Enc | **−1** | LC #2 | Pipe's hill to die; substantive infrastructure work |
| 17 | Hand-shaped marks / per-byline glyphs on career arc | DH | Enc, Pipe, Acc | **−2** | LC #3 | Touches locked career-arc coordinates and Tufte data-ink |

**Within-bucket gradient observation.** HC #3 (aria-hidden) has the
weakest mandate of any high-confidence change (+1, single camp); it
sits at the same net score as four medium-confidence items. Its
high-confidence ranking is justified by zero opposition plus floor-is-
floor, not by breadth. Conversely, MC #2 (anchor wrap on dots) has
stronger mandate (+3) than two high-confidence items and could
arguably be promoted in a future iteration.

---

## Section 2 — Pairwise camp alignment

Score per pair: +1 per backed-the-same-change; −1 per explicit
rebuttal in "What other camps will say" sections or per opposite
prescription for the same element.

### 2.1 Matrix (lower triangle)

|        | Enc  | Edit | DH   | Sys  | Pipe | Acc |
|--------|-----:|-----:|-----:|-----:|-----:|----:|
| Enc    |  —   |      |      |      |      |     |
| Edit   |  +1  |  —   |      |      |      |     |
| DH     |   0  |   0  |  —   |      |      |     |
| Sys    |  −1  |   0  |   0  |  —   |      |     |
| Pipe   |  −1  |  −1  |   0  |  −3  |  —   |     |
| Acc    |  +2  |   0  |  −1  |  +1  |  −1  |  —  |

### 2.2 Pairs ranked (most-aligned → most-contested)

| Pair | Score | One-line reason |
|------|------:|-----------------|
| Enc × Acc | **+2** | Agree on cliff integrity, cliff data source, non-color callouts; mild rebuttal on whether triple-redundant encoding suffices |
| Enc × Edit | +1 | Agree on cliff caption, sparkline, anchor wrap; disagree on whether the cliff figure can stay as-is |
| Sys × Acc | +1 | Both attack the sidenote toggle from different angles and converge on a compatible fix (descriptive labels + visible affordance) |
| Enc × DH | 0 | Three backed changes balanced by sparkline-enrichment rebuttal, career-arc accent rebuttal, and hand-shaped-marks opposition |
| Edit × DH | 0 | Two backed changes balanced by "Patient Choice Award is warmth vs. decoration" rebuttal |
| Edit × Sys | 0 | Two backed changes balanced by nav-typography and subhead-label rebuttals |
| Edit × Acc | 0 | Single backed change (cliff caption) balanced by data-ink-vs-screen-reader-text rebuttal |
| DH × Sys | 0 | Both oppose LC #1 (dot-area replacement); offset by SVG-palette-contract rebuttal |
| DH × Pipe | 0 | Sparkline backing balanced by hand-shaped-marks opposition |
| Enc × Sys | −1 | Anchor wrap agreement loses to dot-area-encoding rebuttal both directions |
| Enc × Pipe | −1 | Sparkline agreement loses to data-driven-build opposition and hand-tuned-coords rebuttal |
| Edit × Pipe | −1 | Sparkline agreement loses to tag-frequency-margin-note and literate-document rebuttals |
| DH × Acc | −1 | Cliff caption agreement loses to hand-shaped-marks-vs-screen-reader-parity argument |
| Pipe × Acc | −1 | No direct backed-change overlap; mild "lint-chain enforcement" rebuttal |
| Sys × Pipe | **−3** | Most contested: cross-rebuttals on CI hygiene vs. user value plus explicit Pipe LC #2 opposition (Conflict 4) |

### 2.3 Top alignments and contests

**Most-aligned pair — Enc × Acc (+2).** The Tufte-rigor and inclusive-
design camps overlap more than the page's surface might suggest:
both treat the cliff figure's data integrity and color-only encoding
as floor-level failures, and both back the non-color 2020 callout fix.
The single Acc rebuttal of Enc ("triple-redundant encoding doesn't
suffice when the 2020 year label is red-only") is a refinement, not a
contradiction.

**Second-most-aligned — Sys × Acc (+1).** A surprise alignment: the
system-design and access camps both look at the sidenote toggle and
conclude the current state fails. Sys frames it as a gulf-of-evaluation
problem ("the control reveals nothing"); Acc frames it as an aria-label
preview problem ("the screen reader hears nothing"). Their fix is
near-identical (descriptive labels visible to all users), reached
through different lenses. This is the conflict-resolution rule's
"different angles, compatible fix" case.

**Most-contested pair — Sys × Pipe (−3).** The slope-graph
generalizability conflict (Conflict 4) is the deepest rift on the page.
Sys wants an interactive widget the reader can operate; Pipe wants
multiple data-driven static views regenerated at build time. They
disagree at the level of what "fix" means: Sys treats charts as
systems-the-user-operates, Pipe treats them as artifacts-that-rebuild-
consistently. Each rebuts the other's hill-to-die directly. The
resolution defers both.

**Second-most-contested — five-way tie at −1.** Notably, every
contested pair at −1 has Pipeline on one side. Pipe is the camp with
the highest discipline-alignment score in Section 3 but the lowest
pairwise alignment with other camps in Section 2 — i.e., Pipe's
proposals are well-formed and respect the locked design, but other
camps see them as orthogonal-bordering-on-irrelevant to the reader-
facing problems. This is the methodological tension to watch.

---

## Section 3 — Camp vs. locked design discipline

For each camp, every proposed change is classified against `CLAUDE.md`
as **Aligned** (lands without amending discipline), **Extending** (adds
new discipline without contradicting locked rules), or **Breaking**
(would require explicit discussion to amend a locked rule).

### 3.1 Ranked

| Camp | Aligned | Extending | Breaking | Score | Top breaking concern |
|------|--------:|----------:|---------:|------:|----------------------|
| Pipeline & reproducibility | 5 | 2 | 0 | **+7** | (none) — all proposals extend the existing scripts/ pipeline |
| Access floor | 6 | 1 | 0 | **+7** | (none) — `prefers-reduced-motion` is the one extension |
| Encoding rigorists | 5 | 1 | 1 | **+5** | Career-arc redesign touches "coordinates are tested" rule |
| Editorial clarity | 5 | 1 | 1 | **+5** | Subtitle rewrite (line 1253) violates "subtitle text itself is locked" |
| Data humanists | 2 | 3 | 2 | **+3** | Career-arc hand-marks + sparkline enrichment touch locked tokens and Tufte data-ink rigor |
| System designers | 4 | 0 | 2-3 | **+1-2** | Nav scrollspy (IntersectionObserver) + slope-graph `:checked` widget against "no JS anywhere else without discussion" |

Pipeline and Access floor are tied at the top because their
proposals largely live in the metadata layer (build scripts, aria
attributes, motion preferences) rather than in the visible chrome
where the locked tokens live. Encoding and Editorial split the
middle: most of their fixes are aligned, with one breaking each.
Data humanists' enrichment direction collides with Tufte minimalism
on multiple fronts. System designers' interactive proposals collide
with the locked "no JS anywhere else without discussion" rule
twice, and the slope-graph CSS-only `:checked` workaround is still
"new interactivity without discussion" in spirit.

### 3.2 Per-camp breaking concerns (cited)

- **Encoding rigorists — career arc redesign.** Item 4 of the camp
  critique proposes making the three lanes truly comparable or
  collapsing to a single timeline. `CLAUDE.md` §Design decisions /
  Career arc SVG: "Do not change SVG coordinates without
  recalculating from scratch — they're tested." Redesign IS
  recalculating from scratch, so the rule allows it, but only after
  discussion; that's why this is breaking-not-blocked.

- **Editorial clarity — subtitle rewrite.** Item 1 of the camp
  critique rewrites the subtitle from a category to a verb-claim.
  `CLAUDE.md` §Design decisions / Hero: "The subtitle text itself is
  locked; do not edit without explicit instruction." Editorial's fix
  is well-motivated but requires explicit go-ahead.

- **Data humanists — career-arc hand-marks + sparkline enrichment.**
  Career-arc coords are locked (as above). Sparkline multidimensional
  encoding fights both the homepage's chart-minimalism inheritance
  and the marker-bracketed regeneration contract that expects a
  single deterministic shape per build.

- **System designers — IntersectionObserver scrollspy.** `CLAUDE.md`
  §Stack: "No JavaScript anywhere else without discussion."
  IntersectionObserver is JS; the `:target` fallback is allowed but
  only fires on hash-link navigation, not scroll. Sys also proposes
  the CSS-only `<select>`/`:checked` widget for the slope graph;
  that's mechanically allowed but the spirit of the rule covers new
  interactivity, not just JS specifically.

---

## Section 4 — Combined top-10

Combined rank = (consensus score from §1) + (sum of backers'
discipline-alignment scores from §3, normalized: Pipe/Enc/Acc = 1.0,
Edit = 0.7, DH = 0.4, Sys = 0.2). This rewards changes that have
broad cross-camp support **and** are backed by camps whose proposals
sit well with the locked design.

| Rank | Change | Net consensus | Backer alignment | Combined | Why it tops |
|-----:|--------|--------------:|-----------------:|---------:|-------------|
| 1 | Rewrite cliff figcaption (line 2034) | +4 | 3.1 | **7.1** | Universal backing across high-discipline camps; pairs cleanly with #4 |
| 1 | Sparkline as per-week count, regenerated (lines 1747-1773) | +4 | 3.1 | **7.1** | Same four-camp backing; Pipe handles the generation, Edit handles the shape |
| 3 | Wrap publication/presentation dots in anchors (lines 1538-1611, 1678-1705) | +3 | 1.9 | **4.9** | Three-camp backing; zero JS, ~12 lines of SVG markup, converts thumbnail to index |
| 4 | CMS data for cliff curve OR relabel schematic (lines 2032-2120) | +2 | 2.0 | **4.0** | Required structural complement to #1; both backers are top-alignment camps |
| 5 | Keep stacked dots on mobile (lines 1649-1704) | +2 | 1.4 | **3.4** | Two-camp backing across discipline tiers; Edit's silence keeps it from rising further |
| 6 | Descriptive aria-labels on sidenote/marginnote toggles | +2 | 1.2 | **3.2** | Acc carries the discipline alignment; Sys's lower score holds it below #5 |
| 7 | Non-color marker on 2020 callout (lines 1334-1336, 1416-1419) | +1 | 2.0 | **3.0** | Both backers fully aligned with discipline; small fix, clear payoff |
| 8 | Limit slope-graph figcaption to one worked example (lines 2167-2169) | +2 | 0.9 | **2.9** | Two-camp backing but Sys's low discipline alignment drags the combined score |
| 9 | `aria-hidden="true"` on viewport-swap SVGs (lines 1284/1390, 1512/1649) | +1 | 1.0 | **2.0** | Floor fix; Acc-only backing keeps the combined score modest |
| 9 | `@media (prefers-reduced-motion: reduce)` block | +1 | 1.0 | **2.0** | Acc hill-to-die; declared discipline that survives future drift |

**Reading the combined ranking.**

The top three changes (cliff caption + sparkline + anchor wrap) carry
the broadest cross-camp mandate AND the highest backer-discipline
alignment. These should ship first.

The cliff-caption rewrite (#1) is tied with the sparkline (#1) but
**must** ship coupled with #4 (cliff data source decision) to avoid
the integrity downgrade flagged as an anti-pattern in the source
critique. Treat #1 and #4 as a single unit.

The anchor-wrap fix (#3) is the surprise of the ranking: it has the
third-highest combined score despite being a medium-confidence item
in the source critique. Three camps back it, the fix is mechanically
trivial (no JS, no new dependencies), and it converts the academic
activity chart from decoration into an interface. Strong candidate
for the next implementation pass.

Changes #5-#8 form a coherent mid-tier of small, high-leverage fixes
that touch the figcaption / aria-label / chart-encoding layer without
demanding structural rework. The tied pair at #9 (aria-hidden and
prefers-reduced-motion) are quick wins.

Notably absent from the top-10: every Pipeline-only proposal and
every System-designer-only proposal. This reflects the methodology
correctly: Pipeline scores high on discipline alignment but low on
cross-camp consensus (the LC #2 data-driven build was opposed by
two camps); System scores high on cross-camp consensus where it
co-backs (MC #2, MC #6) but low on discipline alignment for its
hills-to-die-on (nav scrollspy, slope-graph widget). The combined
rank surfaces this asymmetry by weighting both views.

---

## Reading guide

- **If you're acting on one thing:** ship #1 cliff caption coupled
  with #4 cliff data source. Either redraw from CMS data, or use the
  non-quantitative caption variant from HC #1.
- **If you have an afternoon:** ship the top three plus the cliff
  data-source decision. Roughly 30 lines of SVG and 1 build-script
  patch.
- **If you're prioritizing a quarter of work:** the entire top-10 is
  defensible. The bottom three (LC #1, LC #2, LC #3 in §1) are
  defer-or-redirect candidates; the Pipeline LC #2 in particular
  should wait until a visible chart-data drift incident.
- **If you're reading this to refine the methodology:** the Sys × Pipe
  pair at −3 (§2) is the structural friction worth examining next;
  these two camps consistently look at the same problem and propose
  fixes that route through different abstractions.
