# The case layer: decision record (2026-08-10)

The owner commissioned an information-architecture review of a proposed
"Systems for Consequential Decisions" case-file architecture, with an explicit
Gate 0 (independently compare it against credible alternatives before
adopting), a forced joint Focus Group / Design Council convening, an
adversarial review of each proposed case, and interview rounds before any
edit. This document is the durable record: what was decided, what was
measured, and what a future pass must not silently reopen.

## 1. Gate 0 verdict

**B: adopt with modifications.** The case-file direction won against five
alternatives (career-braid, leader-builder, Medicare-domain-authority, short
front page + deep pages, refine-current) for two reasons on the repo's own
record:

- `evaluations/hiring-eval-2026-05-23.md:302` found the page "reads manager +
  director + staff-IC at once… It cannot be both." The failure mechanism named
  there is HEDGING inside one undifferentiated narrative. The case layer
  answers by SEPARATION: one claim per case at one altitude (judgment /
  execution / adoption), so the dual Director-track + Principal-track
  objective is served additively rather than averaged.
- `docs/homepage-critique-2026-07-19.md:226-231` parked a Tier-1 "audience
  question" (Tufte's hour-long reader vs the recruiter) that gated several
  items. The case layer is the answer: it is the 60-second reader's surface;
  the record beneath stays the hour-long reader's. That question should be
  treated as RESOLVED by this pass.

Runner-up was refine-current (it leaves synthesis to a reader the eval record
proves does not do it). Honest ceiling, stated at the time and preserved
here: architecture cannot make a Director-of-20 candidacy out of a
manager-of-two record; the realistic positioning is Senior Manager /
Director-adjacent plus Principal/Lead.

## 2. What shipped

- `<section class="cases">` between the career band's closing rule and
  `#experience`; `#work` anchor MOVED onto it (nav-order property verified
  intact: `#writing-hero` < `#work` < `#about` < `#contact`). CSS section 23.
- Three cases, TIGHT form (h3 + muted deck + one ~45-word body + a 0.95rem
  exhibits row):
  1. *What a number can be trusted to say* — exhibits: Lucas
     critique, The Metric Isn't Wrong, interrupted time series.
  2. *From specification to running code* — exhibits: HEDIS
     measure-level ETL patterns, CI/CD for SQL developers,
     compliance-as-architecture (thesis-framed; that post remains the private
     Stars predictor's only public surface).
  3. *Whether anyone uses it* — exhibits: the Insight
     Engine method, ROI from clinical workflow data.
- Proposition gained the player-coach sentence ("I lead a small data science
  team and still build."); `build_og.py` mirrors it as `SUBTITLE_LINES` and
  `og-default.png` was regenerated.
- Funding trims: `.hero-lede` second paragraph removed; About ¶2's "Right now
  that means…" sentence removed (its HEDIS gloss moved into the case layer,
  and since §8 lives in Case 02's BODY, not its deck; `mn-role` re-anchored to
  the methodology sentence). The layer is now the page's only home for that
  expansion, so a future edit must not drop it.

## 3. Interview decisions (owner, 2026-08-10)

| Decision | Choice |
|---|---|
| Case-layer relationship | Annotate-light (reorganize and replace both declined) |
| BHA evidence boundary | Repo-public only; BHA present tense stays number-free |
| "Daily Briefing" | Corrected: it is the PUBLIC Daily Briefing tab of the live Insight Engine feed (verified against the live page), not an internal surface |
| HC-era scope | Function lead, no direct reports; the McCay "only engineer" testimonial corroborates player-coach rather than contradicting a people-manager claim |
| Hero | Player-coach clause added to the proposition |
| Case 02 anchor | Prior-era public numbers only (50+ health systems surfaced from resume.md; the migration referenced without restating the 24+ hours already in the Health Catalyst lead) |
| Writing exhibits | The eight-link set above, including compliance-as-architecture |
| Writing index | Stays at six titles (the §6 cap-at-four lever deliberately NOT taken) |
| ECDS Shock Index | Demoted to index-reachable writing; not a case exhibit (asserted, unvalidated index) |

## 4. The budget decision (the one a future pass must not misread)

The plan's original gate was net-zero height at 1400px. It was measured as
unreachable: every real form of the layer costs more than the legitimate
funding cuts (~135px) could cover. All three variants were built and measured
in headless Chromium (animations disabled, served from the repo root):

| Variant | @1400px | delta vs 9,543 baseline | @390px |
|---|---|---|---|
| Baseline (pre-change) | 9,543 | — | 15,754 |
| INDEX (no bodies) | 10,075 | +532 | 16,485 |
| **TIGHT (shipped)** | **10,517** | **+974** | **17,566** |
| TIGHT, de-templated (current) | **10,498** | +955 | **17,479** |
| FULL (long bodies) | 10,743 | +1,200 | 18,077 |

The owner chose TIGHT explicitly, over both the cheaper INDEX (decks without
bodies assert rather than argue) and the reverted layer. **The page's
reference height is therefore 10,498px @1400px** (10,517 as first shipped,
less 19px from the de-templating pass in §8). A future length pass should
measure against that number; treating 9,5xx as the target would silently
relitigate this decision.

## 5. Verification performed

All twelve linters green (`lint_facts` confirms case h3s are invisible to its
`#experience`-scoped parser: 4 resume + 4 homepage roles). Guard greps: 0
em-dashes, accent count 12 of the 20 cap, no SVG-in-p leaks, sim.py compiles.
`pytest scripts/tests/`: 152 passed, 1 skipped (WeasyPrint/libpango
self-skip). Rendered audit at 1400/390, light and dark: nav targets monotonic
in nav order; all case anchor hrefs resolve; exactly one `<hr>` on each side
of the layer; heading outline h1 → h2 → h3 preserved; project counter still
renders 01-06; proposition wraps to two balanced lines; no horizontal
overflow at either width; zero page errors (the lone console line is the
sandboxed GoatCounter fetch). Screenshots archived in the session scratchpad.

## 6. Rollback

Branch point (before): `659cda9` on `claude/zaherkarp-ia-review-v96881`.
The layer is a contiguous block, so the two-line comment-out pattern
documented in `docs/experience-text-reduction-2026-07-30.md` §10 applies: the
section can be disabled without touching git history, and the comment-blind
linters are unaffected (none of them parse the case layer). Reverting the
proposition means also reverting `build_og.py`'s `SUBTITLE_LINES` and
regenerating `og-default.png`, or the social card and the page disagree.

## 7. Deliberately not done

- No BHA production number (owner kept the door closed; the one open Tier-1
  item from `reviews/2026-05-23-synthesis.md:106` stays open by choice).
- No testimonial relocation (owner declined twice previously; never bundled).
- No nav change, no new figures, no accent use, no notes in the layer.
- The two draft Stars posts (final-rule ballast / three live rulebooks) are
  not cited; if they publish later they are natural Case 01/02 exhibits.
- The writing-index cap-at-four lever (`docs/homepage-iteration-2026-07-26.md`
  §6) remains open and untaken.

## 8. The de-templating pass (same day, after the owner read it)

The owner's reaction to the shipped layer was that "The work, in three
arguments" seemed canned, and asked for panel guidance. Both panels were
convened jointly. The finding that mattered was not the heading: **seven
strings were in lockstep** — three gerund-led h3s (Deciding / Making /
Building), two decks sharing the verb phrase "turned into", three identical
"In writing:" labels, and all three decks verbless. The h2 was the visible
top of that stack, so fixing it alone would have left the template intact.

Evidence the panels argued from, recorded because it cuts both ways:

- **Against the heading.** All thirteen other h2s on the page are one or two
  bare nouns; eleven are single words. Massimo's own prior ruling
  (`docs/homepage-ordering-review-2026-07-29.md:304`) is "headings stay two
  words, not sentences." At 390px the five-word heading wrapped to two lines.
- **For it, and not suppressed.** `The robust smoothing, in one formula` — the
  Huber fold summary — is the *identical* construction, and it is this repo's
  own accepted answer to the fold-label critique
  (`critiques/critique-index-2026-07-04.md:116`). The idiom is native to the
  page at `<summary>` altitude, where a label's job is naming hidden contents.
  The panels distinguished altitude rather than declaring the construction
  bad: at h2 the job is marking a boundary, and the layer already framed three
  times (h2, deck, body) before a claim landed.
- **Voice evidence.** Across 24 recent posts the owner's own title voice is
  assertive and verb-driven, making falsifiable statements about named things
  ("BTEQ Still Has a Job"). "The work, in three arguments" is rhetorical
  framing that names nothing falsifiable — a different flaw from being clever,
  and the reason the fix moves claims into prose and leaves headings quiet.

Changes, all copy-only (no ids, CSS, marker regions, or generated output):

| | Before | After |
|---|---|---|
| h2 | The work, in three arguments | **How I work** |
| h3 01 | Deciding what a number can be trusted to say | **What a number can be trusted to say** |
| h3 02 | Making healthcare logic executable and auditable | **From specification to running code** |
| h3 03 | Building decision surfaces people actually use | **Whether anyone uses it** |
| decks | two shared "turned into"; deck 02 carried the HEDIS gloss | three distinct constructions; gloss moved to Case 02's body |
| Case 03 body | "Player-coach is the honest description: two data scientists…" | "Two data scientists today, eight editors once, hands still in the code." |

Three notes for whoever edits this next:

1. **"How I work" is three words and knowingly breaks Massimo's two-word
   rule.** The owner chose it over the bare-noun "Work" because it is first
   person, matches the site's voice, and describes what the three blocks
   actually are. Do not "correct" it to a bare noun without reopening that.
2. **The h3s are deliberately in three different grammatical shapes** (noun
   clause / prepositional phrase / subordinate clause) and read as a sequence
   — "it" in the third refers back to "running code" in the second. Restoring
   a matched mold across all three re-creates the defect this pass removed.
   Treat "no shared grammatical mold across the cases" as a contract.
3. **The three identical "In writing:" labels were kept on purpose.**
   Functional labels earn repetition (contact rows and fold summaries do the
   same); rhetorical structures do not. That is the line, and it is not an
   oversight to finish later.

Also flagged by the panels and NOT acted on: the reception read that Case 03's
kept phrasing still leans on resume language, and Nathan's objection that any
quieter heading weakens the cue that the three blocks are one set. Both were
judged acceptable against the owner's selections.

Verification after the pass: page 10,517px → **10,498px @1400px** (17,566 →
17,479 @390px), visible words 1,896 → 1,873. All twelve linters green, full
guard checks clean, `pytest scripts/tests/` 152 passed / 1 skipped, rendered
re-check at 1400 light+dark and 390 confirming the heading no longer wraps on
mobile and the outline, anchors, and nav order are unchanged.
