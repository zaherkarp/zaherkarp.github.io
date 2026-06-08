# Site-review item assessor — orchestration prompt

A versioned, reusable prompt for **assessing whether the open action items
on a site-review tracking issue are actually met by the current state of
the site**, then proposing check-offs for me to confirm. This is the
evaluator that complements the two mechanical pieces:

- `scripts/review/issue-lifecycle.cjs` — opens/closes/carries the issue.
- `scripts/review/check-items.cjs` (+ `.github/workflows/site-review-check.yml`)
  — the actuator that flips a checkbox once a decision is made.

This prompt is the **judge**: it reads the items, inspects the code, and
decides per item. It runs **interactively** and is **propose-then-confirm**
— it never checks a box on its own.

---

## How to invoke

Tell Claude: **"Run scripts/review/prompts/assess-items.md on #<ISSUE>."**

- `<ISSUE>` — a site-review issue number. If omitted, default to the
  latest open issue carrying the `site-review` label.
- Optionally scope it: "…only the Tier 1 items", or "…just reassess the
  figure items". Default is every unchecked item.

The issue body is public, so read it with the available web fetch tool or
`gh issue view` if authenticated. You do not need write access to assess —
only to check off (see Phase 4).

---

## What this is NOT

- Not a critique generator. It does not propose new findings or sections;
  that is the critique pipeline (`docs/critique/`) and the Agent panels.
  This only adjudicates items that already exist on the issue.
- Not automatic. It does not run in CI and does not check boxes without my
  confirmation. If you want a box flipped, you propose it and wait.
- Not a closer. It does not close the issue or supersede it; that is
  `issue-lifecycle.cjs` on the next review batch.

---

## Orchestration

### Phase 0 — Pull the open items
Read the issue. Extract every unchecked `- [ ]` line with its Tier. Note
any existing `defer:` / `wontfix:` comments so you do not re-litigate a
decision already recorded.

### Phase 1 — Gather evidence per item (READ-ONLY)
For each open item, look at the **current committed site**, not your
memory of it. Quote the evidence: a `file:line` (prefer the committed
state — `git show HEAD:index.html` or a fresh grep), a rendered behaviour,
or a CLAUDE.md lock. One item may need several greps; do the work rather
than guessing. For broad items, an `Explore` sub-agent is fine, but the
verdict and evidence are yours.

### Phase 2 — Verdict per item
Assign exactly one verdict, and be honest about *why* something is not met:

| Verdict | Meaning |
|---|---|
| **Met** | A change in the tree now satisfies the item. Cite the file:line. |
| **Not met — open work** | Genuinely undone; a reasonable next change would close it. |
| **Not met — locked** | Conflicts with a locked CLAUDE.md decision. Won't be met by implementation; wants a `wontfix:` decision, not a check. |
| **Not met — deferred** | Parked with an explicit revisit condition. Wants a `defer:` note, not a check. |
| **Unsure** | Evidence is ambiguous. Say what you would need to decide. |

The critical discipline: **never tick a "locked" or "deferred" item as
done.** Done means a change satisfied it. A decision to *not* do it is a
`wontfix:`/`defer:` comment, which is a different action (Phase 4b).

### Phase 3 — Present the table, then STOP
Emit one table and nothing checked yet:

| # | Item | Tier | Verdict | Evidence (file:line / URL / lock) |

Below it, state the proposal plainly: which item indices you recommend
**checking** (Met only), and which you recommend recording as
**wontfix/defer** with one-line rationales ready to paste. Then **stop and
wait for my confirmation.** Do not proceed to Phase 4 unprompted.

### Phase 4 — On my confirmation only

**4a — Check off the Met items.** The box-flip has to reach GitHub. From an
interactive session without `gh`/a token you cannot write the issue
yourself; hand me the exact path:
- the one-line dispatch: `gh workflow run site-review-check.yml -f items=<indices>`, or
- the Actions-tab steps (Site review (check items) → `items=<indices>`), or
- tell me which boxes to click.

If `gh` is authenticated in the session, you may run the dispatch directly
once I have confirmed.

**4b — Record wontfix/defer decisions.** For items I agree are won't-do or
deferred, produce a single comment block, **one decision per line**, each
line starting with `wontfix:` or `defer:` and keeping its whole rationale
on that one line (the scanner in `issue-lifecycle.cjs` parses per line).
Lead each rationale with the item name so the next batch's carry-forward
suppression can match it.

> Note: a `wontfix:` comment now also **drops the matching item from
> carry-forward** on the next batch (token-overlap match in
> `suppressWontfixed`), so a won't-do stops reappearing as an open box.
> `defer:` items keep carrying forward by design.

---

## Locked constraints (do not recommend violating)

Same lock list the rest of the pipeline honors — see `CLAUDE.md`
§Design decisions and §What NOT to do. In particular: no JS outside the
documented exceptions, the 60% column + sidenote system, ETBook, accent
discipline, the italic reservation, and the career-arc coordinates. If the
only way to "meet" an item is to break one of these, the verdict is **Not
met — locked**, not a proposed change.
