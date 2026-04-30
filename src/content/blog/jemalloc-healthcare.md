---
title: "jemalloc and the Healthcare Allocation Pattern"
description: "Healthcare data systems have allocation patterns that punish general-purpose allocators. jemalloc's arena isolation, thread-local caches, and size-class slabs map directly to HEDIS pipelines, claims adjudication, and variable-width ETL."
publishDate: 2026-04-30
tags: ["systems", "memory-allocation", "jemalloc", "healthcare-data-engineering", "performance"]
---

I spent a weekend writing a particle visualizer for jemalloc[^jemalloc], not because the docs are inadequate, but because watching the allocator behave under load is a different kind of understanding than reading about it. The project, jemallocviz, became a teaching tool I now reach for when explaining why memory pressure in healthcare data systems looks the way it does. Three patterns in particular punish a general-purpose allocator: long-lived denominator populations sitting under millions of transient measure objects, request-per-thread concurrency under latency contracts, and batch loads where every record is a different shape. jemalloc's design answers all three.

## Mixed lifetimes in HEDIS measure calculation

A HEDIS measure run starts with a denominator load. For a commercial book, that is somewhere between two and ten million member-year rows, each carrying enrollment intervals, demographics, and a pointer into the claims index. Call it three to eight gigabytes resident, allocated once per pipeline invocation, kept stable for the entire run. Then for each of the forty or so measures, I allocate and free millions of small transient objects: exclusion-check structs, event-lookup tuples, date-range comparators, intermediate result rows. Each transient object is somewhere between thirty-two bytes and a few kilobytes, and they churn at perhaps a hundred thousand allocations per second per measure thread.

Under glibc malloc, the long-lived denominator and the short-lived transient garbage interleave on the same heap. After a few measures, the heap looks like a Swiss cheese: stable rows pinned in place, freed transient holes scattered between them, and the resident set size keeps climbing because the freed pages cannot be returned to the OS without compaction. jemalloc's arenas[^arena] solve this directly. I pin the denominator allocation to one arena and let the measure logic churn through a second. The stable arena stays packed and never sees a free until pipeline teardown. The churn arena cycles through dirty pages and returns them to the OS on a regular cadence. Fragmentation stops being a function of how long the pipeline has been running.

<figure>
<svg viewBox="0 0 720 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Two-panel diagram. Top panel shows a single heap bar with long-lived black blocks and short-lived gray blocks interleaved, with white gaps after the gray blocks are freed, labeled fragmentation. Bottom panel shows two separate arena bars: Arena A packed with black blocks labeled stable no fragmentation, and Arena B with gray blocks labeled churn zone cleanly reclaimable." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="20" y="20" font-size="11" letter-spacing="1.4" fill="#6a6a6a">WITHOUT ARENA ISOLATION (GLIBC DEFAULT)</text>
  <text x="20" y="38" font-size="13" font-style="italic" fill="#6a6a6a">Single heap. Long-lived and short-lived data interleave.</text>
  <rect x="20" y="56" width="680" height="36" fill="none" stroke="#d0d0c8" stroke-width="1"/>
  <rect x="22" y="58" width="60"  height="32" fill="#111"/>
  <rect x="86" y="58" width="42"  height="32" fill="#6a6a6a"/>
  <rect x="132" y="58" width="80" height="32" fill="#111"/>
  <rect x="216" y="58" width="36" height="32" fill="#6a6a6a"/>
  <rect x="256" y="58" width="70" height="32" fill="#111"/>
  <rect x="330" y="58" width="48" height="32" fill="#6a6a6a"/>
  <rect x="382" y="58" width="60" height="32" fill="#111"/>
  <rect x="446" y="58" width="40" height="32" fill="#6a6a6a"/>
  <rect x="490" y="58" width="76" height="32" fill="#111"/>
  <rect x="570" y="58" width="50" height="32" fill="#6a6a6a"/>
  <rect x="624" y="58" width="74" height="32" fill="#111"/>
  <rect x="20" y="108" width="680" height="36" fill="none" stroke="#d0d0c8" stroke-width="1"/>
  <rect x="22" y="110" width="60" height="32" fill="#111"/>
  <rect x="132" y="110" width="80" height="32" fill="#111"/>
  <rect x="256" y="110" width="70" height="32" fill="#111"/>
  <rect x="382" y="110" width="60" height="32" fill="#111"/>
  <rect x="490" y="110" width="76" height="32" fill="#111"/>
  <rect x="624" y="110" width="74" height="32" fill="#111"/>
  <text x="20" y="160" font-size="11" font-style="italic" fill="#7a0000">After free: fragmentation. Resident set cannot shrink.</text>
  <line x1="20" y1="180" x2="700" y2="180" stroke="#d0d0c8" stroke-width="1"/>
  <text x="20" y="208" font-size="11" letter-spacing="1.4" fill="#6a6a6a">WITH ARENA ISOLATION (JEMALLOC)</text>
  <text x="20" y="226" font-size="13" font-style="italic" fill="#6a6a6a">Two arenas. Lifetimes do not interleave.</text>
  <text x="20" y="252" font-size="10" letter-spacing="1.2" fill="#6a6a6a">ARENA A · DENOMINATOR (STABLE, NO FRAGMENTATION)</text>
  <rect x="20" y="260" width="680" height="28" fill="none" stroke="#d0d0c8" stroke-width="1"/>
  <rect x="22" y="262" width="676" height="24" fill="#111"/>
  <text x="20" y="312" font-size="10" letter-spacing="1.2" fill="#6a6a6a">ARENA B · MEASURE CHURN (CLEANLY RECLAIMABLE)</text>
  <rect x="20" y="320" width="680" height="28" fill="none" stroke="#d0d0c8" stroke-width="1"/>
  <rect x="22" y="322" width="676" height="24" fill="#6a6a6a"/>
</svg>
<figcaption>Arena isolation for mixed-lifetime data. Stable rows live in one arena and never see a free until pipeline teardown; transient measure logic churns through a second arena whose dirty pages return to the OS on a fixed cadence.</figcaption>
</figure>

## Concurrency in claims adjudication

A claims adjudication service has the opposite shape. There is no long-lived working set worth talking about. Every request is its own short-lived universe: parse the 837, look up eligibility, run the benefit grid, build a response, free everything. Two hundred threads doing this in parallel under a sub-fifty-millisecond contract will allocate and free working memory hundreds of thousands of times per second across the process. The bottleneck is not throughput in any single thread. It is contention on the allocator's lock when two hundred threads all try to claim from the same arena at the same time.

jemalloc's tcache[^tcache] sidesteps this. Each thread holds its own cache of recently-freed regions, organized by size class, and the fast path for both `malloc` and `free` lives entirely inside the thread. No atomics, no mutex, no cache-line bouncing. The shared arena is touched only when the tcache needs a refill or a flush, which happens on the order of one access per few thousand allocations rather than one per allocation. For a 200-thread service this is the difference between linear scaling and a thundering herd.

<figure>
<svg viewBox="0 0 720 380" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Three threads each with their own tcache box on the left, each containing several cached allocation squares. A fast-path arrow with no lock label points from each thread to its tcache. Slow rare arrows from each tcache point to a single shared arena box on the right labeled mutex protected, with the annotation only on fill or flush." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="20" y="20" font-size="11" letter-spacing="1.4" fill="#6a6a6a">TCACHE FAST PATH UNDER CONCURRENCY</text>
  <text x="20" y="76" font-size="13" fill="#111">Thread 1</text>
  <text x="20" y="178" font-size="13" fill="#111">Thread 2</text>
  <text x="20" y="280" font-size="13" fill="#111">Thread 3</text>
  <text x="100" y="60" font-size="10" font-style="italic" fill="#7a0000">fast path: no lock</text>
  <line x1="80" y1="68" x2="180" y2="68" stroke="#7a0000" stroke-width="1.2"/>
  <polygon points="180,68 174,65 174,71" fill="#7a0000"/>
  <line x1="80" y1="170" x2="180" y2="170" stroke="#111" stroke-width="1"/>
  <polygon points="180,170 174,167 174,173" fill="#111"/>
  <line x1="80" y1="272" x2="180" y2="272" stroke="#111" stroke-width="1"/>
  <polygon points="180,272 174,269 174,275" fill="#111"/>
  <rect x="180" y="50" width="180" height="44" fill="none" stroke="#111" stroke-width="1"/>
  <text x="190" y="44" font-size="11" letter-spacing="1.2" fill="#6a6a6a">TCACHE</text>
  <rect x="190" y="60" width="20" height="24" fill="#111"/>
  <rect x="216" y="60" width="20" height="24" fill="#6a6a6a"/>
  <rect x="242" y="60" width="20" height="24" fill="#111"/>
  <rect x="268" y="60" width="20" height="24" fill="#6a6a6a"/>
  <rect x="294" y="60" width="20" height="24" fill="#111"/>
  <rect x="320" y="60" width="20" height="24" fill="#6a6a6a"/>
  <rect x="180" y="152" width="180" height="44" fill="none" stroke="#111" stroke-width="1"/>
  <text x="190" y="146" font-size="11" letter-spacing="1.2" fill="#6a6a6a">TCACHE</text>
  <rect x="190" y="162" width="20" height="24" fill="#6a6a6a"/>
  <rect x="216" y="162" width="20" height="24" fill="#111"/>
  <rect x="242" y="162" width="20" height="24" fill="#6a6a6a"/>
  <rect x="268" y="162" width="20" height="24" fill="#111"/>
  <rect x="294" y="162" width="20" height="24" fill="#6a6a6a"/>
  <rect x="180" y="254" width="180" height="44" fill="none" stroke="#111" stroke-width="1"/>
  <text x="190" y="248" font-size="11" letter-spacing="1.2" fill="#6a6a6a">TCACHE</text>
  <rect x="190" y="264" width="20" height="24" fill="#111"/>
  <rect x="216" y="264" width="20" height="24" fill="#6a6a6a"/>
  <rect x="242" y="264" width="20" height="24" fill="#111"/>
  <rect x="268" y="264" width="20" height="24" fill="#6a6a6a"/>
  <rect x="294" y="264" width="20" height="24" fill="#111"/>
  <line x1="360" y1="72" x2="540" y2="170" stroke="#6a6a6a" stroke-width="1" stroke-dasharray="3,3"/>
  <line x1="360" y1="174" x2="540" y2="174" stroke="#6a6a6a" stroke-width="1" stroke-dasharray="3,3"/>
  <line x1="360" y1="276" x2="540" y2="178" stroke="#6a6a6a" stroke-width="1" stroke-dasharray="3,3"/>
  <text x="395" y="124" font-size="10" font-style="italic" fill="#6a6a6a">rare: only on fill / flush</text>
  <text x="395" y="232" font-size="10" font-style="italic" fill="#6a6a6a">rare: only on fill / flush</text>
  <rect x="540" y="120" width="160" height="100" fill="none" stroke="#111" stroke-width="1"/>
  <text x="550" y="142" font-size="11" letter-spacing="1.2" fill="#6a6a6a">SHARED ARENA</text>
  <text x="550" y="162" font-size="11" fill="#111">mutex protected</text>
  <line x1="550" y1="176" x2="690" y2="176" stroke="#d0d0c8" stroke-width="1"/>
  <text x="550" y="196" font-size="10" font-style="italic" fill="#6a6a6a">backing pages, slabs,</text>
  <text x="550" y="210" font-size="10" font-style="italic" fill="#6a6a6a">extents, refill source</text>
</svg>
<figcaption>The tcache absorbs the overwhelming majority of allocations and frees with no synchronization. The shared arena is touched only when a thread's cache needs to be refilled or drained, which is rare relative to the per-request allocation rate.</figcaption>
</figure>

## Variable-width records in batch ETL

A claims extract is the canonical example of allocation-size chaos. One row carries a single diagnosis code and no modifiers; the next carries twenty-three diagnoses, six procedure codes, four modifier fields, and a long free-text remark. The struct I am building per row might be 256 bytes for a clean professional claim and 4 kilobytes for a complex inpatient one. A general-purpose allocator looking at this stream serves each request with whatever-fits, which means the heap accumulates oddly-sized free regions that nothing else asks for at exactly the right size.

jemalloc rounds every request up to the nearest size class[^sizeclass] and serves it from a slab[^slab] of fixed-size regions. There are around forty size classes spanning eight bytes to four megabytes, geometrically spaced. A 256-byte struct lives in the 256-byte slab; a 4096-byte struct lives in the 4096-byte slab; a 312-byte struct rounds up to 320 and lives in that slab. The internal waste from rounding is bounded at roughly twelve percent on average, and the external fragmentation that kills glibc on this workload is gone, because everything in a given slab is the same size. When a slab empties it returns to the arena and is reused for the next request in that class.

## jemallocviz

I built jemallocviz to make these behaviors legible. Particles in the simulation are transient allocations; the cursor seeds new ones; pressing a number key shifts the active size class so I can watch the slab system pick up a new bin; an arena-isolation toggle splits the field into two regions to simulate the HEDIS pipeline shape; a thread mode spawns independent emitters with their own tcaches to simulate the claims-adjudication shape. The numbers driving the visuals are pulled from the running allocator over `mallctl`[^mallctl], jemalloc's runtime control API, on a hundred-millisecond cadence.

```c
size_t sz = sizeof(uint64_t);
uint64_t epoch = 1;

while (running) {
    mallctl("epoch", NULL, NULL, &epoch, sizeof(epoch));

    uint64_t allocated, active, mapped, resident;
    mallctl("stats.allocated", &allocated, &sz, NULL, 0);
    mallctl("stats.active",    &active,    &sz, NULL, 0);
    mallctl("stats.mapped",    &mapped,    &sz, NULL, 0);
    mallctl("stats.resident",  &resident,  &sz, NULL, 0);

    push_to_visualizer(allocated, active, mapped, resident);
    usleep(100 * 1000);
}
```

Bumping `epoch` is what makes the next four reads coherent: jemalloc caches its statistics between epochs, so without that write the four counters would drift relative to each other. `allocated` is bytes the program asked for; `active` is bytes in pages backing live allocations; `mapped` is bytes the allocator has from the OS; `resident` is bytes physically in RAM. The gap between `allocated` and `resident` is where fragmentation hides.

## What I want to do next

The honest version of this post lands a year from now with numbers attached. The next step is to profile a real HEDIS measure run, first against glibc and then against jemalloc with two arenas pinned per the pattern above, and report resident set size, peak allocation rate, and ninety-fifth-percentile measure runtime side by side. The architectural argument is uncontroversial. The size of the win on a specific workload is the part worth measuring.

[^jemalloc]: jemalloc is a general-purpose memory allocator developed at Facebook, designed to minimize fragmentation and scale across many threads. It is the default allocator in FreeBSD, Rust (formerly), and a number of large server systems including the one this post is about.

[^arena]: An arena in jemalloc is an independent allocator instance with its own heap, bins, and locks. A process can have many arenas. Threads either map to an arena automatically or are pinned explicitly via `mallctl`.

[^tcache]: The thread-local cache. Each thread holds a small per-size-class buffer of recently-freed regions so that the common case of `malloc` and `free` requires no synchronization with the shared arena.

[^sizeclass]: A discrete bucket that jemalloc rounds allocation requests up to. Size classes are geometrically spaced so the maximum waste from rounding is bounded and predictable.

[^slab]: A contiguous run of memory subdivided into equal-sized regions, all of the same size class. Allocating from a slab is a bit-vector flip; freeing returns the bit. When the slab empties it goes back to the arena for reuse.

[^mallctl]: jemalloc's general-purpose introspection and control function. It exposes a tree of named keys that read or write internal counters, knobs, and arena state. The visualizer uses it for read-only stats polling.
