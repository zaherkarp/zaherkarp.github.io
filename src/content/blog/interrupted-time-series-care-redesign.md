---
title: "Interrupted Time Series for Organization-Wide Change Measurement"
description: "Pre-versus-post comparisons are the wrong tool for evaluating organization-wide care redesign. Interrupted time series is closer to the right one. A retrospective on why, and on what the design can and cannot tell you."
publishDate: 2026-05-02
tags: ["health-services-research", "interrupted-time-series", "methodology", "stata", "care-redesign"]
---

## The question and the wrong answer

A primary care network rolls out a care-delivery redesign across thirty-some clinics. After eighteen months, somebody asks the question that always gets asked: did it work.

The tempting answer is to take the relevant metric, compute its mean in the year before the redesign, compute its mean in the year after, and report the difference. The numbers will exist. They will tell a story. The story will almost always be wrong.

It will be wrong because the metric was already changing before the redesign. Practice patterns drift. Patient mix shifts. Local labor markets do things that affect staffing patterns. National payer policies introduce new measurement frameworks. The metric a year before the redesign is not the counterfactual for the metric a year after. It is, at best, a starting point for asking what the trajectory looked like, and how the redesign perturbed that trajectory.

The pre-versus-post comparison treats the world as if it stood still before the intervention and stood still after, with the intervention as the only event in between. The world does not stand still. The world keeps changing whether you intervene in it or not.

Interrupted time series is the design that takes the prior trajectory seriously. It does not eliminate the inference problem, but it changes its shape. Instead of "was the post-mean higher than the pre-mean," the question becomes "did the trajectory shift at the intervention point in a way that is not explainable by the trajectory's prior trend." That is a harder question. It is also a more honest one.

This post is a retrospective on the methodology side of a multi-year health services research engagement at UW-Madison, where I worked on the analytics for an organization-wide care redesign initiative across a primary care network. The methodological story, the part about why ITS was the right tool and what we learned about how to use it, is the part this post is about.

---

## What ITS does mathematically

The simplest version of an interrupted time series is a segmented regression with three terms. Pick a metric measured at regular intervals, weekly or monthly, over a window that spans both before and after the intervention point. The regression is:

\[Y_t = \beta_0 + \beta_1 \cdot T + \beta_2 \cdot I_t + \beta_3 \cdot (T - T_0) \cdot I_t + \varepsilon_t\]

where \(Y_t\) is the metric at time \(t\), \(T\) is a counter for time itself (1, 2, 3, ... across the observation window), \(I_t\) is an indicator equal to 0 before the intervention and 1 after, and \(T_0\) is the time index at which the intervention occurred. The fourth term, \((T - T_0) \cdot I_t\), is the time counter rebased to start at zero at the intervention and remain zero before it. Each coefficient answers a different question.

\(\beta_1\) is the pre-intervention slope, the rate at which the metric was already changing before anyone did anything. If \(\beta_1\) is non-zero, the metric was drifting. A pre-versus-post mean comparison would attribute that drift to the intervention; the ITS does not.

\(\beta_2\) is the level shift at the intervention point. It is the immediate jump or drop in the metric that coincides with the intervention. If a clinic suddenly does something differently the day the redesign goes live, a level shift captures it.

\(\beta_3\) is the post-intervention slope change. It is the difference between the slope after and the slope before. The total post-intervention slope is \(\beta_1 + \beta_3\). A positive \(\beta_3\) means the metric is now changing faster (in the same direction) than it was before. A negative \(\beta_3\) means it is changing more slowly, or reversing direction.

The intervention effect, taken as a whole, lives in \(\beta_2\) and \(\beta_3\) together. \(\beta_2\) is the immediate effect; \(\beta_3\) is the change in trajectory. Some interventions produce a level shift without a slope change. Some produce a slope change without a level shift. Some produce both. Reporting only one of the two is a common reporting mistake and tends to either understate or overstate what the intervention did, depending on which one you choose.

The pre-intervention slope is the part of the model that most distinguishes the design from a pre-versus-post comparison. A pre-versus-post mean is a model with no pre-intervention slope term: it implicitly assumes \(\beta_1 = 0\), which is almost never true.

---

## The multi-site complication

A single-clinic ITS is the textbook case. The reality of the engagement was a multi-clinic rollout in which the intervention did not arrive everywhere at once. Some clinics went live in the early wave, some in the middle wave, some not until the second year of the rollout. Each clinic had its own time series.

This is a stepped-wedge design embedded in an ITS framework. The implementation order is not random; it was driven by clinic operational readiness, which means clinics that went live first were systematically different from clinics that went live later. Ignoring the staggered rollout produces estimates that confound the intervention effect with the readiness selection.

The way we handled it was to keep each clinic in its own time series, with the intervention indicator and the time counters rebased to the clinic-specific intervention date, and to fit a panel model that pooled the estimates across clinics while including clinic fixed effects. The fixed effects absorb the time-invariant differences between clinics (average panel size, payer mix, building configuration, all the things that make clinic A systematically different from clinic B regardless of whether either has implemented the redesign). The intervention effect is then estimated off the within-clinic variation around the intervention point.

The model in Stata-flavored notation is approximately:

```stata
xtreg outcome time level_shift slope_change ///
    i.month_of_year ///
    , fe vce(cluster clinic_id)
```

where `time`, `level_shift`, and `slope_change` are all clinic-rebased to the clinic-specific intervention date, `i.month_of_year` is a categorical seasonal control, and the variance estimator is clustered at the clinic level. Standard errors clustered at the clinic level are necessary because the within-clinic residuals are correlated, and treating them as independent would understate the standard errors by enough to invent statistical significance that does not exist.

This is the design that addresses staggered rollout. It is not the only valid design. A pure stepped-wedge analysis with a different parameterization would also work. The choice depended on what we wanted the coefficients to mean. The ITS-on-panel parameterization gives interpretable level-shift and slope-change coefficients per clinic, which were the quantities the operational leads wanted to discuss. A pure stepped-wedge would have given a single average treatment effect that would have summarized the rollout in one number but would not have surfaced the heterogeneity across the clinic panels.

---

## Autocorrelation, the part everyone underestimates

Time series residuals are correlated across adjacent time points. This is true even after the regression terms have done their work. A clinic's outcome in week 12 is more like its outcome in week 13 than it is like its outcome in week 30, for reasons that the model's covariates do not capture: the same staff are still working, the same patients are still on panel, the same operational pattern is still in place.

Ignoring autocorrelation produces standard errors that are too small. The intervention effect can look statistically significant when it is not, or look more precise than the data actually supports. The published methodological literature on ITS is consistent on this point: autocorrelation has to be handled explicitly.

For the panel structure described above, the clustered variance estimator handled the within-clinic correlation reasonably well. We checked the residual autocorrelation using a Durbin-Watson statistic per clinic and a serial-correlation test on the panel residuals. The values were not zero, which is the expectation; the question is whether the clustering correction was sufficient, and in this case the magnitudes were small enough that the corrected estimates and the uncorrected estimates told the same substantive story. If they had not, the next step would have been a Prais-Winsten or Newey-West adjustment for the autocorrelation structure.

The general advice that took me a few attempts to internalize: always check the residual autocorrelation. Never report standard errors that have not been corrected for the dependence structure you can see in the data. When the autocorrelation correction changes the substantive interpretation, the correction is right and the uncorrected estimate is wrong. When the correction does not change the interpretation, you have done the work that lets you say so.

---

## What the design surfaced

The intervention produced a measurable level shift on most operational metrics, with mixed slope changes. On the access metric we were most interested in, the level shift was positive at the intervention point and the slope change was modestly negative, which is the pattern of a one-time improvement that does not continue to accumulate. On a different metric tied to documentation patterns, the level shift was effectively zero and the slope change was positive, the pattern of an intervention that takes effect over time rather than instantly. On a third, both were near zero, which is the pattern of an intervention that did not move the metric at all.

The mixed result was the right result. An intervention designed to change clinic operations across multiple dimensions should not produce identical effects across those dimensions. The honest reporting is per-metric, with the levels and slopes named, not a summary indicator that elides the heterogeneity.

What I would emphasize in retrospect is how unusual it is, in the academic and operational literature on care redesign, to see the per-metric heterogeneity reported at all. Many published evaluations either roll up to a single composite outcome (which destroys the per-metric signal) or report many univariate pre-versus-post comparisons (which inflate the false-positive rate while underestimating the within-cluster correlation). The segmented regression with per-clinic fixed effects gave us a defensible framework for reporting both the size and the structure of the effect, with the kinds of confidence intervals the design can actually support.

---

## What the design cannot tell you

It cannot tell you which mechanism produced the change. ITS attributes the change at the intervention point to the intervention, conditional on the prior trajectory and the seasonal terms. It does not attribute the change to any specific component of the intervention. A care redesign has many components: workflow changes, training, staffing reorganization, environmental design changes, payer-policy changes that happened to coincide. The model cannot decompose the level shift into "x% from the workflow changes and y% from the training." For that decomposition you would need a different design, typically a factorial trial that varies the components independently.

It cannot easily distinguish the intervention effect from a contemporaneous secular event. If the intervention rolled out at a time when something else happened nationally, the ITS attributes the level shift at the intervention point to the intervention even if the level shift was caused by the contemporaneous event. The defense against this is having a comparison group: clinics that did not implement the intervention but were subject to the same secular environment. If the comparison group does not show the level shift, the intervention attribution is stronger. If it does, the attribution is weaker.

It cannot rule out anticipation effects. If clinicians knew the intervention was coming and changed their behavior in the weeks immediately before the official intervention date, the pre-intervention slope captures the anticipation, not the prior trend. The model interprets that anticipation as part of the secular trend and underestimates the intervention effect. The fix is to use a longer pre-period, far enough back that the anticipation period is a small fraction of the pre-window. We had a 24-month pre-period for most clinics; the anticipation horizon in this network was on the order of 4 to 8 weeks, which made the bias small.

It cannot help when the metric itself is poorly measured. ITS estimates the trajectory of whatever Y is. If Y is a noisy proxy for the construct you care about, the design tells you a clean story about the proxy and a muddled story about the construct. We spent more time on the metric definitions than on the analytic design, which in retrospect was the right ratio.

---

## When to use ITS, when to use something stronger

ITS is the right answer when randomization is impossible (which is the usual case for operational redesigns where leadership wants to roll out everywhere), when you have a long enough pre-period to characterize the prior trajectory (at least a year of monthly data is a reasonable rule of thumb), and when the intervention has a clearly identifiable start date that all the data agrees on.

If you have matched control clinics that did not implement the intervention, a difference-in-differences design is stronger than a pure ITS. The DiD subtracts out the contemporaneous secular trend that the ITS has to assume away. In practice, finding good matches is hard. We did not have a clean control group for the engagement; the network was rolling out network-wide, and the comparison would have had to come from a different organization. Cross-organization comparisons introduce different selection effects than within-organization staggered rollout, and we judged the trade-off not worth it.

If the intervention components can be varied independently across clinics, a factorial trial or a stepped-wedge with randomized timing is stronger than the staggered-by-readiness rollout we had. This requires leadership willingness to randomize the rollout, which most organizations resist. The willingness to randomize is a research-culture choice, not a methodological one.

If you have no pre-period at all, ITS is not available and you are back to a pre-versus-post or a cross-sectional comparison, both of which produce weaker inference than ITS. The advice in that case is to capture enough pre-period before the next intervention. The cost of capturing twelve months of pre-period data is small. The cost of evaluating an intervention with no pre-period is the inability to attribute observed change.

---

## What I would tell someone running this design today

Start the pre-period earlier than you think you need to. Twelve months is the minimum if you want to characterize the prior trajectory with any confidence. Twenty-four is better. The cost of capturing too much pre-period is small. The cost of running an analysis with not enough pre-period is the inability to estimate the prior slope reliably, which means the intervention effect is confounded with whatever the slope was doing.

Define the metric before the intervention. Not after, when somebody has decided which metric tells the best story. Define the metric, write the SQL, run it on the pre-period, and let the operational team see what the pre-period looks like before anyone implements anything. The discussion of what the metric should be is much better when it happens against actual data than when it happens against a vague idea of what the data might show.

Decide on the model specification before looking at the post-period data. Pre-register the specification with the team, even informally. The temptation to add seasonal terms or change the form of the trend after seeing the result is real and is the most common path by which an ITS analysis drifts into being a story instead of an estimate. The pre-specification does not have to be elaborate. It has to exist.

Cluster the standard errors at the level the intervention varies. For a multi-clinic rollout, that is the clinic. Failing to cluster invents statistical significance that the data does not support. Most ITS papers that get critiqued on methodological grounds get critiqued on this point.

Plan to report the level shift and the slope change separately, not as a single summary number. The intervention's effect is whatever it actually was; sometimes that is a level shift, sometimes a slope change, sometimes both, sometimes neither. The honest report is the per-clinic per-metric breakdown of which is which.

ITS is not the strongest design available. It is often the strongest design available for the specific problem of attributing change to an organization-wide intervention rolled out without randomization. When that is the problem, the discipline of running the design properly, with the pre-period, the staggered-clinic structure, the clustered standard errors, and the autocorrelation check, is most of what separates a credible attribution from a story dressed up in coefficients.
