# Module 3: Anatomy of the Messages Array

← [Module 2: The Real Size of Your Context Window](./02-context-window-size.md) | [Module 4: Dynamic Allocation — Tool Calling →](./04-tool-calling.md)

---

This module walks through the messages array slot by slot, from index 0 to the end. Think of it as a memory layout — each slot has a purpose and a cost.

## Lesson 3.1: Slot 0 — The System Prompt

- **What it is**: The model's standing instructions — who it is, how it should behave, what constraints apply. In OpenAI's API, this is a message with `role: "system"` (or `role: "developer"` in newer models). In Anthropic's Claude API, it's a top-level `system` parameter separate from the messages array. Either way, it occupies the same conceptual slot: the first thing the model sees.

- **Why it matters**: The system prompt occupies the most privileged position in context. Due to primacy effects (attention is strongest at the start), the system prompt has outsized influence on model behavior compared to the same text placed later.

- **Anatomy of an effective system prompt**:
  - Identity and role (1-2 sentences)
  - Core behavioral constraints (what to do and not do)
  - Output format specifications
  - Domain-specific knowledge or rules
  - Keep it tight. Every token here is paid on every request.

- **Cost awareness**: A 2,000-token system prompt on a model charging $3/M input tokens, across 1,000 API calls = $6 just for the system prompt. In agent workloads with hundreds of calls per session, system prompt bloat is real cost.

- **Common anti-patterns**:
  - Repeating the same instruction 3 different ways "for emphasis" (wastes tokens, doesn't help)
  - Including examples that could be retrieved on-demand instead
  - Stuffing knowledge that should be in a retrieval system

## Lesson 3.2: Slot 1 — The Harness Prompt

- **What it is**: When you use an agent framework or tool (Claude Code, Cursor, Copilot, LangChain, etc.), the framework injects its own instructions into the messages array. This is the harness prompt. You typically don't see it, but it's consuming your context.

- **What it contains** (typical):
  - Tool usage instructions ("To read a file, use the Read tool...")
  - Safety constraints and behavioral rules
  - Output formatting requirements
  - Environment descriptions (OS, working directory, available tools)
  - Can range from 1,000 to 8,000+ tokens depending on the framework

- **The trade-off**: Off-the-shelf harnesses (Claude Code, Cursor) provide robust, well-tested harness prompts but you can't control their token cost. Custom agent implementations let you optimize the harness but require more engineering.

- **Why you should care**: The harness prompt is a "hidden tax" on your context budget. If you're building a custom agent and your harness is 5,000 tokens, that's 5,000 tokens you can't use for actual work on every single call. Audit it. Measure it. Trim it.

- **How to inspect it**: Most frameworks don't expose the harness prompt directly. Techniques:
  - Ask the model "What are your system instructions?" (unreliable)
  - Intercept API calls with a proxy
  - Read the framework's source code (for open-source tools)
  - Check token usage — if your prompt is 100 tokens but the API reports 3,000 input tokens, the harness is the difference

## Lesson 3.3: Slot 2 — AGENTS.md (Project Context)

- **What it is**: Project-specific context files (CLAUDE.md, AGENTS.md, .cursorrules, .github/copilot-instructions.md) that are automatically discovered and injected into context. They tell the model about your specific project — conventions, architecture, key patterns.

- **The discovery hierarchy** (Claude Code example):
  1. `~/.claude/CLAUDE.md` — user-level defaults
  2. `./CLAUDE.md` — project root
  3. `./src/CLAUDE.md` — subdirectory overrides
  These get concatenated and injected into the messages array.

- **Signal-per-token optimization**: This is the most important concept for project context files. Every token must carry maximum information. Compare:

  Bad (47 tokens):
  ```
  When working on this project, please make sure to always use TypeScript
  instead of JavaScript. We prefer TypeScript because it provides better
  type safety and developer experience.
  ```

  Good (9 tokens):
  ```
  Use TypeScript. Never plain JavaScript.
  ```

  Same instruction. 5x fewer tokens. The model understands both equally well.

- **What to include**:
  - Tech stack and key dependencies (with versions that matter)
  - File/folder structure conventions
  - Testing patterns and commands
  - Common gotchas specific to this codebase
  - Architecture decisions the model needs to respect

- **What NOT to include**:
  - Information the model can discover by reading files
  - Generic best practices the model already knows
  - Long examples (use references to files instead)
  - Anything that rarely applies (retrieve on-demand instead)

## Lesson 3.4: Slot 3 — MCP Servers and Agent Skills

- **What MCP (Model Context Protocol) is**: A standard protocol for exposing tools (functions the model can call) and resources (data the model can read) to LLMs. Tool definitions are JSON schemas that describe available functions, their parameters, and expected behavior.

- **The constant-allocation problem**: Tool definitions consume tokens on EVERY request, whether or not the tools are used. This is because the model needs to "know" what tools are available in order to decide when to call them.

  Typical tool definition sizes:
  - Simple tool (1-2 params): ~100-200 tokens
  - Medium tool (3-5 params): ~200-400 tokens
  - Complex tool (nested params, enums): ~400-800 tokens

  10 tools × 300 tokens avg = 3,000 tokens of fixed overhead.
  50 tools × 300 tokens avg = 15,000 tokens — that's a substantial chunk of your smart zone.

  **Real-world example** (from MCP token cost analysis): A developer setup with GitHub (35 tools), Slack (11 tools), Sentry (5 tools), and a few more MCP servers — 58 tools total — consumed ~55,000 tokens. That's ~28% of a 200K context window burned on tool schemas alone, before any conversation begins.

- **Eager vs. lazy loading**:
  - **Eager** (default in most frameworks): All tool definitions are included in every request. Simple, but wasteful if you have many tools and most are rarely used.
  - **Lazy loading**: Start with a minimal tool set. Provide a "discover tools" meta-tool that can load additional tool definitions on demand. Saves tokens but adds latency (extra round trip to discover tools before using them).
  - **Hybrid**: Eagerly load core tools (file read/write, search, execute). Lazy-load specialized tools (database, deployment, specific APIs).

- **Designing for token efficiency**:
  - Keep tool descriptions concise
  - Use clear, self-documenting parameter names instead of long descriptions
  - Avoid overly granular tools — fewer, more capable tools > many tiny ones
  - Consider: does this tool need to be available on every call, or just sometimes?

### A note on prompt caching

Fixed allocations (system prompt, harness, tools, project context) are paid on every request — but they don't have to cost full price. Both Anthropic and OpenAI offer **prompt caching**: if the beginning of your input matches a previous request, the cached portion is processed at a steep discount (Anthropic charges cached tokens at ~10% of uncached rate: $0.30/MTok vs $3/MTok for Sonnet).

This doesn't change the context engineering picture — cached tokens still consume context window space. But it dramatically reduces the dollar cost of fixed allocations. The practical implication: optimize your fixed context for signal-per-token (context window efficiency) but also for cache hit rate (cost efficiency). Keep the prefix of your messages array stable across calls — any change invalidates the cache from that point forward.

## Lesson 3.5: Slot 4 — Your Prompt

- **What's left**: After system prompt, harness, project context, and tool definitions are allocated, the remaining space is your actual context budget — for the user's prompt, conversation history, and tool results.

- **Calculating remaining budget** (revisited from [Module 2](./02-context-window-size.md)):
  ```
  Remaining = Smart zone budget − Slot 0 − Slot 1 − Slot 2 − Slot 3
  ```
  Using realistic numbers (a heavier tool setup than Module 2's example):
  ```
  Smart zone (200K × 0.4):    80,000 tokens
  System prompt:               −1,500
  Harness prompt:              −4,000
  Project context:             −1,500
  Tool definitions (20 tools): −6,000
  ────────────────────────────────────────
  Available for conversation:  67,000 tokens
  ```

- **Context-aware prompt design**: With 67,000 tokens of real budget, your initial user prompt matters:
  - A 500-token prompt leaves 66,500 for conversation and tool results
  - A 5,000-token prompt (pasting a large file inline) leaves 62,000
  - If your first prompt is 20,000 tokens (a whole codebase dump), you've used 30% of your budget before the first response

- **The golden rule**: Don't put in context what can be retrieved. Instead of pasting a file into your prompt, ask the agent to read it with a tool. The file still enters context, but only when needed, and you have the option to manage that allocation later.

## Key Takeaways

- The messages array is a memory layout with fixed and dynamic regions.
- Slots 0-3 (system prompt, harness, project context, tools) are fixed costs paid on every call.
- Signal-per-token is the design principle for all fixed-cost context.
- Tool definitions are surprisingly expensive — audit and optimize your tool set.
- Your actual budget for conversation is what's left after fixed allocations.

## References

- Anthropic. "Model Context Protocol (MCP) Specification." https://modelcontextprotocol.io/
- Anthropic. "Claude Code Documentation — CLAUDE.md." https://docs.anthropic.com/en/docs/claude-code
- Anthropic. "Prompt Caching." https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- Anthropic. "Effective Context Engineering for AI Agents." https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- OpenAI. "Function Calling Guide." https://platform.openai.com/docs/guides/function-calling
- Cursor. ".cursorrules Documentation." https://docs.cursor.com
- GitHub Copilot. "Customizing Copilot Instructions." https://docs.github.com/en/copilot/customizing-copilot
- MMNTM. "The MCP Tax: Hidden Costs of Model Context Protocol." https://www.mmntm.net/articles/mcp-context-tax

---

← [Module 2: The Real Size of Your Context Window](./02-context-window-size.md) | [Module 4: Dynamic Allocation — Tool Calling →](./04-tool-calling.md)
