---
title: "Deletes Are Data Too"
description: "Deletes are the quiet failure mode in data pipelines. Here are the main ways to detect them and the tradeoffs you’re actually signing up for."
publishDate: 2025-02-23 
tags: ["data-engineering", "cdc", "data-pipelines", "data-quality", "architecture"]
---

Identifying deletes that happen in upstream systems is a deceptively hard problem.

Inserts show up. Updates leave fingerprints. Deletes just disappear and take your assumptions with them.

If you miss them, nothing breaks immediately. Your dashboards still render. Your aggregates still compute. You just slowly drift away from reality until something important no longer ties out and now you are debugging a ghost.

There are a few standard approaches people reach for. None of them are perfect. All of them are tradeoffs.

Change logs capture every modification made to the data, including deletions. If you can read directly from database logs using something like Debezium, you get a stream of inserts, updates, and deletes as first class events. There is no guessing. You see exactly what happened.

The upside is precision and timeliness. The downside is that you are now operating infrastructure that is not trivial. You are dealing with connectors, offsets, schema changes, and usually a streaming system whether you planned for one or not. It is worth it if correctness matters. It is overkill if your team is not ready for it.

Soft deletes are the simplest thing that works. Instead of removing rows, the upstream system marks them with something like is_deleted = true. Downstream systems filter them out.

This is easy to reason about and easy to debug because nothing is actually gone. But it pushes discipline onto every query and every consumer. Forget the filter once and you are back in trouble. Over time, tables grow, performance changes, and you have to manage that explicitly.

Full table comparison is the fallback when you do not control upstream and cannot get change logs. You take a snapshot, compare it to what you already have, and anything missing by primary key is treated as a delete.

It works. It is also expensive and slow at scale. You are inferring deletes instead of observing them, which means you are always one step removed from what actually happened. For small datasets or periodic reconciliation, it is fine. For large systems, it becomes a tax you keep paying.

The interesting part is that most real systems do not choose just one of these.

They layer them.

You might use CDC for your main pipelines because you want low latency and accuracy. You keep soft delete semantics around because they are easy to reason about and give you a safety net. Then you run periodic full compares to catch drift and validate that everything is still aligned.

That last piece matters more than people think. Even well built pipelines drift over time. Having a way to re-anchor to truth is the difference between knowing your system works and hoping it does.

If you are starting from scratch, a practical path is to begin with soft deletes if you can influence upstream, add CDC when you need stronger guarantees, and keep a lightweight reconciliation process running in the background.

Deletes are not just another change type. They are absence. And absence is easy to ignore until it is not.

How are you capturing deletes in your pipelines today?