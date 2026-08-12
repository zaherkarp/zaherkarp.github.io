# Proposal: `scripts/lint_provenance.py`

Status: **proposed, not built.** Rule adopted as editorial policy 2026-08-11
(`CLAUDE.md` §Calibrated claims, "Claim provenance rule"). This is the gate
that would enforce it. Written up separately so the policy can stand on its own
and the tooling can be accepted, deferred, or rejected independently.

## Why the existing gates cannot do this

`lint_facts` compares `index.html` to `resume.md` and `cv.md`, but only on
**employment structure** — org, title, start date, one-current-role-per-surface,
resume-orgs ⊆ homepage-orgs. It reads `<h3>` and `<p class="meta">` and nothing
else. No number on the page is in its scope.

`lint_recognition` covers `#service` ⊆ `cv.md` recognition, on title and org
only. `lint_gantt` compares `index.html` to its own SVG and never opens
`cv.md` — which is exactly how the Patient Safety date conflict survived with
CI green until 2026-08-11.

So a claim that exists on exactly one surface is invisible to all three **by
construction**. `RxNorm validation cut client-audit discrepancies ... from
roughly 30% to under 5%` carried no denominator for months, and no gate could
have caught it, because there was nothing to compare it against.

## What it would check

For each **number** and each **named third-party organization** in
`index.html`'s hand-authored prose, assert traceability to either:

  (a) `src/content/resume.md` or `src/content/cv.md`, or
  (b) a public external URL already present in the same section of the page.

## Scope, and what is deliberately excluded

Excluded, all for reasons already established elsewhere in the repo:

  - **Generated marker regions** — `activity-grid`, `writing-list`,
    `writing-index`, `pub-list`, `cliff-path`. Their content comes from sources
    that other linters check directly, and they can be legitimately stale
    between a source edit and the next CI run. Same exclusion `lint_notes`
    already makes.
  - **`<style>`, `<script>`, SVG internals, HTML comments.** Note that
    comment-blindness is the OPPOSITE of the deliberate choice in
    `lint_recognition` and `lint_gantt`, which parse commented-out sections on
    purpose (§Recognition alignment lint). Here a commented-out claim renders
    nothing and asserts nothing, so it is out of scope. **This divergence must
    be commented in the source or a future reader will "fix" it.**
  - **Qualitative framing and mechanism description.** The rule governs numbers
    and named orgs. "I write measure logic I can defend in a client audit" is
    unfalsifiable-by-linter and out of scope by design.
  - **Years and dates.** Too noisy, and date drift is `lint_facts`' job.
  - **Self-referential names** — the owner, the site, this repo's own projects.

## The two hard parts, honestly

**1. Named-organization detection has no clean signal.** Capitalized multiword
phrases catch `Community Health Network` but also `Star Ratings`, `Data Science
and Engineering`, and every section heading. Options, worst to best:

  - Regex on capitalization → unusable false-positive rate.
  - A maintained allowlist of known-good orgs → becomes the per-entry alias map
    that `lint_recognition`'s design notes explicitly reject as a maintenance
    burden.
  - **Invert it:** extract org-shaped strings, subtract everything already
    present in `resume.md`/`cv.md`/`skills.yaml`/`publications.yaml`, and report
    only the remainder. The remainder is small (the 2026-08-11 audit found ~16
    across the whole page) and each new one is a one-line review. This makes the
    check a **report with a small hard core**, not a general classifier.

**2. Numbers are easier but need a threshold.** Reuse `lint_notes`'
significant-number logic: normalize commas, skip years 1900-2099, and consider
a token significant at ≥ some floor. But percentages and multipliers matter here
and are small (`30%`, `5%`, `60%`, `7x`), so the floor cannot simply be 1000.
Proposed: flag any number carrying a unit marker (`%`, `x`, `$`, `+`) plus any
bare integer ≥ 1000.

## Suggested shape

Follow the `lint_recognition` / `lint_ideas` precedent of a **hard gate one way,
informational report the other**:

  - **Hard fail:** a number with a unit marker, in hand-authored prose, that
    appears in neither source file nor beside an external citation in its
    section. This is the RxNorm class and it is narrow enough to be trustworthy.
  - **Informational, never fails:** named organizations not found in any source.
    Printed on a manual run, like `lint_recognition`'s coverage report and
    `lint_ideas`' orphan report. Org detection is too fuzzy to block a push.

Wire the hard half into `scripts/hooks/pre-push` **and** `.github/workflows/lint.yml`
(they must stay in sync — see §Pre-push checks), and add characterization tests
in `scripts/tests/` covering a pass case, a violation case, and the carve-out
case, matching the twelve existing gates.

## Expected result at adoption

Two hard-gate failures on the current tree, both already documented in
`CLAUDE.md`: the Wisconsin Longitudinal Study's `10,000` / `50-year`, and the
Speaking stat's `2` of `45` posters. Both are fixed by adding the facts to
`cv.md`, not by editing the homepage.

## Cost, stated plainly

A thirteenth gate on a repo that already runs twelve, for a property no reader
can perceive (Focus Group R1, unanimous). It earns its place only if new orphan
claims are expected to keep appearing. If the page is near its final content,
the editorial policy alone is the better trade and this file should be closed
unbuilt.
