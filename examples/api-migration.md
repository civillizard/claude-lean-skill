# Example: Migrate 8 API Endpoints to v2

Input: `/lean migrate all 8 REST endpoints from v1 to v2 with new auth middleware`

## Lean Execution Flow

**Task:** Migrate 8 REST endpoints from v1 to v2 with new auth middleware

| # | Piece | Draft | Gate | Reviewer | Why review | What |
|---|-------|-------|------|----------|------------|------|
| 1 | Explore current endpoints | Haiku | 0 | — | read-only, machine-checkable | Read all 8 endpoint files, summarize patterns, list auth differences |
| 2 | Design the shared auth middleware | Sonnet | 2-HIGH | Opus | every endpoint consumes it — a subtle bug here propagates to all 8 | Draft the middleware; Opus reviews the seam (token validation, error paths) before anything depends on it |
| 3 | Migrate `/users` endpoint | Sonnet | 0 | — | tests assert it | Rewrite users route with v2 patterns + the reviewed middleware |
| 4 | Validation gate | Haiku | 0 | — | — | Run `/users` tests + lint, report pass/fail |
| 5 | Migrate remaining 7 endpoints | Sonnet | 0 | — | same pattern, parallel | Apply v2 pattern to orders, products, payments, etc. |
| 6 | Final validation gate | Haiku | 0 | — | — | Full test suite + integration tests |

**Top-tier touches:** none — the one Opus review on the shared seam is enough here.
**Staging:** Test on `/users` first, validate, then expand to all 8.

---

## Why the middleware gets reviewed but the endpoints don't

The 7 remaining endpoints are **Gate 0** work: they follow the pattern set by
`/users`, and the test suite asserts they're correct. No judgment review — a cheap
drafter + the validation gate fully covers them.

The shared auth middleware is **Gate 2 / HIGH**: it's a contract all 8 endpoints
consume, so a subtle pitfall (a token-expiry edge case, a wrong error status) would
propagate everywhere before any single endpoint's tests caught it. That's exactly
the load-bearing seam worth one tier up — Opus reviews the middleware *segment*
(with its contract: who calls it, what it must guarantee) for judgment and missed
cases, not just "does it run."

Note the middleware is small enough to live in one file, so per the **net-negative
rule** the Sonnet-draft + Opus-review round-trip is borderline — for a seam this
size, having Opus *draft it directly* is often the cheaper, higher-quality move.
The conductor picks whichever fits; the point is the seam gets frontier judgment and
the 7 mechanical endpoints don't.
