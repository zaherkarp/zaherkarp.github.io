---
title: "Sunomata Castle and the One-Night Deliverable"
description: "Hideyoshi prefabricated Sunomata upstream and assembled it overnight to establish a forward position, not the finished fortress. The same logic applies to early client deliverables: assemble from open-source clinical groupings (ICD, SNOMED, LOINC, HEDIS) to hold a position long enough to learn what framing actually lands."
publishDate: 2025-10-30
tags: ["consulting", "stakeholder-engagement", "clinical-terminology", "healthcare-data", "client-work"]
---

In the mid-1560s, Toyotomi Hideyoshi solved a problem that had stalled his lord's campaign for years.

Nobunaga needed a forward castle on the far bank of a river, close enough to pressure the enemy position at Inabayama. Previous attempts had failed. The terrain was hostile, the supply lines were exposed, and any construction effort was visible and vulnerable from the moment it started.

Hideyoshi's answer was to not build it there. He prefabricated the components upstream, floated them down by night, and assembled the structure in a single session. By morning, there was a castle. It held. The campaign moved forward.

The part that gets left out of the retelling: the castle wasn't the finished fortress. It was a forward base. Its job was to establish a position, survive long enough to matter, and create the conditions for what came next. It was built to the spec the moment required, not the spec the final objective would eventually require.

That distinction is the useful one.

## The failure mode in client work

The recurring mistake in early-stage stakeholder engagement is treating the first deliverable like it needs to be the finished product. It doesn't. It needs to hold a position long enough for you to learn what framing actually lands.

When you over-engineer before you know what the client needs to believe, you build to the wrong spec. A polished deliverable built around the wrong framing costs more to revise than a rough one, because the sunk effort creates pressure to defend the framing rather than replace it. You find yourself explaining a structure that isn't clicking instead of finding the one that would.

The Hideyoshi move is to identify what can be prefabricated, what already exists in a form the moment can use, and assemble it quickly enough that you get the feedback before you've committed too much.

## Open source groupings as prefab components

There is a recurring pattern in health data work that maps almost directly to this.

Most clinical domains have established, openly published terminologies and groupings: ICD code sets, SNOMED hierarchies, LOINC panels, HEDIS measure specifications, CMS quality measure frameworks. These exist, they are documented, and in many cases the client organization already has some relationship with them, even if informal. A quality team knows what a HEDIS measure is. A clinical informatics team has probably argued about SNOMED. A product team building around chronic condition management has almost certainly encountered ICD groupers.

The pattern is to find which of these groupings intersects with the problem the client is trying to articulate, pull the relevant slice, and use it as the initial scaffolding for a short-term value demonstration. You are not inventing a framework. You are assembling components that already carry institutional legitimacy, and you are testing which ones the client already trusts.

This is low-footprint for several reasons. The components are reusable across engagements. The vocabulary is not yours, so you are not asking the client to adopt your terminology, you are meeting them inside terminology they have some prior relationship with. And the assembly is fast, because you are not building from raw material.

What you learn quickly: which grouping resonates, which level of granularity the client actually thinks in, and where their internal disagreements are. A client who lights up at a HEDIS-framed analysis and goes quiet at a raw SNOMED hierarchy is telling you something about how they are organized internally and what their existing reporting infrastructure looks like. You could not have learned that from a requirements document.

## What holds the position

The castle at Sunomata held not because it was impressive but because it was sufficient. It established a forward position. It changed what was possible next.

A short-term deliverable built from open source groupings holds a position the same way. It demonstrates that you understand the domain well enough to navigate it. It gives the client something to react to, which is more generative than something to approve. It surfaces the real constraints early, before you have committed to a full build. And because the components are reusable, the cost of reassembling around a different framing is low.

The failure mode it prevents is the one where you spend weeks building a bespoke framework for a problem the client was not quite asking, and then spend additional weeks explaining why the framework is right rather than finding out what they actually need.

## Done enough

There is a version of "low-footprint" that is just underprepared. That is not the argument here.

Hideyoshi's castle required real engineering. The prefabrication was precise. The logistics of moving components downstream at night were not simple. The one-night assembly worked because the preparation was serious.

The same holds for open source groupings. Knowing which ICD codes belong to which chronic condition cluster, understanding how HEDIS denominator logic works, being able to explain what a LOINC panel does and does not include: that is real domain knowledge. The point is not to skip the preparation. The point is to prepare in ways that are reusable and to build to the spec the moment requires rather than the spec you imagine the final objective will eventually require.

The castle held. That was the spec. Figure out what "held" means for the meeting you are actually in, build to that, and let what comes next tell you what to build next.
