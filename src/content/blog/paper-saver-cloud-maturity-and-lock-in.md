---
title: "Paper Saver: cloud maturity and lock-in across AWS, Azure, and GCP"
publishDate: 2026-05-19
description: "A follow-up to the original Paper Saver post. The wrong-shaped question is 'now do Azure and GCP.' The right one is whether your organization is mature enough to capture the compute-scaling discount its cloud already advertises. A new diagnostic module returns a 3x3 grid of cost by cloud and by maturity."
draft: false
tags: [aws, azure, gcp, xgboost, mlops, finops, cost-modeling, healthcare-analytics]
---

The [original Paper Saver post](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/) drew one consistent piece of feedback: "now do Azure and GCP." It is the natural follow-up question, and it is also wrong-shaped in a way worth examining before answering it.

The rate-card delta between AWS, Azure, and GCP is the least interesting part of multi-cloud cost work. For a typical XGBoost workload the headline difference between m7i, Dasv5, and n2d-standard at the same vCPU and memory is on the order of 10 to 20 percent of list price. The difference between paying list price and paying the spot or commitment price the same cloud advertises is 50 to 70 percent. So the load-bearing question is not which cloud you are on. It is whether your organization has the operational maturity to capture the discount mechanisms your existing cloud already offers.

There is also a question readers were not asking but should be: if you are a Microsoft shop with data in ADLS and identity in Entra ID, the rate card is not the cost of switching. The cost of switching is egress, re-platforming, identity migration, and a year of re-doing every compliance review for a new control plane. Naive cloud comparison hides that under the rate-card delta.

So the follow-up tool is not "the same estimator with three price lists." It is a maturity-and-lock-in diagnostic. The code lives at [github.com/zaherkarp/paper-saver](https://github.com/zaherkarp/paper-saver) as `cloud_maturity.py`, alongside the original estimator and the annualized TCO model.

## What naive cloud comparison gets wrong

Three things, in increasing order of how much they matter.

CPU microarchitecture is not portable. The compute constant in the [original post's calibration evidence](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/#calibration-evidence) was derived from Intel Xeon performance on Colab. AWS m7i is Intel Sapphire Rapids; Azure Dasv5 and GCP n2d are both AMD EPYC Milan. XGBoost histogram throughput on those parts differs by maybe 10 to 25 percent per clock, and the difference compounds across long training runs. The new module uses one constant for all three clouds because the maturity-tier deltas (50 to 70 percent) are larger than the microarchitecture noise. If you need precision, run `--calibrate` on each target environment. For budgeting and scoping decisions, the noise is below the signal.

Spot semantics are not equivalent. AWS Spot, Azure Spot, and GCP Spot VMs all advertise "up to 90 percent off," and all three have eviction risk that varies by region and SKU. The [working spot factor in the original post](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/#pricing-anchors) (0.30, anchored on real EC2 Spot workshop and case-study data) applies broadly across all three clouds, but the operational lift to actually realize that 70 percent is not the same. Eviction models differ: Azure Spot is eager and varies more aggressively by region; GCP Spot has a 30-second preemption notice and a 24-hour maximum lifetime on some SKUs, which constrains long training jobs that lack mid-flight checkpointing; AWS Spot has the longest operational track record and the most third-party tooling for graceful eviction handling.

The rate-card delta hides the lock-in delta. The egress fee is the visible piece, but it is the smallest part of the lock-in story for an enterprise. The unmoveable costs are data gravity (S3 vs ADLS vs GCS, plus the warehouse layer on top), identity gravity (IAM vs Entra ID vs Google IAM with Workload Identity Federation), and the compliance review burden of bringing a new control plane through legal, security, and audit. A Microsoft shop saving 12 percent on compute by moving an XGBoost workload to GCP will spend that 12 percent multiple times over within a year on the costs the rate card does not show.

## Reframe: maturity gates the discount

The cleaner question is: given the cloud you are locked into for organizational reasons, what fraction of the theoretical compute discount can your team actually realize? That is the question the new module answers, with a three-tier model inspired by the FinOps Foundation's Crawl/Walk/Run maturity framework.

The tiers are not aspirational labels. They are observable operational capabilities that gate which discount mechanisms a team can use without breaking production.

**Crawl** is on-demand only. No spot, no commitments, single-node training. This is the modal starting point for organizations whose ML workloads run on the team's general-purpose dev cluster or an ad-hoc EC2 or VM provisioned per training run. There is nothing wrong with Crawl as a starting point. It is a cost problem only when an organization is paying Crawl prices for a workload portfolio large enough that the unrealized discount is material.

**Walk** is spot for training and batch scoring, plus a 1-year commitment for always-on inference. Single-node training only. This requires three operational pieces that an organization at Crawl tier does not have: spot-tolerant training workflows (checkpoint to object storage every N rounds; tolerate retry on eviction), a job-orchestrator that survives interruption (AWS Batch, Azure Batch, GCP Batch, or equivalent), and a FinOps practice mature enough to make a 1-year commitment without flinching. Most production-ML teams reach Walk tier by the second year of running models in production.

**Run** is spot for training with multi-node where memory dictates, spot for batch scoring, and 3-year commitments for always-on inference. This requires a dedicated MLOps function, a mature FinOps practice that rebalances commitments rather than buying once, and a portfolio large enough that 3-year lock-in carries acceptable risk against demand uncertainty. Run is where compute scaling is mostly captured. Further optimization moves into TCO categories outside the compute slice (data pipelines, monitoring consolidation, FTE leverage), which the [original TCO model](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/#from-marginal-compute-to-annual-tco) covers.

## What the grid actually shows

The module's output is a 3x3 grid: three clouds (AWS, Azure, GCP) across three maturity tiers (Crawl, Walk, Run), with annual compute cost in each cell for a given workload. Each cloud uses its own native instance catalog and discount vocabulary: AWS pulls from m7i and r7i with EC2 Spot and Compute Savings Plans, Azure from Dasv5 and Easv5 with Azure Spot and Reserved Instances, GCP from n2d-standard and n2d-highmem with Spot VMs and CUDs.

Here is the grid for a large production model representative of payer-side analytics: 20M rows, 400 features, 1000 trees, depth 8, weekly retrain, always-on inference endpoint.

<svg viewBox="0 0 700 320" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; height: auto;">
  <style>
    .grid-title { font: 14px sans-serif; font-weight: 500; fill: #222; }
    .grid-sub { font: 11px sans-serif; fill: #888; }
    .grid-cell-label { font: 12px sans-serif; fill: #444; }
    .grid-cell-value { font: 13px sans-serif; font-weight: 500; fill: #222; }
    .grid-axis { font: 12px sans-serif; font-weight: 500; fill: #444; }
    .grid-pct { font: 11px sans-serif; fill: #1D9E75; }
  </style>
  <text class="grid-title" x="20" y="24">Annual compute cost: 20M x 400, weekly retrain, always-on endpoint</text>
  <text class="grid-sub" x="20" y="42">Single workload, three clouds, three maturity tiers. Lower is better.</text>
  <g transform="translate(20, 70)">
    <text class="grid-axis" x="120" y="0" text-anchor="middle">AWS</text>
    <text class="grid-axis" x="330" y="0" text-anchor="middle">Azure</text>
    <text class="grid-axis" x="540" y="0" text-anchor="middle">GCP</text>
    <g transform="translate(0, 20)">
      <rect x="40" y="0" width="160" height="50" fill="#f5f5f5" stroke="#ccc" stroke-width="0.5"/>
      <text class="grid-cell-value" x="120" y="30" text-anchor="middle">$1,086/yr</text>
      <rect x="250" y="0" width="160" height="50" fill="#f5f5f5" stroke="#ccc" stroke-width="0.5"/>
      <text class="grid-cell-value" x="330" y="30" text-anchor="middle">$927/yr</text>
      <rect x="460" y="0" width="160" height="50" fill="#f5f5f5" stroke="#ccc" stroke-width="0.5"/>
      <text class="grid-cell-value" x="540" y="30" text-anchor="middle">$910/yr</text>
      <text class="grid-axis" x="35" y="30" text-anchor="end">Crawl</text>
    </g>
    <g transform="translate(0, 80)">
      <rect x="40" y="0" width="160" height="50" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
      <text class="grid-cell-value" x="120" y="30" text-anchor="middle">$679/yr</text>
      <rect x="250" y="0" width="160" height="50" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
      <text class="grid-cell-value" x="330" y="30" text-anchor="middle">$513/yr</text>
      <rect x="460" y="0" width="160" height="50" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
      <text class="grid-cell-value" x="540" y="30" text-anchor="middle">$517/yr</text>
      <text class="grid-axis" x="35" y="30" text-anchor="end">Walk</text>
    </g>
    <g transform="translate(0, 140)">
      <rect x="40" y="0" width="160" height="50" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
      <text class="grid-cell-value" x="120" y="30" text-anchor="middle">$502/yr</text>
      <rect x="250" y="0" width="160" height="50" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
      <text class="grid-cell-value" x="330" y="30" text-anchor="middle">$362/yr</text>
      <rect x="460" y="0" width="160" height="50" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
      <text class="grid-cell-value" x="540" y="30" text-anchor="middle">$384/yr</text>
      <text class="grid-axis" x="35" y="30" text-anchor="end">Run</text>
    </g>
    <g transform="translate(0, 210)">
      <text class="grid-pct" x="120" y="0" text-anchor="middle">Crawl to Run: 54% off</text>
      <text class="grid-pct" x="330" y="0" text-anchor="middle">Crawl to Run: 61% off</text>
      <text class="grid-pct" x="540" y="0" text-anchor="middle">Crawl to Run: 58% off</text>
    </g>
  </g>
</svg>

The pattern is the headline. Reading across any row (same maturity, different cloud), the three numbers are within 30 percent of each other. Reading down any column (same cloud, different maturity), the numbers move by a factor of 2 to 3. Maturity dominates the cloud choice for compute spend. A Crawl-tier AWS shop and a Crawl-tier Azure shop are both leaving roughly the same money on the table, in roughly the same shape; a Run-tier shop on either captures roughly the same savings.

The Azure column running cheapest at the Run tier is not a marketing recommendation. Azure Reserved Instances at 3-year are published with a deeper discount on compute than AWS Compute Savings Plans (about 60 percent off list versus 50 percent), and the Dasv5 series prices below m7i at the same vCPU and memory. Both of those are conservative working numbers, not the highest marketing figures. The point is not which cloud wins. The point is that the Crawl-to-Run delta within Azure (61 percent) is essentially the same diagnostic as the Crawl-to-Run delta within AWS (54 percent) or GCP (58 percent), and an enterprise reader on any of those three clouds should be asking the same question about their team's tier rather than asking whether to migrate.

Two other examples in the module are worth noting briefly. For a typical small workload (5M rows, 300 features, monthly retrain, daily batch scoring) the grid produces dollar amounts in the single digits per year. The 70-percent reduction from Crawl to Run is real, but going from $6 to $2 in compute is not a planning event. That is the honest finding: most analytics-scale XGBoost workloads have compute as a noise-level line item in TCO, and maturity work on these is not where the return is.

For a memory-bound workload (1 billion rows, 500 features), the Crawl and Walk tiers are infeasible on all three clouds because the workload exceeds the largest single-node instance in each catalog (768 GiB on AWS, 512 GiB on Azure and GCP). Only the Run tier (multi-node capable) handles it. In that case maturity is not an optimization knob. It is the gate that determines whether the workload runs at all.

## Lock-in is not in the rate card

The cost asymmetry that does not appear in the comparison grid is the load-bearing one for any enterprise reader. Three categories matter here, with rough order-of-magnitude impact on a hypothetical migration.

Egress is the visible piece and the smallest piece. AWS S3 internet egress is $0.09 per GB, Azure ADLS is $0.0875 per GB, GCP GCS is $0.12 per GB. For a 5 TB training dataset the one-time egress cost to move clouds is on the order of $450 to $600. That is real money but is dwarfed by the rest.

Data gravity is the data warehouse layer above object storage. An organization on AWS with Glue catalogs and Redshift, or Azure with Synapse and Fabric, or GCP with BigQuery, has a non-portable layer of joins, ETL pipelines, dashboards, and downstream consumers built on those primitives. Re-platforming that layer is a multi-quarter engineering project even before considering retraining the analysts who use it. The same anchor that motivates the ETL multiplier in the [original post's TCO model](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/#from-marginal-compute-to-annual-tco) applies with extra force here: data-pipeline costs are doubly hidden in a cloud-comparison conversation that focuses on training compute alone.

Identity gravity is the hardest piece to estimate because it does not appear as a direct cost. An organization running on Entra ID with conditional access policies, SSO integrations, and on-prem AD trust does not move that to AWS IAM in a quarter. Workload Identity Federation across clouds works as a bridge, but the operational cost of maintaining two identity systems is non-zero and the security-review cost of doing so in regulated industries is substantial.

The honest enterprise read on a multi-cloud cost comparison: if the rate-card delta is below 20 percent, lock-in costs swamp the savings, and the right move is to mature on the cloud you are on. That is the case in all three examples in the new module. The path to compute savings goes through your existing cloud's discount mechanisms, not through migration.

## Using the new module

The new `cloud_maturity.py` module exposes three pieces:

A `CloudCatalog` dataclass with three pre-built instances: `AWS` (m7i and r7i, EC2 Spot factor 0.30, Savings Plan 1yr 0.70, Savings Plan 3yr 0.50), `AZURE` (Dasv5 and Easv5, Azure Spot factor 0.35, Reserved Instance 1yr 0.60, Reserved Instance 3yr 0.40), and `GCP` (n2d-standard and n2d-highmem, Spot VM factor 0.30, CUD 1yr 0.63, CUD 3yr 0.45). Each catalog also carries a `lock_in_hooks` field that surfaces the egress, identity, and data-gravity hooks for that cloud as a reminder that the rate-card comparison is not the full comparison.

A `MaturityProfile` dataclass with three pre-built instances: `CRAWL` (no spot, no commitments, no multi-node), `WALK` (spot for training and batch, 1-year commitment for always-on, no multi-node), and `RUN` (spot, 3-year commitment, multi-node capable). Each profile includes an `unlock_next` field that names the operational capabilities required to climb to the next tier.

A `compare()` function that takes a `TrainingSpec` and optional `InferenceSpec` and returns the full 3x3 grid as a nested dict, plus a `format_comparison()` helper that renders it as the plain-text table shown above. Both accept overrides for which clouds and which maturity tiers to include, so a reader only interested in their own cloud across all three tiers can do `compare(spec, clouds=[AZURE])`.

The module imports the compute math (`estimate_training_seconds`, `estimate_training_memory_gib`, `estimate_inference_throughput`) directly from the original estimator, so the calibration story is unified. Run `--calibrate` on the original estimator to refresh the per-work-unit constant for your CPU; the same constant flows through to the multi-cloud diagnostic.

## What this still does not capture

CPU microarchitecture variance across clouds. Same caveat as the original estimator, larger surface area now. Calibrate on each target environment if precision matters.

Managed-platform premiums. The paper-saver framing remains "without the managed-platform layer," as [originally argued for SageMaker on AWS](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/#why-no-sagemaker). The same operational reasoning extends to Vertex AI on GCP and Azure ML on Azure: instance-type markup, container and SDK lock-in, parallel-platform operational ownership, and the compliance review burden of bringing a new control plane through review. Comparing managed platforms across clouds is a different question with different operational considerations.

Network-bandwidth differences for multi-node training. AWS ENA, Azure Accelerated Networking, and GCP Andromeda all support greater than 25 Gbps on the instance sizes relevant to distributed XGBoost. The Amdahl alpha of 0.20 from the [original distributed-training model](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/#the-compute-model) assumes "good but not best" networking, which is a fair approximation for all three.

Egress costs as a quantitative migration estimate. Discussed narratively here but not modeled. Egress at the rate-card level is straightforward to compute for a known data volume, but lock-in costs are dominated by re-platforming and identity migration which are not.

Engineering labor and program TCO. The cloud-bill comparison above is below the line of what determines program economics; loaded ML-engineer FTE allocations dominate. The math, the working numbers, and the program-vs-cloud-bill distinction are in the [original post's budgeting section](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/#what-this-means-for-budgeting).

## Where this leaves the tool

Paper Saver started as a single-purpose AWS-without-SageMaker estimator and is now three things. The [base estimator and TCO model in the original post](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/) answer the marginal-compute and annual-TCO questions, both on AWS. The new maturity diagnostic answers the cross-cloud, cross-maturity question and is meant to be the first one to run for an enterprise reader trying to figure out what to ask next.

The right entry point depends on the question. For "how much does this one training run cost on AWS spot," use the base estimator. For "what is my annual cloud bill for this model in production," use the TCO model. Both are documented in the [original post](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/). For "given my cloud and my team's maturity, am I leaving compute savings on the table, and what would I need to invest in to capture them," use the new diagnostic. The last one is where most enterprise readers should probably start.

Code, calibration sources, and both posts live at [github.com/zaherkarp/paper-saver](https://github.com/zaherkarp/paper-saver). Pricing constants in the new module are public list rates as of May 2026 and should be re-validated quarterly before quoting externally. Pull requests welcome for refreshed pricing, additional calibration anchors on other CPU microarchitectures, and any maturity-tier criteria worth adding to the model.

## Sources

Pricing pages used for the per-cloud catalogs in `cloud_maturity.py`:

- AWS EC2 on-demand pricing: [instances.vantage.sh](https://instances.vantage.sh) (third-party mirror of AWS list pricing for `m7i.*` and `r7i.*` in us-east-1, Linux on-demand)
- Azure Linux VM pricing: [azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/](https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/) (Dasv5 and Easv5 in East US 2, Linux pay-as-you-go)
- GCP Compute Engine pricing: [cloud.google.com/compute/vm-instance-pricing](https://cloud.google.com/compute/vm-instance-pricing) (n2d-standard and n2d-highmem in us-central1, Linux on-demand)

Discount mechanism documentation:

- AWS Compute Savings Plans: [aws.amazon.com/savingsplans/compute-pricing/](https://aws.amazon.com/savingsplans/compute-pricing/)
- AWS EC2 Spot pricing model: [aws.amazon.com/ec2/spot/pricing/](https://aws.amazon.com/ec2/spot/pricing/)
- Azure Reserved VM Instances: [azure.microsoft.com/en-us/pricing/reserved-vm-instances/](https://azure.microsoft.com/en-us/pricing/reserved-vm-instances/)
- Azure Spot Virtual Machines: [azure.microsoft.com/en-us/products/virtual-machines/spot](https://azure.microsoft.com/en-us/products/virtual-machines/spot)
- GCP Committed Use Discounts (resource-based): [cloud.google.com/compute/cud-analysis-docs/concepts](https://cloud.google.com/compute/cud-analysis-docs/concepts)
- GCP Spot VMs: [cloud.google.com/compute/docs/instances/spot](https://cloud.google.com/compute/docs/instances/spot)

Maturity-model framing: [FinOps Foundation Maturity Assessment](https://www.finops.org/framework/maturity-model/) (Crawl/Walk/Run capability tiers, adapted here to compute-scaling discount realization).

XGBoost benchmark anchor: as documented in the [original post's calibration evidence](/blog/paper-saver-estimating-xgboost-compute-costs-on-aws/#calibration-evidence), the per-work-unit constant default is anchored on Masudahiroto's 2024 DEV Community XGBoost benchmark. Replace with `--calibrate` output for tighter estimates on your own hardware.
