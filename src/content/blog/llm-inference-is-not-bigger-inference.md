---
title: "LLM Inference Is Not Just Bigger Inference"
description: "Why serving large language models is a fundamentally different systems problem from traditional ML inference, especially in applied healthcare IT."
publishDate: 2025-12-19
draft: true
tags: ["llm", "inference", "healthcare-it", "architecture", "systems"]
---

## Introduction

In healthcare analytics, we’ve lived with “inference” for years.

HEDIS gap closure models. Risk adjustment predictors. Fraud detection. CNNs on imaging. Gradient boosting on claims.

Those systems assume something very stable:

- Fixed input shapes  
- Fixed compute graphs  
- Predictable latency per request  
- Stateless serving  

It’s clean. Deterministic. Boring in a good way.

LLMs break almost all of that.

---

## Main Content

### 1. Variable-Length Computation Changes Everything

Traditional inference assumes uniform work per request.

LLMs don’t.

- Prompt length varies  
- Output length varies  
- Total compute is unknown upfront  

Two requests hit your system:

- One finishes in 200ms  
- The other generates 800 tokens  

You cannot just batch and wait.

LLM systems use **continuous batching**, dynamically inserting and removing requests as tokens complete.

> flowchart LR  
> A[Incoming Requests] --> B[Continuous Batching Engine]  
> B --> C[GPU Batch]  
> C --> D[Token Completion]  
> D --> B  

The batch is fluid, not fixed.

In healthcare IT terms: this is the difference between a nightly HEDIS job and a real-time clinical documentation assistant.

---

### 2. Prefill vs Decode: Two Different Workloads

LLM inference splits into:

- **Prefill**: process the full prompt  
- **Decode**: generate tokens one at a time  

They behave differently.

- Prefill is compute-bound  
- Decode is memory-bandwidth-bound  

Running both on the same GPUs causes interference and latency jitter.

High-performance systems separate them.

> flowchart LR  
> A[Client Request] --> B[Prefill Pool]  
> B --> C[KV State Transfer]  
> C --> D[Decode Pool]  
> D --> E[Streaming Tokens to Client]  

Prefill is like loading the full patient history into memory.  
Decode is writing the note sentence by sentence.

Treating them as identical workloads is architectural laziness.

---

### 3. KV Cache Is a Systems Problem

LLMs rely on a **KV cache** to store attention state.

In multi-turn healthcare conversations:

- The prefix persists  
- The model reuses prior computation  
- GPU memory holds request-specific state  

This introduces:

- Cache eviction decisions  
- Fragmentation concerns  
- Memory locality challenges  

Modern engines implement paged KV caches similar to virtual memory systems.

Traditional models finish, release memory, and disappear.  
LLMs persist.

That changes infrastructure design.

---

### 4. Routing Stops Being Stateless

Traditional scaling:

- Replicate the model  
- Route round-robin  

LLMs benefit from prefix-aware routing.

If replica A holds the KV cache for a conversation, routing the next request to replica B destroys cache locality.

> flowchart LR  
> A[Router]  
> A -->|Prefix Hash| B[Replica 1]  
> A -->|Prefix Hash| C[Replica 2]  
> B --> D[KV Cache]  
> C --> E[KV Cache]  

In applied healthcare IT, this mirrors longitudinal care systems. Context matters. Routing must respect state.

---

### 5. Mixture-of-Experts Is Not Replication

LLMs increasingly use **Mixture-of-Experts (MoE)**:

- Shared attention layers  
- Sharded expert layers  
- Token-level routing  

> flowchart TD  
> A[Token] --> B[Shared Attention]  
> B --> C1[Expert 1]  
> B --> C2[Expert 2]  
> B --> C3[Expert N]  

This is one distributed model with dynamic internal traffic.

Not just more replicas.

---

## Conclusion

LLM inference is not interesting because the models are large.

It is interesting because the systems problem is different:

- Continuous batching  
- Prefill/decode separation  
- KV cache management  
- Prefix-aware routing  
- MoE sharding  

If we deploy LLMs into healthcare workflows using infrastructure assumptions from 2018, we will blame the model for what is actually a systems failure.

LLM inference is a different class of architecture.

And healthcare IT is becoming a systems discipline.
