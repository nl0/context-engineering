# Chapter 2: The Real Size of Your Context Window

## Marketing Numbers vs. Engineering Reality

Model providers advertise context windows of 128K, 200K, 1M, even 10M tokens. These numbers represent the theoretical maximum input the model can accept. They do not represent the context size at which the model performs well. The gap between advertised and effective context is substantial, and understanding it is essential.

The most common benchmark for testing long context is **needle-in-a-haystack (NIAH)**: hide a specific fact in a long document, then ask the model to retrieve it. Models score near-perfect on these tests at their full advertised context lengths. But NIAH is misleading — it only tests single-fact retrieval from a mostly irrelevant context. Real tasks require reasoning over multiple pieces of information scattered throughout context.

The **RULER benchmark** (Hsieh et al., 2024) provides a much more rigorous test across four categories:

1. **Single retrieval (NIAH)**: Find one needle — models do well
2. **Multi-key retrieval**: Find multiple needles — performance drops significantly
3. **Tracing**: Follow chains of reasoning through context — steep degradation
4. **Aggregation**: Synthesize information across the full context — worst performance

The key finding from RULER is striking: of 17 models tested claiming 32K+ context, only 4 maintained acceptable performance at their claimed length across all task categories. GPT-4 (the best performer) still dropped 15.4 percentage points from 4K to 128K context. Mixtral (32K claimed) collapsed from 94.9% at 4K to 44.5% at 128K.

The practical takeaway is clear. A 200K-token model might perform reliably only up to ~65-100K tokens for complex tasks. A 128K model might degrade noticeably past 50K. The advertised number is the ceiling, not the floor.

## Why Models Fail at Length

Transformer attention is theoretically over all tokens, but in practice, models develop biases. They attend more strongly to tokens at the beginning (primacy) and end (recency) of context. This **attention degradation** is the root cause of long-context failures.

The landmark **"Lost in the Middle"** paper (Liu et al., 2023) demonstrated this concretely. Information placed in the middle of long contexts is significantly less likely to be retrieved or used correctly. Models form a "U-shaped" attention curve — strong at start and end, weak in the middle. In a 20-document QA task, accuracy was ~75% when the answer was at position 1, dropped to ~55% at position 10 (middle), and recovered to ~72% at position 20. That is a 20+ percentage-point gap from a positional shift alone.

The RULER benchmark identified four specific failure modes that explain how this degradation manifests:

1. **Distraction failure**: Irrelevant context actively interferes with retrieval
2. **Multi-hop failure**: Can't chain together multiple pieces of information
3. **Pattern tracking failure**: Loses track of repeated or sequential patterns
4. **Aggregation failure**: Can't synthesize or count across many distributed items

These failure modes matter especially for agent workloads, which are exactly the kind of task that triggers them. An agent session accumulates tool results, code snippets, error messages, and instructions — all interleaved. The critical instruction from 50 messages ago is exactly the kind of "middle context" that gets lost.

In practice, these academic failure modes show up as recognizable **practitioner-level failure patterns**. **Context poisoning** occurs when the model hallucinates a function name early on; that hallucination stays in context and becomes "ground truth," and the model references its own mistake in later turns, compounding the error. **Instruction attenuation** happens as context fills with tool results and code — the system prompt's instructions lose "weight," and the model stops following formatting rules, forgets safety constraints, or abandons the original goal. **Context confusion** arises when multiple versions of the same file enter context (the original read, then a modified version), and the model blends them into a plausible-but-wrong hybrid.

These are not hypothetical. They are the everyday experience of developers using coding agents.

## The Smart Zone and the Dumb Zone

The core concept here is to divide the context window into two regions. **The Smart Zone** is the portion of the context window where the model performs reliably — typically the first ~40-50% of the advertised context length. **The Dumb Zone** is the remaining capacity where performance degrades progressively. The model still accepts tokens, but reasoning quality, instruction following, and retrieval accuracy decline.

This leads to a practical guideline: **the 40% rule of thumb**. For complex, multi-step tasks (like agent workloads involving multi-hop reasoning), aim to keep total context utilization under ~40% of the advertised window. This is a conservative design target, not an empirical hard line — simpler tasks (single retrieval, straightforward generation) can work fine at higher utilization. But agent workloads hit the worst case. Applied to current models:

- 200K window → target ≤80K of actual context
- 128K window → target ≤50K of actual context
- 1M window → target ≤400K of actual context

Research from Chroma Research (2025) confirms this degradation is real and universal. They tested 18 frontier models and found that every model degrades as input length increases — there are no exceptions. Their data shows approximately 2% effectiveness loss per 100K tokens added for Claude models (which decayed slowest among those tested). This degradation is continuous, not a cliff — there's no safe length below which context is "free."

Recognizing when your agent has crossed into the dumb zone is a practical skill. The signs include: repeating actions it already took, forgetting instructions from earlier in the conversation, making errors on tasks it handled correctly earlier, "hallucinating" about what happened in the session, and tool calls becoming less targeted and more exploratory.

When you detect dumb-zone behavior, the answer is not "give it more context." The answer is to reset: start a fresh context window with only the essential state. This is the foundation of patterns we'll cover in [Chapter 5](./05-sub-agents.md), [Chapter 6](./06-message-passing.md), and [Chapter 7](./07-ralph-wiggum-loop.md).

## Measuring Your Context Budget

Your **context budget** is your total available tokens minus all fixed allocations. This is what's actually available for the dynamic parts of your application — the conversation, tool results, and reasoning.

Several categories of **fixed allocations** consume tokens on every request. System prompts typically run 500-2,000 tokens. Harness and framework prompts add 1,000-5,000 tokens. Project context (AGENTS.md and similar files) contributes 500-3,000 tokens. Tool definitions cost 200-500 tokens per tool, multiplied by the number of tools — if you have 20 MCP tools, that's 4,000-10,000 tokens just for tool schemas.

The budget formula brings this together:

**Effective budget = (Advertised window × 0.4) − Fixed allocations**

Here's a worked example with Claude Sonnet 4.6 (200K window):

| Allocation | Tokens |
|---|---:|
| Smart zone (200K × 0.4) | 80,000 |
| System prompt | −1,500 |
| Harness prompt | −3,000 |
| CLAUDE.md | −2,000 |
| Tool definitions (15 tools) | −5,000 |
| **Effective budget** | **68,500** |

That's your real budget for conversation + tool results + reasoning. It sounds like a lot — until a single file read returns 5,000 tokens, a test run dumps 10,000 tokens, and you're 10 exchanges deep. Budget awareness must be designed into your agent, not bolted on after. This is why sub-agents ([Chapter 5](./05-sub-agents.md)) and fresh-context patterns ([Chapter 7](./07-ralph-wiggum-loop.md)) exist.

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
