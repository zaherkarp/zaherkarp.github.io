# Documentation sweep, 2026-08-07

A pass over the repo's prose and in-line comments, correcting statements that
had stopped being true. No behavior changed: every edit in this pass is a
comment, a docstring, or prose.

---

## 1. Why this was needed

Between 2026-07-26 and 2026-08-04 the homepage was restructured six times: the
Timeline Split, Direction B, the owner hero rewrite, three text-reduction
passes inside a single day, then the hero corner arc and the career-arc
annotation fix. Each pass updated `CLAUDE.md` and whichever function-level
docstrings it happened to touch. None of them swept the second ring: module
docstrings, workflow header comments, the `.md` playbooks beside the scripts,
`README.md`, `TODO.md`, the committed Design Council prompt, and roughly forty
in-file comments in `index.html`.

The failure mode is specific and worth naming, because it will recur. A pass
that moves a thing updates the comment attached to the thing it moved. It does
not update the comment two hundred lines away that merely *referred* to it, and
it does not update the playbook in another directory that tells you how to add
one. Those are the comments that go stale, and they are exactly the ones a
newcomer reads first.

Three shapes of harm showed up:

**Self-contradiction inside one file.** `build_portfolio.py` told you at line 15
that `homepageMarginnote` renders a margin note and at line 233 that it is no
longer rendered, with a test asserting the second. `index.html`'s Experience
banner described the first of the three 2026-07-30 sub-passes, which the second
sub-pass reversed hours later, so three of its claims were backwards.

**Comments that invite a regression.** `lint_recognition.py` and
`lint_gantt.py` parse `#service` and `#education` with raw-text regexes that
deliberately do not strip HTML comments, because both sections are
comment-disabled in `index.html`. Neither docstring said so. A maintainer
reading only the code sees a comment-blind regex, "fixes" it, and silently
voids a gate while CI stays green.

**Instructions that produce invisible work.** `docs/pipelines.md` told you to
add a new award to `<section id="service">` and a new certification to
`<section id="certifications">`. Both are inside HTML comments. The edit renders
nowhere, and every linter passes.

One finding came from arithmetic rather than reading: the hero corner arc's
offset comment had its direction inverted, and `CLAUDE.md` stated a third,
different value. See §3.

---

## 2. Scope

**In scope:** living documentation and in-line comments. `README.md`, `TODO.md`,
`llms.txt`, `colophon/index.html`, `docs/pipelines.md`,
`docs/streamlining-qa-plan.md`, `reviews/README.md`, `scripts/review/README.md`,
`scripts/review/prompts/design-council.md`, the `scripts/*.md` playbooks, Python
docstrings and comments under `scripts/`, workflow header comments, `CLAUDE.md`,
and the `index.html` comment layer.

**Deliberately out of scope:** the dated point-in-time records. Anything under
`critiques/`, `evaluations/`, and the dated files in `reviews/` and `docs/`
(`qa-audit-2026-07-28.md`, `homepage-*-2026-*.md`,
`experience-text-reduction-2026-07-30.md`, `backlog-review-2026-07-28.md`)
records what was true on its date. Correcting those would destroy the decision
record, which is the only thing they are for. They were used here as evidence,
never edited.

Also out of scope of the sweep itself, and recorded as recommendations in §6:
adding test coverage, and the `cv.html` sitemap defect. Three of those five
recommendations were acted on the following day, 2026-08-08, on owner request;
§6 marks which.

---

## 3. The hero corner arc, measured

The one finding that needed a browser rather than a reader. Section 22 of the
`index.html` style block sets `top: calc(var(--arc) * -0.30)` on `body::before`.
The comment said the centre was pushed "20% of the diameter ABOVE the page
top"; `CLAUDE.md` said 30% above. Measured in headless Chromium at 1400px:

| Quantity | Value |
| --- | --- |
| diameter (`width` = `height`, `aspect-ratio: 1`) | 644px |
| computed `top` | -193.2px, i.e. -0.30 x diameter |
| circle's **centre** | +128.8px, i.e. **+0.20 x diameter, BELOW the page top** |
| cropped above the page top | 193.2px, 30% of the diameter |
| visible vertical extent | 450.8px, 70% of the diameter |
| computed `right` | -322px = -0.5 x diameter, so the centre sits exactly on `body`'s right edge |

So all three sources disagreed: the code implements 20% below, the comment said
20% above, and `CLAUDE.md` said 30% above. The `top` multiplier (0.30, which
positions the top *edge*) and the resulting centre offset (0.20, in the opposite
direction) are different numbers, and collapsing them into one figure is what
produced the error twice. Both the comment and `CLAUDE.md` now state the
relationship rather than a single number, and say to read the computed values
back from the browser.

The existing parenthetical, that `-0.5` would put the centre exactly on the page
top and make the arc read as a pie slice, was correct throughout and is what
confirmed the sign convention.

---

## 4. What changed

23 files, comments and prose only. Grouped by the kind of error, since the
kinds recur more usefully than the file list does.

**Comments that would have caused a regression.** `lint_recognition.py` and
`lint_gantt.py` now say in their module docstrings and beside the regexes
themselves that `#service` and `#education` are HTML-comment-disabled, that the
raw-text slice reads through the comment deliberately, and that stripping
comments first would leave nothing to parse so the gate would pass vacuously.
`lint_gantt` also now records that the figure is the only visible surface left
for that content.

**Instructions that produced invisible work.** `docs/pipelines.md`'s cookbook
entries for adding an award and adding a certification now say where the
content actually renders, and that editing the commented-out section is still
correct for a future restore even though it shows nothing today.

**Self-contradictions.** `build_portfolio.py`'s module docstring no longer
claims `homepageMarginnote` renders; `index.html`'s Experience banner now
describes the second 2026-07-30 pass rather than the first one it reversed
(Huber formula back in a fold, one outcome figure not two, `sn-ehrs` dropped,
1,209 to ~570 words); the sidenote breakpoint reads 850px in all four places
rather than 760px in three of them; the mobile dot plot is described as the
stacked dots it draws rather than the bars it once drew.

**Counts and inventories.** Twelve linters in `README.md` now has twelve
bullets. `build_portfolio` writes six marked regions, not three or four. The
`writing-list` region holds two entries and `writing-index` holds six, stated
consistently. Corrected in passing: `.newthought` used four times not once, 12
toggles not 13, 105-unit dot-plot spacing not 115, 7 Gantt service entries not
9, 342-unit mobile width not 360, ~24px body type not ~21px, ~1,920 lines of
inline CSS not ~1,740 or ~2,570.

**The `updated` marker.** A real generated region rendering the footer date,
registered in `lint_markers.PAIR_MARKERS`, that appeared in no prose document
anywhere. Now documented in `README.md`, `docs/pipelines.md`, and
`build_portfolio.py`.

**CSS section numbering.** §21 (`MORE LINE`) was deleted on 2026-07-30 with
`.hero-more`, orphaning `21.1` under a parent that no longer existed and
leaving two comments pointing at a section that was gone. The breakpoints block
is renumbered `20.1`, and the two references corrected. 21 is deliberately left
unused rather than sliding §22 down, because §22 is cited by number from
several places.

**The Design Council's own briefing.** `scripts/review/prompts/design-council.md`
was two seated personas out of date, which mattered because every panel run
reads it. Val (motion) and Luke (mobile and touch) are added, with a new
Group E so the Val-vs-Alan and Luke-vs-Massimo tensions surface in Phase 2
rather than being resolved silently inside an existing pair. The 2026-07-28
joint-convening rule and the three-part synthesis order are added. Three
missing locked constraints are added, each of which was actively producing bad
proposals: the sanctioned full-width exceptions, the fact that there are now
two decorative marks rather than zero, and the site-wide removal of motion
gates on 2026-06-13.

**The committed-prompts confusion.** Four documents said some version of "the
prompts are not committed" while `scripts/review/prompts/` held two committed
panel prompts. All four now distinguish the two report prompts that are
committed from the four report prompts that are not.

**Done work still listed as pending.** `TODO.md`'s citation-count-history item
shipped as `data/snapshots/<date>.json`; its build-provenance item is complete
except for the commit SHA.

**Undocumented load-bearing mechanics, now commented.** The
`nav.top { width: 100% }` override that beats section 10 purely on source
order; the fractional `--seq:2.3` / `2.6` sub-beats that a renumber would
flatten; the no-JS contract's analytics carve-out.

### How this was verified

Every gate passed: the 12 linters, the 5 guard steps, and 145 tests.
`lint_gantt` still reports the sentence that proves the disabled sections are
still guarded: *12 section entry(ies) (5 education + 7 service) reconciled
against 12 figure mark(s)*.

Two checks were worth more than the gates, because the gates cannot see a
comment:

- **`index.html` with all HTML and CSS comments stripped and whitespace
  collapsed is byte-identical before and after** (97,863 bytes each). Whatever
  the comments now say, the browser reads the same bytes.
- **Rendered pixel-identical at 7 widths in both colour schemes**, 14 of 14.
  This took two tries and both failures were in the harness, not the page. A
  naive full-page screenshot is **not** reproducible on an unchanged tree at
  widths of 761px and above, because the scroll-driven figures
  (`animation-timeline: view()`) settle differently when the viewport is
  resized for the capture; the comparison only becomes meaningful with
  animations disabled via an injected stylesheet. And a "before" copy rendered
  from outside the repo root silently loses its relative font paths, so every
  shot differs for a reason that has nothing to do with the change. Prove the
  harness is stable on identical input before trusting a single red result from
  it.

The six changed Python files were additionally compared at the AST level with
docstrings stripped, and are identical. `scripts/hooks/pre-push`'s non-comment
lines are identical. The only executable-adjacent change in
`build_portfolio.yml` is a step `name:`.

---

## 5. Verified correct, do not re-flag

The audits checked a great deal more than they changed. The following all
looked like drift and are not. Recording them so the next audit does not spend
its budget here, and so nobody "corrects" a correct thing.

- **The pre-push hook and `.github/workflows/lint.yml` are genuinely in sync.**
  Both run the same 12 linters (blog, vocab, facts, notes, recognition, gantt,
  markers, skills, links, html, palette, ideas) and the same 5 guard steps (four
  greps plus the `sim.py` compile check). `scripts/tests/test_baseline_clean.py`
  carries a matching list. `lint_jobfit.py` is correctly excluded from all
  three: it is private, manual, and informational.
- **`README.md`'s "All 8 `<details>` folds".** Exact. A raw
  `grep -c '<details'` returns 13, but two are prose mentions inside comments
  and two more are inside the commented-out Education and Service blocks. The
  two quoted Experience fold summaries are verbatim correct.
- **The five career-arc band links**, the academic dot plot's position above the
  publication entries, the 760px horizontal-to-vertical SVG swap, and the nav
  order (writing / work / about / contact, each target strictly further down the
  page) were all confirmed against the markup.
- **`scripts/blog.md` §2b**, the mobile draft-edit section, is accurate against
  `blog_draft_edit_intake.py` and the issue template, including the publish
  checkbox, the retry-by-editing-the-issue behavior, and the draft-only refusal.
- **`build_og.py`'s docstring** correctly documents that it reads
  `src/content/palette.yaml` rather than inlining colors, and explains why. Its
  `SUBTITLE` comment correctly records the 2026-07-29 proposition change.
- **The colophon's "twelve linters"** (all six occurrences, including the SVG
  text) and its **"Five Python scripts"**. The latter is correct *as scoped*:
  `build_palette.py` is deliberately excluded and explained separately on the
  same page, and `build_jobsearch.py` is private. Do not "fix" it to six.
- **`docs/critique/methodology.md` and `docs/critique/playbook.md`.** No drift
  found. The supported-target lists correspond exactly, the referenced rationale
  file exists, and the independence contract they assert is genuinely enforced
  by the pre-push guard and `lint.yml`.
- **`scripts/review/README.md`'s triggers, check-items inputs, and file layout**
  match the workflows and the artifacts on disk exactly.
- **The Lighthouse pipeline entry** in `docs/pipelines.md`: six URLs and the
  `assertMatrix` with its negative lookahead, all as described.
- **`docs/pipelines.md`'s "Twelve pipelines"** and its CI / manual / external
  split. Arithmetic and assignments check out. Palette is deliberately not
  counted as a pipeline.
- **The colophon and blog navs carry more items than the homepage's four, by
  design.** `/#education` and `/#service` still resolve: the ids survive as
  relocated anchor spans beside the Gantt figure, kept deliberately because
  roughly 250 generated blog pages link to them, and `lint_links` cannot see
  blog-to-homepage fragments. This is the documented arrangement, not drift.
- **`llms.txt`'s job-title wording** ("Manager of Data Science & Engineering")
  does not match the canonical `<h3>` and JSON-LD form, but it exactly matches
  the homepage's own About margin note, and no linter reads `llms.txt`.
  Changing one without the other would make it worse.
- **`docs/streamlining-qa-plan.md`'s "8 gate linters + 4 grep guards"** under
  §1 Context. That is the pre-program baseline the rest of the document is
  measured against, not a live claim. Likewise "the 58-test suite" is a dated
  record of one pass.

---

## 6. Recommendations

Five items surfaced that were code rather than documentation, so the sweep
recorded them instead of acting. **Three were fixed the next day, 2026-08-08**,
on owner request; two remain open. The reasoning is kept rather than deleted,
because it is the record of why each existed.

### Resolved 2026-08-08

- **~~`lint_palette.py` has no test file.~~ FIXED.** It was the one gate linter
  of twelve with no test. `scripts/tests/test_lint_palette.py` now covers all
  three of its checks against a synthetic tree: drift, containment, and
  post-figure parity, each with a passing control beside it. Two traps are
  documented in its module docstring so the next reader does not rediscover
  them: `lint_palette` prints to **stdout** rather than stderr, unlike every
  other Layer-2 linter, and `ROOT = bp.ROOT` is an import-time alias, so
  aiming it at a synthetic tree means patching *both* modules' copies. The
  clean-repo pass case stays in `test_baseline_clean.py`, per the division
  `test_lint_html.py` documents.
- **~~The comment-disabled-section parsing has no test.~~ FIXED.** Both
  `test_lint_recognition.py` and `test_lint_gantt.py` now carry a
  `test_comment_disabled_section_still_parsed` and a
  `..._still_detects_drift` sibling, with fixtures that wrap the section in
  `<!--`/`-->` exactly as `index.html` does. **The paired negative is the
  point**: a lone "still returns 0" test would pass vacuously, so the drift
  case is what proves the entries were genuinely parsed and compared. Verified
  by inserting a comment-stripping line into both linters and watching exactly
  those four tests go red while the four live-section tests stayed green.
  Before this, the property was held only by the incidental empty-parse guards
  in each linter.

A third surfaced while checking a claim in the sweep brief itself, which was
wrong: `coerce_date()` is **not** re-exported from `_common` through `_ideas`.
`scripts/_ideas.py:266` carries its own copy, functionally identical to
`scripts/_common.py:78` (both lenient, both returning `None` on a bad value).
That matters because `_common.coerce_date`'s docstring says the lenient form is
"shared by the private job-search tooling" and that the build scripts
deliberately do not use it, and `docs/streamlining-qa-plan.md` §5.2 counts four
copies of publishDate coercion, resolving two into `_common` and listing the
other two (`build_blog.as_date`, `build_portfolio`'s strict parse) as
deliberately distinct in §5.4. The `_ideas` copy is a fifth, it is not private
job-search tooling, it has five consumers, and it appears in neither account.
Either it should import from `_common` or both docstrings should name it. Left
alone here: changing it is a code change.

- **~~`cv.html` is missing from `sitemap.xml`.~~ FIXED.** Surfaced while
  reconciling `llms.txt` against the live page set. `resume.html` was listed
  and `cv.html` was not, so a real page, linked three times from `index.html`
  and allowed by `robots.txt`, was invisible to sitemap-driven crawlers.
  Confirmed an oversight rather than a decision: `cv.html` entered the repo in
  the same commit that already had `resume.html` in the sitemap, and the string
  `cv.html` had never appeared in `build_blog.py`. The root cause is
  cross-pipeline ownership, `sitemap.xml` belongs to `build_blog.py` while
  `cv.html` belongs to `build_resume.py`, which never touches the sitemap.
  Now a hardcoded entry beside `resume.html`, pinned by
  `test_sitemap_includes_resume_and_cv`, and the adjacent `total_urls` counter
  was corrected from `2` to `4` (it already understated by one before this).

  **This paragraph originally said the fix was "a one-line change to
  `SUBPAGES`". That was wrong**, and acting on it would have produced an entry
  with no `<lastmod>`: `SUBPAGES` holds directory paths, and `_subpage_lastmod`
  resolves them as `ROOT / path / "index.html"`, which does not exist for a
  top-level `.html` file. That is exactly why `resume.html` was hardcoded in
  the first place. Corrected here rather than left to misdirect the next
  reader.

  `lint_links.py` still cannot catch a recurrence: it verifies that every
  sitemap entry resolves to a file, not that every real page appears in the
  sitemap, so that gate is green by construction. A general reverse check was
  considered and not written, because the canonical page set is genuinely
  ambiguous: `404.html` is deliberately excluded via `noindex`, and the PDFs
  are deliberately excluded in favour of their HTML twins. The targeted test is
  the guard instead.

### Still open

- **A duplicate `coerce_date`.** Surfaced while checking a claim in the sweep
  brief itself, which was wrong: `coerce_date()` is **not** re-exported from
  `_common` through `_ideas`.
`scripts/_ideas.py:266` carries its own copy, functionally identical to
`scripts/_common.py:78` (both lenient, both returning `None` on a bad value).
That matters because `_common.coerce_date`'s docstring says the lenient form is
"shared by the private job-search tooling" and that the build scripts
deliberately do not use it, and `docs/streamlining-qa-plan.md` §5.2 counts four
copies of publishDate coercion, resolving two into `_common` and listing the
other two (`build_blog.as_date`, `build_portfolio`'s strict parse) as
deliberately distinct in §5.4. The `_ideas` copy is a fifth, it is not private
job-search tooling, it has five consumers, and it appears in neither account.
Either it should import from `_common` or both docstrings should name it. Left
alone: changing it is a code change nobody has asked for.

- **The Certifications trailing rule** is a judgement call rather than a gap:
  it sits inside the disabled region, so restoring that section per its own
  instructions yields two adjacent rules. The comment's reasoning was corrected
  in this pass; moving the rule would be a rendering change and was not done.
