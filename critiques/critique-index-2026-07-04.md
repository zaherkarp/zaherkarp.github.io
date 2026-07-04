# Critique of index.html

Generated: 2026-07-04
Archetype: personal portfolio
Iterations: 1
Changes applied: no (APPLY_CHANGES=false)

> Methodological note: canonical archetype weighting applied per
> docs/critique/methodology.md §Archetype weightings (personal portfolio:
> Editorial clarity dominant; Data humanists strong; Encoding rigorists,
> System designers, Access floor at foundation; Pipeline and
> reproducibility below standard). No deviations.

---

## Camp critiques

## Critique from Encoding rigorists

### Voicing critics
Edward Tufte, Jacques Bertin, Tamara Munzner, Claus Wilke.

### What works on this page (your camp's lens only)
- The Stars Cliff density curve's below-threshold zone uses a diagonal hatch texture rather than a color fill to mark the "no QBP" region (`<pattern id="hatch">`, lines 2434-2443; zone labels, lines 2491-2492), so the QBP boundary survives color-vision deficiency without a second encoding channel.
- The scorecard figure marks its one non-measured card explicitly as an approximation ("near-miss false positive (approx.)", line 2556; "sc-approx" styling, line 1000) instead of presenting an invented number as if it were real.

### What needs to change (your camp's lens only)
1. **The academic dot plot encodes "no citation data" identically to a real, low, measured value.** The citation-to-radius mapping (lines 1841-1846: unknown/no count = 4, 4 citations = 5, 11 citations = 7, 23 citations = 10) assigns the *same* radius (4 desktop / 2.5 mobile) to three publications with no citation count on record (WCEL 2012, line 1849-1850; Implementation Science 2016, line 1855-1856; IJHM 2018, line 1858-1859; mobile equivalents lines 1980, 1982-1983) as it would to an actual measured value of roughly that size. A reader has no visual way to distinguish "this paper has 4-ish citations" from "no citation count is available for this paper." Fix: render the unknown-count dots as open/unfilled circles (stroke only) so absence of data is visually distinct from a small measured value, in both the wide and mobile SVGs.
2. **The Gantt's "peer reviewer (ongoing)" mark breaks its own chart's internal encoding consistency.** Every other label in the figure is solid ink (`fill="#111"`), non-italic, and sits to the right of or above its mark (e.g. lines 2956, 2986, 2991, 2996, 3001, 3006, 3018). The peer-reviewer label alone (lines 3008-3013) is muted, italic, and right-anchored *before* its bar. Nothing in the figure explains why this one entry gets different visual treatment. Fix: either restyle it to match its seven siblings, or, if "ongoing" is meant to be a distinct semantic (unlike the closed-ended entries around it), encode that meaning explicitly (an open-ended arrowhead on the bar) rather than through an unexplained font-and-color shift.
3. **The cliff curve's y-axis is omitted with no gloss marking it as intentionally unscaled.** The code comment (lines 2417-2420) explains the omission is deliberate ("the absolute density is not the message... showing axis numbers would invite spurious precision"), but nothing on the rendered chart itself tells a reader that. A reader has no way to distinguish "the axis was forgotten" from "the axis is deliberately relative." Fix: a small italic note near the curve, e.g. "(density, unscaled)," costs one line and removes the ambiguity without inviting the precision the omission is trying to avoid.
4. **The scorecard's alert threshold tick carries no numeric label.** `.sc-gauge::after` (line 998) draws a fixed tick at `left: 60%`, representing the system's actual alert cutoff, but the rendered figure never states the value the tick represents. A reader can see that the CMS card's gauge clears the mark and the vendor card's doesn't, but cannot recover what the mark itself means numerically. Fix: label the tick (e.g. "0.60" beside it).
5. **The dot plot's own hardcoded citation annotations have already drifted from the true current counts.** The HERD 2019 dot is sized and commented as "11 citations" (lines 1844, 1861), and the JIHI 2014 dot as "23 citations" (line 1852), but the live Publications section two screens below (refreshed by `build_portfolio.py` from Semantic Scholar) now shows 13 citations for HERD (line 2688) and 25 for JIHI (line 2756). The chart is currently making a claim about relative magnitude that is measurably wrong. See also the Pipeline camp's critique of the same element (Conflict-free — both camps agree on the fix) and the Prioritized changes section.
6. **Annotation weight in the career arc no longer varies with narrative importance.** The 2020 acquisition, the 2008 news-wire note, and the 2014 MPH note (lines 1696-1731) all now render with identical visual weight: the same 0.7pt muted connector and the same italic caption style. Bertin's principle that a retinal variable's intensity should track the importance of what it encodes is not honored here — an acquisition that changed the trajectory of the author's career reads with the same emphasis as an article getting picked up by a wire service. This is presented as a live tension (see Conflict 1); the page's own design history records the uniform treatment as a deliberate 2026-06-07 decision, so we do not expect to win this one, but it remains a real inconsistency by this camp's lens.
7. **The citation-to-radius mapping is not a documented function.** The four values (unknown=4, 4 cites=5, 11 cites=7, 23 cites=10, lines 1841-1846) look hand-picked rather than computed from a stated formula (e.g. `r = k·sqrt(citations)`). A future editor adding a seventh publication has no rule to extend the scale correctly, only four prior examples to eyeball against.

### What other camps will say that you disagree with
- **Editorial clarity** will say the missing/real distinction (#1) is invisible to nearly every reader and not worth the complexity. We reject this: the point of encoding correctness is precisely for the reader who does look closely, and the fix is one stroke attribute, not a redesign.
- **Data humanists** will say the undocumented radius formula (#7) is over-engineering a small, personal chart. We partially agree the fix is low-priority, but the underlying risk (a rule that silently breaks on the seventh data point) is real regardless of the chart's size.
- **Pipeline and reproducibility** will want to own the mechanism behind #5 (marker-region regeneration). We agree the mechanism is theirs to fix; the chart's factual accuracy is ours to flag regardless of who authors the repair.
- **System designers** will point to the dot plot's hover-triggered `.dp-label` reveal (lines 1533-1542) as already solving the discoverability half of #1. We note that operability doesn't fix an underlying wrong or ambiguous encoding; a hovered label still can't tell a reader whether "4" was measured or assumed.

### Your camp's hill to die on
Finding #1, the conflation of missing citation data with a real low value in the academic dot plot, is the one this camp will not trade away. The methodology's own charter for this lens states plainly that "missing or approximate data must look missing or approximate," and this chart currently violates that in its most literal form: an absence and a measurement share one visual encoding. Every other finding in this camp's list is a refinement; this one is a category error, and it sits in the same figure the rationale doc calls out as proof that "the shape of academic output" is worth showing at all — a shape that becomes actively misleading if some of its data points are silently invented.

---

## Critique from Editorial clarity

### Voicing critics
Amanda Cox, John Burn-Murdoch, Cole Nussbaumer Knaflic, Hannah Ritchie, Andy Kirk, Lisa Charlotte Muth, Alberto Cairo.

### What works on this page (your camp's lens only)
- The Stars Cliff figcaption makes a complete, arguable claim in one sentence ("Most Medicare Advantage contracts... cluster just below the 4.0 cutoff that can trigger $50M in QBP bonus payments," lines 2423-2425) rather than describing the chart's mechanics.
- "Credentialing Looks Rigorous. Its Performance Scores Are Mostly Noise." (line 2090) is a genuinely strong claim-first headline in the Cox/Burn-Murdoch mold: it states the argument, not the topic.

### What needs to change (your camp's lens only)
1. **The single highest-traffic figure on the page has the weakest caption on the page.** "Career arc, 2007 to present." (lines 1646-1648) is a bare date range with no claim, in stark contrast to every other figure's caption (the cliff curve, the Gantt, the outcome figures all state an argument). The hero figure is the one thing every visitor sees first; it deserves the strongest caption on the page, not the flattest. Fix: rewrite to state what the arc actually argues (three overlapping careers converging into one continuous data-engineering line), scoped only to what the chart currently encodes (see the Anti-patterns section on not overclaiming ahead of Conflict 1's unresolved annotation-weight question).
2. **The writing-cadence tag rollup is an unbroken wall of 37 tags.** The margin note behind the ⊕ toggle (line 2072) lists all 37 tags in one undifferentiated, semicolon-joined run with no grouping, no visual hierarchy, and no cutoff. This is the single worst violation of "one frame, one takeaway" on the page: a reader who opens it gets no argument, just an alphabetized-by-frequency dump. Fix: show the top 5-8 tags inline and fold the long tail behind a second-level disclosure, or drop tags below a frequency floor entirely.
3. **The Speaking list's "year shown once per group" convention is unexplained and reads as missing data.** Eleven of the seventeen rows (lines 2802-2819) carry an empty `<span class="year"></span>`, relying on the reader to infer that a blank year means "same as the row above." Nothing in the visible summary or the list itself states this rule. A reader skimming quickly will plausibly conclude the data is incomplete rather than deliberately grouped. Fix: a one-line note above the list ("year shown once per cluster") removes the ambiguity for a two-word cost.
4. **The page assumes acronym fluency its own stated audience doesn't universally have.** QBP is used four times (prose line 2389; figcaption line 2424; chart labels lines 2491-2492) and never expanded anywhere on the visible page. HEDIS appears in prose (lines 41, 2218) with no expansion visible to a reader (only in invisible JSON-LD/meta tags, lines 7, 17, 25, 41). ECDS (lines 2623, 2625) and the Part D measure codes MAH/MAC/MAD (line 2218) are likewise never glossed. CLAUDE.md's own stated audience includes "recruiters working in regulated healthcare" alongside practitioners; the recruiter half of that audience has no path to understanding four load-bearing acronyms. Fix: expand each acronym once, at first use (see Conflict 5).
5. **The two featured Writing entries use inconsistent headline registers.** "Credentialing Looks Rigorous. Its Performance Scores Are Mostly Noise." (line 2090) states its argument directly. "Governing the Coverage Decision: A Metamodel for LLM Accountability in Payers and Payviders" (line 2082) is an academic colon-subtitle construction that buries any argument behind a topic label. The two sit stacked in the same featured block with visibly different rhetorical registers.
6. **The scorecard's evaluation jargon has no gloss for a lay reader.** "true positive" (line 2538) and "near-miss false positive (approx.)" (line 2556) are ML-evaluation terms of art presented without translation, in a figure whose whole point is to make triage legible to a reader who may not do machine learning for a living.
7. **The Speaking section's lead sentence buries the chart's own argument.** The lead states "Seventeen podium presentations... between 2010 and 2017" (line 2795), a flat count, while the dot plot two figures above and the margin stat beside it both make the real claim: output was concentrated in one extraordinary year (2015, 7 talks). The lead sentence and the visualization are arguing two different things at the same reader.

### What other camps will say that you disagree with
- **Encoding rigorists** will say the hero caption's brevity (#1) is appropriate for a chart meant to be read visually first. We reject this: every other figure on the page already proves a caption and a visual argument can coexist without competing.
- **Access floor** will say acronym expansion (#4) is a nice-to-have, not a compliance requirement. We accept it isn't a WCAG line item, but it is squarely inside this camp's "reader's first three seconds" mandate regardless of accessibility law.
- **Pipeline and reproducibility** will resist any hand-edit to the generated tag-rollup region (#2). We aren't asking for a hand-edit; the generator (`build_portfolio.py`) can group and truncate its own output.
- **System designers** will claim the scorecard jargon (#6) belongs to their plain-language lens (Krug), not ours. We accept this is a shared concern and don't contest their standing on it.

### Your camp's hill to die on
Finding #1, the hero career-arc caption, is the one this camp will not negotiate away. It is the highest-visibility single element on the entire page — the first thing every reader sees after the name and subtitle — and it currently makes no argument at all, in a document whose every other figure proves the author knows how to write one. A visitor who reads nothing else on the page reads this caption; right now it tells them nothing.

---

## Critique from Data humanists

### Voicing critics
Giorgia Lupi, Stefanie Posavec, Nicholas Felton, Hans Rosling, Nadieh Bremer.

### What works on this page (your camp's lens only)
- The three testimonials (lines 2841-2879) keep named, first-person warmth intact rather than reducing endorsement to a rating or a logo; two are Health Catalyst directors and one is a former direct report, each attributed by name and role.
- The margin stats (373,000 care gaps, line 2234; the 10,000-adult cohort, line 2336; "7 talks in 2015... including a co-authored poster that received the Patient Choice Award," line 2796) surface a buried human-scale number as text beside the prose it belongs to, not only as an abstracted chart value.

### What needs to change (your camp's lens only)
1. **Six years of sustained research collaboration is fully legible in the citation blocks and completely absent from the visualization built to represent them.** Nancy Pandhi appears as a coauthor on four of the six papers (lines 2710, 2742, 2760, and the JIHI byline line 2760 itself), but the academic dot plot (lines 1849-1864) renders all six papers as identical anonymous dots, distinguished only by size. The chart shows magnitude; it erases the one relationship that produced most of the author's academic output.
2. **The two outcome figures compress five years of relationship-building into two static bars with nothing felt in between.** The Health Catalyst (lines 2249-2262) and healthfinch (lines 2306-2318) figures each draw exactly two endpoints. We recognize CLAUDE.md documents this as deliberate data-honesty ("no fabricated growth trajectory between them"), so this is raised as a live tension, not a unilateral demand (see Conflict 2).
3. **The 17-talk Speaking list anonymizes both audience and texture into bare venue/city/year rows.** Sixteen of seventeen entries (lines 2802-2819) carry nothing but an institution name and a city; the one exception — the Patient Choice Award note tied to the 2015 peak (line 2796) — proves how much a single fact of texture adds, and how absent that texture is everywhere else in the list.
4. **The Gantt renders a genuinely human role as an anonymous bar.** "Undergraduate Research Scholar Mentor, 2014-2017" names, in the adjacent prose row-note (line 3138), three specific mentees and the skills they were taught; in the Gantt (lines 2990-2991) it is a 4px bar, visually identical in kind to a radio-station board term. The schedule survives; the relationship doesn't.
5. **The full citation strings are the only place seven named collaborators appear together, typeset as bibliographic filler.** Lines like 2760 ("Pandhi N, Yang WL, Karp Z, Young A, Beasley JW, Kraft S, Carayon P.") list real, long-running colleagues in a format indistinguishable from a works-cited footnote — accurate, but with no texture marking them as people the author actually worked alongside for years.

### What other camps will say that you disagree with
- **Encoding rigorists** will call any relationship annotation on the dot plot (#1) chartjunk for a six-point chart. We reject this: a single caption noting a sustained coauthor relationship is a true, data-grounded fact, not decoration — it is currently invisible, not currently absent from the underlying reality.
- **Pipeline and reproducibility** will resist hand-annotating a coauthor relationship into the generated Publications region (#5). We'd ask for a `note` field addition on the relevant entries — the publications.yaml schema already supports free-text notes for exactly this kind of texture.
- **Editorial clarity** will resist lengthening the Speaking list (#3) since it already argued to keep it collapsed. We only ask for texture on rows that already have a fact to hang it on; the Patient Choice Award note proves the pattern works without lengthening the whole list.

### Your camp's hill to die on
Finding #2, the two-point outcome figures, is the one this camp holds hardest even knowing it will likely lose (see Conflict 2 — the page's calibrated-claims discipline explicitly forbids inventing a trajectory the data doesn't support). It is foundational rather than contextual because it is the widest gap on the page between what actually happened over five years of a person's working life and what the chart lets a reader feel of it, and because the same two-endpoint pattern is the template every future role's outcome figure will likely copy without the gap ever being reconsidered.

---

## Critique from System designers

### Voicing critics
Ben Shneiderman, Don Norman, Steve Krug, Khoi Vinh, John Maeda, Moritz Stefaner, Shirley Wu, Mike Bostock, Jeffrey Heer.

### What works on this page (your camp's lens only)
- Career-arc bands and publication dots are real navigational affordances — clicking a band jumps to its role via `#exp-*` anchors (e.g. line 1663) and clicking a publication dot jumps to its full citation via `#pub-*` anchors (e.g. line 1850) — not just decorative chart marks.
- Touch-target overlays already fix the worst mobile operability gap: transparent `<rect>`s on career-arc bands and a widened transparent stroke on publication dots (lines 1498-1509) bring interactive targets up to a usable size without changing a single visible pixel.

### What needs to change (your camp's lens only)
1. **Navigation is not persistent on a roughly 3,270-line single document.** `nav.top` (lines 461-484, markup at 1615-1627) renders once at the top of the page and scrolls away; a reader nine sections deep who wants to jump to Contact has no faster path than scrolling back up or using the browser's own controls. This is presented as a live tension with the page's stated anti-chrome philosophy (see Conflict 4).
2. **Two different "reveal more" glyph systems coexist with no way to predict which behavior each produces before clicking.** The circled-plus ⊕ (e.g. line 1798) toggles an inline sidenote/margin-note reveal; the literal "+ " / "− " text prefix (CSS lines 1156-1161, 1180-1185) expands a `<details>` block. Both mean "there's more here," but they look different and behave differently (inline span vs. block expansion), and nothing distinguishes them for a first-time reader.
3. **Nothing distinguishes an interactive chart mark from a static one before a pointer arrives.** Career-arc bands and publication dots become identifiably clickable only via `cursor: pointer` plus a hover-triggered dim-and-thicken/enlarge effect (lines 1483-1519, 1528-1531); nothing in their resting state (no underline, no icon, no persistent visual cue) signals interactivity to a mouse user scanning the page rather than hovering every mark. Presented as a live tension (see Conflict 3).
4. **The scorecard's jargon assumes fluency the stated recruiter audience won't reliably have.** "true positive" (line 2538) and "near-miss false positive (approx.)" (line 2556) require ML-evaluation vocabulary Krug's first law says a visitor shouldn't need to bring with them.
5. **Four separate, visually identical "More detail" folds give no hint of what's behind them.** The Experience section's four `<details class="fold">` toggles (lines 2178, 2264, 2320, and the implicit fourth at UW) all read as the same generic "+ More detail," even though one of them hides a formula (the Huber psi-function, lines 2204-2216) and the others hide plain prose. A scanning reader has equal reason to skip all four, including the one with the most distinctive content.

### What other camps will say that you disagree with
- **Editorial clarity** will defend the unlabeled fold summaries (#5) as intentionally uniform, arguing a labeled preview would compete with the lead paragraph as a mini-headline. We accept partial defeat here and narrow the ask to the one fold that hides a formula, not all four.
- **Encoding rigorists** will say the sticky-nav ask (#1) has nothing to do with chart honesty. Correct — it's squarely this camp's concern, not theirs.
- **Access floor** will note the sidenote-vs-fold glyph inconsistency (#2) isn't itself a WCAG failure since both mechanisms are individually accessible. We agree it's an operability nit rather than a compliance gap, which is exactly why it belongs in this lens rather than theirs.

### Your camp's hill to die on
Finding #1, the absence of persistent navigation, is the one this camp will not trade away. At this document's length, orientation is the precondition for every other affordance on the page to be reachable at all — a reader who wants to jump ahead currently has no tool for it beyond raw scrolling, which is exactly the kind of "make me think about how to get somewhere" cost Krug and Norman built this lens to catch.

---

## Critique from Pipeline and reproducibility

### Voicing critics
Stephen Few, Hadley Wickham, Jenny Bryan, Yihui Xie, Scott Chamberlain.

### What works on this page (your camp's lens only)
- The Stars Cliff density curve's path data sits inside `cliff-path:start`/`cliff-path:end` markers (lines 2452, 2455), regenerable on demand from the CMS 2025 source CSV via `scripts/build_cliff.py` rather than hand-drawn.
- The Publications section's citation counts live inside `pub-list:start`/`pub-list:end` markers (lines 2677, 2780) and refresh from Semantic Scholar via `build_portfolio.py`, with graceful degradation documented for failed lookups.

### What needs to change (your camp's lens only)
1. **The academic dot plot's citation-derived encoding is a hand-typed snapshot that has already drifted from the source of truth the page itself maintains elsewhere.** The dot plot sizes and annotates HERD 2019 as "11 citations" (lines 1844, 1861) and JIHI 2014 as "23 citations" (line 1852), both outside any marker-bracketed region. The live Publications block, refreshed by the same CI run, now shows 13 citations for HERD (line 2688) and 25 for JIHI (line 2756). This is the exact failure this camp exists to catch: a visible quantity that cannot be derived on demand from the file that actually holds its current value, because the chart never reads from that file at all.
2. **The career-arc and Gantt figures hand-compute every coordinate from a documented linear transform, rather than being emitted by a script the way the cliff curve is.** The Gantt's HTML comment states the transform outright (`x(year) = 90 + (year - 2003) * 19`, line 2924); the career arc does the same implicitly across its two viewBox variants (lines 1650-1793). This is precisely the pattern this camp's charter warns against: "hand-keyed pixel arithmetic with comments explaining the formula is the renderer running in the author's head."
3. **The page mixes marker-governed and hand-maintained figures with no visible signal distinguishing which is which.** The tag rollup and writing-cadence sparkline (lines 2046-2074) are correctly marker-bracketed; the dot plot and Gantt sit in the same file with no such contract. A reader of the source has no way to tell, without external knowledge of the build scripts, which figures will silently go stale on the next data refresh and which won't.
4. **CLAUDE.md's own design-token documentation has drifted from the markup it describes.** The §Palette "Accent discipline" paragraph lists "the 2014–2015 cluster annotation in the Gantt" as one of the page's few accent uses, but that annotation renders `fill="#6a6a6a"` (muted), not the accent sentinel `#7a0000` (line 3043) — the career-arc section of the same document correctly notes the arc itself now uses no accent, but the earlier Accent-discipline paragraph was never updated to match. Since this critique's own Locked-design-rule check (Conflict resolution rule 5) must defer to CLAUDE.md as ground truth, a stale example inside that ground truth is itself worth flagging.

### What other camps will say that you disagree with
- **Encoding rigorists** will treat the citation drift (#1) as primarily an honesty bug rather than a process bug. We don't disagree with the framing; we simply own the mechanism of the fix (bring the dot plot under a marker region, or drop absolute counts from the chart entirely).
- **Editorial clarity** will resist any fix that adds visible chrome (e.g., a "source: publications.yaml" footnote). We aren't asking for visible chrome — only for the existing numbers to be correct on the next regeneration, silently.
- **System designers** has no live disagreement with this camp's findings.

### Your camp's hill to die on
Finding #1, the citation-count drift between the dot plot and the Publications section, is the one this camp will not negotiate away. It is not a style preference; it is a factually wrong number on a public page, wrong for the exact structural reason — a hand-typed value with no regeneration contract — that this camp exists to catch, and it is independently verifiable by any reader who compares the two sections against each other.

---

## Critique from Access floor

### Voicing critics
Inclusive Design (composite voice — practitioner register rather than a named-individual roster, because the access literature is collectively maintained).

### What works on this page (your camp's lens only)
- Career-arc bands and publication dots carry real keyboard-focus parity with their hover behavior — `:focus` mirrors `:hover` for both the dim-and-emphasize effect and the typeset label reveal (lines 1516-1517, 1541-1542) — so a keyboard user gets the same engagement feedback a mouse user does.
- The sidenote/margin-note toggle checkbox is visually hidden but never removed from the tab order (`input.margin-toggle`, lines 356-366), with focus visibly projected onto its sibling label via `:has()` (lines 372-376) — a screen-reader- and keyboard-safe pattern, not a `display: none` trap.

### What needs to change (your camp's lens only)
1. **The academic dot plot's presentation dots carry the entire "talks per year" story and are invisible to assistive technology.** The circles encoding one presentation per dot, including the 2015 peak of seven (lines 1888-1894 wide, 2004-2011 mobile), carry no `<title>`, no `aria-label`, and no adjacent visible text label anywhere. Only the SVG's own top-level `aria-label` ("...17 presentations across 2010 to 2019," line 1814) reaches assistive technology. A sighted reader sees the 2015 spike directly; a screen-reader user receives one aggregate sentence and no year-by-year shape at all. This is the precise failure this camp's charter names: "the accessible layer... must carry the same data narrative," not a summary of it.
2. **Career-arc band links nest a redundant `<title>` inside an already-labeled `<a>`.** Each band's `<a>` carries a complete `aria-label` (e.g. line 1663: "Editorial and writing, 2007 to 2014. Jump to the Sustainable Clarity role."), and its child `<line>` separately carries a `<title>` with overlapping text ("Editorial and writing, 2007 to 2014"). Depending on the screen reader/browser pairing, a `<title>` nested inside an already-labeled link can be announced a second time or ignored inconsistently — the "duplicated SVGs that announce twice" failure this camp's charter names explicitly, even though the practical impact is browser-dependent rather than certain.
3. **The Gantt's fourteen individual marks carry no per-item accessible date range.** The figure's one top-level `aria-label` (line 2938) summarizes "concurrent activity in 2014-2015" but nothing else; each bar and square has an adjacent `<text>` label naming the credential or role (a genuine accessible text node, not a gap), but the actual start/end years each mark encodes exist only as x-position on the SVG canvas. A screen-reader user gets "MPH, Biostatistics" but not "2013 to 2015" from the figure itself — that date range is only recoverable from the separate Education section's prose two screens below.
4. **The scorecard's six-feature comparison bars have no accessible value beyond the adjacent visible number.** The `.sc-fill`/`.sc-bar` elements (lines 986-992) carry no `<title>` or ARIA value; a screen-reader user gets each numeric score sequentially through the surrounding text nodes, but the bar-length comparison itself — the entire visual point of a bar chart — is not exposed as a structured comparison anywhere.

### What other camps will say that you disagree with
- **Encoding rigorists** will treat #1 as a data-completeness bug in their own lens too. We're glad to share the finding, but insist accessibility is the primary framing here: the fix (adding `<title>` elements) is trivial, and this camp's veto exists precisely so a shared finding doesn't get quietly deprioritized because "another camp already flagged it."
- **System designers** will call #2 a micro-optimization given its browser-dependent impact. We agree it isn't this camp's hill to die on for that reason, which is why it's ranked below #1.
- **Pipeline and reproducibility** will note the Gantt's missing per-item titles (#3) overlaps their own "every visible quantity must be derivable" concern. Correct — and per Conflict resolution rule 4, we'd ask any pipeline-driven fix for the Gantt to include accessible text as a matter of course, not as an afterthought bolted on later.

### Your camp's hill to die on
Finding #1, the presentation dots' missing accessible narrative, is the one this camp holds without compromise. The rationale doc's own stated justification for this chart's existence is that "the 2015 column of seven dots reveals that academic output was concentrated in a single peak year" — for a screen-reader user today, that argument, the entire reason this figure exists, is currently unavailable at any level of engagement with the page.

---

## Substantive conflicts and resolutions

### Conflict 1: Uniform annotation weight vs. importance-proportional encoding in the career arc

- **Camps involved:** Encoding rigorists, Editorial clarity (backed by a documented owner decision)
- **Contested element:** The three career-arc annotations — 2020 acquisition, 2008 news-wire syndication, 2014 MPH — lines 1696-1731.
- **Encoding rigorists' prescription:** Differentiate visual weight across the three annotations so the 2020 acquisition, the actual narrative pivot of the career arc, reads as heavier than the minor press-syndication note it currently matches in style.
- **Editorial clarity's prescription:** Keep all three annotations at identical quiet weight, consistent with the page's existing, dated 2026-06-07 decision to demote the acquisition callout from a loud accent treatment specifically for chart uniformity and to reduce Catalyst emphasis.

**Resolution (rule applied: Locked-design-rule check, rule 5):** CLAUDE.md documents the uniform annotation treatment as an explicit, dated owner decision, not merely a Design Council recommendation ("the user wanted chart uniformity and fewer Catalyst call-outs... The career arc now uses NO accent at all"). This functions as a locked design choice even though it is not enumerated in the tokens list verbatim. Encoding rigorists' differentiation fix is rejected on that basis; the uniform treatment stands. Recorded here as a live, documented disagreement rather than an adopted resolution.

---

### Conflict 2: Two-point outcome figures vs. felt trajectory

- **Camps involved:** Data humanists, Encoding rigorists (joined by Pipeline and reproducibility on data-honesty grounds)
- **Contested element:** The Health Catalyst and healthfinch outcome-figure bar pairs — lines 2249-2262, 2306-2318.
- **Data humanists' prescription:** Show an approximate trajectory between the two drawn endpoints, even an uncertain or dashed one, so that five years of change reads as a lived arc rather than a jump cut between two static bars.
- **Encoding rigorists' prescription:** Draw only the two real, sourced endpoints; any interpolation would assert a shape the underlying data does not contain, since only two data points exist for either metric.

**Resolution (rule applied: Compound-claim integrity check, rule 3, reinforced by the Locked-design-rule check, rule 5, via CLAUDE.md's "Calibrated claims: do not punch up" policy):** Any interpolated trajectory would be a quantitative claim the chart cannot support, since only two measured points exist for either outcome. Per rule 3, this is not merely downgraded to a non-quantitative variant; it is rejected outright, because there is no non-quantitative version of "the shape of the middle years" that would not still imply a curve the record doesn't have. This is doubly reinforced by CLAUDE.md's explicit, page-wide calibrated-claims discipline. The two-endpoint drawing stands as currently implemented.

---

### Conflict 3: Static visible click affordance vs. minimal chart chrome

- **Camps involved:** System designers, Editorial clarity (dominant)
- **Contested element:** Career-arc band links and publication-dot links — lines 1483-1519, 1528-1531.
- **System designers' prescription:** Add a persistent, non-hover-dependent visual cue (a subtle dotted underline or small chevron) so a scanning mouse user can identify interactive marks before hovering any of them.
- **Editorial clarity's prescription:** Keep the marks visually bare in their resting state; the page's own existing CSS comment already argues an underline would "read as chartjunk on a chart axis," and the hover/focus reveal is the intended, restrained affordance.

**Resolution (rule applied: Dominant-camp wins direction, rule 1):** Editorial clarity is the dominant camp under the personal-portfolio archetype and has an explicit, already-implemented position on this exact element. Its direction wins: no added static affordance mark. Per rule 4, Access floor's orthogonal concern (keyboard-focus parity and touch-target sizing, already shipped per lines 1498-1517, 1541-1542) carries forward regardless of which direction won, and remains intact under this resolution.

---

### Conflict 4: Persistent navigation vs. restrained "no chrome" philosophy

- **Camps involved:** System designers, Editorial clarity (backed by the page's own stated design philosophy)
- **Contested element:** `nav.top` — lines 461-484 (CSS comment: "Tufte books don't have nav... it is restrained"), markup lines 1615-1627.
- **System designers' prescription:** Make the top navigation sticky or otherwise persistent so wayfinding survives scrolling on a document of this length.
- **Editorial clarity's prescription:** Keep the nav as a single restrained block at the top only, consistent with the page's stated anti-chrome philosophy and its comment explicitly disclaiming a Tufte book's need for navigation at all.

**Resolution (rule applied: Dominant-camp wins direction, rule 1, with an orthogonal carry-forward under rule 4):** Editorial clarity's restraint position wins for the general case; no sticky header is adopted. But System designers' underlying concern — a reader needs some way back — is structurally independent of that direction and is already partially served by the existing footer navigation (`site-footer`, lines 3224-3235). The resolution is to confirm that end-of-document path is not the *only* return mechanism a long-scroll reader has, rather than to add a sticky header (see Prioritized changes, Low confidence).

---

### Conflict 5: Missing acronym glosses vs. assumed-practitioner register

- **Camps involved:** Editorial clarity (dominant), Access floor vs. the page's stated practitioner-first audience register
- **Contested element:** QBP, HEDIS, ECDS, MAH/MAC/MAD — lines 2389, 2424, 2491-2492, 2218, 2623-2625.
- **Editorial clarity's / Access floor's prescription:** Expand each acronym once, at its first use on the page.
- **The implicit counter-position (practitioner-register defenders):** CLAUDE.md's stated audience is "experienced practitioners," and repeated glossing reads as condescending, adding friction for the majority reader who already knows these terms cold.

**Resolution (rule applied: Dominant-camp wins direction, rule 1):** Editorial clarity is dominant, and CLAUDE.md's own audience line names *both* halves of the stated audience explicitly — "experienced practitioners... plus recruiters working in regulated healthcare" — so the recruiter half already gives this camp's position standing without needing to override practitioner-register preferences. The resolution favors a single first-use expansion per acronym (not repeated glossing throughout), which costs practitioners nothing in reading speed after the first instance and removes the barrier for the recruiter half of the named audience.

---

## Prioritized changes

### High confidence

> Suggested by four or more camps, OR by the dominant camp with zero opposition.

1. **Correct the citation-count drift in the academic dot plot.** HERD 2019 is sized/annotated as "11 citations" (lines 1844, 1861) against a live Publications count of 13 (line 2688); JIHI 2014 is sized/annotated as "23 citations" (line 1852) against a live count of 25 (line 2756).
   - **Camps backing:** Encoding rigorists (hill-to-die-adjacent), Pipeline and reproducibility (hill-to-die-on)
   - **Camps opposing:** none
   - **Files / lines:** index.html:1841-1864, 1977-1985, 2688, 2756

2. **Rewrite the hero career-arc figcaption to state an actual claim**, scoped only to what the current (uniform-weight) chart encodes — do not pre-empt Conflict 1's unresolved annotation-weight question.
   - **Camps backing:** Editorial clarity (hill-to-die-on)
   - **Camps opposing:** none (Encoding rigorists raised the brevity defense but did not oppose strengthening the caption itself)
   - **Files / lines:** index.html:1646-1648

3. **Distinguish "no citation data" from a measured low value in both dot-plot SVGs** by rendering unknown-count dots as open/unfilled circles rather than reusing the smallest filled radius.
   - **Camps backing:** Encoding rigorists (hill-to-die-on)
   - **Camps opposing:** none
   - **Files / lines:** index.html:1841-1846, 1849-1850, 1855-1856, 1858-1859, 1980, 1982-1983

4. **Add `<title>`/accessible text to the presentation dots in both dot-plot SVGs**, giving assistive technology the same year-by-year shape (including the 2015 peak) that sighted readers get visually.
   - **Camps backing:** Access floor (hill-to-die-on), Encoding rigorists
   - **Camps opposing:** none
   - **Files / lines:** index.html:1873-1902, 1996-2017

5. **Expand QBP, HEDIS, and ECDS at first use** (per Conflict 5's resolution: once each, not repeated throughout).
   - **Camps backing:** Editorial clarity, Access floor
   - **Camps opposing:** none substantive (resolved in Conflict 5)
   - **Files / lines:** index.html:2389, 2424, 2491-2492, 2218, 2623-2625

### Medium confidence

> Suggested by two or three camps with no substantive opposition; OR by one dominant camp opposed only by a suppressed camp.

1. **Restructure the tag-frequency rollup into a grouped or top-N view** rather than a 37-item undifferentiated wall.
   - **Camps backing:** Editorial clarity, Data humanists
   - **Camps opposing:** none
   - **Files / lines:** index.html:2072

2. **Add a one-line gloss explaining the Speaking list's "year shown once per cluster" convention.**
   - **Camps backing:** Editorial clarity, Encoding rigorists
   - **Camps opposing:** none
   - **Files / lines:** index.html:2801-2819

3. **Restyle the Gantt's "peer reviewer (ongoing)" mark to match its sibling labels**, or give its difference an explicit encoded meaning.
   - **Camps backing:** Encoding rigorists, System designers
   - **Camps opposing:** none
   - **Files / lines:** index.html:3008-3013

4. **Label the scorecard's alert-threshold tick with its numeric value.**
   - **Camps backing:** Encoding rigorists, System designers
   - **Camps opposing:** none
   - **Files / lines:** index.html:998, 2551, 2569

5. **Correct CLAUDE.md's own stale Gantt-accent reference** in its Accent-discipline paragraph (a documentation-only fix, flagged here for completeness since it affects this critique's own Locked-design-rule check going forward).
   - **Camps backing:** Pipeline and reproducibility
   - **Camps opposing:** none
   - **Files / lines:** CLAUDE.md §Palette "Accent discipline"; index.html:3043

### Low confidence

> Suggested by one camp with opposition from non-suppressed camps; deferred for explicit user review.

1. **Differentiate annotation weight in the career arc by narrative importance.** Resolved against in Conflict 1 (locked owner decision).
   - **Camps backing:** Encoding rigorists
   - **Camps opposing:** Editorial clarity
   - **Files / lines:** index.html:1696-1731

2. **Add an approximate trajectory between outcome-figure endpoints.** Resolved against in Conflict 2 (calibrated-claims / compound-claim integrity).
   - **Camps backing:** Data humanists (hill-to-die-on, expected loss)
   - **Camps opposing:** Encoding rigorists, Pipeline and reproducibility
   - **Files / lines:** index.html:2249-2262, 2306-2318

3. **Add a persistent visible click affordance to career-arc bands and publication dots.** Resolved against in Conflict 3 (dominant-camp rule).
   - **Camps backing:** System designers
   - **Camps opposing:** Editorial clarity
   - **Files / lines:** index.html:1483-1519

4. **Make the top nav sticky.** Resolved against in Conflict 4, with only a partial orthogonal mitigation (confirm the footer nav isn't the sole return path) surviving.
   - **Camps backing:** System designers (hill-to-die-on, expected loss)
   - **Camps opposing:** Editorial clarity
   - **Files / lines:** index.html:461-484

---

## Anti-patterns flagged

1. **Feature-creep coalition.** The High-confidence tier alone touches four separate SVG figures (the dot plot twice over, the hero caption, and the acronym glosses spread across the Stars Cliff project and Experience prose) in one pass. Shipping all five High-confidence items in a single commit risks an oversized, hard-to-review diff. Recommend splitting by figure: (a) dot-plot data/accessibility fixes together, since they touch the same two `<svg>` blocks in one sitting anyway; (b) the hero caption rewrite alone; (c) the acronym glosses alone. Each should independently pass `scripts/lint_gantt.py` / the relevant build script's regeneration where applicable.
2. **Strip-everything coalition.** Not detected this iteration — no camp prescribed wholesale deletion of any section or figure.
3. **Caption-rewrite-without-data-rework.** The hero caption fix (High confidence #2) must not be shipped as a caption that asserts more than the current chart encodes — for instance, do not write a caption implying the 2020 acquisition is the pivotal moment of the arc (differentiated emphasis) until or unless Conflict 1's annotation-weight question is separately revisited and its resolution changes. Ship the caption scoped to what the uniform-weight chart currently shows: three overlapping career phases converging into one continuous line, not a differentiated three-tier hierarchy of importance.

---

## Recommended next iteration

Ship the five High-confidence items first, in the three batches named under Anti-patterns above: the dot-plot data-integrity and accessibility fixes together (citation-count correction, missing-vs-measured distinction, and presentation-dot titles all touch the same two SVGs and are cheapest to verify in one sitting), the hero caption rewrite alone, and the acronym-gloss pass alone. Shipping these should retire Encoding rigorists' and Pipeline's current hill-to-die-on findings outright and substantially soften Access floor's and Editorial clarity's; the next critique pass should show those camps' top findings shift to the current Medium-confidence tier (the Gantt label-consistency fix and the scorecard threshold label becoming the new candidates for those lenses' hardest findings). The trigger condition for revisiting the two deferred Low-confidence items that were resolved against on process grounds rather than dismissed as wrong: if a future citation refresh causes the dot plot to drift again after the one-time patch in High-confidence #1, that recurrence is the signal to bring the dot plot's sizing under a marker-region contract (Pipeline's finding #2 in its camp critique) rather than hand-patching it a second time.
