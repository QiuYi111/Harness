---
name: harness-grill
description: Stress-test a plan or spec by asking the user pointed questions one at a time. Each question probes assumptions, edge cases, and implicit requirements. Provides recommended answers. Use before spec finalization or when requirements feel fuzzy.
disable-model-invocation: true
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

Use the question tree in `QUESTION_TREE.md` as your interrogation framework.
