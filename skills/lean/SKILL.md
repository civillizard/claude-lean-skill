---
name: lean
description: Two-path model routing — the session model conducts routine tasks inline; the top tier conducts apex tasks (schema, public API, migrations, novel architecture). Routes each piece to the cheapest capable model, escalates only load-bearing pieces to a pricier reviewer, and persists the plan. Use /lean before complex tasks.
allowed_tools:
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---

# Lean Task Conductor

`/lean` routes a task to the cheapest capable models and reserves pricier tiers for
where they're earned. It has **two conductor paths**, picked by a complexity label
at the floor gate:

- **Mid (routine)** — the **session model conducts inline** (decompose, route, flow
  table). The default, and the bulk of `/lean`.
- **Apex (high-stakes)** — the **top tier conducts**: schema, public API,
  migrations, edits to your agent's own rules/skills, novel architecture,
  multi-subsystem work — where a wrong *structure* propagates before anyone
  catches it.

The top tier is a **dispatched resource**, reached only on the apex path (one
conduct + at most one seam review) and at the apex review junctions below. This
skill loads at ~100 tokens until invoked — it practices what it preaches.

> **Tiers, cheapest → priciest:** Haiku · Sonnet · Opus · Fable. The examples assume
> an Opus session with Fable as the top tier; map these to your provider's tiers
> (see Portability). The top tier is roughly 2× the next one per token.

---

## Usage

- `/lean <task description>` — Analyze the task and produce an optimized execution flow.
- `/lean` (no args) — Ask the user what they're about to do, then plan it.

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

### Step 2: Floor gate — engage at all? and which path?

The conductor has a fixed cost (reading context, writing the plan table, the
approval round, scoped dispatch prompts — easily 2–5K tokens before any work
happens). Below a threshold, that apparatus costs more than it saves.

**Engage the conductor ONLY when the task has ≥3 distinct steps AND at least one
of: touches ≥2 files · contains a high-blast op · is a bulk operation.** Below the
floor → **just do the task directly.** Output a one-liner: *"This is below the lean
floor — I'll just do it. Proceed?"* and stop.

Above the floor, classify the task into a **complexity label** that picks the
conductor:

- **mid** — clears the floor, routing is obvious, NOT apex-blast → **the session
  model conducts inline** (Steps 3–8).
- **apex** — schema · public API · migration · edits to the agent's own
  rules/skills · novel architecture · multi-subsystem — a wrong *design* propagates
  into downstream artifacts before detection → **the top tier conducts** (Step 2.7,
  then rejoin Steps 5–8).
- **Tie-break:** if you genuinely can't tell mid from apex → **classify as apex.**
  Overpaying one top-tier conduct is far cheaper than silently missing a hard task's
  structural error.

Routine research (web/landscape scans, "what's out there") is the canonical **mid**
task — its routing is the known Haiku→Sonnet→conductor fan-out. Only
*novel-decomposition* research (the angles themselves are the hard part) is apex.

**Self-check:** if the routing rationale you're about to write is longer than the
cheapest tier's expected output delta, *you are the waste.* Cap plan prose —
one-phrase "why" cells, never essays.

Then gather context with direct tool calls (not subagents):
- Plan execution → read the plan/spec · feature → Glob/Grep the scope · research →
  identify what to search · bulk → count items + pick ONE representative test case.

On the **apex** path this gathered context becomes the **context package** (Step 2.7).

### Step 2.5: Budget is the user's call — don't route on it

Remaining quota or spend does **not** modulate model or parallelism choices, and is
never a reason to pause and ask "should I run this given the budget?". Assign models
purely by the gates below. If the user wants to slow down, pause, or push, they will
say so. (A status line showing usage is passive context, not a routing input.)

### Step 2.7: Apex path — the top tier conducts

Reached only when Step 2 labelled the task **apex** (including tie-breaks). Mid
tasks skip this step and go straight to Step 3.

1. **Pre-conduct prompt** (the one mandatory pre-dispatch interaction): confirm the
   apex call AND set the conductor's thinking level, **defaulted by the label**
   (apex → "ultrathink"), so it's a confirm, not a cold pick.
2. **Assemble the context package** from the Step 2 gather: task statement, gathered
   artifacts (plan files, greps), the representative item, environment facts
   (hosts, branches, staging). **This is ALL the top tier sees** — its completeness
   is load-bearing, because the human approval gate is the only downstream check,
   and a human cannot eyeball an *absence*.
3. **Dispatch the conduct to the top tier.** It returns: decomposition, per-piece
   drafter + review-tier assignments (via the rubric in Step 3), staging strategy,
   and AT MOST ONE recommended execution-time seam review.
   - **First deliverable is the gap-check:** it must open with *"here's what I'd
     need that I wasn't given."* If it names a gap, gather it and re-dispatch — a
     model naming a missing input beats a human failing to notice an absent one.
   - **Existing plan:** if a plan file already decomposes the task, the top tier
     **routes** the existing steps; it does NOT re-decompose from scratch.
   - **Honest framing for sensitive topics:** if the task touches an area a model
     may misread (security tooling, data collection, anything dual-use), state the
     legitimate context plainly in the brief so the reviewer engages the
     engineering substance.
   - Treat the output as a **lead**: re-derive any line-anchored claim before
     applying it to a persistent artifact.
4. **The session model presents + discusses** the returned flow conversationally,
   then proceeds to the approval gate (Step 5).

**Apex top-tier budget:** conduct = **1 touch, exempt from the review cap, capped at
1** (a re-conduct must *replace* the first, never stack). Execution seam review =
**≤1** (the conduct already did the structural pass; the review is only for
concrete seam-implementation correctness, not design).

**Fallback:** if the top tier is unavailable or can't be dispatched as a subagent,
apex tasks fall back to **session-model conduct with extra rigor**, and the approval
screen says so — `/lean` never breaks, it only loses the apex upgrade.

**Intake is the real lever.** The apex path only helps if apex work actually
**enters `/lean`**. When a task is apex-blast, either it goes through `/lean` (the
top tier conducts) or its plan gets a top-tier review before it lands — silently
doing neither is the drift to catch.

### Step 3: The routing rubric — applied by whoever conducts

The session model applies these on the mid path; the top tier applies them during
the apex conduct. Decompose the task into pieces; for each, apply the gates in
sequence. The first gate that resolves the piece wins — most work resolves at Gate 0.

**Optional: a lessons file.** If you keep one (e.g. `.lean-lessons.md`: per task
archetype, the lowest model that worked + the prompt pattern that made it work),
match each piece to an archetype FIRST. A matching entry overrides the gate defaults
below. **No clean match → use the gates; never force-fit a task into an archetype.**
Name any applied lesson in the flow table.

#### Gate 0 — Can a machine fully check it?

If a cheap mechanical check can *assert correctness* — tests pass, the output
parses, a set-equivalence query holds, the lint is clean — then blast radius is
**neutralized by the check** and no judgment review is needed.

→ **Cheapest capable drafter + a Haiku validation gate.** Most work lands here.

| Piece shape | Drafter | Subagent? |
|---|---|---|
| Single file search/grep/read (1–2 calls) | **Direct** (main context) | No |
| Multi-file research, codebase mapping, content extraction | **Haiku** | Explore / general-purpose |
| Well-specced codegen, tests, mechanical refactor, clear plan execution | **Sonnet** | general-purpose |
| Validation after changes (run tests/lint, report pass/fail) | **Haiku** | Bash |

**Haiku drafts NEVER receive a judgment review.** Haiku is only for work the
mechanical gate fully covers. If a Haiku draft seems to *need* a judgment review, it
was mis-tiered — redraft at Sonnet, don't paper over it with review.

#### Gate 1 — Is the approach decided?

If the *approach itself* is undecided (novel problem shape, a design that will be
iterated):
- **Undecided AND high/apex blast** → the **top tier authors** the piece directly.
- **Undecided but low blast** → the conductor **decides inline** — iteration beats
  deliberation; being wrong is cheap. Novelty *alone* never earns the top tier; it
  needs blast radius too.

#### Gate 2 — Blast radius sets the REVIEW tier (decoupled from the drafter)

For a piece that's machine-uncheckable and approach-decided, the review tier is a
function of **what subtly-wrong costs**, NOT of "drafter + 1":

| Blast band (operational) | Review |
|---|---|
| **LOW** — one-commit revert, no production consumer | **Ship the draft.** No review. |
| **HIGH** — auto-deployed branch · production DB write · a contract another component consumes · irreversible op · security boundary | **Mid-tier review** (e.g. Opus) by default; may **opt up** to the top tier under the guards below |
| **APEX** — a wrong *design* propagates into downstream artifacts before detection: schema, public API, the security boundary itself, the agent's own rule/skill layer | **Top-tier review** of the single highest-impact segment (on the apex path, this is the ≤1 seam review) |

The reviewer critiques **judgment & pitfalls** — *is the approach right, what cases
are missed, does it honor its contract?* — NOT "does it run" (that's the Gate-0
validation gate, which is separate and complementary).

**HIGH may opt up to a top-tier review — not the default.** When a *specific* HIGH
segment's subtly-wrong cost is closer to APEX than to routine (a consumed contract
whose breakage cascades, an irreversible production migration, a security-boundary
change), its review MAY escalate. Guards so the option doesn't quietly become the
default:
1. **Named reason** in the flow table and the approval question ("consumed by X + Y;
   a wrong contract breaks both"). No named reason → HIGH stays mid-tier.
2. **Record the outcome**: `found_blocker: y/n` per opt-up in the plan file.
3. **Calibrate with a real A/B, not a guess.** For the first ~5 opt-ups, run BOTH
   reviews independently (mid-tier first, then the top tier without seeing the
   mid-tier findings) and record the top tier's *marginal* findings. If that delta is
   empty or nit-level across the sample, drop the option.
4. **Rate tripwire:** if more than ~1 in 3 HIGH segments opt up, the band table is
   miscalibrated or the option is drifting default-on — re-examine. A segment class
   that opts up 3× with real blockers belongs in the APEX row.

#### Effort axis — scale THINKING per piece (orthogonal to model tier)

Model tier and **thinking level** are independent axes, and reasoning tokens are
billed too. Set thinking by the piece's **structure × blast** — thinking pays on
sequential, error-compounding, policy-dense work, not on crisp machine-checkable
steps however hard they feel:

- **Gate-0 mechanical** (tests / parse / lint / set-equivalence / clear plan
  execution) → **minimal / no** extended thinking.
- **Gate-2 HIGH judgment** → **"think hard"**.
- **Gate-1 author / Gate-2 APEX** → **"ultrathink"** (the apex conduct runs here too).

Subagents have **no thinking parameter** — encode it as an **in-prompt directive**
("ultrathink" / "think hard" / "no extended thinking") on the dispatch. Carry the
choice in the flow table's **Effort** column so it's visible and approvable.

### Step 3.5: The net-negative rule — when draft→review costs MORE

Draft-by-cheaper-then-review-by-pricier is **only** cheaper than a single pricier
draft for **bulk generation**. The round-trip pays the shared context `C` *twice*
plus two output streams; a single direct draft pays `C` once. For the typical
small-diff-in-a-big-codebase seam (context ≫ generated output), the round-trip costs
**more AND is lower quality** (handoff loss, plus the weaker tier still applies the
revision).

**Rule:** if the load-bearing piece is **under ~150 lines / ~1–2K output tokens, or
lives in a single file → the higher tier DRAFTS IT DIRECTLY.** No round-trip.
Draft→review is for the 13-file rewrite; direct authorship is for the seam.

**One review round only.** The reviewer either approves, **patches directly**
(findings come as exact patches, not prose for a cheap tier to re-apply — a weak
tier misapplying a strong-tier finding is a corruption surface), or **takes
ownership** of the segment at its own tier. Never bounce a segment back for a
second cheap-tier drafting round.

### Step 3.6: Mid-flight escalation

The flow is decided up front, but the plan can be wrong about tractability. Handle
it instead of paying retry loops at the cheap tier:
- **1st miss at tier T → improve the prompt, retry at the SAME tier T.** Most
  cheap-tier misses are prompt quality, not capability. Check the prompt: does it
  name the source of truth to read first? state what "done" looks like? ask for an
  adversarial self-check before reporting? (If you keep a lessons file, take the
  matching entry's pattern.) **2nd miss → escalate to T+1.**
- **Skip the same-tier retry and escalate/surface immediately when:** (a) a lessons
  entry already says this archetype needs a tier above T; (b) the step already
  committed or pushed a side effect — not a free retry, surface it; (c) a mid-tier
  miss on an apex-blast piece → surface to the human.
- **A drafter report that contradicts a plan premise → STOP and re-examine the
  plan** — highest precedence, before any retry.

This is the standard fallback-router shape: start cheap, score-gate, escalate on
failure, and force the higher tier up front for categories known to be hard.

### Step 4: Apply Staging (bulk work)

For any task operating on multiple items:
1. Identify ONE representative item to test first.
2. Plan the test run as a separate step.
3. Add a Gate-0 **validation gate** after it (Haiku runs tests + lint, reports
   pass/fail).
4. Only then plan expansion to all items (parallel subagents if independent).

Validation gates are mandatory between stages. If a gate fails, stop and fix before
continuing.

### Step 4.5: The top-tier review brief

Covers every top-tier review: the ≤1 apex seam review, an APEX-band review, and a
HIGH opt-up. (The conduct dispatch itself is Step 2.7.)

**A top-tier reviewer never gets a bare segment.** A snippet-in-a-prompt review is
shallow and expensive (no probe, relitigates settled trade-offs). Package the brief
with all six parts:

1. **The segment verbatim.**
2. **The contract** — callers, consumers, invariants it must preserve, where it runs.
3. **Settled decisions — do not relitigate** (the trade-offs already made).
4. **Pointed questions** — "is the failure-mode coverage of this seam right?",
   never "review this".
5. **Blast statement** — what breaks if it's subtly wrong, and how it would surface.
6. **Repo paths + budgeted probe rights (≤10 tool calls)** — instruct the reviewer to
   *verify the segment's claims against the actual code*, not reason over a paste.

**Required first deliverable:** *"Is this the right segment, and what OUTSIDE it
does its correctness depend on?"* — catches wrong-segment selection cheaply, before
the deep review.

**Output contract:** severity-ranked findings (BLOCKER / warn), each with a
re-runnable verify command; cannot-verify → flag, never assert. Treat the result as
a **lead**: re-derive any line-anchored claim before applying it.

**Independence wrinkle:** if the conductor authored the spec a cheaper draft
implements, the conductor reviewing that draft only confirms its own mental model —
for apex pieces, the reviewer's scope must include *the spec*, not just
draft-against-spec.

**Transport failure:** if a review dies on a network/API error, resume the same
agent once ("continue the same review; return the FULL report") rather than
re-dispatching — a re-dispatch re-pays the whole context.

### Step 5: Present the Flow — gate approval through AskUserQuestion

Output the structured flow table, then gate approval through **AskUserQuestion** —
never a plain-text "Approve this plan?". The `Reviewer` column is blank on most
rows — that's the point: review is the surgical exception, not the default.

```
## Lean Execution Flow

**Task:** [one-line description]   **Conductor:** [session model inline | top tier]

| # | Piece | Draft | Effort | Gate | Reviewer | Why review | What |
|---|-------|-------|--------|------|----------|------------|------|
| 1 | Explore current state | Haiku | min | 0 | — | machine-checkable | Read X,Y,Z, summarize |
| 2 | Implement test case | Sonnet | min | 0 | — | tests assert it | Write code for [item] |
| 3 | Validation gate | Haiku | min | 0 | — | — | Run tests + lint, report |
| 4 | Wire the integration seam | Sonnet | think hard | 2-HIGH | Opus | consumed contract | Connect A→B |
| 5 | Expand to all items | Sonnet | min | 0 | — | same pattern | Apply to remaining N |
| 6 | Final validation | Haiku | min | 0 | — | — | Full test suite |

**Top-tier touches:** [conduct + N/1 review — what each is for, or "none"]
**Staging:** Test on [item] first, validate, then expand to [N]
```

Then present the approval as an AskUserQuestion. Path-specific:

- **Mid path** — include an explicit escalation option: *"Escalate to top-tier
  conduct — I handled this as routine; if it's actually high-stakes, flip it and the
  top tier re-plans it as apex."* A misclassified apex task can always be caught
  here.
- **Apex path** — show **what the top tier was given** (the context-package summary)
  alongside the flow, so the human can spot a starved-context error. Fold any
  execution-time review thinking levels into this same screen.

Common options: **Approve as planned** · **Tighten review** (drop a review /
downgrade a tier) · **Add a review** · **Adjust staging / revise** (Other). If the
flow routes any top-tier touch, name the cost in that option's description (the top
tier is ~2× the next, plus a fresh dispatch re-pays context).

For repos auto-deployed to production, code-writing steps should run in a staging
worktree or branch as the agent's cwd — production only receives reviewed commits.

### Step 6: Persist the Flow

After approval, write the flow to `.lean-plan.md` in the working directory — **unless
that file already exists or is tracked by git** (some repos commit their plans); then
write `lean-plan-<task>.md` in a scratch location instead. Never overwrite another
task's plan.

- Full flow table, drafter + reviewer assignments, staging strategy.
- Each step marked `[ ]` for progress tracking.
- **Calibration lines** (they keep the apex branch honest — see the kill rule below):
  - `conductor: session | top-tier`
  - `conduct_thinking_level: <level>` (apex only)
  - `qanda_flow_modified: y/n` — `y` iff the approval answer was anything other than
    **Approve as planned** (mechanical — don't judge "how much" it changed).
  - `structural_issue_found: y/n` — did the conduct surface a non-obvious structural call?
  - `flipped_from_mid: y/n` — was this re-conducted as apex after a mid misclassification?
  - `found_blocker: y/n` — per top-tier review.
  - `lesson_applied: <archetype | none>` and `lesson_outcome: helped | neutral | wrong`
    (only if you keep a lessons file — so a lesson's gains aren't credited to the conduct).

This survives context compaction on long conversations and enables session resume.
Update checkboxes as steps complete (`[x]`).

**Kill rule for the apex branch.** A plan file is per task, so keep the cross-task
signal in a running log (one line per apex task, e.g. in `~/.lean-apex-log.md`):
`date · task · qanda_flow_modified · outcome (held / needed rework)` — written at
Step 8, when both are known. **If ≥2 of the last 5 apex tasks were flow-modified at
approval, or ≥2 of the last 5 needed rework, the apex branch isn't earning its
cost — revert to session-model conduct** rather than letting it run by default.

### Step 7: Execute on Approval

1. Execute steps in order.
2. For each subagent, ALWAYS pass the `model` parameter as planned — an omitted
   model inherits the (often priciest) session model.
3. Announce each step: "**Step 2/6:** Spawning Sonnet agent for the rewrite…"
4. Apply scope discipline to every code-writing subagent: an explicit file
   allowlist, instruct it to *surface* unexpected drift rather than "helpfully"
   finishing it, an explicit push policy, and an atomic-commit boundary. Before
   pushing a subagent's output, verify the commit count and that each commit touches
   only allowlisted files.
5. At each **validation gate**, run validation and report before proceeding.
6. At each **top-tier review**, package the brief per Step 4.5, run the reviewer,
   fold findings in (one round only), and record `found_blocker`.
7. After the test-case step, pause and show results before expanding.
8. If a gate fails or a draft contradicts a premise, escalate per Step 3.6 — don't
   loop the cheap tier.
9. Update `.lean-plan.md` checkboxes as each step completes.

### Step 8: Completion Summary

Brief outcome: steps completed, model per step, review findings folded in, test
results, deviations. No dollar-savings estimation — per-step cost guesses are
theater; the routing + review discipline is the saving.

**Apex path:** append this task's line to the apex log now (Step 6 kill rule) — the
approval answer and the outcome both exist only at this point.

**Lesson harvest (only if you keep a lessons file, and only when a candidate
exists).** If a model underdelivered in a way better information or prompting (not a
capability ceiling) would have fixed, record the archetype + the prompt pattern that
worked. Raising an archetype's minimum tier is authoritative; lowering one should
wait for a confirming run at the lower tier.

## Principles

- **Two paths: the session model conducts mid inline; the top tier conducts apex.**
  Ties go to apex.
- **Never decide the path silently.** The mid approval screen always offers
  "escalate to top-tier conduct".
- **The conduct is exempt from the review cap, but capped at 1**; apex execution
  review is ≤1 (the conduct covers the structural half).
- **Context-package completeness is load-bearing** — the top tier reports gaps as its
  first deliverable; the approval screen shows the human what it was given.
- **Verifiability first.** A machine-checkable piece needs a cheap validation gate,
  not a pricey judgment review. Gate 0 resolves most work.
- **Review tier = blast radius, not drafter + 1.** Haiku drafts never get a judgment
  review; the top tier needs *both* novelty and blast.
- **Right-size thinking, not just model tier.** Gate-0 pieces get minimal/no
  thinking; only judgment/apex earns "think hard"/"ultrathink".
- **Draft→review is for BULK only.** Small/single-file load-bearing piece → the
  higher tier drafts it directly. One review round; reviewer patches or owns.
- **Minimize dispatches.** Re-paid input context is the hidden cost. Review the
  *segment*, not the whole output — but always with its contract.
- **Better prompt before bigger model.** 1st miss → improve the prompt at the same
  tier; 2nd miss → tier+1; premise contradicted → re-examine the plan.
- **Budget is the user's call** — route by the gates, not by remaining quota.
- **Calibrate against evidence.** Calibration lines + the kill rule keep the apex
  branch honest.
- **Quality gates between stages** · **persist the flow** · **AskUserQuestion for
  approval** · **parallel when independent, sequential when dependent.**

## Companion: Auto-Nudge Hook (Optional)

For always-on passive protection, add `task-model-guard.py` as a PreToolUse hook on
the Agent tool. It does two things:
1. **Model suggestion** — if a subagent is spawned without an explicit `model`, it
   classifies the prompt (regex-based, zero latency) and suggests a cheaper tier when
   appropriate. Set `LEAN_SESSION_MODEL` (`haiku` · `sonnet` · `opus` · `fable`) to
   your session model and it only ever suggests tiers *cheaper* than that — e.g. with
   `fable`, complex delegated work gets an `opus` suggestion. Never blocks.
2. **Lean nudge** — if the prompt looks like a multi-step task and no `.lean-plan.md`
   exists, it suggests running `/lean` first.

See `hooks/task-model-guard.py` in this repo for the implementation.

## Portability

This skill is designed for **Claude Code** but the patterns transfer:

| Component | Claude Code | Other AI tools |
|-----------|-------------|----------------|
| Tier ladder | Haiku / Sonnet / Opus / Fable | Map to your provider's tiers (e.g. mini / standard / frontier / top) |
| Two conductor paths | session model + dispatched top tier | Any tool that can dispatch a stronger model |
| Subagent spawning | Agent tool with `model` param | Tool-specific (Cursor: @agent, Copilot: #agent) |
| Plan persistence | `.lean-plan.md` in working dir | Works anywhere — plain markdown |
| Validation gates | cheap Bash agent runs tests | Any cheap model can validate |
| Top-tier review brief | frontier model + repo probe rights | Any tool with a strongest tier + tool access |
| Auto-nudge hook | `task-model-guard.py` PreToolUse | Claude Code specific — not portable |

The gates, the net-negative rule, staging, the review brief and the apex kill rule
work with any AI coding tool — only the tier names need remapping.

## Pairs Well With

- **[recursive-decomposition-skill](https://github.com/massimodeluisa/recursive-decomposition-skill)** — For tasks that overflow context (10+ files, 50K+ tokens). /lean optimizes cost + quality; recursive-decomposition handles scale.
- **[planning-with-files](https://github.com/OthmanAdi/planning-with-files)** — For persistent state across long sessions. /lean already persists to `.lean-plan.md`; planning-with-files adds hooks for auto-reading the plan before each tool call.
