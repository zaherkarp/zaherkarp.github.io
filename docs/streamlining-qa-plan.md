# Streamlining + QA program

A plan for the toolchain behind the site, not the site itself. The build
pipelines and linters (see [pipelines.md](./pipelines.md)) are healthy and
do real work, but three things have accumulated cost. This document names
them, records what is being fixed **now**, and scopes the rest as staged
follow-up so nothing ships as a surprise.

Governing rule for the whole program: **streamlining must net-reduce the
maintenance surface, not add to it.** A consolidation that removes duplicate
copies earns its place automatically; a new QA gate only earns its place by
closing a QA hole that today relies on a human remembering to look. Every
phase below is measured against that.

This document is a proposal plus a record of the safe core. It does not
restate the locked design tokens or editorial rules — those live in
[CLAUDE.md](../CLAUDE.md) and are authoritative. Where a phase would reverse
or amend a documented decision, it lives in §Discussion-only and is **not**
scheduled work.

---

## 1. Context — why this exists

Three problems, all in the toolchain, none in the rendered site.

**(1) Duplication maintained in three parallel places.** The integrity suite
is 8 gate linters + 4 grep guards. The *list* of what runs is hand-maintained
in three files that must agree by hand:

- `scripts/hooks/pre-push` — the fast local echo.
- `.github/workflows/lint.yml` — the unconditional server-side backstop.
- `.github/workflows/build_blog.yml` — partially, the two pre-build lints
  (`lint_vocab`, `lint_blog`).

CLAUDE.md already codifies the no-drift contract ("a check added to the hook
belongs in `lint.yml` too, and vice versa"), but nothing *enforces* it. On
top of that, helper code is copy-pasted across the scripts themselves:
`line_of()`, `_field()`, `_section_body()`, HTML-entity `normalize()`,
`_esc()`, the draft/`_`-prefix post-skip loop, and `publishDate` coercion all
exist in two-to-six near-identical copies. `_common.py` even exposes an
alignment matcher explicitly extracted *from* two lints — which those two
lints then never adopted.

**(2) Zero automated tests.** ~6,500 lines of Python (build + lint scripts)
have no test suite. Every refactor is verified by eye or by running the whole
pipeline against the live repo and reading the diff. That is exactly the
footing on which the consolidation in problem (1) would be risky: there is no
behavior-preserving check to refactor against.

**(3) A human-eyeballs QA surface.** README §Before pushing lists a dozen
manual checks — anchor links resolve, figures render, HTML is balanced,
Lighthouse ≥ 90 — that no automated gate covers. Some of these are genuinely
mechanical (does every `#exp-*` link point at a real `id=`?) and are prime
candidates for a linter; a few are irreducibly visual (does dark mode look
right?) and should stay manual.

The goal is to shrink (1) and (3) without regressing the integrity guarantees,
using (2) as the safety net that makes the shrinking verifiable.

---

## 2. Principles / constraints

Any phase, shipped or deferred, must respect these. They are drawn from
CLAUDE.md and the pipeline design; none is negotiable inside this program.

| Constraint | What it forbids |
| --- | --- |
| **No linter weakening** | A linter that false-positives is fixed at the *content*, never softened. New gates hold the same line. |
| **Hook ↔ lint.yml no-drift** | Any check added to `pre-push` must also land in `lint.yml` (the unconditional backstop), and CLAUDE.md §Pre-push checks + README must document it. The three surfaces move together. |
| **Stoplists stay separate** | `lint_recognition` drops `"research"` as generic; `lint_gantt` must keep it so its abbreviated labels still match. Consolidation may share the *matcher functions* with the stoplist passed as a parameter, but must **not** merge the two `STOP` sets. |
| **No npm / node / JS build tooling** | Rules out any JS-ecosystem QA tool (linters, HTML validators, JS syntax checkers that need node). |
| **Preserve the redundancy-trailer + `GITHUB_TOKEN` anti-loop design** | The `Blog-CLI-Linted:` short-circuit and the `workflow_run` citation→CV edge are load-bearing. Do not "simplify" them away. |
| **`index.html` inline CSS stays inline** | ~2,570 lines of inline CSS is a deliberate first-paint decision; no extraction, and no QA gate that assumes an external stylesheet. |

Two structural notes that follow from the above:

- **`lint.yml` never consults the redundancy trailer.** It is the always-on
  gate. Any sync-checking idea (§Discussion-only) must keep that property.
- **Consolidation is behavior-preserving by definition.** Its acceptance
  test is "the new test suite still passes." That is why Track 1 ships first.

---

## 3. Track 1 — Test harness (DONE in this PR)

A pytest suite lands at `scripts/tests/`, run with `pytest scripts/tests/`.
Dev-only dependencies are pinned in `scripts/requirements-dev.in` /
`scripts/requirements-dev.txt` (separate from the runtime
`scripts/requirements.txt` so the site's build deps are unchanged). A new
`.github/workflows/tests.yml` runs the suite in CI.

These are **characterization tests**: they pin down current behavior so the
Track 3 consolidation can be shown to preserve it, not a specification of new
behavior. Coverage shipped:

| Area | What it exercises |
| --- | --- |
| Linters (all 8 gates) | Each linter is run in a **pass** case (against the real repo tree, which is clean) and a **violation** case (a fixture that should trip it), so both exit paths are pinned. |
| `build_blog` | Renders pages; the generated `sitemap.xml` and `blog/feed.xml` are asserted to be well-formed XML. |
| `build_portfolio` | Marker-injection idempotency: running twice against unchanged input is a no-op (the property the pipeline already claims). |
| `build_resume` | Skills-block regeneration from `skills.yaml`. The WeasyPrint PDF render **self-skips** when `libpango` is absent, so the suite runs green on a machine without the system libraries. |

What the suite is *not*: it is not a coverage target, not a spec for
untested edge cases, and not a substitute for the integrity linters (those
guard content; these guard the code that guards the content). It is the
scaffolding under the refactor.

---

## 4. Track 2 — CI/workflow tuning (DONE in this PR)

Four narrow fixes. Each is either a latent-bug fix or a cache-hygiene
tweak; none changes what any workflow *decides*.

| Fix | File | Why |
| --- | --- | --- |
| Add the 5-attempt rebase/retry push loop | `build_blog.yml` | A blog-source push fires both `build_blog.yml` and `build_portfolio.yml`, and both commit to `main`. `build_portfolio.yml` already rebases-and-retries on a lost race; `build_blog.yml` did a bare `git push` and could lose the same race on a new post. This gives it the loop its sibling already has. |
| Add a pip cache | `lighthouse.yml` | Its `setup-python` had no `cache: pip`, so every run reinstalled the full dependency set (including WeasyPrint's tree) from scratch. |
| Add `cache-dependency-path` | `build_portfolio.yml` | It sets `cache: pip` but no `cache-dependency-path`, so its cache key isn't pinned to `scripts/requirements.txt` the way the other workflows' keys are. Aligns it with `lint.yml` / `build_blog.yml`. |
| Remove the dead `ci_portfolio_lint` toggle | `scripts/blog.config.yaml` + `scripts/redundancy.py` `KNOWN_TOGGLES` | The toggle is declared in both places but consumed by **nothing** — no workflow or hook reads it. Removing it drops a phantom knob that implies a portfolio-lint short-circuit that does not exist. `prepush_lint` and `ci_blog_lint` (both real) stay. |

Explicitly out of scope for these fixes: the redundancy-trailer logic and the
`workflow_run` citation→CV edge are untouched (per §2).

---

## 5. Track 3 — Script consolidation (follow-up PR)

**Gate: do this only after the Track 1 suite is green**, so each change can be
shown to preserve behavior rather than argued to. The whole track is
behavior-neutral by intent; the tests are how that intent is verified.

### 5.1 Adopt the shared alignment matcher

`_common.py` already exposes `years_of` / `tokens_of` / `token_overlap` /
`alignment_match`, extracted *from* `lint_recognition.py` and `lint_gantt.py`
so a third lint could reuse them. Those two never adopted them and keep local
copies; `alignment_match` currently has **zero callers**. Adopt the shared
functions in both lints.

**Hard constraint (CLAUDE.md):** share the *matcher functions* with each
call site passing its own `STOP` set as a parameter — `tokens_of(s, stop,
...)` already takes `stop` as a required argument for exactly this reason. Do
**not** merge the two stoplists: `lint_recognition`'s `STOP` drops
`"research"`; `lint_gantt`'s must keep it.

### 5.2 Consolidate duplicated helpers

Into `_common.py` (or a second small shared module if `_common` gets
crowded):

| Helper | Copies today | Target |
| --- | --- | --- |
| `line_of()` | `lint_blog`, `lint_notes` (+ inline copies) | one shared |
| `.row-entry` regex parser + `_field()` | `lint_recognition`, `lint_gantt` (near-identical) | one shared |
| `_section_body()` | `lint_recognition`, `lint_gantt` | one shared |
| HTML-entity `normalize()` / decode | `lint_recognition`, `lint_gantt`, `lint_facts` | one shared |
| draft / `_`-prefix post-skip iteration | `lint_blog`, `lint_vocab`, `lint_notes`, `build_blog`, `build_portfolio`, `lint_jobfit` (6 copies) | one shared iterator |
| `_esc()` | `build_portfolio`, `_publications`, `_skills` (identical) | one shared |
| `publishDate` coercion | 4 copies | one shared |

### 5.3 Remove dead code

- `lint_blog.main()`'s redundant `_`-prefix skip (the file-collection step
  already excludes `_`-prefixed files).
- `lint_markers._scan_pairs()`'s always-empty second return value (`return
  tokens, set()` — the `completed_names` set is computed by `_check_structure`,
  not here).

### 5.4 Explicitly do NOT consolidate

Superficial similarity is not sufficient reason to merge; forcing these
together adds coupling for little gain.

- **The two markdown-it factories** in `build_blog` vs `build_resume`. They
  configure different options and are legitimately distinct.
- **The three resume role-header regexes** (`lint_facts` / `lint_jobfit` /
  `build_resume`) — leave alone **unless** a careful line-by-line check proves
  all three identical. If they differ in even one anchor or class name,
  merging them couples three surfaces that are allowed to evolve separately.

---

## 6. Track 4 — New QA gates (follow-up PR(s))

Each new gate closes a check that README §Before pushing currently asks a
human to perform. **Wiring requirement (the no-drift contract):** a new gate
must land in `pre-push` **and** `lint.yml` **and** CLAUDE.md §Pre-push checks
**and** README — in the same change. A gate wired into only some of these
reintroduces exactly the drift this program is trying to remove.

| Gate | What it checks | Notes |
| --- | --- | --- |
| `scripts/lint_links.py` | Internal href/anchor integrity: every `#exp-*` / `#pub-*` / nav anchor resolves to a real `id=` in `index.html` (~49 ids); homepage `/blog/<slug>/` links point at a built post directory; `sitemap.xml` `<loc>` entries resolve to real files. | Closes the "all internal anchor links resolve" eyeball check. |
| HTML well-formedness | Parse `index.html` and the generated `blog/` / `resume.html` / `cv.html` and fail on malformed structure. | **Recommendation: use `tinyhtml5`.** It is already in `requirements.txt` (transitively via WeasyPrint, so present in the `lint.yml` environment at no new dependency cost) and gives a real HTML5-spec parse. The stdlib `html.parser` subclass alternative (already used in README's balanced-tag smoke check) needs zero anything, but it is a lenient tokenizer, not a validating parser — it silently accepts much malformed nesting. Given `tinyhtml5` costs nothing extra here, prefer it for the stronger parse. |
| `python -m py_compile epidemic-simulation/sim.py` | Syntax-check the client-side Pyodide model that no build imports. | Today a syntax error there only surfaces in-browser. A one-line `py_compile` step (grep-guard shaped, not a new script) catches it at push time. |
| Marginnote inline-only rule | No block-level tags (`<p>`, `<ul>`, `<blockquote>`, `<div>`, …) inside a `marginnote` span. | **Add to the existing `lint_notes.py`**, not a new script. CLAUDE.md currently documents this as "check via grep by hand." |
| Extend `lighthouse.yml` | Also audit `/life-in-weeks/` and `/epidemic-simulation/`, and add their paths to the workflow triggers. | Both subpages have **zero** a11y coverage today. |
| Post-build sanity checks in the three build workflows | Run the generated-output guards (`lint_markers`, the `<p>`-wrapped-SVG grep) *after* the build inside `build_blog.yml` / `build_portfolio.yml` / `build_resume.yml`. | Cheap — the env is already installed there — and closes the bot-commit-lint seam (`lint.yml`'s weekly `schedule:` is the only thing that catches lint-violating *generated* output today). |

---

## 7. Discussion-only

Propose but do **not** schedule. Each item reverses or amends a documented
decision, or needs tooling the repo bans. Per the Working agreement, these
are flagged for a decision, not queued as work.

- **A certifications homepage↔CV linter.** The 2026-06-12 decision explicitly
  says keep that pair in sync **by hand**. Automating it *amends* that
  decision; it is not a straightforward gap-fill.
- **Flip Lighthouse `color-contrast` from warn → error.** A real tightening of
  the a11y bar, with the risk of blocking merges on borderline-but-shipped
  contrast; a taste call for Haben (WCAG) + Alan (perf/CI).
- **Switch CI from committing generated artifacts to a `gh-pages` /
  `deploy-pages` flow.** This would unwind the entire commit-back-to-`main`
  model (and the `workflow_run` edge, the rebase/retry loops) that the current
  design is built around. Large blast radius; a separate discussion.
- **JS syntax checking for the inline-JS subpages** (`star-rating-predictor/`,
  `life-in-weeks/`, `epidemic-simulation/` app glue). Needs node tooling,
  which §2 forbids. No in-repo path today.
- **A unified single check-runner** replacing both the `pre-push` body and the
  `lint.yml` steps. Weigh against the per-step CI-UI value (each linter is its
  own named, independently-readable CI step today). A lighter alternative: a
  tiny **sync-checker** that merely asserts the hook and `lint.yml` reference
  the same check list — enforcing the no-drift contract without collapsing the
  two runners. Presented as an open question, **not** a recommendation.

---

## 8. Net maintenance-surface accounting

The program is held to §Context's rule: net-reduce or hold the hand-maintained
surface. Honest tally by track.

**Track 3 (consolidation) removes surface.** Roughly:

- ~15+ duplicate helper copies collapse to one each (line 5.2 table: 2 + 2 + 2
  + 3 + 6 + 3 + 4 copies → 7 shared definitions), plus two local copies of the
  alignment machinery in 5.1 give way to the already-written shared functions
  (and retire `alignment_match`'s zero-caller status).
- Two dead-code fragments (5.3) go entirely.

This is pure subtraction: every copy removed is one fewer place a fix has to
be applied in lockstep.

**Track 4 (new gates) adds a little surface, deliberately.** Of the six gates,
most add *no new script*: the marginnote rule folds into `lint_notes`, the
`py_compile` and post-build checks are grep-guard-shaped steps, and the
Lighthouse change edits an existing workflow. The genuinely new script is
`lint_links.py` (≈1), and the HTML well-formedness check is either a second
small script or a step (≈0–1). So Track 4 adds **~1–2 scripts**, each wired
into all three no-drift surfaces.

**Track 1 (tests) is additive by nature** — a test suite is new code — but it
is the safety net that makes Track 3's subtraction verifiable rather than
risky. It buys down the risk of the very refactor that shrinks the surface.

**Net direction: the hand-maintained *duplication* surface shrinks; the QA
*coverage* surface grows by a small, earned amount.** Each new gate has to
name the README §Before pushing eyeball check it retires; a gate that doesn't
close a real human step doesn't ship. The program nets toward less to
maintain, not more — which is the only condition under which it is worth
doing.
