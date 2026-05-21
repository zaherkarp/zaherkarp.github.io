---
title: "Compliance as Architecture: A Stars Rating Predictor That Never Sees Member Data"
description: "Treating 'no member-level data leaves the machine' as an architectural premise, not a control bolted on afterward, changed every other design decision in the internal Stars predictor we use at Baltimore Health Analytics."
publishDate: 2026-05-19
tags: ["medicare-advantage", "stars", "compliance", "architecture", "client-side"]
---

## Where the design started

If you build analytic tools inside a health plan, you eventually run into the same review process. You want to look at member-level data. The data has PHI. The compliance team needs to know where it will live, how it will move, who can see it, how long it persists, and what happens to it when the contract ends. That review is not a checkbox. It is a multi-month process involving the privacy office, the security office, sometimes a Business Associate Agreement amendment, and often a legal review of whatever third-party tooling you want to use.

The internal Client-Side Stars Rating Predictor we use at Baltimore Health Analytics started life as a sketch of a forecasting tool. The first design question was: where does the data live. The pragmatic answer was a server-side application with a database, role-based access controls, audit logging, and the usual PHI-handling stack. That answer would have been correct. It would also have taken nine to twelve months to ship.

The eventual design takes a different turn. The model coefficients live in a static JavaScript file. The data lives on the analyst's machine, in their browser, for the duration of the session. When the tab closes, nothing persists. The server never sees member-level data because the server is not in the data path.

This post is about how the constraint reshaped the design. It is not a generalized argument for client-side architectures. It is the narrower claim that some compliance constraints are best treated as architectural premises rather than as a list of controls you bolt on after the fact.

---

## The architectural inversion

A traditional server-side analytic tool inverts the relationship between data and code. The data is at rest in a database; the code travels to the data through queries. The boundary between "inside the system" and "outside the system" is the data center perimeter, the application authentication layer, and the network controls in front of both.

For a Stars rating predictor, the data is a list of measure scores per contract per measure year. The code is an ordinal logistic regression: a coefficient vector and a small set of cut-points. The relative sizes are stark. The data per contract is on the order of megabytes once you have all 42 measures across an enrollment population. The code is on the order of kilobytes.

What if the code travels instead of the data? The model coefficients ship as a static asset. The runtime is the analyst's browser. The data is loaded locally, from a CSV the analyst pulls from the warehouse, and lives only in browser memory. The predictions render in the page. Nothing is sent.

That is the inversion. The boundary between "inside" and "outside" moves. The analyst's machine is now inside the boundary; everything else is outside. The data never crosses a boundary because the only boundary is the local machine.

This is not a clever encoding scheme. It is a different placement of where the analytic work happens.

---

## What the inversion buys you

The first thing it buys you is the absence of an entire compliance review process. The questions a privacy review asks are questions about data movement: where does it go, who has access, how is it transmitted, where is it stored, how is it retained, how is it disposed. If the answer to every question is "the data never moved off the analyst's machine," the questions resolve to "that one does not apply here." Not because you have controls in place, but because the underlying movement does not happen.

This is qualitatively different from a server-side system with strong controls. A server-side system answers the same questions affirmatively: yes, the data moves, here is how we protect it, here is the audit log, here is the retention policy. Those answers are not wrong, but each affirmative answer is a place where the system has to be reviewed, validated, and re-validated on schedule. Each affirmative answer is also a place where things can go wrong. A misconfigured S3 bucket. An expired certificate. A logging pipeline that silently drops events. A retention policy that quietly fails to fire.

The second thing the inversion buys is a different shape of audit trail. The trail for a server-side system is centralized. You log who logged in, what they queried, what was returned. The trail for the client-side tool is intentionally sparse: the analyst opened the page, the page rendered. There is no central log of which member's data was processed, because the central system never knew. Some compliance frameworks consider this a feature; some consider it a gap. The framing depends on whether the threat model is centered on external attack, in which case the absence of a central data store is a smaller target, or on insider misuse, in which case a centralized log is a deterrent and a record.

A third thing: the deployment story is uncomplicated. There is no production database to keep in sync with development. There is no service to monitor. The page is a static asset on a static host. If the model changes, the model file changes. If the page logic changes, the page changes. Releases are file replacements. Rollbacks are file replacements.

---

## What the inversion costs you

The architectural inversion is not free. It rules out several things that server-side systems give you by default.

It rules out shared state. There is no central database, so there is no central record of predictions, no shared cohort definitions, no team-level dashboard. Each analyst's session is independent. If two analysts run the same scenario, they each render their own copy. If you want to compare predictions across analysts, that comparison happens outside the tool, in whatever shared documentation or analytic environment your team uses.

It rules out server-side observability on what runs. You cannot tell, from logs, how often the tool is used or which scenarios analysts are actually running. You can add usage telemetry, but to keep the compliance posture intact that telemetry has to be carefully scoped: aggregate counts, not member-level data. We track that the page was loaded; we do not track which file an analyst opened or what predictions came out.

It rules out elegant model updates. A server-side system can swap in a recalibrated model by updating coefficients in a database; clients fetch the new coefficients on next query. The client-side tool ships coefficients as part of the page. A model update is a page deploy. Versioning matters. Analysts may have cached versions in their browser; cache-busting becomes a concern. None of this is unsolvable, but it is concrete operational work that the inversion does not eliminate.

It puts real performance constraints on the model. The full Stars measure surface has 42 measures across nine domains. Running an ordinal logistic regression against a single contract is fast. Running it against an entire book of business, which at the projection level can be hundreds of contracts when an analyst wants to do scenario sweeps, has to happen in real time on whatever laptop the analyst is using. The tool's responsiveness ceiling is set by the slowest machine in the analyst pool, not by what a server cluster could do.

The pattern is also not a generalized argument that PHI should not move. PHI moves through health plan systems constantly, for very good reasons, and there is a mature compliance infrastructure built around making that movement safe. The client-side architectural inversion is one tool, fit for one shape of problem. The shape it does not fit is anything where the analytic work itself requires cross-organizational aggregation of data that was never centralized in the first place. That is a different problem, with different solutions.

---

## Why the model is ordinal logistic regression, on purpose

The choice of model is load-bearing for the compliance posture as well as for the analytic story.

An ordinal logistic regression with cut-point parameters has a small, transparent set of coefficients per measure. The output is a cumulative probability per star level, from which we recover both the expected rating and the probability of clearing each cut-point. The output is interpretable in the most literal sense: the analyst can read which measures contributed to the projection and by how much.

That interpretability matters in two ways for this design. First, when the model surfaces a cut-point crossing for remediation planning, the analyst needs to be able to explain why. "The probability of clearing 4.0 on contract X is 38% because measure A is 1.2 points below the projected cut-point, measure B is 0.7 points below, and the remaining measures are above" is something an analyst can take into a remediation meeting. "The model predicts 38%" is not. A gradient-boosted ensemble or a small neural network might calibrate slightly better at the margin; neither produces the per-measure contribution decomposition the analyst's conversation actually needs.

Second, the small coefficient vector ships well. The model file is on the order of kilobytes. A black-box model would either need to ship a much larger artifact, which trips browser-cache and load-time concerns, or call out to a server, which defeats the entire architectural posture. The choice of model and the choice of architecture are not independent.

The cut-point projection logic is the thing analysts actually use the tool for. Given the current measure-level inputs and a proposed trajectory for the remainder of the measurement year, the model computes the linear predictor and compares it against the calibration-year cut-points. The projection is the question of where, along that predictor, the contract crosses the next cut-point. The trajectory itself is where most of the analyst's domain judgement enters. The model does not predict trajectories. It converts a trajectory the analyst proposes into a probability of cut-point crossing.

This separation, the analyst supplies the trajectory and the model supplies the conversion, matters for the compliance posture in a way that is easy to miss. The thing that ships is the conversion function. The thing that varies is the trajectory, and the trajectory lives on the analyst's machine alongside the underlying data. Pushing a model update does not require pushing data; pulling new data does not require pushing a model.

---

## What compliance does not get you for free

A common failure mode of "compliance-aware design" is treating the architectural choice as the whole story. It is not. The fact that data never leaves the analyst's machine does not make the tool input-safe. Several things still have to be handled deliberately.

Input validation has to happen on the client. If the analyst loads a malformed file, the tool needs to fail clearly and locally, not silently produce wrong predictions. A server-side tool can validate at the database boundary; the client-side tool has to validate at the file-read boundary. The validation enumerates column names, types, expected ranges, allowable null patterns, and the presence of required measure columns. Failures surface as page-level errors with messages the analyst can act on, not as silent zeros that propagate into the prediction.

Model versioning has to be visible to the analyst. If the tool reports a projection, the analyst needs to know which model version produced it. The page renders the version, the measure year, and the calibration date in a small badge that is always on screen. When the model is updated, the badge updates with the page deploy. The audit story for "what model produced this number" is the badge, not a server log.

The interface is responsible for not displaying member-level data in places it could leak. Browser caches, screen recordings, screen shares with vendors. The tool deliberately renders projections at the contract level, not at the member level, even though the input data is per-member. The analyst can see "contract X has 38% probability of clearing 4.0 stars"; they cannot see "member Y in contract X is below the threshold on measure A." The information could be derived from the input data, but the tool does not surface it. This is a choice about what the tool encourages, not a hard barrier; the input data itself is loaded into the browser memory by definition.

The compliance posture is also fragile to drift. If a future version of the tool adds a "share to team" feature, a "save to cloud" feature, or a "compare against benchmark" feature that requires calling out to a server with member-level data, the posture breaks. The tool's design has to actively defend the inversion as features are added. We have rejected several feature requests on this basis. The decision criterion is whether the feature can be added without crossing the boundary, not whether the feature would be useful.

---

## When the pattern fits

This pattern fits a narrow set of conditions. The data has to be small enough to load locally. The model has to be small enough to ship as a static asset. The user has to be a single analyst, not a team that needs to collaborate inside the tool. The use case has to be exploratory or planning-oriented, not transactional. If the tool needed to update plan-level decisions in a production system, the client-side approach would not work.

For us, those conditions hold. The data is per-contract performance scores from the warehouse, which the analyst already has access to through other tools. The model is a parsimonious ordinal regression that fits in a few kilobytes. The tool is used by a small analytic team for forecasting and remediation planning, not for transactional decisions.

When the conditions do not hold, the architectural inversion does not solve the same problem and forcing it would be a mistake. A team-collaborative dashboard is not a client-side tool. A real-time decision support system embedded in a clinical workflow is not a client-side tool. A model trained on data that genuinely needs to be aggregated across organizations is not a client-side tool.

What the pattern argues, more narrowly, is that you can sometimes redesign the problem so that the riskiest movement does not happen at all. That is a different exercise from designing controls around the movement. It tends to produce smaller, more deployable, and more straightforwardly auditable tools, when it fits. Compliance, framed this way, stops being a checklist that runs after the design is complete and starts being one of the design constraints that shaped the design in the first place.

That reframing is the part of the experience that has carried over into other projects. Not the specific client-side technique, which is narrow, but the prior question: which part of the data movement actually has to happen, and which part is happening because we did not stop to ask.
