# Module 2: The Real Size of Your Context Window

← [Module 1: Tokens and Inference](./01-tokens-and-inference.md) | [Module 3: Anatomy of the Messages Array →](./03-messages-array.md)

---

## Lesson 2.1: Marketing Numbers vs. Engineering Reality

**The gap**: Model providers advertise context windows of 128K, 200K, 1M, even 10M tokens. These numbers represent the theoretical maximum input the model can accept. They do not represent the context size at which the model performs well.

**Needle-in-a-haystack (NIAH) tests**: The most common benchmark — hide a specific fact in a long document, ask the model to retrieve it. Models score near-perfect on these tests at their full advertised context lengths. But NIAH is misleading: it only tests single-fact retrieval from a mostly irrelevant context. Real tasks require reasoning over multiple pieces of information scattered throughout context.

**The RULER benchmark** (Hsieh et al., 2024): A much more rigorous test. Four categories:

1. **Single retrieval (NIAH)**: Find one needle — models do well
2. **Multi-key retrieval**: Find multiple needles — performance drops significantly
3. **Tracing**: Follow chains of reasoning through context — steep degradation
4. **Aggregation**: Synthesize information across the full context — worst performance

Key finding from RULER: Of 17 models tested claiming 32K+ context, only 4 maintained acceptable performance at their claimed length across all task categories. Specific numbers: GPT-4 (the best performer) still dropped 15.4 percentage points from 4K to 128K context. Mixtral (32K claimed) collapsed from 94.9% at 4K to 44.5% at 128K.

**What this means**: A 200K-token model might perform reliably only up to ~65-100K tokens for complex tasks. A 128K model might degrade noticeably past 50K. The advertised number is the ceiling, not the floor.

## Lesson 2.2: Why Models Fail at Length

**Attention degradation**: Transformer attention is theoretically over all tokens, but in practice, models develop biases. They attend more strongly to tokens at the beginning (primacy) and end (recency) of context.

**Lost in the middle** (Liu et al., 2023): Landmark paper showing that information placed in the middle of long contexts is significantly less likely to be retrieved or used correctly. Models form a "U-shaped" attention curve — strong at start and end, weak in the middle. Specific data: in a 20-document QA task, accuracy was ~75% when the answer was at position 1, dropped to ~55% at position 10 (middle), and recovered to ~72% at position 20. A 20+ percentage-point gap from a positional shift alone.

**The four failure modes from RULER**:

1. **Distraction failure**: Irrelevant context actively interferes with retrieval
2. **Multi-hop failure**: Can't chain together multiple pieces of information
3. **Pattern tracking failure**: Loses track of repeated or sequential patterns
4. **Aggregation failure**: Can't synthesize or count across many distributed items

**Why this matters for agents**: Agent workloads are exactly the kind of task that triggers these failures. An agent session accumulates tool results, code snippets, error messages, and instructions — all interleaved. The critical instruction from 50 messages ago is exactly the kind of "middle context" that gets lost.

## Lesson 2.3: The Smart Zone and the Dumb Zone

**The concept**: Divide the context window into two regions:

- **The Smart Zone**: The portion of the context window where the model performs reliably. Typically the first ~40-50% of the advertised context length.
- **The Dumb Zone**: The remaining capacity where performance degrades progressively. The model still accepts tokens, but reasoning quality, instruction following, and retrieval accuracy decline.

**The 40% rule of thumb**: For complex, multi-step tasks (like agent workloads involving multi-hop reasoning), aim to keep total context utilization under ~40% of the advertised window. This is a conservative design target, not an empirical hard line — simpler tasks (single retrieval, straightforward generation) can work fine at higher utilization. But agent workloads hit the worst case.

- 200K window → target ≤80K of actual context
- 128K window → target ≤50K of actual context
- 1M window → target ≤400K of actual context

**Recognizing dumb zone entry**: Signs that your agent has crossed into the dumb zone:

- Repeats actions it already took
- Forgets instructions from earlier in the conversation
- Makes errors on tasks it handled correctly earlier
- Starts "hallucinating" about what happened in the session
- Tool calls become less targeted and more exploratory

**What to do about it**: When you detect dumb-zone behavior, the answer is not "give it more context." The answer is to reset: start a fresh context window with only the essential state. This is the foundation of patterns we'll cover in [Module 5](./05-ralph-wiggum-loop.md), [Module 6](./06-sub-agents.md), and [Module 7](./07-message-passing.md).

## Lesson 2.4: Measuring Your Context Budget

**The context budget**: Your total available tokens minus all fixed allocations. This is what's actually available for the dynamic parts of your application — the conversation, tool results, and reasoning.

**Fixed allocations** (things that consume tokens on every request):

- System prompt: typically 500-2,000 tokens
- Harness/framework prompt: 1,000-5,000 tokens
- Project context (AGENTS.md etc.): 500-3,000 tokens
- Tool definitions: 200-500 tokens per tool × number of tools
- If you have 20 MCP tools: that's 4,000-10,000 tokens just for tool schemas

**The budget formula**:

```
Effective budget = (Advertised window × 0.4) − Fixed allocations
```

Example with Claude Sonnet 4.6 (200K window):

```
Smart zone:     200,000 × 0.4 = 80,000 tokens
System prompt:              −1,500
Harness prompt:             −3,000
CLAUDE.md:                  −2,000
Tool definitions (15 tools): −5,000
─────────────────────────────────────
Effective budget:           68,500 tokens
```

That's your real budget for conversation + tool results + reasoning.

**Agent architecture implications**:

- 68,500 tokens sounds like a lot — until a single file read returns 5,000 tokens, a test run dumps 10,000 tokens, and you're 10 exchanges deep
- Budget awareness must be designed into your agent, not bolted on after
- This is why sub-agents ([Module 6](./06-sub-agents.md)) and fresh-context patterns ([Module 5](./05-ralph-wiggum-loop.md)) exist

## Key Takeaways

- Advertised context lengths are marketing. Effective context is 40-50% of the number on the box.
- NIAH tests are misleading. Use RULER-style benchmarks to understand real model capabilities.
- Models lose information in the middle of context ("Lost in the Middle" effect).
- Calculate your real context budget: (window × 0.4) minus fixed allocations.
- Design for the smart zone. When you exceed it, reset — don't push through.

## References

- Hsieh, C.-P., et al. (2024). "RULER: What's the Real Context Size of Your Long-Context Language Models?" arXiv:2404.06654. https://arxiv.org/abs/2404.06654
- Liu, N. F., et al. (2023). "Lost in the Middle: How Language Models Use Long Contexts." arXiv:2307.03172. https://arxiv.org/abs/2307.03172
- Kamradt, G. (2023). "Needle In A Haystack - Pressure Testing LLMs." https://github.com/gkamradt/LLMTest_NeedleInAHaystack
- Li, Y., et al. (2024). "Long-context LLMs Struggle with Long In-context Learning." arXiv:2404.02060.
- Chroma Research. (2025). "Context Rot: How Increasing Input Tokens Impacts LLM Performance." https://research.trychroma.com/context-rot
- Paulsen, T. (2025). "Context Is What You Need: The Maximum Effective Context Window." arXiv:2509.21361.

---

← [Module 1: Tokens and Inference](./01-tokens-and-inference.md) | [Module 3: Anatomy of the Messages Array →](./03-messages-array.md)
