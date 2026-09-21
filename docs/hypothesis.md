# Hypothesis (chosen 2026-09-20)

**Signal:** `carry_score`, buy high, short low, within each sector.

**Hypothesis:** Assets with a persistently high carry characteristic earn a steady premium over
assets with a low one. In real markets this is the return for holding (coupon, dividend, funding
gap). In this synthetic market the mechanism is not visible, but the designers labelled the
column carry, made it slow-moving, and the data confirms high carry earns more, every year,
at 1-day and 5-day horizons.

**Evidence (development data only):**
- Rank IC with next-day return +0.024 (t = 3.4); with 5-day return +0.044 (t = 2.9). Same sign in 2021, 2022, 2023, 2024.
- Sorted into four carry buckets, next-day return rises monotonically: -1.7, +1.5, +2.6, +4.1 bps/day.
- Top minus bottom bucket: +5.8 bps/day, t = 3.1, positive on 52% of days. Small but consistent edge.
- Portfolio membership changes under one name per day, so the edge is cheap to harvest.

**Evidence against / caveats:** the edge slowed in the first half of 2024 (about +3% top-minus-bottom
versus +30% over 2023). The mechanism is unknown; if the generator changes, this stops working.

**Rejected alternatives:** 1-day reversal (t = -6.5, strongest, but flips half the book daily,
roughly 6%/yr in costs at 100% gross); 5-day reversal (t = -2.6, weaker, still churns a fifth of
the book daily); 20-day momentum (sign flipped in 2022). Sentiment, flow, volume, volatility and
event columns showed no cross-sectional predictive power.
