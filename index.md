# Context Engineering

> Master the art of managing what goes into a language model's context window — from tokens and system prompts to tool calls and memory strategies.

**Source:** [latentpatterns.com/courses/context-engineering](https://latentpatterns.com/courses/context-engineering)

---

## Who This Course Is For

Software developers, ML engineers, and architects who build applications on top of LLMs — especially agent-based systems. You should be comfortable with API calls to language models and have experience (even brief) with tools like Claude Code, Cursor, Copilot, or LangChain.

## What You'll Learn

The context window is the single most important resource in any LLM application. It determines what the model knows, how well it reasons, and when it fails. Most developers treat it as a black box. This course treats it as a system to be engineered.

By the end, you'll be able to:

- Calculate the real (not advertised) context budget for any model
- Design system prompts, project context, and tool sets for maximum signal-per-token
- Architect agent systems that stay in the "smart zone" across long sessions
- Use sub-agents, message passing, and fresh-context patterns to scale beyond single-window limits
- Apply memory management principles from systems programming to context management

---

## Course Modules

### Part I: Foundations

| Module | Topic | Lessons |
|--------|-------|---------|
| [**1. Tokens and Inference**](./modules/01-tokens-and-inference.md) | How LLMs consume text and why inference is stateless | 1.1 What Are Tokens? · 1.2 Inference Is Stateless |
| [**2. The Real Size of Your Context Window**](./modules/02-context-window-size.md) | Why advertised context lengths are marketing, not engineering | 2.1 Marketing vs. Reality · 2.2 Why Models Fail at Length · 2.3 The Smart Zone and the Dumb Zone · 2.4 Measuring Your Context Budget |

### Part II: The Messages Array

| Module | Topic | Lessons |
|--------|-------|---------|
| [**3. Anatomy of the Messages Array**](./modules/03-messages-array.md) | The slot-by-slot structure of what goes into context | 3.1 System Prompt · 3.2 Harness Prompt · 3.3 Project Context Files · 3.4 MCP Servers and Tools · 3.5 Your Prompt |
| [**4. Dynamic Allocation — Tool Calling**](./modules/04-tool-calling.md) | How tool calls grow context and what it costs | 4.1 Tool Calls as Memory Allocations · 4.2 A Real Agent Session |

### Part III: Scaling Patterns

| Module | Topic | Lessons |
|--------|-------|---------|
| [**5. The Ralph Wiggum Loop**](./modules/05-ralph-wiggum-loop.md) | Fresh-context iteration for autonomous coding | 5.1 What Is the Ralph Wiggum Loop? · 5.2 Specs and Plans · 5.3 Three Modes of Ralph |
| [**6. Sub-Agents — Managed Runtimes for AI**](./modules/06-sub-agents.md) | Context isolation through disposable child windows | 6.1 Not About Personas · 6.2 The Test Runner Problem · 6.3 Designing Sub-Agent Boundaries |

### Part IV: Architecture

| Module | Topic | Lessons |
|--------|-------|---------|
| [**7. Message Passing — The Erlang OTP of AI**](./modules/07-message-passing.md) | Context windows as actors with message-passing semantics | 7.1 Context Windows Are Actors · 7.2 Designing the Message Protocol · 7.3 Supervision and Failure |
| [**8. Context Management Strategies**](./modules/08-context-management.md) | Memory management for LLMs — allocation, compaction, and beyond | 8.1 The malloc Without free · 8.2 Why Compaction Is Dangerous · 8.3 Better Strategies |

---

## The Central Insight

Treat the context window as you would treat memory in a systems programming language: **a finite, precious resource that requires deliberate management.**

The techniques in this course — from token budgeting to sub-agent isolation to supervision trees — are the context engineering equivalent of the memory management discipline that separates reliable systems from fragile ones.

---

## How to Read This Course

- **Sequential**: Modules build on each other. Module 1's token economics inform Module 2's budget calculations, which inform Module 3's slot analysis, and so on.
- **Reference**: Each module is self-contained enough to revisit independently. Cross-references link to prerequisite concepts.
- **Practical**: Every concept is tied to concrete numbers, real examples, and actionable patterns. No theory without application.

---

## References and Further Reading

### Papers
- Hsieh, C.-P., et al. (2024). "RULER: What's the Real Context Size of Your Long-Context Language Models?" [arXiv:2404.06654](https://arxiv.org/abs/2404.06654)
- Liu, N. F., et al. (2023). "Lost in the Middle: How Language Models Use Long Contexts." [arXiv:2307.03172](https://arxiv.org/abs/2307.03172)
- Sennrich, R., Haddow, B., & Birch, A. (2016). "Neural Machine Translation of Rare Words with Subword Units." ACL 2016.
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
- Huntley, G. (2025). ["Ralph Wiggum as a 'Software Engineer.'"](https://ghuntley.com/ralph/)
- Manus. (2025). ["Context Engineering for AI Agents."](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- Cognition. (2025). ["Don't Build Multi-Agents."](https://cognition.ai/blog/dont-build-multi-agents)
- Martin, L. (2025). ["Context Engineering for Agents."](https://rlancemartin.github.io/2025/06/23/context_engineering/)

### Tools and Documentation
- [Anthropic — Claude API Documentation](https://docs.anthropic.com)
- [Anthropic — Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Anthropic — Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [OpenAI — Tokenizer](https://platform.openai.com/tokenizer)
- [OpenAI — tiktoken](https://github.com/openai/tiktoken)
- [Google — SentencePiece](https://github.com/google/sentencepiece)
