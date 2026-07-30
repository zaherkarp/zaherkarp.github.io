# Homepage ordering review

**Date:** 2026-07-30
**Branch:** `claude/resume-text-reduction-89c8ox`
**Status:** Study only. **Nothing was reordered.** No site changes in this document.

**Why this exists.** During the 2026-07-30 text-reduction work the owner said the
section ordering "doesn't make sense necessarily anymore and I'm not sure why,"
and floated moving the writing timeline to the top. Offered a choice between
reordering immediately and studying first, they chose the study, on the grounds
that ordering is where they are least sure. One ordering defect was fixed in that
pass because it was unambiguous (the writing cadence sparkline was 1,400px from
the writing list it describes); everything else is deferred to this document.

Read alongside `docs/homepage-ordering-review-2026-07-29.md`, which reordered for
*reading order* the day before. This one is about *sequence and precedence*, and
it has to respect what that pass bought.

---

## 1. Measured state

Heights and the screen each block *starts* on, at four viewports, 900px-tall
window. Measured in headless Chromium against `index.html` at commit `1a6636f`
for the first pass through this table; the `#education` row and the Gantt
figure's height were re-measured after `#education` was ALSO disabled ~20
minutes later that afternoon (§7d of the text-reduction record), and the table
below reflects that final state so it does not go stale on arrival.

| block | head | 1400px | 1000px | 761px | 390px |
|---|---|---|---|---|---|
| header/nav | | 45 / 0.1 | 45 / 0.1 | 45 / 0.1 | 45 / 0.1 |
| `.nameplate` | | 36 / 0.2 | 36 / 0.2 | 36 / 0.2 | 36 / 0.2 |
| `.proposition` | | 35 / 0.2 | 35 / 0.2 | 35 / 0.2 | 62 / 0.2 |
| `.hero-lede` | | 166 / 0.3 | 166 / 0.3 | 166 / 0.3 | 354 / 0.3 |
| `.split-hero` | Recent writing | 871 / 0.5 | 1153 / 0.5 | 1496 / 0.5 | **2900 / 0.8** |
| `.timeline` | career band | 546 / 1.5 | 411 / 1.9 | 327 / 2.2 | 603 / 4.0 |
| **`#experience`** | Experience | **2419 / 2.3** | 2815 / 2.4 | 3633 / 2.7 | **4301 / 4.8** |
| `#projects` | Projects | 903 / 5.1 | 964 / 5.7 | 1114 / 6.9 | 1311 / 9.7 |
| `.fold` | More projects (4) | 34 / 6.1 | 34 / 6.8 | 34 / 8.2 | 34 / 11.2 |
| `#about` | About | 497 / 6.3 | 610 / 6.9 | 798 / 8.3 | 1061 / 11.4 |
| `.fullwidth` | academic dot plot | 379 / 6.9 | 319 / 7.7 | 264 / 9.3 | 307 / 12.7 |
| `#publications` | Publications | 284 / 7.4 | 386 / 8.1 | 451 / 9.7 | 515 / 13.1 |
| `#speaking` | Speaking | 244 / 7.8 | 320 / 8.7 | 553 / 10.3 | 696 / 13.7 |
| `.gantt-figure` | Education + service | 546 / 8.2 | 546 / 9.2 | 542 / 11.0 | 473 / 14.6 |
| `#testimonials` | Testimonials | 780 / 9.0 | 872 / 9.9 | 1015 / 11.7 | 1169 / 15.3 |
| `#contact` | Contact | 355 / 9.9 | 355 / 11.0 | 355 / 13.0 | 385 / 16.7 |
| `.site-footer` | | 76 / 10.4 | 76 / 11.4 | 76 / 13.4 | 100 / 17.2 |

Page totals: **9,518px / 10.6 screens** at 1400px; 10,444 / 11.6 at 1000px;
12,242 / 13.6 at 761px; **15,642px / 17.4 screens** at 390px.

`#service` AND `#education` are both absent from this table: both were disabled
the same afternoon (§7c and §7d of `docs/experience-text-reduction-2026-07-30.md`)
once the Gantt's chart labels were found to already state every entry's title
and date. The Gantt figure is now the visible surface for both, and carries
both anchors.

### The mobile picture is a different problem

At 390px, `.split-hero` is **2,900px (3.2 screens)** and `#experience` is
**4,301px (4.8 screens)**. Those two blocks are **45% of the mobile page**, and a
phone reader passes through eight screens of them before reaching Projects at
9.7. At 1400px the same two are 34%.

**Any ordering proposal has to be evaluated at 390px separately.** The desktop
order and the mobile order are not the same document.

---

## 2. Inbound-link and nav-target map

| id | homepage nav / body | blog nav (~250 pages) | other |
|---|---|---|---|
| `#writing-hero` | **nav** | — | — |
| `#work` | **nav** | — | — |
| `#about` | **nav** | yes | — |
| `#contact` | **nav** | yes | — |
| `#experience` | — | yes | — |
| `#projects` | — | yes | — |
| `#publications` | — | yes | 6 dot-plot links → `#pub-*` inside it |
| `#speaking` | — | yes | — |
| `#education` | — | yes | anchor sits on the Gantt (section disabled 2026-07-30) |
| `#service` | — | yes | anchor sits on the Gantt (section disabled 2026-07-30) |
| `#exp-bha` … `#exp-sustainable` | 10 career-arc band links | — | — |
| **`#testimonials`** | **none** | **none** | **none** |
| `#writing` | none | none | bare anchor kept for external bookmarks |

Verified: **every blog-nav target resolves to a live id.** The homepage nav is 4
items; the blog nav is still **9**, and has never been cut to match — noted as a
finding below, not proposed here.

### The constraint the 2026-07-29 pass bought, and this study must not spend

All four homepage nav targets appear **in nav order down the page**:
`#writing-hero` (0.5) < `#work`/`#experience` (2.3) < `#about` (6.3) <
`#contact` (9.9). That property cost a full iteration to obtain (G1 in the
2026-07-29 review). **Any move that breaks it must say so explicitly and
justify it**, rather than discovering it later.

### The pattern already in force: figure before the section it summarizes

Two pairs remain live: the academic dot plot (6.9) before `#publications` (7.4);
and the career band (1.5) before `#experience` (2.3). The third instance, the
Gantt before `#education`, was retired as a *pair* on 2026-07-30 when
`#education` itself was disabled (§7d of the text-reduction record) — the
Gantt is no longer a figure *preceding a section it summarizes*, it is now the
*only* visible surface for that content, for both education and service. That
is a stronger move than the pattern this note originally described, not an
exception to it.

---

## 3. Candidate moves

Each carries both panels. Recommendation is stated only where the panels
converge; where they do not, the disagreement is the finding.

### M1. Projects above Experience

**The case.** `#projects` starts at screen 5.1 desktop, **9.7 mobile**. The
reception rounds were consistent that a reader deciding in seconds never reaches
it, and that the work built matters more than the job history.

**Focus Group.** Recruiter: *"I never scrolled past screen three, which meant I
never saw a single project."* Director of Quality Analytics: wants roles early
and already got that in the 2026-07-29 pass, but says a 2,419px Experience
functions as a wall regardless of where it starts. Hiring manager on a phone:
Projects at screen 9.7 does not exist.

**Design Council.** Steve supports: show what was built, then the history that
explains it. Edward and Jess object that the career band was deliberately placed
to *lead into* Experience, and `#about`'s methodology paragraph was moved in the
2026-07-29 pass specifically to preface the academic record — a Projects/
Experience swap re-opens sequencing that was just settled. Massimo notes the
swap costs nothing typographically.

**Cost, stated plainly.** Breaks the nav-order property: `work` → `#experience`
would land *after* Projects while still sitting before `about` in the nav.
Requires re-pointing the `#work` anchor and rewriting the CLAUDE.md §Layout
nav-order contract. The project CSS counter is safe — it resets on `#main`, so
DOM order still drives 01/02.

**Alternative that costs nothing.** Shrinking Experience moves Projects up
without moving anything. Modelled: Experience at ~1,300px would put Projects at
**screen 4.2** instead of 5.1, About at 5.4. The 2026-07-30 passes already took
Experience 2,836 → 2,419px, which moved Projects from 5.8 to 5.1 with zero
reordering.

**Verdict: unresolved, and deliberately so.** The panels split on whether the
sequencing settled yesterday should be re-opened one day later. My own read: try
the zero-cost lever (a shorter Experience) before spending the nav-order
property, because the two are substitutes for the same goal.

### M2. Testimonials

**Measured:** 780px desktop, **1,169px mobile**, starting at screen 9.0 / 15.3.
**Zero inbound links** from anywhere — nav, body, blog, or figure. Three quotes,
each behind its own `<details>`, i.e. 3 of the page's **8** live folds (down
from 10 after Experience's third fold and both Education's and Service's went
dark on 2026-07-30; see the text-reduction record).

**Focus Group.** Unanimous that they are never reached. The emotional-register
reader wants *one* quote where it can be seen rather than three where they
cannot. Antagonist: third-party testimony is credibility, but only if read.

**Design Council.** Jess: three folded quotes at screen 9.0 is the page's
clearest instance of paying full structural price for content nobody consumes.
Steve: no inbound links plus late position equals dead weight. Edward: the
existing note in CLAUDE.md §Testimonials calls the set "intentional and
complete," so this is a documented decision to re-open, not a gap.

**Convergent recommendation, both panels:** this is the strongest ordering *and*
length candidate on the page. Either promote one short quote to somewhere it is
read, or reduce the three folds to two inline short quotes and cut ~480px. The
owner declined this once during the second pass; it is recorded here because the
measurement makes it the highest-value remaining move, not to re-litigate it.

**Correction, same day, after the owner pushed back on "no value."** The
declined summary above undersold the content and needs its own correction, not
just a repeat of the position argument. Two of the three quotes are named,
titled, third-party corroboration, not generic praise: Jessica McCay (Director
of Customer Success, Health Catalyst) states, in her own words, the exact
claims the `#experience` Health Catalyst entry makes — sole engineer across
Cerner/Epic/athenahealth/Veradigm, the Sisense-to-Pop-Insights migration,
pushing back to protect data integrity. William Barber's quote is a
deliberate pair with the Sustainable Clarity entry's "managed up to eight
copy editors" line (documented in `CLAUDE.md` §Testimonials). **The content is
real corroborating evidence, not filler; the diagnosis is that its position
wastes it, not that it lacks value.** A concrete idea that follows from that
diagnosis and was NOT in the original assessment: move a short, unfolded
McCay pull-quote into the `#experience` Health Catalyst entry itself, right
where the antagonist archetype already wants third-party proof, and leave
`#testimonials` exactly as it is for a reader who wants all three. Offered to
the owner 2026-07-30; **declined** — no site change made. Recorded so the next
person to read this table does not re-derive "no value" from the position
argument alone; the position argument and the value argument are different
claims, and only the first one is true.

### M3. The orphaned projects-index fold — DONE, and not as trivial as assessed

`.fold` ("More projects (4)") is a **top-level sibling of `main`** sitting
between `#projects` (ends 6.1) and `#about` (6.3) — 34px of disclosure control
outside the section whose content it holds.

**Both panels agreed, no dissent:** it belongs inside `#projects`. Steve calls it
a control with no visible parent; Massimo, a rhythm break between two sections.
Assessed here as **low risk** on the grounds that the CSS counter resets on
`#main`, so moving the fold does not disturb project numbering.

**That counter check was right; the width check was missing, and it mattered.**
Before implementing, `section { width: 60% }` and `.projects-index { max-width:
90% }` were checked together: nesting `.projects-index` literally inside
`<section id="projects">` would have resolved its 90% against the section's own
60%-wide box, rendering the grid at ~54% of the page instead of 90% — a real
visual regression this document's "lowest risk" label did not anticipate.

**Fix applied:** `id="projects"` moved off the `<section>` onto a new outer
`<div id="projects">` (no width rule of its own) that wraps both the un-id'd
`<section>` (unaffected, still 60%) and the fold+grid (unaffected, still 90% of
the new outer div rather than of the column). Verified pixel-identical before
and after at three viewports: 773px/1159px, 416px/624px, 322px/322px
(section/grid). Full details in `CLAUDE.md` §Project numbering and layout.

**The lesson for the rest of this document's recommendations:** "lowest risk"
in a table cell is a claim, not a fact, until it is checked against the actual
CSS. Treat every remaining recommendation here (M1, M2) the same way before
implementing — re-verify the specific mechanism, not just the general shape of
the change.

### M4. About's position

`#about` sits at screen 6.3, moved there deliberately by the 2026-07-29 pass
(G1) so its methodology paragraph prefaces the academic record and so the nav
targets fall in nav order.

**Focus Group.** The hiring manager's 2026-07-29 comment stands recorded and
unchanged: *"About at position 11 is far down, I'd never get there. I also never
did."* Recruiter: does not read About essays at all.

**Design Council.** Edward and Jess: the placement is load-bearing for two
properties simultaneously; moving it costs both. Steve: a reader who wants to
know who this is should not hunt to screen 6.

**Verdict: leave it.** Both panels acknowledge the tension, and neither proposes
a move that keeps the nav-order property. The 2026-07-29 decision record already
holds this argument; re-opening it needs a new reason, not a repeat of the old
one.

### M5. The writing timeline — the owner's original instinct

**Resolved, and already fixed.** The writing *list* was already first (screen
0.5). What was misplaced was its **cadence sparkline**, stranded at screen 2.3
with the 546px career band between the two halves of one idea. Moved into
`.hero-writing` on 2026-07-30. Recorded here because it was the question that
prompted this study and the answer was not what the question assumed.

Note the likely source of the confusion: `.timeline` at screen 1.5 is the
**career** band, not a writing timeline. Two different figures.

### M6. The hero itself, on mobile

At 390px `.split-hero` is 2,900px — **3.2 screens before the career band**. The
2026-07-26 iteration booked hero-column length as an accepted cost and its §6
predicted it would return; the 2026-07-29 antagonist round predicted the same.

**This is the third document to log it.** It is not an ordering problem — moving
the hero cannot help, it is already first — it is a length problem inside a block
whose order is correct. Flagged for a length pass, explicitly out of scope here.

---

## 4. Summary

| # | Move | Panels | Recommendation |
|---|---|---|---|
| M3 | Projects-index fold into `#projects` | agree | **Done** 2026-07-30 (not as simple as scored — see M3) |
| M2 | Testimonials: promote one or cut to two | agree | Real value, wasted by position. Owner declined twice (cut, then promote-one) |
| M1 | Projects above Experience | **split** | Try the shorter-Experience substitute first |
| M4 | About earlier | tension, no proposal | Leave; 2026-07-29 decision stands |
| M5 | Writing cadence orphan | agree | **Done** 2026-07-30 |
| M6 | Hero length at 390px | agree it is real | Length pass, not ordering |
| M7 | Education + Service, both redundant with the Gantt | agree | **Done** 2026-07-30 |

**Nothing in this document has been applied.** M5 and M7 were fixed in passes
that preceded this study (§7c/§7d of the text-reduction record); M3 and M2 are
proposals awaiting a decision. M7 is included for completeness even though it
was not discovered *by* this study — it followed the same figure-precedes-
content logic in §2's convention note, and it removed the third instance of
that pattern this document originally described.

## 5. Findings that are not ordering moves

- **The blog nav still has 9 items** (`scripts/templates/blog/base.html:43-52`)
  while the homepage nav was cut to 4 in the 2026-07-26 iteration for reasons
  that apply equally to both. Never revisited. Changing it rebuilds ~250 pages.
- **`#testimonials` has no inbound link from anywhere.** Combined with
  `#publications`, `#speaking`, `#education`, and `#service` being reachable only
  from the blog nav, five of the page's sections have no homepage-internal path
  now that `.hero-more` is gone. That was an accepted cost when the line was
  removed; it is worth re-checking as a set rather than one at a time.
- **`lint_links` cannot see blog→homepage fragments.** It validates index.html's
  own fragments and homepage→blog links only. Since the blog nav is the *sole*
  inbound path for five sections, any future section rename or removal breaks
  ~250 pages with CI green. This bit twice already on 2026-07-30, once for
  `#service` and once for `#education`, and was caught by hand both times.
