# Chapter 1: Tokens and Inference

## What Are Tokens?

### Why tokens, not characters

LLMs don't process raw text. Before anything happens, text is split into **tokens** — subword units that balance vocabulary size with sequence length. Tokens are the atomic unit of LLM computation. The model reads tokens. The model generates tokens. Pricing is per token. Context limits are in tokens.

Everything in context engineering is measured in tokens.

Common words like "the" or "hello" become single tokens. Rare words like "defenestration" get split into pieces ("def", "en", "est", "ration" or similar). Different models use different tokenization schemes and vocabulary sizes, so the same text can produce different token counts depending on the model.

### Token IDs are just integers

Under the hood, a language model is a function that takes an array of integers and produces the next integer. That's it. The text you type is converted to token IDs before the model sees it, and the token IDs the model outputs are converted back to text before you see them. The sentence `"Hello, world!"` becomes something like `[9906, 11, 1917, 0]`.

This means everything in the context window — your prompt, the system instructions, the conversation history, the tool call results — becomes a single flat stream of integer tokens. The model doesn't "see" the structure you see. It sees numbers.

### The 4:1 rule of thumb

In English prose, **1 token ≈ 4 characters ≈ 0.75 words**. That means 1,000 tokens cover roughly 750 words, and a 100K-token context holds approximately 75,000 words — about the length of a short novel.

This ratio varies wildly by content type, though. **Code** is token-dense because whitespace, punctuation, and rare identifiers (variable names, imports) all fragment into more tokens per character. **Non-English languages** often require more tokens per word, since BPE training corpora are English-heavy — CJK characters, Arabic, and many others tokenize less efficiently. **JSON and XML** are extremely token-expensive: every brace, bracket, quote, colon, and key name eats tokens, and structural overhead can consume 3-5x more tokens than the equivalent data in plain text.

### Why this matters for context engineering

Every character you put into context has a token cost. A verbose system prompt wastes tokens. Bloated tool outputs waste tokens. Wrapping data in JSON when plain text would suffice wastes tokens.

Understanding token economics is the foundation of context engineering. You cannot manage what you cannot measure.

### Practical examples

Consider a few concrete cases. The string `"Hello, world!"` typically becomes 4 tokens (`Hello`, `,`, ` world`, `!`). A typical JSON API response might use 3-5x more tokens than the same data formatted as plain text or markdown. The string `{"name": "Alice", "age": 30}` costs more tokens than `Alice, age 30` — and both convey the same information to the model.

**Tools for counting tokens:**
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer) — interactive web tool
- [tiktoken](https://github.com/openai/tiktoken) — Python library for programmatic token counting
- Anthropic's API returns token counts in every response's `usage` field

Get in the habit of measuring. Don't guess token counts — compute them.

## Inference Is Stateless

### The fundamental truth

LLM inference is stateless. The server retains nothing between API calls. Every request must contain the complete conversation state.

There is no session. There is no memory. There is only the messages array.

### The messages array IS the state

Every API call sends the full conversation:

```json
{
  "model": "...",
  "system": "You are a helpful assistant.",
  "messages": [
    {"role": "user", "content": "What is 2+2?"},
    {"role": "assistant", "content": "4."},
    {"role": "user", "content": "And if you add 3?"}
  ]
}
```

(API formats vary — Anthropic uses a top-level `system` field, OpenAI uses `role: "system"` in the messages array. The concept is the same: a system instruction plus a sequence of user/assistant turns.)

The model sees this entire array on every call. It doesn't "remember" saying "4." — it re-reads it. The fourth message only makes sense because the third message is present. Remove any message and the model loses that context entirely.

### The illusion of memory

Chat UIs — ChatGPT, Claude.ai, Gemini — maintain the messages array client-side and replay it on every request. This creates the illusion of a continuous conversation.

But the implication is critical: **every previous message costs tokens on every subsequent call.** A 50-message conversation replays all 50 messages when you send message 51. The conversation gets more expensive with every exchange — linearly in tokens, quadratically in compute (due to attention).

### Implications for context engineering

These mechanics lead to four consequences that define the discipline.

First, **context is a finite, depletable resource** — not free storage. Every token you add to context is a token you can't use for something else. Second, **every token stays forever** unless you actively manage it. Old messages, stale tool results, and irrelevant context don't expire — they accumulate. Third, **the cost of context is paid on every inference call.** A 10K-token system prompt is charged on every single API call in the conversation. Fourth, and most importantly, **this is why context engineering exists:** to manage this scarce resource intelligently. What goes in? What stays? What gets summarized? What gets dropped? These are the core questions.

### Current context window sizes (early 2026)

| Model | Context Window | Max Output |
|-------|---------------|------------|
| GPT-5 (OpenAI) | 400K tokens | 128K |
| Claude Opus 4.6 (Anthropic) | 200K (1M beta) | 64K |
| Claude Sonnet 4.6 (Anthropic) | 200K (1M beta) | 64K |
| Gemini 2.5 Pro (Google) | 1M tokens | 64K |
| Llama 4 Scout (Meta) | 10M tokens | — |
| DeepSeek R1 | 128K tokens | 64K |

These numbers look generous. But as we'll see in [Chapter 2](./02-context-window-size.md), they are marketing numbers — not engineering reality. Effective context is always smaller than advertised context.

## Key Takeaways

- **Tokens are the currency of context.** Everything is measured in tokens.
- **1 token ≈ 4 English characters.** But format matters enormously — JSON costs 3-5x more than plain text for the same data.
- **Inference is stateless.** The messages array is replayed in full on every call.
- **Context is a finite resource** that gets more expensive with every exchange.

## References

- OpenAI Tokenizer: [https://platform.openai.com/tokenizer](https://platform.openai.com/tokenizer)
- OpenAI tiktoken library: [https://github.com/openai/tiktoken](https://github.com/openai/tiktoken)
- Anthropic API Documentation: [https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
