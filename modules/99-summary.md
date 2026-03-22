# Summary

Context engineering is the discipline of managing the scarcest resource in AI systems: the context window. This book has established that:

1. **Tokens are the currency** — everything has a cost measured in tokens ([Chapter 1](./01-tokens-and-inference.md))
2. **Context windows are smaller than advertised** — design for the smart zone, not the marketing number ([Chapter 2](./02-context-window-size.md))
3. **The messages array has a fixed-cost structure** — system prompt, harness, project context, and tools consume tokens before your conversation even begins ([Chapter 3](./03-messages-array.md))
4. **Tool calls are memory allocations** — they grow context permanently within a session ([Chapter 4](./04-tool-calling.md))
5. **Sub-agents are context isolators** — delegate reads to sub-agents, keep writes centralized ([Chapter 5](./05-sub-agents.md))
6. **Message passing is the architecture** — design explicit protocols between context windows ([Chapter 6](./06-message-passing.md))
7. **Fresh context beats stale context** — the Ralph Wiggum Loop (Requirements → Planning → Building) uses the filesystem as memory and the context window as disposable compute ([Chapter 7](./07-ralph-wiggum-loop.md))
8. **Prevention beats compaction** — avoid filling context rather than trying to compress it after the fact ([Chapter 8](./08-context-management.md))

The central insight: **treat the context window as you would treat memory in a systems programming language — as a finite, precious resource that requires deliberate management.**
