# /lean — Route cheap, review smart

A Claude Code skill that turns your strongest model into a **conductor**: it routes
each step of a task to the cheapest capable model, and escalates *only the
load-bearing pieces* to a pricier tier that reviews for pitfalls a cheaper model
misses. Decomposes work, assigns Haiku/Sonnet/Opus/Fable per step, reviews
surgically, and persists the plan.

## Why

Coding agents default to the top model for everything — including reading files,
running tests, and mechanical refactoring that cheaper tiers handle just fine. The
fix isn't only "use a cheaper model"; it's two-directional:

- **Route down** — cheap tiers draft tractable work (most of it).
- **Route up — but surgically** — a cheaper model drafting a load-bearing seam will
  miss subtle pitfalls; a pricier reviewer catches them early. Reviewing
  *everything* one tier up roughly doubles cost, so the whole value is in the
  **gating**: review only the impactful pieces, and reserve the top tier for the
  ≤2 apex junctions per task where it's earned.

```
/lean migrate 8 API endpoints to v2
```

```
## Lean Execution Flow

| # | Piece              | Draft  | Gate   | Reviewer | Why review        | What                          |
|---|--------------------|--------|--------|----------|-------------------|-------------------------------|
| 1 | Explore endpoints  | Haiku  | 0      | —        | machine-checkable | Read all 8, summarize patterns|
| 2 | Migrate /users     | Sonnet | 0      | —        | tests assert it   | Rewrite with v2 + new auth    |
| 3 | Validation gate    | Haiku  | 0      | —        | —                 | Run tests + lint              |
| 4 | Shared auth middleware | Sonnet | 2-HIGH | Opus | consumed by all 8 | Review the seam before scaling|
| 5 | Migrate remaining  | Sonnet | 0      | —        | same pattern      | Apply to remaining 7          |
| 6 | Final gate         | Haiku  | 0      | —        | —                 | Full test suite               |

Top-tier touches: none — Opus review on the one shared seam is enough here.
```

Most rows have no reviewer. That's the point — review is the surgical exception.

## How it routes — three gates per piece

1. **Gate 0 — machine-checkable?** If tests / a parser / a query can fully assert
   correctness, the cheapest capable model drafts it + a cheap validation gate runs.
   No judgment review. *Most work lands here.*
2. **Gate 1 — approach decided?** If the approach is novel *and* high-blast, the top
   tier authors it directly. Novel but low-blast → just decide inline (iteration
   beats deliberation).
3. **Gate 2 — blast radius sets the review tier**, decoupled from who drafted:
   LOW → ship the draft · HIGH (production branch / DB / a consumed contract /
   irreversible) → mid-tier review · APEX (a wrong design propagates into schema /
   public API / security boundary) → top-tier review of the single highest-impact
   segment.

## Features

- **Three-gate router** — verifiability → tractability → blast radius, applied per piece
- **Draft → review escalation** — load-bearing pieces reviewed one tier up for *judgment & pitfalls*, not just "does it run"
- **The net-negative rule** — draft→review only pays for bulk; a small/single-file seam gets drafted directly by the higher tier (the round-trip would cost more)
- **Surgical top-tier use** — capped at ≤2 apex touches/task, with a structured review brief + repo probe rights so the review is deep, not a shallow paste-read
- **Engagement floor** — below ~3 steps / 2 files, the conductor stays out of the way
- **Staged execution** — test on one item, validate, then scale to all
- **Validation gates** — a cheap model validates between every stage (catch errors cheap)
- **Plan persistence** — writes `.lean-plan.md` so the flow survives context compaction
- **Auto-nudge hook** — optional companion that suggests `/lean` and a cheaper model when it detects complex tasks

## Install

### Option 1: Copy the skill (simplest)

```bash
cp -r skills/lean ~/.claude/skills/lean
```

### Option 2: Clone and symlink

```bash
git clone https://github.com/civillizard/claude-lean-skill.git ~/.claude/skills/lean-repo
ln -s ~/.claude/skills/lean-repo/skills/lean ~/.claude/skills/lean
```

Restart Claude Code after installing.

### Optional: Install the auto-nudge hook

Add to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Agent",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/skills/lean-repo/hooks/task-model-guard.py"
          }
        ]
      }
    ]
  }
}
```

The hook does two things:
1. **Suggests lighter models** when a subagent spawns without an explicit `model` parameter
2. **Nudges `/lean`** when it detects a multi-step task and no `.lean-plan.md` exists

It never blocks — only suggests.

## Drafter Routing Reference (Gate 0)

The default drafter for tractable, machine-checkable work:

| Task Type | Drafter | Why |
|-----------|---------|-----|
| Single file search/read (1-2 calls) | **Direct** | Subagent overhead not worth it |
| Multi-step file research (3+ files) | **Haiku** | Read-only, no reasoning needed |
| Codebase mapping | **Haiku** | Mechanical enumeration |
| Content extraction from large files | **Haiku** | Filter and summarize |
| Well-defined code generation | **Sonnet** | Capable when spec is clear |
| Writing/updating tests | **Sonnet** | Follows existing patterns |
| Mechanical plan execution | **Sonnet** | Steps pre-defined |
| Refactoring with clear transform | **Sonnet** | Transformation well-defined |
| Validation/testing | **Haiku** | Just run tests, report |

When a piece is *not* machine-checkable, Gate 1/2 decide whether it's authored or
reviewed by a pricier tier — see the [skill](skills/lean/SKILL.md) for the full logic.

## Why not just report the savings?

Earlier versions of this skill ended with a per-step dollar "savings report." It was
dropped: the per-token estimates were guesswork, and a cheaper run that ships a
subtle bug isn't a saving. **The routing + surgical review discipline is the
saving** — you pay frontier prices only on the pieces where being wrong is
expensive, and cheap prices everywhere else.

## Works on subscription, API, or hybrid

The routing applies however you're billed — only the *unit you're conserving* changes:

- **API (pay-per-token):** cheaper tiers cost fewer dollars; you pay frontier prices only on the load-bearing pieces.
- **Subscription (Claude Code on a Pro/Max plan):** usage limits are weighted by model — the top tier draws down your 5-hour and weekly limits far faster than Haiku/Sonnet. Routing down stretches how much you get done before hitting a limit, and the surgical reviews spend your scarce top-tier budget only where it matters.
- **Hybrid (subscription with API fallback, or mixing both):** both effects apply — and the engagement floor + ≤2 top-tier cap keep either budget from being burned on orchestration overhead.

In all three, the draft → review ladder is also a **quality** mechanism (catch pitfalls early), which pays off regardless of how you're billed.

## Portability

Designed for Claude Code, but the patterns transfer to other AI coding tools:

| Component | Claude Code | Other tools |
|-----------|-------------|-------------|
| Tier ladder | Haiku / Sonnet / Opus / Fable | mini / standard / frontier (your provider's tiers) |
| Subagent spawning | Agent tool with `model` | Cursor: @agent, Copilot: #agent |
| Plan persistence | `.lean-plan.md` | Works anywhere (plain markdown) |
| Validation gates | cheap Bash agent | Any cheap model can validate |
| Top-tier review brief | frontier model + repo probe rights | Any tool with a strongest tier + tool access |
| Auto-nudge hook | PreToolUse hook | Claude Code specific |

The three gates, the net-negative rule, staging, and the review brief work with any
AI coding tool — only the tier names need remapping.

## Pairs Well With

- **[recursive-decomposition-skill](https://github.com/massimodeluisa/recursive-decomposition-skill)** — For tasks that overflow context (10+ files, 50K+ tokens). /lean optimizes cost + quality; recursive-decomposition handles scale.
- **[planning-with-files](https://github.com/OthmanAdi/planning-with-files)** — For persistent state across long sessions. /lean persists to `.lean-plan.md`; planning-with-files adds hooks for auto-reading plans.

## Examples

See the [`examples/`](examples/) directory for sample flows.

## License

MIT

## Author & Contact

**Mamdoh AlOqiel** — Riyadh, Saudi Arabia

- **Email:** [mao@6ra3.com](mailto:mao@6ra3.com)
- **Issues & feedback:** [GitHub Issues](https://github.com/civillizard/claude-lean-skill/issues)
- **Contributions:** Pull requests welcome — open an issue first to discuss bigger changes

Open to collaboration on Claude Code tooling, token optimization, and AI workflow automation.
