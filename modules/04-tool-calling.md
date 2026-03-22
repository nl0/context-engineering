# Module 4: Dynamic Allocation — Tool Calling

← [Module 3: Anatomy of the Messages Array](./03-messages-array.md) | [Module 5: The Ralph Wiggum Loop →](./05-ralph-wiggum-loop.md)

---

## Lesson 4.1: Tool Calls as Memory Allocations

**The analogy**: If the messages array is memory, then every tool call is a `malloc()`. Each tool interaction adds at minimum three entries to the array:

1. The assistant's message containing the tool call (the function name + arguments)
2. The tool result (returned by your application)
3. The assistant's response interpreting the result

**Token cost anatomy of a single tool call cycle**:

```
Assistant decides to call a tool:
  "I'll read the file src/auth.ts"
  → ~50-100 tokens (reasoning + tool_use block)

Tool call payload:
  {"name": "read_file", "input": {"path": "src/auth.ts"}}
  → ~30-50 tokens

Tool result (the file contents):
  → 200-5,000+ tokens (depends entirely on what comes back)

Assistant processes the result:
  "The auth module exports three functions..."
  → 100-500 tokens
```

**Total for one tool call: 400-6,000+ tokens.**

A single file read can consume as many tokens as the entire system prompt.

**The accumulation problem**: Tool results are append-only. Once a 3,000-token file is read into context, it stays there for the rest of the session. Read 10 files? That's potentially 30,000 tokens of file content that persists in your context forever (within that session).

**Visualizing array growth** during a typical interaction:

```
[system]                            → 1,500 tokens  (cumulative: 1,500)
[harness]                           → 3,000 tokens  (cumulative: 4,500)
[user: "Fix the login bug"]         → 20 tokens     (cumulative: 4,520)
[assistant: "Let me look..."]       → 100 tokens    (cumulative: 4,620)
[tool_call: search_code]            → 80 tokens     (cumulative: 4,700)
[tool_result: 15 matches]           → 2,000 tokens  (cumulative: 6,700)
[assistant: "Found it, reading..."] → 150 tokens    (cumulative: 6,850)
[tool_call: read_file]              → 50 tokens     (cumulative: 6,900)
[tool_result: file contents]        → 4,000 tokens  (cumulative: 10,900)
[assistant: "I see the bug..."]     → 300 tokens    (cumulative: 11,200)
[tool_call: edit_file]              → 200 tokens    (cumulative: 11,400)
[tool_result: "success"]            → 30 tokens     (cumulative: 11,430)
[assistant: "Fixed. Let me test"]   → 100 tokens    (cumulative: 11,530)
[tool_call: run_tests]              → 50 tokens     (cumulative: 11,580)
[tool_result: test output]          → 8,000 tokens  (cumulative: 19,580)
[assistant: "All tests pass."]      → 80 tokens     (cumulative: 19,660)
```

In just one bug fix cycle: ~15,000 tokens of dynamic context consumed. That's ~22% of a 68K effective budget (from [Module 2's](./02-context-window-size.md) calculation) — gone in one task.

## Lesson 4.2: A Real Agent Session

A realistic multi-task session. What happens when an agent handles a more complex request — say, "Add user authentication to this Express app":

**Phase 1: Understanding** (exploring codebase)
- Search for existing auth patterns → 2,000 tokens
- Read package.json → 800 tokens
- Read app.ts → 3,000 tokens
- Read existing middleware → 2,500 tokens

Running total: ~8,300 new tokens

**Phase 2: Implementation** (writing code)
- Create auth middleware → 500 tokens (tool call + result)
- Create user model → 400 tokens
- Update routes → 600 tokens
- Create login endpoint → 500 tokens

Running total: ~10,300 new tokens

**Phase 3: Testing** (running and fixing tests)
- Run tests → 5,000 tokens of output
- Read error details → 2,000 tokens
- Fix test → 300 tokens
- Re-run tests → 5,000 tokens of output
- Another fix → 300 tokens
- Re-run tests → 5,000 tokens of output

Running total: ~28,200 new tokens

**Phase 4: Cleanup** (the model is now deep in context)
- Update README → 500 tokens
- Final test run → 5,000 tokens

Running total: ~33,700 new tokens

**Total context at end**: ~12,000 (fixed: system + harness + project context + tools) + 33,700 (dynamic) = **~45,700 tokens**. Still in the smart zone for a 200K model, but only for a single feature addition. Two or three more tasks in the same session, and you're in the dumb zone.

**Where context pressure hits hardest**: Test output. Notice that testing alone consumed ~20,000 tokens — more than half the session's dynamic context. Each test run dumps its full output into the array. This is the #1 context pressure point in agent sessions. ([Module 6](./06-sub-agents.md) introduces the solution: sub-agents for test running.)

**Signs of session degradation**:

1. The agent re-reads files it already read
2. It forgets constraints you stated earlier
3. Tool calls become less precise (searching broadly instead of targeted reads)
4. It starts apologizing and "trying again" without changing approach
5. Code quality drops — more bugs, less coherent architecture

**The reset decision**: When you notice these signs, the most productive action is often to start a new session, not to "remind" the agent. Reminding adds more tokens to an already-stressed context. Starting fresh (with a well-designed spec) gives the model a clean smart zone to work in. This is the bridge to [Module 5](./05-ralph-wiggum-loop.md).

## Key Takeaways

- Every tool call is a memory allocation — it grows the context permanently within a session.
- A single file read can cost 3,000-5,000 tokens. Test output is the #1 context hog.
- A typical agent session for one feature can consume 30,000-50,000 tokens of dynamic context.
- Context pressure shows up as degraded behavior: repetition, forgotten instructions, imprecise tool use.
- The solution isn't "more context" — it's fresh context with the right state carried forward.

## References

- Anthropic. "Tool Use (Function Calling) Documentation." https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- OpenAI. "Function Calling Guide." https://platform.openai.com/docs/guides/function-calling
- Schick, T., et al. (2023). "Toolformer: Language Models Can Teach Themselves to Use Tools." arXiv:2302.04761.
- Patil, S., et al. (2023). "Gorilla: Large Language Model Connected with Massive APIs." arXiv:2305.15334.

---

← [Module 3: Anatomy of the Messages Array](./03-messages-array.md) | [Module 5: The Ralph Wiggum Loop →](./05-ralph-wiggum-loop.md)
