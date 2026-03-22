# Module 8: Context Management Strategies

## Lesson 8.1: The `malloc` Without `free`

**The memory management analogy** makes the problem concrete. In C, `malloc()` allocates memory and `free()` releases it. Context engineering has `malloc` — you can add messages, tool results, and context to the array. But there is no `free`. Once a message is in the array, it stays there for the rest of the session. (Technically you could remove messages from the array before sending, but most frameworks don't support this, and doing it naively breaks conversational coherence.)

This matters because in traditional programming, memory leaks are bugs. In LLM context management, "leaks" are the default behavior. Every tool call, every file read, every error message — they all accumulate. The context only grows.

### Context Window vs. Traditional Memory

| Operation | Traditional Memory | Context Window |
|-----------|-------------------|----------------|
| Allocate | `malloc(size)` | Add a message to the array |
| Use | Read/write the pointer | Model attends to the message |
| Free | `free(ptr)` | Not available |
| Garbage collect | Automatic (in GC languages) | Not available |
| Leak | Bug — wastes RAM | Default behavior — wastes context |
| Out of memory | Process crashes | Model enters dumb zone |

The three "memory management" primitives we DO have:

1. **Don't allocate**: Avoid putting things in context that aren't needed (use sub-agents — [Module 5](./05-sub-agents.md))
2. **Compact**: Summarize old messages to reduce their token count (lossy — see Lesson 8.2)
3. **Reset**: Start a fresh context window with curated state (the Ralph Wiggum Loop — [Module 7](./07-ralph-wiggum-loop.md))

## Lesson 8.2: Why Compaction Is Dangerous

**Compaction** (also called context compression or summarization) replaces older messages in the array with a shorter summary. For example, 20 messages of conversation (5,000 tokens) might be compressed to a 500-token summary.

Current tools handle this in different ways. Claude Code automatically compresses older messages into a summary when context reaches ~80% of the window. ChatGPT uses a "memory" system that extracts key facts from conversations. LangChain offers `ConversationSummaryMemory` that summarizes older turns.

Understanding the mechanics reveals why this is fragile. Auto-compact typically fires at ~95% capacity (~167K of a 200K token window) — by the time it triggers, you're already deep in context pressure. `CLAUDE.md` (and similar injected instruction files) survive compaction because they're re-injected fresh from disk on every turn — they're the one thing that persists fully intact. Old file reads, grep results, and command outputs account for 60–80% of the content removed during compaction — these are high-token, low-signal messages once acted upon. A practitioner tip: run `/compact` manually with custom instructions (e.g., `/compact summarize only the to-do items and keep all file paths`) at strategic moments rather than letting auto-compact fire at the worst possible time.

The core danger is **non-deterministic eviction**. You can't control what the model considers important when summarizing. The model decides what to keep and what to discard. This is fine for casual conversation. It's dangerous for agent workloads where a specific instruction from 30 messages ago is still critical, a file path mentioned early in the conversation is needed later, an error pattern from the first test run needs to inform the fourth test run, or a constraint ("never modify the database schema") was stated once and must persist.

Real failure scenarios illustrate the risk. **Lost constraints**: "Use only the existing API endpoints" gets compacted away, and the agent creates new endpoints. **Lost context**: A critical error message from an earlier tool call is summarized as "encountered some errors," and the specific error information is gone. **Lost decisions**: "We decided to use approach B because approach A had race conditions" gets compacted to "using approach B," so the next iteration doesn't know why and might revisit approach A. **Merged context**: Information from separate tool calls gets merged in the summary, creating false associations.

The fundamental problem is that compaction is lossy compression performed by the same model that's already struggling with context management. You're asking a model that loses information in long contexts to decide what information is safe to discard. This is asking the fox to guard the henhouse. As Huntley puts it in the Ralph Wiggum Loop ([Module 7](./07-ralph-wiggum-loop.md)): "Compaction is the devil." Here's why he's right. The model performing the compression has no ground truth about what matters downstream — it's making a bet, and every bet it loses destroys information you can never recover. The only safe compaction is the kind you control explicitly, with protected categories and priority tags (see Strategy 3 below).

## Lesson 8.3: Better Strategies

Given the dangers of compaction, what should you actually do?

### Strategy 1: Prevention Over Cure (Sub-Agent Delegation)

The best strategy is to prevent context bloat in the first place. Delegate high-token operations to sub-agents ([Module 5](./05-sub-agents.md)) and only receive summaries in the parent context. This is like avoiding memory allocation rather than trying to free it later.

### Strategy 2: Fresh Context with Curated State (The Ralph Wiggum Loop)

When context accumulation is inevitable, reset deliberately. Write critical state to a persistent file (spec/plan), start a fresh context window, and load only what's needed ([Module 7](./07-ralph-wiggum-loop.md)). This is the closest thing to `free()` — you're starting with a clean heap.

### Strategy 3: Priority-Based Eviction

If you must compact, don't let the model decide what to keep. You decide.

**Protected categories** (never evict) include the system prompt and constraints, the current task specification, active error states being debugged, and user-stated requirements and decisions. **Evictable categories** (safe to summarize) include successful tool calls whose results have been acted on, exploratory reads that didn't lead to action, and verbose output where only the conclusion matters.

A **counter-intuitive finding** from Manus (the AI agent company) is that failed actions should stay visible in context. Leaving wrong turns visible improves behavior — the model performs implicit belief updates and avoids repeating the same mistakes. Evict successful tool output, but keep failure traces.

**Observation masking** (JetBrains Research, 2025) offers another approach: instead of summarizing entire turns, keep the agent's reasoning and actions but replace older tool outputs with placeholder text. A rolling window of ~10 turns of full detail, with older observations masked. This achieved 50%+ cost reduction while actually *improving* solve rates by 2.6% — better than LLM summarization, which paradoxically made agents run 13–15% longer.

For **implementation**, maintain a priority tag on each message. When compaction is triggered, only compact messages tagged as evictable.

### The Write/Select/Compress/Isolate Taxonomy (Lance Martin)

A useful framework for reasoning about context management strategies comes from Lance Martin's "Context Engineering for Agents." Every technique maps to one of four primitives:

**Write** means saving information outside the context window for later retrieval — scratchpads, memory files, persistent state stores. **Select** means retrieving only relevant information into context when needed — RAG, dynamic tool descriptions, filtered search results. **Compress** means retaining only essential tokens from what's already in context — summarization, observation masking, trimming tool outputs. **Isolate** means splitting context across separate components so no single window bears the full load — sub-agents, sandboxed execution environments.

The strategies above map cleanly: sub-agent delegation is **Isolate**, the Ralph Wiggum Loop combines **Write** (persist state to file) and **Select** (load only what's needed), priority-based eviction is **Compress**, and the structured stores below are **Write** + **Select**.

### Strategy 4: Structured Context Stores (Emerging)

Rather than dumping everything into the linear messages array, use external structured stores.

**RAG (Retrieval-Augmented Generation)** works as "virtual memory": store information outside the context window, retrieve it on demand. Like virtual memory paging in an OS — not everything needs to be in "RAM" (context) at once. **Semantic caching** takes this further by caching model responses keyed by semantic similarity of the input. If a similar question was answered recently, reuse the cached answer without re-reading source material. **Session state stores** are external key-value stores where agents can `write("auth_approach", "JWT with refresh tokens")` and later `read("auth_approach")`. This provides persistent memory that doesn't consume context tokens until retrieved.

### Strategy 5: The Context Manager Pattern

Instead of blindly appending to the messages array, **dynamically construct it on every turn**. Maintain state externally and assemble the prompt from current state each time.

**Without a context manager** (naive append):
```
[System prompt]
[Summary: "The user wanted a Python script. I wrote a function. It had a bug..."]
[Turn 47]
[Turn 48]
```
The model forgot the coding style guidelines from turn 2 — they didn't survive summarization.

**With a context manager** (dynamic construction):
```
[System prompt + style guidelines]          (pinned — always included)
[Current file: auth.py]                     (working memory — active task)
[Latest request: "Fix the failing test"]    (current goal)
[Test output: 1 failure, truncated to key lines]  (tool result — trimmed)
```
The context manager explicitly dropped 45 turns of history. It kept what matters: instructions, current state, and the immediate task. Token count is controlled. Critical context is preserved.

This pattern also directly solves the Lost-in-the-Middle problem from [Module 2](./02-context-window-size.md). Recall the U-shaped attention curve: models attend most strongly to tokens at the beginning (primacy) and end (recency) of the context window, while information buried in the middle gets the least attention. The Context Manager exploits this by pinning critical state — system prompts, style guidelines, constraints — to the top of the assembled context (primacy zone) and placing the current task and latest tool output at the bottom (recency zone). Everything in between is expendable working memory. Instead of hoping important information survives the middle of a bloated conversation log, you guarantee it lands where the model actually looks.

This is the difference between treating context as "a conversation log" and treating it as "a dynamically assembled working set."

### Strategy 6: Context-Aware Architecture Design

Design your agent system to minimize context pressure from the start. **Narrow tool outputs** means configuring tools to return minimal output — a test runner that returns only failures (not full pass/fail logs) saves thousands of tokens. **Pagination** means returning paginated results for large result sets (search, file listings) and letting the agent request more only if needed. **Structured over verbose** means returning JSON or structured data instead of human-readable narratives, since structured data is easier to compress and easier for models to parse. **Time-bounded sessions** means setting a context budget alarm (e.g., at 50% utilization) that triggers the agent to wrap up or delegate remaining work.

## Course Summary

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

## Key Takeaways

- Context management has `malloc` but no `free`. The default is to leak.
- Compaction is lossy and non-deterministic — the model decides what to discard. Auto-compact fires at ~95% capacity; CLAUDE.md survives because it's re-injected from disk.
- Prevention (sub-agents) beats cure (compaction). Observation masking beats LLM summarization.
- When you must compact, use priority-based eviction — protect critical context, keep failed actions visible.
- All strategies map to four primitives: Write, Select, Compress, Isolate.
- Emerging patterns (RAG, semantic caching, structured stores) offer alternatives to the linear messages array.

## References

- Kernighan, B. & Ritchie, D. (1988). *The C Programming Language*, 2nd Ed. The `malloc`/`free` analogy originates here.
- Lewis, P., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." arXiv:2005.11401. https://arxiv.org/abs/2005.11401
- Packer, C., et al. (2023). "MemGPT: Towards LLMs as Operating Systems." arXiv:2310.08560. https://arxiv.org/abs/2310.08560
- Anthropic. "Compaction." https://platform.claude.com/docs/en/build-with-claude/compaction
- Anthropic. "Effective Context Engineering for AI Agents." https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Manus. "Context Engineering for AI Agents: Lessons from Building Manus." https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- JetBrains Research. (2025). "Efficient Context Management for Coding Agents." https://blog.jetbrains.com/research/2025/12/efficient-context-management/
- Martin, L. (2025). "Context Engineering for Agents." https://rlancemartin.github.io/2025/06/23/context_engineering/
