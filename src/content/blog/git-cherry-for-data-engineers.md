---
title: "Git Cherry and Cherry-Pick for Data Engineers"
description: "Treating git cherry and git cherry-pick as a pair: one tells you what's missing, the other moves it. With three healthcare-data-pipeline scenarios and the flags you actually need."
publishDate: 2026-04-29
tags: ["git", "version-control", "data-engineering", "dbt", "HEDIS"]
---

Most git tutorials reach for `cherry-pick` when something goes wrong in a release branch. But the more useful mental model is to treat `git cherry` and `git cherry-pick` as a pair: one tells you what's missing, the other moves it. Together they give you surgical control over which work lands where.

## What `git cherry` does

`git cherry` compares two branches and tells you which commits from one haven't been applied to the other. The output is a list of commits prefixed with `+` (not yet applied) or `-` (already applied, matched by patch identity).

```bash
git cherry [-v] <upstream> [<head>]
```

If you omit `<head>`, it defaults to `HEAD`. If you omit both, `<upstream>` defaults to the upstream of your current branch — so day-to-day, `git cherry main` is usually all you need.

The `-v` flag adds the commit subject to the output, which is the form you actually want to read:

```bash
git cherry -v main feature/hedis-cbp-refactor
```

A `+` means that commit is in `feature/hedis-cbp-refactor` but not in `main`. A `-` means an equivalent change exists in both, even if the SHA differs — git matches by *patch identity* (a hash of the diff with whitespace and line numbers normalized, computed by `git patch-id`). So a rebased, squashed, or previously cherry-picked equivalent still shows up as `-`.

This is useful before you ever touch `cherry-pick`. You use `git cherry` to answer: "what commits exist on the source branch that haven't landed on the target yet, and is any of it something I need to move?"

## What `git cherry-pick` does

`git cherry-pick` applies one or more commits from anywhere in your git history onto your current branch. It replays the change introduced by that commit, creating a new commit with a new SHA.

```bash
git cherry-pick <commit-sha>
```

You can also pick a range:

```bash
git cherry-pick A..B
```

This applies all commits *after* A up to and including B. Note the asymmetry: A itself is excluded. To include A, use `A^..B` (which is "everything from A's parent onward, ending at B").

## Using them together

The clean workflow is:

1. Run `git cherry -v` to identify what commits are missing from the target branch.
2. Copy the SHAs you want.
3. Run `git cherry-pick` to apply them.

```bash
# Step 1: see what's in the feature branch that main doesn't have
git cherry -v main feature/hedis-cbp-refactor

# + a3f91c2 fix: correct runout window for TRC measure
# + d84cc1e fix: handle new-year enrollment gap in CBP denominator
# - 77b3a10 chore: update inline comments
#
# + means: in feature/hedis-cbp-refactor, NOT in main
# - means: an equivalent patch is already in main (matched by patch-id,
#          not SHA — so a rebased or cherry-picked version still matches)

# Step 2: pick only the two fixes, skip the chore commit
git switch main
git cherry-pick a3f91c2 d84cc1e
```

## Data engineering scenarios

### Scenario 1: hotfix needs to go to prod without the rest of the feature branch

You're midway through refactoring a HEDIS pipeline. The feature branch has ten commits. One of them fixes a denominator calculation that's wrong in production right now. You don't want to merge the whole branch.

```bash
# Find the commit
git cherry -v main feature/hedis-pipeline-refactor

# + f12a3b1 fix: exclude disenrolled members from CBP denominator
# + 9c01d22 refactor: restructure measure module layout
# + 3a8bc44 wip: new aggregation layer, not ready

# Only the fix is safe to ship. The wip commit likely won't apply
# cleanly anyway — it depends on the refactor above it.
git switch main
git cherry-pick f12a3b1
```

### Scenario 2: a dbt model fix exists on a colleague's branch

A coworker fixed a date spine issue in a staging model on their branch. Their branch isn't ready to merge. You need that fix now for a downstream model you're building.

```bash
# Check their branch against yours
git cherry -v your-branch coworker/date-spine-fix

# + 88de451 fix: anchor date spine to enrollment start, not calendar year

# Apply just that commit
git cherry-pick 88de451
```

### Scenario 3: propagating a fix across multiple environment branches

Your repo has `main`, `staging`, and `prod` branches representing environment promotions. A validation fix needs to land in all three without a full merge.

This is the case for cherry-pick. (It's worth noting that long-lived environment branches are an older pattern; many modern dbt and orchestration shops use a single trunk plus tag- or config-based promotion. If you're maintaining environment branches, cherry-pick across them is a working tool. If you're greenfielding, consider whether you need the branches at all.)

```bash
# Find the commit on main
git log --grep="readmissions filter" main --oneline
# c4f7712 fix: correct PCR scope cell row filter

# Forward-port to staging, recording the origin SHA in the message
git switch staging
git cherry-pick -x c4f7712

# And to prod
git switch prod
git cherry-pick -x c4f7712
```

The `-x` is doing real work here. On a long-lived environment branch you'll want the origin SHA in the message six months from now when you're trying to figure out why prod has a commit that doesn't appear in staging's git log.

## When it conflicts

Cherry-pick can fail when the file you're patching has drifted between branches — a column was renamed, a model was restructured, a yaml schema changed. You're dropped into a half-applied state with conflict markers in the file.

```bash
git cherry-pick c4f7712
# Auto-merging models/marts/measure_pcr.sql
# CONFLICT (content): Merge conflict in models/marts/measure_pcr.sql
# error: could not apply c4f7712... fix: correct PCR scope cell row filter
```

Three exits:

```bash
# 1. Resolve the markers in the file, stage, continue:
git add models/marts/measure_pcr.sql
git cherry-pick --continue

# 2. Bail out entirely and return to the pre-pick state:
git cherry-pick --abort

# 3. Skip this commit and continue a multi-commit pick:
git cherry-pick --skip
```

If you're cherry-picking multiple commits at once (`git cherry-pick A B C`), each is applied as a separate commit in order. A conflict on B pauses the rest — `--continue` resumes from B, `--skip` jumps to C, `--abort` discards everything including A. This is what people sometimes call "octopus" cherry-picking; the trap is assuming the operation is atomic.

For content-level conflicts in generated dbt artifacts (`manifest.json`, compiled SQL), strategy options often save you a manual merge:

```bash
git cherry-pick -X theirs c4f7712   # prefer the picked commit's version
git cherry-pick -X ours c4f7712     # prefer the current branch's version
```

`-X` is a strategy *option* (passed through to the merge strategy), not the same as `--strategy`. For most cherry-picks, `-X theirs`/`-X ours` is the only one you'll reach for.

## Flags worth knowing

**`--no-commit` (`-n`)**: applies the change to your working tree and stages it in the index without committing. Useful when you want to combine multiple cherry-picks into one commit, or inspect the change before committing.

```bash
git cherry-pick --no-commit a3f91c2 d84cc1e
git diff --cached   # review the combined staged diff
git commit -m "fix: apply CBP and TRC runout corrections"
```

**`-x`**: appends a `(cherry picked from commit <sha>)` line to the commit message. Useful for traceability on long-lived multi-environment repos.

```bash
git cherry-pick -x c4f7712
```

**`-m <parent-number>`**: required when cherry-picking a *merge* commit. Without it, you get an error and a commit you can't apply.

```bash
git cherry-pick a1b2c3d
# error: commit a1b2c3d is a merge but no -m option was given.

# -m <n> tells git which parent's diff to use as the base.
# -m 1 = diff against the first parent, i.e. mainline.
git cherry-pick -m 1 a1b2c3d
```

This is the single most common footgun in environment-branch propagation, because the things you most want to forward-port (a feature merge, a hotfix merge) are merge commits.

**`--allow-empty`**: lets you record a cherry-pick that becomes empty because the change is already in the target. Common in env-branch propagation when you've forwarded a fix to prod, then later cherry-pick it to staging — but staging already pulled it from a separate merge.

```bash
git cherry-pick c4f7712
# The previous cherry-pick is now empty, possibly due to conflict resolution.

# If you confirm the change is already there:
git cherry-pick --skip

# Or, to record the no-op explicitly for audit purposes:
git cherry-pick --allow-empty c4f7712
```

`--keep-redundant-commits` is a related variant that keeps the empty commit during multi-commit picks without prompting.

**`--signoff`**: appends a `Signed-off-by` trailer to the commit message. Relevant if your team enforces DCO.

## When to avoid cherry-pick

Cherry-pick duplicates commits. If `feature/` eventually merges into `main`, you'll have the same logical change twice in history, which can cause messy merge conflicts and confusing diffs. (`git cherry`'s patch-identity matching softens this somewhat — equivalent commits show up as `-` and don't get re-applied — but the duplicated SHAs still clutter the log.)

The cases where it earns its keep:

- Emergency hotfixes that can't wait for the full branch to stabilize.
- Propagating fixes across long-lived environment branches.
- Pulling a specific fix from a teammate's branch without taking their whole branch.

If you're routinely cherry-picking between two branches that should eventually merge, that's usually a signal the branching strategy needs review, not a reason to cherry-pick more.

One last note for confidence: a botched cherry-pick is recoverable. `git reset --hard HEAD@{1}` returns you to the state immediately before the pick, and the reflog keeps that state around for ~90 days by default. The perceived risk of cherry-pick is higher than the actual risk.
