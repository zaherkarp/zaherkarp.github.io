---
title: "CI/CD for SQL Developers: Changing the Schema Without Locking the App Out"
description: "The ALTER TABLE at nine in the morning that does not end. The rename that breaks the app between deploys. The pattern that fixes both is called expand, migrate, contract, and it costs three deploys where one would do."
publishDate: 2026-05-19
tags: ["healthcare-data", "ci-cd", "sql", "data-engineering", "schema-changes", "migrations"]
---

# CI/CD for SQL Developers: Changing the Schema Without Locking the App Out

Nine in the morning. A developer pushes a one-line migration to the main branch. The pipeline picks it up, applies it to dev, applies it to QA, runs the smoke tests, requests the production approval. The release manager clicks the button. The migration starts running against the customer-facing table that holds two hundred million rows of claims activity. It does not finish. The first long-running query waits. Then the second one. Within ninety seconds the application's connection pool is full of sessions waiting on a single `ALTER TABLE`. The pager goes off. The developer is on a different team now.

The change was real. It needed to ship. The migration was correct in every way except the one that mattered, which is that it could not be applied against a table the application was actively using. This is the failure mode that makes people frightened of schema changes. It is also the failure mode that has a known answer.

## Why Naive Migrations Break

Two things go wrong, and they go wrong together. The first is at the database level. The second is at the application level.

At the database level, most DDL takes a lock. Adding a column, changing a column's type, adding an index, adding a constraint: each of them needs to read or rewrite metadata, and most engines need to serialize that against concurrent reads and writes for at least part of the work. The exact lock varies by engine. MySQL's InnoDB takes a shared metadata lock for some operations and a table-level lock for others. Postgres takes an `ACCESS EXCLUSIVE` lock that blocks everything for the duration of the change. SQL Server can do many operations online with `WITH (ONLINE = ON)` on the Enterprise edition, and offline everywhere else. The trend across all engines has been toward online DDL. The reality, even with online DDL, is that the operation is doing work, that work consumes I/O and CPU, and the application notices.

A short lock against a small table is invisible. A long lock against a large table is not. The lock that scales with row count is the one that ends careers. An `ADD COLUMN` with a default value, on most engines, has to write the default into every existing row before it can finish. Two hundred million rows of write activity at lunchtime is the kind of change that the database does not let you take back.

At the application level, the problem is coordination. The schema and the code that queries it are coupled. If you rename a column in one migration and the application is still running the old build, the application's queries fail. If you deploy the application first, the new build queries a column that does not yet exist, and the application fails. There is no order of operations that makes a coupled change safe, because at some moment between the two deploys, one side is wrong.

The naive instinct is to do both at once. It usually works, in the same way that running a stop sign usually does not kill anyone. Eventually someone gets unlucky. The change happens at the moment of a long-running query, or the application takes longer to deploy than expected, or a third reader you forgot about is in the middle of a transaction. The pattern that takes the question out of "usually" is the one this article is about.

## The Pattern: Expand, Migrate, Contract

Stop trying to make the change in one step. Break it into three. Each step is a normal deploy. Each step is backwards-compatible with the version of the application that was running before it. At no point does the schema break any version of the code that is currently in production.

**Expand.** Add the new shape alongside the old shape. If you are renaming a column from `member_id` to `beneficiary_id`, add `beneficiary_id` as a new nullable column. Do not touch `member_id` yet. The schema now contains both. The application is unchanged, because the application does not know `beneficiary_id` exists. Deploy this.

**Migrate.** Move readers and writers from the old shape to the new shape, in two sub-steps. First, deploy an application build that writes to both columns and reads from the old one. The application is now redundantly writing to both `member_id` and `beneficiary_id` on every insert and update. Backfill the historical rows so the new column is populated for every existing row. Then deploy an application build that reads from the new column and still writes to both. The application is using the new shape and the database still contains the old one. Verify in production for as long as the team is willing to wait. A day. A week. Long enough that the next step is boring.

**Contract.** Remove the old shape. Drop the writes to `member_id` from the application. Deploy. After the application has run long enough that any cached query plans or open transactions referencing `member_id` are gone, drop the column. The change is complete.

The pattern is three deploys minimum. Often four or five when the migrate step has multiple read/write transitions. It looks like more work than the one-shot version because it is more work. The work that it adds is the work the one-shot version was assuming you would not need to do, and the one-shot version was wrong about that.

The mental model is that the schema is always in a state where both the previous and the current production application can run against it. The contract phase only starts when "the previous production application" is the one that already has the migrate-phase build, not the original one. That sequencing is the whole pattern.

## Worked Example: Adding a Column

A new column needs to be added to a five-hundred-million-row claims fact table. The column will hold a denormalized payer-type code, computed from a join that the analysts are tired of writing. The column needs to be `NOT NULL` eventually because every claim has a payer.

The naive version, in a migration tool, is one statement: `ALTER TABLE claims_fact ADD COLUMN payer_type_cd CHAR(3) NOT NULL DEFAULT 'UNK';`. Run that against the five-hundred-million-row table on most engines and the change will take an hour or more, holding a table-level lock for most of it. Inserts wait. Reads wait, on the engines that need to. The on-call pager rings.

The EMC version is three deploys.

The expand deploy adds the column as nullable, with no default. This is a metadata-only operation on Postgres 11 and later, and on recent versions of every other major engine. It takes milliseconds. Inserts and updates from the running application are not affected. The schema now has a new column that nobody writes to.

The migrate deploy comes in pieces. First, deploy the application change that computes `payer_type_cd` on every new write and inserts it into the new column alongside the existing columns. New rows have the new column populated; old rows do not. Run a batched backfill against the old rows: pick a thousand at a time, compute the payer-type from the existing source columns, update those thousand rows in a small transaction, sleep briefly, repeat. The backfill takes hours. The hours do not matter because the application is unaffected. When the backfill is done, every row has a non-null value.

The contract deploy is the constraint. Add `NOT NULL` to the column. On engines that can validate this in the background, this is the right time to ask for that path. On engines that cannot, the validation is a brief table scan, which on a backfilled column finishes faster than the original ADD-COLUMN-with-default would have, and without rewriting any data.

What goes wrong in the interim is that the application has to handle a column that may be null on historical rows. The backfill closes that window, but for the hours that it runs, code that reads `payer_type_cd` from old rows will see null. Either the read path tolerates it, or the read path waits for the contract deploy. Both are choices the team makes deliberately, not by accident.

## Worked Example: Renaming a Column

A column called `mbr_id` needs to be renamed to `member_id`. The reason is taste. The reason is also that the next data engineer to join the team should not have to learn that `mbr` is an abbreviation for `member` on the third day of the job. Taste compounds. So does its absence.

The naive version is a `RENAME COLUMN` statement and a coordinated application deploy. If everything ships at the same moment and nobody else is reading the table, this works. If the application takes ten minutes to roll across the fleet and any pod with the old build runs a query in those ten minutes, the query fails. If a BI tool somewhere has a saved query against `mbr_id`, it fails at the next refresh.

The EMC version is four deploys.

The expand deploy adds `member_id` as a new nullable column. The application does not know about it.

The first migrate deploy ships an application build that writes to both `mbr_id` and `member_id` on every insert and update. New rows are dual-written. Reads still come from `mbr_id`.

The backfill copies `mbr_id` into `member_id` for every existing row, in batches. When it finishes, the two columns are identical for every row.

The second migrate deploy ships an application build that reads from `member_id` and still writes to both columns. The application is now using the new name. The database still contains the old column.

The first contract deploy ships an application build that no longer writes to `mbr_id`. After that build has been in production long enough that the team is confident no other reader is using `mbr_id`, the second contract deploy drops the column.

That is four deploys, with a backfill between two of them, for what looks like a one-line change. It is also four deploys during which the application is at no point in a state where it is querying a column that does not exist or could not exist. Any of the four deploys can be rolled back independently. The migration is interruptible at every step. This is the price of doing schema changes against a system that does not stop, and it is also why the work has a name.

## Worked Example: Dropping a Column

Dropping a column sounds like the easy case. Nothing has to be added. Nothing has to be backfilled. Just remove the column. It is the case that goes wrong most often.

The hard part is not the drop. It is finding the readers. The application's queries are easy to grep. The downstream views are visible in the database catalog. The materialized views can be listed. The ETL jobs are in a repository somewhere. The dashboard nobody owns is on a server in a department that reorganized last quarter, and the saved query against the column is on a personal account that left the company a year ago. The drop does not break until the next refresh.

The EMC version of a drop is two phases.

The contract-phase deploy stops writing to the column from the application, but leaves the column in place. Run for a week. Two weeks. The team chooses. During that window, anyone who reads the column is reading stale data. The signal that this matters to someone is a complaint. The signal that this does not matter to anyone is silence.

The drop happens after the silence. The longer the wait, the more confident the drop. On a heavily-monitored OLTP system, two weeks is often enough. On a warehouse that feeds slow reporting cycles, a quarter is not unreasonable.

The team that gets this wrong drops the column at the end of the contract-phase deploy and finds out a month later that the closed-claims dashboard the executive team looks at on the first of the quarter has been broken since the drop. The drop was the right change. The drop was correct. The drop also broke something that should not have broken. The fix is to do the drop on a longer timer.

## Backfills at Scale

Two of the three worked examples have a backfill step in the middle. The backfill is what turns a thirty-second lock against a small table into a multi-hour process against a billion rows. The pattern that makes the backfill not lock the application out has a shape that does not change much across engines.

Pick a batch size that is small enough that one batch's transaction holds a lock for at most a few milliseconds. A thousand rows is a reasonable starting point. Ten thousand is sometimes fine. A hundred thousand is sometimes a disaster. The right size is the size that the database can write without holding a lock long enough to queue up application requests. Measure.

Loop. Each iteration picks one batch, updates it in a small transaction, and sleeps. The sleep is on purpose. It rate-limits the backfill against the production workload. Without a sleep, the backfill will run as fast as the database can serve it, and the rest of the workload will notice.

The rough shape on SQL Server:

```sql
WHILE EXISTS (SELECT 1 FROM claims_fact WHERE payer_type_cd IS NULL)
BEGIN
  UPDATE TOP (1000) claims_fact
  SET payer_type_cd = dbo.compute_payer_type(payer_id, plan_cd)
  WHERE payer_type_cd IS NULL;
  WAITFOR DELAY '00:00:00.100';
END;
```

The same shape works in Postgres with `UPDATE ... WHERE ctid IN (SELECT ctid FROM ... LIMIT 1000)`, in MySQL with a paginated keyset walk on the primary key, and in dbt with an incremental model that runs on a short cron for a day.

The backfill should be idempotent. Each batch should be safe to re-run, because the backfill will be paused, resumed, restarted, and possibly partially re-run more than once before it finishes. Idempotency is what makes "rerun the script from where it stopped" a one-line decision instead of a forensic investigation.

Monitor replica lag, if there is a replica. Backfills are a common cause of replica lag, and a lagged replica is a stale read. The backfill's pace is the dial that fixes this.

## What Tools Help

Tooling has closed most of the gap on the locking problem. None of it has closed the gap on the coordination problem, because the coordination problem is about deploys and code, not about the database.

For MySQL, gh-ost and pt-online-schema-change rewrite the table in the background, then swap it in atomically. For Postgres, `CREATE INDEX CONCURRENTLY` and `REINDEX CONCURRENTLY` cover index changes; pg_repack covers full-table rewrites; the planner has steadily added more cases where DDL is metadata-only. For SQL Server, `WITH (ONLINE = ON)` on the Enterprise edition makes most operations non-blocking. For the warehouse engines, the question is different because the application is not reading the table in real time; dbt's incremental and table materializations cover most of what would otherwise be a lock problem.

Migration tools, the ones the previous article in this series talked about, execute the steps you author. None of them is smart enough to take a one-line `RENAME COLUMN` migration and turn it into the four-deploy EMC pattern. The tool can be told to apply the steps in order. The pattern lives in the author's head. The pull request that contains it has to spell each step out, and the team has to accept that what looks like four migrations is one change.

The tool that actually helps the coordination problem is the pull request. The expand, migrate, contract phases each ship as their own pull request, with their own review, their own deploy, their own time in production before the next one. The pattern is the structure. The tools just keep it honest.

## What Still Hurts

Most schema changes have an EMC version. Some do not.

Foreign key changes are the awkward case. Adding a foreign key against an existing column requires validating that every row satisfies the constraint, which is a full table scan and a lock against writes for the duration on most engines. The workaround is to add the constraint as `NOT VALID` on Postgres, or with `NOCHECK` on SQL Server, validate it separately in the background, then mark it trusted. Other engines have similar paths. They are not universal.

Identity and sequence column changes are awkward because the column's value is generated by the database, and changing how it is generated affects every future insert. The expand step is fine. The contract step requires every reader to be moved off the old generator, which is sometimes more readers than the team realized.

Partition reshuffles are awkward because the table's storage layout is changing under the application, and the operation can take hours regardless of which strategy you use. Most engines have at least one online path. None of them are fast.

The honest summary is that the pattern handles the changes that hurt. It does not eliminate the hurt. The changes that are slow under EMC are slower under the naive approach, and dangerous in a way that EMC is not.

## What This Article Skipped on Purpose

Expand, migrate, contract is a boring pattern. Three deploys where one would do. A backfill in the middle. A wait at the end. It is the price of changing a system that does not stop.

The pattern is in your head, the pull request is the structure, and the pipeline executes the steps. What the pipeline cannot do, on its own, is tell you whether the change is working in production after the deploy. The smoke test passes. The metric you actually care about drifts. The next article in this series is about closing that loop.
