# AGENTS.md

Instructions for Claude Code (and other agents) working on this repository.

The authoritative project context lives in [CLAUDE.md](CLAUDE.md). This file
covers agent-style workflows that don't belong in the project constitution.

## Focus Group Agent

Simulates multi-round user feedback panels reviewing the portfolio. Each round
uses distinct personas who evaluate the content and visual hierarchy of
[index.html](index.html) (and, when relevant, [resume.md](src/content/resume.md)
and the latest entries in [src/content/blog/](src/content/blog/)).

### How to Run

When asked to run focus groups:

1. Read [index.html](index.html) end to end, plus any section the user flags for
   specific review. Skim recent blog posts if the round is about writing voice.
2. Simulate 3 rounds of panel feedback (typically 4 panelists per round).
3. Each panelist has a name, title, and specific perspective — hiring manager,
   peer, recruiter, UX reviewer, or a named archetype (e.g. "Director of
   Quality Analytics at a regional MA plan").
4. One round must include **antagonists** — senior practitioners in healthcare
   data engineering who pressure-test claims, specificity, and positioning.
   These panelists should be blunt and specific.
5. After all rounds, produce a synthesis table of actionable changes with
   consensus strength (unanimous / majority / single voice).
6. Propose (don't apply) concrete edits to [index.html](index.html) keyed to
   specific line ranges. Wait for approval before editing.

### Panel Composition Guidelines

- **Supportive round**: hiring managers, recruiters, peers offering
  constructive feedback.
- **Antagonist round**: senior practitioners in healthcare data engineering
  who challenge claims, question denominators, and identify positioning
  weaknesses.
- **Closing round**: balanced mix — potential direct hires, UX reviewers,
  junior peers who validate the narrative.

### What Panelists Evaluate

- Experience entry specificity and outcome language ("so what?").
- Claims that lack denominators or verifiable context (see CLAUDE.md §Stats
  table — defensible numbers only).
- Section ordering and visual hierarchy within the 640px column.
- Resume gaps or entries that raise questions.
- Narrative coherence across the career arc (note: the arc SVG is frozen per
  CLAUDE.md — feedback about it should target labels/prose, not coordinates).
- Technical credibility signals: measure names (Stars, HEDIS, ECDS), tool
  specificity, audit readiness.
- Publications and presentations: length and redundancy.
- Italic policy compliance (CLAUDE.md §Italic policy — italics reserved for
  pull quotes, testimonials, hero claim only).

### Constraints

- Do not propose changes that violate CLAUDE.md §What NOT to do (no frameworks,
  no JS beyond GoatCounter, no color scheme changes, etc.).
- Do not propose adding sections without discussion — the current section set
  is intentional.
- Treat the psql block, hero sequence, and name-appearance policy as locked
  unless the user explicitly opens them for revision.

### History

Historical focus group sessions from the Astro-era site (pre-rewrite) are
preserved in [archive/focus-groups-v1.md](archive/) if copied from the v1
archive repo. They are reference only — the content they critiqued no longer
exists in this codebase.
