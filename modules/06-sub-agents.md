# Module 6: Sub-Agents — Managed Runtimes for AI

← [Module 5: The Ralph Wiggum Loop](./05-ralph-wiggum-loop.md) | [Module 7: Message Passing — The Erlang OTP of AI →](./07-message-passing.md)

---

## Lesson 6.1: Sub-Agents Are Not About Personas

- **The common misconception**: When people hear "multi-agent," they think of role-playing — "one agent is the architect, another is the coder, another is the reviewer." This is the wrong mental model. Personas are a prompt engineering trick. Sub-agents solve a systems engineering problem.

- **What sub-agents actually are**: A sub-agent is a separate context window that runs independently, does work, and returns a result to the parent. The parent's context is protected from the sub-agent's internal work.

  Think of it as a function call in programming:
  ```
  Parent context: "Run the tests and tell me if they pass."

  Sub-agent context (separate window):
    - Receives: "Run the tests"
    - Executes: runs test suite
    - Sees: 50,000 tokens of test output
    - Returns: "All 47 tests pass. 3 were skipped (reason: ...)."

  Parent context receives: the 50-token summary, NOT the 50,000-token output
  ```

- **The analogy**: Sub-agents are like managed runtimes or containers. Each one gets its own isolated memory (context window), runs its workload, and communicates only through well-defined interfaces (the prompt in, the result out). The parent is like the orchestrator — it delegates work and collects results.

- **Why this matters for context engineering**: Without sub-agents, every operation's full output enters the parent's context and stays there. With sub-agents, the parent only pays for the summary. This is the single most effective technique for extending how much work an agent can do in a session.

## Lesson 6.2: The Test Runner Problem

- **The problem in concrete terms**: Consider running a test suite from an agent session.

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

- **The "schedule-a-future" pattern**: Think of sub-agent delegation as scheduling a future/promise:
  1. Parent creates a task description (the "promise")
  2. Sub-agent resolves the promise (does the work)
  3. Parent receives the resolved value (the summary)

  The parent doesn't need to know HOW the work was done — just the result.

- **Beyond test running**: Other high-token operations that benefit from sub-agent delegation:
  - **Large file analysis**: "Read these 5 files and tell me which ones handle authentication" — sub-agent reads all files, parent gets a list
  - **Code search**: "Find all usages of the deprecated API" — sub-agent searches, parent gets locations
  - **Documentation generation**: "Write docs for this module" — sub-agent reads code + writes docs, parent gets confirmation
  - **Dependency analysis**: "What are the security vulnerabilities in our dependencies?" — sub-agent runs audit, parent gets summary

## Lesson 6.3: Designing Sub-Agent Boundaries

- **When to delegate**: Ask: "Will this operation produce output I don't need verbatim in the parent context?"
  - If yes → delegate to sub-agent
  - If no → run directly (e.g., a small file edit where you need to see the exact result)

- **The delegation decision matrix**:
  | Operation | Expected tokens | Need verbatim? | Decision |
  |-----------|----------------|----------------|----------|
  | Read a 50-line config file | ~500 | Yes (need to edit it) | Direct |
  | Run test suite | 5,000-50,000 | No (need pass/fail) | Sub-agent |
  | Search codebase for pattern | 2,000-10,000 | No (need locations) | Sub-agent |
  | Edit a specific function | ~300 | Yes | Direct |
  | Analyze 10 files for patterns | 10,000-50,000 | No (need findings) | Sub-agent |
  | Read a single error log | ~200 | Maybe | Direct (small enough) |

- **Designing the message interface**:
  - **Inbound** (parent → sub-agent): Be specific about what you need back. "Run the tests and return: (1) pass/fail count, (2) names of any failing tests, (3) the error message for each failure." Don't just say "run the tests."
  - **Outbound** (sub-agent → parent): Results-focused, not process-focused. The parent doesn't need "First I read the file, then I noticed..." — it needs "3 tests failed: test_auth (missing token), test_login (timeout), test_signup (duplicate email)."

- **The overhead trade-off**: Sub-agents aren't free:
  - Each sub-agent pays the full fixed allocation cost (system prompt + harness + tools)
  - There's latency overhead (spinning up a new context, making additional API calls)
  - The parent needs tokens to describe the task and process the result

  Rule of thumb: sub-agents are worth it when the delegated operation would add 2,000+ tokens to the parent context that the parent doesn't need verbatim.

- **Nesting depth**: Sub-agents can spawn their own sub-agents, but keep it shallow. Each level adds latency and fixed overhead. In practice, 2 levels (parent → child → grandchild) is usually the maximum useful depth.

- **The anti-pattern warning** (Cognition/Devin): Cognition, the team behind Devin, published "Don't Build Multi-Agents" — arguing that parallel sub-agents making independent decisions leads to conflicting implicit choices. Their recommendation: sub-agents should only handle **well-defined questions** (like "run these tests"), never substantive decision-making. Keep decision-making centralized in the parent. Use sub-agents for information gathering and execution, not for planning or architectural choices.

## Key Takeaways

- Sub-agents are about context isolation, not personas.
- The test runner problem is the canonical example: 15,000 tokens of test output → 200 tokens of summary.
- Delegate when the operation produces tokens the parent doesn't need verbatim.
- Design explicit message contracts: be specific about what you need back.
- Sub-agents have overhead — use them when the token savings justify the cost (typically 2,000+ tokens).

## References

- Anthropic. "Claude Code — Sub-agents Documentation." https://code.claude.com/docs/en/sub-agents
- Cognition. "Don't Build Multi-Agents." https://cognition.ai/blog/dont-build-multi-agents
- Manus. "Context Engineering for AI Agents: Lessons from Building Manus." https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- Wu, Q., et al. (2023). "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." arXiv:2308.08155.
- Hong, S., et al. (2023). "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework." arXiv:2308.00352.

---

← [Module 5: The Ralph Wiggum Loop](./05-ralph-wiggum-loop.md) | [Module 7: Message Passing — The Erlang OTP of AI →](./07-message-passing.md)
