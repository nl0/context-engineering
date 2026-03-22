---
layout: default
title: "5. Sub-Agents"
nav_order: 5
---

# Module 5: Sub-Agents — Managed Runtimes for AI

## Lesson 5.1: Sub-Agents Are Not About Personas

When people hear "multi-agent," they typically think of role-playing — "one agent is the architect, another is the coder, another is the reviewer." This is the wrong mental model. Personas are a prompt engineering trick. Sub-agents solve a systems engineering problem.

**What sub-agents actually are**: a sub-agent is a separate context window that runs independently, does work, and returns a result to the parent. The parent's context is protected from the sub-agent's internal work. Think of it as a function call in programming:

```
Parent context: "Run the tests and tell me if they pass."

Sub-agent context (separate window):
  - Receives: "Run the tests"
  - Executes: runs test suite
  - Sees: 50,000 tokens of test output
  - Returns: "All 47 tests pass. 3 were skipped (reason: ...)."

Parent context receives: the 50-token summary, NOT the 50,000-token output
```

The analogy that best captures this is managed runtimes or containers. Each sub-agent gets its own isolated memory (context window), runs its workload, and communicates only through well-defined interfaces (the prompt in, the result out). The parent is like the orchestrator — it delegates work and collects results.

This matters enormously for context engineering. Without sub-agents, every operation's full output enters the parent's context and stays there. With sub-agents, the parent only pays for the summary. This is the single most effective technique for extending how much work an agent can do in a session.

## Lesson 5.2: The Test Runner Problem

Consider the problem in concrete terms: running a test suite from an agent session.

**Without sub-agent**:
```
Parent context before test: 25,000 tokens
Test output added to context: +15,000 tokens
Parent context after test:  40,000 tokens

Tokens consumed for the test information: 15,000
Tokens the parent actually needs: ~200 (pass/fail + summary)
Waste: 14,800 tokens (98.7%)
```

**With sub-agent**:
```
Parent context before test: 25,000 tokens
Sub-agent runs tests internally (its own 15,000 tokens — separate window)
Sub-agent returns summary: +200 tokens
Parent context after test:  25,200 tokens

Tokens consumed in parent: 200
Savings: 14,800 tokens
```

Over 3 test runs in a session, that's 44,400 tokens saved. That's the difference between staying in the smart zone and entering the dumb zone.

This follows a **"schedule-a-future" pattern** — think of sub-agent delegation as scheduling a future/promise:

1. Parent creates a task description (the "promise")
2. Sub-agent resolves the promise (does the work)
3. Parent receives the resolved value (the summary)

The parent doesn't need to know HOW the work was done — just the result.

Test running is just the canonical example. Other high-token operations benefit from sub-agent delegation in the same way. **Large file analysis** — "Read these 5 files and tell me which ones handle authentication" — lets the sub-agent read all files while the parent gets just a list. **Code search** — "Find all usages of the deprecated API" — lets the sub-agent search while the parent gets locations. **Documentation generation** — "Write docs for this module" — lets the sub-agent read code and write docs while the parent gets confirmation. **Dependency analysis** — "What are the security vulnerabilities in our dependencies?" — lets the sub-agent run the audit while the parent gets a summary.

## Lesson 5.3: Designing Sub-Agent Boundaries

The key question for delegation is: "Will this operation produce output I don't need verbatim in the parent context?" If yes, delegate to a sub-agent. If no — for example, a small file edit where you need to see the exact result — run it directly.

### The Delegation Decision Matrix

| Operation | Expected tokens | Need verbatim? | Decision |
|-----------|----------------|----------------|----------|
| Read a 50-line config file | ~500 | Yes (need to edit it) | Direct |
| Run test suite | 5,000-50,000 | No (need pass/fail) | Sub-agent |
| Search codebase for pattern | 2,000-10,000 | No (need locations) | Sub-agent |
| Edit a specific function | ~300 | Yes | Direct |
| Analyze 10 files for patterns | 10,000-50,000 | No (need findings) | Sub-agent |
| Read a single error log | ~200 | Maybe | Direct (small enough) |

### Designing the Message Interface

The **inbound message** (parent to sub-agent) should be specific about what you need back. "Run the tests and return: (1) pass/fail count, (2) names of any failing tests, (3) the error message for each failure." Don't just say "run the tests."

The **outbound message** (sub-agent to parent) should be results-focused, not process-focused. The parent doesn't need "First I read the file, then I noticed..." — it needs "3 tests failed: test_auth (missing token), test_login (timeout), test_signup (duplicate email)."

### The Overhead Trade-Off

Sub-agents aren't free. Each sub-agent pays the full fixed allocation cost (system prompt + harness + tools). There's latency overhead from spinning up a new context and making additional API calls. The parent needs tokens to describe the task and process the result.

Rule of thumb: sub-agents are worth it when the delegated operation would add 2,000+ tokens to the parent context that the parent doesn't need verbatim.

There is also a **token explosion risk** to consider. Sub-agents save tokens in the *parent* context, but they still consume tokens globally — and parallelism multiplies cost fast. Practitioners report hitting Claude Pro plan limits in as little as 15 minutes when running 5 parallel sub-agents. Anthropic documents that multi-agent workflows use 4-7x more tokens than single-agent approaches; full Agent Teams architectures can reach ~15x. Information flows only parent-to-child, never child-to-child — if two sub-agents need to coordinate, the parent must relay messages, adding further token cost on both sides.

On **nesting depth**: sub-agents can spawn their own sub-agents, but keep it shallow. Each level adds latency and fixed overhead. In practice, 2 levels (parent, child, grandchild) is usually the maximum useful depth.

### Read vs. Write: The Key Heuristic

The most useful heuristic for when multi-agent works comes from Phil Schmid: "The important distinction isn't single vs multi-agent... it is whether your task primarily involves reading or writing."

**Read tasks** (research, analysis, code review, search) parallelize well — sub-agents gather information independently and results combine naturally. Multi-agent shines here. **Write tasks** (code generation, document authoring, system design) create coordination nightmares — parallel writers make conflicting assumptions that an integrator can't reconcile. Single agent is usually better.

The data backs this up: Google/MIT research found that parallelized write tasks degraded performance by 39-70%, while parallelized read tasks improved performance by 80.9%.

### The Anti-Pattern Warning

Cognition, the team behind Devin, published "Don't Build Multi-Agents" — arguing that parallel sub-agents making independent decisions leads to conflicting implicit choices. Their recommendation: sub-agents should only handle **well-defined questions** (like "run these tests"), never substantive decision-making. Keep decision-making centralized in the parent. Use sub-agents for information gathering and execution, not for planning or architectural choices.

Cognition's **Flappy Bird example** makes this concrete: they asked parallel sub-agents to build the game. One sub-agent built a Mario-style background. Another built a bird that was visually and mechanically inconsistent with that background. The integrator agent couldn't reconcile the conflicting outputs. Root cause: "conflicting assumptions not prescribed upfront." The sub-agents each made reasonable but incompatible creative decisions — exactly the kind of implicit choice that can't be parallelized safely.

## Key Takeaways

- Sub-agents are about context isolation, not personas.
- The test runner problem is the canonical example: 15,000 tokens of test output becomes 200 tokens of summary.
- Delegate when the operation produces tokens the parent doesn't need verbatim.
- **Read tasks parallelize well; write tasks don't.** Use sub-agents for research, analysis, and search. Keep code generation and design decisions in the parent.
- Design explicit message contracts: be specific about what you need back.
- Sub-agents have real overhead (4-7x tokens for multi-agent) — use them when the token savings justify the cost.

## References

- Anthropic. "Claude Code — Sub-agents Documentation." https://code.claude.com/docs/en/sub-agents
- Cognition. "Don't Build Multi-Agents." https://cognition.ai/blog/dont-build-multi-agents
- Manus. "Context Engineering for AI Agents: Lessons from Building Manus." https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- Wu, Q., et al. (2023). "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." arXiv:2308.08155.
- Hong, S., et al. (2023). "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework." arXiv:2308.00352.
- Schmid, P. (2025). "Single vs Multi-Agent System?" https://www.philschmid.de/single-vs-multi-agents
- Google Research. (2025). "Towards a Science of Scaling Agent Systems." https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/
- Anthropic. "How We Built Our Multi-Agent Research System." https://www.anthropic.com/engineering/multi-agent-research-system
