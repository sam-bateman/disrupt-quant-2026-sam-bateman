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
