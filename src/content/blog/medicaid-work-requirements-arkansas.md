---
title: "Did Medicaid Work Requirements Work? A Meta-Analysis of Arkansas"
description: "Arkansas removed roughly 18,000 adults from Medicaid in 2018 and produced no measurable gain in employment. A forest-plot synthesis of the natural experiment, and why the binding constraint was paperwork, not work."
publishDate: 2026-06-09
tags: ["medicaid", "health-policy", "work-requirements", "meta-analysis", "difference-in-differences", "causal-inference"]
lifeweek_topic: "Medicaid work requirements"
homepageMarginnote: "Arkansas was the first state to attach work requirements to Medicaid."
draft: false
---

<style>
@media (prefers-reduced-motion: no-preference) {
  .mwr-grow    { transform: scaleY(0); transform-origin: bottom; transform-box: fill-box; animation: mwr-grow 0.9s cubic-bezier(0.2,0.7,0.3,1) forwards; }
  .mwr-whisker { transform: scaleX(0); transform-origin: center; transform-box: fill-box; animation: mwr-whisker 0.7s ease-out forwards; }
  .mwr-pt      { opacity: 0; animation: mwr-fade 0.5s ease-out forwards; }
  .mwr-diamond { opacity: 0; transform: scale(0.4); transform-origin: center; transform-box: fill-box; animation: mwr-pop 0.6s ease-out forwards; }
  .mwr-draw    { opacity: 0; animation: mwr-fade 0.6s ease-out forwards; }
  @keyframes mwr-grow    { to { transform: scaleY(1); } }
  @keyframes mwr-whisker { to { transform: scaleX(1); } }
  @keyframes mwr-fade    { to { opacity: 1; } }
  @keyframes mwr-pop     { to { opacity: 1; transform: scale(1); } }
}
</style>

The argument for attaching work requirements to Medicaid is intuitive enough that it rarely gets examined: people are on Medicaid because they don't work, so condition the benefit on work and you nudge them into jobs, shrink the rolls, and save money. It is a clean theory of change. It has the structure of a syllogism. And in June 2018, Arkansas ran the first real-world test of it, which means we no longer have to argue about the theory in the abstract. We have data.

This post is a meta-analysis of that data. Not a polemic, a synthesis: I pull together the credible quantitative estimates of what Arkansas's work requirement actually did, pool them where the statistics allow, and show the result on a forest plot. The headline is not subtle. Coverage collapsed. Employment didn't move. And the mechanism that produced the coverage loss had almost nothing to do with whether people were working.

## The theory of change, stated precisely

Arkansas's policy ("Arkansas Works") required Medicaid expansion enrollees ages 30 to 49 to complete 80 hours per month of work or "community engagement" (job training, schooling, volunteering, or job search) and to *report* that activity through an online portal each month. Fail to report for any three months in a calendar year and you lost coverage for the rest of the year, with no path back until January.[^policy]

The policy makes two empirical bets, and they are separable:

1. **A labor-supply bet.** Conditioning Medicaid on work will increase employment among enrollees.
2. **A targeting bet.** The people who lose coverage will be the people who aren't meeting the (reasonable) requirement, so coverage loss is a feature, not a bug.

A meta-analysis is useful precisely because it can test these bets one at a time. So let's hold them apart and see how each one did.

## What Arkansas got, in the first six months

The program began terminating coverage in September 2018. The monthly waves were not small.

<figure>
<svg viewBox="0 0 720 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Bar chart of cumulative Medicaid disenrollments in Arkansas under the 2018 work requirement. Cumulative coverage losses rise from about 4,400 in September 2018 to over 18,000 by December 2018, after which a federal court halts the program in March 2019." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="20" y="24" font-size="11" letter-spacing="1.4" fill="#6a6a6a">CUMULATIVE COVERAGE LOSSES, ARKANSAS WORK REQUIREMENT, 2018</text>
  <line x1="120" y1="80" x2="120" y2="280" stroke="#d0d0c8" stroke-width="1"/>
  <line x1="120" y1="280" x2="660" y2="280" stroke="#d0d0c8" stroke-width="1"/>
  <line x1="120" y1="80"  x2="660" y2="80"  stroke="#d0d0c8" stroke-width="0.5" stroke-dasharray="2,3"/>
  <text x="112" y="84"  font-size="10" fill="#6a6a6a" text-anchor="end">20,000</text>
  <text x="112" y="184" font-size="10" fill="#6a6a6a" text-anchor="end">10,000</text>
  <text x="112" y="283" font-size="10" fill="#6a6a6a" text-anchor="end">0</text>
  <g class="mwr-grow" style="animation-delay:0s">
    <rect x="150" y="232" width="70" height="48" fill="#6a6a6a"/>
  </g>
  <g class="mwr-grow" style="animation-delay:0.12s">
    <rect x="270" y="190" width="70" height="90" fill="#6a6a6a"/>
  </g>
  <g class="mwr-grow" style="animation-delay:0.24s">
    <rect x="390" y="137" width="70" height="143" fill="#6a6a6a"/>
  </g>
  <g class="mwr-grow" style="animation-delay:0.36s">
    <rect x="510" y="80" width="70" height="200" fill="#7a0000"/>
  </g>
  <text x="185" y="296" font-size="11" fill="#6a6a6a" text-anchor="middle">Sep</text>
  <text x="305" y="296" font-size="11" fill="#6a6a6a" text-anchor="middle">Oct</text>
  <text x="425" y="296" font-size="11" fill="#6a6a6a" text-anchor="middle">Nov</text>
  <text x="545" y="296" font-size="11" fill="#6a6a6a" text-anchor="middle">Dec</text>
  <g class="mwr-draw" style="animation-delay:0.7s">
    <text x="185" y="226" font-size="11" fill="#6a6a6a" text-anchor="middle">4,353</text>
    <text x="305" y="184" font-size="11" fill="#6a6a6a" text-anchor="middle">8,168</text>
    <text x="425" y="131" font-size="11" fill="#6a6a6a" text-anchor="middle">13,009</text>
    <text x="545" y="74"  font-size="13" font-style="italic" fill="#7a0000" text-anchor="middle">18,164</text>
  </g>
  <g class="mwr-draw" style="animation-delay:0.9s">
    <text x="620" y="150" font-size="11" font-style="italic" fill="#6a6a6a">Mar 2019:</text>
    <text x="620" y="165" font-size="11" font-style="italic" fill="#6a6a6a">federal court</text>
    <text x="620" y="180" font-size="11" font-style="italic" fill="#6a6a6a">halts the</text>
    <text x="620" y="195" font-size="11" font-style="italic" fill="#6a6a6a">program</text>
  </g>
</svg>
<figcaption>Cumulative Medicaid disenrollments in Arkansas under the work requirement, September–December 2018. More than 18,000 adults lost coverage in the first six months. In March 2019, a federal court vacated the program in <em>Gresham v. Azar</em>.[^gresham]</figcaption>
</figure>

By the time the courts intervened, more than 18,000 adults — roughly a quarter of the targeted population — had been removed from Medicaid.[^coverage] That is the targeting bet's report card, and it requires a number that should stop you cold: surveys found that **more than 95% of the target population already appeared to meet the requirement or qualify for an exemption.**[^ninetyfive] The people losing coverage were, overwhelmingly, people the policy was not supposed to touch.

## The evidence base: what counts as a "study" here?

A meta-analysis pools independent estimates. The honest complication, which I want to put on the table before any forest plot, is that Arkansas is *one* natural experiment, and the high-quality evidence comes from essentially two independent data streams:

- **A Harvard telephone survey** of Arkansas adults and a set of comparison states (Kentucky, Louisiana, Texas), analyzed first at one year (Sommers et al., *NEJM* 2019) and again at two years (Sommers et al., *Health Affairs* 2020). These are the *same cohort* observed over a longer window — not two independent studies.
- **National survey data** (the American Community Survey), analyzed independently by Gangopadhyaya and colleagues (*Health Services Research* 2025), using a different population frame, different comparison logic, and randomization inference.

So the true number of independent samples is closer to two than to four. I'll say so on the plot, and I'll pool only across the genuinely independent sources. Anyone who pools the same cohort twice and reports a tight confidence interval is doing the statistical equivalent of the policy's own targeting error: counting the same thing more than once and calling it a result.

| Analysis | Independent data source | Window | Effect on uninsured rate | Effect on employment |
|---|---|---|---|---|
| Sommers et al., *NEJM* 2019 / *Health Affairs* 2020 | Harvard telephone survey, AR vs KY/LA/TX, ages 30–49 | 2016 → 2018, extended to 2019 | **+7.1 pp** (significant) | −3.5 pp in the target group, matched by −2.9 to −5.7 pp in comparison groups → DiD **not significant** |
| Gangopadhyaya et al., *HSR* 2025 | American Community Survey (national) | 2016 → 2019 | **+4.4 pp** (p = 0.04); +7.4 pp below 100% FPL (p = 0.05) | **−0.7 pp** (p = 0.62) |

## How to meta-analyze a single experiment without lying

Both data streams use difference-in-differences: the change in an outcome for the affected Arkansas group, minus the change for a comparison group that the policy didn't touch. That subtraction nets out anything happening to everyone at once (a regional economy, a national trend) and isolates what the policy itself did.

To combine the independent estimates, I use the standard inverse-variance fixed-effect pool, weighting each estimate by its precision:

\[\hat\theta_{\text{IV}} = \frac{\sum_i w_i\,\hat\theta_i}{\sum_i w_i}, \qquad w_i = \frac{1}{\widehat{\operatorname{Var}}(\hat\theta_i)}, \qquad \operatorname{SE}(\hat\theta_{\text{IV}}) = \sqrt{\frac{1}{\sum_i w_i}}\]

and I check whether the sources actually agree using Cochran's \(Q\) and the \(I^2\) statistic:

\[Q = \sum_i w_i\,(\hat\theta_i - \hat\theta_{\text{IV}})^2, \qquad I^2 = \max\!\left(0,\ \frac{Q - (k-1)}{Q}\right)\]

One methodological wrinkle worth being explicit about: the ACS analysis reports point estimates and p-values, not confidence intervals. When only a two-sided p-value is published alongside a point estimate, you can recover an approximate standard error from the normal approximation,[^altman]

\[z = \Phi^{-1}\!\left(1 - \tfrac{p}{2}\right), \qquad \widehat{\operatorname{SE}} = \frac{|\hat\theta|}{z}\]

which gives, for the uninsurance estimate, \(z \approx 2.05\) and \(\widehat{\operatorname{SE}} \approx 2.1\) percentage points; for the employment estimate, \(z \approx 0.50\) and \(\widehat{\operatorname{SE}} \approx 1.4\). I label every interval below by its provenance: *published*, *read from the published exhibit*, or *derived from the reported p-value*. Nothing in the plot is invented.

## Result 1: coverage collapsed. Result 2: employment didn't.

Here is the whole argument on one axis. The top band is the policy's effect on the uninsured rate; the bottom band is its effect on employment. The dashed line is zero — no effect.

<figure>
<svg viewBox="0 0 760 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Forest plot with two panels sharing a horizontal axis in percentage points. Top panel, effect on the uninsured rate: the Harvard survey estimate is plus 7.1 with a confidence interval from 3.0 to 11.0; the ACS estimate is plus 4.4 from 0.2 to 8.6; the pooled estimate is plus 5.8 from 2.9 to 8.7, well to the right of zero. Bottom panel, effect on employment: the Harvard survey difference-in-differences is not significant and sits on zero; the ACS estimate is minus 0.7 from minus 3.5 to plus 2.1; the pooled estimate sits on zero. Coverage moved sharply; employment did not." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="20" y="22" font-size="11" letter-spacing="1.4" fill="#6a6a6a">POOLED EFFECT OF THE ARKANSAS WORK REQUIREMENT (PERCENTAGE POINTS)</text>
  <line x1="410" y1="44" x2="410" y2="300" stroke="#d0d0c8" stroke-width="1" stroke-dasharray="3,3"/>
  <text x="410" y="318" font-size="10" font-style="italic" fill="#6a6a6a" text-anchor="middle">no effect</text>
  <line x1="310" y1="300" x2="650" y2="300" stroke="#d0d0c8" stroke-width="0.5"/>
  <text x="310" y="316" font-size="10" fill="#6a6a6a" text-anchor="middle">−5</text>
  <text x="510" y="316" font-size="10" fill="#6a6a6a" text-anchor="middle">+5</text>
  <text x="610" y="316" font-size="10" fill="#6a6a6a" text-anchor="middle">+10</text>
  <text x="20" y="62" font-size="12" font-style="italic" fill="#111">More people uninsured  &#8594;</text>
  <g class="mwr-pt" style="animation-delay:0.1s">
    <text x="20" y="100" font-size="13" fill="#111">Harvard survey, 2018</text>
    <text x="20" y="114" font-size="10" fill="#6a6a6a">read from exhibit</text>
  </g>
  <g class="mwr-whisker" style="animation-delay:0.1s">
    <line x1="470" y1="96" x2="630" y2="96" stroke="#111" stroke-width="1.4"/>
    <line x1="470" y1="91" x2="470" y2="101" stroke="#111" stroke-width="1.4"/>
    <line x1="630" y1="91" x2="630" y2="101" stroke="#111" stroke-width="1.4"/>
  </g>
  <circle class="mwr-pt" style="animation-delay:0.35s" cx="552" cy="96" r="5" fill="#111"/>
  <text class="mwr-pt" style="animation-delay:0.35s" x="640" y="100" font-size="11" fill="#6a6a6a">+7.1 [3.0, 11.0]</text>
  <g class="mwr-pt" style="animation-delay:0.25s">
    <text x="20" y="138" font-size="13" fill="#111">ACS national, 2019</text>
    <text x="20" y="152" font-size="10" fill="#6a6a6a">CI derived from p = 0.04</text>
  </g>
  <g class="mwr-whisker" style="animation-delay:0.25s">
    <line x1="414" y1="134" x2="582" y2="134" stroke="#111" stroke-width="1.4"/>
    <line x1="414" y1="129" x2="414" y2="139" stroke="#111" stroke-width="1.4"/>
    <line x1="582" y1="129" x2="582" y2="139" stroke="#111" stroke-width="1.4"/>
  </g>
  <circle class="mwr-pt" style="animation-delay:0.5s" cx="498" cy="134" r="5" fill="#111"/>
  <text class="mwr-pt" style="animation-delay:0.5s" x="640" y="138" font-size="11" fill="#6a6a6a">+4.4 [0.2, 8.6]</text>
  <text class="mwr-pt" style="animation-delay:0.6s" x="20" y="170" font-size="13" font-style="italic" fill="#7a0000">Pooled (2 sources)</text>
  <polygon class="mwr-diamond" style="animation-delay:0.7s" points="468,166 526,158 584,166 526,174" fill="#7a0000"/>
  <text class="mwr-pt" style="animation-delay:0.8s" x="640" y="170" font-size="11" font-style="italic" fill="#7a0000">+5.8 [2.9, 8.7]</text>
  <line x1="20" y1="190" x2="740" y2="190" stroke="#d0d0c8" stroke-width="0.5"/>
  <text x="20" y="210" font-size="12" font-style="italic" fill="#111">More people working  &#8594;</text>
  <g class="mwr-pt" style="animation-delay:0.3s">
    <text x="20" y="246" font-size="13" fill="#111">Harvard survey</text>
    <text x="20" y="260" font-size="10" fill="#6a6a6a">DiD not significant; no CI published</text>
  </g>
  <circle class="mwr-pt" style="animation-delay:0.55s" cx="410" cy="242" r="5" fill="none" stroke="#111" stroke-width="1.4"/>
  <text class="mwr-pt" style="animation-delay:0.55s" x="640" y="246" font-size="11" fill="#6a6a6a">≈ 0 (n.s.)</text>
  <g class="mwr-pt" style="animation-delay:0.45s">
    <text x="20" y="284" font-size="13" fill="#111">ACS national, 2019</text>
    <text x="20" y="298" font-size="10" fill="#6a6a6a">CI derived from p = 0.62</text>
  </g>
  <g class="mwr-whisker" style="animation-delay:0.45s">
    <line x1="340" y1="280" x2="452" y2="280" stroke="#111" stroke-width="1.4"/>
    <line x1="340" y1="275" x2="340" y2="285" stroke="#111" stroke-width="1.4"/>
    <line x1="452" y1="275" x2="452" y2="285" stroke="#111" stroke-width="1.4"/>
  </g>
  <circle class="mwr-pt" style="animation-delay:0.7s" cx="396" cy="280" r="5" fill="#111"/>
  <text class="mwr-pt" style="animation-delay:0.7s" x="640" y="284" font-size="11" fill="#6a6a6a">−0.7 [−3.5, 2.1]</text>
</svg>
<figcaption>A two-outcome forest plot of the Arkansas work requirement. The pooled effect on the uninsured rate is +5.8 percentage points (95% CI 2.9 to 8.7), nowhere near zero; the two independent sources agree closely (Cochran's <em>Q</em> = 0.83, df = 1, <em>I²</em> ≈ 0%). The effect on employment is statistically indistinguishable from zero in every analysis. Markers are point estimates; horizontal lines are 95% confidence intervals (provenance labeled per row); the diamond is the inverse-variance pooled estimate.</figcaption>
</figure>

The two independent sources disagree on the *magnitude* of the coverage loss — the survey saw +7.1 points, the ACS +4.4 — but not on its sign or significance, and the heterogeneity statistic confirms it: \(I^2 \approx 0\%\), meaning essentially all the spread between them is sampling noise rather than genuine disagreement. Pooled, the work requirement raised the uninsured rate by **5.8 percentage points** (95% CI 2.9 to 8.7). That interval does not come close to including zero.

The employment panel is the one that should end the policy debate. Every estimate sits on top of the no-effect line. The best-identified single number, the ACS estimate, is −0.7 points with a confidence interval running from −3.5 to +2.1 — and the negative sign, for what little it's worth, points the *wrong way* for the policy's theory. The Harvard analysis reaches the same non-result: employment among the targeted 30-to-49-year-olds fell by 3.5 points, but it fell by a statistically identical amount among the younger and older adults the policy never touched, so the difference-in-differences washes out to nothing.[^employment] Two independent designs, one conclusion: **the labor-supply bet returned nothing.**

## Why the theory failed: the portal *was* the policy

Put the two results together and a mechanism falls out. If conditioning Medicaid on work had actually pushed people into jobs, you'd expect the employment line to move. It didn't. If the people losing coverage were the ones failing to work, you'd expect the losses to concentrate among non-workers. They didn't — over 95% of the target population already met the bar or qualified for an exemption.

<figure>
<svg viewBox="0 0 720 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A two-column comparison. The policy promised: employment up, coverage roughly steady. Arkansas got: employment flat, coverage down sharply with over 18,000 disenrolled. The mechanism note explains that more than 95 percent of the target population already met the requirement, so the binding constraint was monthly online reporting, not work." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="180" y="30" font-size="12" letter-spacing="1.2" fill="#6a6a6a" text-anchor="middle">WHAT THE POLICY PROMISED</text>
  <text x="540" y="30" font-size="12" letter-spacing="1.2" fill="#6a6a6a" text-anchor="middle">WHAT ARKANSAS GOT</text>
  <line x1="360" y1="46" x2="360" y2="240" stroke="#d0d0c8" stroke-width="1"/>
  <g class="mwr-draw" style="animation-delay:0.1s">
    <text x="40" y="92" font-size="14" fill="#111">Employment</text>
    <line x1="210" y1="100" x2="250" y2="70" stroke="#6a6a6a" stroke-width="1.6"/>
    <polygon points="250,70 243,72 248,78" fill="#6a6a6a"/>
    <text x="262" y="86" font-size="12" font-style="italic" fill="#6a6a6a">rises</text>
  </g>
  <g class="mwr-draw" style="animation-delay:0.3s">
    <text x="400" y="92" font-size="14" fill="#111">Employment</text>
    <line x1="560" y1="85" x2="610" y2="85" stroke="#111" stroke-width="1.6"/>
    <text x="620" y="90" font-size="12" font-style="italic" fill="#111">flat (≈ 0)</text>
  </g>
  <g class="mwr-draw" style="animation-delay:0.5s">
    <text x="40" y="172" font-size="14" fill="#111">Coverage</text>
    <line x1="210" y1="160" x2="250" y2="168" stroke="#6a6a6a" stroke-width="1.6"/>
    <text x="262" y="172" font-size="12" font-style="italic" fill="#6a6a6a">roughly steady</text>
  </g>
  <g class="mwr-draw" style="animation-delay:0.7s">
    <text x="400" y="172" font-size="14" fill="#111">Coverage</text>
    <line x1="560" y1="150" x2="600" y2="186" stroke="#7a0000" stroke-width="1.8"/>
    <polygon points="600,186 593,180 597,190" fill="#7a0000"/>
    <text x="610" y="176" font-size="12" font-style="italic" fill="#7a0000">+5.8 pp uninsured</text>
    <text x="610" y="192" font-size="11" font-style="italic" fill="#6a6a6a">18,000+ disenrolled</text>
  </g>
  <line x1="40" y1="222" x2="680" y2="222" stroke="#d0d0c8" stroke-width="0.5"/>
  <text class="mwr-draw" style="animation-delay:0.9s" x="40" y="248" font-size="12" font-style="italic" fill="#6a6a6a">Mechanism: &gt; 95% of the target group already met the requirement or qualified for exemption.</text>
  <text class="mwr-draw" style="animation-delay:0.9s" x="40" y="266" font-size="12" font-style="italic" fill="#6a6a6a">The binding constraint was monthly online reporting, not work.</text>
</svg>
<figcaption>The policy made two bets. The labor-supply bet (employment rises) returned nothing. The targeting bet (only non-compliant people lose coverage) failed because the constraint that actually disenrolled people was the monthly reporting requirement, not their work status.</figcaption>
</figure>

So what was the binding constraint? Reporting. To keep coverage, an enrollee who was *already working full time* still had to log into a state web portal every month and attest to it. Miss three months — because you didn't know the rule, because you lost the letter, because the portal was down between 9 p.m. and 7 a.m., because you don't have reliable internet, because you assumed your employer's payroll already proved you worked — and you were cut. The policy didn't filter on work. It filtered on the ability to navigate a monthly compliance task. Coverage loss tracked notification and login failure, not labor-market behavior.

## What a data engineer sees

I spend my working life in the gap between what a system is supposed to measure and what it actually measures, and Arkansas is one of the cleanest examples of that gap I know of in public policy. The work requirement was specified as a labor-supply intervention. Its *implementation* was a monthly ETL job with a human in the loop and no retry logic: ingest an attestation each month, and on three missing records, terminate. Predictably, the thing it measured was not work. It was data-submission reliability, which is correlated with internet access, health literacy, and stable housing far more than with employment.

That is the failure that the forest plot makes visible. The coverage diamond sits at +5.8 points because the reporting filter has real teeth. The employment diamond sits on zero because the labor-supply theory was never the operative mechanism. When you build a system whose stated purpose and whose actual selection criterion are different things, the data will eventually tell you so — and here it told us at the cost of more than 18,000 people's health insurance, with no jobs to show for it.

---

### Limitations

This is a synthesis of one natural experiment, not a meta-analysis of many independent trials, and I've tried not to dress it up as more than that. There are really two independent data streams (the Harvard survey and the national ACS analysis); the pooled coverage estimate rests on \(k = 2\), and the employment "pool" is effectively anchored on the single ACS estimate with the survey result as concordant support. Several intervals are reconstructed — from a published exhibit, or from a reported p-value via the normal approximation — rather than lifted verbatim, and I've labeled each one accordingly. None of these caveats touch the qualitative conclusion, which is robust precisely because it is so lopsided: a large, significant, sign-consistent effect on coverage, and an effect on employment that no analysis can distinguish from zero.

[^policy]: Arkansas Department of Human Services, "Arkansas Works" Section 1115 demonstration. The community-engagement requirement applied to expansion enrollees ages 30–49 and required 80 hours/month of qualifying activity reported through an online portal.

[^gresham]: *Gresham v. Azar*, 363 F. Supp. 3d 165 (D.D.C. 2019). The court vacated the Secretary's approval of the Arkansas work requirement in March 2019, halting the program.

[^coverage]: B. D. Sommers et al., "Medicaid Work Requirements — Results from the First Year in Arkansas," *New England Journal of Medicine* 381 (2019): 1073–1082. <https://www.nejm.org/doi/full/10.1056/NEJMsr1901772>

[^ninetyfive]: Harvard T. H. Chan School of Public Health, "Coverage losses, substantial confusion in Arkansas following implementation of Medicaid work requirements" (2019). Survey evidence indicated more than 95% of the target population appeared to meet the requirement or qualify for an exemption.

[^employment]: In the Harvard survey, employment among Arkansans ages 30–49 fell from 42.4% to 38.9% (−3.5 pp), but comparison age groups not subject to the policy fell by a similar −2.9 to −5.7 pp, leaving no significant difference-in-differences. See also B. D. Sommers et al., "Medicaid Work Requirements in Arkansas: Two-Year Impacts on Coverage, Employment, and Affordability of Care," *Health Affairs* 39, no. 9 (2020): 1522–1530. <https://www.healthaffairs.org/doi/10.1377/hlthaff.2020.00538>

[^altman]: D. G. Altman and J. M. Bland, "How to obtain the confidence interval from a P value," *BMJ* 343 (2011): d2090. The ACS estimates are from A. Gangopadhyaya et al., "The Impact of Arkansas Medicaid Work Requirements on Coverage and Employment: Estimating Effects Using National Survey Data," *Health Services Research* (2025). <https://onlinelibrary.wiley.com/doi/10.1111/1475-6773.14624>
