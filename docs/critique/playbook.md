# Critique playbook

This is the prompt-as-document the critique pipeline runs. It is
designed to be executed by Claude Code (CLI locally, Claude Code
GitHub Action in CI) against a target file in this repo. No Python
script orchestrates this. The repo carries the methodology and the
playbook; Claude Code is the runtime. There is no `anthropic` SDK
import and no `ANTHROPIC_API_KEY` dependency in this repo's code or
workflows — see §Independence contract in `CLAUDE.md`.

## How to run it

### Locally

Open this repo in Claude Code. Say:

> Run `docs/critique/playbook.md` against `index.html`.

Substitute any other supported target (see §Supported targets below)
for `index.html`. Claude reads this playbook, reads
`docs/critique/methodology.md`, reads the target, and writes the
output to `critiques/critique-<target-slug>-<YYYY-MM-DD>.md`. No
network calls, no API keys; the engine is whatever Claude Code is
authenticated against on your machine.

### In CI

`.github/workflows/critique.yml` invokes the Claude Code GitHub
Action with this playbook as its prompt and the target as a workflow
input (`workflow_dispatch`) or the default (monthly schedule). The
Action authenticates via `CLAUDE_CODE_OAUTH_TOKEN`, not
`ANTHROPIC_API_KEY`. The output commit lands on the branch that
triggered the workflow.

---

## Supported targets

| Target glob                         | Archetype          | Slug rule                           |
| ----------------------------------- | ------------------ | ----------------------------------- |
| `index.html`                        | personal portfolio | `index`                             |
| `src/content/blog/<slug>.md`        | blog post          | `<slug>` (frontmatter slug)         |
| `src/content/resume.md`             | resume             | `resume`                            |
| `star-rating-predictor/index.html`  | subpage            | `star-rating-predictor`             |
| `life-in-weeks/index.html`          | subpage            | `life-in-weeks`                     |
| `epidemic-simulation/index.html`    | subpage            | `epidemic-simulation`               |

If the target is not on this list, ask the user to add it to the
list and to `docs/critique/methodology.md` §Archetype weightings
before running. Do not infer a new archetype on the fly; the
methodology doc is the canonical source.

---

## Steps

Execute these steps in order. Do not skip any step. Do not condense
the camp passes; six full critiques is the contract.

### 1. Resolve the run inputs

- Read the target path from the user's invocation. Verify it is on
  the §Supported targets list. If not, stop and ask the user to
  extend the list.
- Determine the archetype from the table above.
- Determine the slug from the table above.
- Determine today's date (`YYYY-MM-DD`).
- Compute the output path: `critiques/critique-<slug>-<YYYY-MM-DD>.md`.
- If a file already exists at that exact path, append `-iter2`,
  `-iter3`, etc. before the extension. Do not overwrite a prior
  same-day artifact.

### 2. Load context

- Read the full target file. Line numbers will be cited in the
  output, so retain them.
- Read `docs/critique/methodology.md` in full. Cite the archetype
  weighting table for the target's archetype.
- Read `CLAUDE.md` end to end. The §Design decisions/tokens — locked
  section and §What NOT to do section are the hard rails that the
  Locked-design-rule check (Conflict resolution rule 5) will
  reference.
- If the target is a blog post, read `blog.css` for shared styles.
- If the target is `index.html`, also read
  `archive/redesign/zaherkarp-tufte-rationale.md` if present, for
  the design rationale baseline.
- Do not read prior critique artifacts in `critiques/`. The point of
  each run is fresh-eyes analysis at the current state of the
  target; reading the prior run anchors findings to whatever the
  prior run flagged.

### 3. Write the file header

Open the output file and write:

```
# Critique of <target path>

Generated: <YYYY-MM-DD>
Archetype: <archetype>
Iterations: 1
Changes applied: no (APPLY_CHANGES=false)

> Methodological note: canonical archetype weighting applied per
> docs/critique/methodology.md §Archetype weightings (<archetype>).
> <If you had to deviate from the canonical weighting for any reason,
> state the deviation and the rationale here. Otherwise: "No deviations.">

---
```

### 4. Run each camp's critique pass

For each of the six camps, in the order they appear in
`docs/critique/methodology.md` §The six camps (Encoding rigorists,
Editorial clarity, Data humanists, System designers, Pipeline and
reproducibility, Access floor):

1. Write the `## Critique from <Camp name>` heading.
2. Write `### Voicing critics` and list the critics from the
   methodology doc verbatim.
3. Write `### What works on this page (your camp's lens only)` and
   list 1-2 things the target does well, each with a
   `(<element>, lines <a>-<b>)` citation. If the target genuinely
   does nothing well by this camp's lens, say so honestly in one
   bullet; do not pad. Stay strictly inside the camp's lens — do
   not borrow another camp's frame.
4. Write `### What needs to change (your camp's lens only)` and list
   findings as numbered items. Each finding starts with a bolded
   headline sentence, then a body with line citations, and ends with
   a `Fix:` prescription that is concrete enough to act on. Six to
   ten findings per camp is typical for a complex target like
   `index.html`; three to five is typical for a single blog post.
   Do not pad.
5. Write `### What other camps will say that you disagree with` and
   list 2-4 adjacent camps' likely positions with this camp's
   one-sentence rebuttals. Anticipate, don't fabricate.
6. Write `### Your camp's hill to die on`: a single paragraph
   identifying THE one finding the camp would not negotiate, with
   the reasoning for why it is foundational rather than contextual.
7. Write `---` to separate camps.

### 5. Run substantive conflicts and resolutions

After all six camps have spoken, identify cross-camp conflicts —
places where two or more camps prescribed conflicting fixes for the
same element. Two to five substantive conflicts is typical.

For each conflict, write:

```
### Conflict N: <one-line description>

- **Camps involved:** <list>
- **Contested element:** <element with line range>
- **<Camp A>'s prescription:** <one paragraph>
- **<Camp B>'s prescription:** <one paragraph>

**Resolution (rule applied: <rule name from methodology §Conflict
resolution>):** <paragraph>.
```

Apply the conflict-resolution rules from
`docs/critique/methodology.md` §Conflict resolution in order. Name
the specific rule that fired. Do not collapse disagreement into
consensus.

### 6. Write the prioritized changes section

Group the resolved findings into three confidence tiers, using the
definitions in `docs/critique/methodology.md` §Output structure.
Each item names the camps backing, the camps opposing, and the file
and line range to touch.

### 7. Flag anti-patterns

In a `## Anti-patterns flagged` section, name the coalitions or
sequencing risks the runtime detected. Examples:

- **Feature-creep coalition.** Adopting multiple "enrich the
  visualization" fixes from different camps in the same iteration
  produces multiplicative authoring complexity.
- **Strip-everything coalition.** Adopting every camp's "delete X"
  fix produces an editorially thin page.
- **Caption-rewrite-without-data-rework.** A caption fix that
  asserts a claim the chart cannot support, shipped without the
  paired structural fix — the integrity downgrade in Conflict
  rule 3.

If the run produced no anti-pattern risks, say so explicitly:
"No anti-pattern coalitions detected this iteration."

### 8. Recommend the next iteration

In a `## Recommended next iteration` section (single paragraph),
name the 3-5 changes the user should ship first, the predicted
downstream effect on the next critique pass, and any deferred
changes whose trigger condition is named.

### 9. Save and stop

Save the output file. Do not edit the target file. Do not commit
the artifact (CI commits; locally the user reviews and commits
manually). Report the output path to the user.

---

## What the playbook deliberately does not do

- **It does not apply fixes.** The contract is "Changes applied:
  no". Every finding is a prescription; the target file is read-only
  during a critique run.
- **It does not propose new sections, pages, or features.** Site-level
  structural proposals belong in the Focus Group / Design Council
  framework in `CLAUDE.md` §Agent panels, not in a critique.
- **It does not soften disagreement.** Substantive conflicts are
  recorded as conflicts and resolved per the methodology's rules,
  never compressed into "all camps generally agree that…"
- **It does not read prior critique artifacts before running.** Each
  run is fresh-eyes against the current state of the target.
- **It does not call out to the Anthropic API.** The runtime is
  Claude Code, billed against the user's subscription. The
  independence contract in `CLAUDE.md` §Critique pipeline forbids
  reintroducing an SDK import or an API-key dependency.

---

## When the playbook should be updated

- A new target type is supported (add to §Supported targets and to
  `docs/critique/methodology.md` §Archetype weightings together; do
  not split the change).
- The output structure changes (update §Output structure in
  `docs/critique/methodology.md` first; this file's §Steps mirror
  that contract).
- A conflict-resolution rule is added, removed, or reordered (update
  `docs/critique/methodology.md` §Conflict resolution and step 5
  here together).
- The independence contract changes (update `CLAUDE.md` §Critique
  pipeline, this playbook's "How to run it" section, and the
  workflow file together).
