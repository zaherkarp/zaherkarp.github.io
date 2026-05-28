# Site review workflow

A multi-agent feedback + iterative implementation loop for `index.html`.
This directory holds the cross-report synthesis reports the workflow
produces; sibling directories hold the per-camp critiques (`critiques/`)
and hiring evaluations (`evaluations/`) those syntheses are built from.

The workflow is independent of the blog / resume / portfolio build
pipelines documented in `CLAUDE.md`. It produces no site changes by
itself; it produces feedback documents that drive iterations of
hand-applied changes.

---

## The shape

Four prompts produce three independent feedback reports plus a
cross-report synthesis with a tiered action checklist. A GitHub Action
reads the synthesis and opens a tracking issue. Iterations work the
checklist, batch-commit per iteration, update the synthesis as work
ships. State lives in the issue body (`- [ ]` items, `defer:` and
`wontfix:` comments) and the next review run carries unchecked items
forward.

```
┌───────────────────────────────────────────────────────────────┐
│ 1. Generate the four reports in a Claude Code session         │
│    (or via API, or by hand). Files land in critiques/,        │
│    evaluations/, reviews/.                                    │
├───────────────────────────────────────────────────────────────┤
│ 2. Batch-commit the reports and push.                         │
├───────────────────────────────────────────────────────────────┤
│ 3. site-review-publish.yml fires on the push, parses the      │
│    synthesis, opens (or updates) a tracking issue, carries    │
│    forward any unchecked items from the prior open issue.     │
├───────────────────────────────────────────────────────────────┤
│ 4. Work the Tier 1 checklist. Each batch: small group of      │
│    related items, single commit, synthesis updated to reflect │
│    what shipped, Tier 2 items promoted as Tier 1 empties.     │
├───────────────────────────────────────────────────────────────┤
│ 5. Check boxes in the tracking issue as items ship. Use       │
│    defer: / wontfix: comments to skip items with a reason     │
│    the next review will see.                                  │
├───────────────────────────────────────────────────────────────┤
│ 6. When Tier 1 empties or you want fresh feedback, regenerate │
│    the reports and the cycle restarts.                        │
└───────────────────────────────────────────────────────────────┘
```

---

## The four prompts

The prompts are **not committed** in this repo by deliberate choice
(Option A scope: publish-only pipeline, prompts live with the
generator). They exist in two places:

1. The Claude Code session that produced the 2026-05-23 reports.
   Search the session history for the multi-agent invocation blocks.
2. Your own private notes, if you've copied them elsewhere.

If you want them versioned alongside the pipeline, drop them into
`scripts/review/prompts/` (the directory is in `.gitignore` only by
absence; nothing in the pipeline depends on their location).

### 1. Craft critique — six-camp data-viz panel

Spawns six parallel sub-agents, each voicing a critic camp:

| Camp | Critics | Commitment |
|---|---|---|
| Encoding rigorists | Tufte, Bertin, Munzner, Wilke | Encoding matched to perceptual rank; decoration is failure |
| Editorial clarity | Cox, Burn-Murdoch, Knaflic, Ritchie, Kirk, Muth, Cairo | Lead with the takeaway; one frame, one claim |
| Data humanists | Lupi, Posavec, Felton, Rosling, Bremer | Data at human scale; hand-shaped marks |
| System designers | Shneiderman, Norman, Krug, Vinh, Maeda, Stefaner, Wu, Bostock, Heer | Visualization is a system the user operates |
| Pipeline & reproducibility | Few, Wickham, Bryan, Xie, Chamberlain | Tidy data, declarative grammar, literate programming |
| Access floor | Inclusive Design (composite voice) | WCAG is the floor, not the ceiling |

Each camp produces critique strictly from its lens. The main thread
surfaces conflicts (3-5 substantive ones), applies per-archetype
tiebreakers from a `findings.md` reference file, produces a prioritized
changes list with high / medium / low confidence and any anti-pattern
flags.

**Output:** `critiques/critique-<YYYY-MM-DD>.md`

**Use when** the page has been substantially designed and you want
multi-lens critique on craft (design, encoding, accessibility, build
hygiene).

### 2. Alignment summary — synthesis of #1

Reads the craft critique and produces three views:

- **Change-by-change consensus ranking.** Every proposed change scored
  by cross-camp support (backers minus opposers, with archetype
  weighting).
- **Pairwise camp alignment.** Which camps agree and disagree across
  all 15 unique pairs, ranked from most-aligned to most-contested.
- **Camp vs. locked design discipline.** Each camp's proposals
  classified as aligned / discipline-extending / discipline-breaking
  against `CLAUDE.md`'s locked tokens.

Plus a combined top-10 weighting both consensus and discipline
alignment.

**Output:** `critiques/critique-<YYYY-MM-DD>-alignment.md`

**Use when** the craft critique has returned and you want to understand
which proposals have the strongest mandate before deciding what to
ship.

### 3. Hiring signal evaluation — eight-evaluator panel

Spawns eight parallel sub-agents at three reading depths:

| Depth | Evaluators |
|---|---|
| 10 seconds | First-impression scanner |
| 60 seconds | Recruiter screen, Executive fit check |
| 5 minutes | Manager-track HM, Director-track HM, Staff-IC-track HM, Peer engineer, Healthcare domain expert |

Each returns five sections (what hit me, what I expected, red flags,
level read, decision) plus a one-paragraph "what would change my
mind." Calibrated to brutal honesty, not coaching.

The main thread aggregates decisions, identifies four gaps
(first-impression, depth-dependency, role-calibration, credibility),
and produces a prioritized changes list keyed to reading-depth
leverage (top-of-page / mid-page / detail).

**Output:** `evaluations/hiring-eval-<YYYY-MM-DD>.md`

**Use when** you want to know what signal the page sends to people
who decide whether to hire you.

### 4. Cross-report synthesis

Reads both the craft critique and the hiring evaluation, classifies
every recommendation as convergent / craft-only / signal-only / in
tension, resolves tensions explicitly, produces a Tier 1 / Tier 2 /
Tier 3 action checklist that the publish workflow can parse.

**Output:** `reviews/<YYYY-MM-DD>-synthesis.md`

**Use when** both panels have returned and you want a single
prioritized list. This is the **load-bearing output** for the publish
workflow's issue checklist.

---

## The publish pipeline

`.github/workflows/site-review-publish.yml` reads the synthesis and
opens (or updates) a single tracking issue per review batch. Carries
forward unchecked items and `defer:` / `wontfix:` comments from the
prior open issue. No API keys; no secrets.

Full pipeline contract, file-naming conventions, deferral comment
syntax, and failure-mode table live in `scripts/review/README.md`.

---

## The 2026-05-23 run

Five iterations across two days, all on
`claude/multi-agent-page-critique-BYmwb`.

### Shipped

| Iteration | Theme | Files |
|----:|---|---|
| 1 | Accessibility floor + chart anchors | `index.html` |
| 2 | Cliff figure honesty pass | `index.html`, new `src/data/cms-ma-pd-stars-2025.csv`, new `scripts/build_cliff.py` |
| 3 | Hiring-signal additions to Experience | `index.html` |
| 4 | Technical and domain credibility (partial) | `index.html` |
| 5a | Chart-fix encoding consistency | `index.html` |
| 5b | Sparkline regeneration | `index.html`, `scripts/build_portfolio.py` |

Pre-push checks (em-dash, accent budget at 19/20, fact-lint,
vocab-lint, blog-lint, SVG-paragraph-nesting) green across all six
commits.

### Headline outcomes

- Cliff figure rebuilt from real CMS 2025 contract-rating distribution
  via `build_cliff.py` (Gaussian KDE, pure Python). Curve peaks at
  rating 3.5 (140 contracts), still high at 4.0 against the cliff,
  drops sharply for 4.5/5.0. Figcaption rewritten to a claim. GitHub
  Source link added on the simulator card. +$50M label gets a
  non-color triangle marker; hatch contrast raised to AA.
- BHA experience meta line now carries team size (two data
  scientists), work mode (remote), and the Lead/Manager promotion
  context — five-of-eight evaluators' top universal flag closed.
- Health Catalyst entry now cites three real customer outcomes
  (Community Health Network, St. Joseph Heritage Healthcare, Valley
  Medical Group) with inline anchors to the published case studies.
- New direct-report testimonial from William Barber (Sustainable
  Clarity, 2013) corroborates the editorial-era management claim.
- Sparkline regenerated as per-week stems from blog frontmatter; the
  May 2026 publishing burst now reads visually instead of being
  flattened to identical dots.
- Named Stars measures (TRC, MAH/MAC/MAD), regulatory levers
  (hierarchical clustering, disaster adjustment), dbt layering at the
  silver tier, HITRUST-as-controls framing fix.
- Mobile dot plot: bars replaced with 17 stacked dots matching the
  wide version's encoding. Dot-plot publication circles wrapped in
  anchors to the entries below. 2020 acquisition callout gets non-
  color markers in both viewport copies. Accessibility floor: `@media
  (prefers-reduced-motion: reduce)` declared, descriptive aria-labels
  on all sidenote/marginnote toggles.

### Tier 3 — still deferred

Each touches a locked design token or sits in an "explicit author
go-ahead" zone. Full per-item rationale and recommendation in
`reviews/2026-05-23-synthesis.md`:

- Subtitle rewrite (locked text in CLAUDE.md §Hero)
- Career arc redesign (locked coordinates)
- Delete "Featured" / "More projects" subhead labels
- Hand-shaped marks on career arc
- Replace dot-area citation encoding
- Full data-driven build pipeline for every figure
- Interactive slope-graph widget
- Current-section nav indicator

### Tier 1 — single item pending input

- Add one production-system anchor with a real number (volume, schema
  count, DAG size, freshness SLO) inside the BHA or Health Catalyst
  fold. Deferred because no number safe for public surface was on hand
  at the time of Iteration 4.

---

## Running it again next quarter

1. Start a Claude Code session against this repo.
2. Generate the four reports for the new date. (The prompt recipes are
   not in this repo; see "The four prompts" above.)
3. Commit the four reports in a single batch and push. The publish
   workflow opens a tracking issue and carries forward unchecked items
   from any open prior issue.
4. Iterate. Update the synthesis as you ship.

### Routine refreshes outside the review cycle

- `src/data/cms-ma-pd-stars-2025.csv` should refresh annually after
  CMS's October Star Ratings release. Update the CSV, re-run
  `python scripts/build_cliff.py`, commit the regenerated path.
- `scripts/build_portfolio.py`'s sparkline regenerates automatically
  on every push that changes blog frontmatter (the
  `.github/workflows/build_portfolio.yml` workflow). No manual step.

---

## Files this workflow added to the repo

```
.github/workflows/
  site-review-publish.yml          # tracking-issue lifecycle; no secrets

scripts/
  build_cliff.py                   # CSV-driven SVG renderer for cliff figure
  build_portfolio.py               # (extended) sparkline now per-week stems
  review/
    README.md                      # publish-pipeline operator notes
    issue-lifecycle.cjs            # Octokit lifecycle script

src/data/
  cms-ma-pd-stars-2025.csv         # cliff-figure canonical distribution data

critiques/
  critique-2026-05-23.md           # six-camp craft critique
  critique-2026-05-23-alignment.md # alignment companion

evaluations/
  hiring-eval-2026-05-23.md        # eight-evaluator hiring panel

reviews/
  README.md                        # this file
  2026-05-23-synthesis.md          # cross-report synthesis + checklist
```
