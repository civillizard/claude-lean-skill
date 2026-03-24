---
name: lean
description: Plan tasks with optimal model routing to minimize token usage. Breaks work into steps, assigns each the right model (Haiku/Sonnet/Opus), adds quality gates, persists the plan to file, and reports savings after execution. Use /lean before complex tasks.
allowed_tools:
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---

# Lean Task Planner

Optimize token usage by planning tasks with the right model for each step.
This skill loads at ~100 tokens until invoked — it practices what it preaches.

## Usage

- `/lean <task description>` — Analyze task and produce optimized execution plan
- `/lean` (no args) — Ask user what they're about to do, then plan it

## Instructions

### Step 1: Understand the Task

If no argument provided, ask the user what task they're planning:

```
Question: "What task are you about to work on?"
Header: "Task"
Options:
1. "Plan execution" - "Execute steps from an existing plan or spec file"
2. "New feature/fix" - "Build something new or fix a bug"
3. "Research/exploration" - "Understand code, find information"
4. "Bulk operation" - "Process multiple items (files, endpoints, components)"
```

If an argument was provided, proceed directly to Step 2.

### Step 2: Gather Context

Before planning, quickly check relevant context using direct tool calls (not subagents):
- If it's plan execution: Read the plan or spec file to understand the tasks
- If it's a feature: Glob/Grep to understand scope (how many files touched)
- If it's research: Identify what needs to be searched
- If it's bulk: Count the items and identify a representative test case

**Quick mode:** If the task decomposes to 3 or fewer steps with no bulk/staging needed, skip the full plan table. Output a one-liner instead: *"This is a [Model] task — [brief description]. Proceed?"*

### Step 3: Decompose and Assign Models

Break the task into discrete steps. For each step, assign a model using these rules:

| Task Type | Model | Why | Subagent? |
|-----------|-------|-----|-----------|
| Single file search/grep/read (1-2 calls) | **Direct** | Trivial — subagent overhead not worth it | No — do in main context |
| Multi-step file research (3+ files) | **Haiku** | Read-only, no reasoning needed | Yes — Explore or general-purpose |
| Codebase mapping (find files, list functions) | **Haiku** | Mechanical enumeration | Yes — Explore agent |
| Codebase understanding (patterns, architecture) | **Sonnet** | Needs pattern recognition, not just reading | Yes — Explore or Plan agent |
| Content extraction from large files/pages | **Haiku** | Filter and summarize, no generation | Yes — digest and return summary |
| Well-defined code generation (clear spec) | **Sonnet** | Capable enough when spec is unambiguous | Yes — general-purpose |
| Writing/updating tests | **Sonnet** | Follows existing patterns, clear inputs/outputs | Yes — general-purpose |
| Mechanical plan execution (clear tasks) | **Sonnet** | Steps are pre-defined, just needs execution | Yes — general-purpose |
| Complex execution (ambiguous, design decisions) | **Opus** | Judgment calls, trade-offs, novel territory | No — main context |
| Refactoring with clear before/after | **Sonnet** | Transformation is well-defined | Yes — general-purpose |
| Architecture, debugging, novel problems | **Opus** | Needs deepest reasoning | No — main context |
| Validation/testing after changes | **Haiku** | Just run tests, report pass/fail | Yes — Bash agent for test runs |

### Step 4: Apply Staging

For any task operating on multiple items:
1. Identify ONE representative item to test first
2. Plan the test run as a separate step
3. Add a **quality gate** after the test (Haiku runs tests + lint, reports pass/fail before proceeding)
4. Only then plan the expansion to all items

Example: "Migrate 8 API endpoints to v2" →
- Step 1: Haiku explore — read all 8 endpoints, summarize patterns
- Step 2: Sonnet — migrate `/users` endpoint (representative)
- Step 3: **Quality gate** — Haiku runs `/users` tests + lint, reports pass/fail
- Step 4: Sonnet — migrate remaining 7 (parallel subagents if independent)
- Step 5: **Final quality gate** — Haiku runs full test suite

Quality gates are mandatory between stages. If a gate fails, stop and fix before continuing.

### Step 5: Present the Plan

Output a structured plan:

```
## Lean Execution Plan

**Task:** [one-line description]

| # | Step | Model | Why | Agent Type | What |
|---|------|-------|-----|------------|------|
| 1 | Explore current state | Haiku | Read-only scan | Explore | Read X, Y, Z and summarize |
| 2 | Implement for test case | Sonnet | Clear spec from step 1 | general-purpose | Write code for [item] |
| 3 | Quality gate | Haiku | Validate before scaling | Bash | Run tests + lint, report |
| 4 | Expand to all items | Sonnet | Same pattern, parallel | general-purpose | Apply pattern to remaining |
| 5 | Final quality gate | Haiku | Catch regressions | Bash | Full test suite |

**Model mix:** ~40% Haiku, ~50% Sonnet, ~10% Opus (this conversation)
**Staging:** Test on [item] first, validate, then expand to [N] items

Approve this plan? (adjust any step if needed)
```

### Step 6: Persist the Plan

After user approves, write the plan to `.lean-plan.md` in the working directory:
- Include the full plan table, model assignments, and staging strategy
- Mark each step with `[ ]` checkbox for progress tracking
- This survives context compaction on long conversations and enables session resume

Update `.lean-plan.md` as steps complete (check off `[x]`).

### Step 7: Execute on Approval

If the user approves:
1. Execute steps in order
2. For each Task subagent, ALWAYS include `model` parameter as planned
3. Announce each step: "**Step 2/5:** Spawning Sonnet agent for endpoint migration..."
4. At each **quality gate**, run validation and report results before proceeding
5. After the test case step, pause and show results before expanding
6. If a quality gate fails, stop and fix before scaling
7. Update `.lean-plan.md` checkboxes as each step completes

### Step 8: Savings Report

After all steps complete, output a savings summary:

```
## Lean Savings Report

| Step | Model Used | Est. Input | Est. Output | Cost    | If All-Opus |
|------|-----------|------------|-------------|---------|-------------|
| 1    | Haiku     | ~3K        | ~1K         | $0.003  | $0.045      |
| 2    | Sonnet    | ~5K        | ~3K         | $0.027  | $0.105      |
| 3    | Haiku     | ~2K        | ~0.5K       | $0.002  | $0.030      |
| ...  |           |            |             |         |             |
| **Total** |      |            |             | **$X**  | **$Y**      |

**Saved: ~Z% vs all-Opus execution**
```

Use these rates for estimation (per 1M tokens, as of March 2026):
- Haiku: $0.80 input / $4.00 output
- Sonnet: $3.00 input / $15.00 output
- Opus: $15.00 input / $75.00 output

Estimates are rough — based on typical prompt/response sizes for each step type. The percentage matters more than exact dollars.

## Principles

- **Contain noise**: Verbose output stays inside subagents, main context gets summaries
- **Filter early**: Specific extraction prompts, not "summarize this page"
- **Test small first**: Always validate on one case before scaling
- **No model = Opus**: Always specify `model` on Task tool — never let it default
- **Quality gates**: Haiku validates between every stage transition — catch errors early and cheap
- **Persist the plan**: Write to `.lean-plan.md` so the plan survives context compaction
- **Parallel when independent**: Launch multiple Haiku/Sonnet subagents simultaneously for independent work
- **Sequential when dependent**: Don't guess at outputs — wait for results before next step
- **Show the savings**: Always report estimated savings after execution completes

## Companion: Auto-Nudge Hook (Optional)

For always-on passive protection, add `task-model-guard.py` as a PreToolUse hook on the Agent tool. It does two things:
1. **Model suggestion** — If a subagent is spawned without an explicit `model`, it classifies the prompt (regex-based, zero latency) and suggests Haiku or Sonnet when appropriate. Never blocks.
2. **Lean nudge** — If the prompt looks like a multi-step task (mentions "all endpoints", "migrate 8 files", etc.) and no `.lean-plan.md` exists, it suggests running `/lean` first.

See `task-model-guard.py` in this repo for the implementation.

## Portability

This skill is designed for **Claude Code** but the patterns transfer:

| Component | Claude Code | Other AI tools |
|-----------|-------------|----------------|
| Model routing table | Haiku / Sonnet / Opus | Map to your provider's tiers (e.g. GPT-4o-mini / GPT-4o / o1) |
| Subagent spawning | Agent tool with `model` param | Tool-specific (Cursor: @agent, Copilot: #agent) |
| Plan persistence | `.lean-plan.md` in working dir | Works anywhere — plain markdown |
| Quality gates | Haiku Bash agent runs tests | Any cheap model can validate |
| Savings report | Claude pricing | Adjust rates for your provider |
| Auto-nudge hook | `task-model-guard.py` PreToolUse | Claude Code specific — not portable |

The decomposition pattern, staging strategy, and quality gates work with any AI coding tool. The model routing table just needs remapping to your provider's model tiers.

## Pairs Well With

- **[recursive-decomposition-skill](https://github.com/massimodeluisa/recursive-decomposition-skill)** — For tasks that overflow context (10+ files, 50K+ tokens). /lean optimizes cost; recursive-decomposition handles scale.
- **[planning-with-files](https://github.com/OthmanAdi/planning-with-files)** — For persistent state across long sessions. /lean already persists to `.lean-plan.md`; planning-with-files adds hooks for auto-reading the plan before each tool call.
