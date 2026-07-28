# Outstanding-notes review — 2026-07-28

A sweep of every open recommendation in the repo, verified against current
source, and put to the Design Council where it is a design question.

**Why this exists.** The improvement notes had accumulated across five
documents, two GitHub issues, and a corrupted carry-forward block, with no
single view of what is actually still open. Several items are recorded as open
but shipped weeks ago, which makes the backlog look larger and less trustworthy
than it is. This document is the triage, not the fix. Nothing here has been
changed except where noted.

**Sources read:** `docs/homepage-critique-2026-07-19.md`,
`docs/homepage-iteration-2026-07-26.md`, `docs/qa-audit-2026-07-28.md`,
`docs/streamlining-qa-plan.md`, `docs/critique/subpage-backlog.md`,
`critiques/critique-index-2026-07-04.md`, `reviews/2026-05-23-synthesis.md`,
`reviews/README.md`, `TODO.md`, `src/content/blog-ideas.yaml`, issues #43 and
#110.

---

## 1. Already shipped, still recorded as open

The highest-value finding. Five records are stale; correcting them removes more
apparent backlog than any actual change would.

| Record | Says | Actually |
|---|---|---|
| `homepage-critique-2026-07-19.md` §4.1 | `lang="fr"` on Montréal is "deferred… not urgent" | **Shipped** in `6f7bea8` via `venue_lang` in `publications.yaml` + a render-time wrapper in `_publications.py`. |
| `homepage-critique-2026-07-19.md` §8 | Palette is "a proposal, not a change. Nothing was written to `index.html`" | **Shipped** 2026-07-23. `index.html` carries the board's Lichen values verbatim. |
| `TODO.md:79-83` | Custom `404.html` pending; "GitHub Pages serves its generic 404" | **Shipped.** Styled, with the GoatCounter 404-prefix callback. |
| `TODO.md:20-23` | Bing `REPLACE_WITH_TOKEN` lives in `index.html` and `base.html` | Removed from `index.html`; survives only in `scripts/templates/blog/base.html:14-17`, commented out. |
| `reviews/2026-05-23-synthesis.md:121-128`, `reviews/README.md:213-226` | 8 Tier-3 items open | **Owner resolved all 8 on 2026-06-08** in an issue #43 comment: 6 `wontfix:`, 2 `defer:`. Never propagated back. |

**Two follow-ons worth noting:**

- The Montréal fix left a genuine residual nobody recorded: `cv.md:58`'s
  presentation entry is still unwrapped while the homepage equivalent
  (`index.html:3050`) is wrapped, so the two surfaces now disagree.
- One `wontfix:` (keep the "Featured" subhead as wayfinding) **contradicts
  `CLAUDE.md:800-803`**, which still says the label "can be removed in a later
  pass." The owner decided; CLAUDE.md should stop inviting the opposite.

Also: issue #43's body is corrupted by a carry-forward loop. The Tier-3 block is
duplicated roughly six times, and items already shipped (cliff figure, sparkline
stems, HITRUST framing, dbt sentence, team-size line) reappear unchecked.
`scripts/review/README.md:149-155` explains the mechanism: `wontfix:` suppresses
matching items, `defer:` deliberately does not. A `defer:`-heavy history
therefore grows without bound. **The issue is currently not readable as a
worklist.**

One unreconciled contradiction: the Tier-1 "add one production-system anchor
with a number" item shows `[x]` on issue #43 but `[ ]` in
`reviews/2026-05-23-synthesis.md:106` and `reviews/README.md:228-233`. No
public-safe number appears in the BHA fold, so it is most likely still open.

---

## 2. Design Council — agenda

Convened per `CLAUDE.md` §Agent panels. Recommendations only; nothing here is a
change, and the disagreements are recorded rather than collapsed.

### 2.1 The sidenote band at 761-1000px — the one formally unresolved item

`homepage-critique-2026-07-19.md` §3.4 records this as **"Status: unresolved.
Luke and Edward disagree about a number, not a principle, and neither moved. All
three reject do-nothing."** Verified still true: `grep -c 'box-sizing'
index.html` → 0, so `content-box` applies; `index.html:290-293` still sets
`float: right; margin-right: -60%; width: 50%`. Direction B added a 1000px media
query but it touches only `.split-hero`, so **761-1000px remains ungoverned**.

It was blocked on one thing: *"None of this has been seen in a browser"* (§7,
six unchecked verification boxes). **That blocker is now removable** — this
session used a headless Chromium harness to settle the split-hero question with
measurements instead of argument, and the same harness answers §3.4.

- **Edward:** "only sub-850px is genuinely degraded" — a narrow fix.
- **Luke:** iPad portrait is 768px; the wider viewport getting the worse
  experience is the defect, not the ch count.
- **Haben:** explicitly **no veto** — 1.4.8's 80ch is a maximum and AAA, so this
  is a taste call, not a compliance one.

**Recommendation:** stop arguing the threshold and measure it. Render the
sidenote band at 761 / 800 / 900 / 1000px and read the actual ch count, then
pick the breakpoint from the number. Carry the doc's engineering caution into
the fix: `width` and `margin-right: -60%` are **coupled** — widening one moves
the note's left edge into the body column — so they must be retuned together and
verified visually, not computed.

### 2.2 The audience question — route it to the Focus Group, not here

§4 Tier 1: *"Tufte designed for a reader with an hour. `CLAUDE.md` names an
audience that includes recruiters. Nearly every Tier 2 item resolves differently
depending on which reader wins."*

The doc explicitly routes this to the **Focus Group** (reader reception), not
the Design Council. **Recommendation:** honor that routing, and settle it before
spending council time on §2.5 and §2.6 below, both of which it gates.

### 2.3 Mobile: two concrete defects — the strongest ship-now candidates

From §5, Casey's red flag, both halves verified:

- All three `.stat-num` margin stats — 373,000 care gaps, the 10,000-adult
  cohort, 7 talks in 2015 — sit inside marginnotes, and `index.html:429-431`
  hides `.sidenote, .marginnote` at ≤760px. **The three most quotable numbers on
  the page are invisible by default on majority-traffic viewports**, which
  inverts the stated intent of surfacing buried figures.
- The mobile `label.margin-toggle` rule (`index.html:421-428`) sets only
  display, color, text-decoration and cursor. **No `min-height`, no padding, no
  hit area**, against 12 `⊕` glyphs — while the arc bands and publication dots
  got explicit 24px+ touch overlays.

The second directly contradicts Direction B's own Luke ruling ("Keep 24px+ touch
overlays"). **Recommendation: ship both.** These are the only items in the whole
backlog that are unambiguous defects, scoped, and unblocked by any open
question.

### 2.4 The Direction B hand-off trio, plus what has compounded around it

`homepage-iteration-2026-07-26.md:156-170` left three items. All still open, and
two have since gained weight from independent findings:

- **Writing-column length vs. the timeline's fold position.** Now better
  understood: the split-hero balance is set by whichever column grows unchecked,
  and this session's fix came at it from the opposite side (see the appended note
  in that doc). The ~38% column needs a prose budget; the ~62% column needs a
  title cap. Treat as one question, not two.
- **`#writing` is now thin** — cadence sparkline and a margin note, nothing else.
  Compounded twice: the sparkline is independently flagged as *"the least legible
  figure on the page"* (no y-axis, no scale, 2 vs 3 posts indistinguishable), and
  `qa-audit:208-211` notes the nav's "writing" label now points at that anchor
  while `/blog/` is called "Writing" in the blog nav and "Blog" in every footer.
  **Recommendation:** treat as one composite question — what is `#writing` for
  now that its articles moved to the hero? Answering it probably also answers the
  sparkline.
- **Proposition copy is provisional** — an owner call, not a council one.

### 2.5 The page closer

§4 Tier 2 P2. Direction B moved Certifications off the last slot, but the
underlying decision was never made — `CLAUDE.md` already frames it as *"a fresh
design decision, not a restoration."* Gated by §2.2. **Recommendation:** hold
until the audience question resolves.

### 2.6 Projects index still folded

The count shipped (`More projects (4)`); the substantive objection — the index
*"was designed as a visible small-multiples grid"* — did not. Gated by §2.2.

### 2.7 Palette follow-through

§8's own closing caveat asked that a chosen direction get *"hand-tuning that
palette's five roles against the real page (the ten figures, the sidenotes, the
`#7a0000` accent-sentinel remap) and a full-council convening — not a
find-and-replace of the tokens."* The shipped hexes are the board values
verbatim, so that pass appears not to have happened. A second, narrower item at
§8:448-450 asked that the nudge-vs-statement vote be *"held explicitly, not
averaged away"* if a single winner were ever forced. One was.

**Recommendation:** low urgency — the palette is live, passes AA, and nobody has
complained. But record that the hand-tuning pass is outstanding rather than
letting the adoption imply it happened.

### 2.8 Two live `defer:` options from issue #43

Both are genuinely open, both have explicit trigger conditions:

- **`:target`-based section indicator.** An `IntersectionObserver` scrollspy
  violates the no-JS rule, but the owner held rather than rejected: *"a
  `:target`-based fallback stays a possible future option."*
- **`scripts/build_figures.py`.** Deferred with a live trigger: *"revisit when a
  second chart visibly drifts out of truth."* `critiques/critique-index-2026-07-04.md:331`
  records a matching trigger for the dot plot specifically. Neither has fired.

---

## 3. Not committee work — verified wrong, just needs doing

Ranked by real-world cost. None is a design question.

1. **`resume.md:3` / `resume.html:193` advertise a different contact email**
   (`zaherkarp@gmail.com`) than `cv.md`, `cv.html`, `index.html:3443` and
   CLAUDE.md (`me@zaherkarp.com`). The resume is the surface most likely to reach
   a recruiter.
2. **`colophon/index.html` says "eleven linters" in six places**, including
   **visible SVG text at `:144`**. Actual: twelve. A public page wrong on its own
   subject, and the subject is the site's own rigor.
3. **The `$50M` cliff number carries four different denominators** across
   `index.html:2475/:2510` and `/star-rating-predictor/`, and
   `star-rating-predictor-methodology.md` disagrees with itself at L6 vs L12.
   Directly violates §Calibrated claims, which requires naming the denominator.
4. **healthfinch outcome numbers disagree** between `index.html:2394` ("roughly
   ten users to more than one hundred", "400 hours *annual*") and `resume.md:33`
   ("**7×**", "400+ prep hours *per quarter*"). Both the multiple and the period
   conflict, and the bare "7×" is the exact construction §Calibrated claims
   forbids.
5. **Propagate the issue #43 decisions** into the two review docs, fix the
   `CLAUDE.md:800-803` contradiction, and reconcile the Tier-1 `[x]`/`[ ]` split.
6. **Correct the five stale statuses** in §1 above.
7. **Documentation drift**, all verified: `README.md:526` "nine linters" vs its
   own L220 "twelve"; `README.md:686` "7 `<details>` folds" (actual 11);
   `README.md:690` references the removed SkillSprout slope graph; `README.md:693`
   places the Gantt between Testimonials and Education (Direction B moved
   Testimonials to the end); `CLAUDE.md:498` still names the retired `tl-compact`
   while `:39`, `:345` and `:470` correctly say retired; `CLAUDE.md:742`
   references the dead `.sankey-figure`; `CLAUDE.md:135` says "~2,570 lines" of
   inline CSS (actual ~1,740); `docs/pipelines.md:192` says "nine pipelines" then
   enumerates eleven.
8. **Dead code:** `index.html:918-935` `.sankey-figure` CSS — verified the only
   dead class family in the file. Plus the section-number collision: two blocks
   numbered **19** (`PRINT OVERRIDES` at `:1577`, `SPLIT HERO` at `:1627`), which
   makes CLAUDE.md's "sections 19 / 20 / 20.1" ambiguous.
9. **`robots.txt` does not disallow `/critiques/`, `/evaluations/`, `/reviews/`,
   `/docs/`, `TODO.md`, `CLAUDE.md`.** `/evaluations/` contains a candid hiring
   eval. Worth an explicit decision either way rather than an accident.
10. **Em dashes in ~250 blog page titles.** `scripts/build_blog.py` hardcodes
    `f"{post['title']} — Zaher Karp"` at L285, L337, L355, L408, L423, feeding
    `<title>` and both social tags. Chrome is supposed to be em-dash-clean; the
    pre-push grep covers only four files, so `blog/` output is unguarded.
11. **`lint_links.py:63` stops path capture at `#`**, so cross-page fragments are
    never validated. This is the class of dead link the 2026-07-28 audit found
    eight of; it can recur silently.

---

## 4. Untouched lanes, recorded so they are not rediscovered

- **`docs/critique/subpage-backlog.md` is orphaned** — referenced nowhere, and
  all four of its source citations point into `archive/design-review-presentations/`,
  which does not exist. Its substance is still live: **the critique pipeline has
  only ever run against `index.html`, never the three interactive subpages**, and
  the Subpage archetype in `methodology.md` has never been exercised. Its
  strongest single finding: a "Star Rating Predictor" that emits a scalar with no
  prediction interval *"is not a statistical graphic, it is a fortune teller in
  serif type."*
- **`docs/streamlining-qa-plan.md:240`** — the one explicitly deferred gate:
  post-build sanity checks inside the three build workflows, which would close
  the bot-commit-lint seam (today only `lint.yml`'s weekly cron catches
  lint-violating *generated* output). Cheap; the env is already installed there.
- **§7 of the same doc** lists five discussion-only items that are deliberately
  *not* scheduled. Leave them that way.
- **`TODO.md`** — four genuinely open items after the two stale ones are struck:
  Bing verification (manual), per-post OG images (needs a Pillow dependency
  decision), a homepage build-provenance line, and `rel="me"` links (the
  cheapest open item in the repo, self-described as "five minutes").
- **Blog backlog (issue #110)** — three drafts, zero captured ideas, all aging;
  `how-this-site-builds-itself` at 44 days untouched. Content scheduling, not
  design.

---

## Recommendation

Three things, in order:

1. **Ship §2.3** — the two mobile defects. Unambiguous, scoped, unblocked.
2. **Do §1 and §3.5-6** — correct the stale records. It is a text-only pass and
   it makes every future review start from a truthful baseline.
3. **Settle §2.2 with the Focus Group**, then re-open §2.5 and §2.6, which it
   gates.

§2.1 is the most interesting item and is now unblocked, but it is a taste call
with no user complaint behind it. §3.1-4 are the ones with actual real-world
cost and no design content at all.
