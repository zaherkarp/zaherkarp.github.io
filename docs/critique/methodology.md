# Critique methodology — seance-symposium model

This document is the canonical reference for how a critique of any
surface in this repo (the homepage, a blog post, the resume, an
interactive subpage) is structured. It exists so the critique pipeline
runs reproducibly from this repo alone, without the runtime having to
"infer reasonable defaults" the way the first critique artifact
(`critiques/critique-2026-05-23.md`) had to.

A critique convenes six camps. Each camp speaks only through its own
lens, names the prior critics it is voicing, raises substantive
disagreement with adjacent camps, and ends with a single
hill-to-die-on finding. The runtime resolves substantive cross-camp
conflicts using the rules in §Conflict resolution below, weighted by
the archetype of the surface under critique (§Archetype weightings).

The output structure is fixed (§Output structure) so successive
critiques are comparable across surfaces and across time.

---

## The six camps

### 1. Encoding rigorists

The data-ink, perceptual-channel, uncertainty-visibility lens. A
chart's visual claim must be derivable from the data it encodes; the
encoding channels must be the strongest fit for the data type; missing
or approximate data must look missing or approximate.

Voicing critics: Edward Tufte, Jacques Bertin, Tamara Munzner,
Claus Wilke.

Default tiebreaker camp when no other camp dominates (see §Conflict
resolution).

### 2. Editorial clarity

The one-frame-one-takeaway, caption-as-claim, direct-label lens. The
reader's first three seconds determine whether the rest of the page
gets read; every figure should make one sentence and every section
should argue with the reader, not describe itself.

Voicing critics: Amanda Cox, John Burn-Murdoch, Cole Nussbaumer
Knaflic, Hannah Ritchie, Andy Kirk, Lisa Charlotte Muth, Alberto
Cairo.

### 3. Data humanists

The texture, granularity, felt-unit lens. Counts are people; aggregate
encodings erase the unit that gave the count its meaning. Warmth and
hand-shape in the data layer are not decoration.

Voicing critics: Giorgia Lupi, Stefanie Posavec, Nicholas Felton,
Hans Rosling, Nadieh Bremer.

### 4. System designers

The overview-zoom-filter, operability, affordance lens. A chart on a
page where the same data exists below as prose is an interface, not a
picture. Affordances must be visible, navigation must orient,
interaction (where allowed) must be earned.

Voicing critics: Ben Shneiderman, Don Norman, Steve Krug, Khoi Vinh,
John Maeda, Moritz Stefaner, Shirley Wu, Mike Bostock, Jeffrey Heer.

### 5. Pipeline and reproducibility

The data-driven, lint-enforceable, drift-resistant lens. Every visible
quantity must be derivable on demand from a file in the repo by a
script in the repo. Marker-bracketed regenerated regions are good;
hand-keyed pixel arithmetic with comments explaining the formula is
the renderer running in the author's head.

Voicing critics: Stephen Few, Hadley Wickham, Jenny Bryan, Yihui Xie,
Scott Chamberlain.

### 6. Access floor

The keyboard, screen-reader, reduced-motion, color-vision, low-vision
lens. The accessible layer is not a summary of the visual layer; it
is a parallel representation that must carry the same data narrative.
Color-only encoding fails. Toggles whose results are unguessable fail.
Duplicated SVGs that announce twice fail.

Voicing critics: Inclusive Design (composite voice — practitioner
register rather than a named-individual roster, because the access
literature is collectively maintained).

Holds soft veto on AA-contrast regressions. No other camp has veto
power.

---

## Archetype weightings

Per-surface weighting determines which camp dominates substantive
conflicts. The weights are not numeric coefficients; they are
ordering rules that say which camp wins direction when two camps
prescribe conflicting fixes.

### Personal portfolio (default for `index.html`)

| Camp                          | Weight     |
| ----------------------------- | ---------- |
| Editorial clarity             | Dominant   |
| Data humanists                | Strong     |
| Encoding rigorists            | Foundation |
| System designers              | Foundation |
| Access floor                  | Foundation |
| Pipeline and reproducibility  | Below standard |

Rationale: the page must argue with the reader (Editorial dominant);
a personal portfolio is allowed to feel personal (Data humanists
strong); the universal-foundation camps stay at full weight because
they are floors, not preferences; Pipeline is weighted below standard
because a one-author personal site does not face multi-author /
multi-quarter handoff pressure, though its concerns are not
suppressed.

### Blog post (`src/content/blog/<slug>.md`)

| Camp                          | Weight     |
| ----------------------------- | ---------- |
| Editorial clarity             | Dominant   |
| Encoding rigorists            | Strong     |
| Pipeline and reproducibility  | Strong     |
| System designers              | Foundation |
| Access floor                  | Foundation |
| Data humanists                | Below standard |

Rationale: long-form prose is the unit; the post must make a single
argument (Editorial dominant); methodology posts in particular need
chart-data integrity and reproducible build (Encoding and Pipeline
strong); humanist texture is welcome but not load-bearing for the
form (Data humanists below standard, not suppressed).

### Resume (`src/content/resume.md`)

| Camp                          | Weight     |
| ----------------------------- | ---------- |
| Editorial clarity             | Dominant   |
| Pipeline and reproducibility  | Strong     |
| Access floor                  | Strong     |
| System designers              | Foundation |
| Encoding rigorists            | Foundation |
| Data humanists                | Suppressed |

Rationale: a one-page recruiter-readable artifact has no room for
texture-as-data (Data humanists suppressed); ATS-parseability and
deterministic PDF rendering matter (Pipeline and Access strong); the
claim per line must read in three seconds (Editorial dominant).

### Subpage (interactive demo: `/star-rating-predictor/`,
       `/life-in-weeks/`, `/epidemic-simulation/`)

| Camp                          | Weight     |
| ----------------------------- | ---------- |
| System designers              | Dominant   |
| Editorial clarity             | Strong     |
| Encoding rigorists            | Strong     |
| Access floor                  | Foundation |
| Pipeline and reproducibility  | Foundation |
| Data humanists                | Below standard |

Rationale: interactivity is the whole point (System designers
dominant); the affordance and one-frame-one-question must still hold
(Editorial strong); the chart must encode honestly (Encoding strong);
the lane allows JS but does not relax the accessibility floor.

---

## Conflict resolution

When two or more camps prescribe conflicting fixes for the same
element, the runtime applies these rules in order:

1. **Dominant-camp wins direction.** If exactly one camp at "Dominant"
   weight under the surface's archetype has a position on the
   contested element, that camp's fix wins.

2. **Suppressed-camp loses enrichment.** If the disagreement is
   between a dominant camp's "simplify" fix and a suppressed camp's
   "enrich" fix, the simplification wins; the enrichment is not
   adopted.

3. **Compound-claim integrity check.** If the winning fix is a
   caption rewrite that asserts a quantitative claim, the runtime
   checks whether the underlying encoding can support the claim. If
   not, the caption fix must ship paired with the structural fix
   from the losing camp, OR the caption must be downgraded to a
   non-quantitative variant. A caption that makes a claim the chart
   cannot support is a quiet integrity downgrade, not a resolution.

4. **Orthogonal-camp's concern applies regardless.** A camp whose
   concern is structurally independent of the direction (e.g.
   Pipeline's "regenerate from data" concern when two other camps
   are arguing about which encoding to render) has its concern
   applied to whichever direction wins, not negotiated away.

5. **Locked-design-rule check.** Before adopting any fix, the runtime
   verifies the fix does not violate a rule under §Design
   decisions/tokens — locked or §What NOT to do in `CLAUDE.md`. A
   fix that would require adding JS to the homepage, removing
   sidenotes, regressing the 60% column, etc. is rejected even if
   it won under rules 1-4.

6. **Default tiebreaker → Encoding rigorists.** If no camp dominates
   and rules 1-5 do not resolve the conflict, Encoding rigorists
   wins direction. The rationale: data-encoding honesty is the
   universal foundation other camps rely on; absent a stronger
   archetype-driven signal, defer to it.

7. **Access floor veto.** A fix that introduces an AA-contrast
   regression, removes a non-color encoding redundancy, or breaks a
   keyboard / screen-reader contract is rejected by Access floor
   regardless of which camp's direction otherwise won. Access can
   only block; it cannot redirect. This is the only veto in the
   system.

---

## Output structure

Every critique writes to
`critiques/critique-<target-slug>-<YYYY-MM-DD>.md` with the
following structure. Successive critiques against the same target
should produce comparable-shaped artifacts so cross-time diffs are
legible.

```markdown
# Critique of <target path>

Generated: <YYYY-MM-DD>
Archetype: <personal portfolio | blog post | resume | subpage>
Iterations: <integer, default 1>
Changes applied: no (APPLY_CHANGES=false)

> Methodological note: <any deviations from canonical archetype
> weighting, with rationale; or "None — canonical weights applied."
> Reference this file (`docs/critique/methodology.md`) explicitly.>

---

## Camp critiques

## Critique from <Camp 1 name>

### Voicing critics
<comma-separated list, lifted from §The six camps above>

### What works on this page (your camp's lens only)
- <observation with `(<element>, lines <a>-<b>)` citation>
- <observation>

### What needs to change (your camp's lens only)
1. **<Finding headline.>** <Body with line citations. Concrete fix
   at the end of the paragraph, prefixed "Fix:". >
2. **<Finding headline.>** ...
   <as many as the camp's lens generates; do not pad>

### What other camps will say that you disagree with
- **<Adjacent camp>** will argue <their likely position>. We reject /
  partially agree because <one-sentence rebuttal>.
- <continue for each adjacent camp whose position the current camp
  has a substantive disagreement with>

### Your camp's hill to die on
<single paragraph, 3-5 sentences, identifying the ONE finding from
"What needs to change" that the camp will not negotiate. State why
it is foundational rather than contextual.>

---

<repeat for camps 2-6>

---

## Substantive conflicts and resolutions

### Conflict 1: <one-line description>

- **Camps involved:** <list>
- **Contested element:** <element with line range>
- **<Camp A>'s prescription:** <one paragraph>
- **<Camp B>'s prescription:** <one paragraph>

**Resolution (rule applied: <rule name from §Conflict resolution>):**
<paragraph describing the resolution, naming which camp's direction
won, and stating any compound-claim integrity requirement>.

<repeat for each substantive conflict; 2-5 is typical for a single
surface>

---

## Prioritized changes

### High confidence

> Suggested by four or more camps, OR by the dominant camp with zero
> opposition.

1. **<Change title.>** <Body, including from/to where applicable.>
   - **Camps backing:** <list with hill-to-die markers>
   - **Camps opposing:** <list, or "none">
   - **Files / lines:** <repo-relative paths and line numbers>

### Medium confidence

> Suggested by two or three camps with no substantive opposition; OR
> by one dominant camp opposed only by a suppressed camp.

<same shape>

### Low confidence

> Suggested by one camp with opposition from non-suppressed camps;
> deferred for explicit user review.

<same shape>

---

## Anti-patterns flagged

<numbered list of coalitions or sequencing risks the runtime
detected; e.g. "Caption-rewrite-without-data-rework" — adopting a
caption fix that makes a claim the chart can't support without the
paired structural fix>

---

## Recommended next iteration

<one paragraph naming which 3-5 changes to ship first, the
predicted downstream effect on the next critique pass, and any
deferred changes whose trigger condition is named>
```

---

## What this methodology deliberately does not do

- It does not propose new sections, new pages, or new features. The
  six camps critique what exists; the playbook does not invite
  invention. Site-level structural proposals belong in the §Agent
  panels (Focus Group, Design Council) framework in `CLAUDE.md`, not
  here.
- It does not write code changes. Every "Fix:" is a prescription; the
  runtime never edits the target file as part of a critique run
  (`APPLY_CHANGES=false` is the contract).
- It does not collapse disagreement into consensus. Substantive
  conflicts are recorded as conflicts and resolved per the rules
  above, never softened into "all camps generally agree that…"
- It does not replace user judgement. A critique is an input; the
  user decides which fixes to ship and in which order.
