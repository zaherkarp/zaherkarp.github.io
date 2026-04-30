---
title: "The Inversion: When Developer Infrastructure Breaks Under Its Own Momentum"
description: "Stack Overflow visits collapsed while GitHub commits surged, and the platform underneath both is degrading in real time. The productivity gains from AI coding agents are real. So is the load they put on infrastructure that wasn't designed for them."
publishDate: 2026-04-28
tags: ["infrastructure", "ai-agents", "github", "developer-tools", "reliability"]
---

## TL;DR

- **The inversion:** Stack Overflow monthly visits collapsed from 110M to 25M between 2019 and 2026. GitHub commit volume rose from 800M to roughly a billion per month over the same period. Pull-request opens are growing 23% YoY.
- **The twist:** GitHub's own platform reliability went the wrong way at the same time. Third-party trackers put 90-day rolling uptime at 90.21%. February 2026 alone logged 37 distinct incidents, against a 2019 baseline of 1 to 4 per month.
- **The diagnosis:** GitHub was not architected for a world where millions of AI coding agents trivially generate huge volumes of commits, PRs, and Actions runs. The factory got faster. The factory floor did not.

---

A claim that sounds too neat, but holds up: the place where developers used to ask each other questions emptied out, the place where developers push code filled up, and the place where they push code is now down more often than at any point in the last seven years. Three trends, one system, and the irony lives in the third.

The chart below is the centerpiece. Four small panels, one figure, same x-axis on all of them: 2019 to 2026.

<figure>
<svg viewBox="0 0 720 460" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Four-panel chart from 2019 to 2026: Stack Overflow visits collapsing from 110 million to 25 million per month; GitHub commits rising from 800 million to roughly a billion per month; GitHub pull-request year-over-year growth climbing from 12 percent to 23 percent; GitHub uptime degrading from 99.8 percent to 90.2 percent." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="20" y="18" font-size="9" letter-spacing="1.4" fill="#6a6a6a">STACK OVERFLOW VISITS — MILLIONS / MONTH</text>
  <line x1="70" y1="60" x2="70" y2="200" stroke="#d0d0c8" stroke-width="0.6"/>
  <line x1="70" y1="200" x2="320" y2="200" stroke="#d0d0c8" stroke-width="0.6"/>
  <text x="64" y="64" text-anchor="end" font-size="8" fill="#6a6a6a">120</text>
  <text x="64" y="203" text-anchor="end" font-size="8" fill="#6a6a6a">0</text>
  <polyline fill="none" stroke="#6a6a6a" stroke-width="1.2" points="70,72 106,78 141,89 177,107 213,124 249,142 284,159 320,171"/>
  <circle cx="70" cy="72" r="2" fill="#6a6a6a"/>
  <circle cx="320" cy="171" r="3" fill="#7a0000"/>
  <text x="64" y="74" text-anchor="end" font-size="9" fill="#6a6a6a">110M</text>
  <text x="326" y="174" font-size="9" fill="#7a0000">25M</text>
  <text x="70" y="215" font-size="8" fill="#6a6a6a">2019</text>
  <text x="320" y="215" text-anchor="end" font-size="8" fill="#6a6a6a">2026</text>
  <text x="380" y="18" font-size="9" letter-spacing="1.4" fill="#6a6a6a">GITHUB COMMITS — MILLIONS / MONTH</text>
  <line x1="430" y1="60" x2="430" y2="200" stroke="#d0d0c8" stroke-width="0.6"/>
  <line x1="430" y1="200" x2="680" y2="200" stroke="#d0d0c8" stroke-width="0.6"/>
  <text x="424" y="64" text-anchor="end" font-size="8" fill="#6a6a6a">1050</text>
  <text x="424" y="203" text-anchor="end" font-size="8" fill="#6a6a6a">750</text>
  <polyline fill="none" stroke="#6a6a6a" stroke-width="1.2" points="430,177 466,167 501,153 537,139 573,125 608,111 644,93 680,83"/>
  <circle cx="430" cy="177" r="2" fill="#6a6a6a"/>
  <circle cx="680" cy="83" r="2" fill="#6a6a6a"/>
  <text x="424" y="180" text-anchor="end" font-size="9" fill="#6a6a6a">800M</text>
  <text x="686" y="86" font-size="9" fill="#6a6a6a">~1B</text>
  <text x="430" y="215" font-size="8" fill="#6a6a6a">2019</text>
  <text x="680" y="215" text-anchor="end" font-size="8" fill="#6a6a6a">2026</text>
  <text x="20" y="238" font-size="9" letter-spacing="1.4" fill="#6a6a6a">GITHUB PULL REQUESTS — YoY GROWTH, %</text>
  <line x1="70" y1="280" x2="70" y2="420" stroke="#d0d0c8" stroke-width="0.6"/>
  <line x1="70" y1="420" x2="320" y2="420" stroke="#d0d0c8" stroke-width="0.6"/>
  <text x="64" y="284" text-anchor="end" font-size="8" fill="#6a6a6a">25</text>
  <text x="64" y="423" text-anchor="end" font-size="8" fill="#6a6a6a">0</text>
  <polyline fill="none" stroke="#6a6a6a" stroke-width="1.2" points="70,353 106,342 141,347 177,358 213,336 249,314 284,302 320,291"/>
  <circle cx="70" cy="353" r="2" fill="#6a6a6a"/>
  <circle cx="320" cy="291" r="2" fill="#6a6a6a"/>
  <text x="64" y="356" text-anchor="end" font-size="9" fill="#6a6a6a">12%</text>
  <text x="326" y="294" font-size="9" fill="#6a6a6a">23%</text>
  <text x="70" y="435" font-size="8" fill="#6a6a6a">2019</text>
  <text x="320" y="435" text-anchor="end" font-size="8" fill="#6a6a6a">2026</text>
  <text x="380" y="238" font-size="9" letter-spacing="1.4" fill="#6a6a6a">GITHUB UPTIME — %, 90-DAY ROLLING</text>
  <line x1="430" y1="280" x2="430" y2="420" stroke="#d0d0c8" stroke-width="0.6"/>
  <line x1="430" y1="420" x2="680" y2="420" stroke="#d0d0c8" stroke-width="0.6"/>
  <text x="424" y="284" text-anchor="end" font-size="8" fill="#6a6a6a">100</text>
  <text x="424" y="423" text-anchor="end" font-size="8" fill="#6a6a6a">88</text>
  <polyline fill="none" stroke="#6a6a6a" stroke-width="1.2" points="430,282 466,282 501,284 537,285 573,286 608,292 644,321 680,394"/>
  <circle cx="430" cy="282" r="2" fill="#6a6a6a"/>
  <circle cx="680" cy="394" r="3" fill="#7a0000"/>
  <text x="424" y="285" text-anchor="end" font-size="9" fill="#6a6a6a">99.8</text>
  <text x="686" y="397" font-size="9" fill="#7a0000">90.2</text>
  <text x="430" y="435" font-size="8" fill="#6a6a6a">2019</text>
  <text x="680" y="435" text-anchor="end" font-size="8" fill="#6a6a6a">2026</text>
</svg>
<figcaption>Four trends, one system. Stack Overflow visits sourced from public Similarweb summaries; GitHub commit and PR volumes from GitHub's published platform statistics; uptime from a third-party status aggregator's 90-day rolling window. Endpoints rounded.</figcaption>
</figure>

The eye wants to read it as a 2-by-2 narrative. Top row is the inversion most people already know about: question-asking traffic moved off Stack Overflow and code-pushing traffic kept climbing on GitHub. Bottom row is what doesn't get talked about as much: PR creation is still accelerating, and the platform that hosts all of it is having its worst reliability stretch in years.

## Part 1: The Data Story (with the Irony)

### The inversion most people stop at

Stack Overflow's traffic chart is now famous. From a peak around 110 million visits per month in 2019, it slid to roughly 25 million by early 2026. The decline was gradual through 2020 and 2021, then bent sharply downward in late 2022, which is the same window where general-purpose code-generating chat assistants entered everyday workflows. The functional substitution was clean. Asking a question on a public forum and waiting for a human answer is a slow-feedback loop. Asking a model for a working snippet is a fast-feedback loop. Where both options work, the fast one wins.

The mirror trend on GitHub is the other half of the story. Monthly commit volume rose from about 800 million to a number GitHub itself now rounds to "roughly a billion." Pull-request opens kept their YoY growth rate above 20% for two years running, and ended at 23% YoY. The composition matters: a meaningful share of new PRs are agent-authored, opened against repos by tools running under user credentials, then either merged after lightweight review or abandoned as throwaway scratch work. The signal is strong, but it doesn't separate "human shipped code" from "agent shipped code" cleanly. From the platform's perspective, both look like writes.

### The third dimension nobody asked for

Here is where the chart earns its keep. The bottom-right panel is the trend that complicates the rest.

GitHub's own platform reliability moved the wrong way over the same window. Third-party uptime trackers put 90-day rolling availability at 90.21%, which is one nine. Not three. February 2026 alone logged 37 distinct incidents on GitHub's status page, against a baseline closer to 1 to 4 per month in 2019. The cluster wasn't a single bad week. It was a steady drip of degraded states across Copilot, Actions, and core Git operations, with several windows where users could not reliably push, pull, or run workflows.

The plain-language reading of the chart: the harder developers leaned on GitHub, the less reliably it answered the phone.

### Why this is the irony, not just bad luck

The mechanism is not mysterious. GitHub's architecture predates the era it is now serving. It was built for human-paced contribution. Branch protection, status checks, Actions runners, even the database that stores PR metadata, all of it was sized against a workload where commit rates rose maybe 10% a year and a single PR represented a coherent unit of human attention. The current load looks different. A single agent harness can open hundreds of PRs against itself in a day. The often-cited example is the openclaw repository, which by itself is responsible for around 700,000 Actions runs. That is not a typo. One repository accounts for a workload that would have been a sizable fraction of all of GitHub Actions a few years ago.

Layered on top of that, GitHub's ongoing infrastructure migration to Azure happened to coincide with the demand surge. The migration itself is sound engineering. The timing collided with a load curve nobody priced in. The result is the panel on the bottom right.

## Part 2: Practical Ramifications

### The speed trap

For a working engineer, the lived experience of the chart is a paradox. Velocity feels higher than it has ever been. The wait for an answer is gone. The wait for a generated diff is measured in seconds. Refactors that would have been a Friday afternoon are now a coffee break. And yet the foundation under that velocity is, on a measurable axis, less reliable than it has been at any point in recent memory.

The danger is not that any single incident is catastrophic. Any individual GitHub incident is recoverable. The danger is that the new tempo has compressed the buffer between commit and merge. When a team's median PR-to-merge time is under an hour, an Actions outage that lasts ninety minutes is no longer an annoyance. It is a stop-the-line event for the whole team's day.

### Cascading failures

The February 2026 cluster is the cleanest case study. Inside a single rolling window, Copilot completions, Actions workflows, and core Git operations all degraded. Users could not reliably push, pull, or run CI. Each subsystem has its own runbook and its own on-call. From the user's seat that distinction is invisible. Either the platform works or it doesn't, and during the worst stretches it didn't.

The cascading shape matters because of how AI-generated work distributes load. When every engineer effectively has an agent attached, they generate 5x to 6x the commit and PR volume they used to. A platform incident that would have idled one engineer's day in 2019 now idles that engineer plus their agent's queued work plus the dependent CI fan-out. The blast radius scales with the multiplier.

### Reliability as the new bottleneck

The traditional bottleneck on a developer's day was knowledge discovery. Stack Overflow existed because that bottleneck was real. The unfamiliar error message, the obscure flag, the right way to bind a parameter, all of it lived in the tail of a search index that someone, somewhere, had answered. The decline of that index is not the loss of a tool. It is the loss of a category of friction that already got solved by something faster.

The new bottleneck is platform availability. It is not the constraint people optimized their workflow around, because for most of GitHub's history it didn't need to be. Three nines was background. One nine is foreground. Teams I talk to are building habits they didn't have a year ago: bundling small commits into larger ones to reduce CI exposure, mirroring critical workflows to a second provider, writing pre-commit checks that are robust to a Git server returning a transient error.

None of those habits are technically new. They are ops hygiene from an older era reasserting itself in a context that thought it had moved past them.

## Part 3: Philosophical Consequences

### The Faustian bargain

Every productivity transition ships with a hidden bill. The bill on this one is starting to come due.

The "how do I find an answer" problem is, for most working tasks, solved. The price was that the solution centralized. Stack Overflow distributed its knowledge across hundreds of thousands of contributors, each of whom got a reputation, some of whom argued, occasionally with heat, about whether a given answer was actually correct. That argument was a feature. It was the place where claims got tested and tightened in public.

What replaced it does not have that property. A model answer is not contested. It is not visible to other readers. It is not corrected by a peer in the comments. The expertise that used to live in the dialogue now lives in the weights, which is to say it lives in a private artifact owned by a vendor and surfaced through an interface that does not invite disagreement. That is a real shift, and it is not symmetric.

### Distributed knowledge versus centralized generation

Stack Overflow, at its peak, was distributed human knowledge. The set of people who could answer a Postgres question included you, me, the original author of the relevant patch, a self-taught hobbyist in Lagos, and a Microsoft engineer who happened to be procrastinating that afternoon. The medium did not care which of us answered. The vote count cared.

GitHub at scale, with agents at scale, is something different. It is the place where centralized machine generation gets enacted. When the generator is a model and the substrate is a single platform, the failure mode of either one is no longer redundant against the other. The forum used to be a fallback for the codebase. The codebase is, in a real sense, no longer a fallback for anything.

This is the structural reason the bottom-right panel is more than a curiosity. When generation centralized and the platform centralized in the same window, there isn't a graceful degradation path. There's the platform, or there isn't.

### The tragedy of scale

The productivity gains here are real. I want to be clear about that. I have written more working code in the last twelve months than in any twelve-month stretch of my career, and I am not unusual. The teams I work with are shipping more, faster, with smaller groups. None of that is fictional.

What is also real is that the load patterns those gains create exceed the engineering capacity of the platforms they run on. Building infrastructure to absorb a 5x or 6x volume increase in three years is not a vendor failing. It is a category of demand growth that ops capacity simply cannot match in real time. We are driving faster. The roads have not gotten better. In some places they are visibly worse.

### Authority and failure

Stack Overflow's decline meant losing a public space where expertise was visible, debated, and occasionally wrong in instructive ways. GitHub's reliability slide means losing trust in the place where expertise is now enacted. Those are two different losses, and they compound.

The first loss is partly aesthetic and partly civic. The second loss is operational. Together they describe a developer experience where the place that used to teach you is gone and the place that now does the work is unreliable. The middle ground, where a senior engineer reviewed a junior engineer's code in public on a forum and the answer existed for the next person, was always going to be hard to preserve under economic pressure. It is gone now.

### The unasked question

The question I keep getting stuck on is whether development velocity should be constrained by infrastructure maturity. The tooling industry's answer is implicitly no. The platform answer, also implicitly, is also no. Demand is shipped, supply absorbs it. So the question keeps not being asked.

It is worth asking anyway. There is no version of the next twelve months in which AI-driven code generation slows down. There is also no version in which existing platforms scale to absorb that growth without strain. Somewhere in the middle is a band of operational practice that hasn't been written yet. Whether that band ends up looking like multi-platform redundancy, or self-hosted forges making a real comeback, or pure-play coordination layers that route around individual platform outages, I don't know. None of those answers feels obviously right and none feels obviously wrong.

What I do know is that we built something faster than we can support, and we are only beginning to feel the consequences. The chart at the top of this post is a snapshot, not a forecast. The trend lines do not have to keep going in the directions they are going. But none of them turn around on their own.
