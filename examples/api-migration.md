# Example: Migrate 8 API Endpoints to v2

Input: `/lean migrate all 8 REST endpoints from v1 to v2 with new auth middleware`

## Lean Execution Plan

**Task:** Migrate 8 REST endpoints from v1 to v2 with new auth middleware

| # | Step | Model | Why | Agent Type | What |
|---|------|-------|-----|------------|------|
| 1 | Explore current endpoints | Haiku | Read-only scan of route files | Explore | Read all 8 endpoint files, summarize patterns, list auth differences |
| 2 | Migrate `/users` endpoint | Sonnet | Clear spec from step 1 findings | general-purpose | Rewrite users route with v2 patterns + new auth |
| 3 | Quality gate | Haiku | Validate before scaling | Bash | Run `/users` tests + lint |
| 4 | Migrate remaining 7 endpoints | Sonnet | Same pattern, can parallelize | general-purpose | Apply v2 pattern to orders, products, payments, etc. |
| 5 | Final quality gate | Haiku | Catch regressions across all routes | Bash | Full test suite + integration tests |

**Model mix:** ~40% Haiku, ~50% Sonnet, ~10% Opus
**Staging:** Test on `/users` first, validate, then expand to all 8

---

## Lean Savings Report

| Step | Model Used | Est. Input | Est. Output | Cost    | If All-Opus |
|------|-----------|------------|-------------|---------|-------------|
| 1    | Haiku     | ~4K        | ~2K         | $0.011  | $0.210      |
| 2    | Sonnet    | ~6K        | ~4K         | $0.078  | $0.390      |
| 3    | Haiku     | ~2K        | ~0.5K       | $0.004  | $0.068      |
| 4    | Sonnet    | ~20K       | ~15K        | $0.285  | $1.425      |
| 5    | Haiku     | ~3K        | ~1K         | $0.006  | $0.120      |
| **Total** |      |            |             | **$0.38** | **$2.21** |

**Saved: ~83% vs all-Opus execution**
