---
title: "ROI Modeling from Clinical Workflow Data: A Case Study"
description: "ROI for clinical automation is usually a regression problem disguised as a survey problem. A retrospective on the OCHIN deployment of healthfinch Charlie, what the workflow data could and could not tell us, and the gap between the renewal-conversation metric and the methodologically clean one."
publishDate: 2026-04-26
tags: ["healthfinch", "automation", "linear-regression", "epic-clarity", "case-study"]
---

## The setup

OCHIN runs the EHR for a network of federally qualified health centers across the western U.S. healthfinch Charlie is a prescription-refill automation tool that, at the time, sat inside Epic and processed inbound refill requests through a configurable protocol: route the auto-approvable ones through automatically, escalate the rest to a clinician with the protocol-relevant context attached. When OCHIN deployed Charlie across a subset of its member health centers, the question that came back to the analytics team was the question that comes back about every clinical-workflow tool: did it actually save clinician time, and if so, how much.

The temptation, when the question is "did this save time," is to ask the clinicians. Surveys are cheap and produce numbers fast. The numbers from surveys tend to be either wildly optimistic (clinicians want the tool to work, want to support their colleagues' adoption decisions, want to be helpful in answering) or wildly pessimistic (clinicians had a bad week, the tool failed last Tuesday, the survey landed at the wrong time). Either way, the variance is high and the signal is contaminated with social and emotional factors that the question was not asking about.

The workflow data Epic Clarity captures, by contrast, is unconcerned with how anyone feels about Charlie. It records when a refill request arrived, when it was processed, when it was forwarded to a clinician for review, when it was closed. The timestamps are not perfect, but they are independent of the clinician's after-the-fact recollection of how much time they spent on the encounter. They tell a quieter, more reliable story.

This post is the case-study version of how we used that workflow data to estimate Charlie's effect on clinician time per refill, with linear regression as the analytic spine, and with a deliberate accounting of where the regression's clean estimate diverged from the metric the commercial team needed for renewal conversations.

---

## What the workflow data captured

The Clarity tables we worked from had several timestamps per refill request:

- The arrival timestamp, when the request landed in the in-basket.
- The processing-start timestamp, when somebody (a tech, a nurse, a physician, or Charlie itself) first touched it.
- The processing-end timestamp, when the request was either auto-approved by Charlie, escalated by Charlie to a clinician, manually approved by a clinician, or denied.
- A downstream documentation completion timestamp, when the patient record was updated to reflect the action.
- A series of user-action timestamps in between, indicating which user touched the request at each stage.

Per-refill processing time, the quantity we cared about, is the processing-end minus the processing-start. The other timestamps mattered for separating reliable signal from noise. Documentation completion frequently lagged the processing event by hours or days, sometimes spanning shifts; the gap between processing-end and documentation-end was not "clinician time on the refill" but "the operational lag between completing the work and updating the chart." Confusing the two would have overstated Charlie's effect by counting documentation lag as clinician time.

The unreliable parts of the data were also identifiable, and that identification was itself part of the analysis.

In-basket arrival timestamps were reliable, generally. The exception was a small fraction of requests that arrived through a fax-to-EHR pipeline that batched overnight; for those requests, the arrival timestamp reflected the batch-processing time, not the real-world receipt time. We filtered those out by source channel. They were too small a fraction of the overall volume to materially affect the estimates, and including them would have introduced a known bias.

Processing-start timestamps were less reliable in clinics where requests were sometimes touched briefly (a glance, a re-routing, a "leave for later") and then re-touched substantively later. The Clarity system recorded the first touch, not the substantive one. We addressed this by collapsing same-user same-day touches into a single processing event, defined by the start of the first touch and the end of the last touch. This conflated brief touches with sustained ones, which was the lesser of two evils given the alternatives.

User-action timestamps were reliable when populated and were sometimes not populated. The not-populated case appeared in older Clarity records and was a known data-completeness issue. We worked from the post-2014 records exclusively, where the population rate was above 95%.

The reliable/noisy distinction is the part of the work that does not appear in the published case study but is the most important part of the analyst's job on engagements like this. The regression's quality depends on the inputs more than on the regression's specification. If the inputs are wrong, fitting a more elaborate model on top of them does not recover the missing signal.

---

## The regression

The model is a linear regression on per-request processing time. The specification:

\[\text{time}_i = \beta_0 + \beta_1 \cdot \text{Charlie}_i + \beta_2 \cdot \text{complexity}_i + \gamma_{c(i)} + \delta_{m(i)} + \varepsilon_i\]

where \(\text{time}_i\) is the per-refill processing time for request \(i\) in minutes, \(\text{Charlie}_i\) is an indicator for whether Charlie was processing requests at this clinic at the time of the request, \(\text{complexity}_i\) is the request-complexity covariate (more on which below), \(\gamma_{c(i)}\) is a clinic fixed effect, \(\delta_{m(i)}\) is a month fixed effect for seasonality, and \(\varepsilon_i\) is the error term.

\(\beta_1\) is the quantity of interest: the average change in per-request processing time attributable to Charlie's presence, controlling for complexity and for time-invariant clinic differences.

A few things to note about the specification.

The dependent variable is the natural log of processing time in some published variants of this analysis, to handle the right-skewed distribution of processing times and to interpret the coefficient as a proportional change. We tested both specifications. The substantive conclusions did not differ; the log specification produced tidier residuals. The published version used the log specification for that reason; the natural-units version stayed in the appendix because the renewal-conversation audience preferred minutes to log-minutes.

Standard errors were clustered at the clinic level, for the same reasons described in the ITS post: residuals within a clinic are correlated, and treating them as independent invents precision the data does not support.

Clinic fixed effects rather than random effects, on the principle that we had no reason to assume the clinic-level deviations were uncorrelated with the regressors. Random effects would have been more efficient if the assumption held; fixed effects are safer when it does not, and the cost is small at the sample sizes we were working with.

The seasonal term was per-month rather than a continuous time trend, because the seasonality in refill volume was non-monotonic (a spike in January when prescriptions renewed for the new plan year, smaller spikes around school start, an August dip), and a smooth trend would have absorbed the pre-Charlie post-Charlie variation in ways that would have biased the estimate.

---

## The complexity covariate is doing the load-bearing work

The complexity covariate is the part of the model that, if mis-specified, breaks the whole estimate. Charlie auto-approves the easy refills and escalates the hard ones. If complexity is not in the model, the comparison between Charlie-on and Charlie-off conflates "Charlie made the easy ones faster" with "Charlie made everything faster." The two are different. The first is real; the second is not.

The complexity score was constructed from request features that did not depend on Charlie's processing:

- The number of medications on the refill request.
- The presence of controlled substances.
- The presence of medications requiring lab monitoring or prior authorization.
- The patient's chronic-disease count (from problem-list data).
- The interval since the most recent in-person visit.
- The clinical role of the originally-routed clinician.

These features were combined into a complexity score using a separate logistic regression trained on Clarity data from before Charlie's deployment, with "request escalated to physician review" as the dependent variable. The fitted score is the model's estimate of the probability of escalation under pre-Charlie conditions, used as a proxy for clinical complexity.

The construction has the property that the complexity score is determined by the request, not by the system that processed it. A high-complexity request is high-complexity whether Charlie or a clinician handled it. This is the property the regression needs to make the comparison meaningful.

The construction also has the property of being entirely defensible. Every feature in the complexity model is a feature the clinical team agrees corresponds to complexity. The weights are calibrated against pre-Charlie escalation patterns, which means the score reflects the clinic's own historical sense of which requests are hard. This was important because the analysis had to survive scrutiny from clinical leadership; a complexity score that the clinical team did not recognize as complexity would have been rejected, regardless of its statistical properties.

If I were running the analysis again with current tools, I would build the complexity model the same way. The temptation would be to use a gradient-boosted ensemble for slightly better calibration, and that would be a mistake for the same reason it was a mistake in the Stars predictor: when clinical leadership needs to interpret the model's behavior on a contested request, the linear-logistic structure carries the conversation and the boosted ensemble does not.

---

## Why linear regression and not survival analysis

A reasonable methodological reader will ask why we did not use survival analysis. The dependent variable is time-to-event (processing-end minus processing-start), which is exactly the variable survival models are designed for.

The answer is that the events were not censored. Every request in the analytic sample had a completed processing event within the observation window. Survival analysis is the right tool when some observations have not yet reached the event by the end of follow-up, and you have to model the right-tail of the time distribution under censoring. When all events are observed, survival analysis reduces to a regression on observed times, with extra machinery that does not buy precision.

We could have used a survival model for theoretical tidiness. We did not, because the model would have had no censoring to handle, and the linear-regression-on-log-time specification is more compact, more interpretable, and produces estimates that converged faster against the cluster-robust variance estimator.

If the dataset had included open requests that had not yet been processed by the end of the observation window, the answer would have been different. We chose the window so that this case did not arise: the analytic window closed at a date sufficiently before our analysis date that all requests in the window had been processed.

This is a small methodological choice that has more general implications. The right tool for a problem is often the one the data structure actually requires, not the one a textbook chapter title suggests. A heavily right-censored time-to-event dataset is a survival problem. A fully-observed processing-time dataset is a regression problem. They are not interchangeable, and choosing between them is an act of judgement about the data, not about the canonical method.

---

## The two metrics

The model produced an estimate of \(\beta_1\) in log-minutes, which translates to an average proportional reduction in per-request processing time. The point estimate was sizable, in the range expected from the operational team's prior intuition about the tool's effect, with a confidence interval that excluded zero by a substantial margin.

That was the methodologically clean metric. The renewal-conversation metric was different.

For renewal conversations, the commercial team needed time saved per refill, in minutes, multiplied by refill volume per FTE-hour, to produce a dollar value of clinician time recovered. The product of those numbers is what the health center's CFO wanted to see. The clean methodological estimate was an input to that calculation, but it was not the calculation.

There were two places the gap opened up between the clean metric and the renewal metric.

The first was the assumption about what clinician time was worth. The clinical team's hourly cost is not a single number; it is a function of role mix (MD, NP, RN, MA), of regional wage levels, of benefit overhead, of the way the health center accounted for clinician time. The renewal metric had to pick an hourly cost figure, multiply through, and produce a single dollar number. Any single number embedded an assumption that varied across the clinics we were reporting to. The methodologically clean way to handle this is to publish the time savings and let each health center apply its own cost figure. The renewal-conversation way to handle this is to pick a number that is defensible across the average and own the assumption.

The second was the question of fixed versus variable clinical capacity. If Charlie saves twelve minutes per clinician per day, and the clinician's day is not made shorter as a result, is that twelve minutes recovered? The methodological answer is yes, with the caveat that the recovered time is redirected to other work and the value of that other work is the operational variable that determines the dollar return. The renewal-conversation answer is also yes, with the same caveat largely suppressed because the renewal conversation needs a number. The gap between the two answers is small in the cases where the redirected work is clearly higher-value (more patient visits, more clinical documentation, fewer overtime hours); the gap is larger in the cases where the redirected work is administrative slack that does not produce identifiable downstream value.

I am not arguing the renewal metric was wrong. I am arguing that the gap between it and the methodologically clean metric was real, and the responsible thing was to report both and to be explicit about the assumptions that converted one into the other.

---

## What the case study fed

The model output became the methodological backbone of the published case study, which the commercial team used in renewal conversations and new-customer pitches. The published version emphasized the time-saved-per-refill and refills-per-FTE-hour numbers, with the methodologically cleaner log-minutes specification in the appendix.

Internally, the model also surfaced something the commercial team found useful: the heterogeneity across clinics. Charlie's effect was larger at clinics with higher-complexity request mixes (more complex patients, more controlled substances, more lab-monitored medications) and smaller at clinics with simpler mixes. The interpretation, which I find still defensible, is that Charlie's auto-approval logic captures most of the easy requests in any environment; the marginal time savings come from the harder requests where the protocol-relevant context attachment is most useful to the escalating clinician. At a simple-mix clinic, fewer requests fall into that category; at a complex-mix clinic, more do.

This heterogeneity was the part of the analysis I would emphasize most in retrospect. The commercial team's pitch was naturally about "Charlie saves time," with a single number for the magnitude. The honest story was "Charlie saves time, more so when the mix is harder, and the implementation pays off fastest at clinics whose mix already runs complex." That second story is harder to fit on a slide. It is also more useful to a health-center CFO trying to decide whether their clinic resembles the ones in the case study or differs from them.

---

## Lessons for the next ROI study

A short list of operational habits that survived from this engagement into later ones.

Capture timestamps from day one. The hardest data-engineering problem in any retrospective ROI analysis is the timestamps that were not captured during the pre-period because nobody knew they would be needed. If you are deploying anything that you might want to evaluate in twelve months, instrument the in-basket fully, the user-action timestamps fully, and the documentation lags fully, before the deployment. The marginal cost is small; the marginal value of having the data when the evaluation question comes is large.

Define complexity before the deployment. The complexity score in the Charlie analysis worked because we could train it on pre-deployment data. If we had had to construct it after the deployment, we would have had to use Charlie's own processing patterns to define complexity, which would have circularized the comparison. Constructing a complexity model on pre-period data is cheap if you do it early; it is expensive if you do it late.

Save the pre-period. The single biggest determinant of the analysis's credibility was the length of the pre-Charlie observation window. We had over a year of pre-deployment workflow data on most of the clinics in the sample. If the pre-period had been three months, the seasonal terms would have been unidentified and the complexity score would have been poorly calibrated, and the analysis would have been a story rather than an estimate. Pre-period data is the foundation of the entire design.

Report the methodologically clean metric and the renewal-conversation metric, and own the gap. The commercial team did not have a vocabulary for that distinction at the start. Building the vocabulary, with the team, was part of the work, and the conversations were the kind of internal handoff that determines whether the analysis lives past the deployment. The temptation to report only one metric (either the clean one, which the commercial team cannot use, or the renewal one, which methodologists will critique) is the temptation to ship something less useful than the analysis actually produced.

ROI from clinical workflow data is a regression problem. It is also a stakeholder-communication problem and a data-completeness problem. The regression is the smallest part. That is the case-study-shaped version of what I would tell anyone planning the next one.
