# Context Engineering — Original Course Outline

> **Note:** This is the original outline captured from the source website before the course was written. It is preserved here for provenance. The actual course structure has evolved — see [index.md](./index.md) for the current module listing.

> Master the art of managing what goes into a language model's context window — from tokens and system prompts to tool calls and memory strategies.

**Source:** [latentpatterns.com/courses/context-engineering](https://latentpatterns.com/courses/context-engineering)

---

## Module 1: Tokens and Inference

- **1.1** What Are Tokens?
- **1.2** Inference Is Stateless

## Module 2: The Real Size of Your Context Window

- **2.1** Marketing Numbers vs. Engineering Reality
- **2.2** Why Models Fail at Length
- **2.3** The Smart Zone and the Dumb Zone
- **2.4** Measuring Your Context Budget

## Module 3: Anatomy of the Messages Array

- **3.1** Slot 0 — The System Prompt
- **3.2** Slot 1 — The Harness Prompt
- **3.3** Slot 2 — AGENTS.md
- **3.4** Slot 3 — MCP Servers and Agent Skills
- **3.5** Slot 4 — Your Prompt

## Module 4: Dynamic Allocation — Tool Calling

- **4.1** Tool Calls as Memory Allocations
- **4.2** A Real Agent Session

## Module 5: The Ralph Wiggum Loop

- **5.1** What Is the Ralph Wiggum Loop?
- **5.2** Specs and Plans — The Persistent Memory
- **5.3** Three Modes of Ralph

## Module 6: Sub-Agents — Managed Runtimes for AI

- **6.1** Sub-Agents Are Not About Personas
- **6.2** The Test Runner Problem
- **6.3** Designing Sub-Agent Boundaries

## Module 7: Message Passing — The Erlang OTP of AI

- **7.1** Context Windows Are Actors
- **7.2** Designing the Message Protocol
- **7.3** Supervision and Failure

## Module 8: Context Management Strategies

- **8.1** The `malloc` Without `free`
- **8.2** Why Compaction Is Dangerous
- **8.3** Better Strategies
