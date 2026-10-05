# Blaque Baux Bankroll

**Systematic options income — and the first sell-side sleeve to escape "insurance-selling, not alpha," when it's done right.**

Bankroll is a member of the Blaque Baux family. It asks whether writing options for income earns its keep or just
caps your upside. Unlike naked short-vol (`brace`, `bushel` — landmines), a **covered** overlay keeps the
underlying, so the trade is premium-collected vs upside-surrendered. The answer splits sharply: *naive* always-write
is a drag, but *selective/active* writing is a real low-vol income edge.

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/bankroll_1_buywrite.py   # needs Alpaca data keys in the environment
```

## The finding (honest)

[`research/bankroll_1_buywrite.py`](research/bankroll_1_buywrite.py) — total return vs SPY, 2020→2026:

| | Sharpe | CAGR | maxDD | M² exc |
|---|---|---|---|---|
| SPY (index) | +1.06 | +18% | −24% | +0.0% |
| XYLD / QYLD / RYLD (naive buy-write) | +0.7–1.0 | +10–11% | −19 to −25% | **−1 to −6%** (drag) |
| **DIVO (active/selective)** | **+1.18** | +15% | **−14%** | **+2.0%** |
| JEPI (active) | +1.05 | +11% | −14% | −0.1% |

And **timing matters**: a gated SPY↔buy-write switch that **writes only in calm regimes** beats SPY (Sharpe +1.08,
M² +0.4%), while **writing when vol is "rich" is worse** (M² −2.0%) — because high vol coincides with the selloff,
so you write into the drop and cap the rebound.

## Verdict

**CONDITIONAL KEEPER — options income done right.** Naive always-write caps the upside for less than it's worth
(confirming `brace`), but **selective/active writing (DIVO-style) and calm-regime gating clear or beat the index
risk-adjusted at ~a third less drawdown** — and DIVO did it in a *bull* sample that structurally disadvantages
call-writing. The covered structure keeps the upside the naked short-vol sleeves threw away, so this is the first
sell-side exploration to escape the landmine. The honest niche: **lower-vol equity income for a drawdown-sensitive
holder**, with the writing *selective and gated to calm*, not blanket. (Total-return basis nets distributions, so a
fund that trails SPY was paying you your own capital back — the yield illusion.)

## Status
**Research — conditional keeper (active/gated); naive buy-write is a drag.** A governed low-vol-income rail is the
natural graduation. `bankroll_2` = selective-write construction on single names (DIVO-style) vs the ETF proxies.

## Layout
```
research/  _bankroll_common.py       — bars (total return) + fat-tail toolkit
           bankroll_1_buywrite.py    — the complex vs SPY + gated (calm vs rich) buy-write
```

## The Blaque Baux family
One sleeve of the **Blaque Baux** family. The [core repo](https://github.com/blaquebaux/base) is the
base/blueprint and holds the [full family roster](https://github.com/blaquebaux/base#the-blaquebaux-family).

## License
[MIT](LICENSE). (c) 2026 Carter Warrens.
