---
title: "Building a Browser-Based Star Rating Predictor: Methodology & Evidence"
description: "Technical documentation and literature review supporting the ordinal logistic regression model used in the interactive Medicare Star Rating predictor on this site."
publishDate: 2026-03-14
tags: ["medicare", "star-ratings", "ordinal-regression", "methodology", "interactive"]
---

The interactive demo on this site lets visitors adjust four healthcare quality inputs and watch a predicted Medicare Star Rating update in real time. This post documents the statistical approach, explains why ordinal logistic regression is the right tool for the job, and cites the CMS methodology and published research that inform the model's design.

## What the Demo Does

Four sliders control inputs that map to real CMS Star Rating domains:

| Slider | Real-World Analog | CMS Domain |
|--------|-------------------|------------|
| HEDIS Composite Rate | Weighted average of clinical quality measures (e.g., breast cancer screening, A1C control) | Part C — Process & Outcome |
| CAHPS Member Satisfaction | Consumer Assessment of Healthcare Providers and Systems survey score | Part C — Patient Experience |
| Medication Adherence (D-SNP) | Proportion of Days Covered for diabetes, statins, and RAS antagonists | Part D — Drug Measures |
| Readmission Rate | Plan All-Cause Readmissions (PCR) within 30 days | Part C — Intermediate Outcome |

The output is a predicted overall Star Rating on a 1–5 scale, with a probability distribution across all five levels.

## Why Ordinal Logistic Regression?

Star Ratings are an **ordinal outcome**: 1 < 2 < 3 < 4 < 5, but the distances between levels are not equal. A plan jumping from 3 to 4 stars triggers quality bonus payments worth millions; 4 to 5 does not carry the same marginal financial impact.

Standard linear regression treats the outcome as continuous and assumes equal spacing. Multinomial logistic regression ignores the ordering entirely. **Ordinal (proportional odds) logistic regression** respects both the ordering and the non-equal spacing by modeling cumulative probabilities:

$$P(Y \geq k \mid X) = \sigma(\alpha_k + \beta^T X)$$

where $\sigma$ is the logistic function, $\alpha_k$ are threshold parameters (intercepts) for each cumulative split, and $\beta$ is a shared coefficient vector.

This is the **proportional odds model** introduced by McCullagh (1980), the standard approach for ordinal outcomes in biomedical research.

### Foundational Reference

> **McCullagh, P.** (1980). Regression Models for Ordinal Data. *Journal of the Royal Statistical Society, Series B*, 42(2), 109–142.
> [Wiley Online Library](https://rss.onlinelibrary.wiley.com/doi/10.1111/j.2517-6161.1980.tb01109.x) ·
> [Author PDF](https://www.stat.uchicago.edu/~pmcc/pubs/paper2.pdf)

McCullagh showed that the proportional odds model provides interpretable odds ratios that summarize the effect of each predictor across all threshold cutpoints, making it ideal for ordered rating scales.

## CMS Star Ratings Methodology

CMS publishes annual Technical Notes that detail exactly how Star Ratings are calculated. The key points relevant to this demo:

### Measure Structure

The 2025 Star Ratings include up to **42 measures** across **9 domains** for MA-PD contracts. Each measure receives a weight from 1 to 5. CMS assigns individual measure stars using either clustering or relative distribution methods, then computes weighted summary ratings.

> **CMS** (2024). Medicare 2025 Part C & D Star Ratings Technical Notes (Updated 10/03/2024).
> [PDF](https://www.cms.gov/files/document/2025-star-ratings-technical-notes.pdf)
>
> **CMS** (2024). 2025 Medicare Advantage and Part D Star Ratings Fact Sheet.
> [CMS Newsroom](https://www.cms.gov/newsroom/fact-sheets/2025-medicare-advantage-part-d-star-ratings)

### Medication Adherence Measures Are Triple-Weighted

Three medication adherence measures — for diabetes medications, RAS antagonists (hypertension), and statins (cholesterol) — each carry a **weight of 3** in the overall Star Rating. Together they account for 9 of 81 total weighted stars (11.1%) in the 2026 ratings cycle.

A 2025 decade-long analysis confirmed that plans performing well on adherence measures have substantially higher rates of achieving ≥4-star overall ratings and qualifying for quality bonus payments:

> **Akinbosoye, O. E., et al.** (2025). The influence of medication adherence on Medicare Star Ratings: A decade-long analysis of health plan performance. *Journal of Managed Care & Specialty Pharmacy*, 31(5), 512.
> [JMCP](https://www.jmcp.org/doi/10.18553/jmcp.2025.31.5.512) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12039503/)

As little as 3% in PDC can separate a 3-star from a 5-star rating on the RAS antagonist adherence measure, underscoring the sensitivity of these inputs.

### Plan All-Cause Readmissions Now Triple-Weighted

For 2025, CMS increased the weight of the Plan All-Cause Readmissions (PCR) measure from **1 to 3**, making it one of the most heavily weighted Part C measures. PCR assesses the percentage of hospital stays followed by an unplanned readmission within 30 days.

This change contributed to the average overall MA-PD Star Rating dropping to 3.92 (down 0.15 stars) — the lowest in four years — and the number of 5-star contracts falling from 38 to just 7.

> **CMS** (2024). 2025 Medicare Advantage and Part D Star Ratings Fact Sheet.
> [CMS Newsroom](https://www.cms.gov/newsroom/fact-sheets/2025-medicare-advantage-part-d-star-ratings)
>
> **AdhereHealth** (2024). Conquering the Plan All-Cause Readmissions (PCR) Measure.
> [Article](https://adherehealth.com/blog-healthcare-quality-improvement-measures-plan-all-cause-readmission/)

### CAHPS Patient Experience Measures

CAHPS survey scores evaluate member satisfaction across dimensions like provider communication, access to care, and customer service. These measures have been weighted between 2x and 4x in recent years. For 2026, CMS reduced the weight from 4 back to 2, but CAHPS remains a significant contributor to overall ratings.

> **MA-PDP CAHPS** (2025). Scoring and Star Ratings.
> [ma-pdpcahps.org](https://ma-pdpcahps.org/en/scoring-and-star-ratings/)
>
> **Health Management Associates** (2024). HMA Analysis of Medicare Advantage Star Rating Challenges.
> [HMA Blog](https://www.healthmanagement.com/blog/hma-analysis-of-medicare-advantage-star-rating-challenges/)

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

Analyzed 366 contracts and found medication adherence measures explained **27–29% of variance** in related clinical outcomes (R² = 0.27–0.29). Each unit increase in adherence increased odds of top-quartile performance by factors of 4.13–4.69, providing strong empirical support for adherence as a key predictor.

### Lingsma et al. (2021) — Why Ordinal Beats Binary

> **Lingsma, H. F., Bottle, A., Middleton, S., Kievit, J., Steyerberg, E. W., & Marang-van de Mheen, P. J.** (2021). Ordinal Outcome Analysis Improves the Detection of Between-Hospital Differences in Outcome. *BMC Medical Research Methodology*, 21(1), 4.
> [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7788719/)

Demonstrated that ordinal outcome analysis substantially improves statistical power for detecting quality differences compared to dichotomizing outcomes (e.g., "4+ stars vs. below"). This provides methodological justification for treating star ratings as ordinal rather than collapsing them into binary categories.

Together, these studies validate using a small number of composite quality inputs in an ordinal logistic framework to predict a 1–5 star outcome.

## How the Demo Model Works

### Architecture

The demo implements a **cumulative logit model** (proportional odds) entirely in client-side JavaScript:

```
P(Y ≥ k | X) = σ(αₖ + β₁·HEDIS + β₂·CAHPS + β₃·MedAdherence + β₄·Readmission)
```

Four threshold parameters (α₂, α₃, α₄, α₅) define the cumulative splits. The shared coefficient vector β captures each input's effect across all thresholds.

### Converting to Probabilities

Cumulative probabilities are converted to category probabilities:

```
P(Y = 1) = 1 - P(Y ≥ 2)
P(Y = 2) = P(Y ≥ 2) - P(Y ≥ 3)
P(Y = 3) = P(Y ≥ 3) - P(Y ≥ 4)
P(Y = 4) = P(Y ≥ 4) - P(Y ≥ 5)
P(Y = 5) = P(Y ≥ 5)
```

The expected value E[Y] = Σ k·P(Y=k) gives the predicted star rating displayed in the UI.

### Coefficient Design

The synthetic coefficients reflect the directional relationships established in the CMS methodology:

| Input | Weight | Direction | Rationale |
|-------|--------|-----------|-----------|
| HEDIS Composite | +0.08 per pp | Positive | Higher clinical quality → higher stars |
| CAHPS Score | +0.9 per unit | Positive | Better patient experience → higher stars |
| Medication Adherence | +0.06 per pp | Positive | Higher PDC → higher stars (triple-weighted in CMS) |
| Readmission Rate | −0.15 per pp | Negative | Higher readmissions → lower stars (inverse measure) |

The magnitudes are calibrated so that realistic input ranges produce outputs spanning the 1–5 star range, with most combinations falling in the 2.5–4.5 range that reflects real-world plan distribution.

## Limitations and Disclaimers

This demo uses **synthetic weights** that are not trained on actual CMS contract-level data. The model is illustrative:

1. **No real training data.** Actual Star Rating prediction would require contract-level measure scores linked to final ratings, which CMS publishes but which would need proper train/test splitting and cross-validation.

2. **Simplified inputs.** Real Star Ratings incorporate 42 measures across 9 domains. Our 4 inputs are composites representing the most influential categories.

3. **Proportional odds assumption.** We assume the effect of each predictor is constant across all threshold cutpoints. In practice, this assumption should be tested with a Brant test or graphical method (Harrell, 2001).

4. **No case-mix adjustment.** CMS adjusts CAHPS scores and some clinical measures for demographic and health status differences. Our model does not.

Despite these simplifications, the demo accurately represents:
- The correct statistical framework (ordinal logistic regression) for a 1–5 ordered outcome
- The correct direction and relative importance of each input domain
- The probabilistic nature of quality prediction (showing distributions, not just point estimates)

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
