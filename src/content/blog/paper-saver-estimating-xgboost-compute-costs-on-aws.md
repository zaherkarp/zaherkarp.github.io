---
title: "Paper Saver: estimating XGBoost compute costs on AWS without SageMaker"
publishDate: 2026-05-17
description: "A practitioner's working tool for budgeting XGBoost training and inference on AWS, anchored to public benchmarks. Includes the gap between marginal compute cost and realistic annual TCO."
draft: false
tags: [aws, xgboost, mlops, healthcare-analytics, cost-modeling]
---

A common ask: how much will it cost to train this XGBoost model and serve it? Naive answers fail. Cost depends on data shape, hyperparameters, infrastructure choices, and whether you mean the marginal compute cost of one training run or the realistic annual cost of keeping a production model running. Most attempts at answering conflate these and produce numbers that are either implausibly low or pulled from thin air.

Paper Saver is a back-of-the-envelope tool for both. The name is the joke: it replaces the napkin or scratch-paper math an analyst would otherwise scribble to budget a model, and the saved-trees pun lands twice (trees as in paper, trees as in the gradient-boosted kind whose cloud spend the tool is sizing).

The code lives at `https://github.com/zaherkarp/paper-saver` and runs as a self-contained uv script.

## Scope

AWS only. No SageMaker. CPU only. XGBoost with `tree_method='hist'`, which has been the default since 1.5 and is what almost all CPU production deployments use. The model targets analytics-scale workloads (a few million to a few hundred million rows, up to a few thousand features) which is where most healthcare, payer, and actuarial XGBoost lives.

## The compute model

For single-node training, wall time is dominated by the product of rows, features, and trees. Memory is dominated by rows times features after histogram quantization. So if you know only N and P, you have the two biggest cost levers. Tree count and depth default to 500 and 6 (canonical XGBoost defaults), and the formula is:

```
work_units = N * P * n_trees * (depth / 6) * early_stopping_factor
single_core_seconds = work_units * SECONDS_PER_WORK_UNIT_TRAIN * 1.10
wall_seconds = single_core_seconds / vcpu ** 0.75
```

The 0.75 exponent on vCPU count reflects sub-linear scaling: XGBoost's histogram method gets diminishing returns past about 16 cores due to memory bandwidth and synchronization. The 1.10 multiplier covers the validation set used for early stopping.

Memory follows the same shape:

```
raw_bytes = N * P  (1 byte per cell after histogram quantization)
total_gib = 3 * raw_bytes / 1 GiB
floor = 4 GiB  (Python + libraries + overhead)
```

The 3x multiplier covers the original DataFrame, the DMatrix, the validation set, the model itself, and Python runtime overhead.

For multi-node distributed training, the model adds an Amdahl's-law speedup with alpha = 0.20:

```
speedup(N) = N / (1 + (N - 1) * 0.20)
```

This gives a max speedup of 5x no matter how many nodes you add, which matches empirical experience that distributed XGBoost on CPU plateaus around 8 to 16 nodes due to histogram all-reduce overhead. Memory partitions across nodes (each node holds roughly 1/N of the data, plus a 2 GiB baseline for comm buffers), and cost scales linearly with N because all nodes run concurrently and you pay for each.

## Calibration evidence

The per-work-unit compute constant defaults to 1.0e-8 seconds. Two public benchmarks anchor it. The cleaner one is Masudahiroto's 2024 DEV Community post: 1M rows times 200 features times 100 trees on 2-vCPU Google Colab in 96 seconds wall time. Working back through the formula implies the constant should be about 8.1e-9 seconds per work unit. The HackerNoon Amex Default Prediction benchmark from 2025 (5.5M rows times 313 features on M3 Pro 12-core CPU in 27 minutes) implies about 4.0e-9 if you assume n_trees around 1500.

The default sits conservatively above both anchors so the estimator over-budgets rather than under-budgets. The repo ships with a `--calibrate` command that runs a real XGBoost benchmark on your CPU and prints the empirically-calibrated constant. Run it once before trusting dollar figures for real budgeting.

For distributed scaling, the alpha = 0.20 default is anchored on GitHub issue dmlc/xgboost#10853, which documents a practitioner getting worse performance from a Dask cluster with 3x more RAM and 4x more cores than from a single big EC2 instance training on 50 million rows. The takeaway: distributed XGBoost has substantial overhead, and the primary reason to use it is memory constraints rather than wall-time speedup.

## Pricing anchors

m7i (general purpose, 4 GiB per vCPU) and r7i (memory optimized, 8 GiB per vCPU) families from us-east-1, May 2026 pricing pulled from instances.vantage.sh. AWS documentation explicitly recommends M-family over C-family for XGBoost because the workload is memory-bound, not compute-bound.

Spot discount of 70 percent off on-demand, factor 0.30. This is anchored on the EC2 Spot Workshop documented run (68.8 percent actual savings) and the Cinnamon AI AWS customer case study (70 percent reduction). The "up to 90 percent" you'll see in AWS marketing is the ceiling, not the working number.

For always-on inference endpoints, spot is risky because interruptions break real-time serving. The realistic discount path is a 1-year Compute Savings Plan at about 30 percent off on-demand.

## Why no SageMaker

A few common reasons a tech stakeholder vetoes SageMaker. ml.* instance markup of 15 to 40 percent over equivalent EC2. Lock-in to SageMaker-specific containers and SDK conventions. Operational ownership of a parallel ML platform that the team has to learn and maintain. Compliance review burden for managed services handling regulated data. Even with the AWS HIPAA BAA covering SageMaker, healthcare organizations that already have a worked review for EC2 in a locked-down VPC often don't want to re-run that review for a different control plane.

Equivalent alternatives without SageMaker: AWS Batch on EC2 Spot (closest functional substitute, no premium), AWS Batch Multi-Node Parallel Jobs for distributed training, ECS or EKS scheduled tasks if a container platform already exists, AWS Lambda for low-volume inference, Fargate for scheduled batch scoring. The same 70 percent spot discount applies because the underlying capacity pool is identical.

## The single-run cost picture

For a typical Medicare member-level Stars risk model (5M rows, 300 features, 1000 trees, depth 8, one-hour training budget), the estimator returns about $0.18 on spot for a single training run on m7i.4xlarge. Inference of 500K rows in a five-minute batch window costs pennies. These numbers are correct but easy to misread. They are marginal compute costs, not the cost of running a model in production.

Here is the full spread across workload types, all on spot:

<svg viewBox="0 0 700 320" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; height: auto;">
  <style>
    .bar-label { font: 12px sans-serif; fill: #444; }
    .bar-value { font: 11px sans-serif; fill: #222; }
    .axis { font: 10px sans-serif; fill: #888; }
    .title { font: 14px sans-serif; font-weight: 500; fill: #222; }
    .legend-text { font: 11px sans-serif; fill: #555; }
  </style>
  <text class="title" x="20" y="24">Monthly cost on AWS spot, by workload type</text>
  <g transform="translate(0, 40)">
    <rect x="200" y="10" width="380" height="32" fill="#f5f5f5"/>
    <text class="bar-label" x="195" y="30" text-anchor="end">Single retrain (1M x 200)</text>
    <rect x="200" y="10" width="2" height="32" fill="#888780"/>
    <text class="bar-value" x="210" y="30">$0.005</text>
    <rect x="200" y="50" width="380" height="32" fill="#f5f5f5"/>
    <text class="bar-label" x="195" y="70" text-anchor="end">Daily batch scoring (30d)</text>
    <rect x="200" y="50" width="3" height="32" fill="#888780"/>
    <text class="bar-value" x="210" y="70">$0.07</text>
    <rect x="200" y="90" width="380" height="32" fill="#f5f5f5"/>
    <text class="bar-label" x="195" y="110" text-anchor="end">Large training (50M x 500)</text>
    <rect x="200" y="90" width="80" height="32" fill="#378ADD"/>
    <text class="bar-value" x="290" y="110">$5.72</text>
    <rect x="200" y="130" width="380" height="32" fill="#f5f5f5"/>
    <text class="bar-label" x="195" y="150" text-anchor="end">100-config HPO sweep</text>
    <rect x="200" y="130" width="116" height="32" fill="#378ADD"/>
    <text class="bar-value" x="326" y="150">$8.44</text>
    <rect x="200" y="170" width="380" height="32" fill="#f5f5f5"/>
    <text class="bar-label" x="195" y="190" text-anchor="end">Distributed 500M (8 nodes)</text>
    <rect x="200" y="170" width="195" height="32" fill="#378ADD"/>
    <text class="bar-value" x="405" y="190">$14.55</text>
    <rect x="200" y="210" width="380" height="32" fill="#f5f5f5"/>
    <text class="bar-label" x="195" y="230" text-anchor="end">Always-on endpoint (30d)</text>
    <rect x="200" y="210" width="290" height="32" fill="#378ADD"/>
    <text class="bar-value" x="500" y="230">$21.77</text>
  </g>
  <g transform="translate(20, 290)">
    <rect x="0" y="0" width="10" height="10" fill="#888780"/>
    <text class="legend-text" x="16" y="9">local fits</text>
    <rect x="100" y="0" width="10" height="10" fill="#378ADD"/>
    <text class="legend-text" x="116" y="9">cloud earns it</text>
  </g>
</svg>

The pattern is bimodal. Single-job training and daily batch scoring are pennies. Then there is a roughly 100x jump to scenarios that actually justify cloud spend. There is no smooth gradient between them. The trigger for the gray-to-blue transition is one of three things: memory beyond workstation RAM, HPO parallelism, or always-on serving with real uptime requirements. Everything else is a wash, and for most analytics shops with a decent workstation, "train locally and push flat files to cloud" is the right architecture.

## Where the threshold actually lives

The memory side is easier to reason about because it is a hard constraint:

<svg viewBox="0 0 700 280" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; height: auto;">
  <style>
    .zone-title { font: 14px sans-serif; font-weight: 500; }
    .zone-text { font: 12px sans-serif; fill: #444; }
    .zone-sub { font: 11px sans-serif; fill: #666; }
  </style>
  <rect x="40" y="20" width="620" height="70" rx="8" fill="#f1efe8" stroke="#888780" stroke-width="0.5"/>
  <text class="zone-title" x="60" y="44" fill="#444441">Local fits</text>
  <text class="zone-text" x="60" y="62">Under ~50M rows. Workstation with 64 to 128 GiB RAM.</text>
  <text class="zone-sub" x="60" y="78">100K x 80, 1M x 200, 5M x 300 all comfortable. Train locally, push outputs to cloud.</text>
  <rect x="40" y="100" width="620" height="70" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
  <text class="zone-title" x="60" y="124" fill="#0C447C">Single cloud node</text>
  <text class="zone-text" x="60" y="142">50M to ~500M rows. Memory exceeds typical workstation.</text>
  <text class="zone-sub" x="60" y="158">50M x 500 fits r7i.16xlarge (512 GiB). Cloud earns it on the memory dimension alone.</text>
  <rect x="40" y="180" width="620" height="70" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
  <text class="zone-title" x="60" y="204" fill="#085041">Distributed required</text>
  <text class="zone-text" x="60" y="222">Above ~500M rows. No single AWS box holds enough RAM.</text>
  <text class="zone-sub" x="60" y="238">500M x 200 needs 8+ nodes via AWS Batch Multi-Node Parallel or Dask cluster.</text>
</svg>

The exact row count shifts with feature width. A 64 GiB workstation can hold roughly 64 divided by (3 times P times 1 byte) million rows in DMatrix memory. At 80 features that is 270M rows. At 500 features it is 43M rows. At 1000 features it is 21M rows. So the "under 50M rows" boundary above is a rough lower bound for healthcare-typical feature widths.

The other two triggers are independent of memory. An HPO sweep that needs 20 to 100 parallel boxes is a parallelism trigger: a workstation can run those configs sequentially but a sweep that takes three days locally takes 90 minutes in cloud. An always-on serving requirement is an uptime trigger: workstations do not stay on with a load balancer in front. Each of these triggers independently moves a workload from gray to blue in the chart above, even when memory is comfortably within local bounds.

## From marginal compute to annual TCO

Here is where the original framing falls apart. The estimator above measures `xgb.train` wall time multiplied by a spot rate. That captures maybe 3 to 5 percent of what a production XGBoost program actually costs to keep running. Anyone who has paid an AWS bill for a production ML deployment will look at "$0.18 per training run" and know that number cannot be right at the program level.

The industry literature is consistent on this. ModelOp, an MLOps vendor that publishes pharma-specific benchmarks in PharmExec, gives a working range of $25,000 to $100,000 per use case annually for big pharma ML programs. A 2025 Mondaysys healthcare TCO study found that one provider discovered 63 percent of their ML expenses came from data pipeline optimization and GPU cluster management, costs that were absent from vendor proposals. The same study reported that 68 percent of organizations underestimate data preparation and retraining costs. Sumatosoft's ongoing-cost framework breaks annual TCO down by category and lands on 17 to 30 percent of initial development cost per year, with up to 50 percent in the worst case. Glean's TCO framework is in the same range: 15 to 25 percent maintenance, $20K to $60K in infrastructure annually per system.

The gap is real and predictable. Training compute is the thing everyone measures and the thing that matters least to annual TCO. The seven or eight cost categories that dominate are:

ETL and feature pipeline compute, which runs continuously to produce the features the model consumes. In healthcare analytics with member-level joins this is typically 3 to 8 times the cost of training compute itself.

Cluster idle overhead, which is the fair share of an always-on EKS or EMR cluster that exists 24/7 whether or not your model is training. Industry rule of thumb is 30 to 60 percent average utilization on always-on ML clusters, so the allocated cost is roughly 1.5 to 3 times the marginal training cost.

Storage of training data and model artifacts. S3 Standard at $0.023 per GB-month, and you typically keep three copies (raw, processed, intermediate) plus model versions, eval reports, and logs.

Inference serving, especially for always-on endpoints which carry 24/7 instance costs and cannot use spot pricing.

Monitoring and observability. CloudWatch logs and metrics, Datadog or equivalent APM, model drift monitoring through Arize, Fiddler, WhyLabs, or homegrown. Realistic floor is about $3K to $5K per production model per year.

Compliance and audit infrastructure. Audit trail storage, access review tooling, change management workflows, security scanning. Higher in regulated industries.

Data egress. Pulling raw EHR data, scoring outputs, and model artifacts in and out of S3 across regions or to external customers. At $0.09 per GB this adds up.

The repo includes a second tool that wraps the base estimator and adds these categories with industry-anchored defaults that can be overridden. For a typical Medicare member-level Stars model (5M members, 300 features, monthly retrain, daily batch scoring), it produces the breakdown below.

<svg viewBox="0 0 700 380" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; height: auto;">
  <style>
    .tco-title { font: 14px sans-serif; font-weight: 500; fill: #222; }
    .tco-label { font: 12px sans-serif; fill: #444; }
    .tco-value { font: 12px sans-serif; fill: #222; }
    .tco-pct { font: 11px sans-serif; fill: #888; }
    .total-line { font: 13px sans-serif; font-weight: 500; fill: #222; }
  </style>
  <text class="tco-title" x="20" y="24">Annual TCO breakdown: large production model, daily retrain, always-on endpoint</text>
  <text class="tco-pct" x="20" y="42">$33,525/year, training compute is 6.9% of total</text>
  <g transform="translate(20, 60)">
    <rect x="0" y="0" width="660" height="32" fill="#f5f5f5"/>
    <text class="tco-label" x="10" y="20">ETL and feature pipelines</text>
    <rect x="280" y="0" width="280" height="32" fill="#378ADD"/>
    <text class="tco-value" x="570" y="20">$13,856</text>
    <text class="tco-pct" x="630" y="20">41.3%</text>
    <rect x="0" y="40" width="660" height="32" fill="#f5f5f5"/>
    <text class="tco-label" x="10" y="60">Cluster idle overhead</text>
    <rect x="280" y="40" width="140" height="32" fill="#1D9E75"/>
    <text class="tco-value" x="430" y="60">$6,928</text>
    <text class="tco-pct" x="630" y="60">20.7%</text>
    <rect x="0" y="80" width="660" height="32" fill="#f5f5f5"/>
    <text class="tco-label" x="10" y="100">Monitoring and observability</text>
    <rect x="280" y="80" width="80" height="32" fill="#7F77DD"/>
    <text class="tco-value" x="370" y="100">$4,000</text>
    <text class="tco-pct" x="630" y="100">11.9%</text>
    <rect x="0" y="120" width="660" height="32" fill="#f5f5f5"/>
    <text class="tco-label" x="10" y="140">Compliance and audit infra</text>
    <rect x="280" y="120" width="80" height="32" fill="#888780"/>
    <text class="tco-value" x="370" y="140">$4,000</text>
    <text class="tco-pct" x="630" y="140">11.9%</text>
    <rect x="0" y="160" width="660" height="32" fill="#f5f5f5"/>
    <text class="tco-label" x="10" y="180">Training compute (annualized)</text>
    <rect x="280" y="160" width="48" height="32" fill="#D85A30"/>
    <text class="tco-value" x="338" y="180">$2,309</text>
    <text class="tco-pct" x="630" y="180">6.9%</text>
    <rect x="0" y="200" width="660" height="32" fill="#f5f5f5"/>
    <text class="tco-label" x="10" y="220">Storage</text>
    <rect x="280" y="200" width="35" height="32" fill="#BA7517"/>
    <text class="tco-value" x="325" y="220">$1,706</text>
    <text class="tco-pct" x="630" y="220">5.1%</text>
    <rect x="0" y="240" width="660" height="32" fill="#f5f5f5"/>
    <text class="tco-label" x="10" y="260">Inference serving</text>
    <rect x="280" y="240" width="14" height="32" fill="#D4537E"/>
    <text class="tco-value" x="304" y="260">$618</text>
    <text class="tco-pct" x="630" y="260">1.8%</text>
    <rect x="0" y="280" width="660" height="32" fill="#f5f5f5"/>
    <text class="tco-label" x="10" y="300">Data egress</text>
    <rect x="280" y="280" width="3" height="32" fill="#5F5E5A"/>
    <text class="tco-value" x="293" y="300">$108</text>
    <text class="tco-pct" x="630" y="300">0.3%</text>
  </g>
</svg>

The training compute slice in orange is the thing the original estimator measures. Everything else is what determines your actual annual bill. The pattern holds across all three worked examples in the repo. For a small POC at $8,200 per year, training compute is essentially zero. For the typical Stars model at $8,300 per year, training compute is $2.22 against $8,000 in monitoring and compliance flat costs. For the large production model at $33,500 per year, training is 6.9 percent. In no realistic scenario is training compute the cost driver.

## What this means for budgeting

If you are sizing a new XGBoost workload in healthcare or insurance, here is what to take from the two tools together.

For the marginal compute cost of a single training run, use the base estimator. The numbers are honest and will keep you from over-budgeting one training job to thousands of dollars when it actually costs cents.

For annual budgeting of a production model, use the TCO tool. The realistic range is $8K to $35K per cloud-bill TCO per model per year, scaling with how much of an always-on infrastructure stack the model occupies. ModelOp's $25K to $100K range from PharmExec is the right sanity check; if your TCO model produces numbers outside that range, double-check your overrides.

For program TCO (cloud bill plus engineering labor), add an FTE allocation on top. A loaded ML engineer is $200K to $400K per year, and a single production model in regulated industries typically needs 0.2 to 1.0 FTE depending on its criticality. That alone is $50K to $400K per model per year, dwarfing the cloud bill. The repo's TCO tool is explicitly cloud-bill TCO, not program TCO.

## What the model still does not capture

GPU training, where the Amex benchmark shows 27 minutes on CPU becoming 35 seconds on A100. If your workload is large enough to benefit, the economics flip and a separate model is needed.

S3 I/O wall time. For typical analytics workloads this is negligible (a few minutes to pull a few GB), but for TB-scale workloads it can dominate.

Categorical feature handling overhead. XGBoost's native categorical support is fast but high-cardinality categoricals add memory and time that the linear N times P model does not capture.
