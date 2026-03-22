# Project Summary: Context Engineering Course

## What This Is

A comprehensive course on **Context Engineering** — the discipline of managing what goes into a language model's context window. Based on the outline from [latentpatterns.com/courses/context-engineering](https://latentpatterns.com/courses/context-engineering), fleshed out with deep research into practitioner experiences, academic papers, and production systems.

**Final state**: 13,217 words across 10 files, producing a 46-page PDF book (192KB).

## File Structure

```
context-engineering-course/
├── index.md                              # Course overview, module index, master references
├── outline.md                            # Original captured outline from source
├── modules/
│   ├── 01-tokens-and-inference.md        # BPE, tokenization, stateless inference
│   ├── 02-context-window-size.md         # RULER, lost-in-middle, smart/dumb zones, budgets
│   ├── 03-messages-array.md              # 5 slots: system, harness, project context, MCP, prompt
│   ├── 04-tool-calling.md                # Tool call token costs, session walkthrough
│   ├── 05-ralph-wiggum-loop.md           # Three-phase funnel, specs, backpressure, brownfield
│   ├── 06-sub-agents.md                  # Context isolation, test runner, read/write distinction
│   ├── 07-message-passing.md             # Erlang OTP analogy, protocols, supervision trees
│   └── 08-context-management.md          # malloc/free, compaction, 6 strategies, course summary
├── build_pdf.py                          # Concatenates modules, runs pandoc + tectonic
├── header.tex                            # LaTeX header (fancyhdr for running headers/footers)
├── pyproject.toml                        # uv project (no runtime deps needed for PDF build)
├── uv.lock
├── .gitignore                            # Excludes .pdf, .venv, __pycache__
├── prompt.md                             # Original user prompt (captured at start)
└── context-engineering-course.pdf         # Generated output (not in git)
```

## How to Build the PDF

Requires `pandoc` and `tectonic` (install via `brew install pandoc tectonic`):

```bash
python3 build_pdf.py
```

Outputs `context-engineering-course.pdf` (~46 pages, ~192KB).

## Approach and History

### Phase 1: Initial Content (commit `ddc0499`)
- Fetched course outline from latentpatterns.com via WebFetch
- Launched 5 parallel research agents (tokenization, benchmarks, MCP/tools, tool calling/Ralph Wiggum, sub-agents/Erlang/memory management)
- Wrote all 8 modules in parallel via background agents
- 2 parallel review agents caught 20+ issues
- All issues fixed in the initial commit

### Phase 2: Gemini Comparison (commit `fba14f1`)
- Read the competing Gemini-generated course at `../context-engineering-course-gemini/`
- Produced a detailed comparative assessment
- Incorporated Gemini's strengths: JSON payload walkthrough (Module 4), practitioner-level failure taxonomy (Module 2), Context Manager pattern (Module 8)
- Added research findings: Chroma context rot data, Manus insights, JetBrains observation masking, Cognition anti-multi-agent warning

### Phase 3: PDF Generation (commits `cc18073`, `ff71bc8`)
- Initially tried xhtml2pdf (pure Python) — code blocks didn't render properly
- Switched to pandoc + tectonic (LaTeX-based) — excellent results
- Fixed tables that were indented inside list items (pandoc couldn't parse them)
- Added header.tex for running headers/footers

### Phase 4: Deep Practitioner Research (commit `7ebb41e`)
- Launched 4 parallel research agents for deep dives into Ralph Wiggum Loop, sub-agents, context management, and MCP/tools
- Key findings incorporated:
  - **Module 5**: Three-phase funnel (Requirements → Planning → Building), greenfield vs brownfield nuance with 3 documented counterexamples, backpressure principle, overbaking and failure modes, concrete file structure and budget numbers, prompt language discoveries
  - **Module 6**: Read vs write distinction (Schmid/Google), token explosion risk, Cognition's Flappy Bird example
  - **Module 7**: Manus's todo.md attention pattern, Agent-as-Tool mental model
  - **Module 8**: Compaction mechanics, Lance Martin's Write/Select/Compress/Isolate taxonomy
  - **Module 3**: ETH Zurich AGENTS.md study, deferred tool loading specifics
  - **Index**: Context engineering term origin (Lutke/Karpathy, June 2025)

### Phase 5: Brownfield Research (integrated into Phase 4 commit)
- User challenged the "greenfield only" claim for Ralph Wiggum Loop
- Deep research confirmed: Huntley's claim is directionally right but technically wrong
- Found 3 documented counterexamples (900K game port, 300K LOC Rust, 3-year framework migration)
- Key insight: "spec convergence" — research the codebase first, spec only the change area

### Phase 6: Polish and Prose Reformat (commits `478460d`, `702c78c`)
- Updated index lesson listings to match actual module headings
- Updated key takeaways across modules for consistency
- **Major reformat**: Converted all 8 modules from bullet-point lists to flowing prose paragraphs
- Lists now reserved for: enumerated steps, tables, code blocks, Key Takeaways, references

## Key Design Decisions

1. **Prose over bullets**: Textbook-style flowing paragraphs, not slide-deck bullet points
2. **Concrete numbers**: Every claim backed by specific data (RULER scores, token counts, dollar costs)
3. **Practitioner depth**: Not just theory — includes failure modes, criticisms, real-world numbers
4. **Honest treatment**: Includes limitations (METR complexity ceiling, code quality concerns, cost)
5. **Cross-linked**: All module references are hyperlinks; forward references introduce concepts
6. **Research-backed**: 50+ specific citations with URLs, covering academic papers, engineering blogs, and practitioner reports

## Key Sources (most frequently referenced)

- Anthropic. "Effective Context Engineering for AI Agents." (the canonical reference)
- Huntley, G. "Ralph Wiggum as a Software Engineer." + "How to Ralph Wiggum" GitHub repo
- Hsieh et al. "RULER" benchmark paper (context window evaluation)
- Liu et al. "Lost in the Middle" paper (U-shaped attention)
- Cognition. "Don't Build Multi-Agents." (anti-pattern for parallel writes)
- Schmid, P. "Single vs Multi-Agent System?" (read vs write heuristic)
- Manus. "Context Engineering for AI Agents." (KV-cache, todo.md, failed actions)
- Martin, L. "Context Engineering for Agents." (Write/Select/Compress/Isolate)
- JetBrains Research. "Efficient Context Management." (observation masking vs summarization)
- Chroma Research. "Context Rot." (degradation quantification)
- Farr, C. "The Ralph Wiggum Playbook." (backpressure, plan disposability)

## Commit History

```
702c78c Reformat all modules from bullet lists to prose
478460d Polish: update index, key takeaways, and narrative flow
7ebb41e Deepen course with practitioner research findings
ff71bc8 Fix table rendering in PDF output
cc18073 Add PDF build script (pandoc + tectonic)
fba14f1 Improve course based on Gemini comparison and research findings
ddc0499 Initial course content: Context Engineering (8 modules)
```
