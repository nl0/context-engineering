---
layout: default
title: "Course Summary"
nav_order: 9
---

# Course Summary

Context engineering is the discipline of managing the scarcest resource in AI systems: the context window. Through this course, we've established that:

1. **Tokens are the currency** — everything has a cost measured in tokens ([Module 1](./01-tokens-and-inference.md))
2. **Context windows are smaller than advertised** — design for the smart zone, not the marketing number ([Module 2](./02-context-window-size.md))
3. **The messages array has a fixed-cost structure** — system prompt, harness, project context, and tools consume tokens before your conversation even begins ([Module 3](./03-messages-array.md))
4. **Tool calls are memory allocations** — they grow context permanently within a session ([Module 4](./04-tool-calling.md))
5. **Sub-agents are context isolators** — delegate reads to sub-agents, keep writes centralized ([Module 5](./05-sub-agents.md))
6. **Message passing is the architecture** — design explicit protocols between context windows ([Module 6](./06-message-passing.md))
7. **Fresh context beats stale context** — the Ralph Wiggum Loop (Requirements → Planning → Building) uses the filesystem as memory and the context window as disposable compute ([Module 7](./07-ralph-wiggum-loop.md))
8. **Prevention beats compaction** — avoid filling context rather than trying to compress it after the fact ([Module 8](./08-context-management.md))

The central insight: **treat the context window as you would treat memory in a systems programming language — as a finite, precious resource that requires deliberate management.**
