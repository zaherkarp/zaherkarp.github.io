# Homepage compression pass, 2026-08-13

Branch `claude/zaherkarp-homepage-compression-32k3yy`. Commits `ce1b370` and
`c0dd609`.

## Why

The owner asked for a shorter homepage, then, mid-pass, added two constraints that
changed the answer: **the figures stay** ("I don't want to lose my sweet sweet
figures"), and testimonials should be **reformatted rather than cut** ("any way to
format this interestingly and save space?").

Those two answers invalidated the approach the pass had been taking. Everything
before them was subtraction: which chart, which quote, which fold to delete. The
finding that replaced it is that **the page owns a 40% margin that only sidenotes
were using**, and moving secondary material into it buys height at zero content
cost.

## Result

| | Desktop @1363px | vs baseline |
|---|---:|---:|
| Baseline (HEAD at pass start) | 10,721px | |
| After `ce1b370` | 10,147px | −5.4% |
| After `c0dd609` | **9,928px** | **−7.4%** |

Mobile @390px: 18,240 → 17,286px. No horizontal scroll at 1363/1000/900/761/390px.
Twelve linters, five guards, 159 tests green.

Everything the owner protected survives: all seven charts, all three testimonial
voices, the full case layer, the complete Speaking and Publications records, and
Contact in full.

## The margin as a lever

Two applications, both measured, both saving more than the deletions they replaced.

**Testimonials, −198px.** The attribution moves out of the prose column into the
margin and the vertical padding tightens. This is worth more than deleting the 2013
Sustainable Clarity quote (185px), which means the section got shorter *and* kept
the only direct-report voice on the page, the one carrying the leadership evidence.

**Experience stack lines, −191px.** The five `.stack` lines (tools per role) move
into the margin, top-anchored to each role's heading.

### Two defects that only rendering caught

Both applications hit the same defect, and the obvious CSS was wrong both times.

1. **`float: right; clear: right` produces ambiguous attribution.** Floats stack
   downward, so each attribution drifts below the previous one. By the third quote,
   Joanna Laucirica's name sat nearer the second pullquote than her own. An
   unattributed testimonial is worth nothing, so this was a correctness defect, not
   a cosmetic one. Fixed with `position: absolute; top: 0` inside a
   `position: relative` parent, which anchors each item to the top of its own block.

2. **The same drift in Experience, plus a wrapping bug.** The first draft of the
   role wrappers put `<h2>Experience</h2>` *inside* role 0's wrapper, because the
   h2 shares a chunk with the first role when the section is split on `<hr>`. That
   role's stack line rendered level with the section heading rather than its own.
   Two prototypes read as "nearly right" in a screenshot; what exposed it was
   measuring each stack's offset from *its own* `h3` and seeing role 0 at −48px
   while roles 1-3 sat at +6px.

**The rule this pass adds:** when a device is applied to a repeated element, verify
the *pairing*, not just the placement. A margin item that renders in the margin can
still be attached to the wrong thing.

### Three things that keep the role wrappers aligned

Each was found by measuring role 0 against the rest, not by reading the CSS:

- the section `<h2>` stays outside the wrapper;
- the empty `.role-anchor` spans stay outside too (an empty inline as first child
  generates a line box that pushes the `h3` down);
- the `h3`'s top margin moves onto the wrapper, so wrapper top and `h3` top coincide.

### A regression the wrappers would have caused

`.role-anchor:target + h3` drives the arrival cue when a career-band click lands on
a role. Once the `h3` is inside a wrapper it is no longer the anchor's sibling, so
the selector silently stops matching and the cue dies. Now
`.role-anchor:target + .role-block > h3`. **No linter covers this**: `lint_links`
checks that `#exp-catalyst` resolves to a real id, which it still does, and a
selector that matches nothing is valid CSS. Verified by loading
`index.html#exp-catalyst` and reading back the computed `animation-name`.

### Rejected: a two-column testimonial grid

Measured at **+60px**. Inside the 60% column each quote gets ~390px and wraps more
than the side-by-side arrangement saves. The intuition that two columns are more
compact than one is wrong at this measure.

## The honest accounting

Compression and credibility pulled in opposite directions in this pass, and the
plan did not predict it:

| Change | Projected | Measured |
|---|---:|---:|
| Testimonial attributions to margin | −198px | −198px |
| Experience stacks to margin | −190px | −191px |
| Current role gains its shipped outcome | +60px | +60px |
| Insight Engine observed layer | not costed | +110px |

The two margin moves landed within 1px. The miss was entirely the figcaption, which
went uncosted because the plan reasoned it was "cheaper per pixel than prose" — true
per word, but it was four sentences in the narrowest column on the page. It was
tightened from 254px to ~144px across four measured drafts.

**Both additions were kept.** An expert reader marks down an unanchored modeled
funnel, or a current role with no shipped outcome, faster than they mark down a long
page.

## Content changes worth recording

**Current role.** Restructured to scope → decision rights → cross-functional
delivery → shipped and adopted outcome → technical approach. It previously carried
no shipped outcome at all. The adoption clause is `resume.md`'s own wording,
unaltered. Case 03 stops restating it and points at `#exp-bha` instead, per the case
layer's no-restated-claims contract.

**Insight Engine figcaption.** The observed layer lives here; the modeled body
paragraph is byte-identical, so observed volume never enters it. Modeled sentences
keep the model as subject, observed sentences take the pipeline and the status page
as subjects, so a reader cannot attach "a few dozen signals" to the funnel. Only
drift-proof figures are stated, and the honest limit is named: the status page
reports volume, not classification accuracy (no precision or recall measure exists).

**Ingestion runs every six hours, not nightly.** The plan said "nightly". The live
status page says *"Ingestion runs every 6h"*. Caught by fetching the page before
linking it. The Daily Briefing is daily; the ingestion cadence is not. This would
have been a factual error on the one card whose entire purpose is separating modeled
claims from observed ones.

**Meta descriptions.** All three (`description`, `og:description`,
`twitter:description`) now carry the leadership claim. They previously read "15+
years building production analytics..." with no leadership claim at all, while
`resume.md` leads with "Healthcare data and analytics leader". That inconsistency
worked against the goal of reading equally to a Director and a Principal
requisition.

## What was not done, and why

- **−15% is not reachable** while keeping all seven charts, all three testimonials,
  and the case bodies. Measured, not estimated: deleting *every* chart on the page
  would still not reach 26%. Both routes to −15% required giving up either the
  publications dot plot or the case bodies, and the owner ruled out both. Record
  this as a deliberate trade, not a missed target.
- **Blog nav alignment** (~250 generated pages have a 9-item nav describing a
  different site structure, and link `/#education` and `/#service`, which are
  commented out and land on the Gantt). ~~Flagged, not actioned: it needs a template
  change and a CI regeneration.~~ **Partly resolved 2026-08-13:** the two dead
  items were dropped from `scripts/templates/blog/base.html` and from the two
  hand-authored pages sharing that nav (`colophon/`, `case-study-care-redesign/`),
  taking the blog nav 9 items to 7; `build_blog.yml` regenerates the ~250 pages on
  merge. The remaining half of the finding stands: the 7-item nav still describes a
  different site structure than the homepage's four items
  (writing/work/about/contact), and reconciling the two is a structural change for
  the panels, not a link fix.
- **The methodology post's volume paragraph** now reads stale against the status
  page. Internally honest (scoped "so far", dated 2026-05-13) but the card links
  straight to it. A dated addendum is a separate decision.
- **`resume.md` six-vs-seven publications count**, still open from the 2026-08-11
  provenance audit.

## Reproducing the measurements

Render in headless Chromium with animations neutralised by an injected stylesheet;
without that, scroll-driven figures settle differently run to run and nothing is
comparable. Confirm `docWidth == innerWidth` rather than reading `scrollWidth`.
Measure each `.role-block > .stack` against *its own* `h3`, and check
`elementsFromPoint`-style pairing rather than trusting a screenshot. Do NOT run
`build_blog.py` in a session container: it rewrites ~247 files and a shallow clone
makes `git_iso_lastmod` return empty.
