# Implementation Prompt: Tufte-inspired rebuild of zaherkarp.github.io

## Goal

Rebuild `zaherkarp.github.io` (an Astro site for a personal portfolio) using the design patterns established in the Tufte-inspired demo at `zaherkarp-tufte-demo.html`. The demo is a single-file HTML proof of concept; this work translates those patterns into the real site's Astro components.

## Reference materials

- **Demo artifact**: `zaherkarp-tufte-demo.html`. Treat this as the canonical reference for visual design, typography, color palette, figure construction, and section layout.
- **Rationale document**: `zaherkarp-tufte-rationale.md`. Read first. Explains why each design decision was made.
- **Current site**: `zaherkarp.github.io` source. Treat as the source of truth for content (text, dates, links, project descriptions, testimonials, publication metadata).

## Stack constraints

- Astro static site generator. Existing build pipeline.
- No JavaScript framework dependency. Vanilla HTML and CSS only inside components.
- No CSS framework. Pure CSS, written by hand, using the variable system in the demo.
- No external font CDN dependency for production. Self-host ETBook font files; fall back to Palatino.
- No client-side analytics, no third-party scripts. Site stays static and private.

## Communication preferences (from user)

- No em dashes. Use commas, periods, or rephrase. En-dashes are fine for compound proper nouns (UW-Madison) but never as sentence breaks.
- No rhetorical questions in copy.
- No unusual symbols or weird LLM tone.
- Italic and small caps used sparingly and meaningfully, not decoratively. See rationale doc for specific rules.
- Heavy code annotation expected. Comments explain WHY, not just WHAT.
- Ask clarifying questions before large tasks. List uploaded files at conversation start.

## Implementation order

Do these in order. Each step produces a working, testable site state.

### 1. Foundation: typography and color

Implement the design tokens from the demo:

```css
:root {
  --paper: #fffff8;
  --ink:   #111;
  --muted: #6a6a6a;
  --rule:  #d0d0c8;
  --accent:#7a0000;
}
```

Self-host ETBook woff files (already public-domain via the Tufte CSS GitHub Pages distribution). Fallback stack: Palatino, Palatino Linotype, Book Antiqua, Georgia, serif.

Body type: 1.4rem (about 21px), line-height 1.58, color var(--ink), background var(--paper).

H1 plain serif. H2 italic serif (the only running italic heading). H3 plain serif. Sizes per demo. No bold body text anywhere.

Links: body-colored, underlined with var(--rule), no hover or visited state changes.

### 2. Structural skeleton: sections and column width

Article max-width 1400px, 60% body column, leaves 40% for margin notes and sidenotes. Below 760px viewport, body column collapses to 100%.

Sections: about, writing, experience, projects, publications, speaking, education, service, contact. Plus a testimonials section that exists on the page but not in the nav (it sits between projects and education, or wherever feels right narratively).

Each section wrapped in `<section id="...">`. The article > section structure is required for sidenote positioning to work.

### 3. Nav and hero

Top nav: 9 small-caps links in a flex-wrap row, with a hairline rule below. No brand element (the H1 carries the name).

Hero: H1 with name, single plain subtitle line below. No epigraph, no pullquote.

### 4. Career arc figure (hero)

Implement both the desktop horizontal SVG and the mobile vertical SVG. Toggle via media query at 760px. CSS specificity is important: use `.timeline svg.tl-horizontal` and `.timeline svg.tl-vertical` to override the parent `.timeline svg` rule. See demo for full SVG code; coordinates are designed and tested.

The figure sits between the hero and the About section, anchoring the page visually.

### 5. About section

Three short paragraphs maximum. First paragraph opens with a `newthought` small-caps phrase. Use one numbered sidenote (grounded theory gloss) and one unnumbered margin note (current role context). No third-paragraph manifesto about the return to writing.

### 6. Writing section

24-week cadence sparkline above the entry list. Six entries, each: date (oldstyle figures), italic title with link, summary paragraph. Optional margin note for technical context. "View all writing" link at the bottom.

### 7. Experience section

Five roles, reverse chronological: BHA, Health Catalyst, healthfinch, UW Research, Sustainable Clarity.

Each entry:
- H3 role title (plain serif)
- Meta line: organization and dates
- Visible lead paragraph (one paragraph, the role overview)
- `<details class="fold">` with summary "More detail" containing the technical detail paragraphs
- Stack tags as a separate paragraph below the fold

The Huber psi formula goes inside the BHA fold. Use the `.formula-block` CSS pattern from the demo.

Sidenotes for technical depth (CMS Technical Notes context, four-EHR problem, medallion architecture, WLS context, etc.). Margin notes for tangential facts.

### 8. Projects section

Seven projects, numbered 01 through 07 with hanging oldstyle figures.

Each entry: H3 title, body paragraph, optional links row, stack row.

Project 02 (Stars Cliff Simulator) gets the embedded density curve figure. Coordinates and bezier path in the demo.

Project 03 (SkillSprout) gets the embedded transition slope graph. Source-to-targets pattern from the demo.

### 9. Publications section

Six entries. Each entry: year, italic title, citation/links margin note, authors and venue in muted grey.

### 10. Speaking section

Short lead paragraph with a margin note for the Patient Choice Award. Then a `<details class="speaking-list">` collapsed disclosure containing all 17 presentations.

### 11. Testimonials section

Two testimonials. Each is a pullquote (italic blockquote with thin left border), attribution below the quote, and a `<details class="fold">` with summary "More" containing the full version.

### 12. Education + Service combined Gantt figure

Insert between Testimonials section close and Education section open. The figure summarizes both sections that follow. Coordinates in the demo.

### 13. Education and Service sections

Both use the row-entry pattern: year-span on the left, content on the right. At narrow viewports, stack vertically.

### 14. Contact section

Six rows: email, LinkedIn, GitHub, Scholar, Tableau, Resume PDF. Small-caps labels, links body-colored.

### 15. Postgres closer

Preserve verbatim. It is the user's signature and intentionally breaks the Tufte aesthetic. Pre tag with monospace font and accent color on the prompt indicator.

### 16. Sidenote and margin-note system

Implement the CSS checkbox-hack pattern from the demo. On wide viewports, sidenotes float into the right margin. On narrow viewports, they collapse to a tappable toggle.

Every label-for must match an input-id. Use a consistent naming scheme: `sn-<name>` for numbered sidenotes, `mn-<name>` for unnumbered margin notes.

### 17. Fold disclosure pattern

The `<details class="fold">` pattern is shared by all expand-collapse content (Experience role detail, testimonial full text, speaking list). Style summaries as muted italic prose with `+`/`-` prefix, NOT browser default markers.

## Things that must NOT happen

- No "More detail / Less" buttons rendered as JavaScript. Use native `<details>` only.
- No localStorage, sessionStorage, or any client-side state. The site is static.
- No icon fonts. SVG inline only.
- No multiple bold weights. The page uses one weight (regular) plus italic for H2 and intentional contexts.
- No images of the user. The professional photo from the existing site is fine to keep but is not required by this rebuild.
- No "By the Numbers" stats table. It was removed for being decontextualized self-marketing. The figures (career arc, dot plot) carry the same information with shape.
- No epigraph or pullquote above the career arc.
- No "Return to writing" justification paragraph in About.
- No em dashes anywhere in any visible copy.

## Visual design rules (carry over to all new content)

1. **Italic only for**: titles of works (publication titles, journal names), the H2 heading style, the newthought opener, sidenote numerals, chart annotations, figure captions, testimonial pullquotes. Nothing else.

2. **Small caps only for**: nav items, contact field labels, the `newthought` opener. Not for stack tags, citation counts, dates, or anything else.

3. **One accent color (red oxford)**: used only at the most important callout in any given chart. In the career arc, that's the 2020 acquisition. In the Stars Cliff, that's the 4.0 threshold. Two reds per chart maximum.

4. **Folds for prose only**: never hide data inside a fold. The Experience role overview is visible; the technical detail is folded. The testimonial gist is visible; the full version is folded. Charts are always visible.

5. **Charts follow Tufte's same-frame rule**: every comparison the chart claims must be visible at once. If a comparison can't fit in one frame at the target viewport, redesign the chart, don't add scroll or pagination.

6. **Mobile responsiveness for charts**: native redesign over rotation or scroll. Career arc has a vertical mobile version. Dot plot has a compressed two-row mobile version.

7. **Annotations are muted by default**: any annotation that isn't the chart's central claim should be in muted grey italic, not in accent color.

## Acceptance criteria

The site is done when:

- All 9 nav links work and scroll to their sections.
- All sidenote and margin-note toggles work on both wide and narrow viewports.
- All `<details>` folds open and close correctly.
- All six figures render correctly at desktop, tablet, and phone widths.
- The career arc and dot plot swap orientations cleanly at 760px.
- Page validates as HTML5, no broken or unmatched tags.
- No external network dependencies at runtime (fonts self-hosted, no analytics, no CDN scripts).
- Build passes Astro's content collection validation.
- Site renders identically on Safari, Chrome, and Firefox latest stable.

## When to ask for clarification

Ask before deviating from the demo. Ask before adding new figures not in the inventory. Ask before changing copy beyond mechanical edits (e.g., re-pluralizing or expanding em-dash sentences into commas, fine; rewriting paragraphs, ask first).

The user prefers clarifying questions over assumptions.
