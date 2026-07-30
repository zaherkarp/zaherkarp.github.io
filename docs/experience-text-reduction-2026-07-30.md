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

## 7b. Second pass, same day: the visible-layer cut

The owner reversed the stop-here decision within the hour: *"I need things to be
shorter. Its too much to provide value since it probably scares people away."*
That is a reception argument, not a taste call, so it goes to the Focus Group's
lane, and the panels were convened jointly on the whole page rather than on
Experience alone.

### What the page-level measurement showed

Page was **10,709px = 11.9 screens, 1,834 visible words**, with `#experience` at
**31%** of it. Panels agreed the problem was page-level, not section-level.

### Reception findings

The recruiter round never scrolled past screen three, which meant never seeing a
single project (Projects began at screen 5.8). The antagonist round put it
sharpest: *"Cut half of this and I'd trust it more, not less. Length reads as
insecurity."* All six reception panelists independently rejected the
`.hero-more` line: its four targets sat 3 to 9 screens away, a promise the
scroll cannot keep.

### Applied

Every lead cut to ~35-55 words; the Huber formula returned to a named fold; the
healthfinch outcome figure removed with its facts moved into prose; `sn-ehrs`
dropped; `.hero-more` deleted entirely (markup, CSS, print rule); the cadence
sparkline moved into `.hero-writing` and `<section id="writing">` retired.

| | Before pass 1 | After pass 1 | After pass 2 |
|---|---|---|---|
| Page height @1400px | 11,028px | 10,709px | **10,033px** |
| Screens @900px | 12.3 | 11.9 | **11.1** |
| Visible words | — | 1,834 | **1,665** |
| `#experience` | 2,884px | 2,836px | **2,419px** |
| Mobile @390px | 17,786px | 17,252px | **16,345px** |
| Accent uses | 14 | 14 | **12** |

Per-role: BHA 490px, Health Catalyst 684px, healthfinch 456px, UW 445px,
Sustainable Clarity 290px.

### Declined, and why

**Testimonials (780px) and the Gantt figure (462px)** were both offered and not
taken. The Gantt was contested inside the Council: Jess and Steve wanted it gone
as an enforced duplicate of `#education` + `#service` (removing it would also
retire `lint_gantt.py` entirely), while Edward and Nathan argued the figures are
the page's distinguishing asset and cutting charts to buy scroll trades the
memorable thing for the thing already lost. Recorded as unresolved, not settled.

**Reordering was deliberately not done.** Reception wanted Projects above
Experience; the Council noted the 2026-07-29 pass had just spent a full
iteration getting the four nav targets into nav order. The owner chose a study
instead, so no section moved in this pass.

### Open item this pass created

Catalyst is now **29% of the section at 684px** against 445-490px for the
others, because it alone retains a figure. The asymmetry the owner originally
flagged is sharper, not resolved. Dropping the last outcome figure evens it at
~504px but leaves Experience as pure prose, undoing the 2026-06-09 answer to the
wall-of-text critique. Flagged for decision, not taken unilaterally.

## 7c. Third pass: Service disabled, Education trimmed

Owner question: can `#service` be cut while staying "active in a pipeline form
but not visible"? And does `#education` have fluff or innovatively combinable
parts? Framed honestly by the owner as hard because *"it's something I care
about."*

### The measurement that reframed it

Both sections were **already folded**. Each cost 225px at 1400px (2.2% of the
page) in `<h2>` + one-line lead + fold summary, while every `.row-entry` inside
contributed **zero pixels**. So the advice given was: this is not where the fat
is (Experience 2,419px, Projects 903px, hero 871px, Testimonials 780px), and
cutting something you care about for 2.2% is a poor trade.

### Yes, pipeline-active-but-invisible works. Verified.

`lint_recognition.py:122-124` (`SERVICE_SECTION_RE`) and
`lint_gantt.py:179-184` (`_section_body`) both slice with a raw-text
`<section id="...">` regex and **neither strips HTML comments**. After the
comment-out, `lint_gantt` still reports *"12 section entry(ies) (5 education + 7
service) reconciled against 12 figure mark(s)"*. The homepage ⊆ CV subset gate
likewise still fires. **Do not "fix" either linter to skip comments** without
replacing what it guards.

### The trap CI cannot see

All ~250 generated blog pages link to `/#education` and `/#service`
(`scripts/templates/blog/base.html:50-51`), and `lint_links` validates only
index.html's own fragments plus homepage→blog links — never blog→homepage
fragments. Commenting the section out without keeping the id would have left 250
dead nav links with every gate green. Fixed by **moving `id="service"` to sit
immediately before the Gantt figure** (verified: 0px offset), so those links land
on the chart that carries the service record. This avoided editing the nav
template and rebuilding ~250 pages.

### The merged-highlights proposal, rejected

A single prose-line section (following the retired Certifications pattern) would
run ~170px against 450px. But it has no `.row-entry` blocks, so
`lint_recognition.parse_homepage()` returns `[]` and **both gates pass
vacuously** — green while guarding nothing, the third instance of that failure
class in one day. Keeping them meaningful means re-pointing both at `cv.md` and
rewriting two test files, to beat the simple comment-out by **~55px**. Two
variants also fail: highlights-unfolded measures the same as
everything-folded, and nesting `<section id="service">` inside a merged fold
breaks the outer slice (`_section_body` is non-greedy).

### Fluff trimmed, and what was deliberately kept

Cut: the Oxford and Boot Camp notes (each restated its own title), the MPH
committee names (CV material), the mentor note's six-item skill list, the Spirit
of Charlie citation quote (the antagonist round read it as internal-recognition
language), and the Road Home / WORT org descriptions.

Kept as recognizable field credentials, on the Director archetype's objection:
**Pascale Carayon as advisor, the AHRQ-funded SEIPS training, the $18,000
grant, and Digital Fellow's 25-of-2,000 selectivity.**

Service fluff was trimmed *before* the comment-out, so a restore brings back the
clean version rather than the old one.

### Result

| | before | after |
|---|---|---|
| Page @1400px | 10,033px | **9,734px** |
| Screens @900px | 11.1 | **10.8** |
| Mobile @390px | 16,345px | **15,943px** |
| Live `.row-entry` blocks | 12 | **5** (education only) |
| Live `<hr>` between #education and #testimonials | 2 | **1** |

## 7d. Fourth pass, same afternoon: Education disabled too

Twenty minutes after the Service disable shipped, the owner asked directly:
*"isn't it redundant with the figure?"* — about Education this time. They were
right, and it exposed an inconsistency: disabling Service had made Education
*more* redundant with the Gantt, not less, and the two sections were now
getting different treatment for the same underlying reason.

### The check, done before acting

After the day's trim, the Gantt's terse chart labels already stated all five
Education entries' title AND date: "MPH, Biostatistics", "Grad Cert, Patient
Safety", "Oxford, qualitative methods", "Entrepreneurial Boot Camp", "BA,
English Literature", each positioned on the year axis. Enumerated precisely
what was NOT already in the chart: exactly two facts across the whole
five-entry fold — the MPH's $18,000 grant, and the Patient Safety entry's
Carayon-advisor / AHRQ-funding detail. Everything else, including every org
name except Oxford's (which the chart label already carries), duplicated the
figure.

### Applied

Both facts folded into the Gantt figcaption. `#education` disabled with the
identical mechanism, banner shape, and restore instructions as `#service`:
`id="education"` relocated beside `id="service"`'s anchor before the figure;
`lint_gantt`'s raw-text `_section_body` regex (no comment stripping) keeps
reconciling both lanes against the figure exactly as before —
`lint_recognition` was never in scope for `#education` to begin with, so no
coverage was lost or gained there.

### A defect this created, caught by rendering rather than inspection

Disabling three consecutive sections (education, service, certifications) all
sharing the pattern of "content, then a trailing `<hr>`" silently removed the
rule between the Gantt and Testimonials. The Gantt itself had never carried a
rule of its own — the three sections after it each supplied one on their way
out — so with all three hidden, the figure ran straight into Testimonials on a
bare 48px margin gap, the one place on the page where a section boundary had no
divider. Fixed with a single `<hr>` placed OUTSIDE all three disabled blocks,
immediately before the Testimonials banner, specifically so it is not
duplicated if any of the three sections is restored later.

### Result

| | before this pass | after |
|---|---|---|
| Page @1400px | 9,734px | **9,518px** |
| Mobile @390px | 15,943px | **15,642px** |
| Live `.row-entry` blocks | 5 (education only) | **0** |
| Live `<details>` folds, page-wide | 9 | **8** |
| `#education`/`#service` linter coverage | unchanged | unchanged (verified) |

Both sections' content survives verbatim in the file, guarded by `lint_gantt`,
restorable by deleting two lines each plus moving an anchor back. `cv.md`
remains each one's live record.

## 8. Deliberately not done: the reordering study

The owner stopped after the content cut and asked for a prompt to pick up the
*visible* streamlining later, with the panels reviewing each step. This pass is
therefore complete as scoped; the section below is the handoff, not a TODO that
this change left broken.

### Prompt for the follow-up pass

> (Partly superseded by the second pass in section 7b, which did cut the
> visible leads. What remains open from it: Testimonials, the Gantt, and the
> Catalyst asymmetry.)
>
> Streamline the **visible** text of the Experience section on `index.html`,
> with the Focus Group and Design Council reviewing each step. Read
> `docs/experience-text-reduction-2026-07-30.md` first: the 2026-07-30 pass cut
> the section's content 53% by retiring three of four folds, but its rendered
> default height fell only ~2%, because most of the section was already hidden.
> The folds are now nearly empty. **The remaining bulk is in the visible layer,
> and that is what this pass is about.**
>
> **Measure before proposing anything.** Render `index.html` in headless
> Chromium at 1400 / 1000 / 761 / 390px and record the `#experience` bounding
> height plus a per-component visible word count. As of 2026-07-30 that was:
> five lead paragraphs ~300w, two figcaptions 43w, the promoted Huber caption
> 34w, three margin notes 51w, and ~117w of structural h3 / meta / stack / h2
> that cannot be cut. Bring those numbers to the panels rather than adjectives;
> CLAUDE.md §Agent panels requires it, and this repo has already lost months to
> one argument that a single measurement settled.
>
> **Work one role at a time, and convene both panels on each** before editing
> it, per the 2026-07-28 joint-convening decision. Lead with the editorial
> voices (Jess on the Council; the recruiter, hiring-manager, and
> emotional-register archetypes on the Focus Group) but report the three-part
> synthesis: reception findings, design findings, then the conflicts, held open
> rather than collapsed. Expect real conflict here, because the prior reviews
> rate this prose as the page's **strongest asset with expert readers**
> (`docs/homepage-ordering-review-2026-07-29.md` §antagonist rounds;
> `evaluations/hiring-eval-2026-05-23.md`), and no prior critique has ever
> asked for Experience to be shorter. A cut that removes a verifiable fact is a
> loss, not a win. Do not convert the prose to bullets: CLAUDE.md's register is
> long-form prose explaining decisions, and `resume.md` already carries the
> bullet version.
>
> **Hard constraints, all mechanically enforced.** Keep all five
> `.role-anchor` spans (ten career-arc band links target them; `lint_links`
> gates it). Keep each role's bare `<h3>` and markup-free
> `<p class="meta">` in `Org · … · Mon YYYY to Present|Mon YYYY` form, and keep
> every `resume.md` employer present as a homepage org (`lint_facts`). Keep
> `id="experience"` (blog nav links `/#experience`) and `id="work"`. Numbers a
> figcaption cites must stay in that role's prose. Deleting prose is always safe
> for `lint_notes`; **lifting note text into a lead is what fails it**, so
> rewrite rather than copy-paste.
>
> **Treat these four as decisions to reopen explicitly, not copy edits.** Each
> is documented and each was argued once already: the promoted Huber ψ formula
> and its verbatim caption (a canonical §Calibrated claims example); the Stars
> cut-point clause in the BHA lead (one of only two public surfaces for that
> internal tool, per §Stars tools distinction); the two outcome figures (kept on
> purpose, since cutting prose around them is what raises the data-ink ratio);
> and the `.stat-num` margin stats. Touching any of them means updating
> CLAUDE.md in the same change.
>
> **Guard the calibrated claims.** The 2026-07-30 pass introduced two
> regressions purely through compression: "contributed to more than $1M in
> **new** recurring revenue" became "**added** more than $1M in recurring
> revenue", which claims sole causation and reads as total rather than
> incremental. Tightening prose is exactly when this happens. After each role,
> re-read the result against §Calibrated claims specifically for causation verbs
> and dropped qualifiers.
>
> **Verify by rendering, not by linting.** All twelve linters stayed green
> through a bug that leaked live markup onto the page and caused horizontal
> overflow below 761px. Assert explicitly: no horizontal overflow at any
> viewport, all five `#exp-*` anchors resolving, expected `<details>` and `<hr>`
> counts, and both colour schemes. Then run the twelve linters, the five guard
> steps, and `pytest scripts/tests/`.
>
> **Report the honest delta in both units** — content words *and* rendered
> height — and update CLAUDE.md §Experience entry expand rule, which currently
> records the 2836px figure as the baseline.

## 9. Found, not fixed

`CLAUDE.md:830`, the whole `### .exp-stack contrast` subsection around
`CLAUDE.md:1070-1076`, and `docs/pipelines.md:669` all reference a `.exp-stack`
class that **does not exist** in `index.html`. The live selector is
`.experience .stack`. Out of scope here; worth its own pass.
