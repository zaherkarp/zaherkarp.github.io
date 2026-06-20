# Credentialing validity: a statistical post with computed charts

A self-contained essay arguing that physician credentialing and privileging have
high face validity but weak predictive validity. The mechanism is statistical:
the adverse events these systems are meant to catch are rare, per-physician case
volumes are small, and a rare numerator over a small denominator is a
noise-dominated estimate. The four charts are the argument made visible. Every
one is computed from a stated formula on seeded, clearly labelled simulated data
(except the OPPE yield panel, which reports sourced figures).

## Files

- `generate_charts.py` -- seeds the RNG (and prints the seed), simulates the
  data, computes every statistic, writes the four SVGs into `charts/`, and
  assembles `post.html` with the SVGs inlined.
- `charts/` -- the generated SVG figures (`reliability.svg`, `funnel.svg`,
  `quartile_slopegraph.svg`, `oppe_yield.svg`).
- `post.html` -- the finished post. Self-contained: the SVGs are inlined, so it
  renders in any browser with no build step and no external assets.
- `post.md` -- the markdown version of the post (references the SVGs in
  `charts/`).

## Run

```sh
pip install -r requirements.txt
python generate_charts.py
```

The script prints the seed and the computed numbers the prose quotes, then writes
`charts/*.svg` and `post.html`. Open `post.html` in a browser.

## Pinned versions

Generated and verified with:

- Python 3.11.15
- numpy 2.4.6
- matplotlib 3.11.0

See `requirements.txt`.

## Reproducibility

Re-running `generate_charts.py` reproduces byte-identical SVGs and `post.html`.
This holds because the figures depend only on a single
`numpy.random.default_rng(SEED)` generator, and because the script removes the
two run-to-run sources of SVG drift matplotlib would otherwise introduce: the
embedded save timestamp (`metadata={'Date': None}`) and salted element ids (a
fixed `svg.hashsalt`). The seed is `20260620`, printed on every run.

The text that depends on the simulation (the reliability values, the funnel
outlier count, the quartile-change share) is interpolated into `post.html` from
the same computed variables used to draw the charts, so prose and figures cannot
silently disagree.

## What is computed vs sourced

Computed from seeded simulation, labelled illustrative on every figure:

- Reliability curve: `R(n) = var_between / (var_between + var_within / n)`, with
  `var_between = 1`, `var_within = 45` (chosen so reliability near 30 cases sits
  in the 0.3-0.5 range the literature reports).
- Funnel control limits: `p0 +/- z * sqrt(p0 (1 - p0) / n)` at the 95% and 99.8%
  two-sided levels, over 300 providers who all share a true rate `p0 = 3%` and
  lognormal caseloads (median ~30).
- Quartile churn: two independent `Binomial(n, p0)` years for the same providers,
  sorted into quartiles (random tie-breaking), reporting the share that change
  quartile.

Sourced (not simulated, attributed in the post, not altered):

- OPPE is required by The Joint Commission, which also provides a low-volume
  carve-out permitting supplemental outside data.
- A study of 12,854 providers found 0 outliers via OPPE metrics alone, at a
  recurring cost near $50/provider, roughly $78M/year nationally.
- A worked physician-measure case required 138-255 cases per physician to reach
  reliability 0.90; a modest risk-adjustment change reclassified 8 of 56 doctors
  across quartiles.

The OPPE yield panel renders only these sourced figures. Citations are listed at
the foot of `post.md` and must be filled in before publishing the sourced
numbers.
