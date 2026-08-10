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
  1. *Deciding what a number can be trusted to say* — exhibits: Lucas
     critique, The Metric Isn't Wrong, interrupted time series.
  2. *Making healthcare logic executable and auditable* — exhibits: HEDIS
     measure-level ETL patterns, CI/CD for SQL developers,
     compliance-as-architecture (thesis-framed; that post remains the private
     Stars predictor's only public surface).
  3. *Building decision surfaces people actually use* — exhibits: the Insight
     Engine method, ROI from clinical workflow data.
- Proposition gained the player-coach sentence ("I lead a small data science
  team and still build."); `build_og.py` mirrors it as `SUBTITLE_LINES` and
  `og-default.png` was regenerated.
- Funding trims: `.hero-lede` second paragraph removed; About ¶2's "Right now
  that means…" sentence removed (its HEDIS gloss moved into Case 02's deck;
  `mn-role` re-anchored to the methodology sentence).

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
| FULL (long bodies) | 10,743 | +1,200 | 18,077 |

The owner chose TIGHT explicitly, over both the cheaper INDEX (decks without
bodies assert rather than argue) and the reverted layer. **The page's
reference height is therefore 10,517px @1400px.** A future length pass should
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
