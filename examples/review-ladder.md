# Example: The Draft → Review Escalation Ladder

This example shows the core idea that replaced the old savings report: a cheaper
model drafts, and a pricier tier reviews *only the load-bearing pieces* — for
judgment and pitfalls a cheaper model misses.

Input: `/lean add a refund flow to the payments service`

## Lean Execution Flow

**Task:** Add a refund flow (idempotent, partial-refund aware) to the payments service

| # | Piece | Draft | Gate | Reviewer | Why review | What |
|---|-------|-------|------|----------|------------|------|
| 1 | Map the existing charge flow | Haiku | 0 | — | read-only | Read the charge/webhook code, summarize state transitions |
| 2 | Refund idempotency + partial-refund logic | Opus | 1 (APEX) | Fable | money + irreversible + idempotency edge cases propagate silently | Author directly at Opus (novel + high-blast); Fable reviews the segment |
| 3 | Refund API endpoint | Sonnet | 0 | — | tests assert it | Wire the endpoint to the reviewed logic |
| 4 | Validation gate | Haiku | 0 | — | — | Run refund tests + lint |
| 5 | Webhook handler for async refund settle | Sonnet | 2-HIGH | Opus | consumed contract, async ordering | Draft handler; Opus reviews ordering/retry edge cases |
| 6 | Final validation gate | Haiku | 0 | — | — | Full suite + a double-refund integration test |

**Top-tier touches:** 1/2 — Fable reviews the idempotency segment (step 2 is money + irreversible).
**Staging:** Single-refund path first, validate, then the partial + async settle paths.

---

## How the gates decided each piece

- **Steps 1, 3, 4, 6 — Gate 0.** Reading code, wiring a tested endpoint, running the
  suite. Machine-checkable → cheapest capable drafter, no judgment review.
- **Step 2 — Gate 1, APEX.** Refund idempotency is *novel* (this codebase has no
  pattern for it) **and** high-blast (money, irreversible, silent double-refunds).
  Novelty + blast → the top of the ladder is involved. Opus **authors** it; because
  a wrong design here is the worst case in the whole task, **Fable reviews** that one
  segment — handed the segment verbatim, its contract (who calls refund, what
  "idempotent" must guarantee), the settled decisions, and probe rights to check the
  charge code itself. Its first answer must be *"is this even the right segment, and
  what outside it does correctness depend on?"*
- **Step 5 — Gate 2, HIGH.** The webhook handler isn't novel, but it's a consumed
  contract with async ordering hazards. One tier up (Opus) reviews the ordering/retry
  edge cases. Not APEX — a bug is recoverable and the integration test will surface
  most of it — so Fable isn't needed here.

## What this buys you

Frontier judgment lands on exactly two places — the idempotency core (Fable) and the
async seam (Opus) — while the endpoint, the wiring, and the validation stay cheap.
You're not paying top-tier prices to read files or run tests, and you're not shipping
a money-handling edge case that only a strong reviewer would have caught.
