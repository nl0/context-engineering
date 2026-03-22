# Context Engineering

A short textbook on managing what goes into a language model's context window — from tokens and system prompts to tool calls and memory strategies.

**Read online:** [nl0.github.io/context-engineering](https://nl0.github.io/context-engineering/)
**Download PDF:** [Context-Engineering.pdf](https://nl0.github.io/context-engineering/Context-Engineering.pdf)

Based on the outline from [latentpatterns.com/courses/context-engineering](https://latentpatterns.com/courses/context-engineering), fleshed out with research into practitioner experiences, academic papers, and production systems.

## Chapters

| # | Chapter | Core concept |
|---|--------|-------------|
| 1 | Tokens and Inference | Tokenization, stateless inference, the messages array |
| 2 | Context Window Size | RULER benchmark, lost-in-the-middle, smart zone vs. dumb zone |
| 3 | Messages Array | The 5 slots: system prompt, harness, project context, tools, your prompt |
| 4 | Tool Calling | Tool calls as memory allocations, token accumulation |
| 5 | Sub-Agents | Context isolation, the test runner problem, read vs. write heuristic |
| 6 | Message Passing | Erlang OTP actor model, message protocols, supervision trees |
| 7 | The Ralph Wiggum Loop | Crash-only agent design, fresh-context iteration, specs as memory |
| 8 | Context Management | malloc without free, compaction dangers, Write/Select/Compress/Isolate |

## Building locally

Requires [Quarto](https://quarto.org/docs/get-started/) and TinyTeX (`quarto install tinytex`).

```bash
quarto render
```

Outputs HTML site to `_site/` and PDF. Pushes to GitHub trigger automatic builds via GitHub Actions.

## Credits

Written by [Claude](https://claude.ai) (Anthropic), directed and edited by a human author across multiple sessions. Outline from [Latent Patterns](https://latentpatterns.com/courses/context-engineering). Research drawn from 50+ sources including academic papers, engineering blogs, and practitioner reports.

## License

[CC BY-ND 4.0](./LICENSE)
