---
title: "Why CMS Never Let STAR Ratings Touch Meaningful Use"
description: "On the surface, it looks like an omission - but CMS understood that capability and outcomes cannot be governed the same way, even when one enables the other. The deliberate separation was probably the right call."
publishDate: 2025-12-21
draft: true
tags: ["healthcare", "policy", "cms", "meaningful-use", "star-ratings", "ehr"]
---

# Why CMS Never Let STAR Ratings Touch Meaningful Use
*(and why that was probably the right call)*

On the surface, it looks like an omission.

CMS spent years pushing clinicians and hospitals to adopt electronic health records through the Meaningful Use program, while at the same time rewarding Medicare Advantage plans based on outcomes through STAR Ratings. One program focused on technology adoption and workflow compliance. The other focused on whether patients actually received high-quality care.

If the goal was better care, better outcomes, and better accountability, why were these two programs never connected?

The short answer is that CMS understood something that still frustrates analysts today: capability and outcomes cannot be governed the same way, even when one enables the other. Trying to fuse STAR Ratings into Meaningful Use would have created a program that was theoretically elegant and operationally unworkable.

## The temptation to merge capability and outcomes

From a data and engineering perspective, the idea is seductive. Meaningful Use measured whether organizations could capture data, exchange it, and use it in structured ways. STAR Ratings measured whether that care translated into better outcomes, adherence, access, and patient experience.

Put them together and you get a clean story: prove you are using modern tools, then prove those tools are producing results.

That logic makes sense in a whiteboard session. It breaks down the moment you try to operationalize it.

## A counterfactual: Meaningful Use with STAR gates

To imagine how this might have worked, CMS would have had to add some form of STAR-linked requirement to Meaningful Use attestation. There are only a few plausible ways they could have done that.

One option would have been plan-level attribution: a clinician or hospital's Meaningful Use performance would depend, in part, on the STAR performance of the Medicare Advantage plans they served.

Another option would have been provider-level STAR proxies: recreating STAR-like measures at the clinician or hospital level using claims, EHR data, and partial CAHPS analogs.

A third option would have been network-level scoring, where Meaningful Use credit depended on the performance of an ACO, IPA, or delegated entity.

All three approaches fail for the same core reasons.

## Where the design collapses

First, attribution. Meaningful Use was designed around entities with direct operational control: a clinician, a practice, or a hospital. STAR Ratings are assigned to MA contracts. Providers influence STAR outcomes, but they do not control benefit design, pharmacy networks, outreach operations, enrollment churn, or call center performance. Holding a provider accountable for those outcomes under a compliance program would have guaranteed disputes and appeals.

Second, timing. Meaningful Use operated on short, auditable reporting windows. STAR performance is lagged, multi-year, and subject to annual methodological changes. A compliance program where organizations discover failure after incentives are already locked in is not enforceable at scale.

Third, data provenance. Meaningful Use relied on EHR-auditable actions. STAR relies on claims, enrollment, survey vendors, and plan operations. There is no single system of record. CMS would have had to adjudicate endless disagreements about whose data was correct and which entity was responsible for gaps.

Fourth, equity and access. STAR measures are sensitive to social risk, access barriers, and patient behavior. Without sophisticated adjustment, tying them to Meaningful Use penalties would have disproportionately harmed providers serving higher-need populations. With adjustment, the program becomes too complex to audit cleanly.

Finally, perverse incentives. If Meaningful Use depended on outcome performance, organizations would rationally optimize for the narrowest interpretation of those outcomes. Avoid hard-to-reach patients, reshape denominators, and prioritize documentation over care. The original goal of accelerating adoption would have stalled.

## Why CMS chose sequencing instead

Rather than merging programs, CMS sequenced them.

First, get EHRs adopted.
Then, standardize workflows.
Then, enable interoperability.
Then, apply outcome accountability through separate programs.

That sequencing gave CMS faster adoption, clearer compliance rules, and fewer legal and operational failures. It also created fragmentation and analytic debt, but it kept the system moving.

The absence of STAR Ratings from Meaningful Use wasn't an oversight. It was a tradeoff.

## What we gained and what we lost

We gained rapid EHR adoption and a compliance framework that organizations could realistically meet. We lost a clean narrative connecting technology investment directly to patient outcomes.

That gap still frustrates analysts and policymakers. But it is the price CMS paid to get the infrastructure built at all.
