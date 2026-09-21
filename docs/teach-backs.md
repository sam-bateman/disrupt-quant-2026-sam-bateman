# Teach-backs

Sam's own explanations after each step. Raw material for the research note and interview.

## 1. Setup

Baseline (equal-weight, 100% long all 24 assets, development 2021-01 to 2024-06, run 2026-09-18):
- Sharpe 0.42, annualized return 4.2%, annualized volatility 11.3%
- Max drawdown -11.0%, hit rate 50.5%
- Annualized turnover 2.4x, total transaction costs 0.45% of NAV over 3.5 years

Sam's explanation (2026-09-18):
At the close of each day the backtester takes that day's data and asks the strategy for target weights. It does not trade until the open of day t+1, so only positions already held capture the overnight move. At the open it values the book and trades to reach the requested targets. Every trade is charged a cost: half the bid-ask spread plus a market impact term that scales with trade size. The new positions earn open-to-close that day, then carry overnight as held positions, and the loop repeats until the final day when everything is sold with exit costs. The baseline is 100% long all 24 stocks: Sharpe 0.42, annual return 4.2%, annual volatility 11.3%, max drawdown -11%. Development is 2021 to June 2024, validation is July to December 2024 out of sample.

Corrections noted: drawdown is peak-to-trough loss, not caused by volatility; 2025 is the hidden period that is actually graded.

## 2. Signal scan

Sam's explanation (2026-09-18):
A signal is a column each stock has every day, like the carry score. The rank IC is the grade that column gets: how well sorting the stocks by that column is associated with the next day's returns. We tested carry by splitting stocks into four buckets by carry each day: the lowest-carry bucket earned about -1.7 bps the next day and the highest-carry bucket earned about +4.1 bps, a clean staircase. The daily rank IC for carry averaged 0.024 and was positive on 54% of days, which is a small edge but real, not noise.

Correction noted: Sam first called the carry column itself the "information coefficient"; fixed to carry = the column, IC = the measurement of it.

## 3. Hypothesis
See docs/hypothesis.md (Sam's words, verbatim, 2026-09-19).

## 4. Strategy

Sam's explanation (2026-09-20):
A carry number becomes a position when it is one of the 2 highest or 2 lowest in its sector: long the highest, short the lowest, rebalanced every 5 days. Doing this inside each sector keeps the book net neutral (and, added after correction, keeps each sector net zero so there is no accidental sector bet). The calmer (lower-volatility) stock is favored because it makes all stocks contribute to risk equally; without it the jumpiest stock would dominate the signals of the other stocks.

Also discussed: why weekly not daily (daily doubles costs, Sharpe 1.09 vs 1.34); drift trimming on holding days is the engine's rule and costs a rounding error; carry buckets are sticky for weeks but every stock cycles through high and low phases, so we re-rank rather than buy and hold.

## Ideas raised by Sam
- 2026-09-18: can the spread be exploited? Answer: no, it is only a cost here. Sam chose "lean on cheap names" (down-weight wide-spread stocks) as an optional cost refinement for the stress step.

## 5. Split trials (2026-09-20)
No parameters were fitted. Settings (carry, top2/bottom2 per sector, inverse-vol, rebalance 5, gross 1.0) were the plan defaults.
One check was run on the full development set before this split (rebalance every 1/5/10/20 days: Sharpe 1.09/1.34/1.28/1.24); the default of 5 was kept. Disclose in the note as a mild look at the hold-out window.

| | tune 2021-2022 | holdout 2023-Jun2024 |
|---|---|---|
| Sharpe | 0.89 | 2.00 |
| annual return | 3.5% | 7.5% |
| annual vol | 4.0% | 3.6% |
| max drawdown | -3.2% | -2.5% |
| hit rate | 50.4% | 56.2% |
| costs | 2.1% | 1.2% |

Sam's explanation (2026-09-20):
The split shows the strategy isn't overfit to the training data: the first period is worse than the second, which shows it is not just built for the period we trained on.
Corrections noted: "built for any market" is too strong, say "held out of sample within development"; time split rather than shuffle because shuffled days leak the future through rolling features and adjacent days, and real trading only moves forward in time.

## 6. Stress and risk (2026-09-20, development)

Cost stress (decisions fixed, costs scaled):
| cost multiplier | Sharpe | total return | costs | max drawdown |
|---|---|---|---|---|
| 1.0x | 1.34 | 20.2% | 3.2% | -3.2% |
| 1.5x | 1.23 | 18.3% | 4.7% | -3.3% |
| 2.0x | 1.11 | 16.5% | 6.3% | -3.3% |

Sensitivity (one setting at a time, others at default):
| setting | value | Sharpe | total return | max dd | costs |
|---|---|---|---|---|---|
| rebalance every | 3 | 1.17 | 17.3% | -4.3% | 3.8% |
| rebalance every | 5 (default) | 1.34 | 20.2% | -3.2% | 3.2% |
| rebalance every | 10 | 1.28 | 19.1% | -2.6% | 2.3% |
| gross | 0.6 | 1.35 | 11.8% | -1.9% | 1.8% |
| gross | 1.0 (default) | 1.34 | 20.2% | -3.2% | 3.2% |
| gross | 1.4 | 1.34 | 29.1% | -4.4% | 4.6% |
| per side | 1 | 1.14 | 23.8% | -6.1% | 3.2% |
| per side | 2 (default) | 1.34 | 20.2% | -3.2% | 3.2% |
Sharpe keeps its sign and stays above 1.1 for every neighbour. Gross is a pure dial: return and drawdown scale together, Sharpe unchanged.

Sam's cheap-names tilt (shrink positions by 1/sqrt(spread_bps)): costs fell 3.15% -> 2.68%, but Sharpe fell 1.34 -> 1.17 and return 5.2% -> 4.7%. The wide-spread names carry part of the edge, so under-weighting them loses more than it saves. Rejected; flag kept in code as SPREAD_TILT = False for reproducibility.

Monthly: 29 of 42 months positive; worst month -1.12% (Feb 2023); best +2.17% (Sep 2023). All six sectors contributed positively (Financials most, 6.2%; Industrials least, 1.3%). Best asset A08 +3.9%, worst A22 -3.6%: no single name dominates.

## 2. Signal scan (Sam, 2026-09-18)
Carry score is a column each stock has every day. We tested it: the lowest carry bucket returned -1.7 bps next day and the highest +4.1 bps. Reinforced by a daily rank IC mean of 0.024, positive on 54% of days: a small edge but real, not noise.
Correction: carry score is the signal (the column); rank IC is the grade the signal received for how well sorting by it sorted next-day returns.

## 3. Hypothesis
Chosen by Claude's recommendation on 2026-09-20 under time pressure; Sam to confirm. See docs/hypothesis.md.

## 4-6. Build, split, stress (Claude, 2026-09-20, speed mode)
Development 2021-01 to 2024-06, run 2026-09-20, settings: carry_score, top2/bottom2 per sector, inverse-vol, gross 1.0, rebalance every 5 sessions.
- Dev all: Sharpe 1.34, total return 20.2%, annual return 5.2%, annual vol 3.9%, max DD -3.2%, hit rate 52.9%, turnover 14.5x/yr, costs 3.2% total
- Tune 2021-2022: Sharpe 0.89 | Hold-out 2023-Jun 2024: Sharpe 2.00 (hold-out not tuned to; 5-session cadence was the plan default, chosen before any results)
- Costs 1x / 1.5x / 2x: Sharpe 1.34 / 1.23 / 1.11; total costs 3.2% / 4.7% / 6.3%
- Sensitivity: rebalance 1/3/5/10/20 -> Sharpe 1.09/1.17/1.34/1.28/1.24; gross 0.6/1.0/1.4 -> 1.35/1.34/1.34; per side 1/2 -> 1.14/1.34. No setting flips the sign.
- Monthly: 29 of 42 months positive; worst month -1.12%. All six sectors contribute positively (Financials largest at 6.2% of NAV, Industrials smallest 1.3%). Largest single asset contribution 3.9% of NAV, worst -3.6%.
- Tested and rejected: divide weights by sqrt(spread_bps). Costs -15% but Sharpe 1.34 -> 1.17 (tune 0.89 -> 0.57). Not worth it at 0.9%/yr costs.

## 7. Validation (run once, 2026-09-20, strategy frozen at git tag frozen-before-validation, commit 917c877)
Validation July-December 2024, 132 sessions:
- 1x costs: total return -3.6%, annualized -6.7%, annual vol 3.9%, Sharpe -1.75, max DD -5.7%, hit rate 49.2%, turnover 14.7x/yr, costs 0.41%
- 1.5x costs: total return -3.8%, Sharpe -1.86, costs 0.62%
- Monthly: +1.69, -0.76, -2.15, -0.87, +0.58, -2.08. 2 of 6 positive.
- Sector: 5 of 6 negative (Energy -1.5%, Financials -1.3%); only Industrials positive (+0.6%).
- Costs are not the cause (0.4% over six months). The gross return was negative.

## Post-validation diagnostic (2026-09-20, one pass, no strategy change)
Carry rank IC with next-day return by period: 2021-22 +0.013 (t 1.4), 2023 +0.047 (t 3.6), H1-2024 +0.024 (t 1.2), validation -0.008 (t -0.5).
Within-sector top2-minus-bottom2 carry, no costs: +3.1, +6.8, +4.3, -3.5 bps/day. The signal itself faded to zero in H2 2024; construction and costs are not the cause.
Reversal signals got stronger in validation (return_1d IC -0.112, t -6.4) but are untradable after costs: 1-day reversal on development all windows negative (Sharpe -2.6, costs 55% over 3.5 years, turnover 271x/yr); 5-day reversal also negative in every window. No alternative signal survives costs. Decision: keep the frozen strategy, disclose the loss.
