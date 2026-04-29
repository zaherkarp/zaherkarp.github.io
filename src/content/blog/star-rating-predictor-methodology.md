---
title: "The Stars Cliff Simulator: Methodology & Evidence"
description: "The statistical methodology and published literature behind the Stars Cliff Simulator — a public, teaching-oriented ordinal logistic regression tool focused on the 4.0★ Quality Bonus Payment threshold."
publishDate: 2026-04-05
tags: ["medicare", "star-ratings", "ordinal-regression", "methodology", "interactive"]
homepageMarginnote: "The 4.0 star Quality Bonus Payment threshold creates a sharp non-linearity in Medicare Advantage plan economics. Crossing it is worth roughly $50M to a mid-size contract."
---

## TL;DR for Executives

- **What it does:** The [Stars Cliff Simulator](/star-rating-predictor/) is an interactive, teaching-oriented demo focused on one number — the 4.0★ Quality Bonus Payment threshold. Move four quality inputs; watch the probability of clearing the 4.0★ cliff update in real time.
- **Why it matters:** Plans at ≥4.0★ qualify for Quality Bonus Payments (QBPs) — a 5% premium increase worth $50M+ annually for large contracts. The 4.0★ threshold is the single most consequential cliff in managed care economics, and the 3.5–3.99★ "dead zone" is where quality-improvement ROI is most nonlinear.
- **What it shows you:** The probability of clearing 4.0★, the distance from the cliff in expected stars, and which of the four quality levers — HEDIS, CAHPS, medication adherence, or readmission — delivers the most star improvement at your plan's current performance level.

---

## Scope: what this post documents (and what it does not)

This post is the methodology and evidence appendix for the **Stars Cliff Simulator**, the public interactive tool on this site at [/star-rating-predictor/](/star-rating-predictor/). The simulator is a single-page, browser-side demo built for a general audience — students, analysts new to Medicare Advantage, non-technical stakeholders who need to understand the shape of the cliff and the ordinal structure that produces it.

It is *not* the same thing as the internal Client-Side Stars Rating Predictor I maintain at Baltimore Health Analytics. That internal tool is a cut-point dashboard that runs against live measure feeds to project contract-level cut-point crossings for remediation planning; its source is private, and this post does not describe it. The two tools share a statistical skeleton (ordinal logistic regression with cut-point visualization) because ordinal models are the right structural fit for Star Ratings — not because one is a rewrite of the other.

With that distinction out of the way: the simulator lets visitors adjust four healthcare quality inputs and watch a predicted Medicare Star Rating update in real time, with the readouts focused on clearing the 4.0★ QBP cliff. This post documents the statistical approach, explains why ordinal logistic regression is the right tool for the job, and cites the CMS methodology and published research that inform the model's design.

## What the Simulator Does

Four sliders control inputs that map to real CMS Star Rating domains:

| Slider | Real-World Analog | CMS Domain | CMS Weight |
|--------|-------------------|------------|------------|
| HEDIS Composite Rate | Weighted average of clinical quality measures (breast cancer screening, colorectal screening, A1C control, blood pressure control, statin therapy, etc.) | Part C — Process & Outcome | 1–3× |
| CAHPS Member Satisfaction | Consumer Assessment of Healthcare Providers and Systems survey score (provider communication, access, customer service, care coordination) | Part C — Patient Experience | 2× |
| Medication Adherence (D-SNP) | Proportion of Days Covered (PDC) ≥80% across three measures: diabetes medications, RAS antagonists, and statins | Part D — Drug Measures | **3×** |
| Readmission Rate | Plan All-Cause Readmissions (PCR) within 30 days | Part C — Intermediate Outcome | **3×** |

The output foregrounds the 4.0★ cliff:

- **P(clearing 4.0★ cliff)** — the probability that the underlying ordinal model places the plan at 4★ or 5★. This is the hero statistic and the question a Stars analyst actually asks.
- **Distance to cliff** — expected rating minus 4.0, with sign. Quantifies the margin in the same units the user is manipulating.
- A predicted overall Star Rating (expected value) on a 1–5 scale with the full probability distribution across all five star levels
- An **ordinal threshold visualization** with the 3→4 cut-point highlighted as the QBP cliff, showing where the linear predictor falls relative to each cut-point
- **Plain-language impact guidance** — which quality lever offers the largest star gain from a feasible improvement at the current performance level
- National **percentile markers** (25th, 50th, 75th) on each slider for benchmarking
- A contextual callout that distinguishes three regimes: above the cliff, the 3.5–3.99★ "dead zone," and below 3.5★

An optional **CMS Reward Factor** toggle adds up to +0.4 stars, simulating the bonus CMS grants to plans maintaining ≥4 stars for 3+ consecutive years. When active, the distance-to-cliff readout incorporates the reward; the P(clearing) readout reports the raw ordinal probability, because the reward factor is a deterministic add-on rather than a shift in the underlying latent.

## The Financial Stakes: Quality Bonus Payments

The 4-star threshold is the most consequential cliff in Medicare Advantage economics. Plans at ≥4 stars qualify for **Quality Bonus Payments** — a 5% increase in their CMS benchmark payment. For a plan with 200,000 members, this translates to roughly **$50–80 million annually** in additional revenue.

The stakes are asymmetric:
- **Below 3.5★**: No QBP eligibility. At ≤2.5★ for 3 consecutive years, CMS may terminate the contract entirely.
- **3.5–3.99★**: Plans round to 3.5★ and receive no bonus, despite being close. This is the "dead zone."
- **≥4.0★**: Full QBP eligibility. The reward factor can push plans that sustain 4★+ even higher.

This cliff function is why quality improvement ROI is heavily nonlinear — a 0.1-star improvement from 3.9 to 4.0 can be worth tens of millions, while the same improvement from 4.3 to 4.4 has essentially zero marginal financial impact. The simulator is designed around this asymmetry: the hero readouts are about the cliff, not about the point estimate.

## Why Ordinal Logistic Regression?

Star Ratings are an **ordinal outcome**: 1 < 2 < 3 < 4 < 5, but the distances between levels are not equal. A plan jumping from 3 to 4 stars triggers quality bonus payments worth millions; 4 to 5 does not carry the same marginal financial impact.

Standard linear regression treats the outcome as continuous and assumes equal spacing. Multinomial logistic regression ignores the ordering entirely. **Ordinal (proportional odds) logistic regression** respects both the ordering and the non-equal spacing by modeling cumulative probabilities:

\[P(Y \geq k \mid X) = \sigma(\alpha_k + \beta^T X)\]

where \(\sigma\) is the logistic function \(\sigma(x) = \frac{1}{1 + e^{-x}}\), \(\alpha_k\) are threshold parameters (intercepts) for each cumulative split, and \(\beta\) is a shared coefficient vector.

This is the **proportional odds model** introduced by McCullagh (1980), the standard approach for ordinal outcomes in biomedical research.

### Foundational Reference

> **McCullagh, P.** (1980). Regression Models for Ordinal Data. *Journal of the Royal Statistical Society, Series B*, 42(2), 109–142.
> [Wiley Online Library](https://rss.onlinelibrary.wiley.com/doi/10.1111/j.2517-6161.1980.tb01109.x) ·
> [Author PDF](https://www.stat.uchicago.edu/~pmcc/pubs/paper2.pdf)

McCullagh showed that the proportional odds model provides interpretable odds ratios that summarize the effect of each predictor across all threshold cutpoints, making it ideal for ordered rating scales.

## CMS Star Ratings Methodology

CMS publishes annual Technical Notes that detail exactly how Star Ratings are calculated. The key points relevant to the simulator:

### Measure Structure

The 2025 Star Ratings include up to **42 measures** across **9 domains** for MA-PD contracts. Each measure receives a weight from 1 to 5. CMS assigns individual measure stars using either clustering or relative distribution methods, then computes weighted summary ratings.

> **CMS** (2024). Medicare 2025 Part C & D Star Ratings Technical Notes (Updated 10/03/2024).
> [PDF](https://www.cms.gov/files/document/2025-star-ratings-technical-notes.pdf)
>
> **CMS** (2024). 2025 Medicare Advantage and Part D Star Ratings Fact Sheet.
> [CMS Newsroom](https://www.cms.gov/newsroom/fact-sheets/2025-medicare-advantage-part-d-star-ratings)

### Medication Adherence: Triple-Weighted and Highly Sensitive

Three medication adherence measures — for diabetes medications, RAS antagonists (hypertension), and statins (cholesterol) — each carry a **weight of 3** in the overall Star Rating. Together they account for 9 of 81 total weighted stars (11.1%) in the 2026 ratings cycle.

**Key nuance:** CMS measures the percentage of members achieving **PDC ≥80%** (Proportion of Days Covered at or above 80%), not the plan's mean PDC. This is a binary threshold applied at the member level, then aggregated. The three sub-measures have meaningfully different baseline performance profiles — statin adherence typically runs 5–8 percentage points higher than diabetes medication adherence across plans — so interventions should be targeted by measure, not treated as a monolith.

**As little as 3 percentage points in PDC can separate a 3-star from a 5-star rating** on the RAS antagonist adherence measure, making this the single most actionable lever for many plans.

A 2025 decade-long analysis confirmed that plans performing well on adherence measures have substantially higher rates of achieving ≥4-star overall ratings and qualifying for quality bonus payments:

> **Akinbosoye, O. E., et al.** (2025). The influence of medication adherence on Medicare Star Ratings: A decade-long analysis of health plan performance. *Journal of Managed Care & Specialty Pharmacy*, 31(5), 512.
> [JMCP](https://www.jmcp.org/doi/10.18553/jmcp.2025.31.5.512) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12039503/)

### Plan All-Cause Readmissions Now Triple-Weighted

For 2025, CMS increased the weight of the Plan All-Cause Readmissions (PCR) measure from **1 to 3**, making it one of the most heavily weighted Part C measures. PCR assesses the percentage of hospital stays followed by an unplanned readmission within 30 days.

This change contributed to the average overall MA-PD Star Rating dropping to 3.92 (down 0.15 stars) — the lowest in four years — and the number of 5-star contracts falling from 38 to just 7.

**Operational note for D-SNP plans:** Readmission is driven heavily by social determinants of health — housing instability, food insecurity, lack of transportation — making it substantially harder to move than clinical quality or adherence measures for plans serving dual-eligible populations. The model's coefficients treat a percentage-point improvement in readmission equivalently to one in HEDIS, but the operational cost and difficulty of achieving that improvement can differ by an order of magnitude depending on population acuity.

> **CMS** (2024). 2025 Medicare Advantage and Part D Star Ratings Fact Sheet.
> [CMS Newsroom](https://www.cms.gov/newsroom/fact-sheets/2025-medicare-advantage-part-d-star-ratings)
>
> **AdhereHealth** (2024). Conquering the Plan All-Cause Readmissions (PCR) Measure.
> [Article](https://adherehealth.com/blog-healthcare-quality-improvement-measures-plan-all-cause-readmission/)

### CAHPS Patient Experience Measures

CAHPS survey scores evaluate member satisfaction across dimensions like provider communication, access to care, and customer service. These measures have been weighted between 2× and 4× in recent years. For 2026, CMS reduced the weight from 4 back to 2, but CAHPS remains a significant contributor to overall ratings.

**Measurement noise caveat:** CAHPS scores are derived from a sample survey with response rates that vary widely across plans (typically 20–45%). Low response rates amplify sampling noise, meaning that a plan's true satisfaction level may differ meaningfully from its reported score. The model treats CAHPS as a precise input, but users should interpret the output with this measurement uncertainty in mind — particularly for plans with small enrollment or low response rates.

> **MA-PDP CAHPS** (2025). Scoring and Star Ratings.
> [ma-pdpcahps.org](https://ma-pdpcahps.org/en/scoring-and-star-ratings/)
>
> **Health Management Associates** (2024). HMA Analysis of Medicare Advantage Star Rating Challenges.
> [HMA Blog](https://www.healthmanagement.com/blog/hma-analysis-of-medicare-advantage-star-rating-challenges/)

### Reward Factor

CMS applies a **Reward Factor** of up to +0.4 stars to plans that have maintained ≥4-star overall ratings for three or more consecutive years. This bonus is additive — applied to the weighted summary rating before final rounding — and can be the difference between a 3.5-star and a 4-star plan qualifying for quality bonus payments.

The simulator includes a toggle to simulate this factor, reflecting its material impact on final ratings.

### Improvement Measures

CMS also evaluates **year-over-year improvement** in certain measures. Plans showing statistically significant improvement may receive credit even if their absolute level remains below the top cut-point. The simulator does not model improvement measures, as they require longitudinal data (prior-year performance), but they represent a meaningful path to higher ratings for plans in the 3.0–3.5★ range that are on an upward trajectory.

## Published Precedent: Ordinal Logistic Regression for Star Ratings

Multiple published studies have applied ordinal logistic regression to Medicare star ratings or closely related healthcare quality outcomes.

### Kurian et al. (2021) — Hospital Star Ratings

> **Kurian, N., Maid, J., Mitra, S., Rhyne, L., Korvink, M., & Gunn, L. H.** (2021). Predicting Hospital Overall Quality Star Ratings in the USA. *Healthcare*, 9(4), 486.
> [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8074583/) · [MDPI](https://www.mdpi.com/2227-9032/9/4/486) · [PubMed](https://pubmed.ncbi.nlm.nih.gov/33924198/)

- Applied **ordinal logistic regression with stepwise variable selection** to 4,519 U.S. hospitals
- Found that **20 performance measures** (from 57 total) contained all the relevant information for star rating prediction after accounting for correlation
- Used multiple imputation to handle missing data, enabling inference even when not all measures are available
- Demonstrated that the proportional odds model provides **interpretable odds ratios** for the relationship between quality measures and star rating levels

### Hohmann et al. (2018) — Part D Star Ratings

> **Hohmann, N., Hansen, R., Garza, K. B., Harris, I., Kiptanui, Z., & Qian, J.** (2018). Association between Higher Generic Drug Use and Medicare Part D Star Ratings: An Observational Analysis. *Value in Health*, 21(10), 1186–1191.
> [PubMed](https://pubmed.ncbi.nlm.nih.gov/30314619/) · [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1098301518302766)

This is the most direct methodological precedent: Hohmann et al. **explicitly used ordinal logistic regression** to model Medicare Part D summary and domain star ratings (1–5) as a function of generic drug dispensing rates, controlling for contract type and enrollment. They found higher generic dispensing was associated with higher summary star ratings (adjusted OR 1.08, 95% CI 1.04–1.12).

### Xie et al. (2023) — Adherence Predicts Clinical Outcomes

> **Xie, Z., St. Clair, P., Goldman, D. P., & Joyce, G. F.** (2023). Is There a Relationship Between Part D Medication Adherence and Part C Intermediate Outcomes Star Ratings Measures? *Journal of Managed Care & Specialty Pharmacy*, 29(8), 918–925.
> [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10397682/)

Analyzed 366 contracts and found medication adherence measures explained **27–29% of variance** in related clinical outcomes (\(R^2\) = 0.27–0.29). Each unit increase in adherence increased odds of top-quartile performance by factors of 4.13–4.69, providing strong empirical support for adherence as a key predictor.

### Lingsma et al. (2021) — Why Ordinal Beats Binary

> **Lingsma, H. F., Bottle, A., Middleton, S., Kievit, J., Steyerberg, E. W., & Marang-van de Mheen, P. J.** (2021). Ordinal Outcome Analysis Improves the Detection of Between-Hospital Differences in Outcome. *BMC Medical Research Methodology*, 21(1), 4.
> [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7788719/)

Demonstrated that ordinal outcome analysis substantially improves statistical power for detecting quality differences compared to dichotomizing outcomes (e.g., "4+ stars vs. below"). This provides methodological justification for treating star ratings as ordinal rather than collapsing them into binary categories.

Together, these studies validate using a small number of composite quality inputs in an ordinal logistic framework to predict a 1–5 star outcome.

## How the Simulator's Model Works

### Architecture

The simulator implements a **cumulative logit model** (proportional odds) entirely in client-side JavaScript. The core equation:

\[P(Y \geq k \mid X) = \sigma(\alpha_k + \beta_1 \cdot \text{HEDIS} + \beta_2 \cdot \text{CAHPS} + \beta_3 \cdot \text{MedAdherence} + \beta_4 \cdot \text{Readmission})\]

Four threshold parameters (\(\alpha_2, \alpha_3, \alpha_4, \alpha_5\)) define the cumulative splits. The shared coefficient vector \(\beta\) captures each input's effect across all thresholds (the proportional odds assumption).

### Converting Cumulative Probabilities to Category Probabilities

The cumulative model yields \(P(Y \geq k)\) for each threshold. Individual category probabilities are obtained by differencing:

\[P(Y = 1) = 1 - P(Y \geq 2)\]

\[P(Y = 2) = P(Y \geq 2) - P(Y \geq 3)\]

\[P(Y = 3) = P(Y \geq 3) - P(Y \geq 4)\]

\[P(Y = 4) = P(Y \geq 4) - P(Y \geq 5)\]

\[P(Y = 5) = P(Y \geq 5)\]

The expected value \(E[Y] = \sum_{k=1}^{5} k \cdot P(Y = k)\) gives the predicted star rating displayed in the UI. The **P(clearing 4.0★)** hero statistic is simply \(P(Y = 4) + P(Y = 5)\) from this same distribution — a free statistic the ordinal model produces without any extra math, and the most policy-relevant scalar the model can report.

### Coefficient Calibration

The synthetic coefficients are calibrated to satisfy two constraints simultaneously:

1. **CMS weight proportionality**: Each input's total contribution across its realistic slider range is proportional to its share of CMS weighted points.
2. **Distribution calibration**: At median slider positions, the predicted distribution matches the 2025 MA-PD star distribution (avg 3.92, ~42% at ≥4★, ~2% at 5★).

#### CMS Weight Share Analysis

From the 2025 Technical Notes, the 81 total weighted points for MA-PD contracts break down as:

| Domain | Measures | Weight Each | Total Points | Share |
|--------|----------|-------------|-------------|-------|
| HEDIS clinical composite | ~6 key measures | 1–3 | ~12 | 15% |
| CAHPS experience | 4 measures | 2 | 8 | 10% |
| Medication adherence | 3 measures | **3** | **9** | **11%** |
| Readmission (PCR) | 1 measure | **3** | **3** | 4% |
| Other Part C & D | ~28 measures | 1–3 | ~49 | 60% |

The simulator's four inputs represent 40% of total CMS weighted points. The "other" 60% is held constant (absorbed into the intercepts), a standard approach when building a reduced-form predictor from the most policy-relevant measures.

#### Resulting Coefficients

| Input | β | Scale Range | Total Effect | Relative Share |
|-------|---|-------------|-------------|----------------|
| HEDIS Composite | +0.08 / pp | 55%–95% (40pp) | 3.20 | 31% |
| CAHPS Score | +1.50 / unit | 2.5–4.8 (2.3u) | 3.45 | 33% |
| Medication Adherence | +0.06 / pp | 50%–92% (42pp) | 2.52 | 24% |
| Readmission Rate | −0.08 / pp | 8%–22% (14pp) | 1.12 | 11% |

These proportions track the CMS weight shares when accounting for scale differences: CAHPS has fewer scale units but high weight per measure, while readmission is a single measure despite its triple weight.

#### Intercept Calibration

The four intercepts (\(\alpha_2 = -10.1\), \(\alpha_3 = -11.76\), \(\alpha_4 = -15.1\), \(\alpha_5 = -18.17\)) are set so that at median input values:

\[P(Y \geq 2) \approx 0.99, \quad P(Y \geq 3) \approx 0.95, \quad P(Y \geq 4) \approx 0.40, \quad P(Y \geq 5) \approx 0.03\]

This produces an expected rating of ~3.2★ at default slider positions (representing a middling plan), consistent with the real-world distribution where most plans cluster between 3.0 and 4.5 stars.

### Reward Factor

When the CMS Reward Factor toggle is enabled, +0.4 is added to \(E[Y]\), capped at 5.0. This models the CMS mechanism where sustained high performance receives an additive bonus before final rounding.

### Impact Guidance

The simulator computes **scenario-based impact guidance** for each input by simulating a feasible one-year improvement:

| Input | Simulated Improvement | Rationale |
|-------|----------------------|-----------|
| HEDIS Composite | +5 percentage points | Achievable with targeted HEDIS gap closure campaigns |
| CAHPS Satisfaction | +0.3 points | Typical gain from focused member experience initiatives |
| Medication Adherence | +5 percentage points | Consistent with MTM program impact in published literature |
| Readmission Rate | −2 percentage points | Achievable with care transition programs, though harder for D-SNP populations |

For each input, the model computes \(E[Y \mid x_j + \Delta] - E[Y \mid x_j]\) and reports the two highest-impact levers in plain language (e.g., "Improving medication adherence from 70% → 75% would shift the predicted rating by +0.3★").

Because the logistic function is nonlinear, impact varies across the input space — it is largest near the ordinal cut-points and smallest in the tails. This means the highest-impact lever changes depending on where your plan currently sits.

### Threshold Visualization

The ordinal threshold bar shows the four cut-points (\(-\alpha_2, -\alpha_3, -\alpha_4, -\alpha_5\)) on a linear predictor scale, with a moving indicator for the current \(z\) value. This makes visible the core mechanism of the proportional odds model: the linear predictor \(z\) crossing successive thresholds shifts probability mass from lower to higher star categories.

## Limitations and Disclaimers

The simulator uses **synthetic weights** that are not trained on actual CMS contract-level data. The model is illustrative — a teaching tool, not a production predictor:

1. **No real training data.** Actual Star Rating prediction would require contract-level measure scores linked to final ratings, which CMS publishes but which would need proper train/test splitting and cross-validation.

2. **Simplified inputs.** Real Star Ratings incorporate 42 measures across 9 domains. Our 4 inputs represent the most influential categories but absorb the remaining ~60% of weighted points into the intercepts. This is a *reduced-form* model, not a full specification.

3. **Proportional odds assumption.** We assume the effect of each predictor is constant across all threshold cutpoints. In practice, this assumption should be tested with a Brant test or graphical method (Harrell, 2001). For star ratings, the assumption is plausible for HEDIS and adherence (monotonic quality measures) but may be violated for readmission rate, where plans with extreme values may face nonlinear threshold effects.

4. **No case-mix adjustment (CAI).** This is the most important limitation for D-SNP and other plans serving high-acuity populations. CMS applies a **Categorical Adjustment Index (CAI)** that adjusts measure-level stars for the proportion of enrollees who are dual-eligible (Medicare + Medicaid), disabled, or low-income subsidy recipients. CAI adjustments can shift individual measure stars by up to a full level. Plans serving predominantly dual-eligible populations should interpret the simulator's predictions as *pre-adjustment* estimates — actual final ratings may differ substantially. A future version could include a D-SNP population toggle to approximate CAI effects.

5. **No interaction terms.** The model assumes additive effects. In reality, HEDIS and medication adherence are partially overlapping constructs (adherence measures feed into HEDIS composites for some plans), and the joint effect of poor readmission + poor CAHPS may be super-additive. A production model would test for interactions.

6. **Input ranges are bounded.** Slider ranges reflect the 5th–95th percentile of observed plan performance, not the full theoretical range. This improves face validity but means the model cannot represent extreme outlier plans.

7. **No improvement measures.** CMS awards credit for statistically significant year-over-year improvement, which can boost ratings for plans on an upward trajectory even if absolute levels remain modest. This requires longitudinal data and is not modeled here.

8. **Adherence is treated as a single composite.** The three PDC measures (diabetes, RAS, statins) have different baseline distributions and different intervention profiles. Statin adherence typically runs 5–8 points higher than diabetes adherence. The single slider is a weighted average, but operational improvement strategies should target each measure independently.

Despite these simplifications, the simulator accurately represents:
- The correct statistical framework (ordinal logistic regression) for a 1–5 ordered outcome
- The correct direction and CMS-proportional relative importance of each input domain
- The probabilistic nature of quality prediction (showing full distributions, not just point estimates)
- The nonlinear sensitivity structure inherent in logistic models (impact varies by position on the curve)
- The material impact of CMS's reward factor and QBP threshold on plan economics

## References

1. McCullagh, P. (1980). Regression Models for Ordinal Data. *JRSS Series B*, 42(2), 109–142.
2. CMS (2024). Medicare 2025 Part C & D Star Ratings Technical Notes.
3. CMS (2024). 2025 Medicare Advantage and Part D Star Ratings Fact Sheet.
4. Kurian, N. et al. (2021). Predicting Hospital Overall Quality Star Ratings in the USA. *Healthcare*, 9(4), 486.
5. Hohmann, N. et al. (2018). Association between Higher Generic Drug Use and Medicare Part D Star Ratings. *Value in Health*, 21(10), 1186–1191.
6. Xie, Z. et al. (2023). Is There a Relationship Between Part D Medication Adherence and Part C Intermediate Outcomes Star Ratings Measures? *JMCP*, 29(8), 918–925.
7. Lingsma, H. F. et al. (2021). Ordinal Outcome Analysis Improves the Detection of Between-Hospital Differences in Outcome. *BMC Medical Research Methodology*, 21(1), 4.
8. Akinbosoye, O. E. et al. (2025). The influence of medication adherence on Medicare Star Ratings. *JMCP*, 31(5), 512.
9. Harrell, F. E. (2001). *Regression Modeling Strategies*. Springer.
10. SAS Institute (2005). Using the Proportional Odds Model for Health-Related Research. *SUGI 30 Proceedings*, Paper 205-30.
