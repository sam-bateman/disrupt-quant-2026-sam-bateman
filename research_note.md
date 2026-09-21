# Sector-neutral carry in a synthetic 24-asset market

Sam Bateman · Disrupt Quant 2026 · 2026-09-20

## 1. Hypothesis

Assets with a persistently high "carry_score" will earn a small, steady premium over assets with a low one, and the premium is best captured within each sector so that sector and market moves cancel.
In real markets carry is the return for holding: a coupon in bonds or a dividend in equities. This market is synthetic and the actual mechanism is not visible, but the designers labelled the column carry, made 
it slow-moving, and a slow characteristic is the natural place for a premium to sit. This is something I wanted to explore.

## 2. Evidence

I scanned every provided column on development data only (Jan 2021 - Jun 2024). Each day I ranked the 24 assets by the respective column  value and by the return they would earn if bought at the next open(column/t+1 bps), 
and correlated the two rankings to give it an rank IC. 
Three columns had |IC rank| > 2 with the same sign every year(meaning the coefficent would be viable across the years); everything else was noise, despite their  names like sentiment and flow.

| Signal | Direction | 1-day IC | 5-day IC | Names switching side per day |
|---|---|---|---|---|
| return_1d | reversal | -0.048 (-6.5) | -0.010 (-0.6) | 12.4 of 24 |
| carry_score | buy high | +0.024 (+3.4) | +0.044 (+2.9) | 0.9 of 24 |
| return_5d | reversal | -0.018 (-2.6) | +0.002 (0.1) | 5.3 of 24 |

Sorted into four carry buckets, next-day return rose like a stair case: -1.7, +1.5, +2.6, +4.1 bps/day. Top minus bottom earned 5.8 bps/day and was positive on only 52% of days. This was the small, consistent edge I hypothesized.
One-day reversal was the strongest signal but flips half the book daily, which is very expensive to trade.
Conflicting evidence: the carry edge was strong in 2023 and weaker in 2021–22 and the first half of 2024, so it was not uniform but keep the same direction of IC rank.

## 3. Construction

Every fifth session(day), rank the four assets in each sector by "carry_score". Long the top two, short the bottom two. Size each position by the inverse of its assets 20-day realized volatility, then scale so every sector is dollar-neutral, 
the whole book is dollar-neutral, and gross exposure is 100%. Hold the weights between rebalances(5d periods). Parameters were fixed before any backtest: 5-session cadence to limit churn(and cost), gross 1.0(100%) as a conservative default 
well inside the 200% limit, two names per side because a sector only has four assets. All to avoid overfitting.

## 4. Risk

Maximum single-asset weight is about 6%, far inside the 20% limit. Sector nets are zero by construction, so no sector or market bet can decide the outcome. Development annual volatility was 3.9% and the worst drawdown 3.2%. 
All six sectors contributed positively over development; the largest single-asset contribution was 3.9% of NAV. 
Expected failure: the carry premium fades or reverses, in which case the book earns roughly zero minus costs. Zero cash yield and no borrow cost are simplifications; a short book of 50% would carry real financing cost.

## 5. Costs

Costs use the rules spread-plus-impact formula from the previous close. Turnover was 14.5x per year, mostly small rebalancing trades as volatilities drift. Total development cost 3.2% of NAV over 3.5 years, about 0.9% a year.

| Cost multiplier | 1.0x | 1.5x | 2.0x |
|---|---|---|---|
| Development Sharpe | 1.34 | 1.23 | 1.11 |
| Total costs | 3.2% | 4.7% | 6.3% |

Costs shaped two decisions. First, one-day reversal were ignored: on development it loses in every window after costs (Sharpe -2.6, turnover 271x, costs 55% of NAV over the period, just horrible), even at 60% gross. 
Second, I tested down-weighting wide-spread names (divide by sqrt of spread): costs fell 15% but Sharpe fell from 1.34 to 1.17, so it was rejected.

## 6. Validation

| Window | Sharpe | Total return | Max DD | Positive months |
|---|---|---|---|---|
| Dev tune 2021–2022 | 0.89 | +7.4% | -3.2% | |
| Dev hold-out 2023–Jun 2024 | 2.00 | +11.8% | -2.5% | |
| Development, all | 1.34 | +20.2% | -3.2% | 29 of 42 |
| **Validation Jul–Dec 2024, frozen** | **-1.75** | **-3.6%** | **-5.7%** | 2 of 6 |

The strategy was frozen and validation was run once. The carry rank IC by period was +0.013 (2021–22), +0.047 (2023), +0.024 (H1 2024) and -0.008 in validation. The signal itself faded to zero; costs were 0.4% and construction held 
(five of six sectors lost, no single name dominated). 
Sensitivity on development: rebalance every 1/3/5/10/20 sessions gave Sharpe 1.09/1.17/1.34/1.28/1.24; gross 0.6/1.0/1.4 gave 1.35/1.34/1.34; one name per side instead of two gave 1.14. 

## 7. Limitations

The edge is small (about 5 bps/day gross) and regime-dependent. It was carried by 2023 and had already weakened before validation. The scan's 16 signals times two horizons is a mild multiple-testing risk, mitigated by requiring the 
same sign in every year and a monotonic bucket pattern. The mechanism behind "carry_score" is unknown, so there is no economic reason to expect it to return in 2025. Reversal signals strengthened in validation (return_1d IC -0.11) 
but remain untradable at these cost levels. If 2025 resembles late 2024, this strategy will lose a few percent; if it resembles 2023, it will earn 5–10% at low volatility.

## 8. Next step

Test a simple on/off switch: hold the carry book only when the trailing 60-day carry IC is positive, otherwise sit in cash. It is one line of logic, it would have cut exposure in late 2024, and it can be evaluated on development without 
touching validation again.
