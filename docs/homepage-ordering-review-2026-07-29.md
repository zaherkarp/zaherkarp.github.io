# Homepage text-ordering review and fix plan, 2026-07-29

**What this is.** The owner reported that "the ordering of text in the page
seems wrong, it doesn't make sense." This document is the evaluation of that
complaint against `index.html` and the complete, pre-approved fix plan for a
follow-up implementation session to execute. It changes nothing itself:
`index.html` is untouched by the commit that adds this file.

**State pinned.** All line numbers refer to `index.html` at commit `15d93bd`
("Rewrite the hero as a plain introduction, and retire the subtitle",
2026-07-29), which is also the file's state at `357e282` (HEAD at review
time; the later commits touch only generated blog and resume output). Line
numbers are drift-prone; every finding is therefore also anchored by a
selector or id plus a short verbatim quote, and the implementing session
should re-locate anchors by grep on the quote, not by line number.

**Lineage.** This review is the "next review" that
`docs/homepage-iteration-2026-07-26.md` §6 requested for the thinned
`#writing` section, and it answers the composite question
`docs/backlog-review-2026-07-28.md` left open ("what is `#writing` for"):
it is the cadence strip, and it should say so honestly. House note: this
file is written em-dash-clean (commas and colons throughout, including the
H1), a deliberate deviation from the sibling docs' em-dash titles; do not
"fix" it back.

---

## 1. Context and scope

The homepage opening was rebuilt three times in four days: the Timeline
Split (2026-07-26, `77db71e`), Direction B (same day, `6ced48d`), and the
owner hero rewrite (2026-07-29, `15d93bd`). Each pass moved blocks: the
featured project into the hero, the writing list and index into the hero,
the academic dot plot to a slot before `#publications`, the testimonials to
the page ending. What no pass did was re-stitch the prose around the moved
blocks. The result is a page whose paragraphs, links, and figures keep
referring to a layout that no longer exists around them.

Scope: reading order and the text that establishes it, on `index.html`
only. Out of scope: the blog pipeline, subpages, palette, motion, and
everything §11 lists as considered and rejected.

## 2. What is NOT wrong

Verified before diagnosing, so the implementing session does not chase
ghosts:

- **No drift.** The DOM section order matches the documented Direction B
  order exactly (CLAUDE.md and `docs/homepage-iteration-2026-07-26.md` §4
  agree with the file).
- **No CSS reordering.** Zero `order:` declarations, zero
  `grid-template-areas`, zero `*-reverse` flex directions. Visual order
  equals DOM order everywhere, including the split-hero grid.
- **No structural damage.** All tags balance (11/11 sections, 85/85 divs,
  7/7 figures); no duplicated, spliced, or truncated prose anywhere.

The wrongness is editorial and architectural, not mechanical.

## 3. The current reading order

As of `15d93bd`, top to bottom:

| Pos | Block | Anchor | Line |
|---|---|---|---|
| 0 | skip link, then `<main id="main">` OPENS | `#main` | 1849-1850 |
| 1 | nav: writing, work, about, contact | `nav.top` | 1855 |
| 2 | nameplate h1 | `.nameplate` | 1878 |
| 3 | proposition + two-paragraph lede | `.proposition`, `.hero-lede` | 1897-1902 |
| 4 | split hero: recent writing (2 featured + 6-title index) and current work (project 01) | `.split-hero` | 1923-2082 |
| 5 | career timeline band | `figure.timeline.career-band` | 2105 |
| 6 | "More:" router line | `.hero-more` | 2225 |
| 7 | **About** | `#about` | 2227 |
| 8 | **Writing** (cadence sparkline only) | `#writing` | 2238 |
| 9 | work anchor + Experience | `#work`, `#experience` | 2319-2320 |
| 10 | Projects ("Featured", one project, numbered 02) | `#projects` | 2539 |
| 11 | "More projects (4)" fold (03 to 06) | `details.fold` > `.projects-index` | 2687 |
| 12 | academic dot plot | `figure.fullwidth.timeline` | 2751 |
| 13 | Publications | `#publications` | 2972 |
| 14 | Speaking | `#speaking` | 3095 |
| 15 | Education + Service Gantt | `figure.gantt-figure` | 3177 |
| 16 | Education (all inside a closed fold) | `#education` | 3298 |
| 17 | Service and Recognition (all inside a closed fold) | `#service` | 3361 |
| 18 | Certifications | `#certifications` | 3443 |
| 19 | Testimonials | `#testimonials` | 3463 |
| 20 | Contact, footer | `#contact` | 3514 |

Note position 0: the `main` landmark opens before the nav, so the nav and
the whole hero live inside `<main>`. `#main` is also the
`counter-reset: project-num` root; the hero project must stay inside it.

## 4. Findings and prescriptions

Severity-ordered. Tier A: mechanical, apply directly. Approved: structural,
resolved by the owner during the 2026-07-29 panel review (§6, §7). Exact
replacement copy for every edit is in §9; findings here carry the diagnosis
and the decision.

**F1. The nav's first link lands on an empty shell.** Anchor:
`<a href="#writing">` (1857) vs `<section id="writing">` (2238-2295), whose
entire visible content is "24 weeks [sparkline] 34 posts". The actual
writing (two featured entries, six-title index, "View all writing") lives
in `.hero-writing` (1929), which has no id. A reader clicking "writing"
scrolls PAST the writing to a stub. Fix (approved, G2): retarget the nav at
the hero column via a new `id="writing-hero"`; retitle the stub section
"Writing cadence" and give it a one-line lead (F8). The sparkline, its
`mn-cadence` note, and the `activity-grid` markers stay exactly where they
are.

**F2. Nav order contradicts page order.** Nav reads writing, work, about,
contact; the page delivers about (2227), writing (2238), work (2319),
contact (3514). Fix (approved, G1, the keystone): move
`<section id="about">` from position 7 to between the "More projects" fold
and the dot plot (current 2742/2751 boundary). After the move the four nav
targets appear in exactly nav order, and About's methodology paragraph
("grounded theory ... regression ... time series", 2232) sits directly
above the academic dot plot and Publications it describes. One move
resolves F2, F11, and the felt half of F3.

**F3. The career story is told three times in 330 lines, and the newest
telling inverts the chronology.** The hero lede (1900: "Before this, I
worked in public-health research and editorial production"), the career
band caption (2107: "Three overlapping careers converge..."), and the About
lead (2230: "I started in writing and editing...") all tell the same arc.
The lede lists research FIRST; the band (editorial 2007, research 2009) and
About both put editorial first. Fix (Tier A): swap the two nouns in the
lede, touching nothing else in the owner's sentence. G1 separates the lede
telling from the About telling by the entire work block; the band caption
stays, it captions the figure between them. Any deeper lede rewrite is a
flagged owner decision (§7), not part of this plan.

**F4. "Featured" projects open at number 02.** `#projects` (2539) shows the
subhead "Featured" (a plural label) over exactly one project, whose CSS
counter renders 02 because project 01 was moved into the hero. Readers
arriving via the "More: projects" link see a count that starts at 02,
unexplained. Fix (Tier A): one bridging sentence between the subhead and
the project. The subhead itself is locked (issue #43, wontfix, owner
decision 2026-06-08); reopening it is a §7 flag, not done here. The
single-voice contention on whether the bridge is needed at all is recorded
in §6; it ships, and the owner may strike it in PR review.

**F5. The dot plot forward-references an award two sections early.** The
figure (2751) sits above `#publications`, but its presentations-lane
annotation "Patient Choice Award" (2857) is only explained by the Speaking
margin stat (3098), past the entire publication list. Fix (Tier A): one
added figcaption sentence pointing the reader to Speaking. No SVG edits
(coordinates are locked); no numbers (the award's denominator stays in the
Speaking note, which is `.stat-num`-exempt from additivity anyway).

**F6. The dot plot is unintroduced.** The Publications lead (2976) reads as
if the figure directly above it does not exist. Fix (Tier A): one appended
sentence acknowledging the chart. Lean, no numbers, per the panel.

**F7. The Gantt asserts what closed folds hide.** The chart's density
annotation "2014-15: three credentials, two roles" (3287) sits above two
sections whose entire content is inside closed `details.fold`s, so the
evidence for the chart's one claim is invisible on load. Fix (Tier A,
merged with F8): one-line leads for Education and Service written FROM the
fold contents and consistent to-the-word with the annotation: the three
credentials are the MPH (conferred 2015), the patient-safety graduate
certificate (2015), and the Oxford interviewing training (2014); the two
roles are the undergraduate research scholar mentorship (2014-2017) and the
WORT community advisory board chair (2013-2015). Folds stay closed (the
archival-fold design is deliberate); the Gantt stays where it is.

**F8. Three sections have no lead sentence.** Writing (2239), Education
(3299), and Service (3362) go straight from heading to metric or fold
summary; every other section gets a prose lead. Fix (Tier A): one plain
line each (copy in §9). No `.newthought` openers: the small-caps policy
keeps those selective (currently four: About, Experience, Speaking,
Publications). The Writing lead must not restate the sparkline's generated
numbers or the tag-rollup note's contents (lint_notes).

**F9. The skip link skips nothing.** `<main id="main">` opens at 1850,
BEFORE `nav.top` (1855), so "Skip to main content" targets a landmark that
begins with the nav it exists to bypass (WCAG 2.4.1). Fix (Tier A): move
the nav (with its comment) out of `<main>` into a `<header>` directly
before it, and give the header the centering box `main` was providing
(max-width 1400px, auto margins, the clamp padding). Verified: no CSS
selector assumes the nav is inside main (`nav.top` rules only, at 531 and
1667), the print block hides `nav.top` by selector wherever it lives, and
the skip link keeps `href="#main"`. The counter-reset root is untouched;
the hero project stays inside `#main`.

**F10. Four h2s for two content classes.** The hero's `h2.col-head`s
("Recent writing" 1930, "Current work" 2011) coexist with the section h2s
"Writing" (2239) and "Projects" (2540). The col-heads are deliberate
(heading order h1 > h2 > h3, commit `13080e6`) and stay exactly as they
are. Fix (approved with G2): retitle the stub section h2 to "Writing
cadence", which both disambiguates the outline and makes the heading honest
about its content. "Projects" vs "Current work" already differ; no change.

**F11. The lede promises an order the page doesn't deliver.** "This site
holds my writing, projects, and a fuller account of the work" (1901), but
About and the Writing stub interpose before Experience and Projects. Fix:
resolved entirely by G1; after the move the page delivers writing, then
work and projects, then the fuller account. No copy change.

**F12. Testimonials sit 940 lines from the roles they describe.** True,
and deliberate: the ending placement (Certifications, then Testimonials,
then Contact) is a documented Direction B decision. Verified during this
review: all three attributions are self-contained (each names the person,
role, and company inline: two Health Catalyst directors, one direct report
at Sustainable Clarity, 2013). Fix: none. Do not move them back.

**F13. Two source comments describe a page that no longer exists.** (a)
1729: "Small-caps column headers cue the three lanes", written for the
retired three-column hero; the same comment carries the `13080e6`
heading-order rationale, which must survive the edit. (b) 2670-2686: the
projects-index comment omits that the grid has been wrapped in a
`details.fold` ("More projects (4)") since 2026-07-26. Fix (Tier A): correct
both comments; exact text in §9.

## 5. Target reading order

After all approved fixes (changes marked with *):

1. skip link
2. \* header > nav (now OUTSIDE `main`; skip link becomes real)
3. `<main id="main">` opens at the nameplate
4. nameplate, proposition, hero-lede (\* nouns swapped)
5. split-hero: \* `#writing-hero` recent writing | current work, project 01
6. career band, "More:" line
7. \* `#writing`, retitled **Writing cadence** (new lead + sparkline)
8. `#work` + `#experience`
9. `#projects` Featured (\* bridge sentence, project 02)
10. "More projects (4)" fold (03 to 06)
11. \* **`#about`** (moved here)
12. dot plot (\* award pointer in figcaption)
13. `#publications` (\* chart acknowledgment in lead)
14. `#speaking`
15. Gantt figure
16. `#education` (\* new lead)
17. `#service` (\* new lead)
18. `#certifications`
19. `#testimonials`
20. `#contact`, footer

Nav targets are monotonic in nav order: `#writing-hero` < `#work` <
`#about` < `#contact`. Positions 13 to 20 are order-unchanged. The `<hr>`
rule between adjacent main blocks stays exactly one per boundary after the
About move (no doubled rules at the old or new slot).

## 6. Panel review (convened 2026-07-29)

Joint Focus Group + Design Council, convened together per the 2026-07-28
house rule, over the specific prescriptions above with the owner present.
Recorded in the mandated three parts.

### 6.1 Reception findings (Focus Group, three rounds)

Round 1, target audience: a Director of Quality Analytics at a regional
Medicare Advantage plan ("I screen roles, not About essays; Experience
arriving a section earlier is a win"); a staff engineer at a payer-analytics
vendor (the unexplained award annotation "genuinely read as an editing
mistake"; About-as-preface-to-the-academic-record is the better story); a
healthcare technical recruiter (the About move relocates the margin-note
role line downward, but Experience with the same facts moves up: "net wash,
slight win"); a UX researcher (the empty `#writing` target is the most
reportable defect; fixing it matters more than nav symmetry, and the plan
does both).

Round 2, antagonists: a VP of Stars at a national payer (the reorder is
fine; the untouched issue is hero writing-column height, correctly booked
as an accepted cost, "and I predict you'll be back for it"); a principal
payer-analytics engineer (questioned whether the 02 start confuses anyone;
conceded one clause is the cheap honest fix given the counter contract); a
former CMS measure developer (condition: the Education/Service leads must
match the Gantt annotation to-the-word or not exist; met in §9); a
health-system CIO (after the move, no prose says who this person is until
deep scroll; two hero lines carry it; wants the owner to re-read the page
top to bottom before shipping, which the PR review of the implementing
change provides).

Round 3, emotional register: the recruiter who reads forty portfolios a
week ("the pages I remember open with a voice, and this one now does...
what I'd remember: the one whose nav didn't lie to me"); a hiring manager
on a phone (thumb-scroll to the job history shrinks; About at position 11
is far down, "I'd never get there. I also never did"); a returning reader
(their hero path is untouched; flagged that nav "writing" landing below the
writing was still faintly odd, which drove the G2 retarget).

| Reception finding | Strength |
|---|---|
| Empty `#writing` nav target is the top felt defect; plan fixes it | Unanimous |
| About move net-positive or neutral for every archetype | Majority (one residue, CIO) |
| Figure-prose stitching (F5, F6) | Unanimous |
| New leads, conditional on Gantt-annotation consistency | Majority with condition |
| F4 bridge sentence harmless-to-useful | Majority (one voice: unnecessary) |
| Out of scope residue: hero column height; no near-top role line | Noted, not this plan |

### 6.2 Design findings (Council)

Edward (Tufte rigor): the About move "adds information without adding ink";
the methodology paragraph becomes the preface to the dot plot instead of an
orphan; keep the F4 bridge to one clause. Nathan (narrative viz): charts
should speak their punchlines; the award dot and the Gantt claim finally get
spoken antecedents; keep the Publications clause lean. Steve (cognitive
usability): nav order matching page order "is Krug 101"; renaming the stub
heading alone would leave the nav's first click landing below the writing,
hence the retarget. Haben (accessibility): the nav-out-of-main fix turns a
decorative skip link into a real one (WCAG 2.4.1); "Writing cadence"
preserves the `13080e6` outline; **no veto: every proposal improves or
preserves AA**; verify tab order with an actual keyboard pass. Massimo
(typographic detail): one `<hr>` per boundary through the moved seam, no
doubles; headings stay two words, not sentences. Jess (editorial): swap the
lede nouns and touch nothing else in the owner's sentence; the leads are one
line each with no numbers the figures already state; the doc must carry
exact copy so implementation pastes rather than improvises. Luke (mobile):
the move shortens hero-to-Experience on phones; re-check nav wrap at 761 to
1000px after the header extraction; no touch-target changes. Alan
(performance): moving the nav element is free; the header centering is a
few declarations; do not duplicate the hero project card, the counter
contract keeps one copy. Val (motion) and Bret (interactive documents) were
not seated: no motion-vocabulary or interactive-lane changes are in scope,
the moved About carries no figures, and the load-draw and scroll-draw
selectors are untouched.

### 6.3 Conflicts and how each resolved

1. **Nav "writing" landing (Steve + returning reader vs. rename-only):**
   resolved by the owner, 2026-07-29: retarget at the hero column (G2,
   approved). The rename-only option is recorded as the road not taken.
2. **F4 bridge necessity (principal engineer, single voice):** ships per
   the majority, held to one clause per Edward; the owner may strike it in
   PR review of the implementing change.
3. **About-move residue (CIO, single voice):** the proposition and lede are
   accepted as carrying the page's identity above the fold; booked as a
   known residue of G1, to be re-felt by the owner in the implementing PR's
   top-to-bottom re-read. Not resolvable by argument.

## 7. Decision record and open flags

Resolved by the owner during this review (2026-07-29):

- **G1, approved:** move `#about` to between the projects fold and the dot
  plot.
- **G2, approved:** retarget nav "writing" at the hero writing column via
  `id="writing-hero"`; the cadence section keeps `id="writing"` and is
  retitled "Writing cadence".

Flagged, NOT part of this plan, each needs a fresh owner decision:

- Reopening issue #43 (removing or rewording the "Featured" subhead).
- Any rewrite of the hero lede beyond the two-noun chronology swap.
- Reordering the nav items themselves (rejected here: about-first nav would
  reverse Direction B's writing-first primacy).
- A near-top current-role line (recruiter residue, §6.1); adjacent to the
  retired-subtitle decision, so it is an owner call, not a fix.

## 8. Constraints and lint matrix

Locked decisions this plan honors (do not relitigate during
implementation): the "Featured" subhead (#43 wontfix); testimonials at the
ending and the dot plot as a `#main` sibling (Direction B); the timeline
sitting below the fold (accepted cost, 2026-07-29); the hero hosts no
floating notes; `.newthought` stays at four leads; career-arc and dot-plot
SVG coordinates; the three-primitive motion vocabulary (nothing here
touches motion); `#main` as the `counter-reset` root with the hero project
inside it; the `h2.col-head` pattern (`13080e6`).

| Edit | Linters that gate it |
|---|---|
| G2 id + href retarget | `lint_links` (fragment must resolve), `lint_html` |
| G1 About move | `lint_html`, `lint_links` (ids unchanged), `lint_notes` (notes travel with their section; counters self-renumber) |
| New leads (F4, F6, F7, F8) | `lint_notes` (no significant-number or five-word-run overlap with any sidenote/margin note), em-dash grep |
| Figcaption sentence (F5) | `lint_notes` (award denominator stays in the `.stat-num`-exempt Speaking note), em-dash grep |
| Nav out of main (F9) | `lint_html`; eyeball + keyboard pass |
| Heading rename (F10) | `lint_html`; Lighthouse heading order |
| Comment fixes (F13) | none (comments), but keep quotes greppable |
| Everything | full `lint.yml` suite is the backstop; accent grep stays at 14 of 20, measured at `15d93bd` (no new accent uses anywhere in this plan; CLAUDE.md's "16" note trails the 2026-07-28 trims) |

The `activity-grid`, `writing-list`, and `writing-index` marker pairs are
not moved or edited by any fix; the Writing lead must be inserted BEFORE
`<!-- activity-grid:start -->`, outside the generated region, or the next
build overwrites it.

## 9. Implementation sequence: four commits, exact copy

Every new sentence below is final copy: paste it, do not improvise. All of
it is em-dash-clean by construction.

### Commit 1: mechanical copy and comments (position-independent)

**F3, line 1900.** Swap two nouns, change nothing else:

> Before this, I worked in editorial production and public-health research. That path continues to shape how I think about measurement, software, and the people who have to use both.

**F4, after the subhead at 2542.** Insert, styled like the Publications
lead (muted, 1.05rem):

> `<p style="color: var(--muted); font-size: 1.05rem; margin-bottom: 1.4rem;">Project 01, the Medicare Advantage Insight Engine, opens the page under Current work; the count continues here.</p>`

**F5, figcaption at 2752-2754.** Append as a third sentence:

> The Patient Choice Award noted on the presentations lane is described under Speaking below.

**F6, Publications lead at 2976.** Append inside the same `<p>`, after
"electronic health records.":

> The dot plot above charts these papers beside the presentation record.

**F7/F8, Education lead.** Insert a plain `<p>` between `<h2>Education</h2>`
(3299) and the fold (3301):

> A literature degree first, then a concentrated graduate stretch: the MPH, the patient-safety certificate, and the Oxford interviewing training all landed in 2014 and 2015.

**F7/F8, Service lead.** Insert a plain `<p>` between
`<h2>Service and Recognition</h2>` (3362) and the fold (3364):

> Peer review, board terms, mentoring, and awards; the two roles the chart above flags in 2014 and 2015 are the undergraduate research mentorship and the WORT board chair.

**F13a, comment at 1729.** Replace only the first sentence; the
heading-order rationale stays verbatim:

> `/* Small-caps column headers cue the two columns. These are <h2> ...` (rest unchanged)

**F13b, comment at 2670-2686.** After "Sibling of `<section id="projects">`,
NOT a child," insert:

> wrapped in a details.fold ("More projects (4)") since 2026-07-26,

Run: full lint suite, em-dash grep (expect 0), accent grep (expect 14).

### Commit 2: make the skip link real (F9)

Move lines 1852-1862 (the NAV comment block plus `<nav class="top">...
</nav>`) to sit between the skip link (1849) and `<main id="main">` (1850),
wrapped:

> `<header class="site-header">` ... nav comment + nav ... `</header>`

Add to CSS section 10 (after the `nav.top` rules at 531-553):

> `/* Header wrapper: the nav moved out of <main> on 2026-07-29 so the`
> `   skip link actually bypasses it; the header replicates the centering`
> `   box main provided. */`
> `.site-header { max-width: 1400px; margin: 0 auto; padding: 0 clamp(2rem, 4vw, 5rem); }`

Do NOT touch the `nav.top { width: 100%; }` override at 1667 or the print
rules; both are selector-scoped and position-independent. Verify: keyboard
tab from the skip link lands past the nav; nav renders identically at
1400px, 1000px, 761px, 600px; print preview still hides the nav.

### Commit 3: the reorder (G1 + G2 + F10), owner-approved

1. **G2:** at 1929, `<div class="hero-writing">` becomes
   `<div class="hero-writing" id="writing-hero">`. Nav 1857 becomes
   `<a href="#writing-hero">writing</a>`. Add CSS beside the
   `.section-anchor` rule (322): `#writing-hero { scroll-margin-top: 2rem; }`.
   Extend the left-column comment (1925-1928) with one line: "This column
   is the nav's 'writing' target (id=writing-hero, 2026-07-29)."
2. **F10:** the h2 at 2239 becomes `Writing cadence`.
3. **Writing lead (F8):** insert after the h2, BEFORE
   `<!-- activity-grid:start -->`:

> `<p>The pulse behind the writing list above: publishing pace, week by week.</p>`

4. **G1:** cut `<section id="about">...</section>` (2227-2234) and its
   trailing `<hr>` (2236); reinsert both between `</details>` (2742) and
   the existing `<hr>` (2744), so the sequence reads: projects fold,
   `<hr>`, About, `<hr>`, dot plot. The seam it leaves closes to:
   "More:" line, then `<section id="writing">` directly (no `<hr>` between
   the hero and the first section, matching the current pattern).

Run: `lint_links`, `lint_notes`, `lint_markers`, `lint_html`, then
`python scripts/build_portfolio.py` twice and confirm `index.html` is
byte-identical (marker idempotency), then the full suite. Lighthouse
accessibility in both modes: heading outline must stay clean (`13080e6`).

### Commit 4: documentation sync

See §12. Same-change rule: CLAUDE.md must describe the shipped page.

## 10. Verification checklist (implementing session)

- All twelve linters: `lint_blog`, `lint_vocab`, `lint_facts`,
  `lint_notes`, `lint_recognition`, `lint_gantt`, `lint_markers`,
  `lint_skills`, `lint_links`, `lint_html`, `lint_palette`, `lint_ideas`.
- The four greps: em-dash on `index.html` = 0; accent count at or under 20
  (expected: 14, unchanged); the blog `<p><svg-child>` grep empty; the
  anthropic-independence grep empty. Plus
  `python -m py_compile epidemic-simulation/sim.py`.
- `pytest scripts/tests/` green.
- `python scripts/build_portfolio.py` run twice: no diff on the second run.
- Browser eyeball (README subset): light and dark; all 11 folds; sidenote
  toggles at 600px; the career SVG swap and dot-plot swap at 760px; nav
  wrap 761 to 1000px; keyboard: skip link jumps past nav; the nav's four
  links land on writing (hero), Experience, About (new slot), Contact, in
  page order; print preview (nav hidden, folds forced open, no doubled
  rules at the About seam); Lighthouse accessibility at or above 90, both
  modes.
- Re-read the whole page top to bottom once (the CIO condition, §6.3).

## 11. Considered and rejected

- **Moving the sparkline into the hero and retiring `#writing`:** the hero
  hosts no floating notes (its design contract), the `mn-cadence` note
  would need a third note idiom the Council already rejected ("a
  fracture"), and the activity-grid markers would sit inside a denser
  generated region. Rejected.
- **Opening the Education/Service folds by default:** the archival-fold
  design is deliberate and print already forces folds open. The leads carry
  the claim instead. Rejected.
- **Moving the Gantt below its two sections:** the figure-then-detail
  pattern matches the dot plot and README's walk-through contract; the
  leads fix the evidence gap. Rejected.
- **Moving the testimonials up:** documented Direction B ending. Rejected.
- **Reordering the nav items to match the OLD page order:** about-first nav
  reverses the writing-first identity Direction B established. Rejected in
  favor of G1.
- **Renumbering projects or duplicating the hero card:** breaks the
  DOM-order counter contract. Rejected.

## 12. Documentation updates (commit 4 of the implementation)

- **CLAUDE.md:** add a dated paragraph to the top-of-file iteration notes
  (pattern of the existing Timeline Split and Direction B paragraphs)
  citing this doc: the 2026-07-29+ text-ordering pass, G1 and G2, the
  header extraction, the "Writing cadence" retitle, and the new leads.
  Correct the two stale "About-first section order" phrases (top notes and
  §Hero history): About-first survived every 2026-07-26 iteration and
  ended only with this pass. Update §Layout's nav bullet (`writing` targets
  `#writing-hero`; the four un-navigated section anchors are unchanged) and
  §Writing section update rule ("#writing, retitled Writing cadence, holds
  the sparkline and a one-line lead").
- **docs/homepage-iteration-2026-07-26.md:** append a dated superseded
  note (house pattern, like its 2026-07-28 note): the §6 thin-`#writing`
  item is resolved by this review; the §4 in-main order is superseded where
  it conflicts.
- **README walk-through:** re-check the eyeball list; "dot plot above the
  publication entries" and "Gantt between Speaking and Education" both stay
  true; add the skip-link keyboard item if absent.
- **docs/qa-audit-2026-07-28.md** line 215 (nav "writing" points at
  `#writing`): historical record of its date, leave unedited.
- **docs/backlog-review-2026-07-28.md:** historical record, leave unedited;
  its "what is `#writing` for" question is answered here.

---

## 13. Addendum: what the verification pass turned up (2026-07-29)

Added after implementation. The plan above is unchanged; this records one
finding that came out of running §10 rather than out of §4.

**A real Label in Name gap, fixed.** §10 asks for Lighthouse accessibility in
both modes. It scored 100 both ways, but its `label-content-name-mismatch`
audit flagged the five career-arc band links. Four were false positives (see
below). The fifth was real: the desktop arc labels the current-role band
**"BHA"**, while its accessible name read "Baltimore Health Analytics, 2025 to
present. Jump to the current role." A speech-input user reading the chart says
"click BHA" and matches nothing, which is exactly the failure WCAG 2.5.3
(Label in Name, Level A) exists to prevent. Fixed by fronting the abbreviation
in the `aria-label`; no coordinate, `<title>`, or rendered pixel moved. The
mobile `tl-rail` needed nothing, since it labels that band "Baltimore Health",
which its accessible name already contains. All ten band links across both
SVGs now satisfy containment. The contract is recorded in CLAUDE.md
§Career arc SVG.

**Why the audit still shows five, and why that is correct to ignore.** axe
computes "text inside the element" as `textContent`, which concatenates the
visible `<text>` label with the `<title>` nested inside the band line:
`'BHABaltimore Health Analytics, 2025 to present'`. That string appears in no
accessible name, so the rule fails for every band, including the four
("Editorial and writing", "healthfinch", "Health Catalyst", and the
en-dash/hyphen "Research, UW-Madison") whose visible labels were already clean
prefixes. Clearing it would require moving `<title>` out of the link, which is
the documented all-browser accessible layer for these marks. The audit is
weight 0 and does not affect the score. Check Label in Name by testing
containment directly; do not re-litigate this audit.

**Method note.** This is a second instance of the §Agent panels rule that
opened this review: render and measure before arguing. The audit's own summary
said five links were broken; measuring said one was, and named it.
