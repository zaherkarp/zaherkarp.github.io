---
title: "Test Mermaid Diagrams"
description: "A simple test page to verify Mermaid diagram rendering works correctly."
publishDate: 2025-01-10
draft: false
tags: ["test", "mermaid"]
---

## Simple Flowchart

This is a basic test to verify Mermaid rendering works:

```mermaid
flowchart LR
  Internet --> App
  App --> Database
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant App
    participant Database

    User->>App: Request data
    App->>Database: Query
    Database-->>App: Results
    App-->>User: Display results
```

If you can see the diagrams above rendered as actual flowcharts and sequence diagrams (not code blocks), then Mermaid is working correctly!
