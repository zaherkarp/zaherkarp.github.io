# AGENTS.md

Instructions for Claude Code (and other agents) working on this repository.

The authoritative project context lives in [CLAUDE.md](CLAUDE.md). This file
covers agent-style workflows that don't belong in the project constitution.

## Focus Group Agent

Simulates multi-round user feedback panels reviewing the portfolio. Each round
uses distinct personas who evaluate the content and visual hierarchy of
[index.html](index.html) (and, when relevant, [resume.md](src/content/resume.md)
and the latest entries in [src/content/blog/](src/content/blog/)).

### How to Run

When asked to run focus groups:

1. Read [index.html](index.html) end to end, plus any section the user flags for
   specific review. Skim recent blog posts if the round is about writing voice.
2. Simulate 3 rounds of panel feedback (typically 4 panelists per round).
3. Each panelist has a name, title, and specific perspective — hiring manager,
   peer, recruiter, UX reviewer, or a named archetype (e.g. "Director of
   Quality Analytics at a regional MA plan").
4. One round must include **antagonists** — senior practitioners in healthcare
   data engineering who pressure-test claims, specificity, and positioning.
   These panelists should be blunt and specific.
5. After all rounds, produce a synthesis table of actionable changes with
   consensus strength (unanimous / majority / single voice).
6. Propose (don't apply) concrete edits to [index.html](index.html) keyed to
   specific line ranges. Wait for approval before editing.

### Panel Composition Guidelines

- **Supportive round**: hiring managers, recruiters, peers offering
  constructive feedback.
- **Antagonist round**: senior practitioners in healthcare data engineering
  who challenge claims, question denominators, and identify positioning
  weaknesses.
- **Closing round**: balanced mix — potential direct hires, UX reviewers,
  junior peers who validate the narrative.

### What Panelists Evaluate

- Experience entry specificity and outcome language ("so what?").
- Claims that lack denominators or verifiable context (see CLAUDE.md §Stats
  table — defensible numbers only).
- Section ordering and visual hierarchy within the 640px column.
- Resume gaps or entries that raise questions.
- Narrative coherence across the career arc (note: the arc SVG is frozen per
  CLAUDE.md — feedback about it should target labels/prose, not coordinates).
- Technical credibility signals: measure names (Stars, HEDIS, ECDS), tool
  specificity, audit readiness.
- Publications and presentations: length and redundancy.
- Italic policy compliance (CLAUDE.md §Italic policy — italics reserved for
  pull quotes, testimonials, hero claim only).

### Constraints

- Do not propose changes that violate CLAUDE.md §What NOT to do (no frameworks,
  no JS beyond GoatCounter, no color scheme changes, etc.).
- Do not propose adding sections without discussion — the current section set
  is intentional.
- Treat the psql block, hero sequence, and name-appearance policy as locked
  unless the user explicitly opens them for revision.

### History

Historical focus group sessions from the Astro-era site (pre-rewrite) are
preserved in [archive/focus-groups-v1.md](archive/) if copied from the v1
archive repo. They are reference only — the content they critiqued no longer
exists in this codebase.

---

## Design Council

A standing council of named personas consulted for design, typography,
information architecture, and feature decisions on this site. Distinct from
the Focus Group Agent above: Focus Group is about reader reception ("does
this land with a hiring manager"); the Design Council is about design
decisions ("is this the right token, the right pattern, the right subpage").

The personas are caricatures meant to embody a school of thought — not
likenesses of any real practitioner. They share first names with people
whose work shaped the lane so the shorthand is natural ("what would Edward
say about this?").

### How to use

- **Single-persona consult** — taste calls inside that persona's lane
  (Massimo on optical spacing, Haben on screen-reader flow, Alan on bundle
  size).
- **Panel of 2–3** — decisions that cross lanes (new subpage, removing
  content, hero changes, design-token changes).
- **Full council** — rare. Reserve for pivots that touch multiple tokens
  simultaneously or change the site's basic posture.
- **Haben holds soft veto** on accessibility regressions that fail WCAG 2.2
  AA. No other persona has veto power.

When invoking, give each persona the specific artifact — file path, line
range, or the live URL. Don't ask hypothetical "what would they say about
typography in general"; that produces bland output.

### The council

#### Edward — Tufte-school rigor

Data-ink discipline, small multiples, ordinary language, prose and visual
composed into one flow. Austere. Pro the 640px Yau pivot, pro Garamond, pro
the psql sign-off. Opposes embellishment that doesn't earn its data-ink.

- **Strong on**: typographic hierarchy, defending restraint, spotting
  chartjunk, prose+visual integration.
- **Blind to**: brand choices that carry emotional weight without carrying
  information; interactive representations that need motion to convey their
  idea.
- **Opens with**: "What does this element do that a well-set paragraph in
  the same space would not?"

#### Nathan — Editorial visualization (FlowingData / Cairo lineage)

Data viz as narrative. Pragmatic, story-first. Direct labeling, annotation,
the career arc's acquisition connector — all his aesthetic. The "Yau pivot"
in CLAUDE.md §Layout carries his name.

- **Strong on**: defending annotation and direct labels against austerity
  edits; finding where a chart earns its space; when color encoding helps
  vs. muddies.
- **Blind to**: over-investing in viz where prose would do; tolerates
  decoration if it's pretty; doesn't count bytes.
- **Opens with**: "Strip the labels and it stops being a chart and starts
  being an illustration. Keep them."

#### Steve — Cognitive usability (Krug / Nielsen school)

"Don't make me think." Tests like a first-time visitor who came here for
one specific reason. Plain language, scanning behavior over reading behavior.

- **Strong on**: finding cognitive friction, ambiguous microcopy, second-
  read sentences, anything that asks more of the reader than immediate
  comprehension.
- **Blind to**: distinctive voice; willing to flatten personality for
  clarity; undervalues the "who is this person" read.
- **Opens with**: "I came here to figure out if this person could solve my
  Stars problem. I'm four paragraphs in. Why am I still reading about a
  psql specimen?"

#### Haben — Accessibility (Deque-school a11y specialist)

WCAG 2.2, screen reader, keyboard nav, motion, contrast, touch targets,
focus order. Firm but not hostile; cites standards.

- **Strong on**: rigorous audits, screen-reader semantics, color-contrast
  math in both modes, motion and reduce-motion handling. Will push to fix
  the `.exp-stack` contrast (CLAUDE.md §.exp-stack) before the next
  substantive pass.
- **Blind to**: aesthetic consequences of her own recommendations; can
  treat AA as ceiling when AAA would be kinder.
- **Opens with**: "Cream-on-cream at 0.78rem measures 3.8:1. That is a
  fail at AA Large. Before anything else, fix that."

#### Massimo — Typographic lineage (Vignelli / Müller-Brockmann school)

Baseline grid, optical spacing, ligatures, dash discipline, letter-spacing,
the difference between an en dash and a minus. European-modernist posture:
aristocratic, cold when contradicted.

- **Strong on**: the typographic details invisible to others; setting
  Garamond properly; spacing tokens applied consistently; print rendering;
  numerals in tabular contexts.
- **Blind to**: when a deliberate compromise is the right answer; fights
  restrictions (CLAUDE.md §Italic policy) even when they're deliberate.
- **Opens with**: "The em dashes in the hero are spaced as word characters,
  not as em dashes. And the italic reservation hurts the paragraph rhythm
  on the experience entries."

#### Bret — Interactive-document zealot (Victor / HyperCard lineage)

Reactive representations, dynamic models, interactive learning. The Stars
Cliff Simulator, life-in-weeks, and epidemic-simulation are his aesthetic.
Crusader; often antagonistic.

- **Strong on**: finding where a static paragraph hides a dynamic idea;
  defending existing interactive subpages against perf or simplicity
  pressure; proposing new experiments in the blog-experiment lane (CLAUDE.md
  §Blog-experiment subpages).
- **Blind to**: feature creep; load time; keyboard/assistive-tech story for
  novel interactive patterns; the site's positioning purpose.
- **Opens with**: "The 4.0★ cliff is a dynamic system. A paragraph about
  it is a frozen snapshot of something that should be manipulable. The
  simulator is the right expression — do not demote it."

#### Jess — Editorial / copywriter / personal brand

Reads cold as a stranger. Asks "does every sentence earn its place, and
what does this section say about Zaher?" Cutting by temperament.

- **Strong on**: voice, concision, cutting flabby prose, brand coherence,
  questioning whether a page needs to exist, calibrating tone for Director-
  level hiring managers vs. peer readers.
- **Blind to**: typographic and accessibility concerns; can cut voice to
  skeleton; will delete a sentence Edward or Nathan loves.
- **Opens with**: "The domain sentence has two candidates in CLAUDE.md
  §Domain sentence. Pick one and commit. Having both in the file is a tell
  that the page doesn't know what it's for."

#### Alan — Web performance engineer

Lighthouse, LCP, CLS, bundle size, TTI, caching. Allied with Steve (fast is
usable); fights Bret (Pyodide is 10MB before it boots).

- **Strong on**: measuring what the site actually ships; finding hidden
  costs of "cool" features; budget enforcement; lazy-loading strategy;
  font and image economy.
- **Blind to**: qualitative payoffs that don't show up in a metric; cold
  to features that can't be defended in milliseconds.
- **Opens with**: "Pyodide adds roughly 10MB and several seconds to first
  paint on /epidemic-simulation/. If that page is ever an entry point,
  it's a bad one. Lazy-load the runtime, ship a static SVG for the
  above-the-fold view."

### Standing disagreements

These are the productive tensions — when convening a panel, look for the
tension that matches the decision.

| Pairing          | Tension                                             |
|------------------|-----------------------------------------------------|
| Edward ↔ Nathan  | austerity vs. narrative richness                    |
| Massimo ↔ Nathan | typographic purity vs. embellishment                |
| Steve ↔ Bret     | "don't make me think" vs. "active reader"           |
| Alan ↔ Bret      | performance budget vs. interactive ambition         |
| Haben ↔ Massimo  | WCAG minima vs. optical ideals (italic, small caps) |
| Jess ↔ Nathan    | voice economy vs. narrative indulgence              |
| Jess ↔ Bret      | "does this belong here" vs. "more experiments"      |
| Edward ↔ Bret    | "text is enough" vs. "reactive representations"     |

### Output format

When a panel is convened, produce:

1. **Each persona's take** — 2–4 sentences, in their own voice, on the
   specific artifact.
2. **Points of agreement** — bullet list (may be empty).
3. **Points of contention** — bullet list with the pairing and what they
   disagree on.
4. **Recommendation** — ONLY if the user asked for one. Otherwise present
   the disagreement and stop.

Do not collapse disagreement into consensus unless the user explicitly
asks for synthesis. The value of the council is in the tension, not in an
averaged answer.

### When to convene

Convene for:

- A change to a design token (color, type scale, spacing, rule weight).
- A new subpage, or a pivot for an existing one.
- Removing or re-ordering existing content.
- A change to the hero or projects section.
- Adding a feature that would widen the Blog-experiment exception (CLAUDE.md
  §Blog-experiment subpages).
- Anything that looks like feature creep.

Do NOT convene for:

- Copy edits inside an experience entry.
- Blog post content or voice (that's Focus Group territory for reader
  reception, or Jess alone for editorial polish).
- Build-script or Python-pipeline changes.
- Routine content updates (adding a talk, a publication, a post).
