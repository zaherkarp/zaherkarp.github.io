---
title: "Publicly Available but Practically Unavailable"
description: "Why healthcare executives repeatedly ask for data that technically exists, yet remains inaccessible in usable form—and how misunderstanding 'public data' quietly undermines quality, cost, and governance decisions."
publishDate: 2025-02-01
tags: ["healthcare-data", "quality-measurement", "executive-decision-making", "cms", "public-data"]
---

Healthcare executives ask reasonable questions.

Where are we underperforming compared to peers?  
What will be publicly reported about us before it goes live?  
What is actually driving cost, leakage, and avoidable utilization?

And yet the answer they get, again and again, feels evasive even when it is accurate:

The data exists, but we cannot actually access it in a usable form.

This is not a technical failure. It is a structural one. Most of the most important healthcare quality and performance data is publicly documented, sometimes publicly summarized, but operationally inaccessible to individuals and often even to the organizations being evaluated.

I hear versions of this in nearly every executive conversation. A chief medical officer at a regional integrated delivery network put it bluntly: “We know that data exists, so why can’t we just get it?” A chief analytics officer framed it more sharply: “The data most critical for improving care is the data that is hardest to touch.”

The misunderstanding usually starts with the word “public.”

In healthcare, public almost never means downloadable. It usually means one of three things: the existence of the dataset is public, aggregated results are public, or APIs are documented. What leaders often expect, understandably, is something else entirely: a timely, analyzable dataset that can be used without organizational gates or special eligibility.

To make this gap concrete, it helps to talk about accessibility in tiers.

At the first tier is data that is fully public and directly accessible. Anyone can reach it, usually through a download or an open API. This includes aggregated hospital quality measures, patient experience summaries like HCAHPS, and readmissions or mortality rates published at the hospital or national level. These datasets are useful for high-level benchmarking and communication, but they stop short of management. As one hospital CFO told me, “We can see our star ratings online, but we can’t audit what went into them.”

The second tier is data that is technically public but practically fragmented. It is accessible through APIs, often dozens of them, with inconsistent schemas and shifting joins. Many analytics teams encounter this tier and conclude, not unfairly, that the data is unavailable. A director of data engineering described it this way: “You can get the data, but it’s thirty endpoints, no stable grain, and no clear dictionary. That’s not access in any operational sense.”

The third tier is individual-only access. This is the world of patient-mediated APIs, where a beneficiary can retrieve their own claims or encounters through OAuth and FHIR workflows. This is an important step for consumer empowerment, but it does not solve population-level questions. As one chief quality officer put it, “That helps patients. It tells me nothing about trends my clinicians need to see.”

The fourth tier is where most executive frustration lives: organizationally gated data that is publicly documented but not publicly accessible. This includes Medicare claims at scale, quality reporting preview data, and facility-level surveillance feeds. Access depends on eligibility, contracts, enrollment, and governance workflows. A health system CEO summarized the tension succinctly: “We are accountable for performance, but we only see the final numbers.”

The final tier consists of data that is non-public by design. Raw submissions, audit trails, and corrected records live here. These restrictions are appropriate and necessary, but they are often conflated with the tiers above, adding to confusion about what should be possible.

When you listen across organizations, a clear ranking emerges of what executives ask for most and struggle to obtain.

At the top is Medicare claims for attributed populations. Leaders want to understand leakage, post-acute patterns, avoidable utilization, and total cost of care. Instead, they face eligibility barriers and technical onboarding. A leader of a payer-provider ACO told me, “We’re held responsible for total cost, yet blind to the claims driving it.”

Second is public reporting preview data. Executives want to know what will be published, how it differs from internal numbers, and whether there is time to respond. What they encounter instead are secured portals, UI-first workflows, and limited export options. A vice president of quality improvement described the result: “We find out what the public will see at the same time the public sees it.”

Third are near-real-time quality signals. Leaders want early warnings and course correction. Public data lags by design, and timelier feeds are gated. One chief operating officer summed it up as “managing from a rearview mirror instead of a dashboard.”

Fourth is facility-level safety and surveillance data. Executives want peer context and operational insight. What they get are delayed aggregates without local comparators. As a head of infection prevention noted, “National trends are interesting, but our teams need local context.”

There are legitimate reasons for these barriers. Privacy, program integrity, governance, and the shift from flat files to APIs all matter. But acknowledging those reasons does not eliminate the misalignment. Leaders are expected to manage performance using data that is structurally hard to obtain in usable form.

This is where a truly useful public resource can help. Not by listing datasets, but by translating reality. By naming which tier a dataset lives in. By explaining why access is restricted. By clarifying substitutes and eligibility paths. By setting realistic expectations before engineering time is burned and trust erodes.

When executives say, “I know the data is out there,” they are usually right. When analytics teams say, “I can’t just give you a CSV,” they are also right. The gap between those statements is not technical. It is structural. Making that gap visible, plainly and honestly, is real value.
