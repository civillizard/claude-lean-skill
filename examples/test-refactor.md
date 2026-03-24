# Example: Migrate Tests from Jest to Vitest

Input: `/lean migrate 15 test files from Jest to Vitest`

## Lean Execution Plan

**Task:** Migrate 15 test files from Jest to Vitest

| # | Step | Model | Why | Agent Type | What |
|---|------|-------|-----|------------|------|
| 1 | Explore test patterns | Haiku | Read-only scan | Explore | Read all 15 test files, list Jest-specific APIs used (mocks, timers, snapshots) |
| 2 | Migrate `auth.test.ts` | Sonnet | Most Jest features in one file | general-purpose | Convert Jest APIs to Vitest equivalents |
| 3 | Quality gate | Haiku | Validate the pattern works | Bash | Run `vitest auth.test.ts`, report pass/fail |
| 4 | Migrate remaining 14 files | Sonnet | Mechanical — same transforms | general-purpose | Apply pattern to all remaining test files (3 parallel agents, ~5 files each) |
| 5 | Final quality gate | Haiku | Catch regressions | Bash | Run full `vitest` suite |
| 6 | Cleanup | Haiku | Verify no Jest remnants | Explore | Grep for remaining `jest.` references, check package.json |

**Model mix:** ~50% Haiku, ~50% Sonnet, ~0% Opus
**Staging:** Test on `auth.test.ts` first (has mocks + snapshots + timers), validate, then expand

---

## Quick Mode Example

Input: `/lean add a health check endpoint`

> This is a **Sonnet** task — single endpoint with clear spec, no bulk items. Proceed?
