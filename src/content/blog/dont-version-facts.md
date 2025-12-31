---
title: "Why You Probably Shouldn't Version Your Fact Table"
description: "Most teams version their fact tables because they've modeled their dimensions incorrectly. Understanding the true grain of your table—whether it's event-based or state-based—will save you from double-counting metrics, failed audits, and painful refactoring projects in healthcare data warehouses."
publishDate: 2025-12-24 
tags: ["data modeling", "warehousing", "data architecture"]
---

# Why You Probably Shouldn't Version Your Fact Table

A few years ago, during a technical interview, I was asked how I would implement SCD Type 2 on a large fact table.

I paused and asked, "Why would you do that?"

"It's the requirement," he said.

I pushed further: "What's the business case?"

Because to me, this didn't sound like an SQL optimization problem. It sounded like a data model problem. And nine times out of ten, when someone tells you "it's the requirement," what they really mean is "we didn't think this through."

## The Core Problem

Fact tables, when designed properly, should be append-only. Period.

Just because you *can* version a fact table doesn't mean you *should*. And in most cases, you absolutely shouldn't.

In healthcare analytics, fact tables capture events. A claim was adjudicated. A member enrolled in a plan. A Star Ratings measure was submitted. These events happened once, at a specific point in time. They don't "slowly change" over time. The claim didn't gradually transform from one state to another. It was processed, adjudicated, and paid. That's the event.

When you treat a fact table like an SCD Type 2 dimension, you break something fundamental. You create multiple versions of the same event. Metrics start double-counting, and if you've ever tried explaining to a CFO why member months don't reconcile to eligibility files, you know exactly how that conversation goes. Stakeholders reasonably ask which version is the source of truth, and you don't have a good answer. The grain becomes ambiguous. Queries become slower because they need complex logic to pick the "current" version. Fixing it later requires painful ETL refactoring across every dependent mart.

It's like keeping a historical record of the same hospital admission happening four different ways. That's not history, that's confusion. And confusion in healthcare data leads to bad business decisions, failed audits, and incorrect Star Ratings calculations.

## When Versioning Actually Works

I'm not saying versioning is always wrong. There are legitimate scenarios where it makes sense, but they're rarer than most people think.

Daily member eligibility snapshots capture state, not events. The member's plan assignment changes over time, and you need each day's state preserved for accurate member month calculations. Monthly premium rates change, and you need to know which rate was effective when claims were processed for proper revenue recognition. Star Ratings thresholds get published annually by CMS, and historical comparisons require knowing which cut points were active in each measurement year. Provider network status changes affect claims payment calculations and need to be tracked over time.

In these cases, the fact table grain is time-based or state-based, not event-based. Versioning is valid because the state genuinely changes over time, and each version represents meaningful business information.

Though even here, let me be clear: you can often design these as append-only if you structure them with proper effective dating. You don't need SCD Type 2 machinery. You just need to close your previous records when state changes and insert new ones. Same result, cleaner implementation.

## Understanding Grain Saves Everything

The question that actually matters is this: what is the true grain of this table?

If the grain is one row per event—one row per claim, one row per encounter, one row per enrollment transaction—do not apply SCD Type 2. Don't do it. Put historical context in the dimension tables where it belongs. Your claim fact records when the claim was processed. If you need to know what the provider's network status was at that time, that's dimensional context. Build your dimensions correctly.

If the grain is one row per state or time period—one row per member per day, one row per contract per month—versioning may be appropriate. You're modeling a snapshot fact, not a transaction fact. But be honest with yourself about whether you actually need snapshots or whether you're just avoiding fixing your dimensional model.

## Why This Matters in Healthcare Data Warehouses

Healthcare data warehouses are particularly vulnerable to this anti-pattern, and I see it repeatedly.

Claims corrections exist, and teams think they need to version the fact table. They don't. They need a separate claim adjustment event with proper lineage to the original claim. This isn't complicated—it's just different from what they initially built.

Regulatory changes are frequent. Star Ratings measures get redefined, and teams version historical facts instead of properly dating the measure definition dimensions. This creates a nightmare when CMS asks you to restate historical performance under new measure specifications.

Multiple source systems create conflicts. When eligibility data comes from three systems, versioning facts seems easier than reconciling dimensions properly. But "easier" in month one becomes "catastrophically expensive" in month twelve when nothing reconciles and nobody trusts the data.

The pattern is always the same: poor dimensional modeling leads to fact table versioning, which leads to metric confusion, which leads to loss of trust in the data warehouse.

## The Real Requirement

Understanding your grain isn't just good data modeling. In healthcare analytics, where regulatory compliance and financial accuracy are non-negotiable, getting this wrong creates downstream problems that compound. Your quality measures won't calculate correctly. Your financial forecasts won't reconcile. Your audit trail becomes unintelligible. Your Star Ratings calculations will be wrong, and you won't know why until CMS publishes their results and they don't match yours.

When someone tells you "the requirement is to version the fact table," push back. Ask what problem they're actually trying to solve. Ask what the business case is. Ask what the grain is supposed to be.

Most of the time, you don't need to version your facts. You need to model your dimensions correctly.