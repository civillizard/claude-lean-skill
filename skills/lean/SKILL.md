---
name: lean
description: Route each step of a task to the cheapest capable model, and escalate only the load-bearing pieces to a pricier reviewer that catches pitfalls early. Decomposes work, assigns Haiku/Sonnet/Opus/Fable per step, reviews surgically, and persists the plan. Use /lean before complex tasks.
allowed_tools:
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---

# Lean Task Conductor

The strongest model you're running acts as the **conductor**: it designs the flow
of which model drafts what, in what sequence, and which pieces a pricier tier
*reviews* — to get the best quality at the least cost. This skill loads at ~100
tokens until invoked — it practices what it preaches.

Routing has two directions. Route **down** to cheaper tiers (Haiku/Sonnet) for
tractable work. Route **up** to the priciest tier only for the ≤2 *apex* junctions
per task where its cost is earned — to author a genuinely novel piece, or to
review the single highest-impact segment a cheaper tier drafted.

> **Tiers, cheapest → priciest:** Haiku · Sonnet · Opus · Fable. The top tier is
> roughly 2× the next one per token — so reach up only when it pays. (Map these to
> your provider's tiers; see Portability.)

## Usage

- `/lean <task description>` — Analyze the task and produce an optimized flow
- `/lean` (no args) — Ask the user what they're about to do, then plan it

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

### Step 2: The Engagement Floor — should the conductor even run?

The conductor has a fixed cost (reading context, writing the plan, the approval
round, scoped dispatch prompts). Below a threshold, that apparatus costs more than
it saves.

**Engage the conductor ONLY when the task has ≥3 distinct steps AND at least one
of: touches ≥2 files · contains a high-blast op · is a bulk operation.**

Below the floor → just do the task directly. Output a one-liner:
*"This is below the lean floor — I'll just do it. Proceed?"* and stop.

**Self-check:** if the routing rationale you're about to write is longer than the
cheapest tier's expected output delta, *you are the waste.* Cap plan prose —
one-phrase "why" cells, never essays.

Above the floor, gather context with direct tool calls (not subagents):
- Plan execution → read the plan/spec · feature → Glob/Grep the scope · research →
  identify what to search · bulk → count items + pick ONE representative test case.

### Step 3: Route each piece through THREE GATES, in order

Decompose the task into pieces. For each piece, apply the gates in sequence — the
first that resolves the piece wins. Most work resolves at Gate 0.

#### Gate 0 — Can a machine fully check it?

If a cheap mechanical check can *assert correctness* — tests pass, the output
parses, a query holds, the lint is clean — then blast radius is **neutralized by
the check** and no judgment review is needed.

→ **Cheapest capable drafter + a cheap validation gate.** Most work lands here.

| Piece shape | Drafter | Subagent? |
|---|---|---|
| Single file search/grep/read (1–2 calls) | **Direct** (main context) | No |
| Multi-file research, codebase mapping, content extraction | **Haiku** | Explore / general-purpose |
| Well-specced codegen, tests, mechanical refactor, clear plan execution | **Sonnet** | general-purpose |
| Validation after changes (run tests/lint, report pass/fail) | **Haiku** | Bash |

**Haiku drafts NEVER receive a judgment review.** Haiku is only for work the
mechanical gate fully covers. If a Haiku draft seems to *need* a judgment review,
it was mis-tiered — redraft it at Sonnet, don't paper over it with review.

#### Gate 1 — Is the approach decided?

If the *approach itself* is undecided (novel problem shape, a design that will be
iterated):
- **Undecided AND high/apex blast** → the **top tier authors** the piece directly.
- **Undecided but low blast** → the conductor just **decides inline** — iteration
  beats deliberation; being wrong is cheap. Novelty *alone* never earns the top
  tier; it needs blast radius too.

#### Gate 2 — Blast radius sets the REVIEW tier (decoupled from the drafter)

For a piece that's machine-uncheckable and approach-decided, the review tier is a
function of **what subtly-wrong costs**, NOT of "drafter + 1":

| Blast band (operational) | Review |
|---|---|
| **LOW** — one-commit revert, no production consumer | **Ship the draft.** No review. |
| **HIGH** — production branch · production DB write · a contract another component consumes · irreversible op · security boundary | **Mid-tier review** (e.g. Opus), regardless of who drafted |
| **APEX** — a wrong *design* propagates into downstream artifacts before detection: schema, public API, the security boundary itself | **Top-tier review** of the single highest-impact segment |

The reviewer critiques **judgment & pitfalls** — *is the approach right, what cases
are missed, does it honor its contract?* — NOT "does it run" (that's the Gate-0
validation gate, which is separate and complementary).

### Step 3.5: The net-negative rule — when draft→review costs MORE

Draft-by-cheaper-then-review-by-pricier is **only** cheaper than a single pricier
draft for **bulk generation**. The reason: the round-trip pays the shared context
*twice* (drafter reads it, reviewer reads it) plus two output streams; a single
direct draft pays the context once. For the typical small-diff-in-a-big-codebase
seam (context ≫ generated output), the round-trip costs **more AND is lower
quality** (handoff loss, plus the weaker tier still applies the revision).

**Rule:** if the load-bearing piece is **under ~150 lines / ~1–2K output tokens,
or lives in a single file → the higher tier DRAFTS IT DIRECTLY.** No round-trip.
Draft→review is for the 13-file rewrite; direct authorship is for the seam.

**One review round only.** The reviewer either approves, **patches directly**
(findings come as exact patches, not prose for a cheap tier to re-apply — a weak
tier misapplying a strong-tier finding is a corruption surface), or **takes
ownership** of the segment at its own tier. Never bounce a segment back for a
second cheap-tier drafting round — that's where the round-trip silently goes
net-negative.

### Step 3.6: Mid-flight escalation

The flow is decided up front, but the plan can be wrong about how tractable a piece
is. Handle it instead of paying retry loops at the cheap tier:
- **2 failed gate cycles at tier T on the same step → redo at T+1.**
- **A drafter report that contradicts a plan premise → STOP and re-examine the
  plan**, don't keep paying cheap-tier retries.

This is the standard fallback-router shape: start cheap, escalate on failure,
force the higher tier up front for categories known to be hard.

### Step 4: Apply Staging (bulk work)

For any task operating on multiple items:
1. Identify ONE representative item to test first.
2. Plan the test run as a separate step.
3. Add a Gate-0 **validation gate** after it (a cheap model runs tests + lint).
4. Only then plan expansion to all items (parallel subagents if independent).

Validation gates are mandatory between stages. If a gate fails, stop and fix
before continuing.

### Step 4.5: Calling the top tier — the review brief

The top tier is capped at **≤2 touches per task** (author or review). A 3rd touch
must name which earlier touch it *replaces*, or the task should be split. Minimize
**dispatches** — re-paid input context is the hidden cost, not just the per-token
tier.

**A top-tier reviewer never gets a bare segment.** A snippet-in-a-prompt review is
shallow and expensive (no probe, relitigates settled trade-offs). Package the
review brief with all six parts:

1. **The segment verbatim.**
2. **The contract** — callers, consumers, invariants it must preserve, where it runs.
3. **Settled decisions — do not relitigate** (the trade-offs already made).
4. **Pointed questions** — "is the failure-mode coverage of this seam right?",
   never "review this".
5. **Blast statement** — what breaks if it's subtly wrong, and how it would surface.
6. **Repo paths + budgeted probe rights (≤10 tool calls)** — instruct the reviewer
   to *verify the segment's claims against the actual code*, not reason over a
   paste. A reviewer that can run the `grep` that disproves the seam's premise is
   categorically deeper.

**Required first deliverable:** *"Is this the right segment, and what OUTSIDE it
does its correctness depend on?"* — segment-only review structurally misses
cross-segment bugs; the contract + this question catch the conductor's own
wrong-segment error cheaply, before the deep review.

**Output contract:** severity-ranked findings (BLOCKER / warn), each with a
re-runnable verify command; cannot-verify → flag, never assert. Treat any
line-anchored claim as a **lead** — re-derive it before applying to a persistent
artifact.

**Independence wrinkle:** if the conductor authored the spec a cheaper draft
implements, the conductor reviewing that draft only confirms its own mental model
— for apex pieces, the reviewer's scope must include *the spec*, not just the
draft-against-spec.

### Step 5: Present the Flow — gate approval through AskUserQuestion

Output the structured flow table, then gate approval through the
**AskUserQuestion** wizard — not a plain-text "Approve this plan?". The `Reviewer`
column is blank on most rows — that's the point: review is the surgical exception,
not the default.

```
## Lean Execution Flow

**Task:** [one-line description]

| # | Piece | Draft | Gate | Reviewer | Why review | What |
|---|-------|-------|------|----------|------------|------|
| 1 | Explore current state | Haiku | 0 | — | machine-checkable | Read X,Y,Z, summarize |
| 2 | Implement test case | Sonnet | 0 | — | tests assert it | Write code for [item] |
| 3 | Validation gate | Haiku | 0 | — | — | Run tests + lint, report |
| 4 | Wire the integration seam | Sonnet | 2-HIGH | Opus | consumed contract | Connect A→B |
| 5 | Expand to all items | Sonnet | 0 | — | same pattern | Apply to remaining N |
| 6 | Final validation | Haiku | 0 | — | — | Full test suite |

**Top-tier touches:** [N/2 — what each is for, or "none"]
**Staging:** Test on [item] first, validate, then expand to [N]
```

Then present the approval decision as an AskUserQuestion with options like:
- **Approve as planned** — execute with the assigned drafters + reviewers.
- **Tighten review** — drop a review (ship a draft) or downgrade a reviewer tier.
- **Add a review** — escalate a piece you think is higher-blast than assigned.
- **Adjust staging / revise** — change test case, gate placement, batch sizes (Other).

If the flow routes any **top-tier** touch, name the cost in that option's
description (the top tier is ~2× the next, plus a fresh dispatch re-pays context).

For repos auto-pulled into production, code-writing steps should run in a staging
worktree/branch as the agent's cwd — production only receives reviewed commits.

### Step 6: Persist the Flow

After approval, write the flow to `.lean-plan.md` in the working directory:
- Full flow table, drafter + reviewer assignments, staging strategy.
- Each step marked `[ ]` for progress tracking.
- **A back-end line per top-tier touch:** `found_blocker: yes/no` — so the ≤2 cap
  calibrates against evidence over time instead of staying a vibe.

This survives context compaction on long conversations and enables session resume.
Update checkboxes as steps complete (`[x]`).

### Step 7: Execute on Approval

1. Execute steps in order.
2. For each Task subagent, ALWAYS pass the `model` parameter as planned.
3. Announce each step: "**Step 2/6:** Spawning Sonnet agent for the rewrite…"
4. Apply scope discipline to every code-writing subagent: an explicit file
   allowlist, instruct it to *surface* unexpected drift rather than "helpfully"
   finishing it, an explicit push policy, and an atomic-commit boundary. Before
   pushing a subagent's output, verify the commit count and that each commit
   touches only allowlisted files.
5. At each **validation gate**, run validation and report before proceeding.
6. At each **review** (Gate 2), package the brief per Step 4.5, run the reviewer,
   fold findings in (one round only), and record `found_blocker` for a top-tier touch.
7. After the test-case step, pause and show results before expanding.
8. If a gate fails or a draft contradicts a premise, escalate per Step 3.6 — don't
   loop the cheap tier.
9. Update `.lean-plan.md` checkboxes as each step completes.

### Step 8: Completion Summary

Brief outcome: steps completed, model per step, review findings folded in, test
results, deviations. No dollar-savings estimation — per-step cost guesses are
theater; the routing + review discipline is the saving.

## Principles

- **The strongest tier conducts; reach up surgically.** Route down to
  Sonnet/Haiku for tractable work; reach up to the top tier only for the ≤2 apex
  junctions where it's earned.
- **Verifiability first.** A machine-checkable piece needs a cheap validation
  gate, not a pricey judgment review. Gate 0 resolves most work.
- **Review tier = blast radius, not drafter + 1.** Decoupled. Haiku drafts never
  get a judgment review; the top tier needs *both* novelty and blast.
- **Draft→review is for BULK only.** Small/single-file load-bearing piece → the
  higher tier drafts it directly. One review round; reviewer patches or owns.
- **Minimize dispatches.** Re-paid input context is the hidden cost. Review the
  *segment*, not the whole output — but always with its contract.
- **Escalate mid-flight, don't loop cheap.** 2 failed gates → tier+1; premise
  contradicted → re-examine.
- **No model = the session model.** Always specify `model` on the Agent tool — an
  omitted model inherits the (priciest) session model.
- **Quality gates between stages** · **persist the flow** · **AskUserQuestion for
  approval** · **parallel when independent, sequential when dependent.**

## Companion: Auto-Nudge Hook (Optional)

For always-on passive protection, add `task-model-guard.py` as a PreToolUse hook on
the Agent tool. It does two things:
1. **Model suggestion** — if a subagent is spawned without an explicit `model`, it
   classifies the prompt (regex-based, zero latency) and suggests a cheaper tier
   when appropriate. Never blocks.
2. **Lean nudge** — if the prompt looks like a multi-step task and no
   `.lean-plan.md` exists, it suggests running `/lean` first.

See `task-model-guard.py` in this repo for the implementation.

## Portability

This skill is designed for **Claude Code** but the patterns transfer:

| Component | Claude Code | Other AI tools |
|-----------|-------------|----------------|
| Tier ladder | Haiku / Sonnet / Opus / Fable | Map to your provider's tiers (e.g. mini / standard / frontier) |
| Subagent spawning | Agent tool with `model` param | Tool-specific (Cursor: @agent, Copilot: #agent) |
| Plan persistence | `.lean-plan.md` in working dir | Works anywhere — plain markdown |
| Validation gates | cheap Bash agent runs tests | Any cheap model can validate |
| Top-tier review brief | frontier model + repo probe rights | Any tool with a strongest tier + tool access |
| Auto-nudge hook | `task-model-guard.py` PreToolUse | Claude Code specific — not portable |

The three gates, the net-negative rule, staging, and the review brief work with any
AI coding tool — only the tier names need remapping.

## Pairs Well With

- **[recursive-decomposition-skill](https://github.com/massimodeluisa/recursive-decomposition-skill)** — For tasks that overflow context (10+ files, 50K+ tokens). /lean optimizes cost + quality; recursive-decomposition handles scale.
- **[planning-with-files](https://github.com/OthmanAdi/planning-with-files)** — For persistent state across long sessions. /lean already persists to `.lean-plan.md`; planning-with-files adds hooks for auto-reading the plan before each tool call.
