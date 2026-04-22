---
title: "How the Stars Cliff Simulator Works"
description: "A short explainer for the Stars Cliff Simulator: why ordinal logistic regression is the right tool for a 1–5 star outcome, how P(clearing 4.0★) falls out of the model for free, and what the distance-to-cliff readout actually measures."
publishDate: 2026-04-12
draft: false
tags: ["medicare", "star-ratings", "ordinal-regression", "methodology", "statistics"]
---

# How the Stars Cliff Simulator Works

The [Stars Cliff Simulator](/star-rating-predictor/) is a public, teaching-oriented demo focused on one number — the 4.0★ Quality Bonus Payment threshold that separates Medicare Advantage plans that qualify for QBPs from the 3.5–3.99★ "dead zone" that does not. You adjust four quality inputs and watch the probability of clearing the 4.0★ cliff, the distance to it, and the underlying predicted rating update in real time. This post is the short explainer — what is happening under the hood, and why the cliff-focused readouts are free statistics from the model, not bolted-on heuristics.

It is not about the internal Client-Side Stars Rating Predictor I maintain at Baltimore Health Analytics, which is a different tool with a different audience and a private source tree. The simulator shares an ordinal-regression skeleton with the internal tool — that is the right structural fit for Star Ratings — but this post is strictly about the public simulator. For the long methodology and literature review, see the [methodology and evidence post](/blog/star-rating-predictor-methodology/).

## The right model for ordered outcomes

Star Ratings are **ordinal**: 1 < 2 < 3 < 4 < 5, but the distances between levels are not equal. A plan jumping from 3 to 4 stars triggers Quality Bonus Payments worth tens of millions of dollars. A jump from 4 to 5 does not carry the same financial weight.

Standard linear regression treats the outcome as continuous and assumes equal spacing. Multinomial logistic regression ignores the ordering entirely. **Ordinal logistic regression** — specifically the proportional odds model introduced by McCullagh (1980) — respects both the ordering and the non-equal spacing.

The model estimates cumulative probabilities:

\[P(Y \geq k \mid X) = \sigma(\alpha_k + \beta^T X)\]

where \(\sigma(x) = \frac{1}{1 + e^{-x}}\) is the logistic function, \(\alpha_k\) are threshold parameters for each cumulative split, and \(\beta\) is a shared coefficient vector that captures each input's effect across all thresholds.

This is the **proportional odds assumption**: the effect of each predictor is constant regardless of which threshold you are crossing. It means one set of coefficients tells the full story.

## From cumulative probabilities to a prediction

The cumulative model gives \(P(Y \geq k)\) for each threshold. Individual star-level probabilities come from differencing:

\[P(Y = 1) = 1 - P(Y \geq 2)\]

\[P(Y = k) = P(Y \geq k) - P(Y \geq k+1) \quad \text{for } k = 2, 3, 4\]

\[P(Y = 5) = P(Y \geq 5)\]

The expected value \(E[Y] = \sum_{k=1}^{5} k \cdot P(Y = k)\) gives the predicted star rating displayed in the simulator.

## The cliff is a free statistic

The question a Stars analyst actually cares about is not "what is my expected rating?" but "will we clear 4.0★ and qualify for Quality Bonus Payments?" The ordinal model produces this directly:

\[P(\text{clearing 4.0★ cliff}) = P(Y = 4) + P(Y = 5) = P(Y \geq 4)\]

This falls out of the cumulative structure without any additional modeling — it is the `(α₄ + βᵀX)` threshold evaluated through the sigmoid. The simulator displays this as the hero statistic under the predicted rating. A linear regression on stars could produce a point estimate of the expected rating, but it could not produce this probability. That is the reason ordinal is the right tool for the cliff: the most useful scalar the page could report is a side-effect of the model's structure, not a post-hoc transformation.

The **distance-to-cliff** readout, \(E[Y] - 4.0\), is complementary. P(clearing) tells you how likely you are to clear the threshold in the model's probabilistic sense; distance-to-cliff tells you how close the point estimate sits to it in the units you're adjusting. When the reward factor toggle is active, distance incorporates its +0.4 additive bonus; P(clearing) reflects the underlying latent probability, since the reward factor is a deterministic CMS add-on rather than a shift in the ordinal structure.

## Calibration to CMS weights

The simulator uses four inputs that map to real CMS Star Rating domains:

| Input | CMS Domain | CMS Weight | Coefficient (\(\beta\)) |
|-------|------------|------------|----------------------|
| HEDIS Composite Rate | Part C — Process & Outcome | 1–3× | +0.08 per pp |
| CAHPS Member Satisfaction | Part C — Patient Experience | 2× | +1.50 per unit |
| Medication Adherence | Part D — Drug Measures | **3×** | +0.06 per pp |
| Readmission Rate | Part C — Intermediate Outcome | **3×** | −0.08 per pp |

The coefficients are calibrated to satisfy two constraints simultaneously:

1. **Weight proportionality**: Each input's total contribution across its realistic slider range is proportional to its share of CMS weighted points (out of 81 total for MA-PD contracts).
2. **Distribution calibration**: At median slider positions, the predicted distribution matches the 2025 MA-PD star distribution — average 3.92 stars, approximately 42% of contracts at 4 stars or above, roughly 2% at 5 stars.

The four intercepts (\(\alpha_2 = -10.1\), \(\alpha_3 = -11.76\), \(\alpha_4 = -15.1\), \(\alpha_5 = -18.17\)) position the thresholds so that a plan at the 50th percentile on all inputs lands around 3.2 stars.

## The "What Would Move the Needle?" calculation

For each input, the model simulates a feasible one-year improvement:

| Input | Simulated Step | Rationale |
|-------|---------------|-----------|
| HEDIS Composite | +5 pp | Achievable with targeted gap closure |
| CAHPS Satisfaction | +0.3 points | Typical gain from member experience initiatives |
| Medication Adherence | +5 pp | Consistent with MTM program impact |
| Readmission Rate | −2 pp | Achievable with care transition programs |

It computes \(E[Y \mid x_j + \Delta] - E[Y \mid x_j]\) for each input and reports the two highest-impact levers. Because the logistic function is nonlinear, the highest-impact lever changes depending on where the plan currently sits — it is largest near the ordinal cut-points and smallest in the tails.

## CMS Reward Factor

Plans maintaining 4 or more stars for three consecutive years receive up to +0.4 stars added to the summary rating before final rounding. The simulator's toggle simulates this additive bonus.

## What the model does not include

1. **No real training data.** Coefficients are synthetic, calibrated to CMS weight shares and the published star distribution. A production model would be trained on contract-level measure scores.
2. **Simplified inputs.** CMS uses 42 measures across 9 domains. The four inputs here represent roughly 40% of total weighted points; the remaining 60% is absorbed into the intercepts.
3. **No case-mix adjustment.** CMS applies a Categorical Adjustment Index (CAI) for plans serving dual-eligible, disabled, or low-income populations. D-SNP plans should treat these predictions as pre-adjustment estimates.
4. **No improvement measures.** CMS awards credit for year-over-year improvement, which requires longitudinal data not modeled here.
5. **Adherence treated as a single composite.** The three PDC measures (diabetes, RAS, statins) have different baseline distributions and intervention profiles.

Despite these simplifications, the model accurately represents the correct statistical framework, the correct relative importance of each domain, and the nonlinear sensitivity structure inherent in ordinal logistic regression.

## References

1. McCullagh, P. (1980). Regression Models for Ordinal Data. *JRSS Series B*, 42(2), 109–142.
2. CMS (2024). Medicare 2025 Part C & D Star Ratings Technical Notes.
3. CMS (2024). 2025 Medicare Advantage and Part D Star Ratings Fact Sheet.
4. Kurian, N. et al. (2021). Predicting Hospital Overall Quality Star Ratings in the USA. *Healthcare*, 9(4), 486.
5. Hohmann, N. et al. (2018). Association between Higher Generic Drug Use and Medicare Part D Star Ratings. *Value in Health*, 21(10), 1186–1191.
