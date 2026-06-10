# Changelog

## 2.0.0 (2026-06-10)

Re-architected from a flat per-step model table into a **conductor with a surgical
draft → review escalation ladder**. The strongest model designs the flow; cheap
tiers draft; only load-bearing pieces are reviewed one tier up; the top tier is a
capped, called resource — not the default.

### Added
- **Three-gate router** per piece: Gate 0 (machine-checkable → cheapest drafter +
  validation gate), Gate 1 (approach decided?), Gate 2 (blast radius sets the
  review tier).
- **Draft → review escalation** for judgment & pitfalls (distinct from the
  "does-it-run" validation gate), with the review tier **decoupled from the
  drafter tier** (set by blast radius, not drafter+1).
- **The net-negative rule**: draft→review only pays for bulk; a small/single-file
  load-bearing piece is drafted directly by the higher tier.
- **Top-tier review brief**: segment + contract + settled-decisions + pointed
  questions + blast statement + budgeted repo probe rights, capped at ≤2 apex
  touches/task.
- **Mid-flight escalation**: 2 failed gate cycles → tier+1; a draft that
  contradicts a plan premise → re-examine instead of looping the cheap tier.
- **Engagement floor**: the conductor only runs above ~3 steps / 2 files / a
  high-blast or bulk op — below it, just do the task.
- **Fable** added as the top tier in the ladder.
- `Reviewer` / `Gate` columns in the flow table; `found_blocker` back-end line in
  `.lean-plan.md`.

### Changed
- Approval now always goes through the **AskUserQuestion** wizard.
- Repositioned from "minimize tokens / show savings" to "right model per step +
  catch pitfalls early."

### Removed
- **Savings report** (Step 8) and the per-step dollar estimates — the numbers were
  guesswork, and a cheaper run that ships a subtle bug isn't a saving. The routing
  + review discipline is the saving.

## 1.0.0 (2026-03-24)

Initial public release.

### Features
- Model routing table: 12 task types mapped to Haiku/Sonnet/Opus with rationale
- Quick mode: skips full plan for simple (<=3 step) tasks
- Staging: test-on-one, validate, then scale to all items
- Quality gates: mandatory Haiku validation between every stage
- Plan persistence: writes `.lean-plan.md` with checkboxes, survives context compaction
- Savings report: per-step cost estimates vs all-Opus baseline after execution
- Companion hook: `task-model-guard.py` auto-suggests lighter models + nudges `/lean` on complex tasks
- Portability section: model mapping guide for non-Claude providers
