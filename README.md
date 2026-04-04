# /lean — Stop Paying Opus Prices for Haiku Work

A Claude Code skill that plans your tasks with the right model for each step. Decomposes work, assigns Haiku/Sonnet/Opus per step, adds quality gates between stages, and shows you exactly how much you saved.

## Why

Claude Code defaults to Opus for everything — including reading files, running tests, and mechanical refactoring that Haiku or Sonnet handle just fine. On a 10-step task, that's easily 5-10x more expensive than it needs to be.

`/lean` fixes this by planning before executing:

```
/lean migrate 8 API endpoints to v2
```

```
## Lean Execution Plan

| # | Step             | Model  | Why                        | Agent Type      | What                          |
|---|------------------|--------|----------------------------|-----------------|-------------------------------|
| 1 | Explore endpoints| Haiku  | Read-only scan             | Explore         | Read all 8, summarize patterns|
| 2 | Migrate /users   | Sonnet | Clear spec from step 1     | general-purpose | Rewrite with v2 + new auth    |
| 3 | Quality gate     | Haiku  | Validate before scaling    | Bash            | Run tests + lint              |
| 4 | Migrate remaining| Sonnet | Same pattern, parallel     | general-purpose | Apply to remaining 7          |
| 5 | Final gate       | Haiku  | Catch regressions          | Bash            | Full test suite               |

Model mix: ~40% Haiku, ~50% Sonnet, ~10% Opus
Saved: ~83% vs all-Opus execution
```

## Features

- **Model routing table** — 12 task types mapped to the cheapest capable model, with rationale
- **Quick mode** — Simple tasks (<=3 steps) get a one-liner, not a full plan
- **Staged execution** — Test on one item, validate, then scale to all
- **Quality gates** — Haiku validates between every stage (catch errors cheap)
- **Plan persistence** — Writes `.lean-plan.md` so the plan survives context compaction
- **Savings report** — Shows per-step cost estimates vs all-Opus after execution
- **Auto-nudge hook** — Optional companion that suggests `/lean` when it detects complex tasks

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

## Model Routing Reference

The core routing table that `/lean` uses to assign models:

| Task Type | Model | Why |
|-----------|-------|-----|
| Single file search/read (1-2 calls) | **Direct** | Subagent overhead not worth it |
| Multi-step file research (3+ files) | **Haiku** | Read-only, no reasoning needed |
| Codebase mapping | **Haiku** | Mechanical enumeration |
| Codebase understanding (patterns) | **Sonnet** | Needs pattern recognition |
| Content extraction from large files | **Haiku** | Filter and summarize |
| Well-defined code generation | **Sonnet** | Capable when spec is clear |
| Writing/updating tests | **Sonnet** | Follows existing patterns |
| Mechanical plan execution | **Sonnet** | Steps pre-defined |
| Complex execution (ambiguous) | **Opus** | Judgment calls, trade-offs |
| Refactoring with clear transform | **Sonnet** | Transformation well-defined |
| Architecture, debugging, novel problems | **Opus** | Deepest reasoning needed |
| Validation/testing | **Haiku** | Just run tests, report |

## Typical Savings

| Task Type | Model Mix | Savings vs All-Opus |
|-----------|-----------|---------------------|
| Bulk refactoring (5+ files) | 40% Haiku / 50% Sonnet / 10% Opus | **70-85%** |
| Feature implementation | 30% Haiku / 50% Sonnet / 20% Opus | **50-70%** |
| Research + implementation | 50% Haiku / 40% Sonnet / 10% Opus | **75-85%** |
| Pure research/exploration | 80% Haiku / 20% Sonnet | **85-95%** |

## Portability

Designed for Claude Code, but the patterns transfer to other AI coding tools:

| Component | Claude Code | Other tools |
|-----------|-------------|-------------|
| Model routing table | Haiku / Sonnet / Opus | GPT-4o-mini / GPT-4o / o1 (or your provider's tiers) |
| Subagent spawning | Agent tool with `model` | Cursor: @agent, Copilot: #agent |
| Plan persistence | `.lean-plan.md` | Works anywhere (plain markdown) |
| Quality gates | Haiku Bash agent | Any cheap model can validate |
| Auto-nudge hook | PreToolUse hook | Claude Code specific |

## Pairs Well With

- **[recursive-decomposition-skill](https://github.com/massimodeluisa/recursive-decomposition-skill)** — For tasks that overflow context (10+ files, 50K+ tokens). /lean optimizes cost; recursive-decomposition handles scale.
- **[planning-with-files](https://github.com/OthmanAdi/planning-with-files)** — For persistent state across long sessions. /lean persists to `.lean-plan.md`; planning-with-files adds hooks for auto-reading plans.

## Examples

See the [`examples/`](examples/) directory for sample plans and savings reports.

## License

MIT

## Author & Contact

**Mamdoh AlOqiel** — Riyadh, Saudi Arabia

- **Email:** [mao@6ra3.com](mailto:mao@6ra3.com)
- **Issues & feedback:** [GitHub Issues](https://github.com/civillizard/claude-lean-skill/issues)
- **Contributions:** Pull requests welcome — open an issue first to discuss bigger changes

Open to collaboration on Claude Code tooling, token optimization, and AI workflow automation.
