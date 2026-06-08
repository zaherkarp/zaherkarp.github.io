# Site review pipeline (publish-only mode)

A lightweight workflow for keeping a structured record of multi-agent
page reviews on this repo.

Reports are generated outside CI — typically in a Claude Code session,
but any source works. A GitHub Action handles the lifecycle: opening a
single tracking issue per review, closing the prior one, and carrying
unchecked items forward so nothing falls off the back.

**No API keys, no secrets.** The workflow reads files from the working
tree and writes to GitHub Issues. That's the whole surface.

## Panel prompts (`scripts/review/prompts/`)

Versioned, reusable prompts for the verbal-invocation panels described in
`CLAUDE.md` §Agent panels. These drive interactive critique sessions; they
do not produce site changes by themselves.

- `design-council.md` — the **Grumpy Design Council**: convenes the
  design-decision personas (Edward, Massimo, Steve, Haben, Nathan, Bret,
  Jess, Alan) as four parallel read-only sub-agent groups that argue across
  lanes, emit a consensus-graded synthesis table, then iterate with you on
  fixes one row at a time. Invoke: "Run
  scripts/review/prompts/design-council.md on `<target>`, goal: `<goal>`."
- `assess-items.md` — the **item assessor**: reads the open action items on
  a site-review tracking issue, inspects the current committed site, and
  renders a per-item verdict (met / not met-open / not met-locked /
  deferred / unsure) with file:line evidence. Interactive and
  propose-then-confirm: it never checks a box on its own. On confirmation it
  drives the check-off actuator (below) and drafts `wontfix:`/`defer:`
  comments. Invoke: "Run scripts/review/prompts/assess-items.md on
  `#<issue>`."

---

## File layout the pipeline expects

The lifecycle script (`scripts/review/issue-lifecycle.cjs`) looks for
four canonical paths per review, keyed on date:

| Report | Path |
|---|---|
| Six-camp data-viz craft critique | `critiques/critique-<YYYY-MM-DD>.md` |
| Alignment summary (companion to the craft critique) | `critiques/critique-<YYYY-MM-DD>-alignment.md` |
| Eight-evaluator hiring signal evaluation | `evaluations/hiring-eval-<YYYY-MM-DD>.md` |
| Cross-report synthesis with action checklist | `reviews/<YYYY-MM-DD>-synthesis.md` |

You can land any subset. Missing files are noted as `— *(missing)*`
in the issue body but do not fail the run. Only the synthesis is
**load-bearing**: it's where the action checklist comes from.

## Synthesis-report contract

For the workflow to populate an Action items section, the synthesis
report must contain a tiered checklist in this exact shape:

```markdown
## Action items

### Tier 1 (ship now)
- [ ] Rewrite cliff figcaption to claim-stating
- [ ] Add team-size line to BHA role

### Tier 2 (queue)
- [ ] @media prefers-reduced-motion block

### Tier 3 (defer or discuss)
- [ ] Career arc hand-shaped marks
```

Parser rules:

- `- [ ] <label>` exactly, one item per line. Indented sub-items are not
  picked up.
- Tier attribution comes from the most recent `### Tier <n> ...`
  heading. The word "Tier" (case-insensitive) is the trigger.
- A non-Tier `##` heading clears tier attribution. Items under no tier
  end up in an "Untiered" group.

The other three reports are not parsed for action items today; only
the synthesis is.

## Triggers

The workflow at `.github/workflows/site-review-publish.yml` fires on:

**Push** — any commit touching `critiques/**`, `evaluations/**`, or
`reviews/**`. Default path: generate reports in a session, batch-commit,
push. The workflow detects the latest date prefix and opens an issue
for that date.

**Manual dispatch** — Actions tab UI, or:

```bash
gh workflow run site-review-publish.yml \
  -f date=2026-05-23 \
  -f notes="prepping for Q3 search"
```

Both inputs are optional:

- `date` — explicit `YYYY-MM-DD`. Defaults to the latest detected
  across the three report directories.
- `notes` — short context string rendered as a blockquote in the
  issue body.

## Issue lifecycle (what the workflow actually does)

1. **Find any open issue with the `site-review` label** — the "prior"
   issue.
2. **Parse the prior issue body** for unchecked `- [ ]` lines. These
   become **Carried forward** items in the new issue.
3. **Scan the prior issue's comments** for lines starting with
   `defer:` or `wontfix:` (case-insensitive). These become an
   **Explicitly deferred** section in the new issue, with the
   commenter and date attached.
4. **Build the new issue body** with: a header, the list of
   present/missing reports, the action checklist parsed from the new
   synthesis, the carry-forward block, and the deferrals block.
5. **Open the new issue** with labels `site-review` and
   `needs-decision`. Labels are created on first run if missing.
6. **Close the prior issue** with a templated comment counting
   completed items (boxes that were checked between runs), carried-
   forward items, and deferrals.

The workflow is **idempotent**: re-running it for the same date
updates the existing issue in place rather than opening a duplicate.

## Working with an open review issue

- **Check a box** when you ship the change — in the GitHub web UI, or
  via a Claude Code on the web session that opens a PR and ticks the
  box as part of its work.
- **Defer or skip** by commenting on the issue with one of:

  ```
  defer: not yet, blocked on Q3 contract confirmation
  ```

  ```
  wontfix: violates CLAUDE.md locked subtitle rule; needs design discussion
  ```

  The next review run captures these and re-surfaces them so they do
  not get forgotten. Comments without these prefixes are not parsed —
  they remain in the issue history but do not affect the next run.

  A `wontfix:` note additionally **drops its matching item from
  carry-forward** on the next batch, so a won't-do stops reappearing as
  an open checkbox. The match is token-overlap (`suppressWontfixed` in
  `issue-lifecycle.cjs`): at least 80% of the item's significant words
  must appear in the reason, so lead the rationale with the item name. A
  non-match fails safe — the item simply carries forward as before.
  `defer:` notes are intentionally **not** suppressed: deferral means
  revisit later, so the box keeps surfacing with its reason attached.

- **Edit the body** freely. The action checklist is yours once the
  issue is open; the lifecycle script does not overwrite an existing
  issue unless you re-dispatch the workflow for the same date.

## Checking items off programmatically

`.github/workflows/site-review-check.yml` (backed by
`scripts/review/check-items.cjs`) flips checklist boxes on a tracking
issue without opening the web UI. Same no-secrets surface as the publish
workflow: it edits the issue body via the Actions `GITHUB_TOKEN`.

```bash
# Check the Tier 1 anchor item (by 1-based index) on the latest open issue
gh workflow run site-review-check.yml -f items=1

# Mix indices and label substrings; target a specific issue
gh workflow run site-review-check.yml \
  -f issue=43 \
  -f items="1, weekly load latency, subtitle rewrite"

# Preview without writing, then untick instead of tick
gh workflow run site-review-check.yml -f items=2 -f dry_run=true
gh workflow run site-review-check.yml -f items=2 -f state=unchecked
```

Inputs:

- `items` (**required**) — comma- or newline-separated selectors. A pure
  integer matches by **1-based index** over every `- [ ]`/`- [x]` line in
  the body (in document order, across all tiers and the carried-forward
  block). Anything else is a **case-insensitive substring** matched
  against the item label; one selector may flip several lines.
- `issue` — issue number. Defaults to the latest open `site-review` issue.
- `state` — `checked` (default) or `unchecked`.
- `dry_run` — `true` previews the matches in the job log and writes
  nothing.
- `comment` — `true` (default) posts an audit comment listing what flipped
  and which selectors matched nothing.

Selectors that match no box are reported as warnings, not failures; the
run only fails if **none** of the selectors match anything (a typo guard).

**Durability caveat.** This edits the issue body in place. The publish
workflow (`issue-lifecycle.cjs`) regenerates the body from
`reviews/<date>-synthesis.md` whenever it re-runs for the **same date**,
re-emitting every item as `- [ ]` and wiping checks made here. Across
review batches a `- [x]` *is* durable (carry-forward only repeats
unchecked items), but if you need a check to survive a same-date
republish, resolve the item in the synthesis source too.

## Generating the four reports

The pipeline does not generate reports. You produce them however you
want; the canonical recipes are the four multi-agent prompts:

- **Craft critique** — six-camp methodology (encoding rigorists,
  editorial clarity, data humanists, system designers, pipeline &
  reproducibility, access floor). Output → `critiques/critique-<date>.md`.
- **Alignment summary** — derivative synthesis of the craft critique
  with three views (per-change consensus, pairwise camp alignment,
  camp vs. design discipline) and a combined top-10. Output →
  `critiques/critique-<date>-alignment.md`.
- **Hiring evaluation** — eight-evaluator panel at three reading depths
  (10s / 60s / 5min). Output → `evaluations/hiring-eval-<date>.md`.
- **Synthesis** — cross-report comparison that produces the Tier 1/2/3
  action checklist this workflow reads. Output → `reviews/<date>-synthesis.md`.

The prompts themselves are not committed in this repo yet. If you
want them versioned, drop them into `scripts/review/prompts/` —
nothing else in the pipeline depends on a specific location.

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Workflow fails with "No reports found for date X" | The detected or supplied date has no matching files | Verify filenames match the canonical pattern; or use manual dispatch with explicit `date` input |
| Issue opens but action items section says "no checklist found" | Synthesis report has no `- [ ]` lines under `### Tier N` headings | Re-emit the synthesis with the canonical structure (see "Synthesis-report contract" above) |
| Duplicate issues for the same date | Should not happen — workflow updates in place — but if it does, close the older one manually | The dupe check uses exact title match (`Site review: <date>`); rename collisions break it |
| Carry-forward block is empty when you expected items | Prior issue's items were already checked, or no prior open issue exists | Check the closed issue's body to confirm; verify only one issue had the `site-review` label open |
| Labels missing on first run | Fresh repo, no labels yet | The workflow creates `site-review` (purple `#5319e7`) and `needs-decision` (yellow `#fbca04`) on first run; no action needed |

## What's deliberately out of scope (for now)

- **Report generation in CI.** Tokens cost money. Generate
  interactively, commit, let CI handle the issue lifecycle. If you
  want hands-off generation later, add a second workflow that
  produces the four files and pushes them; this publish workflow
  will pick them up automatically.
- **JSON-fed reports.** If you ever need to feed reports from a
  non-markdown source, add a `scripts/review/from_json.py` helper
  that writes the four markdown files from a JSON blob, then this
  workflow runs unchanged.
- **PR auto-creation from action items.** Out of scope. Open PRs
  from a Claude Code session and tick the corresponding box when
  the PR merges.
