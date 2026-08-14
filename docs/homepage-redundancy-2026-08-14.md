# Homepage redundancy pass, 2026-08-14

Branch `claude/reduce-redundancy-education-service-vmp5ea`.

## Why

The owner asked to reduce redundancy on the homepage, giving one example: the
Education/Service Gantt, whose "title seems too long and repeats the caption."
Two steers followed mid-pass:

1. **Prioritize the visualizations** — when a fact lives in both a chart and its
   surrounding prose, keep it in the chart and cut the prose. (This is the
   Tufte data-ink direction anyway: let the figure carry the data.)
2. **Reframe Case 01 off "Stars" toward statistics** — the owner disliked that
   the "Stars measurement" case read as Stars-specific rather than statistical.

## The redundancy the owner named

The Gantt asserts the **2014-15 concurrency point four times**: the lead-in
`<p>`, the figcaption, the SVG `aria-label`, and the in-chart density annotation
("2014-15: three credentials, two roles"). It also had the lead-in and figcaption
both open by naming the same three buckets (degrees / certificates / service),
and the figcaption re-narrated bars the chart already labels (WORT board chair,
UG research mentor, MPH, Patient Safety certificate). There is no `<h2>` for this
region — it was deleted with the `#education` / `#service` prose sections — so the
lead-in *was* the reader's "title," which is what made the repetition felt.

## Changes (all prose-only)

| # | Where | Change |
|---|---|---|
| 1 | Gantt (`figure.gantt-figure`) | **Removed the lead-in `<p>`**; trimmed the figcaption to drop the bar re-naming and the "running through 2014-15" restatement. Kept the legend, the $18,000 grant + Carayon/AHRQ certificate (the only facts not in the chart), and the CV pointer. Kept the density annotation and the `aria-label`. |
| 2 | Insight-Engine funnel | Prose dropped ~200 / ~20 / ~5; they now live only in the SVG labels. The "modeled, not measured" caveat stays in the figcaption. Prose is now mechanism-only. |
| 3 | Stars-cliff figcaption | Dropped "$50M in QBP bonus payments for a mid-size contract"; kept in the prose hook ("a tenth of a star can be worth $50 million") and the "+$50M" SVG label. Folded "QBP" onto "4.0 cutoff". |
| 4 | Case 01 (`section.cases`) | Heading "Stars measurement" → **"Statistical measurement"**; deck → "I develop the statistical methods behind healthcare quality measurement and cut-point forecasting." The MA / Stars domain stays grounded in the body. Aligns the case with its own exhibits (Lucas critique / Metric / ITS are statistics posts). |
| 5 | Speaking fold summary | "Full list (17 presentations, 2010 to 2017; year shown once per group)" → "Full list (year shown once per group)"; the count + range are in the lead one line above. |
| 6 | Case 03 | Dropped the restated cut-point-dashboard arc ("from a spreadsheet everyone maintained separately to one surface people actually open"); the BHA lead already carries it. Honors the case-layer "annotate, don't duplicate" contract. |
| 7 | About lead | Opener "I started in writing and editing, and moved into data engineering..." → "I moved into data engineering..."; the editorial→research→data-engineering arc stays in the hero-lede (its documented single words-version). About keeps its motivation and methodology thread. |
| 8 | Publications lead | Dropped "the most-cited of them on primary care teams and electronic health records"; the dot plot annotates "most-cited" directly. Tradeoff accepted: the topic is now hover-only (the dot `<title>`). |

## Deliberately kept (considered, not redundant in the default view)

- **373,000 care gaps** in the Health Catalyst `.stat-num` margin note vs. its
  closed fold — this is the documented additivity exception; the `.stat-num`
  exists precisely to surface a number buried in a closed fold, so in the default
  view it shows once.
- **Six-venue Publications fold summary** — a locked decision (the closed-fold
  credibility signal). The dot-plot venue labels are hover-only, so there is no
  *visible* duplication.
- The funnel figcaption's "modeled, not measured" caveat (deliberate standalone
  scope-guard) and the refill figure's 37,000 / 72→12 split (deliberate
  figure-anchoring).

## Result

| | @1363px | @390px |
|---|---:|---:|
| Before (branch tip, this pass) | 9,928px | 17,364px |
| After | **9,537px** | **16,480px** |
| Delta | **−391px** | **−884px** |

No SVG mark, element `id`, sidenote, or vocab canonical was touched, so the gates
hold by construction.

## Verification

- `lint_html`, `lint_notes`, `lint_facts`, `lint_gantt`, `lint_recognition`,
  `lint_links`, `lint_vocab`, `lint_palette` all clean.
- `grep -c '—' index.html` = 0; accent count 12 (≤ 20).
- Headless Chromium, animations disabled, light + dark: no JS errors, no
  horizontal scroll at 1363px or 390px. Deep-links `#education` / `#service` /
  `#work` land their target (Gantt figcaption / case-layer h2) at the top of the
  viewport under the 2rem `scroll-margin-top` — the anchor behavior survived
  removing the lead-in, which was the one mechanical risk in change #1.

## Rollback

Every change is a self-contained prose edit; revert this branch's commit(s) to
restore the prior copy. The Gantt lead-in text (before removal) and each
before/after string are recorded in the table above.
