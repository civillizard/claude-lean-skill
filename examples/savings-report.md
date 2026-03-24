# Example: Savings Report

After `/lean` finishes executing a plan, it outputs a savings report like this:

## Lean Savings Report

| Step | Model Used | Est. Input | Est. Output | Cost    | If All-Opus |
|------|-----------|------------|-------------|---------|-------------|
| 1    | Haiku     | ~8K        | ~3K         | $0.018  | $0.345      |
| 2    | Haiku     | ~5K        | ~2K         | $0.012  | $0.225      |
| 3    | Sonnet    | ~10K       | ~8K         | $0.150  | $0.750      |
| 4    | Haiku     | ~3K        | ~1K         | $0.006  | $0.120      |
| 5    | Sonnet    | ~15K       | ~12K        | $0.225  | $1.125      |
| 6    | Haiku     | ~4K        | ~1K         | $0.007  | $0.135      |
| **Total** |      | ~45K       | ~27K        | **$0.42** | **$2.70** |

**Saved: ~84% vs all-Opus execution**

## How Estimates Work

Token counts are rough estimates based on typical sizes for each step type:
- **Explore steps:** 3-8K input (file contents), 1-3K output (summary)
- **Code generation:** 5-15K input (context + spec), 3-12K output (code)
- **Validation:** 2-4K input (test command + context), 0.5-1K output (pass/fail)

Pricing (per 1M tokens, March 2026):
| Model | Input | Output |
|-------|-------|--------|
| Haiku | $0.80 | $4.00 |
| Sonnet | $3.00 | $15.00 |
| Opus | $15.00 | $75.00 |

The **percentage** is the key metric — exact dollar amounts will vary by task complexity.

## Typical Savings by Task Type

| Task Type | Typical Model Mix | Savings vs All-Opus |
|-----------|-------------------|---------------------|
| Bulk refactoring (5+ files) | 40% Haiku / 50% Sonnet / 10% Opus | 70-85% |
| Feature implementation | 30% Haiku / 50% Sonnet / 20% Opus | 50-70% |
| Research + implementation | 50% Haiku / 40% Sonnet / 10% Opus | 75-85% |
| Pure research/exploration | 80% Haiku / 20% Sonnet / 0% Opus | 85-95% |
