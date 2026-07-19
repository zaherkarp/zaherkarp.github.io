# Homepage critique and action record — 2026-07-19

Record of an `/impeccable audit` + `/impeccable critique` pass over `index.html`,
the Design Council rulings that followed, the fixes already applied, and the
findings still open.

Two audiences: the **Analysis** and **Open findings** sections are written to be
read by a person. The **Implementation prompt** section at the end is written to
be handed to a coding agent verbatim.

Source artifacts:
- Critique snapshot: `.impeccable/critique/2026-07-18T16-10-30Z__index-html.md`
- Design Health Score: **27/40** (Acceptable, top edge). First run; no trend.

---

## 1. What was run

| Pass | Method | Outcome |
|---|---|---|
| `/impeccable audit index.html` | Single context + bundled detector | 19/20. Two real findings. |
| `/impeccable critique index.html` | **Dual-agent**, isolated (design review · detector evidence) | 27/40. Three P1s. |
| Design Council — sidenote band | 3 seats (Luke, Haben, Edward) | Unresolved disagreement, documented below |
| Design Council — focus visibility | 1 seat (Haben) | Conformance failure confirmed, fix applied |

No browser automation was available in either pass. Everything below is reasoned
from source. **Nothing here has been verified in a rendered browser**, which is
the single largest caveat on this document. A human render pass at 761px, 900px,
1200px, and 400% zoom would confirm or kill several items.

---

## 2. Already fixed (committed or in working tree)

### 2.1 Cadence sparkline missing `role="img"` — DONE, merged (`438a238`)

The writing-cadence sparkline was the only one of nine homepage SVGs carrying
`aria-label` without `role="img"`. Without an explicit role, screen-reader
handling of `aria-label` on `<svg>` is inconsistent across AT, so the label could
go unannounced.

Fixed in `scripts/build_portfolio.py` (the generator), **not** in `index.html`,
whose `activity-grid` marker region CI overwrites. SVG role coverage is now 9/9.

### 2.2 Focus Visible conformance failure — DONE, working tree

**WCAG 2.4.7 Focus Visible (AA), failure technique F78.** Ruled a conformance
failure by Haben, not a usability defect.

`index.html` has 17 `input.margin-toggle` checkboxes, deliberately sr-only
positioned rather than `display:none` so they stay in the tab order (comment at
L353-355). Their focus ring is projected onto the preceding label via
`label.margin-toggle:has(+ input.margin-toggle:focus-visible)`. But
`label.margin-toggle:not(.sidenote-number) { display: none }` hides 13 of those
labels above 760px — and an outline cannot paint on a non-rendered box. Result:
13 focus stops with no visible indicator in a ~15-screen document.

Fix applied at `index.html:405`:

```css
@media (min-width: 761px) {
  input.margin-toggle { display: none; }
}
```

Three points of reasoning worth preserving:

- **Why removing them honors the original intent rather than reversing it.** The
  L353-355 comment is about never stranding a note behind a mouse. Above 760px
  `.sidenote, .marginnote` float into the margin *ungated by `:checked`* — the
  note is already visible and the toggle does nothing. A keyboard user at desktop
  loses nothing.
- **Why the rule is unscoped.** An earlier draft tried to scope it so the four
  `sidenote-number` pairs were unaffected. That selector cannot be written: all 17
  inputs carry the identical `class="margin-toggle"` and none carries
  `sidenote-number` — the distinction lives only on the label. Verified by grep.
  The four numbered toggles are equally functionless at desktop, so one legible
  rule beats a sibling combinator a future editor will break.
- **Why it is media-query-scoped.** At 400% zoom a 1280px viewport resolves to
  ~320 CSS px, which falls under the existing `≤760px` block where labels
  re-display and toggles work. The 1.4.10 Reflow path is untouched.

Rejected alternative: changing the label to `visibility:hidden` or clip-positioning
so the ring has a box. Both suppress or clip the outline along with the box,
leaving an invisible indicator.

Adds no `--accent` reference; count holds at 14/20.

### 2.3 `.index-label` dead CSS + documentation drift — DONE, working tree

`CLAUDE.md` §Writing section update rule documented a
`<p class="index-label">More writing</p>` header as shipping. No such element
exists in the markup — both grids are now wrapped in
`<details class="fold"><summary>More writing</summary>` (L2128) and
`<summary>More projects</summary>` (L2628). The CSS rule was orphaned.

Removed the dead CSS (12 lines) and corrected `CLAUDE.md` to describe the fold
that actually ships, with a note on when and why the label was removed.

---

## 3. Analysis — what the two passes actually established

### 3.1 The deterministic detector found nothing real, twice

Across both passes the bundled detector reported the same three findings.
**Zero are true positives.** Assessment B traced each to root cause in the
detector's own source:

| Finding | Root cause | Verdict |
|---|---|---|
| `side-tab` (border-left ≥3px) | `isNeutralBorderColor()` cannot resolve CSS custom properties. It captures the literal string `"var"`, fails to classify it, fires. | False positive |
| `layout-transition` | Substring match. Source is `stroke-width`; `\b` matches at the hyphen. Only `max-`/`min-` prefixes are guarded. The emitted snippet is rewritten to `transition: width`, hiding the real property. | False positive |
| `numbered-section-markers` | Matched ISO dates in the writing list, a DOI, and CSS section comments (`10. NAV`, `11. CAREER ARC`). The real project numbering is CSS-counter generated and invisible to a text scan. | False positive |

**Standing implication for this repo:** the entire design system is CSS custom
properties, so *any* `var(--x)` border at ≥3px will false-positive on `side-tab`
forever. The `--rule` token (`#d0d0c8` light / `#2a2f36` dark) sits inside the
helper's own neutrality threshold and would have been exempted had it been
resolved. Treat detector output here as advisory only, and verify every hit
against source before acting.

Related: `.testimonial` uses `border-left: 2px`, which is *under* the detector's
3px trigger. An earlier prediction that a future automated pass would flag it is
wrong — it will not.

### 3.2 The judgment pass found the only real defect

The detector has no rule for the Focus Visible failure in §2.2. It was found by
design review reasoning over the CSS cascade. Worth remembering when weighing how
much to trust automated design tooling on this codebase.

### 3.3 The AI-slop verdict, and the more interesting finding underneath it

**Not AI-generated, and not close.** The page trips two of impeccable's named
reflexes on a checklist — the cream `--paper` token, the editorial-typographic
lane — but survives because the lane is *cited*, not borrowed: self-hosted ETBook,
real sidenotes in a real 40% margin, a committed rationale doc, ten
hand-coordinated SVGs with computed transforms, a native mobile career-arc
redesign rather than a scaled copy.

The sharper finding is **borrowed identity**. Nobody will say "AI made this."
Anyone design-literate says "that's Tufte CSS" within a second, and they are
right. The figures are yours; the chrome is inherited. Whether that is a feature
(the medium demonstrating the message) or a limit is a question this document
does not answer.

### 3.4 The unresolved council disagreement — sidenote band

`.sidenote, .marginnote` use `width: 50%` of the 60% column with
`margin-right: -60%`. Because `main` carries `padding: 0 clamp(2rem, 4vw, 5rem)`
and there is **no `box-sizing` declaration anywhere in the file**, `content-box`
applies and that padding subtracts from usable width inside the band:

| Viewport | Content | Column (60%) | Sidenote | ≈measure |
|---|---|---|---|---|
| 1400px+ | 1400 | 840 | 420px | ~47ch |
| 1000px | 920 | 552 | 276px | ~31ch |
| 800px | 732 | 439 | 220px | ~25ch |
| 761px | 693 | 416 | 208px | ~23ch |

All ten media queries sit at 760px; nothing handles 761–1000px.

- **Luke** — the whole band is broken. At 760px you get the inline toggle and it
  reads fine; at 761px a 23ch gutter. The wider viewport gets the worse
  experience. iPad portrait is 768px; split-screen laptops land 700–900px. Those
  are touch devices, so the `:hover` focus-plus-context reveals are also dead
  there.
- **Haben** — **not** an AA violation and explicitly no veto. 1.4.10 and 1.4.4
  both pass; WCAG has no *minimum* measure requirement (1.4.8's 80-character
  limit is a maximum, and AAA). Noted without claiming authority: 200% zoom on a
  1600px display lands low-vision readers in the 25ch band.
- **Edward** — will not concede the 60/40 split, but concedes that Tufte's margin
  is a fixed physical measure on a page that does not reflow. At 208px it has
  "stopped being a margin and become a gutter." Holds that only sub-850px is
  genuinely degraded, and that collapsing the whole band over-corrects.

**Status: unresolved.** Luke and Edward disagree about a number, not a principle,
and neither moved. All three reject do-nothing.

**Engineering caution if this is actioned:** widening `width` toward 60–65% while
`margin-right: -60%` stays fixed moves the note's *left* edge toward the body
column — the float is pulled right by the negative margin, so the right edge is
what is pinned. The two values are coupled and must be retuned together. This was
flagged without being rendered; verify visually.

---

## 4. Open findings

Ordered by leverage. None are defects; all are decisions.

### Tier 1 — decide before touching anything else

**The audience question.** Tufte designed for a reader with an hour. `CLAUDE.md`
names an audience that includes recruiters. Nearly every Tier 2 item resolves
differently depending on which reader wins. **This is a Focus Group question
(reader reception), not a Design Council one.**

### Tier 2 — contingent on Tier 1

| # | Finding | Evidence | Note |
|---|---|---|---|
| 1 | **Hidden content (P1)** | 6/8 posts and 4/6 projects behind two-word summaries (L2127, L2627) | The projects index was *designed* as a visible small-multiples grid. Cheapest partial fix regardless of Tier 1: put counts in the summaries (`More projects (4, 2 with source)`). |
| 2 | **Nav: 9 items, no rule (P2)** | L1636-1646, covers 9 of 13 sections | Cutting to five also fixes medium-viewport wrap and ~7px tap-row spacing. No locked tokens involved. |
| 3 | **Weak closer (P2)** | Page ends on a 2015 Six Sigma Yellow Belt (L3216) | `CLAUDE.md` already says replacing the removed psql closer "is a fresh design decision, not a restoration." Design Council territory. |
| 4 | **Certifications → Education** | L3214-3217, an `<h2>` for 20 words | **Contradicts a stated decision** — `CLAUDE.md` documents Certifications as deliberately standalone. Flagged, not recommended. |

### Tier 3 — noted, low urgency

- Career arc capped at 1000px while the dot plot runs 90% — two hero figures
  200px apart reads as a mistake before a decision.
- The cadence sparkline is the least legible figure on the page and it opens a
  section: no y-axis, no scale label, no reference. 2 vs 3 posts is
  indistinguishable without measuring pixels.
- Nine inline `style=` attributes repeat `color: var(--muted); font-size: 1.05rem`
  inside generator-owned marker regions — the one place a value can drift with no
  linter watching. Promote to a `.pub-meta` class in the generator.
- `/colophon/` is the most interesting footer link for a Tufte-literate audience
  and sits fourth of five, three of which duplicate the top nav.
- `MAH, MAC, MAD` (L2241) is the one unglossed acronym in a file that carefully
  expands HEDIS, QBP, and ECDS. It is contextualized ("Part D medication
  adherence triplet") but not expanded.
- No `lang` attribute on `Cancún` (L2834) or `Montréal` (L2839, L2800).

### Explicitly out of scope

- **The subtitle (L1650).** Flagged as doing no work at the page's
  highest-attention line, but it is a **locked token** per `CLAUDE.md` §Hero.
  Not to be edited without explicit instruction.
- **The borrowed-identity read.** Philosophical, not actionable.
- **The 761–1000px sidenote band.** Blocked on the unresolved council
  disagreement in §3.4.

---

## 5. Persona red flags (condensed)

- **Casey (mobile)** — all three `.stat-num` margin stats collapse behind `⊕` at
  ≤760px: 373,000 care gaps, the 10,000-adult cohort, 7 talks in 2015. The three
  most quotable numbers on the page, invisible by default on majority-traffic
  viewports. Inverts the stated intent of surfacing buried figures. The `⊕` labels
  also never got the touch hit-area treatment the arc bands and publication dots
  did.
- **Dana (Director of Quality Analytics)** — asks "has he run Stars in
  production?" That is answered by the only experience entry with no figure (BHA,
  deliberately). The featured Stars project is labeled "for teaching purposes";
  the real production work sits three levels deep in a closed fold.
- **Marcus (recruiter, 40 portfolios/week)** — none of his five facts (title,
  tenure, location, seniority, resume) is above the fold. The resume PDF is
  second-to-last on the page.

---

## 6. Implementation prompt

Hand the block below to a coding agent verbatim. It covers only the
**mechanically safe** Tier 2/3 items — the ones that need no design decision.
Everything requiring a taste call is deliberately excluded.

```
You are working in the zaherkarp.github.io repo. Read CLAUDE.md first and treat
its locked design tokens as binding. Read docs/homepage-critique-2026-07-19.md
for the findings behind these tasks.

Hard constraints:
- No JavaScript on index.html. No npm, no bundlers, no CSS frameworks.
- Do not change the palette, the 1400px/60% column, ETBook, the italic policy,
  the small-caps policy, or the career-arc SVG coordinates.
- The --accent count in index.html is capped at 20 (currently 14). Do not add
  accent references.
- index.html must stay em-dash-free.
- Never hand-edit inside a build marker region (activity-grid, writing-list,
  writing-index, cliff-path, pub-list, updated). Edit the generator in
  scripts/ and re-run it instead.

Tasks, in order. Do each as its own commit. Do not batch.

1. Add lang attributes to two proper nouns in index.html:
   - "Cancún" at roughly L2834 -> wrap in <span lang="es">
   - "Montréal" at roughly L2839 and L2800 -> wrap in <span lang="fr">
   Verify: grep for the entities, confirm both instances of Montréal are wrapped.
   Screen readers otherwise mispronounce both.

2. Expand the one unglossed acronym at roughly L2241. The text reads "the Part D
   medication adherence triplet (MAH, MAC, MAD)". Expand each on first use, in
   the same register as the HEDIS/QBP/ECDS expansions already in the file. Do not
   restructure the sentence; this is an inline gloss only. Keep the calibrated
   claim intact and do not punch up any number.

3. Add item counts to the two disclosure summaries so a reader can judge whether
   opening is worth it:
   - L2128 "More writing" -> include the number of tiles inside
   - L2628 "More projects" -> include the number of tiles inside
   These summaries are hand-authored and sit OUTSIDE the marker regions, so edit
   index.html directly. Confirm that by checking the marker positions first. If
   either turns out to be inside a marker region, stop and report instead of
   editing.

4. Promote the repeated inline styles in the publications block to a class. Nine
   elements carry an identical inline style="color: var(--muted); font-size:
   1.05rem;". They are emitted by scripts/build_portfolio.py inside the pub-list
   marker region, so the fix belongs in that script plus a new .pub-meta rule in
   index.html's inline CSS. After editing, re-run:
       python scripts/build_portfolio.py
   and confirm index.html regenerates with the class and no inline styles. The
   script makes a network call to Semantic Scholar; a 429 there is expected and
   harmless (cached counts are preserved).

After every task, run the full gate suite and confirm all pass:
    for l in blog vocab facts notes recognition gantt markers skills links html; do
      python scripts/lint_$l.py; done
    grep -cE -- '--accent|#7a0000' index.html    # must be <= 20
    grep -c '—' index.html                        # must be 0

Then verify build idempotency: run python scripts/build_portfolio.py twice and
confirm the second run produces no diff.

Do NOT attempt any of the following; they are blocked on human decisions
documented in docs/homepage-critique-2026-07-19.md:
- The hero subtitle (locked token).
- The 761-1000px sidenote band (unresolved council disagreement; width and
  margin-right are coupled).
- Unfolding the projects or writing index (depends on an unresolved audience
  question).
- Trimming the nav.
- Anything touching the page closer or the Certifications section.
```

---

## 7. Verification checklist for a human

None of this has been seen in a browser. Before trusting §2:

- [ ] Keyboard-tab the full page at 1200px. Confirm no invisible focus stops and
      that sidenote superscripts are still reachable.
- [ ] Same at 700px. Confirm `⊕` toggles work and reveal notes inline.
- [ ] 400% browser zoom at 1280px. Confirm the mobile block engages and toggles
      function (this is the path §2.2's media query depends on).
- [ ] Render at 761px, 800px, 1000px. Judge the sidenote measure against the
      table in §3.4 and decide the Luke/Edward threshold question.
- [ ] Light and dark mode on the writing index, confirming the removed
      `.index-label` CSS left no visual gap.
- [ ] Print preview — folds should force open.
