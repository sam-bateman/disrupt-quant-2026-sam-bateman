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

## Ideas raised by Sam
- 2026-09-18: can the spread be exploited? Answer: no, it is only a cost here. Sam chose "lean on cheap names" (down-weight wide-spread stocks) as an optional cost refinement for the stress step.
