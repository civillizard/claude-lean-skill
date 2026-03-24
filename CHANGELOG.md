# Changelog

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
