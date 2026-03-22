# Module 6: Message Passing — The Erlang OTP of AI

## Lesson 6.1: Context Windows Are Actors

Erlang, created by Ericsson in the 1980s for telecom systems, introduced a powerful concurrency model known as the **Erlang OTP actor model**. In this model, **processes** (actors) are lightweight and isolated — they share nothing. **Communication** happens exclusively through message passing, with no shared memory. Processes can spawn child processes, creating hierarchies. And failure is expected — processes crash, and supervisors restart them. This model has powered systems achieving 99.9999999% uptime (the "nine nines" — notably Ericsson's AXD 301 ATM switch).

### The Mapping to AI Agents

| Erlang/OTP | AI Agents |
|------------|-----------|
| Process | Context window |
| Process mailbox | Messages array / prompt |
| Message passing | Task description → result summary |
| No shared memory | Each context window is isolated |
| Spawn a child process | Launch a sub-agent |
| Process state | Accumulated context within a session |
| Process crash | Context window exceeds smart zone / errors out |
| Supervisor | Parent agent that manages sub-agents |

This analogy matters because Erlang solved the same fundamental problem 40 years ago — how do you build reliable systems from unreliable components that can't share state? The answer: isolate them, let them communicate through messages, and design for failure.

The "no shared memory" constraint is real. Two context windows cannot share state. There is no global variable, no shared database they both see in real-time. The only way to move information between context windows is to explicitly send it — just like Erlang processes. This constraint, while it feels limiting, is actually what makes the system reliable.

Data transfer between agents follows **copy semantics**. When you send data to a sub-agent, you're copying it. The sub-agent gets its own version. If the sub-agent modifies its understanding, the parent doesn't know unless the sub-agent explicitly sends back a message. This is exactly how Erlang works: messages are copied, never referenced.

## Lesson 6.2: Designing the Message Protocol

The **inbound message** (parent to sub-agent) is the sub-agent's prompt — the task description. Design it like an API contract.

**Bad message** (vague, will produce unpredictable results):
```
Look at the code and fix any issues.
```

**Good message** (specific contract):
```
Task: Run the test suite for the auth module.
Command: npm test -- --testPathPattern=auth
Return format:
  - Total tests: <number>
  - Passed: <number>
  - Failed: <number>
  - For each failure: test name, expected vs actual, file:line
  - Do NOT include passing test details
```

The **outbound message** (sub-agent to parent) is the return value. Design for minimum tokens, maximum signal.

**Bad return** (process-focused, verbose):
```
First I ran npm test and saw that there were some failures.
I looked at the output and found that three tests failed.
The first failure was in test_login where...
[500 tokens of narration]
```

**Good return** (results-focused, structured):
```
Total: 47 | Passed: 44 | Failed: 3

Failures:
1. test_login_expired_token - Expected: 401, Got: 500 (src/auth.test.ts:42)
2. test_refresh_missing_header - Expected: 400, Got: undefined (src/auth.test.ts:78)
3. test_signup_duplicate - Expected: 409, Got: 200 (src/auth.test.ts:103)
```

### Protocol Design Principles

Four principles govern good message protocol design:

1. **Specify the return format in the inbound message**: Don't hope the sub-agent returns what you need. Tell it exactly what format to use.
2. **Results, not narration**: The parent needs data, not a story about how the sub-agent got the data.
3. **Failure information over success details**: If everything passed, a one-liner is sufficient. Detail the failures.
4. **Structured over prose**: Structured formats (lists, tables, key-value pairs) are easier for the parent model to parse and reason about.

### The todo.md Attention Manipulation Pattern

Manus discovered a powerful technique for maintaining coherence during long agent runs (~50+ tool calls). Their agents create and continuously update a `todo.md` file throughout execution — checking off completed items and adding new ones as the task evolves. This pushes current objectives into the model's most recent attention span, directly combating the lost-in-the-middle problem. The filesystem serves as what Manus calls "unlimited, persistent, and directly operable" extended context. It's a message the agent sends to its future self, using the filesystem as the medium.

### The "Agent as Tool" Mental Model

Phil Schmid offers an alternative framing: rather than thinking of sub-agents as members of an org chart ("the architect agent talks to the coder agent"), treat them as deterministic function calls: `call_planner(goal="...")`. Harness frameworks like Hugging Face's smolagents spin up a temporary sub-agent loop, let it run, and return structured output that's immediately usable by the caller — no different from calling any other tool. This mental model keeps the protocol clean: input in, output out, no ongoing relationship or state to manage.

The sub-agent's system prompt can formalize the protocol directly:

```
You are a test runner agent. Execute the requested tests and return
results in this exact format:

SUMMARY: <total> tests, <passed> passed, <failed> failed
FAILURES:
- <test_name>: <expected> vs <actual> (<file>:<line>)
NOTES: <any relevant observations, max 2 sentences>
```

## Lesson 6.3: Supervision and Failure

Erlang's **"let it crash" philosophy** says: don't write defensive code to prevent every possible failure inside a process. Instead, let processes crash and have supervisors that detect the crash and restart the process. This produces simpler, more reliable code than trying to handle every edge case.

Applied to AI agents, sub-agents can fail in several ways: they exceed their context window, they hallucinate and produce wrong results, they get stuck in loops, the API call errors out (rate limit, timeout, etc.), or they misunderstand the task.

### Supervision Strategies

Borrowing from Erlang OTP, there are three core supervision strategies.

**one_for_one**: If a sub-agent fails, restart just that sub-agent. This is the simplest and most common strategy.

```
Parent delegates: "Run auth tests"
Sub-agent fails (timeout)
Parent response: Spawn new sub-agent, same task
```

**one_for_all**: If one sub-agent fails, restart all sub-agents. Use this when sub-agents' work is interdependent.

```
Parent delegates: "Build frontend" + "Build backend" (in parallel)
Frontend sub-agent fails
Parent response: Restart both (backend may depend on frontend decisions)
```

**rest_for_one**: If a sub-agent fails, restart it and all sub-agents that were started after it. Use this when there's a sequential dependency.

### Practical Supervision in AI Agents

The simplest supervisor pattern is **retry with the same prompt**. This often works because LLM outputs are non-deterministic — the same prompt may succeed on retry. If the sub-agent failed because of ambiguity, **retry with a modified prompt** to clarify the task. If retries fail, **escalate to the parent**, which can try a different approach entirely. In all cases, set a **retry budget** — typically 2-3 attempts maximum — to avoid infinite loops.

### Supervision Trees

Just as Erlang builds hierarchies of supervisors, complex agent systems can build hierarchies:

```
Orchestrator (top-level)
├── Feature Agent (supervisor)
│   ├── Code Writer (worker)
│   ├── Test Runner (worker)
│   └── Reviewer (worker)
├── Feature Agent (supervisor)
│   ├── Code Writer (worker)
│   └── Test Runner (worker)
└── Integration Test Agent (worker)
```

Each supervisor manages its workers. If a worker fails, the supervisor handles it. If the supervisor can't handle it, it escalates to the orchestrator.

The most important property of this architecture is **failure isolation**: a sub-agent's failure doesn't corrupt the parent's context. If a sub-agent hallucinates wildly, those hallucinations exist only in the sub-agent's context window. The parent sees only the result message (or the failure signal).

## Key Takeaways

- Context windows map directly to Erlang actors: isolated processes communicating through messages.
- Design explicit message protocols — specify input format AND output format.
- Results-focused returns beat narration. Structure beats prose.
- "Let it crash" applies: design for sub-agent failure with retry and supervision strategies.
- Failure isolation is the key benefit — a sub-agent's problems don't infect the parent's context.

## References

- Armstrong, J. (2003). *Making Reliable Distributed Systems in the Presence of Software Errors*. PhD Thesis. (The definitive Erlang/OTP reference.)
- Armstrong, J. (2007). *Programming Erlang: Software for a Concurrent World*. Pragmatic Bookshelf.
- Erlang/OTP Design Principles: https://www.erlang.org/doc/system/design_principles
- Hewitt, C., Bishop, P., & Steiger, R. (1973). "A Universal Modular ACTOR Formalism for Artificial Intelligence." IJCAI.
- Agha, G. (1986). *Actors: A Model of Concurrent Computation in Distributed Systems*. MIT Press.
- Manus. "Context Engineering for AI Agents." https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- Schmid, P. (2025). "Context Engineering Part 2." https://www.philschmid.de/context-engineering-part-2
