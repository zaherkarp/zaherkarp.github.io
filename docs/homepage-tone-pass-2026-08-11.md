# Homepage tone pass, 2026-08-11

Owner: "The language changes feel very grandiose. How can we make them less
so? Talk to the committee and group and think about it, maybe use stop-slop
as a guide."

Target: `section.cases` (the case layer added 2026-08-10) and the hero
proposition. Rollback point: `fd98a24`.

---

## 1. What went wrong, and why it was predictable

The case layer shipped on 2026-08-10 and the owner read it as "canned" the
same day. The de-templating pass that followed
(`docs/homepage-case-layer-2026-08-10.md` §8) correctly diagnosed a
**parallelism** defect: seven strings in lockstep, three gerund-led h3s at the
top of the stack. It fixed the parallelism by rewriting the three h3s as three
differently-shaped **questions**.

That satisfied variety by moving **up in register**. Two of the three new h3s
opened with a wh- word, none named anything falsifiable, and the case bodies
kept the aphorisms that go with that voice. The layer stopped being canned and
started being grandiose within twenty-four hours.

The trap is worth naming precisely, because the next pass will meet it again:
**plainness and variety are independent axes, and the mold contract only
constrains one of them.** "No shared grammatical mold" can be satisfied by
three equally portentous headings in three different shapes. It was.

§8 contains its own counter-evidence, unused: it records that across 24 recent
posts the owner's title voice is "assertive and verb-driven, making falsifiable
statements about named things," and rejects the old h2 for naming "nothing
falsifiable" (`docs/homepage-case-layer-2026-08-10.md:154-158`). All three of
the h3s that pass shipped had exactly that flaw. Naming concrete things is what
makes copy quieter here. Abstraction is the grandiosity, not sentence length.

## 2. The rubric

[stop-slop](https://github.com/hardikpandya/stop-slop) (Hardik Pandya, MIT),
applied as a guide and **not vendored** into `scripts/review/prompts/`. The
rules that fired, and where:

| stop-slop rule | String | Was at |
|---|---|---|
| No wh- sentence starters | `What a number can be trusted to say` | `index.html:2568` |
| No wh- starters; dramatic fragmentation | `Whether anyone uses it` | `index.html:2582` |
| Formulaic construction (journey template) | `From specification to running code` | `index.html:2575` |
| Formulaic construction, second use | `from analyst triage to executive review` | `index.html:2583` |
| Binary contrast | `Cut points are equilibria, not trends` | `index.html:2570` |
| False agency | `teaches its stakes`, `nine research years sit underneath` | `index.html:2570` |
| False agency | `measure logic becomes SQL and Python` | `index.html:2577` |
| False agency, agentless | `The pattern has scaled` | `index.html:2577` |
| Passive + triad | `can be reviewed, tested, and defended` | `index.html:2577` |
| Quotable-sounding statement | `hands still in the code` | `index.html:2584` |
| Quotable-sounding statement | `and still build.` | `index.html:2148` |

`How I work` survives the scan as a wh- opener and is **deliberately kept**:
owner choice on the record (`CLAUDE.md` §Case layer), and near-unanimously
not-a-problem in reception (11/12).

`nobody opened` survives as a "lazy extreme" and is **deliberately kept**: the
Focus Group found it is believed *because* it is unflattering (finding R17,
7/12). The stop-slop rule targets false authority ("everyone", "always"), not
a concrete deflating detail. Documented so it is not swept later.

## 3. Joint panel convening

Both panels, per the 2026-07-28 joint-convening rule. Lanes with no stake in a
copy-only pass (Val, Luke, Alan, Bret) were **not** convened, per
`design-council.md:49-50` ("rather than theatre-casting ten personas for a
comma"). Three groups ran: Jess + Massimo (voice and type, leading), Edward +
Nathan + Steve (rigor, story, scanning), and a 12-panelist Focus Group across
three rounds including antagonists and an emotional-register round.

### 3a. Reception findings (Focus Group)

1. **The charge is elevation, not inflation** (unanimous, 12/12). No panelist
   alleged a false or inflated claim; several found *under*-claims relative to
   `resume.md`. Elevated diction sitting on modest, well-attributed facts.
2. **The defect is positional** (majority, 9/12): diction stays plain until the
   last three to five words of each body, then lifts. Case 02 was the only body
   ending on a boring noun (`the AWS to Azure migration`) and was the body the
   panel liked best and flagged least.
3. **The de-templating pass moved the mold down one altitude rather than
   removing it** (majority, 9/12): all three bodies were exactly two sentences,
   all three pivoted mid-sentence on a colon or semicolon, `the current role`
   was identical link text twice with `owns` as its verb both times. The
   40-portfolios-a-week reader diagnosed this from cadence before reading a
   single claim.
4. Register **buys** credibility on exactly one string (`Cut points are
   equilibria, not trends`, unanimous on substance) and **costs** it on three.

### 3b. Design findings (Design Council)

| # | Issue | Element | Raised by | Consensus | Fix |
|---|---|---|---|---|---|
| D1 | `.cases` selector collision (see §4) | `index.html:1088` vs `:2564` | Edward | single voice, verified | rename formula class |
| D2 | h3s are "oracles": passive, name nothing falsifiable | `:2568`, `:2582` | Jess, Edward, Steve | majority | rewrite plainer |
| D3 | From-X-to-Y used twice in fifteen lines | `:2575`, `:2583` | Jess | single voice, verified | rewrite both |
| D4 | Four inanimate agents in two sentences under a heading that says "How I **work**" | `:2570`, `:2577` | Jess | majority | first person |
| D5 | No h3 names the domain, so each block costs two fixations instead of one | `:2568`–`:2582` | Steve | majority | domain nouns |
| D6 | Semicolon splices carry the load the em-dash ban displaced; terminal comma-runs are cadence, not sentence | `:2570`, `:2584` | Massimo | single voice | periods, varied length |
| D7 | Final sentence restates a number already in page prose | `:2584` | Edward | unanimous | cut |

Nathan dissented throughout: quieter headings weaken the cue that the three
blocks are one set, and the `it` in `Whether anyone uses it` was the only
device chaining case 02 to case 03. See §6.

### 3c. Where the two conflict

**C1 — the h3s themselves.** The Council (Jess, Massimo, Edward, Steve) wanted
them rewritten. The Focus Group wanted them **kept**, arguing they are the part
of the layer earning its register, that the sequence
(judgment → execution → adoption) is the answer to the 2026-05-23
role-calibration gap, and that the case layer is "the only section that sounds
like a person with an opinion; the rest is record."

Not merged. **Owner ruled: rewrite all three plainer.** The reception cost is
real and is accepted, not refuted. If the layer later reads as three parallel
résumé buckets rather than one argument, this is the finding to reopen, and the
fix is *not* to re-grandify the headings.

**C2 — restated numbers.** `CLAUDE.md` §Case layer forbids a case restating a
number already in page prose. The shipped layer breached it (§4b). The Focus
Group's position is that the breach was **the good part**: those numbers are
the layer's clearest answer to the role-calibration gap, and the 60-second
reader the layer exists for will never reach the sources. The design contract
optimizes for the hour-long reader inside a surface built for the 60-second
one. Reception would have fixed the *flattening* ("eight editors" for "up to
eight copy editors, designers, and photographers"); the contract fixes the
*repetition*. Opposite edits. The contract won here; the conflict is not
resolved and is recorded for the next pass.

**C3 — Nathan's parked objection is now answered, not by argument but by
data.** §8 recorded it unacted. Twelve of twelve panelists read the three
blocks as one set, from visual grouping and the repeated "In writing:" labels,
not from any heading. The mechanism Nathan defends is one reception does not
use. Closing it.

## 4. Two defects found while working, neither about language

### 4a. `.cases` matched two unrelated things (fixed, owner-approved)

`index.html:1088` defined an **unscoped** `.cases` rule for the Huber formula's
`<span class="cases">` piecewise brace. `section class="cases"`, added
2026-08-10, matched the same selector. The section-23 rules are all descendant
selectors and reset none of it.

Verified in Chromium rather than inferred: `section.cases` computed to
`display: inline-block` with a `1px solid var(--ink)` left border, `10.2px`
padding-left and `5.1px` margin-left, sitting at `left: 61px` and `width: 784px`
against `left: 56px` / `width: 773px` for **every other section on the page**.
An undesigned third decorative mark, against the two-mark limit
(`design-council.md:262-267`).

Fix: the formula's class renamed `.cases` → `.piecewise` (CSS, the class-index
comment at `:1068`, and the markup at `:2679`). `.case-line` and `.case-cond`
do not collide and were left alone. After: `section.cases` computes
`display: block`, `border-left: 0px`, `left: 56px`, `width: 773px`, identical
to `section#experience`; `span.piecewise` keeps its brace, both case-lines
render, zero `span.cases` remain.

**No linter caught this and none could.** `lint_html` checks tree structure,
`lint_palette` checks token drift. A valid rule matching an unintended element
is invisible to both.

### 4b. The shipped layer breached its own no-restated-numbers contract

`Two data scientists today` (`:2584`) restated `team of two data scientists`
(`:2634`, itself a §Calibrated claims canonical example), and `eight editors
once` restated the Sustainable Clarity lead. Removed with the sentence.

## 5. Two factual defects in the copy, found by the antagonist round

Both verified against source before acting:

- **`nine research years` pointed at the wrong evidence.** The link resolves to
  `#publications`, whose lead reads "Six peer-reviewed papers in health services
  research, **2012 to 2019**" (`index.html:3287`) — six papers over an
  eight-year window. Nine matched neither; it matched the career band's research
  lane (2009–2018), a different anchor. "Research years" was a unit coined for
  the sentence, and `sit underneath` asserted a transfer from health-services
  research to Stars forecasting that nothing on the page argues. Cut.
- **`The pattern has scaled` attributed healthfinch's work to the current
  role.** The sentence's subject was HEDIS measure logic under BHA release
  governance; the evidence was Epic Clarity **report libraries**, which
  `src/content/resume.md:31` places at Healthfinch (2017–2020). The resume's own
  credibility-carrying verbs — *authored*, *reusable*, *deployed* — were dropped
  in favour of an agentless perfect tense. The rewrite restores them verbatim
  and marks the era with "Earlier".

A third, not acted on: an ex-CMS reader noted that cut points are hierarchical
clustering outputs on a distribution, then constrained by guardrails and Tukey
outer-fence deletion, so "cut points **are** equilibria" is a modeling claim in
definitional dress. The linked post knows this; the homepage compression dropped
the proof that it knows it. The rewrite sidesteps the issue by stating the
mechanism ("CMS sets cut points from where every plan lands") instead of the
thesis, and letting the linked post carry the argument.

Related: `Cut points are equilibria, not trends` was not authored for the
homepage. It is the verbatim section heading of Exhibit one in
`src/content/blog/lucas-critique-stars-forecasting.md`. A thesis lifted out of
the argument that earns it is a slogan, whatever its merits in place.

## 6. Before and after

Round one is below; **round two (§6a) supersedes every heading and deck in
this table.**

| | Before | After (round one) |
|---|---|---|
| proposition s2 | I lead a small data science team and still build. | I lead a small data science team and review its code. |
| h3 01 | What a number can be trusted to say | **Cut points move** |
| body 01 | Cut points are equilibria, not trends; forecasts built on them break when the rules move. The current role owns that projection problem end to end, the Stars Cliff Simulator below teaches its stakes, and nine research years sit underneath. | CMS sets cut points from where every plan lands, so a forecast trained on last year's trend misses in the years the rules change. I own that projection in my current role, and the Stars Cliff Simulator below lets you move a measure and see the rating change. My published research comes from the years before that. |
| h3 02 | From specification to running code | **Auditable measure logic** |
| deck 02 | …specifications **written as** production pipelines… | …specifications, **running as** pipelines… |
| body 02 | HEDIS … measure logic becomes SQL and Python that can be reviewed, tested, and defended in a client audit… The pattern has scaled: Epic Clarity libraries across 50+ health systems… | I write HEDIS … measure logic as SQL and Python I can defend in a client audit… Earlier I authored reusable Epic Clarity report libraries deployed across 50+ health systems, and moved the analytics stack through the AWS to Azure migration. |
| h3 03 | Whether anyone uses it | **In use** |
| deck 03 | Analytics that people adopt, from analyst triage to executive review, and the team behind them. | Dashboards and a daily feed that analysts and executives open, and the team that keeps them running. |
| body 03 | …replaced spreadsheet workflows, adopted by data science and the CEO. Two data scientists today, eight editors once, hands still in the code. | …I built the cut-point review dashboard at Baltimore Health Analytics that replaced spreadsheet workflows, adopted by data science and the CEO. |

**Heading shapes in round one, checked as distinct** per the mold contract:
independent declarative clause (`Cut points move`) / bare noun phrase
(`Auditable measure logic`) / prepositional phrase (`In use`). None
gerund-led, so the 2026-08-10 defect was not restored. **Round two abandoned
shape-distinctness at this tier entirely; see §6a.** What survives from this
paragraph is the length rule: 2 / 3 / 3 words now, still deliberately not a
monotone gradient, per Jess's objection that an ordered gradient is itself a
mold in the metrical dimension.

**Preserved verbatim**, all contract-protected: the HEDIS parenthetical (the
page's only home for that expansion), `adopted by data science and the CEO`
(`resume.md` wording), `50+ health systems` (the layer's only number), deck 01,
the three `In writing:` labels, and `How I work`.

**Costs, stated plainly.** The `#exp-sustainable` exhibit link leaves the case
layer with the cut sentence; the editorial thread now lives only in the hero
lede and the Experience record. Case 03 is now two sentences against Case 01's
three. The Case 02 → 03 `it` backreference is gone, as the owner's ruling
requires. `I built` is new and is sourced: `resume.md:13` records "Built a
self-service dashboard for forecast-versus-actual Star Ratings cutpoint review",
and the player-coach claim the proposition makes now has evidence under it
instead of being asserted twice with none.

## 6a. Round two: complete sentences (same day)

Owner, after reading round one: "also i really need correct grammar and
complete sentences."

The complaint was correct and round one had made one part of it worse. Three
findings, all genuine grammar rather than style:

1. **All three decks were fragments punctuated as sentences**, and had been
   since the layer shipped on 2026-08-10: noun phrases closed with a full stop
   (`Measure methodology and cut-point forecasting in Medicare Advantage Star
   Ratings.`), no finite verb in any of them.
2. **Round one introduced two more fragments in the h3 tier** (`Auditable
   measure logic`, `In use`) while chasing three distinct grammatical shapes.
3. **Two defects in round one's own bodies.** In Case 03, `adopted by data
   science and the CEO` sat immediately after `spreadsheet workflows`, so the
   participial phrase could attach to the workflows rather than the dashboard.
   In Case 02, a comma preceded a compound predicate sharing one subject
   (`I authored …, and moved …`).

**Owner ruled headings EXEMPT.** Headings are conventionally noun phrases; no
editor calls `Projects` a fragment error, and all thirteen other h2s on this
page are bare nouns. Decks and bodies carry the complete-sentence rule.

| | Round one | Round two |
|---|---|---|
| h3 01 | Cut points move | **Stars measurement** |
| h3 02 | Auditable measure logic | *(unchanged)* |
| h3 03 | In use | **Dashboards people open** |
| deck 01 | Measure methodology and cut-point forecasting in Medicare Advantage Star Ratings. | I work on measure methodology and cut-point forecasting for Medicare Advantage Star Ratings. |
| deck 02 | CMS quality-measure specifications, running as pipelines over… | CMS quality-measure specifications **run** as pipelines over… |
| deck 03 | Dashboards and a daily feed that analysts and executives open, and the team behind them. | Analysts and executives open these every day, and my team keeps them running. |
| body 01 | CMS **sets** cut points **from where every plan lands**… | CMS **computes** cut points **from the scores every plan reports**… |
| body 02 | …Python I can defend…, governance I own…. Earlier I authored … systems, and moved the stack… | …Python **that** I can defend…, governance **that** I own…. Earlier I authored … systems. **I also moved** the stack… |
| body 03 | I built the cut-point review dashboard at Baltimore Health Analytics that replaced spreadsheet workflows, adopted by data science and the CEO. | **At Baltimore Health Analytics I built** the cut-point review dashboard that replaced our spreadsheet workflows, **and it was** adopted by data science and the CEO. |

### The contract this breaks, deliberately

Three bare noun phrases are a **matched grammatical mold**, which
`docs/homepage-case-layer-2026-08-10.md:176-180` forbids outright. Flagged to
the owner before the edit rather than shipped quietly; the owner chose
consistency.

The narrowing recorded in `CLAUDE.md` §Case layer is that the contract now
governs **rhetorical templates, not taxonomies**, and no longer binds the h3
tier at all. The distinction is load-bearing and worth stating precisely: three
gerund-led parallel constructions ("Deciding what… / Making… / Building…") are
a device the reader *hears*, and hearing it is what made the layer read as
canned. Three nouns naming three domains are the same thing every other
heading on the site already is. The deck and body tiers keep the
no-shared-mold rule in full, which is where the 40-portfolios-a-week reader
actually detected the cadence (finding R15).

`body 01`'s change also retires the last trace of the ex-CMS reader's
objection (§5): `CMS computes cut points from the scores every plan reports`
states the mechanism without the "cut points **are** equilibria" modeling
claim, and without the looser `from where every plan lands`.

## 7. Verification

Deps installed into `.venv` (the container's system PyYAML blocks a bare
`pip install -r`; use a venv).

- **All twelve linters green**, before and after.
- **`pytest scripts/tests/`: 155 passed** (no skips; libpango present here).
- Guards: em-dash `0`; accent `12` of 20; `<p>`-wrapped SVG `0`;
  `py_compile epidemic-simulation/sim.py` OK; independence contract clean under
  the exact CI invocation (a naive grep without `--exclude`/comment filtering
  reports six self-referential hits and is not the contract check).
- **Render harness validated before use.** Animations disabled via injected
  stylesheet, served from the repo root. Two identical baseline runs returned
  byte-identical numbers and reproduced the documented reference exactly
  (10,498px @1400, 17,479px @390, 1,873 visible words), so the deltas below are
  trustworthy.

| | Before | Round one | Round two | Net Δ |
|---|---|---|---|---|
| height @1400 | 10,498px | 10,436px | **10,511px** | +13 |
| height @1000 | 11,627px | 11,631px | 11,631px | +4 |
| height @761 | 13,692px | 13,705px | 13,705px | +13 |
| height @390 | 17,479px | 17,421px | **17,506px** | +27 |
| visible words @1400 | 1,873 | 1,882 | 1,891 | +18 |

Round one cut 62px; round two put 75px back, because complete sentences cost
words. The net is +13px at 1400px. **The governing reference height is now
10,511px, not 10,436 and not 10,498.** Round one's `section.cases` measurement
(945px before, 882px after) is not a clean copy delta and is dropped from this
table: the "before" was taken while the `.cases` selector collision was still
rendering the section as an inline-block.

Also confirmed: all three h3s render on **one line at every width** including
390px (two of the three wrapped to two lines at 1400px before); no horizontal
overflow at any width; `navOrderOk` true at all widths (`#writing-hero` <
`#work` < `#about` < `#contact`); `#work` still lands on `section.cases`; dark
mode @1400 identical; the Huber formula's brace and both case-lines render
correctly after the class rename; `og-default.png` regenerated and both
subtitle lines fit the 1200px card.

## 8. Deliberately not done

- **`.hero-lede` left alone.** Jess proposed a rewrite (`That path continues to
  shape how I think about…` is false agency plus a three-item list). It is the
  owner's own 2026-07-29 wording, no Focus Group panelist flagged it, and it is
  outside the 2026-08-10 text the complaint was about.
- **Experience leads, figcaptions, project prose, section leads.** The
  structural scan found one straggler (the Gantt lead-in's "rather than
  following in a tidy sequence"). Left for a future pass.
- **stop-slop not vendored.** Applied as a guide and cited here.
- **`nobody opened` and `How I work` kept**, both against a stop-slop rule, for
  the reasons in §2.

## 9. Rollback

Before: `fd98a24` (merge of PR #127). This pass is copy plus a one-class CSS
rename plus the regenerated OG card; reverting the commit restores the prior
state exactly. Tag push is blocked in this environment's git scope, so the SHA
is the durable rollback point, as with the 2026-07-30 pass.
