# Cross-surface fact lint — playbook

`scripts/lint_facts.py` enforces consistency between the three surfaces
that name the same employment facts:

- `src/content/resume.md` — the canonical Markdown source
- `index.html` — visible chrome (`<h3>` + `<p class="meta">` blocks)
- `index.html` — embedded JSON-LD (`<script type="application/ld+json">`)

When you update one surface but not the others, this lint catches the
divergence at pre-push time and in CI. It runs as part of the pre-push
hook installed by `scripts/_common.install_git_hooks()`.

## What it checks

Three assertions, all phrased as invariants the surfaces should hold:

1. **Current role agreement.** The newest entry on resume.md (the one
   with `Present` as its end date) must match the first job block on
   the homepage and must match the JSON-LD `jobTitle` and
   `worksFor.name`. Compared fields: organization, title, start date.

2. **Resume orgs ⊆ homepage orgs.** Every employer named on the
   resume must also appear on the homepage. The homepage may list
   more entries (it splits Healthfinch / Health Catalyst at the
   2020 acquisition while the resume condenses), but every resume
   org must have a homepage counterpart.

3. **Exactly one current role per surface.** Each of resume.md and
   index.html should have exactly one entry with `Present` as the
   end date. Two-current usually means a stale edit; zero-current
   means a missing one.

## How it works

### Parsing

The linter does not maintain a separate canonical store (no YAML
fact-spine, no schema). It parses the existing surfaces directly:

- **resume.md** — regex on `**Org** | Title\nDate – Date` blocks.
  Org may contain a parenthetical (stripped before comparison);
  title may contain a parenthetical (also stripped). The first
  block under `## Experience` is treated as the current role.

- **index.html h3+meta** — regex on `<h3>...</h3>` followed
  (within a small window, no intervening `<h3>`) by
  `<p class="meta">Org · Date to Date</p>`. Inline label/input
  chrome inside the h3 (margin-note toggles) is stripped before
  comparison.

- **index.html JSON-LD** — JSON parse of the
  `<script type="application/ld+json">` block. Reads `jobTitle`
  and `worksFor.name`.

### Normalization

For comparison, organization names are:

1. Stripped of `(...)` parentheticals
2. Truncated at the first comma (department names on the homepage
   don't break the match)
3. Lowercased

Titles are stripped of parentheticals only — no synonym dictionary,
no fuzzy matching. If the resume says `Analytics Manager` and the
homepage says `Healthcare Analytics Manager`, the linter fails. That
is intentional: drift detection is the whole point, and "fix it on
whichever surface you want to change" is the right response.

### Why no synonym table

Synonym tables grow without bound and become a maintenance tax of
their own. By keeping comparison strict, the linter has zero false
negatives: when surfaces disagree, you find out. The cost is the
occasional false positive on a deliberate phrasing difference; the
fix is a few seconds of editing.

## Failure playbook

When a pre-push fails with `Cross-surface fact lint found drift`,
read the violation list and find the matching section below. Each
section has the same six-part shape: symptom, why, triage, fix,
verify, false positives.

---

### A. current employer mismatch

**Symptom.**

```
current employer mismatch: resume.md:11 says 'Baltimore Health Analytics',
index.html:1632 says 'BHA Inc.'. Playbook: §A.
```

**Why this check exists.** The current employer name appears in three
places: resume.md, the visible homepage h3+meta, and the JSON-LD
`worksFor.name` consumed by search engines and LLM summarizers. Drift
between them produces a recruiter's worst impression: "your site says
one thing, your resume says another."

**Triage.**

```bash
grep -n "Baltimore Health" src/content/resume.md
grep -nE 'class="meta"' index.html | head
grep -nA 4 'worksFor' index.html
```

**Fix.** Pick the canonical name, update the two surfaces that don't
match.

- Resume.md: edit the role header line `**Org** | Title`.
- Homepage chrome: edit the relevant `<p class="meta">` line.
- JSON-LD: edit `worksFor.name` in the
  `<script type="application/ld+json">` block (near the top of
  index.html).

The career-arc SVG also references employer names in `<text>`
elements (around lines 1080–1230). The fact lint does NOT check
those, but if the visible h3 changes, the SVG label probably should
too. Eyeball both render modes after the edit.

**Verify.**

```bash
python scripts/lint_facts.py
```

**False positives.** If you're mid-rebrand (employer changed names),
both old and new will appear in transition. Pick a switchover date,
do the edit on all three surfaces in one commit.

---

### B. current title mismatch

**Symptom.**

```
current title mismatch: resume.md:11 says 'Manager of Data Science & Engineering',
index.html:1630 says 'Manager, Data Science'. Playbook: §B.
```

**Why this check exists.** Promotions and title changes are the most
common silent drift. They typically land in one surface (the one you
were editing at the time) and not the others. The JSON-LD `jobTitle`
is invisible in the browser but consumed by structured-data crawlers;
it tends to be the most stale of the three.

**Triage.**

```bash
grep -nE '^\*\*' src/content/resume.md         # all role headers
grep -nE '<h3>' index.html | head -20          # h3 entries (jobs + projects)
grep -nE 'jobTitle' index.html                 # JSON-LD
```

The first homepage `<h3>` whose next-sibling `<p class="meta">` ends
in `Present` is the current job. The first resume role under
`## Experience` is the current role.

**Fix.** Pick the canonical title (the resume version is usually the
most considered, since you write it for an external audience). Update
the homepage h3 *and* the JSON-LD `jobTitle`. If the homepage's
margin note reflects a sub-component of the title (e.g., "promoted
from X in YYYY"), keep the parenthetical out of the h3 itself.

**Verify.** `python scripts/lint_facts.py`

**False positives.** If your homepage uses a richer title for prose
reasons (e.g., `Healthcare Analytics Manager, Embedded Refills and
Care Gaps`) and the resume uses a shorter form (`Analytics Manager`),
the linter will fail and you'll have to choose. The right answer is
usually to bring them into agreement on the *short* form, since
resumes are scanned, and to surface the long form via a homepage
margin note or fold.

---

### C. current start date mismatch

**Symptom.**

```
current start date mismatch: resume.md:11 says 'Nov 2025',
index.html:1632 says 'Apr 2026'. Playbook: §C.
```

**Why this check exists.** The start date answers "how long have you
been there?" — used by recruiters to size tenure and by you to size
your own narrative. Drift here usually means one surface was updated
to reflect a promotion (start of new title) while the other reflects
start of employment with the org. Pick a convention and apply it
consistently.

**Triage.** Decide which start date you mean.

- **Start at employer** — the date you joined the org, regardless of
  title changes inside it.
- **Start in current role** — the date your current title began, even
  if you joined the org earlier in a different role.

The site's convention is **start at employer**: promotions are
recorded as homepage margin notes (`Promoted from X in MM YYYY`)
rather than as new entries. This matches what most resumes do and
avoids fragmenting a single tenure into multiple short stints.

**Fix.** Update the surface that disagrees with the convention. If
the homepage shows the promotion date and the resume shows the join
date, the homepage is wrong (per convention); change the homepage's
`<p class="meta">` start to the join date and let the margin note
carry the promotion timing.

**Verify.** `python scripts/lint_facts.py`

**False positives.** If you genuinely want to record a promotion as
a separate role (rare for short tenures, common for very long ones),
restructure the resume to have two entries for the same employer.
Order them newest-first; the newer entry's `Present` end date is
what the linter reads as the current role.

---

### D. JSON-LD drift

**Symptom.**

```
JSON-LD jobTitle='Lead Data Engineer' does not match resume current
title 'Manager of Data Science & Engineering'. Playbook: §D.
```

(Or the same shape for `worksFor.name`.)

**Why this check exists.** JSON-LD is invisible in the browser, so it
silently goes stale on every other update. Search engines, LLM-based
summarizers, and rich-snippet pipelines read it as authoritative, so
stale JSON-LD spreads outdated facts to surfaces you don't control.

**Triage.**

```bash
grep -nA 30 'application/ld+json' index.html
```

You'll see a JSON object near the top of the file. The fields that
matter for this check are `jobTitle` and `worksFor.name`.

**Fix.** Edit the JSON-LD block in index.html to mirror the resume's
current role. Keep the JSON syntactically valid (commas, quotes).

**Verify.** `python scripts/lint_facts.py` — and, if you want a
syntactic sanity check on the JSON itself:

```bash
python -c "import json,re; m=re.search(r'<script type=\"application/ld\+json\">(.*?)</script>', open('index.html').read(), re.DOTALL); json.loads(m.group(1)); print('json ok')"
```

**False positives.** None expected. JSON-LD has no rendering nuance
to argue with.

---

### E. resume employer not on homepage

**Symptom.**

```
resume.md:21: employer 'sustainable clarity' on resume but not on
homepage (homepage has: ['baltimore health analytics', 'health catalyst',
'healthfinch', 'university of wisconsin-madison']). Playbook: §E.
```

**Why this check exists.** Resume.md condenses your story; the
homepage tells the longer version. If a resume entry has no homepage
counterpart, either the resume is leaning on a job the site has
forgotten, or the site has dropped a meaningful chapter.

**Triage.** Search the homepage for any mention of the missing
employer.

```bash
grep -in "sustainable clarity" index.html
```

- **Match found in prose, not in an h3+meta block.** The employer
  is mentioned but not as a structured experience entry. Decide if
  it deserves promotion to an h3 entry (and add one) or removal
  from the resume.
- **No match.** The site has nothing about this employer. Add a
  homepage entry (h3 + `<p class="meta">`) or drop the resume entry.

**Fix.** Most often: add an `<h3>...</h3>` + `<p class="meta">...</p>`
block to the homepage Experience section for the missing employer.
Match the existing block formatting (org name, middle dot, date
range with `to` connector and `Present` end where applicable).

**Verify.** `python scripts/lint_facts.py`

**False positives.** If the resume names a non-employer (a fellowship,
a freelance period, a sabbatical) that you want on the resume but
not on the homepage, the linter will complain. Two options:

- Add a corresponding homepage entry (often the right answer), or
- Move the resume entry under a non-`## Experience` section
  (`## Awards`, `## Affiliations`) so the parser ignores it. The
  parser only matches `**Org** | Title` blocks; section headings
  are not considered.

---

### F. multiple-current-role drift

**Symptom.**

```
resume.md: expected exactly 1 'Present' role, found 2: ['Baltimore
Health Analytics', 'Some Other Org']. Playbook: §F.
```

Or, less commonly:

```
resume.md:11: first role end='Aug 2025' (expected 'Present'); newest
role must come first. Playbook: §F.
```

**Why this check exists.** A resume that lists two current jobs
without explicitly framing them as concurrent is usually a stale
edit (a previous job's end date wasn't filled in). The same goes
for the homepage. The "newest first" version of this check protects
against ordering drift — if the most recent role isn't at the top,
the rest of the lint trusts the wrong row.

**Triage.** Find every entry whose end date is `Present`.

```bash
grep -nE '–\s*Present' src/content/resume.md
grep -nE 'to Present</p>' index.html
```

**Fix.**

- For the role that ended, replace `Present` with the actual end
  date (`MMM YYYY`).
- For the role that's current, keep `Present`.
- Reorder the resume so the current role is first under
  `## Experience`. Reorder the homepage Experience h3 blocks
  accordingly.

**Verify.** `python scripts/lint_facts.py`

**False positives.** If you genuinely hold two roles concurrently
(advisory, board work, side employment), the linter as written will
not let that pass. Two options:

- Move the secondary role to a non-`## Experience` section on the
  resume and use a different homepage marker so the parser doesn't
  pick it up.
- Loosen the assertion (allow `>=1` current). Edit
  `check_single_present` in `scripts/lint_facts.py` and document
  your reason in this playbook.

---

### G. parser failure (no jobs found)

**Symptom.**

```
resume.md: no jobs parsed; check format (**Org** | Title / Date – Date).
Playbook: §G.
```

or

```
index.html: no jobs parsed; check <h3>...</h3> + <p class="meta">...</p>
structure. Playbook: §G.
```

**Why this check exists.** A regex change (intentional or accidental,
in the source files or in the linter itself) can render the parser
blind. Failing loudly when zero jobs are parsed prevents a false
"lint clean" pass on a totally broken file.

**Triage.** Look at the structure of the file the parser couldn't
read. Most common causes:

- **Resume.** Role header on a single line instead of three (org,
  title, and date got merged); date connector changed from en-dash
  (`–`) to something else; org wrapped in something other than
  `**...**`.
- **Homepage.** `<p class="meta">` replaced by `<p>` (class lost
  during an edit); date connector in the meta line changed from
  `to` to something else; the middle-dot separator (`·`) replaced
  with something else.

**Fix.** Restore the format the parser expects — see the
**How it works → Parsing** section above. If you changed the format
deliberately for editorial reasons, update the regex in
`scripts/lint_facts.py` and add a one-line note here in the
playbook explaining what changed.

**Verify.** `python scripts/lint_facts.py` should report job counts
on success:

```
facts lint: 3 resume role(s) + 4 homepage job block(s) consistent
```

If the count is lower than expected (e.g., 2 resume roles when you
have 3), the parser is partially blind and a single role is being
skipped. Check the format of the role that disappeared.

---

## Bypassing the check

If you absolutely must push without passing this lint (e.g., a
scheduled deploy unrelated to content):

```bash
git push --no-verify
```

CI still runs the check, so the next push that *isn't* skipped will
re-fail with the same drift. Treat `--no-verify` as a "not now,"
not a "never."

## Adding a new check

Two cases.

1. **A new fact you want to enforce.** Add a parser, a check
   function, and a new section to this playbook with the same
   six-part shape (symptom, why, triage, fix, verify, false
   positives). Resist adding a synonym dictionary — keep
   comparison strict.

2. **A new surface (e.g., a future CV PDF source).** Add a parser
   function that returns `list[Job]` and run the existing checks
   against it as well. The pattern is `parse_<surface>(text) ->
   list[Job]`. Update this document to list the new surface in
   the opening summary.

## When the linter is wrong

If you're certain the data is correct and the linter is producing a
false positive that the existing False-positives notes don't cover,
change the linter rather than the data. Bias toward making the
parser smarter, not adding synonym escape hatches. Update this
playbook in the same commit so the next person who hits the same
case doesn't relearn it.

## Known gaps

The fact lint is deliberately scoped to the most-leveraged
invariants. Things it does NOT check today:

- Career-arc SVG `<text>` labels in index.html (lines ~1080–1230
  for desktop, ~1180–1240 for mobile). Employer name changes here
  must be made by hand.
- Education entries (degree, institution, year). The homepage
  references education in chart annotations and a stat figure
  rather than a structured list, so cross-surface comparison is
  fragile. A future check could match on `(degree, institution,
  year)` triples if the homepage adopts a structured education
  section.
- Skills, methods, BI tools listed on the resume vs the
  experience-entry stack lines on the homepage. These overlap
  semantically but rarely in exact wording.
- Publications listed on the resume vs the publications section
  on the homepage. The homepage carries `data-sid` attributes for
  citation lookups; a future check could verify the resume's
  publication list aligns with those entries by year and venue.

When an unchecked drift causes pain, promote it to a check. Don't
add synonym dictionaries to paper over it.
