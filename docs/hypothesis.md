# Hypothesis

Chosen 2026-09-19 by Sam. Signal: `carry_score`. Direction: buy high, short low (SIGN = +1).

## Sam's words, verbatim

The relatioships that I am beetting on is between carry adn the price movement in the next day. The highest carries measured at the end of the day are then longed adn the lowest are shorted. This shows an IC of .024 meaning 54% of the days proves this correlation isnt jsut noise.  Carry is typically something seen in equities that pay divdiends, or bonds that pay coupons, or the futures curve of a future, these are all garuentted increases which could explaiun why this straety works. This correlation does slow down in 2024 which is sort of concerning for the 2025 test. It also use a priotiy system to pick the highest carry that also has the smalest bps spread which limits the trade cost, and this strategy buys/sells a new stock less than one a day so amragins are rarelty being donated to trade costs.

## Corrections to carry into the note
- IC 0.024 (average agreement) and 54% positive days are two separate statistics that both point the same way; one does not imply the other.
- Carry is not guaranteed in real markets, and this synthetic market has no dividend. Say: in real markets carry is a payment for holding an asset; this synthetic characteristic behaves like one, and the data, not the label, is the evidence.
- The spread-priority tilt is an optional refinement for the cost-stress step, not part of the base hypothesis.

## Evidence (development data, 2021-01 to 2024-06)
- Rank IC vs next-day return: +0.024, t-stat 3.4, positive in all four years (2021 0.005, 2022 0.021, 2023 0.047, 2024H1 0.022).
- Rank IC vs next-5-day return: +0.044, t-stat 2.9 (overlap-adjusted), positive all four years.
- Bucket test (4 buckets of 6 by carry, next-day return): -1.7, +1.5, +2.6, +4.1 bps/day, monotonic.
- Top-minus-bottom bucket: +5.8 bps/day, positive 51.9% of days, t-stat 3.1. $1 grew to $1.67 before costs; 2021 +5.9%, 2022 +15%, 2023 +32%, 2024H1 +3%.
- Churn: about 0.9 of 24 names switch side per day under a top-2/bottom-2 per sector rule.

## Against or weak
- Edge slowed sharply in the first half of 2024.
- Per-day edge is the smallest of the three real signals; one-day reversal is stronger before costs (IC -0.048) but churns half the book daily.
- Mechanism cannot be verified; the generator could change in 2025.
