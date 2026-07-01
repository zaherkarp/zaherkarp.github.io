---
title: "Distinguishing a CMS Rulemaking Notice from a Press Release"
description: "A small news-triage tool for Medicare Advantage analysts that turns their fast, intuitive scoring into a handful of named, weighted, explainable features."
publishDate: 2026-05-13
tags: ["medicare-advantage", "stars", "automation", "python", "domain-knowledge"]
---

## The triage problem

A Stars analyst skims about 200 healthcare news items per week. Roughly five of them matter. The question is which five.

"Matter" is not a vague word here. It has a specific meaning that the analyst could articulate if you asked them. A CMS rulemaking notice that changes a measure weight matters. A trade-press article that mentions Medicare Advantage in passing, while really reporting on a hospital system's earnings call, does not matter. A NCQA bulletin about a value-set update matters. A press release from a quality-improvement vendor reframing a CMS announcement as their product launch, also mentions Medicare Advantage, does not matter.

The first time I sat with an analyst doing this triage, the most striking thing was how fast they were. Title and source were enough to dismiss 80% of items in under a second each. The remaining 20% got a five-second skim of the lede. Of those, maybe ten percent got opened, and of those, maybe half ended up shared with the team. The output was five items.

What the analyst was doing is what any domain expert does on a flood of input: applying a learned scoring function, fast, with high recall on the items that matter. The fact that it was fast made it tempting to leave alone. The fact that it was fast also made it a near-perfect candidate for codification, because the scoring function was operating on a small number of features that the analyst could name.

That is the working observation behind the Medicare Advantage Insight Engine. The scoring function already exists, unspoken, in the analyst's head. Building the tool is mostly the work of drawing it out, feature by feature, so it can be written down, weighted, and argued with.

---

## What "matters" decomposes into

The first conversation produced four features. Each one had a name and an honest weight.

**Source authority.** Items from cms.gov rank above items from ncqa.org rank above items from regulations.gov rank above items from trade press, in roughly that order. Items from vendor blogs and PR distribution sites rank below trade press. The ordering is not arbitrary; it reflects how often each source produces an item that the analyst ends up taking action on. The source domain is a single string lookup and contributes more to the score than any other feature.

**Rulemaking stage.** A Notice of Proposed Rulemaking matters more than an advance notice; a final rule matters more than either; a request for information matters less than any of them but more than a press release. This decomposition matters because each stage has a different action implication. A proposed rule is something the analyst's team comments on. A final rule is something the analyst plans against. Comments due by date X is a different calendar item than effective date Y. The triage tool surfaces the stage if it can detect one.

**Measure-set relevance.** The most useful signal is whether the item names a specific measure: PCR, CBP, MCC, HEI, the SUPD adherence triplet. A generic mention of "Star Ratings" is weak. A mention of "the Plan All-Cause Readmissions measure" is strong. The reason is that the analyst's daily work is at the measure level. Items that match the level at which the work happens land harder than items that match the level above it.

**Plan-level versus industry-level framing.** Items framed at the plan level ("CMS revised the threshold for measure X") are higher-yield than items framed at the industry level ("Medicare Advantage faces uncertainty as rulemaking continues"). The first is operational; the second is narrative. Both can be true, but the analyst needs the operational items first and the narrative items as time permits.

These four features are not exhaustive. There are at least four more the analyst could articulate after a few more conversations: recency, the presence of a specific date the item is anchored to, mentions of named CMS personnel that signal authority of the source's reporting, and structural signals like whether the page contains a downloadable PDF or just a paragraph of summary. The tool uses six features in its current form. The point is that each one started as a sentence the analyst could say out loud about what they were doing.

---

## The scoring function

The scoring function is a small Python module that takes an item (title, source URL, body text, publication date) and returns a numeric score plus a feature breakdown for explainability. Sketch of the structure:

```python
def score_item(item: NewsItem) -> ScoredItem:
    features = {
        "source_authority":   source_authority_score(item.url),
        "rulemaking_stage":   rulemaking_stage_score(item.body),
        "measure_relevance":  measure_relevance_score(item.body),
        "framing_level":      framing_level_score(item.title, item.body),
        "structural_signals": structural_signals_score(item.url, item.body),
        "recency":            recency_score(item.published_at),
    }

    score = sum(
        WEIGHTS[name] * value
        for name, value in features.items()
    )

    return ScoredItem(
        item=item,
        score=score,
        features=features,
        passes_threshold=(score >= TRIAGE_THRESHOLD),
    )
```

The weights and the threshold are configuration values, not constants. Both are set empirically against a labeled backlog of items the analyst sorted by hand. The labeling exercise was two hours of one analyst going through a stratified sample of 200 items and marking each one as "share with team," "read for context," or "skip." The exercise was the most expensive part of building the tool and also the most useful, because it forced the scoring function to operate on something more grounded than my own guess at what mattered.

The threshold is set so that the tool's precision on the labeled holdout is high (the analyst rarely sees a flagged item that they would have skipped) and the recall is acceptable (the analyst rarely sees an item shared by a colleague that the tool would have skipped). Precision matters more than recall here. The cost of a false positive is the analyst spending three seconds dismissing a flagged item. The cost of a false negative is the analyst missing an item entirely. But high precision is what gets the tool used at all: an analyst who has been burned by three false positives in a row stops paying attention to the alerts.

---

## A worked example: the true positive

A real item from the calibration set: CMS posted a Notice of Proposed Rulemaking that revised the measure weight for Plan All-Cause Readmissions back upward, after the controversial 2025 weight increase. The URL was on cms.gov. The body contained the phrase "Plan All-Cause Readmissions" four times in the first three paragraphs and "weighted at 3" in the section heading. The page included a PDF download for the full text of the proposed rule. The publication date was within the prior 24 hours.

The scoring function ran. Source authority: high (cms.gov, 1.0 on the source-authority lookup). Rulemaking stage: NPRM detected from the body (0.85 on the stage scale, where final rule would have been 1.0). Measure relevance: high (PCR named explicitly four times, 0.95). Framing level: plan-level (the proposed rule text itself is operational, 1.0). Structural signals: PDF present (0.8). Recency: within 24 hours (1.0).

Weighted sum, with the calibrated weights, well above threshold. The tool posted a structured alert to the Teams channel with a one-line title, the source authority, the matched measure, and a link to the underlying page. The analyst opened the link, skimmed the proposed rule, started a comment-period calendar item, and shared the alert with the comment-drafting team.

That is the case the tool exists for. Five seconds from feed to "this is worth twenty minutes of my time."

---

## A worked example: the near-miss false positive

A vendor press release with the headline "QualityFirst Announces Industry-Leading Stars Compliance Solution Following CMS Plan All-Cause Readmissions Rule Update." The URL was on a PR distribution domain. The body mentioned PCR three times and Medicare Advantage twice. The publication date was within 48 hours of the CMS rule.

The first version of the scoring function flagged this. Measure relevance was high (PCR named). Recency was high. The source authority was low, but the keyword density was high enough to push the total over threshold. The tool surfaced it as a near-tie with the true positive.

The analyst's reaction surfaced the problem: the keyword density was high because the vendor was deliberately mirroring the language of the CMS announcement to ride its visibility. The scoring function had been fooled by exactly the optimization that drives the press-release ecosystem: take the keywords from the authoritative source, restate them in your own marketing copy, distribute widely.

The fix was to raise the source-authority weight and lower the measure-relevance weight, and to add a structural signal. Items whose URL contained PR-distribution-domain patterns ("prnewswire," "businesswire," "globenewswire," et cetera) got a hard reduction in source authority that the keyword density could not fully offset. The fix had to be structural, not threshold-based, because tuning the threshold alone would have suppressed legitimate trade-press items as collateral damage.

After the fix, this item scores below threshold and the legitimate CMS item still scores above. The decision rule that distinguishes them is the source-authority component: cms.gov is higher than prnewswire.com by enough to dominate the keyword density of a well-mirrored press release.

The general lesson is that keyword density is the feature most vulnerable to gaming, because the gamers are optimizing for the same keywords. Structural features (where the page is hosted, what kind of artifact it links to, what the URL path looks like) are less vulnerable because they are harder to fake.

---

## Why this is not an LLM problem

A reasonable reader will ask why this is not a job for a small language model. The answer is not that LLMs do not work; they work fine on this kind of triage. The answer is that the value here was in articulating what the analyst was doing, not in scaling it.

The features the tool scores against are features the analyst names. The weights are weights the analyst can argue with. When the tool gets something wrong, the analyst can read the feature breakdown, see which feature contributed, and decide whether the feature was wrong or the weight was wrong. The fix is a configuration change that can be reviewed, version-controlled, and rolled back.

An LLM-based triage tool can be more accurate. It can also be opaque in ways that the analyst cannot easily debug. The cost of a confused LLM triage classifier is the analyst losing trust in the tool, at which point the tool stops being useful. The cost of a misweighted heuristic is a five-minute conversation about which weight to tune.

There is also a smaller, more boring reason. The scoring function fits in two hundred lines of Python and runs in under a millisecond per item. The infrastructure to run an LLM, even a small one, on each of 200 items per week, is more than this problem requires. Engineering parsimony is a real consideration when the alternative is a half-millisecond latency budget against a workflow that needs sub-second.

This is also not a general-purpose news triage. It is a Stars-analyst-shaped triage. Pointing it at a different domain would require relabeling the calibration set, renaming the features, and reweighting them. The structure carries over; the contents do not. That is true of any heuristic triage built from a domain expert's working knowledge, and treating it as a limitation would miss the point. The strength of the approach is that it is shaped to the actual user. A general-purpose tool would be shaped to nobody in particular and useful to nobody in particular as a result.

---

## Why a webhook, not an email

The output destination matters more than the output format. The original prototype emailed the analyst a daily digest of flagged items. The daily digest was not opened. When it was opened, the items were already three to twenty-four hours stale.

The current version posts to the analyst's Teams channel. That is where the analyst already is. The post is a single line per item: the score-driving feature in plain English ("CMS rulemaking notice, PCR weight change"), the source, the link. No digest. No aggregation. One item per post, in the order they were scored.

This works because Teams is where the conversation about the items happens. The analyst opens an item, decides it matters, replies in-thread with their take, and the rest of the team sees it. The Teams thread becomes the working record of what the analyst chose to attend to, which is the same record the calibration set was built from.

Email triggers triage; webhook triggers reading. That distinction is small but it is the distinction between a tool that the analyst ignores and a tool the analyst uses.

---

## What the experience taught me about building these tools

Two things, both small, that I would carry into the next one.

The labeling exercise was worth ten times what I expected. Two hours of an analyst sorting a stratified sample produced the calibration set, the feature list, the threshold, and the weight ratios. The same exercise produced the language for the alerts (the analyst's own words about why an item mattered, repurposed as the one-line alert text). I would budget more time for labeling and less time for tuning weights, because the labeling is where the model is, and the tuning is only as good as what the labeling captured.

Domain expertise is harder to articulate than it looks. The analyst's confident, fast triage was operating on features they could not initially name. The conversation to draw the features out took multiple sessions and an analyst willing to slow down and explain the obvious. The willingness to slow down is the thing that makes the tool possible. An expert who does not have time to articulate what they know is an expert whose knowledge does not leave their head, which is a perfectly reasonable state of affairs but is also the state of affairs the tool is designed to change.

If the labeling exercise is too expensive to run, the tool will not be useful enough to justify. If the expert will not articulate the features, the tool will be too generic to be useful. Both costs are upstream of the code, which is part of why the code is the easiest part of the work, and the part that takes the least time.
