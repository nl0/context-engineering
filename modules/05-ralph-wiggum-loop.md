# Module 5: The Ralph Wiggum Loop

← [Module 4: Dynamic Allocation — Tool Calling](./04-tool-calling.md) | [Module 6: Sub-Agents — Managed Runtimes for AI →](./06-sub-agents.md)

---

## Lesson 5.1: What Is the Ralph Wiggum Loop?

- **The name and origin**: Created by Geoffrey Huntley in early 2025 and named after Ralph Wiggum from The Simpsons — a character who lives entirely in the present moment with no memory of what came before. In its purest form, it's a bash loop:
  ```bash
  while :; do cat PROMPT.md | claude-code ; done
  ```
  Each new context window is Ralph: capable and completely unaware of previous iterations. The pattern went viral in late 2025. Huntley's philosophical framing: "My institutional knowledge is in the specifications file." Code is clay on a pottery wheel. The spec is the real asset.

- **The core idea**: Instead of fighting context degradation, embrace the reset. Run your agent in a loop of fresh context windows. Each iteration starts clean, reads the spec, does one task, saves progress, and exits. The next iteration picks up where it left off — not from memory, but from files.

- **Why it works**: Each iteration gets the full smart zone. No accumulated cruft from tool calls. No degraded attention. The model is at peak performance every time. Huntley: "Compaction is the devil" — instead of lossy summarization, you get lossless persistence via the filesystem.

- **The key insight**: The specification file IS the memory. The context window is disposable. This inverts the usual mental model where people try to preserve the conversation. Instead: preserve the plan, discard the conversation.

## Lesson 5.2: The Three-Phase Funnel

Huntley structures work as three distinct phases, each with its own prompt and loop:

### Phase 1: Requirements (conversational, not looped)

Before any loop runs, spend 30+ minutes in a dedicated planning conversation using **bidirectional prompting**:

1. Describe what you want to build
2. Ask the model to ask YOU questions (surface hidden assumptions)
3. Answer the questions
4. Ask the model to generate more questions based on your answers
5. Repeat until the model has no more questions
6. Have the model write the specification

This produces specs dramatically more complete than what you'd write alone. The model surfaces edge cases, architectural decisions, and requirements you hadn't considered. The output is one or more spec files in a `specs/` directory — one topic per file, passing the "single-sentence without conjunctions" test.

### Phase 2: Planning (looped, but no code)

Run the planning loop: `./loop.sh plan` with `PROMPT_plan.md`

The agent performs gap analysis — comparing specs against existing code. It outputs a prioritized `IMPLEMENTATION_PLAN.md`. **No code is written. No commits.** This is pure analysis.

For existing codebases, this phase is where **spec convergence** happens: the agent studies the codebase, maps what exists, and the plan accounts for existing patterns and constraints. Without this phase, the agent will duplicate existing functionality or violate established conventions.

### Phase 3: Building (looped, one task per iteration)

Run the build loop: `./loop.sh` with `PROMPT_build.md`

Each iteration: agent reads the spec + plan, picks the most important unchecked task, implements it, runs tests, commits, and exits. The loop restarts fresh.

**"One thing per loop"** — Huntley's most emphatic principle. Each iteration does exactly one task. Trust the agent to pick which one. You control what's in the plan; the agent controls execution order.

### The File Structure

```
project-root/
├── loop.sh                    # Bash orchestrator (mode selection, iteration limits)
├── PROMPT_plan.md             # Planning mode instructions
├── PROMPT_build.md            # Building mode instructions
├── AGENTS.md                  # Operational guide (~60 lines max)
├── IMPLEMENTATION_PLAN.md     # Living state — checkboxes, progress, notes
├── specs/                     # One requirement file per topic
│   ├── authentication.md
│   └── data-model.md
└── src/
```

## Lesson 5.3: Specs and Plans — The Persistent Memory

- **Checkbox-based progress tracking**: Structure the implementation plan as a checklist:
  ```markdown
  ## Implementation Plan

  - [x] Set up project structure
  - [x] Create database schema
  - [x] Implement user model
  - [ ] Add authentication middleware  ← current
  - [ ] Create login/register endpoints
  - [ ] Add JWT token refresh
  - [ ] Write integration tests
  - [ ] Update API documentation

  ## Notes
  - JWT library: using jose (iteration #4 discovered jsonwebtoken has ESM issues)
  - Auth middleware must check both cookie and Authorization header (spec update from iteration #6)
  ```

- **Spec design principles**:
  - **Self-contained**: The spec alone must be enough to continue work. No dependency on "remembering" a previous conversation.
  - **Concise**: ~5,000 tokens per spec file. It loads into every iteration's context — bloat wastes your smart zone.
  - **One topic per file**: If you need "and" to describe it, split it.
  - **Machine-verifiable completion criteria**: "If you can't define 'done' in terms a test suite can verify, Ralph can't stop."
  - **Append-friendly**: Include a "Notes" section where iterations log discoveries for future iterations.

- **Plan disposability**: "A plan that drifts is cheaper to regenerate than to salvage." When reality diverges from the plan, switch back to planning mode and regenerate. Don't try to manually fix a stale plan.

## Lesson 5.4: Backpressure and Guardrails

The most underrated aspect of the Ralph Loop isn't the loop itself — it's the environment it runs in.

- **"Backpressure beats direction"**: Instead of telling the agent what to do, engineer an environment where wrong outputs get rejected automatically. Tests, linters, type-checkers, and build validation create hard gates. If the agent produces bad code, the backpressure system catches it — the agent sees the failure on its next iteration and corrects course.

- **Start with hard gates**: Tests and builds are deterministic. Start there. A passing test suite is a stronger signal than any prompt instruction. "Your codebase is stronger evidence than your instructions" — existing code patterns steer the agent more than prompts do.

- **Git as safety net**: Each iteration commits independently. `git reset --hard` is an acceptable recovery strategy. The version history is your undo button.

- **Cap iterations**: Set explicit limits (5-50 depending on scope) to prevent runaway costs and overbaking. Don't let the loop run indefinitely.

- **Run in sandboxes**: Docker containers or isolated environments. Huntley: "It's not if it gets popped, it's when."

- **Use sub-agents for heavy lifting**: Up to many parallel sub-agents for reads, but only 1 for build/tests. Serializing validation prevents backpressure collapse — if multiple agents run tests simultaneously, they can't tell whose changes broke what.

## Lesson 5.5: Greenfield vs. Brownfield

- **The common claim**: Huntley famously said "There's no way in heck would I use Ralph in an existing code base." This is directionally right — **naive** Ralph on existing code creates duplicates, ignores existing patterns, and causes regressions.

- **But it's not absolute**: Huntley's own formalized methodology (his GitHub repo) instructs the agent to "compare specifications against existing source code to identify gaps" and warns "don't assume not implemented." The planning phase is explicitly brownfield-aware.

- **Documented successes on existing code**:
  - 900K-line game engine ported from Windows to macOS in 4 days (Ronin Consulting)
  - 300K LOC Rust codebase — bug fix in 1 hour + 35K LOC of features in 7 hours by a developer who'd never seen the code (HumanLayer ACE-FCA on BAML)
  - 3-year-old Next.js/React framework migrated across major versions — 271 commits in 3 days (Dan Malone)

- **What makes brownfield work**: The research/planning phase must be proportionally larger and the iteration scope proportionally smaller:
  1. **Research first**: Agent explores the existing codebase before any spec is written
  2. **Spec only the change area**: Don't reverse-engineer the whole system. Spec coverage grows incrementally where changes happen
  3. **Capture conventions in AGENTS.md**: Build commands, architecture patterns, testing conventions — information the agent can't infer from code alone
  4. **Existing test suites as guardrails**: Brownfield has an advantage here — tests already exist to catch regressions

- **What breaks without this**: The agent "ignored the notes that these were descriptions of existing classes, it just took them as a new specification and generated them all over again, creating duplicates" (Thoughtworks evaluation of spec-kit).

## Lesson 5.6: Failure Modes and Criticisms

The Ralph Loop is not a silver bullet. Know its failure modes:

- **Overbaking**: Running too long without supervision produces unrequested features. Huntley documented "bizarre emergent behavior" — post-quantum cryptography support appearing in a project that didn't need it.

- **Oscillation**: "It fixed a type error in utils.ts by breaking an import in main.ts. Then it fixed main.ts by reverting the change in utils.ts." Back-and-forth without progress. Iteration caps and human review break the cycle.

- **Duplicate implementations**: Without "don't assume not implemented" guardrails, the agent rebuilds existing functionality. Critical in brownfield work.

- **Plan staleness**: The plan drifts from reality but isn't regenerated. Solution: treat plans as disposable — switch to planning mode when drift is detected.

- **Task complexity ceiling**: METR's 2025 research found agent success rates drop from near-100% on sub-4-minute tasks to less than 10% on tasks requiring 4+ hours of human effort. Ralph doesn't change this ceiling — it helps you stay under it by decomposing large tasks.

- **Cost**: 50 iterations on a medium codebase cost $50-100+ in API credits. Each iteration re-reads the spec and relevant files. Budget for this.

- **Code structure quality**: GitClear's 2025 analysis found AI-assisted development correlates with increased copy-paste code and decreased refactoring. Ralph-generated code runs but may lack structural coherence. Huntley targets "90% done" — expect human refinement.

### Prompt language that matters

Practitioners discovered specific phrasings that trigger better agent behavior:

- **"study"** (not "read" or "look at") — triggers deeper analysis
- **"don't assume not implemented"** — prevents duplicate functionality
- **"only 1 subagent for build/tests"** — serializes validation
- **"if functionality is missing then it's your job to add it"** — prevents learned helplessness
- **"capture the why"** — produces better documentation

## Key Takeaways

- The Ralph Wiggum Loop is a three-phase funnel: Requirements → Planning (no code) → Building (one task per loop).
- The specification is the asset. Code is clay. The context window is disposable.
- Backpressure (tests, linting, type-checking) steers the agent more than prompt instructions.
- It works on existing codebases — but the research phase must be proportionally larger and iteration scope smaller.
- Know the failure modes: overbaking, oscillation, duplication, plan staleness, complexity ceiling.
- Budget: ~5K tokens per spec, AGENTS.md under 60 lines, cap iterations at 5-50, expect $50-100 per 50 iterations.

## References

- Huntley, G. (2025). "Ralph Wiggum as a 'Software Engineer.'" https://ghuntley.com/ralph/
- Huntley, G. (2025). "Everything is a Ralph Loop." https://ghuntley.com/loop/
- Huntley, G. (2025). "How to Ralph Wiggum." https://github.com/ghuntley/how-to-ralph-wiggum
- Farr, C. (2025). "The Ralph Wiggum Playbook." https://paddo.dev/blog/ralph-wiggum-playbook/
- HumanLayer. (2025). "A Brief History of Ralph." https://www.humanlayer.dev/blog/brief-history-of-ralph
- HumanLayer. (2025). "Advanced Context Engineering for Coding Agents (ACE-FCA)." https://github.com/humanlayer/advanced-context-engineering-for-coding-agents
- Malone, D. (2026). "Orchestrating AI Agents to Migrate a 3-Year-Old Codebase." https://www.dan-malone.com/blog/ralph-wiggum-orchestrating-ai-agents
- Ronin Consulting. (2025). "Using the Ralph Wiggum Loop." https://www.ronin.consulting/artificial-intelligence/using-the-ralph-wiggum-loop/
- Osmani, A. (2025). "How to Write a Good Spec for AI Agents." https://addyosmani.com/blog/good-spec/
- Thoughtworks. (2025). "Spec-Driven Development." Technology Radar. https://www.thoughtworks.com/en-us/radar/techniques/spec-driven-development
- METR. (2025). "Measuring the Impact of AI on Software Engineering Tasks."

---

← [Module 4: Dynamic Allocation — Tool Calling](./04-tool-calling.md) | [Module 6: Sub-Agents — Managed Runtimes for AI →](./06-sub-agents.md)
