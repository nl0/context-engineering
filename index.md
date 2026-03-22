# Context Engineering

> Master the art of managing what goes into a language model's context window — from tokens and system prompts to tool calls and memory strategies.

**Source:** [latentpatterns.com/courses/context-engineering](https://latentpatterns.com/courses/context-engineering)

---

## Who This Book Is For

Software developers, ML engineers, and architects who build applications on top of LLMs — especially agent-based systems. You should be comfortable with API calls to language models and have experience (even brief) with tools like Claude Code, Cursor, Copilot, or LangChain.

## Why "Context Engineering"?

The term was popularized in June 2025 by Tobi Lutke (Shopify CEO) — "the art of providing all the context for the task to be plausibly solvable by the LLM" — and Andrej Karpathy, who elaborated: "context engineering is the delicate art and science of filling the context window with just the right information for the next step." It supersedes "prompt engineering" because in production systems, the prompt is the least of your concerns. The real work is managing everything else that goes into context: tool definitions, retrieved documents, conversation history, project conventions, and compaction strategies.

## What You'll Learn

The context window is the single most important resource in any LLM application. It determines what the model knows, how well it reasons, and when it fails. Most developers treat it as a black box. This book treats it as a system to be engineered.

By the end, you'll be able to:

- Calculate the real (not advertised) context budget for any model
- Design system prompts, project context, and tool sets for maximum signal-per-token
- Architect agent systems that stay in the "smart zone" across long sessions
- Use sub-agents, message passing, and fresh-context patterns to scale beyond single-window limits
- Apply memory management principles from systems programming to context management

---

## Chapters

### Part I: Foundations

| Chapter | Topic | Sections |
|---------|-------|----------|
| [**1. Tokens and Inference**](./modules/01-tokens-and-inference.md) | How LLMs consume text and why inference is stateless | [What Are Tokens?](./modules/01-tokens-and-inference.md#what-are-tokens) <br>[Inference Is Stateless](./modules/01-tokens-and-inference.md#inference-is-stateless) |
| [**2. The Real Size of Your Context Window**](./modules/02-context-window-size.md) | Why advertised context lengths are marketing, not engineering | [Marketing vs. Reality](./modules/02-context-window-size.md#marketing-numbers-vs.-engineering-reality) <br>[Why Models Fail at Length](./modules/02-context-window-size.md#why-models-fail-at-length) <br>[The Smart Zone and the Dumb Zone](./modules/02-context-window-size.md#the-smart-zone-and-the-dumb-zone) <br>[Measuring Your Context Budget](./modules/02-context-window-size.md#measuring-your-context-budget) |

### Part II: The Messages Array

| Chapter | Topic | Sections |
|---------|-------|----------|
| [**3. Anatomy of the Messages Array**](./modules/03-messages-array.md) | The slot-by-slot structure of what goes into context | [System Prompt](./modules/03-messages-array.md#slot-0-the-system-prompt) <br>[Harness Prompt](./modules/03-messages-array.md#slot-1-the-harness-prompt) <br>[Project Context Files](./modules/03-messages-array.md#slot-2-project-context-files) <br>[MCP Servers and Tools](./modules/03-messages-array.md#slot-3-mcp-servers-and-agent-skills) <br>[Your Prompt](./modules/03-messages-array.md#slot-4-your-prompt) |
| [**4. Dynamic Allocation — Tool Calling**](./modules/04-tool-calling.md) | How tool calls grow context and what it costs | [Tool Calls as Memory Allocations](./modules/04-tool-calling.md#tool-calls-as-memory-allocations) <br>[A Real Agent Session](./modules/04-tool-calling.md#a-real-agent-session) |

### Part III: Scaling Patterns

| Chapter | Topic | Sections |
|---------|-------|----------|
| [**5. Sub-Agents — Managed Runtimes for AI**](./modules/05-sub-agents.md) | Context isolation through disposable child windows | [Not About Personas](./modules/05-sub-agents.md#sub-agents-are-not-about-personas) <br>[The Test Runner Problem](./modules/05-sub-agents.md#the-test-runner-problem) <br>[Designing Boundaries](./modules/05-sub-agents.md#designing-sub-agent-boundaries) |
| [**6. Message Passing — The Erlang OTP of AI**](./modules/06-message-passing.md) | Context windows as actors with message-passing semantics | [Context Windows Are Actors](./modules/06-message-passing.md#context-windows-are-actors) <br>[Designing the Message Protocol](./modules/06-message-passing.md#designing-the-message-protocol) <br>[Supervision and Failure](./modules/06-message-passing.md#supervision-and-failure) |

### Part IV: Architecture

| Chapter | Topic | Sections |
|---------|-------|----------|
| [**7. The Ralph Wiggum Loop**](./modules/07-ralph-wiggum-loop.md) | Crash-only agent design — fresh-context iteration for autonomous coding | [What Is It?](./modules/07-ralph-wiggum-loop.md#what-is-the-ralph-wiggum-loop) <br>[The Three-Phase Funnel](./modules/07-ralph-wiggum-loop.md#the-three-phase-funnel) <br>[Specs and Plans](./modules/07-ralph-wiggum-loop.md#specs-and-plans-the-persistent-memory) <br>[Backpressure](./modules/07-ralph-wiggum-loop.md#backpressure-and-guardrails) <br>[Greenfield vs. Brownfield](./modules/07-ralph-wiggum-loop.md#greenfield-vs.-brownfield) <br>[Failure Modes](./modules/07-ralph-wiggum-loop.md#failure-modes-and-criticisms) |
| [**8. Context Management Strategies**](./modules/08-context-management.md) | Memory management for LLMs — allocation, compaction, and beyond | [The malloc Without free](./modules/08-context-management.md#the-malloc-without-free) <br>[Why Compaction Is Dangerous](./modules/08-context-management.md#why-compaction-is-dangerous) <br>[Better Strategies](./modules/08-context-management.md#better-strategies) |

---

## The Central Insight

Treat the context window as you would treat memory in a systems programming language: **a finite, precious resource that requires deliberate management.**

The techniques in this book — from token budgeting to sub-agent isolation to supervision trees — are the context engineering equivalent of the memory management discipline that separates reliable systems from fragile ones.

---

## How to Read This Book

- **Sequential**: Chapters build on each other. Chapter 1's token economics inform Chapter 2's budget calculations, which inform Chapter 3's slot analysis, and so on.
- **Reference**: Each chapter is self-contained enough to revisit independently. Cross-references link to prerequisite concepts.
- **Practical**: Every concept is tied to concrete numbers, real examples, and actionable patterns. No theory without application.
- **PDF**: The full book is available as a [PDF download](/Context-Engineering.pdf) for offline reading.

---

## Credits

Written by [Claude](https://claude.ai) (Anthropic), directed and edited by a human author. Outline from [Latent Patterns](https://latentpatterns.com/courses/context-engineering). See [publication history](history.md) for details.

Licensed under [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

---

## References and Further Reading

### Papers
- Hsieh, C.-P., et al. (2024). "RULER: What's the Real Context Size of Your Long-Context Language Models?" [arXiv:2404.06654](https://arxiv.org/abs/2404.06654)
- Liu, N. F., et al. (2023). "Lost in the Middle: How Language Models Use Long Contexts." [arXiv:2307.03172](https://arxiv.org/abs/2307.03172)
- Lewis, P., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." [arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
- Packer, C., et al. (2023). "MemGPT: Towards LLMs as Operating Systems." [arXiv:2310.08560](https://arxiv.org/abs/2310.08560)
- Paulsen, T. (2025). "Context Is What You Need: The Maximum Effective Context Window." [arXiv:2509.21361](https://arxiv.org/abs/2509.21361)
- Chroma Research. (2025). "Context Rot." [research.trychroma.com/context-rot](https://research.trychroma.com/context-rot)

### Books
- Armstrong, J. (2007). *Programming Erlang: Software for a Concurrent World*. Pragmatic Bookshelf.
- Kernighan, B. & Ritchie, D. (1988). *The C Programming Language*, 2nd Ed. Prentice Hall.
- Brooks, F. (1975). *The Mythical Man-Month*. Addison-Wesley.

### Articles and Blog Posts
- Anthropic. (2025). ["Effective Context Engineering for AI Agents."](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Anthropic. (2025). ["How We Built Our Multi-Agent Research System."](https://www.anthropic.com/engineering/multi-agent-research-system)
- Huntley, G. (2025). ["Ralph Wiggum as a 'Software Engineer.'"](https://ghuntley.com/ralph/)
- Farr, C. (2025). ["The Ralph Wiggum Playbook."](https://paddo.dev/blog/ralph-wiggum-playbook/)
- Manus. (2025). ["Context Engineering for AI Agents."](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- Cognition. (2025). ["Don't Build Multi-Agents."](https://cognition.ai/blog/dont-build-multi-agents)
- Schmid, P. (2025). ["Single vs Multi-Agent System?"](https://www.philschmid.de/single-vs-multi-agents)
- Martin, L. (2025). ["Context Engineering for Agents."](https://rlancemartin.github.io/2025/06/23/context_engineering/)

### Tools and Documentation
- [Anthropic — Claude API Documentation](https://docs.anthropic.com)
- [Anthropic — Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Anthropic — Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [OpenAI — Tokenizer](https://platform.openai.com/tokenizer)
- [OpenAI — tiktoken](https://github.com/openai/tiktoken)
- [Google — SentencePiece](https://github.com/google/sentencepiece)
