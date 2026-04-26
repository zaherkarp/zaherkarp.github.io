# Tufte-Inspired Rebuild: Design Rationale

This document records the design decisions made during the redesign of `zaherkarp.github.io`, with reasoning for each. Read this when you need to understand or revisit a choice. The companion prompt (`zaherkarp-tufte-prompt.md`) is for executing the rebuild.

## Source material

The redesign draws from `https://edwardtufte.github.io/tufte-css/`, Edward Tufte's books (Visual Display of Quantitative Information, Envisioning Information, Beautiful Evidence), and Robert Bringhurst's Elements of Typographic Style. It also draws from honest disagreement with parts of the Tufte CSS implementation, where over-application of italic and small caps undermines the source material's actual principles.

## Foundational decisions

### Color palette

Off-white (#fffff8) and near-black (#111) instead of pure white and pure black. The small warmth shift makes the page read like a printed page rather than a screen. Pure white on a screen produces harsher contrast than paper, and pure black against pure white reads as harder still. Tufte's canonical compromise.

One accent color, oxford red (#7a0000), used only at the most important callout in each chart. Not used decoratively elsewhere on the page.

Muted grey (#6a6a6a) for sidenote bodies, metadata, and chart annotations that aren't the central claim.

Hairline rules (#d0d0c8) at half-opacity so they recede.

### Typography

ETBook self-hosted, with Palatino as fallback. Two woff files: roman and italic. No bold weight, because the page does not use bold body text anywhere.

Body type at 1.4rem (~21px), line-height 1.58. This is Tufte's comfortable reading size for serif text. A 60% column at this size produces lines of roughly 65 to 70 characters, which is the upper edge of the comfortable reading range.

Italic and small caps used sparingly. The Tufte CSS reference implementation overuses both, applying them to H1, H3, subtitles, citations, dates, stack tags, and link previews. This is decoration, not signal. Bringhurst's rule (which Tufte cites): italic is for titles of works, foreign words, and emphasis; small caps for acronyms and structural markers. When half the page is italic, italic stops meaning anything.

Final italic inventory: H2 only (one running italic heading style), sidenote numerals, the newthought opener, chart annotations and axis labels, figure captions, publication titles, journal names, testimonial pullquotes, formula variables, formula caption.

Final small-caps inventory: nav items, contact labels, the newthought opener.

### Section structure

Article > section nesting is required for sidenote positioning. Sections wrap in `<section id="...">`, body column at 60% width, leaving 40% for floating sidenotes and margin notes.

At 760px and below, the column collapses to 100% and sidenotes become inline toggles.

## Sidenote and margin-note system

CSS checkbox-hack pattern, no JavaScript. A label tied to a hidden checkbox toggles a sibling note element via the `+` selector and `:checked` pseudo-class.

Two flavors:

**Sidenotes (numbered)**: For citations, references, and methodological glosses that supplement the main argument. Numbered automatically via CSS counter.

**Margin notes (unnumbered)**: For tangential facts and asides. Use a `⊕` symbol as the toggle label.

The choice between sidenote and margin note is editorial: numbered for things a reader would want to reference back to, unnumbered for things that just happen to be there.

### Why sidenotes replaced the original site's "More detail / Less" toggles

The original site had four different patterns for handling secondary content: expand-collapse buttons on Experience roles, expand-collapse on testimonials, inline pills for publication links, expand-collapse on UW research. Sidenotes replace some of this and the `<details>` fold pattern replaces the rest. The result is one consistent mechanism for "more if you want it" content, with clear rules for when to use which.

## Heading discipline

H1 plain serif (the user's name). H2 italic serif (the only running italic heading style). H3 plain serif (role titles, project titles).

Bringhurst's rule: two levels of heading is enough for almost everything. Feynman's three-volume Caltech physics lectures use only two levels. The page does not push to H4.

H1 is intentionally not italic. The user's name does not need decoration; the size and weight already mark it as the document title.

## Folds (`<details>` disclosure)

The original site had multiple "More detail" expand-collapse patterns implemented as JavaScript. The rebuild uses native `<details>`/`<summary>` styled to look like muted italic prose with a `+`/`-` prefix instead of a browser disclosure widget.

Used for:

- Experience role detail (4 of 5 roles: BHA, Health Catalyst, healthfinch, UW; not Sustainable Clarity which is one paragraph)
- Full versions of testimonials
- The 17-item speaking list

NOT used for:

- Charts (charts are always visible)
- Project descriptions (already short)
- Publication entries (already short)
- About paragraphs (the whole section is short)

Rule: folds hide prose, never data. A reader who doesn't open any fold sees every chart, every metric in the lead paragraphs, and every category of content the page offers.

## Hero (top of page)

The page opens with: nav, H1 (name), single-line plain subtitle, then the career arc figure.

Earlier drafts had an italic blockquote epigraph and a self-quoted attribution between the subtitle and the timeline. This was removed because two framing statements above the same chart was self-absorbed and added length without adding information. The subtitle ("Healthcare data engineering and Medicare Advantage analytics") does the framing work; the chart does the demonstrating.

The career arc functions as the page's hero visualization. A reader who scrolls once sees the entire career trajectory in one image before they read any prose.

## Self-absorption discipline

Several small rewrites removed phrases that read as self-centering:

- "because the problems I want to work on require change at a scale that individual technical contribution cannot reach" became "because the decisions I want to influence happen above the individual contributor level." Less grand.
- "with the product roadmap and the CMS-to-organizational-priorities translation sitting in the middle of all of it" became "plus the product roadmap and translation between CMS requirements and organizational priorities." Removed the center-of-the-universe framing.
- The "return to public writing" justification paragraph in About was deleted entirely. The Writing section that follows speaks for itself.

Standing rule: read every paragraph for hub-of-everything language and rephrase or cut.

## "By the Numbers" table removed

The original site had a stats table with five rows (16+ years, 50+ health systems, 4 EHRs, 6 publications, 17 presentations). Removed because:

1. Tufte rejects bare decontextualized numbers as not data display.
2. The same information has more shape when shown as charts (career arc covers tenure; dot plot covers publications and presentations).
3. Five self-stats stacked together reads as marketing regardless of the typography used.

The chart inventory below replaces it with information that has shape.

## Chart inventory

The page has six substantive figures plus one inline sparkline. Each earns its place by showing something prose can't.

### 1. Career arc (hero)

Horizontal bar chart at desktop, vertical bar chart at mobile (native redesign, not rotation).

Three rows on desktop:
- Editorial and writing (2007 to 2014)
- Research, UW-Madison (2009 to 2018)
- Data engineering sequence (healthfinch 2017-2020, Health Catalyst 2020-2025, BHA 2025-now), all on one row because the roles are continuous in time.

Two quiet annotations: "news-wire syndication" at 2008 (Editorial era), "MPH, Biostatistics" at 2014 (Research era). One loud callout: red dashed line plus filled circle plus red text marking the 2020 Health Catalyst acquisition.

Why this chart: it makes the simultaneity of editorial and research overlap visible (2009 to 2014), shows the data engineering sequence as continuous, and pivots on the single most important career inflection.

Why vertical for mobile, not horizontal-scroll: a reader scrolling the page meets the timeline naturally; making them swipe sideways breaks the page's reading flow at the top. Vertical preserves the narrative-sequence reading. The two annotations were dropped from the vertical version because they crowded the narrower layout.

### 2. Academic dot plot

Year axis 2010 to 2019 horizontal. Publications above the axis, sized by citation count. Presentations below, stacked vertically per year.

Why this chart: the original "By the Numbers" table said "6 publications, 17 presentations." This shows the temporal shape. The 2015 column of seven dots reveals that academic output was concentrated in a single peak year, not evenly distributed. The 23-citation paper in 2014 stands out by size.

Mobile version: compressed two-row layout (publications above year axis, presentations below as proportional bars). Tufte 1B from the design proposals. Stacked-dot resolution would become illegible at phone scale, so presentations become a single bar per year scaled to count. The peak shape is preserved; literal countability is sacrificed.

### 3. Stars Cliff density curve (Project 02)

Density curve approximating MA contract Star Rating distribution. Diagonal hatch shading on the "no QBP" zone (below 4.0). Red dashed line at exactly 4.0 with "+$50M" annotation at the top.

Why this chart: the project is named after the cliff. Showing the cliff is more compelling than describing it. The threshold passes through the densest part of the distribution, which is the chart's central insight: a tenth of a star really does change the plan's financial structure.

### 4. Education + Service Gantt

Two-lane horizontal date-range plot from 2003 to now. Education above, Service below, with a small italic annotation at 2014-2015 calling out the cluster.

Why this chart: prose lists hide that three credentials and two service commitments overlapped within a 24-month window. The figure makes that visible. Single-year credentials are filled squares; multi-year items are bars.

### 5. SkillSprout transitions (Project 03)

Slope graph (linked-bar design instead of curved Sankey). Source on the left (Medical Assistant, 100 candidates), three category headers across the top, five target occupations on the right with bar widths and connecting line widths proportional to flow.

Why slope graph instead of Sankey: at small inline scale (600x290), curved bezier flows are visually heavy and overstate precision. Linked bars carry the same information (source-to-target with magnitude) more cleanly.

Why this chart: it shows the project's actual output (categorized transition pathways with credential requirements), not just its inputs. The credential notes ("12-month certificate", "ADN or BSN program") are the practically useful part.

### 6. Huber psi formula

CSS-styled inline math. Piecewise definition of Huber's psi-function: linear for small residuals, clipped at threshold k for large ones. Sits inside the BHA fold.

Why this formula: the BHA paragraph mentions "robust exponential smoothing" without showing what makes it robust. A short formula plus a one-sentence caption explaining the consequence (COVID-era shocks don't dominate the parameter estimates) gives a methodologically literate reader concrete evidence of depth. Casual readers don't see it because it's behind the fold.

### 7. Writing cadence sparkline (inline)

24 dots above the writing entry list, filled or empty for publication weeks. Trailing "11 posts" total in oldstyle figures, last-point-label pattern from Beautiful Evidence.

Why this is small: a sparkline is a Tufte signature for inline data display. It rewards reading at word density. Larger would be inappropriate for what it shows.

## Mobile-responsive figures

The career arc and academic dot plot have native mobile redesigns; the cliff, sankey, gantt, and formula are sized to scale gracefully without redesign.

Tufte's same-frame principle says all comparisons in a chart should be visible at once. Horizontal scroll violates this. Native vertical or compressed mobile versions preserve it.

The career arc earns vertical because its narrative is sequential (top-to-bottom reads as 2007-to-now). The dot plot earns the two-row compression because all years must remain co-present for the comparison-across-years to work; vertical-and-tall would force the reader to scroll past 2015 to compare it to 2014.

Two figures (cliff and sankey) sit inside Project bodies, are smaller, and scale via `width: 100%` on the SVG. No mobile-specific version needed.

The Gantt sits between sections and is roughly 600 units wide; it scales similarly.

The formula uses HTML and CSS rather than SVG and reflows naturally.

## Postgres closer

Preserved verbatim from the original site. It does not fit the Tufte aesthetic, and that is the point: it is the user's signature, and the page is better with it than without. Monospace stack, accent red on the prompt indicator, hairline rule above to separate it from Contact.

## Em dash policy

Stripped throughout. Every em dash was either replaced with a comma (for parenthetical asides), a period (for sentence breaks), or rephrased entirely. En dashes preserved in compound proper nouns (UW-Madison, AWS-to-Azure).

This is a personal preference of the user, not a Tufte requirement.

## What was considered and rejected

- **Bullets and numbered lists in body prose**: the user prefers prose. Lists used only where they're genuinely structural (the speaking list disclosure, the contact rows).

- **Tag clouds for skills**: anti-Tufte (font-size encoding popularity rather than position).

- **Year-by-year carousel for the dot plot on mobile**: violates same-frame comparison.

- **Tap-to-zoom thumbnails**: requires a tap to see the data; the chart's job is to show data, not wait for permission.

- **Period-grouped buckets ("Early UW", "Peak research", "Late UW") for the dot plot**: replaces data with summary categories; the year-by-year resolution is the chart's value.

- **A second chart in the Speaking section**: the academic dot plot at the top of the page already covers Speaking temporally.

- **Project iconography (a small grid of seven project markers)**: would require designing seven distinctive markers, which is significant design work for marginal information gain. The numbered list (01 through 07) provides the visual rhythm.

- **A photo of the user in the hero**: the original site has one. Not required for the rebuild but not removed either; preserve if you keep it.

- **MathJax or KaTeX for the Huber formula**: overkill for a single short formula. Pure CSS suffices.

## Overall density

The final page has six substantive figures plus one inline sparkline, eight `<details>` folds, sidenotes and margin notes throughout, and roughly 2,400 lines of source HTML in the demo.

Tufte's standard is "as much information as the reader can handle without losing the thread." The page tries to maximize information per square inch without becoming cluttered. A more reduced version is possible, and a more decorated version is also possible. This sits between.

The chart inventory is at the upper end of what a personal portfolio should have. Adding a seventh substantive figure would push into "look at all my charts" territory. Adding an eighth would be self-indulgent.

## What this is NOT

This rebuild is not a clone of Tufte CSS. It uses Tufte's principles selectively and disagrees with parts of the Tufte CSS implementation (specifically its over-application of italic and small caps).

It is not a Medium-style "blog template" applied to a portfolio. The page is structured as a single document that happens to have section anchors, not as a collection of cards or modules.

It is not a heavily-typed designed object. The page reads as a serious working portfolio. That register is intentional.
