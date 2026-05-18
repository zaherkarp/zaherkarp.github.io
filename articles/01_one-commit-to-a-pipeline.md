# From One Commit to a Pipeline

For a long time my workflow had three steps. Open a file, write the SQL, run it. If the row counts matched what I expected, I committed and moved on. If something else broke, I fixed that file too, ran them both, and committed when everything was green. The repo was a place I copied finished work into when I was done thinking about it. Git was a save button with history.

## The workflow I used to have

Picture a small warehouse team. Three or four developers, a reporting database, a stack of stored procedures that build last night's facts, maybe two dozen views that the BI tool reads from. Someone has to add a channel breakdown to the daily sales rollup so the marketing team can split web from store. That someone is me.

I open the file for the procedure in whichever editor is already open. I edit it. The change is small, two new columns in the `GROUP BY` and two new columns in the target table. Something like this:

```sql
-- MySQL 8.0 dialect throughout this series.
-- Daily aggregate from the staging order table into the warehouse fact.

DROP PROCEDURE IF EXISTS daily_sales_rollup;
DELIMITER //
CREATE PROCEDURE daily_sales_rollup(IN run_date DATE)
BEGIN
  -- Wipe out any previous run for this date so reruns are idempotent.
  DELETE FROM fact_sales_daily WHERE sales_date = run_date;

  -- Aggregate staged orders into one row per store and channel.
  INSERT INTO fact_sales_daily
    (sales_date, store_id, channel, gross_revenue, net_revenue)
  SELECT
    DATE(order_ts) AS sales_date,
    store_id,
    channel,
    SUM(line_total) AS gross_revenue,
    SUM(line_total - discount) AS net_revenue
  FROM stg_orders
  WHERE DATE(order_ts) = run_date
  GROUP BY DATE(order_ts), store_id, channel;
END //
DELIMITER ;
```

I run it against the dev database. The procedure creates without error. I call it with yesterday's date. I check the result against a quick aggregate of the staging table. The numbers reconcile to the cent. I commit the file with the message "Add channel to daily sales rollup" and push.

What happens next depends on the team. Sometimes I deploy it to QA myself by running the file there. Sometimes I send the file to whoever owns the QA box. Sometimes I message the channel and say "this is ready when you're ready," and the SQL ends up on QA an hour or a day later. Eventually it goes to prod, by whichever mechanism prod changes happen. Sometimes that mechanism is me. Sometimes it is a ticket and a release window.

There is a lot to recommend this workflow. It is fast. The feedback loop between writing SQL and seeing the result is tighter than in any other kind of programming I have done. The tools are minimal, the ceremony is zero, and you stay close to the data the whole time. If you are working alone on a small system you understand completely, this workflow can carry you indefinitely.

It carried me for years. Then it did not.

## Where it quietly breaks

The breakage is not loud. It accretes. The workflow keeps working on the file in front of you, and the rest of the system slowly drifts away from the file in front of you.

A 2am page goes off because the nightly load is failing. I open the stored procedure and find it does not match what I last committed. Someone, possibly me, ran an `ALTER PROCEDURE` against prod three weeks ago to handle an edge case and never put it back in the repo. The repo says version A. Prod is running version B. The file on the shared drive that another developer was about to edit is version A, the one in the repo, which means the next deploy is going to overwrite the prod fix and the same page is going to go off again next week. The repo does not know what prod looks like. Nothing in this workflow does.

A migration that ran in eight seconds on dev locks prod for forty minutes because the dev database has five thousand rows in `stg_orders` and prod has sixty million. I knew the migration was going to be slow, in the abstract. I had no way to estimate how slow because the only place that exists at prod scale is prod.

A column changes from `CHAR(1)` to `TINYINT` to save space. Two reports that cast the column to a string break the next morning. Those reports live in a different repository, owned by a different team, and nothing connects a schema change in one repo to a regression in the other.

A regulator or an internal auditor asks when a specific column on a specific table last changed, why, and who approved it. The git log says when the file in the repo was last edited. The file in the repo may or may not match what was actually deployed. There is no record of approval because the approval was a Slack thread that has since rolled out of free-tier retention. The honest answer is "I think it was Maria in March, possibly April, and I am not sure why."

A `DROP TABLE` that was supposed to run on staging runs on prod, because the two databases are in the same client and the connection string was the wrong one. The rollback is restoring last night's backup, which means losing today's data, which means an awkward conversation with the team whose reports were built on today's data.

A simpler version of the same problem: two files for the same object, and no way to tell which one is real.

```sql
-- File in the repo, last commit timestamp says April.
CREATE PROCEDURE refresh_member_eligibility() ...

-- File on the shared drive, edited as a hotfix in June.
CREATE PROCEDURE refresh_member_eligibility() ...

-- The actual definition currently running in prod.
SHOW CREATE PROCEDURE refresh_member_eligibility;
-- Could match either of the above. Could match neither. Nobody has checked in months.
```

These are all solo failure modes. They all happened to me with a team of one editing a single repo.

Now add a second person. They edit the same stored procedure I edited, the same week, from their own copy on their own laptop. We both deploy. Whoever deploys second wins. The first person's change is gone. Neither of us notices until the report that depended on it breaks two days later, and by then it is hard to reconstruct what the original change even was. Git would have caught the conflict if either of us had pulled before pushing, but in this workflow pulling is something you do when you remember, which is mostly when something has already broken.

The new hire asks where the latest version of the warehouse schema is. The honest answer is "the prod database, sort of, plus some uncommitted changes from last sprint." There is no version anywhere that you can point at and say: this is what we believe is true. Onboarding becomes an oral tradition.

The "I thought you'd already deployed that" gap. Two people, each assuming the other ran the migration on QA. The migration never ran. The next deploy fails because the table the new code expects does not exist. Or both people run it, one of the runs fails silently because the column already exists, and now both of you believe it ran and neither of you can tell whose attempt actually applied.

A change goes out at midnight on a Saturday. There is no record of who approved it because there was no approval. Compliance has questions later. So does the person trying to figure out what changed between Friday and Monday.

The common thread is the same in every case. The workflow stores code. It does not represent state, ownership, or sequence. Everyone working on the system is carrying around a mental model of what is where and which version is real. The mental models do not agree, and there is no shared place to check.

Version control, used well, is the shared place. The pipeline is what keeps the place honest.

## Version control as scaffolding

You already use the basic moves. `git add` stages a file. `git commit` saves a snapshot of the staged files into the history of your current copy of the repository. `git push` sends those commits to a shared repository that everyone else can read. `git pull` fetches everyone else's commits from the shared repository and merges them into your copy. If you have used git at all, even as a save button, those four commands are where you live.

Pull is the move the save-button workflow tends to skip. Without pulling, two people can edit the same file at the same time and neither of them will see the other's edits until one of them tries to push. At that point git will refuse, on the grounds that the shared repository has commits the pusher has not seen. The fix is to pull, resolve any conflicts the merge surfaces, and push again. This is annoying but valuable; the alternative is the silent overwrite I described above, which is much worse.

The first concept the save-button workflow is missing is the branch. A branch is a separate line of history. By convention every repository has a branch called `main` (older repos call it `master`) that represents the canonical version of the project. Until you do otherwise, when you commit, you commit on `main`. Everyone else also commits on `main`. There is one shared line of history and everyone is writing on it.

When you start a piece of work, you make a branch off of `main`. The branch starts as a copy of main at the moment you branched. As you commit on the branch, you add to that separate line. Main keeps moving independently. Your branch does not affect what anyone else sees until you choose to bring it back into main.

The mental shift this enables is small but consequential. `main` stops being "where I save my work" and becomes "what we believe is the canonical state of the project." Work in progress lives on a branch. The branch is a place where things can be wrong, half-finished, or experimental, and that is fine, because the branch is not what anyone else is reading from. When the work is ready, you bring the branch back into main.

The mechanism for bringing a branch back is a pull request. GitLab and a few others call it a merge request. The two terms mean the same thing. A pull request is a structured proposal that says: here are the commits on my branch, here is the diff against main, please merge them. The proposal sits in the open until it is approved. While it sits there, three things happen that do not happen with a bare commit.

The change is visible. Anyone on the team can read the diff, comment on specific lines, and ask why a stored procedure was rewritten the way it was. There is a record of the discussion attached to the change.

Automated checks can run. The pull request is a known target. A pipeline can hook itself to "every new pull request" and "every push to an existing pull request" and run a battery of checks. This is the seam where CI lives. Without a branch and a pull request, there is no clear moment at which to run the checks.

Someone reads it. Even if that someone is me an hour later. The review need not be elaborate, but it is structurally required for the change to land. The moment of commitment is the merge into main, not the commit on the branch. That distinction is the whole point of the system.

I want to be honest about the overhead. For a typo fix in a file nobody else depends on, branches and pull requests feel like ceremony. They are. But for the SQL changes that matter, which is most of them once a system is more than a few months old, the friction is the feature. Every shared stored procedure, every schema migration, every view that downstream reports depend on benefits from being visible, reviewable, and reversible before it lands. The reason it feels heavy is the same reason it works.

There is one more piece of vocabulary worth knowing before we move on. The `main` branch is usually configured to be protected. Protection means you cannot push directly to main; you have to go through a pull request. This is what closes the loophole. Without protection, the team can branch and review when they feel like it, and commit directly to main when they are in a hurry. With protection, every change to main goes through the same door, which means every change to main can be checked the same way.

The branch gives you a thing to check. The pull request gives you a place to check it. The thing doing the checking is the pipeline.

## The pipeline in plain English

A pipeline is a sequence of automated steps that runs against a change. Two parts are doing work here: "sequence of automated steps" and "runs against a change." The first part means a stack of small jobs that each verify something specific. The second part means the stack is triggered by something concrete: a new pull request, a push to a branch, a merge into main, a tag being created. The pipeline runs every time the trigger fires, without anyone having to remember to ask.

For a SQL codebase, the questions a pipeline can answer for you, automatically, on every change:

- Does every SQL file parse against the dialect we use?
- Does each migration apply cleanly to a fresh schema, in order, from the beginning of the project?
- Does each migration apply cleanly to a clone of the current production schema?
- After the migrations run, do the tests we wrote still pass?
- Does the resulting schema match what is checked into source control as the canonical definition?
- Is this change safe to deploy automatically, or does it need a human to look first?

Every one of these is a question a careful developer asks before deploying. The pipeline asks them every time. It is consistent in a way that a person performing them by hand cannot be.

The pipeline is usually split into two halves, and the names matter because they appear in every conversation about this. CI is continuous integration. It is the half that checks the change. Every pull request triggers it, every push to a branch triggers it, and merges into main trigger it. CD is continuous delivery, sometimes continuous deployment. The two terms mean slightly different things, and the next article unpacks the difference. For now, treat CD as the half that moves a change that has passed CI through the staged environments on its way to production.

There are two tradeoffs to name before this gets oversold.

The first is setup cost. The initial pipeline for a project is real work. You have to decide what counts as a test, how to provision a database for the pipeline to run against, how to handle credentials, where to store the results, what the deployment target looks like. None of this is free. The payoff arrives later, and only if you commit to running the pipeline against every change. A pipeline that exists but is not enforced is decorative.

The second is the pipeline you cannot trust. A slow pipeline gets bypassed; people start pushing changes before the pipeline finishes, on the theory that they know their change is fine. A flaky pipeline gets ignored; if half the failures are spurious infrastructure issues, people stop reading the failures. Once trust erodes, the pipeline is not a check, it is noise. Building one well takes more discipline than tooling.

There is one thing the pipeline does not do, and pretending it does is the most common way to sell people sour on CI/CD. A pipeline does not replace thinking. It catches the things a checklist catches: syntax errors, migrations that fail on a fresh schema, regressions in tests you wrote, schema drift between source control and the database. It does not catch a join that looks correct and produces subtly wrong numbers under prod data. It does not catch a deadlock that only manifests at prod concurrency. It does not catch a business rule that is encoded incorrectly. The pipeline takes care of the boring stuff so that human review can focus on intent.

That last point is the underrated one. The reason to automate the checklist is not that humans are bad at running checklists. It is that humans are bad at running the same checklist on every single change, every single time, when the change is small and the developer is confident. The pipeline does not get tired or skip steps. That consistency is what lets you trust the system as it grows past the size where any one person can hold it in their head.

## What's in the pipeline

The next article walks through what each piece of a SQL pipeline looks like in concrete terms. Linting that catches dialect violations and naming-convention drift before review. Migration validation that applies the change against a clean database and against a production-shaped clone. Unit tests for stored procedures and functions, with notes on what tools like tSQLt, pgTAP, and similar harnesses do well and where they do not. Schema-drift checks that compare the live database against the source-controlled definition. The distinction between continuous delivery and continuous deployment, and what each one means for who pushes the deploy button. Daily life on a team that has one of these set up, the objections SQL developers tend to raise about each piece of it, and a survey of the tools that fill each slot.
