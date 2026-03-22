# Context Engineering

A course on managing what goes into a language model's context window — from tokens and system prompts to tool calls and memory strategies.

Based on the outline from [latentpatterns.com/courses/context-engineering](https://latentpatterns.com/courses/context-engineering), fleshed out with research into practitioner experiences, academic papers, and production systems.

## Reading the course

Start with **[index.md](./index.md)** — the course overview and module index.

Modules are in `modules/` and meant to be read sequentially:

| # | Module | Core concept |
|---|--------|-------------|
| 1 | Tokens and Inference | BPE tokenization, stateless inference, the messages array |
| 2 | Context Window Size | RULER benchmark, lost-in-the-middle, smart zone vs. dumb zone |
| 3 | Messages Array | The 5 slots: system prompt, harness, project context, tools, your prompt |
| 4 | Tool Calling | Tool calls as memory allocations, token accumulation |
| 5 | Sub-Agents | Context isolation, the test runner problem, read vs. write heuristic |
| 6 | Message Passing | Erlang OTP actor model, message protocols, supervision trees |
| 7 | The Ralph Wiggum Loop | Crash-only agent design, fresh-context iteration, specs as memory |
| 8 | Context Management | malloc without free, compaction dangers, Write/Select/Compress/Isolate |

## Building the PDF

The build script assembles all modules into a single markdown file, then runs pandoc with LaTeX to produce a ~46-page PDF.

**With Docker** (no local dependencies):

```bash
uv run build_pdf.py --docker
```

**Locally** (requires `pandoc` and `tectonic`):

```bash
uv run build_pdf.py
```

## How this course was built

The course was written by Claude (Anthropic) across multiple sessions, using aggressive parallelism: 5 research agents ran simultaneously to gather source material, 8 modules were drafted in parallel, and 2 review agents caught issues before the initial commit.

Key design decisions:

- **Prose over bullets** — textbook-style flowing paragraphs, not slide-deck lists
- **Concrete numbers** — every claim backed by specific data (RULER scores, token counts, dollar costs)
- **Practitioner depth** — failure modes, criticisms, and real-world numbers alongside theory
- **Honest treatment** — includes limitations (METR complexity ceiling, code quality concerns, cost)
- **Research-backed** — 50+ citations from academic papers, engineering blogs, and practitioner reports

The original outline from the source website is preserved in [outline-original.md](./outline-original.md).
