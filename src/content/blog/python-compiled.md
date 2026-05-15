---
title: "What I Got Wrong About Python Over Dinner"
description: "A confident dinner-table claim that Python isn't compiled, walked back. Bytecode, .pyc files, and what compiled vs. interpreted actually means."
publishDate: 2026-05-15
tags: ["python", "programming", "misconceptions"]
---

I was at dinner the other week, eating sambusas and a plate of suqaar at a Somali spot, and I said something with the easy confidence of a person who has not been challenged in a while: "Python isn't compiled." A friend across the table, who writes more Rust than is probably healthy, looked at me and said, "Wait, are you sure?" And I, immediately, was not.

Here's what I had to walk back, because it's the kind of thing a lot of working developers carry around without ever stress-testing it.

## The claim, and why it feels right

The folk definition of a compiled language is: you write code, you run a compiler over it, you get a binary, you ship the binary. The folk definition of an interpreted language is: you write code, you run the file. Python, by that measure, is obviously not compiled. There is no build step. There is no `a.out` sitting on disk. You type `python thing.py` and the thing happens. If it walks like an interpreter and quacks like an interpreter, it's an interpreter. Right?

This is the trap. The developer experience really is "no build step, just run the file," and that experience is what we mean when we casually say a language is interpreted. The problem is that the experience is hiding a step rather than skipping one.

## What CPython is actually doing

When CPython gets a `.py` file, it does not start reading source code line by line like a shell script. It compiles the source into bytecode first, a flat sequence of stack-machine instructions like `LOAD_CONST`, `BINARY_ADD`, `CALL_FUNCTION`. Only then does the runtime start executing anything. The compiler is just so fast and so quiet that you never notice it ran.

If you want proof, look in any Python project you have worked in. You will find a `__pycache__/` directory full of `.pyc` files. Those are cached bytecode, written to disk so CPython can skip recompiling on the next run. They are receipts. The compiler was there. And if you want to see what it produced, `import dis; dis.dis(some_function)` will print the bytecode out for you, opcode by opcode.

## Compile to what, exactly?

The distinction I should have been drawing at dinner isn't compiled versus not compiled. It's what the compiler targets. C, Rust, and Go compile to machine code, instructions a CPU runs directly. Python, Java, and C# compile to bytecode for a virtual machine: CPython's eval loop, the JVM, the CLR. Both halves of that are compilation. The artifact is different and the runtime is different, but there is a compile step in every one of them.

Even the REPL compiles. Every statement you type at a `>>>` prompt gets compiled to bytecode in memory before the VM executes it. The only thing missing is the on-disk cache. The lack of a `.pyc` isn't proof that nothing was compiled. It's proof that nothing was saved.

## So what

"Compiled versus interpreted" is a useful shorthand. It tells you something real about how a language feels to use, and most of the time the distinction it gestures at is the one you care about. But it falls apart under pressure, which is what happened to me at a table with a half-finished plate of suqaar. The honest version is longer and less satisfying: almost every language you'll touch is compiled in some sense, and the interesting question is what the compiler targets and what runs the result. Anyway, the injera was good.
