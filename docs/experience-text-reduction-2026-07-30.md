# Experience text reduction, Certifications disabled

**Date:** 2026-07-30
**Branch:** `claude/resume-text-reduction-89c8ox`
**Owner request:** dramatically reduce the text in the Experience section, and
comment out Certifications so it survives in the file and through the
pipelines but no longer renders.

---

## 1. What was measured first

Per CLAUDE.md §Agent panels ("render before arguing about a rendered thing"),
the section was measured before anything was cut.

| Role | Lead | Fold | Figcaption | Notes | Total |
|---|---|---|---|---|---|
| BHA (`exp-bha`) | 56 | 286 | — | 35 | 342 |
| Health Catalyst (`exp-catalyst`) | 104 | 225 | 20 | 60 | 349 |
| healthfinch (`exp-healthfinch`) | 64 | 57 | 39 | 0 | 160 |
| UW (`exp-uw`) | 70 | 124 | — | 16 | 194 |
| Sustainable Clarity (`exp-sustainable`) | 52 | 0 | — | 0 | 52 |

**Experience was 1,209 words of a 3,609-word page — 35% of the homepage.**
**698 of those words (58% of the section) were behind closed `<details>`.**

That second number is the one that governs everything below.

---

## 2. Panel synthesis

Both panels were convened together, per the 2026-07-28 owner decision.

### Reception findings (Focus Group)

- **Recruiter, forty portfolios a week:** never opened a single "More detail."
  Five in a row read as five tasks, and none got done. What was retained: two
  bar charts and the number 373,000.
- **Director of Quality Analytics, regional MA plan:** the BHA lead is the best
  writing on the page. The Technical Notes paragraph beneath it explains her own
  job back to her.
- **Hiring manager:** five roles in identical shape means nothing is
  foregrounded. Sustainable Clarity gets 52 words and BHA gets 342, but with the
  folds closed they look like siblings. The proportion the page *shows* is not
  the proportion that matters.
- **Principal payer-analytics engineer (antagonist):** the Huber ψ-function is
  the most credible thing here and it is two clicks deep. Either it is
  load-bearing evidence and belongs in view, or it is a flex and should go.
  Buried is the one option that earns neither.
- **Former CMS measure developer (antagonist):** the three Health Catalyst
  customer-outcome *links* are the only third-party verification on the page. If
  one fold survives, that is the one.
- **Emotional-register reader:** "the infrastructure did not exist when I
  arrived" does more work than the 286 words under BHA. There are four sentences
  like it, diluted by ~900 forgettable ones.

### Design findings (Design Council)

- **Jess (editorial, leading):** the fold prose is *scope description*, not
  decision-writing, and `resume.md` already carries it. Every fold's opening
  clause restates its lead. The register rule protects long-form prose that
  explains decisions; it does not protect volume. Cutting here makes the section
  *more* compliant with the register, not less.
- **Edward:** more than half a section being invisible by default is deferral,
  not restraint. Keep both outcome figures; cutting prose around them raises the
  data-ink ratio, which is what they are for.
- **Steve:** five identical disclosure controls train the reader that the page
  has a hidden layer they are responsible for.
- **Massimo:** the `<hr>` / h3 / meta rhythm is what makes five roles legible as
  five roles, and it survives any prose cut.
- **Haben:** every retired fold is one fewer control in the tab order. No AA
  concern; no objection.
- **Luke:** supports the deepest cut on offer.

### Where the panels conflicted

Reception wanted the BHA fold gone. The repo's own contracts said it could not
simply be deleted:

1. **CLAUDE.md §Stars tools distinction** named that fold as one of exactly two
   public surfaces describing the internal client-side Stars predictor.
2. **The Huber ψ caption** is a canonical §Calibrated claims example, and the
   antagonist round wanted it *promoted*, not deleted.

Resolution: retire the fold, preserve the Stars-predictor pattern as one clause
in the visible lead, and promote the formula into visible prose.

---

## 3. Decisions

Owner selected, from three costed options:

- **Depth: Option C, selective.** Retire the BHA, healthfinch, and UW folds.
  Keep the Health Catalyst fold, renamed **"Published customer outcomes"** —
  with one fold left, a generic label is precisely the defect
  `critiques/critique-index-2026-07-04.md:116` raised.
- **Huber formula: promote to visible.** Caption kept verbatim.
- **Overflow valve: yes.** A closing pointer to `/resume.html` and `/cv.html`,
  and the hero's `.hero-more` link retitled from "full experience" to
  "experience".

Also applied: the `sn-tech-notes` and `sn-medallion` sidenotes went with their
host paragraphs (two fewer toggles in the tab order; Experience keeps `sn-ehrs`
and the two `.stat-num` stats); `cut weekly load latency by 24+ hours` and the
`$1M` recurring-revenue figure were pulled up into their leads so they survived
their folds; the healthfinch figcaption was trimmed 39 → ~26 words.

---

## 4. Result, and the number that is easy to misread

| | Before | After | Change |
|---|---|---|---|
| Section total | 1,209 w | ~570 w | **−53%** |
| Behind closed folds | 698 w | 42 w | −94% |
| Folds in Experience | 4 | 1 | −3 |
| Note toggles in Experience | 5 | 3 | −2 |
| Outcome figures | 2 | 2 | unchanged |

Rendered, measured in headless Chromium:

| Viewport | `#experience` height | Full page height |
|---|---|---|
| 1400px | 2884 → **2836px** (−1.7%) | 11028 → **10709px** (−2.9%) |
| 1000px | 3355 → **3269px** (−2.6%) | 12142 → **11748px** (−3.2%) |
| 761px | 4230 → **4206px** (−0.6%) | 14175 → **13805px** (−2.6%) |
| 390px | 4995 → **4881px** (−2.3%) | 17786 → **17252px** (−3.0%) |

**The content fell 53%; the rendered default height fell about 2%.** These are
not in tension — 58% of the section was already invisible, so retiring folds is
a content cut, not a page-length cut. Two of the approved changes (promoting the
formula, adding the resume/CV pointer) *added* visible words, which is why the
default view did not shrink proportionally.

**Consequence for future work:** anyone asked for a visibly shorter Experience
should start from the five lead paragraphs (~300 visible words), the two
figcaptions, the promoted formula caption, and the three margin notes — not the
folds, which are now nearly empty. And they should measure, not estimate.

---

## 5. Certifications

`<section id="certifications">` is wrapped in an HTML comment, with the
trailing `<hr>` inside the wrap. `src/content/cv.md ## Certifications` is now
the live record.

Safe to disable, verified rather than assumed: **zero** scripts reference the
section (`grep -rni certification scripts/` is empty), it has **no inbound
`href`** anywhere, and it carries **no classes**, so only generic
`section`/`h2`/`p` rules applied and no CSS went dead. An HTML comment rather
than `display: none` was the owner's instruction and is also correct — the
content leaves the DOM entirely, so it is not read by screen readers, not
indexed, and not printed.

### Two defects this produced, and how they were caught

1. **The explanatory banner terminated itself.** It originally contained the
   literal strings for the comment delimiters and an `<hr>`, written as prose in
   the restore instructions. Comments cannot nest, so the first close sequence
   ended the banner early and dumped its remaining text onto the page as live
   markup: a spurious `<hr>` rendered, and a long unbroken row of equals signs
   overflowed the page horizontally at 761px and below.
2. **The trailing `<hr>` has to be inside the disabled region.** An `<hr>`
   already sits above the banner, so disabling the section alone leaves two
   adjacent rules between `#service` and `#testimonials`.

**`lint_html` was green for both.** The broken result was structurally valid
HTML — merely wrong. `lint_links`, `lint_vocab`, and every other gate passed
too. Only a headless render caught either one, via an explicit assertion that
exactly one `<hr>` sits between `#service` and `#testimonials` and that
`document.documentElement.scrollWidth` does not exceed the viewport. This is the
"render before arguing about a rendered thing" rule applying to *verification*,
not just to design argument.

---

## 6. Verification performed

- All twelve gate linters clean.
- All five pre-push guard steps pass. Em-dash count 0; accent count **14** of
  the 20 cap (unchanged — both outcome figures keep their `#7a0000` sentinels).
- `pytest scripts/tests/` — 144 passed.
- Headless Chromium at 1400 / 1000 / 761 / 390px, asserting: Certifications
  absent from the DOM and its text absent from `body.innerText`; exactly one
  `<hr>` between `#service` and `#testimonials`; exactly one `<details>` in
  `#experience`; all five `#exp-*` anchors resolving; no horizontal overflow.

## 7. Contracts updated in the same change

`CLAUDE.md` §Experience entry expand rule, §Stars tools distinction (surface (a)
is now the BHA lead, not its fold), §Certifications, plus a new dated status
entry. `README.md` fold count 11 → 9, which also corrects the stale count
`docs/qa-audit-2026-07-28.md:272-273` had already flagged. Two stale
`index.html` comment blocks were rewritten: the `EXPERIENCE - HEALTH CATALYST
ENTRY` banner (already reported wrong at
`docs/qa-audit-2026-07-28.md:70-73`) and the `#service` banner's
"Certifications live in their own collapsed section below" cross-reference.

## 8. Found, not fixed

`CLAUDE.md:830`, the whole `### .exp-stack contrast` subsection around
`CLAUDE.md:1070-1076`, and `docs/pipelines.md:669` all reference a `.exp-stack`
class that **does not exist** in `index.html`. The live selector is
`.experience .stack`. Out of scope here; worth its own pass.
