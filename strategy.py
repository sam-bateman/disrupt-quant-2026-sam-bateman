"""Disrupt Quant 2026 submission.

One signal (carry_score), ranked within each sector. Long the top 2 and short
the bottom 2 of each sector's 4 assets, so every sector and the whole book are
dollar-neutral. Positions are sized by inverse 20-day volatility so no single
asset dominates. Weights are recomputed every REBALANCE_EVERY sessions and
held in between. The function is stateless: it re-derives the last rebalance
date from the history it is given.
"""
import numpy as np
import pandas as pd

SIGNAL = 'carry_score'    # column used to rank assets (see docs/hypothesis.md)
SIGN = 1                  # +1: buy high values of SIGNAL; -1: buy low values
REBALANCE_EVERY = 5       # sessions between rebalances
GROSS = 1.0               # sum of absolute weights at execution
PER_SIDE = 2              # longs and shorts per sector (4 assets per sector)


def _rebalance_rows(history, current_date):
    dates = history.date.unique()
    k = len(dates)
    idx = ((k - 1) // REBALANCE_EVERY) * REBALANCE_EVERY
    return history.loc[history.date == dates[idx]]


def _weights(rows):
    rows = rows.dropna(subset=[SIGNAL, 'realized_vol_20d'])
    sectors = rows.sector.unique()
    side_budget = GROSS / (2 * len(sectors))  # dollars per side per sector
    weights = {}
    for sector in sectors:
        grp = rows[rows.sector == sector].sort_values(SIGNAL, ascending=(SIGN < 0))
        if len(grp) < 2 * PER_SIDE:
            continue
        longs, shorts = grp.head(PER_SIDE), grp.tail(PER_SIDE)
        for side, sign in ((longs, 1.0), (shorts, -1.0)):
            inv_vol = 1.0 / np.maximum(side.realized_vol_20d.to_numpy(), 1e-3)
            w = sign * side_budget * inv_vol / inv_vol.sum()
            weights.update(zip(side.asset_id, map(float, w)))
    return weights


def generate_positions(history, current_date):
    try:
        rows = _rebalance_rows(history, current_date)
        return _weights(rows)
    except Exception:
        return {}  # never raise: fall back to cash
