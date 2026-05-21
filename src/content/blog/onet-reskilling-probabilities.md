---
title: "Reading O*NET for Reskilling Probabilities: A Worked Example"
description: "O*NET's skill taxonomy is rich enough to support quantitative reskilling guidance, but only if you commit to a probabilistic framing. A categorical 'can this person become an X' answer over-promises; a probability with a clearly-labeled feature set is honest."
publishDate: 2026-05-08
tags: ["workforce", "onet", "logistic-regression", "healthcare", "methodology"]
---

## The reskilling question, stated honestly

Workforce shortages do not reskill themselves. The healthcare labor market in particular has been running on the same demographic math for a decade: aging clinicians, slow pipeline replenishment, demand growth concentrated in roles that take years to credential. The reasonable response is to ask which adjacent roles current staff can move into, with what training investment, and how confident we can be that the move will stick.

The unreasonable version of that question is "can a Medical Assistant become a Registered Nurse." A categorical yes or no over-promises and is wrong in both directions. Some Medical Assistants can. Most cannot do it on the timeline the workforce planner is thinking about. Some can do it but not without a degree program that the local labor market does not have capacity to absorb. The honest version is a probability, conditioned on a feature set the planner can inspect, with the limits of the conditioning spelled out.

This post is a walkthrough of how to use the O*NET occupational taxonomy to estimate that probability. The worked example is Medical Assistant as the source occupation, with five target occupations distributed across three readiness categories. The model is a logistic regression on skill-overlap features, calibrated against published transition patterns from the Bureau of Labor Statistics. The methodology is straightforward; the discipline is in what the model is allowed to say and what it is not.

---

## Why O*NET is the right starting point

O*NET is the Occupational Information Network maintained by the U.S. Department of Labor. It associates each Standard Occupation Classification (SOC) code with a structured description: required skills, knowledge areas, abilities, work activities, work context, and education levels. Each association carries a numeric importance rating and a level rating, both on bounded scales.

For a reskilling model, three properties of this structure matter.

First, the SOC codes are stable. The taxonomy is maintained on a slow update cycle (the major revisions happen roughly every decade), which means an occupation pair you analyzed last year is almost certainly the same pair this year, with the same internal structure. Models built on top of O*NET do not break silently because the source taxonomy shifted.

Second, the skill taxonomy gives you a feature space that survives across occupation pairs. A skill like "Active Listening" is rated for both Medical Assistants (importance 4.0 of 5, level 3.5 of 7) and Registered Nurses (importance 4.5 of 5, level 4.0 of 7). The same feature column applies to every pair. You do not have to invent a new feature space for every comparison.

Third, the importance ratings are real weights, not nominal indicators. When O*NET says an LPN needs "Reading Comprehension" at an importance of 4.4, that is a statement about what the work actually requires. The ratings are derived from incumbent surveys and occupational analyst review. They are not perfect, but they are better than the alternatives a workforce model would otherwise rely on, which are usually job-posting text mining or self-reported job-board taxonomies, neither of which is calibrated against the underlying work.

The decision to anchor the model on O*NET is not an endorsement of O*NET as the final word on occupational structure. It is a recognition that O*NET is the only widely-available, taxonomically-stable, government-maintained source that does the thing the model needs: produce a comparable feature vector for any pair of U.S. occupations.

---

## The model: logistic regression on skill-overlap features

The model is intentionally simple. For each candidate occupation pair (source, target), the feature vector contains:

- The cosine similarity between the source and target skill-importance vectors across all O*NET skill categories.
- The mean gap across "core" skills, defined as those with importance at or above 3.5 in the target occupation. The gap is the target level minus the source level, clipped at zero on the bottom (so a source that already exceeds the target on a skill contributes zero to the mean, not a negative).
- The fraction of the target's core skills for which the source's level is within one standard deviation of the target's mean. This is a coverage metric: how many of the things the target requires the source already plausibly has.
- The education-level difference, encoded as an ordinal step. Stepping from "Some college, no degree" to "Associate's degree" is one step. To "Bachelor's degree" is two. The difference, not the absolute level, is what predicts the time investment.
- The licensure-required indicator on the target side. This is not derived from O*NET directly; it is a hand-maintained lookup for U.S. healthcare occupations, since licensure is a binary structural fact that the skill-overlap features do not capture.

The dependent variable is whether the transition has been observed at non-negligible frequency in BLS labor flow data. We define "non-negligible" deliberately, at a threshold the BLS data can actually distinguish from noise, and we calibrate it to land within reach of the published transition tables. This is the calibration step that turns the model from a similarity score into a probability.

The output is a probability that a worker in the source occupation can complete a transition into the target occupation within a defined timeframe. We use a three-year window because the underlying BLS data is most reliable at that horizon. Shorter horizons are sparser and longer horizons drift into structural retraining (degree completion, midlife career changes) that the skill-overlap features were never going to predict well.

---

## Why categorical readiness bands are not arbitrary

The model produces a continuous probability. The interface produces three bands: Ready Now, Trainable, and Long-Term Reskill. The threshold values are not round numbers. They are the points at which the underlying feature distributions actually break.

Ready Now is the band where the source already meets or exceeds the target's core-skill requirements and no licensure step intervenes. In feature terms, the mean core-skill gap is at or near zero and the education-level difference is zero or negative. The licensure indicator is the gating constraint. A Medical Assistant moving to EHR Specialist falls here, in the worked example below, because the EHR Specialist role's core skill set is a subset of what Medical Assistants demonstrate in practice, and the role does not require a clinical license.

Trainable is the band where the mean gap is meaningful but small and is bridgeable by a defined certification or training program. The threshold is set at the gap level where the BLS data shows transitions actually occurring with a measurable certification investment, typically twelve months or less of formal training. LPN and Phlebotomist sit here for a Medical Assistant. LPN requires a state-approved certificate program; Phlebotomist requires a short certification. Both have skill profiles where the gap is concentrated in specific clinical-procedure areas rather than spread across the full skill space.

Long-Term Reskill is the band where the gap is concentrated in education and the transition path is a degree program. The threshold is set at the education-level difference of two or more steps. Registered Nurse from Medical Assistant is the canonical case: the path is an ADN or BSN program, the timeline is two to four years, and the skill gap is concentrated in clinical assessment, pharmacology, and the procedural skills that the degree program teaches. Health Information Technician is the same shape, with an associate's degree as the gating credential.

The bands are not arbitrary because the underlying distributions are bimodal. Most candidate pairs cluster either at small gaps with no education step (the Ready Now and Trainable regions, which run together at the low end) or at large gaps with a multi-step education path (Long-Term Reskill). The middle of the distribution is sparse. Where the bands cut the continuous probability is approximately where the histogram has its troughs.

This is the part of the methodology that does not generalize to every workforce. It generalizes to the healthcare workforce because U.S. healthcare credentialing is highly structured: the gap between "no license" and "licensed practical nurse" is a discrete step, not a continuous one. In an industry without that structure the bands would have to be redrawn or dropped.

---

## The Medical Assistant worked example

Take a population of 100 hypothetical Medical Assistants and ask the model about five target occupations.

```
Source: Medical Assistant (SOC 31-9092)

Target                              Band           p̂(transition)
----------------------------------- -------------- --------------
EHR Specialist (SOC 29-9021)        Ready Now      0.62
Licensed Practical Nurse (29-2061)  Trainable      0.31
Phlebotomist (31-9097)              Trainable      0.44
Registered Nurse (29-1141)          Long-Term      0.18
Health Information Tech (29-9021)   Long-Term      0.22
```

The Ready Now estimate for EHR Specialist is the strongest individual probability, but it applies to the smallest segment of the source population, the analyst-leaning Medical Assistants whose existing work already touches EHR documentation. Multiply the probability by a realistic share of the source pool that would consider this transition and you arrive at the schematic Medical Assistant transition figure on the homepage: five candidates routed to EHR Specialist, thirty-five to LPN, twenty-five to Phlebotomist, twenty-five to RN, ten to Health Information Technician.

Note what the numbers say and what they do not. The 62% probability for EHR Specialist is not a statement that 62% of all Medical Assistants will become EHR Specialists. It is a statement that, conditional on a Medical Assistant pursuing the transition, 62% complete it within the three-year window the model is calibrated for. The share routed to each target is a separate question, answered by demand, geography, wage trajectory, and the worker's preferences, none of which the model knows.

The 18% probability for Registered Nurse, similarly, is not a statement that nursing is a low-yield reskilling target. It is a statement that on a three-year horizon, conditional on pursuit, the completion rate is low because the path requires a degree program with its own attrition. The same model would give a higher probability on a five- or seven-year horizon. We do not extend it that far because the BLS calibration data thins out and the proportional structure of the feature set begins to break down.

---

## Gap analysis is a feature, not a result

The gap analysis is the part of the methodology that does the most planning work. The mean-gap feature compresses the skill landscape into a single number, which is useful for the regression but not useful for a workforce planner who needs to know which skills are the gap.

We expose the per-skill breakdown alongside the probability. For a Medical Assistant moving toward Licensed Practical Nurse, the gap is concentrated in:

- Medication Administration (importance 4.6 for LPN, 3.2 source baseline)
- Patient Assessment (importance 4.4, 3.3 baseline)
- Documentation in clinical record (importance 4.3, 3.5 baseline)
- Pharmacology knowledge (importance 4.2, 2.8 baseline)

The probability does not change when you look at this breakdown. The training program design does. A program that addresses Pharmacology and Medication Administration explicitly will move more candidates across the threshold than one that addresses them implicitly through clinical rotations alone. The gap analysis is what makes that visible.

The same breakdown for the RN transition shows the same skills, with one additional dimension: the gap on Pharmacology is larger (4.8 importance, 2.8 baseline), and there are skill categories absent from the LPN gap that show up on the RN gap (Critical Thinking at level 5 versus 3.5, Clinical Assessment as a distinct skill). The breakdown is what distinguishes a Trainable target from a Long-Term Reskill target in terms a curriculum designer can work with. The probability is what distinguishes them in terms a workforce planner can budget against.

---

## Why not ordinal regression even though the categories are ordered

The categories are ordered. Ready Now is less reskilling investment than Trainable is less than Long-Term Reskill. The natural temptation is to fit an ordinal model that respects the ordering and produces cumulative probabilities at each cut-point.

We do not, for one reason. The training-investment dimension that defines the ordering is not continuous. It has discrete steps with substantial structural differences between them. The investment to move a candidate from Ready Now to Trainable is the cost of a short certification, on the order of months. The investment to move from Trainable to Long-Term Reskill is the cost of an associate's or bachelor's degree program, on the order of years. The ratio between those two costs is roughly ten to one, but it is not the ratio that matters; the qualitative shape is different. A short certification is a budget item. A degree program is a life decision with attrition risks, financial-aid considerations, and labor-market timing that the budget item does not have.

An ordinal model assumes the cut-points are points on a continuum. The cut-points here are not on a continuum. They mark transitions from one kind of program to a different kind of program. A binary logistic regression per band, with the bands defined by the discrete structure of the underlying labor-market institutions, respects that shape better than a proportional-odds model would.

For a workforce planner this distinction is operationally important. The output of the binary model is "given pursuit of this target, here is the completion probability." The output of an ordinal model would be "given pursuit of any of these targets, here is the cumulative probability of clearing each band," which is the wrong question; nobody pursues all three bands at once.

The ordinal framing would be appropriate if the dependent variable were "highest band attained over a long horizon, given general workforce mobility." That is a different and much harder question, requiring panel data that BLS does not publish at the granularity the model would need.

---

## What the model cannot say

It cannot say whether a given individual will succeed. The model is a population-level estimator. It tells you about the distribution of outcomes for workers in a source occupation pursuing a target. It does not tell you about the candidate sitting across the desk in a workforce-development office. That candidate's outcome depends on factors the model does not see: prior education, motivation, financial stability, geographic mobility, social support, English-language proficiency in regions where the credentialing exam is English-only. A program that uses the model to gate individual placement is using it wrong.

It cannot say whether the local labor market can absorb the trained worker. A 0.6 probability of completion is not the same as a 0.6 probability of employment. The two coincide when the labor market has demand at the credentialed level; they diverge when the credential pipeline is producing more candidates than the local employer base needs. The model is silent on the demand side because O*NET is silent on the demand side. Use BLS occupational projections alongside the model output to answer that question, not in place of it.

It cannot say anything about wage trajectory. A candidate who reskills from Medical Assistant to LPN sees a wage step. A candidate who reskills from Medical Assistant to EHR Specialist sees a smaller wage step in some markets and a step down in others. The model does not weight transitions by wage outcome because the variance in regional wage data is large enough that a national-average wage trajectory would mislead more often than it would inform. The interface labels the target wage at the national median with a regional adjustment factor, and that is the limit of what we are willing to claim.

It cannot say whether the transition will stick. Three-year completion is not five-year retention. A worker who completes an LPN certificate may move on to RN training within two years, may move out of clinical work entirely, may move out of the labor force. The model is calibrated against completion, not retention, because that is the question the BLS data can answer cleanly. Retention would require panel data that follows the same workers across the labor-force lifecycle, which exists in academic research but not in workforce-planning tools.

---

## What this is useful for

Workforce planning at the program level. A federally qualified health center thinking about an LPN-bridging program for its Medical Assistants can use the model to estimate how many candidates the program would need to enroll to graduate a target number, and which skill domains the curriculum needs to address. A state workforce-development agency thinking about which certifications to subsidize can compare the expected reskilling flow under different subsidy structures, knowing that the underlying probabilities are coarse but directionally honest.

It is not useful for individual placement, for wage projection, or for any decision that needs precision the model is not calibrated to deliver. A probabilistic framing is more useful than a categorical one because it forces the user to take the uncertainty into account; the temptation to read "Trainable" as a binary green light is the failure mode the bands were designed to surface, not to enable.

The honest framing of what the model does is the framing that opened the post: which adjacent roles can the workforce move into, with what training investment, and with what probability the move sticks. Three numbers. Each one labeled. Each one with the limits of its conditioning visible to the person reading it. That is the most a reskilling model can do, and it is also enough to make planning decisions that the alternative, planning on intuition, would not make as well.
