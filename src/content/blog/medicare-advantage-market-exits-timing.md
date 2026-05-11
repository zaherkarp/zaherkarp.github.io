---
title: "When Insurers Leave: The Hidden Calendar Behind Medicare Advantage Exits"
publishDate: 2026-05-09
description: >
  Private Medicare coverage is contracting. The exits aren't random,
  they follow a regulatory clock most people never see. Two charts explain
  what's happening and when.
tags: ["medicare advantage", "health policy", "data visualization"]
homepageMarginnote: "Exit announcements cluster in a 2-day window each July. That's not a coincidence."
---

More than half of Medicare beneficiaries now get their coverage through private plans, called Medicare Advantage. Those plans have been contracting. In the 2025 and 2026 plan years, the largest insurers cut service areas, dropped counties, and exited entire markets. Coverage was withdrawn from millions of seniors who had to find new plans during open enrollment. Most news coverage treated the wave as surprising. It wasn't. The exits were predictable from a regulatory calendar that almost no one outside the industry reads.

The shape of the contraction is visible in two pictures.

<figure class="post-chart">
<style>
.post-chart { --pc-ink:#111; --pc-muted:#6a6a6a; --pc-rule:#d0d0c8; --pc-accent:#7a0000; --pc-paper:#fffff8; font-family:'et-book', Palatino, "Palatino Linotype", "Book Antiqua", Georgia, serif; margin:1.8rem auto; max-width:760px; width:100%; }
.post-chart .pc-summary { display:flex; gap:1rem; flex-wrap:wrap; margin:0 0 1rem; padding:0.55rem 0; border-top:1px solid var(--pc-rule); border-bottom:1px solid var(--pc-rule); }
.post-chart .pc-summary .metric { flex:1 1 30%; padding:0.2rem 0.3rem; text-align:left; }
.post-chart .pc-summary .metric .n { display:block; font-size:1.5rem; line-height:1; color:var(--pc-ink); font-feature-settings:"lnum"; }
.post-chart .pc-summary .metric .lab { display:block; margin-top:0.3rem; font-size:0.78rem; font-style:italic; color:var(--pc-muted); line-height:1.3; }
.post-chart .pc-panel { margin:0 0 1rem; }
.post-chart .pc-panel-title { margin:0 0 0.3rem; font-size:0.85rem; font-style:italic; font-weight:normal; color:var(--pc-muted); letter-spacing:0.02em; }
.post-chart canvas { max-width:100%; height:200px !important; }
.post-chart .pc-note { font-size:0.78rem; font-style:italic; color:var(--pc-muted); margin:0.6rem 0 0; line-height:1.4; }
.post-chart figcaption { font-size:0.82rem; color:var(--pc-muted); margin-top:0.8rem; font-style:italic; line-height:1.45; text-align:left; }
.post-chart .chart2-svg { display:block; width:100%; max-width:860px; height:auto; margin:0 auto; }
@media (prefers-color-scheme: dark) { .post-chart { --pc-ink:#f5ecd7; --pc-muted:#c2b8a0; --pc-rule:#3a3024; --pc-accent:#e05e3e; --pc-paper:#201b14; } }
</style>
<div class="pc-summary"><div class="metric"><span class="n">43</span><span class="lab">peak plans per beneficiary (2023–24)</span></div><div class="metric"><span class="n">18</span><span class="lab">brand exits, 2025 plan year</span></div><div class="metric"><span class="n">1.8M</span><span class="lab">members affected, 2025</span></div></div>
<div class="pc-panel"><h4 class="pc-panel-title">Plans available per beneficiary, on average</h4><canvas id="chart1-plans"></canvas></div>
<div class="pc-panel"><h4 class="pc-panel-title">Confirmed full brand exits, by plan year</h4><canvas id="chart1-exits"></canvas></div>
<p class="pc-note">Hatched bars (2022–2024): no systematic public count of full brand exits before the 2025 cycle. Absence of data is not evidence of zero exits.</p>
<figcaption>Panel 1: Average MA plans available per Medicare beneficiary (KFF, CMS Landscape files, non-SNP individual enrollment). Panel 2: Confirmed full brand exits by plan year. Gray bars = not systematically reported in public literature; absence of data is not evidence of zero exits.</figcaption>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
(() => {
  const dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const ink = dark ? '#f5ecd7' : '#111';
  const muted = dark ? '#c2b8a0' : '#6a6a6a';
  const rule = dark ? '#3a3024' : '#d0d0c8';
  const accent = dark ? '#e05e3e' : '#7a0000';
  const years = ['2022', '2023', '2024', '2025', '2026'];
  const plans = [38, 43, 43, 42, 39];
  const hatchCanvas = document.createElement('canvas');
  hatchCanvas.width = 8; hatchCanvas.height = 8;
  const hctx = hatchCanvas.getContext('2d');
  hctx.strokeStyle = muted; hctx.lineWidth = 0.7;
  hctx.beginPath();
  hctx.moveTo(0, 8); hctx.lineTo(8, 0);
  hctx.moveTo(-2, 2); hctx.lineTo(2, -2);
  hctx.moveTo(6, 10); hctx.lineTo(10, 6);
  hctx.stroke();
  const hatch = hctx.createPattern(hatchCanvas, 'repeat');
  const ctxPlans = document.getElementById('chart1-plans');
  if (ctxPlans && window.Chart) {
    new Chart(ctxPlans, {
      type: 'line',
      data: { labels: years, datasets: [{ data: plans, borderColor: ink, backgroundColor: ink, borderWidth: 1.4, tension: 0.18, pointRadius: 4, pointBackgroundColor: ink, pointBorderColor: ink }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { enabled: true, callbacks: { label: (c) => `${c.formattedValue} plans` } } }, scales: { y: { beginAtZero: false, suggestedMin: 30, suggestedMax: 46, grid: { color: rule, drawBorder: false }, ticks: { color: muted, font: { family: 'Palatino, Georgia, serif', size: 11 }, stepSize: 5 } }, x: { grid: { display: false, drawBorder: false }, ticks: { color: muted, font: { family: 'Palatino, Georgia, serif', size: 11 } } } } }
    });
  }
  const ctxExits = document.getElementById('chart1-exits');
  if (ctxExits && window.Chart) {
    const exitsData = [4, 4, 4, 18, 8];
    const labelPlugin = {
      id: 'chart1-bar-labels',
      afterDatasetsDraw(chart) {
        const { ctx, scales } = chart;
        if (!scales || !scales.x || !scales.y) return;
        ctx.save();
        ctx.fillStyle = muted;
        ctx.font = "italic 9px Palatino, Georgia, serif";
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        [0, 1, 2].forEach(i => { ctx.fillText('no count', scales.x.getPixelForValue(i), scales.y.getPixelForValue(4) - 3); });
        ctx.fillStyle = accent;
        ctx.font = "10px Palatino, Georgia, serif";
        ctx.fillText('18', scales.x.getPixelForValue(3), scales.y.getPixelForValue(18) - 3);
        ctx.fillStyle = muted;
        ctx.fillText('8+', scales.x.getPixelForValue(4), scales.y.getPixelForValue(8) - 3);
        ctx.restore();
      }
    };
    new Chart(ctxExits, {
      type: 'bar',
      data: { labels: years, datasets: [{ data: exitsData, backgroundColor: [hatch, hatch, hatch, accent, muted], borderColor: [muted, muted, muted, accent, muted], borderWidth: 0.6 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => { const y = c.label; if (['2022', '2023', '2024'].includes(y)) return 'No public count (data gap)'; if (y === '2025') return '18 brand exits'; if (y === '2026') return '8+ brand exits (incomplete)'; return c.formattedValue; } } } }, scales: { y: { beginAtZero: true, suggestedMax: 22, grid: { color: rule, drawBorder: false }, ticks: { color: muted, font: { family: 'Palatino, Georgia, serif', size: 11 }, stepSize: 5 } }, x: { grid: { display: false, drawBorder: false }, ticks: { color: muted, font: { family: 'Palatino, Georgia, serif', size: 11 } } } } },
      plugins: [labelPlugin]
    });
  }
})();
</script>
</figure>

The top panel tracks the average number of plans available to a typical beneficiary. The count rose for years, peaked at 43 in 2023 and 2024, then reversed. The bottom panel counts the full brand exits behind that reversal. Eighteen named insurer brands left for the 2025 plan year, dropping coverage for roughly 1.8 million people. The hatched bars before 2025 are a data gap. The first systematic public counts of full brand exits appeared in October 2024; earlier years were never tallied the same way.

None of this happens on its own. The Centers for Medicare and Medicaid Services, or CMS, runs Medicare Advantage on a fixed annual schedule. In mid-January, CMS publishes the Advance Notice, a draft of next year's payment rates. The final rates land in early April. By federal statute, the announcement is always anchored to the first Monday of the month. Insurers then have until early June to submit their bids, which include the plans they intend to sell, the counties they will sell them in, and the premiums they will charge. Bids are where the internal exit decisions get locked in. CMS reviews the bids over the summer, releases the public plan landscape on October 1, and opens enrollment from October 15 through December 7. New coverage begins January 1. Insurers know in April whether the rates work. They decide by June. The public hears in October.

Plot the exit announcements against the calendar and the choreography is hard to miss.

<figure class="post-chart">
<svg id="chart2-svg" class="chart2-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 400" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Two-lane timeline of Medicare Advantage exit announcements for plan years 2025 and 2026, plotted against the fixed CMS regulatory calendar (Advance Notice in January, Final Rate in April, Bid Deadline in June, Landscape Release in October).">
<text id="chart2-cluster-q2" x="525" y="18" font-size="10" font-style="italic" fill="#6a6a6a" text-anchor="middle">Q2 earnings cluster</text>
<text id="chart2-cluster-oct" x="645" y="18" font-size="10" font-style="italic" fill="#6a6a6a" text-anchor="middle">public confirmation</text>
<line id="chart2-cluster-q2-guide" x1="525" y1="22" x2="525" y2="38" stroke="#6a6a6a" stroke-width="0.4" stroke-dasharray="2 2"/>
<line id="chart2-cluster-oct-guide" x1="645" y1="22" x2="645" y2="38" stroke="#6a6a6a" stroke-width="0.4" stroke-dasharray="2 2"/>
<text id="chart2-py25-title" x="14" y="48" font-size="13" font-style="italic" fill="#111">Plan year 2025 cycle</text>
<text id="chart2-py25-sub" x="14" y="62" font-size="10" fill="#6a6a6a">bid year 2024</text>
<line id="chart2-py25-axis" x1="80" y1="92" x2="830" y2="92" stroke="#d0d0c8" stroke-width="0.5"/>
<g id="chart2-py25-months" font-size="9" fill="#6a6a6a" text-anchor="middle">
<text x="120" y="84">Jan</text><text x="178" y="84">Feb</text><text x="243" y="84">Mar</text><text x="305" y="84">Apr</text><text x="366" y="84">May</text><text x="428" y="84">Jun</text><text x="490" y="84">Jul</text><text x="553" y="84">Aug</text><text x="616" y="84">Sep</text><text x="676" y="84">Oct</text><text x="738" y="84">Nov</text><text x="800" y="84">Dec</text>
</g>
<g id="chart2-py25-milestones" stroke="#6a6a6a" stroke-width="0.7" stroke-dasharray="3 3">
<line id="chart2-py25-an" x1="120" y1="100" x2="120" y2="170"/>
<line id="chart2-py25-fr" x1="277" y1="100" x2="277" y2="170"/>
<line id="chart2-py25-bid" x1="402" y1="100" x2="402" y2="170"/>
<line id="chart2-py25-ls" x1="643" y1="100" x2="643" y2="170"/>
</g>
<g id="chart2-py25-mlabels" font-size="9" font-style="italic" fill="#6a6a6a" text-anchor="start">
<text id="chart2-py25-an-l" transform="rotate(-90 124 132)" x="124" y="132">Adv. Notice · Jan 15</text>
<text id="chart2-py25-fr-l" transform="rotate(-90 281 132)" x="281" y="132">Final Rate · Apr 1</text>
<text id="chart2-py25-bid-l" transform="rotate(-90 406 132)" x="406" y="132">Bid Deadline · Jun 3</text>
<text id="chart2-py25-ls-l" transform="rotate(-90 647 132)" x="647" y="132">Landscape · Oct 1</text>
</g>
<line id="chart2-py25-lane" x1="80" y1="140" x2="830" y2="140" stroke="#111" stroke-width="0.6"/>
<circle id="chart2-py25-cigna" cx="153" cy="140" r="6" fill="#7a0000"/>
<circle id="chart2-py25-humana" cx="510" cy="140" r="6" fill="#111"/>
<circle id="chart2-py25-centene" cx="524" cy="140" r="6" fill="#111"/>
<circle id="chart2-py25-cvs" cx="526" cy="140" r="6" fill="#111"/>
<circle id="chart2-py25-ow" cx="645" cy="140" r="6" fill="#6a6a6a"/>
<g id="chart2-py25-clabels" font-size="9" fill="#6a6a6a" font-style="italic">
<text x="162" y="143" text-anchor="start">Cigna 8-K · HCSC sale · Jan 31</text>
<text x="162" y="155" text-anchor="start" fill="#7a0000">M&amp;A, not rate</text>
<text x="510" y="170" text-anchor="middle">Humana Q2 · Jul 31 · 500K decline</text>
<text x="525" y="182" text-anchor="middle">Centene 6-state · Aug 7 &nbsp;|&nbsp; CVS/Aetna · Aug 8</text>
<text x="645" y="170" text-anchor="middle">Oliver Wyman count: 18 brands</text>
</g>
<line id="chart2-divider" x1="14" y1="208" x2="866" y2="208" stroke="#d0d0c8" stroke-width="0.5"/>
<text id="chart2-py26-title" x="14" y="228" font-size="13" font-style="italic" fill="#111">Plan year 2026 cycle</text>
<text id="chart2-py26-sub" x="14" y="242" font-size="10" fill="#6a6a6a">bid year 2025</text>
<line id="chart2-py26-axis" x1="80" y1="272" x2="830" y2="272" stroke="#d0d0c8" stroke-width="0.5"/>
<g id="chart2-py26-months" font-size="9" fill="#6a6a6a" text-anchor="middle">
<text x="120" y="264">Jan</text><text x="178" y="264">Feb</text><text x="243" y="264">Mar</text><text x="305" y="264">Apr</text><text x="366" y="264">May</text><text x="428" y="264">Jun</text><text x="490" y="264">Jul</text><text x="553" y="264">Aug</text><text x="616" y="264">Sep</text><text x="676" y="264">Oct</text><text x="738" y="264">Nov</text><text x="800" y="264">Dec</text>
</g>
<g id="chart2-py26-milestones" stroke="#6a6a6a" stroke-width="0.7" stroke-dasharray="3 3">
<line id="chart2-py26-an" x1="120" y1="280" x2="120" y2="350"/>
<line id="chart2-py26-fr" x1="287" y1="280" x2="287" y2="350"/>
<line id="chart2-py26-bid" x1="400" y1="280" x2="400" y2="350"/>
<line id="chart2-py26-ls" x1="643" y1="280" x2="643" y2="350"/>
</g>
<g id="chart2-py26-mlabels" font-size="9" font-style="italic" fill="#6a6a6a" text-anchor="start">
<text id="chart2-py26-an-l" transform="rotate(-90 124 312)" x="124" y="312">Adv. Notice · Jan 15</text>
<text id="chart2-py26-fr-l" transform="rotate(-90 291 312)" x="291" y="312">Final Rate · Apr 7</text>
<text id="chart2-py26-bid-l" transform="rotate(-90 404 312)" x="404" y="312">Bid Deadline · Jun 2</text>
<text id="chart2-py26-ls-l" transform="rotate(-90 647 312)" x="647" y="312">Landscape · Oct 1</text>
</g>
<line id="chart2-py26-lane" x1="80" y1="320" x2="830" y2="320" stroke="#111" stroke-width="0.6"/>
<circle id="chart2-py26-hum-q1" cx="333" cy="320" r="6" fill="#111"/>
<circle id="chart2-py26-uhc-q2" cx="516" cy="320" r="6" fill="#111"/>
<circle id="chart2-py26-hum-q2" cx="518" cy="320" r="6" fill="#111"/>
<circle id="chart2-py26-uhc-ls" cx="645" cy="320" r="6" fill="#6a6a6a"/>
<circle id="chart2-py26-beckers" cx="647" cy="320" r="6" fill="#6a6a6a"/>
<g id="chart2-py26-clabels" font-size="9" fill="#6a6a6a" font-style="italic">
<text x="333" y="338" text-anchor="middle">Humana Q1 · Apr 29 · 550K affirmed</text>
<text x="517" y="354" text-anchor="middle">UHC Q2 · Jul 29 (600K PPO) &nbsp;|&nbsp; Humana Q2 · Jul 30</text>
<text x="646" y="366" text-anchor="middle">UHC plans · Oct 1 (180K no alt.) &nbsp;|&nbsp; Becker's 8+ · Oct 2</text>
</g>
<line id="chart2-q2-band-top" x1="505" y1="38" x2="505" y2="378" stroke="#d0d0c8" stroke-width="0.4" stroke-dasharray="1 4"/>
<line id="chart2-q2-band-bot" x1="540" y1="38" x2="540" y2="378" stroke="#d0d0c8" stroke-width="0.4" stroke-dasharray="1 4"/>
<line id="chart2-oct-band-l" x1="628" y1="38" x2="628" y2="378" stroke="#d0d0c8" stroke-width="0.4" stroke-dasharray="1 4"/>
<line id="chart2-oct-band-r" x1="655" y1="38" x2="655" y2="378" stroke="#d0d0c8" stroke-width="0.4" stroke-dasharray="1 4"/>
</svg>
<figcaption>Two plan-year cycles. Dashed verticals = fixed CMS regulatory milestones. Circles = exit announcements, plotted by the date of first public disclosure. Color indicates announcement type: <span style="white-space:nowrap"><svg width="9" height="9" viewBox="0 0 9 9" style="vertical-align:baseline;display:inline-block"><circle cx="4.5" cy="4.5" r="3.5" fill="#7a0000"/></svg> 8-K / definitive agreement</span>; <span style="white-space:nowrap"><svg width="9" height="9" viewBox="0 0 9 9" style="vertical-align:baseline;display:inline-block"><circle cx="4.5" cy="4.5" r="3.5" fill="#111"/></svg> earnings-call disclosure</span>; <span style="white-space:nowrap"><svg width="9" height="9" viewBox="0 0 9 9" style="vertical-align:baseline;display:inline-block"><circle cx="4.5" cy="4.5" r="3.5" fill="#6a6a6a"/></svg> landscape file / press confirmation</span>. Dates sourced from SEC 8-K filings, earnings call transcripts, and contemporaneous press releases.</figcaption>
</figure>

Two clusters dominate. The first sits in late July and early August, the same days each year that the major insurers report Q2 earnings, days after bids are due. The second sits at October 1, the day the public plan landscape goes live. The Cigna circle at January 31, 2024 is the lone outlier in either cycle. Cigna sold its entire Medicare Advantage book to HCSC under a definitive agreement that month, well before the April rate notice. That exit was driven by a portfolio sale, not by payment policy.

The position on the calendar tells you something about the kind of exit you are looking at. An announcement that surfaces at Q2 earnings, with explicit member-loss guidance handed to investors, is large, intentional, and rate-reactive. Humana fits this pattern cleanly. On July 31, 2024, the company guided to a 550,000-member decline for the 2025 plan year on its Q2 call. CVS and Aetna followed the same week with a similar signal, and Centene confirmed a six-state withdrawal the week before. An exit that first becomes visible in October, with no July signal, is usually smaller and tactical, the kind of county-level pruning that does not move a quarterly earnings number. An exit announced before April, like the Cigna sale, is almost always merger-driven, not rate-driven.

The same calendar is already running for the 2027 plan year. CMS published the 2027 Advance Notice on January 26, 2026. The final rate notice will land by April 6, 2026. Bids are due June 1. If there are exits to come, the late-July 2026 Q2 earnings calls are when they will surface, months before any beneficiary hears about them.
