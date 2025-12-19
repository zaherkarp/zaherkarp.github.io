---
title: "I Don’t Actually Care About Making Change"
description: "Solving the same problem in Haskell, Python, and SQL reveals less about coins and more about how programming languages shape how we think about correctness, process, and structure."
publishDate: 2025-12-19
tags: ["software-engineering", "data-engineering", "algorithms", "python", "sql", "haskell", "functional-programming"]
---

# I Don’t Actually Care About Making Change

I don’t actually care how many ways there are to make change for a dollar.

What I care about is why the *same problem* feels almost self-evident in one language, procedural in another, and strangely structural in a third. That difference ends up being far more instructive than the numeric answer.

The change-making problem is a familiar one. It shows up in interviews, coding exercises, and textbooks. Most people solve it once, recognize the pattern, and move on.

I didn’t. Not because the problem itself is especially interesting, but because solving it in **Haskell**, then **Python**, then **SQL** exposed something subtle but important: programming languages don’t just offer tools. They nudge you toward particular ways of reasoning.

## The Problem (Briefly)

Given a target amount and a set of coin denominations, how many *unique combinations* of coins sum to that amount?

Order does not matter.  
`1 + 5` is the same as `5 + 1`.

That’s the entire problem. It looks trivial. It isn’t.

## Haskell: State the Definition and Let It Work

When I solve this problem in Haskell, it doesn’t feel like I’m writing an algorithm. It feels like I’m writing down a definition and trusting it.

```haskell
countChange :: Int -> [Int] -> Int
countChange 0 _      = 1
countChange _ []     = 0
countChange amount (c:cs)
  | amount < 0 = 0
  | otherwise =
      countChange (amount - c) (c:cs)
    + countChange amount cs
```

There’s no explicit iteration here. No mutable state. Just cases.

If the amount is zero, that’s a valid solution.  
If there are no coins left, it isn’t.  
Otherwise, the answer is the sum of solutions that include the current coin and solutions that exclude it.

What stands out isn’t just concision. It’s how directly the code mirrors the underlying logic. The function reads like a recursive definition rather than a sequence of steps.

This version is inefficient without memoization. Haskell doesn’t remove the need to think about performance, but it cleanly separates *correctness* from *optimization*.

## Python: Make the Process Explicit

Python pulls me in the opposite direction. Here, I’m very aware of execution.

```python
def count_change(amount, coins):
    dp = [0] * (amount + 1)
    dp[0] = 1

    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] += dp[i - coin]

    return dp[amount]
```

This solution is operational.

`dp[i]` represents the number of ways to make amount `i`.  
Each coin extends existing partial solutions.  
The loop order enforces uniqueness by construction.

State is visible. Performance characteristics are obvious. Python trades elegance for explicitness, and in many production settings that’s the right trade.

## SQL: Reframe the Problem as Data

Solving this problem in SQL requires a different mental model.

SQL doesn’t want loops or mutable state. It wants to know what a *valid row* looks like.

Using a recursive CTE, the problem becomes: what does a partial solution look like, and how can it be extended?

```sql
WITH RECURSIVE change(amount, coin_index) AS (
    SELECT 0, 1
    UNION ALL
    SELECT
        amount + c.value,
        coin_index
    FROM change
    JOIN coins c
      ON c.id >= coin_index
    WHERE amount + c.value <= 100
)
SELECT COUNT(*)
FROM change
WHERE amount = 100;
```

Each row represents a state.  
Each join represents a legal transition.  
Constraints replace control flow.

This doesn’t feel like an algorithm. It feels like modeling a space of valid states and letting the engine explore it.

## Same Answer, Different Emphases

All three approaches are correct, but they emphasize different things.

Haskell emphasizes definitions and exhaustiveness.  
Python emphasizes process and accumulation.  
SQL emphasizes structure and constraints.

The problem stays the same. The thinking changes.

## Closing

I still don’t care about making change for a dollar.

But I care a lot about what a language asks me to be explicit about, and what it allows me to abstract away. Solving the same problem three ways made that impossible to ignore.

If you haven’t taken a familiar problem and solved it in an unfamiliar paradigm, it’s worth doing. You may not learn a new trick.

You’ll probably learn something about how you think.
