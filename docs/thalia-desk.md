# Thalia's desk

Continuity between sessions. A session reads this before touching a draft and
updates it before finishing. Persona, standards, and workflow rules live in
`CLAUDE.md` §Thalia; this file holds only what accumulates.

**What belongs here: exactly what cannot be recomputed.** Draft staleness, lint
status, `[CLAIM?]` counts, PR state, merge status and who is blocked are all one
command away from the repo, so recording them here creates a second copy that
goes stale and misleads. What is not derivable, and belongs here: observations
about the owner's voice, decisions he has ruled on, options already offered and
declined, and pushes already made so they are not made twice.

**Keep it short.** The sections below this header should total roughly sixty
lines; the header itself is fixed overhead and does not count. The PR letters
carry the detail, this is the index to them. When a line becomes computable, or
a decision is superseded, replace it rather than appending. A desk that only
grows is a graveyard, and a session reading a graveyard is worse off than one
reading nothing.

**On merge conflicts.** Reviews running in parallel each update this file on
their own branch, so two of them can collide here. Resolve by keeping both
entries: they are facts about different reviews, not competing versions of one.

## Voice, as observed

- He opens drafts with "This is the first of two articles on...". Both Stars
  drafts did. Cut it on sight. The published corpus never does this;
  `what-the-metric-cannot-see` opens in the room where every number on the slide
  is green and nobody quite believes care got better.
- **Headings mix noun phrases and assertions freely, and that is not a defect.**
  "Four hours to the wrong diagnosis" sits beside "Quality lives in the residual"
  in one published post. I planned a pass pushing headings toward assertions,
  read the corpus, and dropped it. The rule was mine, not his. Do not revive it.
- Published posts link every claim in place, DOIs and STAT and PMC and AMCP.
  Both Stars drafts park sourcing in an end note instead. The gap is real, but
  see the standing offer below before raising it again.
- When two sources disagree he names the disagreement and says which number he
  used: "The episode rendered the market revenue impact as 1.4 percent; Wakely's
  updated white paper states 1.2 percent, which is used here." That is
  §Calibrated claims running unprompted. Protect it in any trim.

## Decisions, with dates

- **2026-08-14, awaiting his ruling.** I cut the closing hedge from the sourcing
  note in both Stars drafts ("Any figure you intend to rely on should still be
  confirmed..."), as redundant with the sentence before it and as declining to
  stand behind his own numbers. Flagged in both letters as a register call,
  revertible in one line.
- **2026-08-14.** The two Stars parts disagreed on the eleven retiring measures.
  Fixed from Part 2's side only. Part 1's breakdown is the more precise of the
  two and stands untouched; do not reconcile from the other direction.
- **2026-08-14.** In the build-system post I changed an argument, not just a
  number: the concurrency section now tells the cron, why it failed, and the
  `workflow_run` edge that replaced it.
- **2026-08-14.** Frontmatter is left alone by default. The build-system post is
  the exception, because its description carried counts the body had corrected.

## Offered and declined, do not re-offer without a ruling

- **Inline citations for the Stars pair**, replacing the end notes. Offered, not
  implemented: the court opinion, the Groom Law Group and Crowell & Moring
  analyses, and the June CMS announcement cannot be verified from this repo, and
  inventing a citation URL is the one thing the claims rule forbids outright.
  His move, with the sources in front of him.
- Two alternative openings for Stars Part 2, built and rejected: the cut-point
  mechanics, which buries the news, and Loper Bright, which mismatches the voice.
- Bullets for Part 1's five-part playbook paragraph. Declined; the standards
  prefer prose in post bodies and the draft already agreed.

## Standing pushes, not yet taken up

- Both Stars posts bury their own thesis. Part 2 has "A Stars number without its
  rulebook version attached is not a forecast; it is a guess with a timestamp."
  Part 1 has "plans could once administer their way to four stars." Each is the
  argument in one line, sitting where a scanning reader misses it.
- No linter reads blog posts, which is how the build-system post drifted from
  the repo in seven places in three months. A thirteenth linter is an idea, not
  a decision.

## Resume prompt

Paste this to pick up in a fresh session:

> You are Thalia (`CLAUDE.md` §Thalia). Read `docs/thalia-desk.md`, then run
> `./scripts/blog queue` for the funnel and `git log --since="8 days ago"
> --name-only -- src/content/blog/` for what moved. Do not re-offer anything in
> the declined list. Pick up with:

## Last session

2026-08-15. Reviewed three drafts, opened their letters as PRs, and armed the
Monday nudge routine. Created this file.
