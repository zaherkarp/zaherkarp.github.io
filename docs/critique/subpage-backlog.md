# Subpage critique backlog

These leads were extracted from the never-committed `archive/design-review-presentations/`
persona presentations before those regenerable files were discarded. They all share one
blind spot: the pushed critique pipeline has only ever critiqued `index.html`, never the
three interactive subpages (`/star-rating-predictor/`, `/life-in-weeks/`,
`/epidemic-simulation/`).

## Leads

1. **Prediction interval on the Star Rating predictor** — source `wilke-presentation.md`:
   "A 'Star Rating Predictor' that emits a scalar without a prediction interval is not a
   statistical graphic — it is a fortune teller in serif type."
   (Confirmed: `star-rating-predictor/index.html` has no uncertainty markup.)

2. **Mechanism-named → finding-named widgets** — source `bremer-presentation.md`:
   rename `star-rating-predictor` → "What a hospital must change to gain one star," etc.
   Apply across all three subpages.

3. **URL-hash / shareable widget state** — source `shneiderman-presentation.md`:
   "No state persistence anywhere... no URL serialization, no localStorage, no export."

4. **CI auto-commits generated artifacts to `main`** — source `bryan-presentation.md`:
   recommends `gh-pages`/Actions deploy instead.
   (Confirmed: workflows push generated files to the working branch; no deploy-pages step.)

To regenerate the full analysis, point `docs/critique/playbook.md` at `/star-rating-predictor/`, `/life-in-weeks/`, `/epidemic-simulation/` (the Subpage archetype in methodology.md, never yet run).
