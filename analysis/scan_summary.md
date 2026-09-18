# Signal scan summary (development data only, run 2026-09-18)

Method: each day, rank the 24 assets by the signal and by the return they would earn
if bought at the next open (1-day and 5-day horizons). Correlate the two rankings
(rank IC). Average over 910 days. t-stat > 2 in absolute value means the average is
unlikely to be zero by chance. 5-day t-stats are divided by sqrt(5) because the
windows overlap.

## Looks real (|t| > 2, same sign in all four years)

| Signal | Direction | 1-day IC (t) | 5-day IC (t) | Names switching side per day |
|---|---|---|---|---|
| return_1d | reversal: buy yesterday's losers | -0.048 (-6.5) | -0.010 (-0.6) | 12.4 of 24 |
| carry_score | buy high carry | +0.024 (+3.4) | +0.044 (+2.9) | 0.9 of 24 |
| return_5d | reversal: buy last week's losers | -0.018 (-2.6) | +0.002 (0.1) | 5.3 of 24 |

## Borderline (|t| about 2, one year flipped)

| Signal | Direction | 1-day IC (t) | 5-day IC (t) | Names switching per day |
|---|---|---|---|---|
| return_20d | momentum: buy last month's winners | +0.013 (1.8) | +0.034 (2.3) | 2.7 of 24 |
| price_strength_60 | buy above 60-day average | +0.008 (1.1) | +0.029 (1.8) | - |

## Noise (|t| < 1.5 or sign flips across years)
sentiment_score, flow_index, volume_zscore, volume_trend, event_intensity,
realized_vol_5d, realized_vol_20d, intraday_range, liquidity_score, spread_bps.
Named "sentiment" and "flow" but they do not rank next-day returns here.

## Market facts that matter for construction
- Average correlation between assets: 0.24. Being long/short removes most of the common move.
- Daily volatility per asset: 1.1% to 1.8%, median 1.35%. Fairly even, so inverse-vol sizing is a mild adjustment.
- One-way cost of a 4%-of-book trade: median 4.9 bps, worst asset 12.6 bps.

## What the cost figure means
The 1-day reversal signal is the strongest but flips half the book every day. Trading
half of a 100%-gross book daily at about 5 bps one-way costs roughly 0.5 x 5 bps = 2.5 bps
per day, about 6% per year. Its edge must beat that. Carry barely trades (under one
name a day) so its costs are close to zero, but its edge is weaker per day. return_5d
sits between them.
