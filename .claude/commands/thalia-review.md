---
description: Thalia's full review of one draft post, edits on a branch, PR as editorial letter
argument-hint: <draft path or slug>
disable-model-invocation: true
---

Run Thalia's full review (persona and standards in `CLAUDE.md` §Thalia) on the
draft identified by: $ARGUMENTS

Work the passes in order. Commit after each pass that changed something, using
the labeled message format from §Thalia (`opening: replace announcement with
checkout scene`, `claims: mark two unverified prices`). A pass that changes
nothing gets no commit and is reported in the letter instead.

**1. Locate.** Resolve `$ARGUMENTS` to exactly one file under
`src/content/blog/`. Accept a slug, a filename, or a path. If zero or several
candidates match, list them and stop. Confirm the post carries `draft: true`:
this command reviews drafts, and a published post is a different conversation
with the owner. If the draft has no row in `src/content/blog-ideas.yaml`,
register it with `./scripts/blog idea adopt <slug>` before editing, so the
funnel does not lose sight of it.

**2. Calibrate.** Read `docs/thalia-desk.md` first. It carries what earlier
sessions learned about the owner's voice, the decisions he has ruled on, and the
options already offered and declined; re-offering something on that list is the
fastest way to sound like a stranger who has never read him. Then read the draft
in full, then the three most recent published posts in `src/content/blog/`
(newest `publishDate` with `draft` false or absent) for voice. No edits in this
pass.

**3. Branch.** `git fetch origin main`, then create `muse/<slug>-review` off
`origin/main`. Never work on the default branch. If the session imposes its own
designated branch, use that one and say so in the editorial letter.

**4. Muse pass.** Generate two or three pushes: alternative openings, angle
inversions, structural reframes, the image the draft implies but never lands.
Implement the strongest one directly in the draft. Record all of them, the
rejected ones included, for the letter. Every riff terminates as a concrete
edit or a concrete written option, never as vibes.

**5. Structure pass.** Reorder, cut, and tighten at the paragraph level until
the argument survives a skeptical reread.

**6. Line pass.** Sentence-level edits enforcing every editorial standard in
§Thalia. Flag any passive that hides the actor. Cut rhetorical setup sentences
and rhetorical questions. No em dashes in prose you write or rewrite; leave the
author's existing em dashes alone unless you are already rewriting that
sentence, since post sources keep their historical voice.

**7. Claims pass.** Check every number, date, name, and technical claim against
the draft's own sources and the repo. Mark anything unverifiable with an inline
plain-text `[CLAIM?]` next to the claim and collect the list. Plain text, never
an HTML comment: `lint_blog` fails on HTML comments the moment the post stops
being a draft, and a comment marker would ship invisibly. Never silently fix a
fact. The post stays `draft: true` while any marker remains.

**8. Verify.** Run, from the repo root with the project venv active:

```bash
./scripts/blog lint <slug>       # lint_blog + lint_vocab, scoped to the post
./scripts/blog preview <slug>    # renders to a tempfile, opens a browser
```

A pass is a clean lint plus a rendered preview; report the tempfile path the
preview prints. In a headless session the browser will not open, and the
written file is the check. KaTeX, Mermaid, and Prism load from a CDN and are
absent from preview, so judge math, diagrams, and fenced code by their markup
here. Never run `scripts/build_blog.py` to check a draft: drafts are excluded
from the build by design, and a container run rewrites every generated page
with a wrong footer and wrong `lastmod` values. See CLAUDE.md §Blog pipeline.

**9. Update the desk.** Add to `docs/thalia-desk.md` only what a later session
cannot recompute: a voice observation this draft earned, a decision made or
awaiting his ruling with the date, an editorial option offered and declined so
it is not offered twice. Keep two things off the desk because something else
already holds them. Recomputable state stays off (`[CLAIM?]` counts, lint
results, staleness, PR state); it is one command from the repo and a stale copy
misleads. And a pitched post idea's fate stays off: it lives in the ledger as a
row or a `dropped` status (§Blog idea backlog), which the nudge already reads.
If the review leaves owner-only work behind, record the outstanding decision
that keeps the draft unshipped, not the fact behind it, so the Monday nudge's
one ask and the next review agree on what is unshipped and why. Replace
superseded lines rather than appending, and hold the sections below the file's
header to roughly sixty lines between them.
Commit it on its own, `desk: <what you learned>`, so it reads apart from the
draft edits. A review that learned nothing new adds nothing here, which is a
normal outcome and not a gap to fill.

**10. Deliver.** Push the branch and open a ready PR whose description is the
editorial letter: what changed and why, options offered but not implemented,
what you declined to touch and why, the full `[CLAIM?]` list, and one closing
muse push for the next revision. Report the preview route from pass 8.
Publishing is not part of a review; it stays the owner's call via
`./scripts/blog publish <slug>`, which flips the draft flag and moves the
ledger row in one commit.

**Scope guard.** Only the draft under review, the assets it requires, and
`docs/thalia-desk.md`, which pass 9 is the single sanctioned exception for.
Never the default branch, never generated output under `blog/`, never a
build-marker region, never another post.
