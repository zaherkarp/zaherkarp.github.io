---
title: "CI/CD for SQL Developers: Watching It Land, and a Project to Practice On"
description: "The pipeline shipped the change. Friday morning the dashboard went red. Observability closes the loop. Plus a weekend project for the SQL developer who wants to build the whole series end to end."
publishDate: 2026-05-20
tags: ["healthcare-data", "ci-cd", "sql", "data-engineering", "observability", "dbt"]
---

# CI/CD for SQL Developers: Watching It Land, and a Project to Practice On

The pipeline did its job. The pull request was reviewed, the migration applied to QA, the smoke test passed, the release manager approved the production gate, the change landed Tuesday night. Friday morning the head of analytics opens the weekly leadership dashboard and the composite quality score has dropped by twenty percent. Nothing in the pipeline knows this. Nothing in the deploy log flags it. The change shipped clean. The change was also wrong, and it took the business three days to notice.

This is the gap the first three articles in this series did not close. The pipeline knows whether the SQL is syntactically valid, whether the migration applies, whether the unit tests pass, whether the smoke test against a known sample comes back as expected. It does not know whether the dashboard the executive team looks at on Monday is right. Closing that gap is what observability is for, and it is the last thing the pipeline needs to be useful.

## The Observability Gap

CI checks that the SQL is valid. CD checks that the migration applies, and that whatever you remembered to assert in the smoke test still asserts. Both of those are bounded checks. They cover the things the team thought to write down. The interesting failures are unbounded. They are the failures where the syntax was fine, the migration applied, the smoke test came back green, and the dashboard is still wrong because a join started double-counting, or because a denominator went to zero on a population segment nobody had a fixture for, or because the upstream feed dropped one CSV file at 2 AM and the pipeline cheerfully aggregated zero rows.

The smoke test is necessary. It is not sufficient. A smoke test is an assertion about a specific input and a specific expected output. It catches the regressions in logic that you knew to look for. It does not catch the regressions in logic that you did not know to look for. It does not catch the regressions in data, which is most of them.

What is missing is the thing that watches what the change actually did, in production, after it landed. That thing has three layers, and a SQL team that wants to ship with confidence needs all three.

## Three Layers

The first layer is **infrastructure observability**. The database doing its database job: query duration, lock waits, replica lag, connection-pool depth, deadlocks per minute, error rates by query class. Most of this comes for free with the cloud provider's database product, or from a Datadog, Prometheus, or Grafana stack pointed at the database. The signals are noisy and the alerts are easy to misconfigure into uselessness, but the baseline is necessary. If the deploy lands and the query running the dashboard is now taking thirty seconds instead of three, that is an infrastructure signal, and it shows up here.

The second layer is **data observability**. This is the layer that answers questions the infrastructure cannot. Did today's ETL load complete? Is the row count for today within ten percent of yesterday's? Did the daily distinct-beneficiary count stay flat when it should have grown? Is the latest partition's date what it should be? These are checks against the shape of the data, not against the performance of the database. dbt has source-freshness tests and column-level tests that cover most of this. Great Expectations is the standalone tool that covers the same ground. The data-observability category, with vendors like Monte Carlo and Bigeye, is what you buy when you want this without writing the YAML yourself. The point is that the checks run on a schedule against production, not on a fixture in CI, and they alert when something the team did not think to assert about has nonetheless changed.

The third layer is **business-metric observability**. This is the layer that the head of analytics opens on Monday. The dashboard with the composite Star Rating, or the readmission rate, or the average days in accounts receivable. The right pattern is to instrument the metric the business actually looks at, with its own alerting that fires when the number moves more than the team thinks is plausible. The threshold is not zero. The threshold is "more than yesterday's number plus the daily variance we have measured." When the threshold trips, somebody looks. The alert does not have to be loud. It has to be timely. A drift caught on Friday before the Monday meeting is a save. A drift caught at the Monday meeting is a story.

The three layers belong to different owners. Infrastructure is on the database team or the platform team. Data observability is on the data engineering team. Business-metric observability is on the analytics team, with the business owner on the alert. The team that tries to put all three on one person ends up with one well-monitored layer and two layers that nobody is looking at.

## Closing the Loop

The point of observability is not the alerts themselves. The point is that every alert can be traced back to a deploy.

When an infrastructure alert fires, the question is "what changed?" The git log has the answer, if the change discipline from the first two articles is in place. The pull request history is the audit trail of changes. The observability stack is the audit trail of consequences. When you can lay one over the other, the time from "the dashboard is red" to "this is the deploy that broke it" drops from hours of forensic work to minutes of scanning a list.

The closing-the-loop pattern, in practice, is a Slack channel, or a wiki page, or a chat thread, where every deploy is announced when it goes out, and where every alert posts a link back to the deploy that immediately preceded it. The mechanism is not the point. The pairing is. Deploys without alerting are shipping in the dark. Alerting without deploy context is firefighting without a map. The two together are what makes the pipeline honest, because the pipeline can now tell you whether the change worked, not just whether it shipped.

The team that gets this right finds that the smoke test starts to drift toward whatever the observability stack is alerting on. The smoke test learns. A drift in the daily distinct-beneficiary count becomes a smoke-test assertion. A jump in lock waits during the daily batch becomes a query-plan check in the next pipeline. The pipeline absorbs what observability discovers, and the next deploy is a little safer than the last one. That is the loop.

## Lessons from the Series

Four articles in, the things that matter are short.

**Version control is the substrate, not the goal.** The goal is changes you can review, attribute, and roll back. Pull requests are the discussion layer where the review happens; the version-control system is what makes the discussion possible. Without it, the change is a phone call.

**CI catches the dumb mistakes. Tests catch the logic mistakes. Neither catches the data mistakes.** Linting catches the casing drift. Migration validation catches the migration that runs on an empty schema and dies on a real one. Unit tests catch the CASE expression that returns the wrong bucket. None of these catch the day the upstream feed sends a malformed file. That is what data observability is for. The three categories of check are not interchangeable. A team with great unit tests and no data checks ships clean code that produces wrong numbers.

**CD is policy, not philosophy.** Continuous delivery and continuous deployment are different choices for different blast radii. Customer-facing OLTP gets delivery, with a human in the loop. Internal warehouses get deployment, on automation. Treating one as more advanced than the other is a category error. The mature team picks the one that matches the cost of being wrong.

**Schema changes are boring on purpose.** Expand, migrate, contract is three deploys where one would do, because three deploys is what it takes to keep the schema in a state where every running version of the application is valid. The boring version saves you on the day the naive version would have made the pager ring.

**Observability is what makes the pipeline honest.** Without it, you have shipped a change you cannot evaluate. The pipeline says it landed. The observability stack tells you whether it should have. The first is necessary. The second is what closes the loop.

The single sentence under all five of these is the same: the discipline is more valuable than the tooling. The team that runs a clean process with a mid-tier stack ships better than the team with the best stack and no process. Tooling is a force multiplier. The force is the discipline.

## A Project to Practice On

Reading the four articles gets you to nodding. Building the project gets you to ready. Here is one shaped to exercise everything in the series, on a laptop, with public data, over two or three weekends.

The dataset is **CMS Hospital Care Compare** for the first build, and **CMS SynPUF** for the second if you want to feel the lock problem. Care Compare publishes hospital-level quality measures, around five thousand hospitals across fifty-ish measures across a few years. Small enough to fit on a laptop. Real enough to be interesting. Structured enough that you will write the same kind of queries you would write at work. SynPUF is the Synthetic Medicare Public Use Files based on 2008 through 2010 claims, several gigabytes of claims-shaped data across roughly two million synthetic beneficiaries. Care Compare gets you through the pipeline. SynPUF gets you to the row-count where a naive `ALTER TABLE` actually locks the table long enough to notice.

The stack is **Postgres in Docker** for the database, **Flyway** for migrations, **sqlfluff** for the linter, **pgTAP** for unit tests, **GitHub Actions** for the pipeline, and **dbt** for the transformation layer and the source-freshness checks. Every piece is free. Every piece runs on a laptop. Every piece is something you would plausibly see in a healthcare-data shop.

The build is seven steps.

**One.** Stand up Postgres in a Docker container with a volume. Load the Care Compare CSV files into a `raw` schema with a small Python or shell loader. The point of step one is to have a database with a non-trivial amount of real data in it that you can query.

**Two.** Put the schema in a Flyway project, source-controlled in a fresh GitHub repository. Every table is a migration. The migration that creates `raw.hospital` is `V1__create_raw_hospital.sql`. Re-run Flyway in CI to prove the migrations apply against an empty database.

**Three.** Wire up GitHub Actions. The pipeline runs on every push. It spins up a Postgres service container, applies the Flyway migrations against the fresh database, runs sqlfluff against the SQL files in the repo, and runs pgTAP tests against the migrated schema. Three jobs, one workflow file, all of it in the free tier.

**Four.** Write one derived metric. The thirty-day readmission rate is the obvious choice; the heart-attack mortality measure is the simpler one. Build it as a SQL view on top of the raw tables, then promote it to a stored procedure with a clear contract. Write three or four pgTAP tests against a small handwritten fixture: one row that should be included, one that should be excluded, one edge case. Watch the tests run in CI and fail when you change the procedure's logic.

**Five.** Do a schema change with the EMC pattern. Rename a column the loader is writing to, across three or four pull requests, the way the third article walked through. The point is not that the rename matters. The point is that you do the rename across multiple deploys against a real running database, and you feel the difference between the naive version and the EMC version. If you are running SynPUF instead of Care Compare, do this on the claims table and watch the difference in lock duration. Do it once the naive way to feel it.

**Six.** Add the dbt layer on top. Models for the derived metric, source-freshness tests against the raw tables, schema tests on the model columns. Configure dbt to run on a cron in GitHub Actions, against the database, and to fail the workflow when freshness or row-count drifts past a threshold. That is the data-observability layer from earlier in this article, in fifty lines of YAML.

**Seven.** Build a tiny dashboard. One number, one history line, one alert. Streamlit or a small static page hitting the database is fine. Add a daily cron that compares today's number to yesterday's and posts to a webhook when the delta exceeds a threshold you have measured. That is the business-metric observability layer, in fifty more lines of Python.

When you finish the seven steps, you have a repository that contains everything the four articles described, with public data, on free tooling, that you built. The job description on a CI/CD-for-SQL position is now something you can describe in your own voice, with examples from your own work. The teams that are hiring for this are mostly looking for people who can say "I have built it" instead of "I have read about it." The repo is the proof. The README is the cover letter.

A note on scope. The first build should take a weekend. It will take three weekends. That is normal. The first weekend is Docker and the loader, the second is the pipeline and tests, the third is dbt and the dashboard. If you try to do all of it in one sitting, you will skip the parts that matter and end up with a repository that demonstrates that you can copy a tutorial. The repository that matters is the one where you got stuck on something the tutorials did not cover, and worked through it.

## Close

The series is done. Four articles, one pattern. Put your SQL in version control. Build a pipeline that runs every time someone pushes. Change the schema in three deploys, not one. Watch the dashboard after it lands, and connect what it shows you back to what you shipped.

The articles are the map. The project is the work. If you build the project, you will know whether the map is right, which is the only review of writing that actually matters.
