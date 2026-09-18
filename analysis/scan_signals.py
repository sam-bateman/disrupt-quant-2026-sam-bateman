"""Which provided signals line up with what we would actually earn?

Reads ONLY data/development.csv. Never touches validation.csv.
For each signal, each day: rank the 24 assets by the signal and by their
forward return, and take the correlation of the two rankings (rank IC).
Forward return is measured from the NEXT session's open, because that is
where the engine executes.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SIGNALS = ['return_1d', 'return_5d', 'return_20d', 'price_strength_20',
           'price_strength_60', 'volume_zscore', 'volume_trend',
           'sentiment_score', 'flow_index', 'carry_score', 'event_intensity',
           'realized_vol_5d', 'realized_vol_20d', 'intraday_range',
           'liquidity_score', 'spread_bps']
# macro_factor_1..3 and market_* are identical across assets on a date, so
# they cannot rank assets against each other and are excluded here.


def load_development():
    d = pd.read_csv(ROOT / 'data/development.csv', parse_dates=['date'])
    return d.sort_values(['date', 'asset_id']).reset_index(drop=True)


def add_forward_returns(d):
    g = d.groupby('asset_id')
    next_open = g.open.shift(-1)
    d['fwd_1d'] = g.close.shift(-1) / next_open - 1
    d['fwd_5d'] = g.close.shift(-5) / next_open - 1
    return d


def rank_ic(d, signal, target):
    sub = d.dropna(subset=[target])
    out = {}
    for date, day in sub.groupby('date'):
        out[date] = day[signal].rank().corr(day[target].rank())
    return pd.Series(out)


def scan(d):
    rows = []
    for s in SIGNALS:
        for t in ['fwd_1d', 'fwd_5d']:
            ic = rank_ic(d, s, t)
            by_year = ic.groupby(ic.index.year).mean()
            t_stat = ic.mean() / ic.std() * np.sqrt(len(ic))
            if t == 'fwd_5d':
                t_stat /= np.sqrt(5)  # overlapping 5-day windows overstate it
            rows.append({'signal': s, 'horizon': t, 'mean_ic': round(ic.mean(), 4),
                         't_stat': round(t_stat, 2),
                         'years_same_sign': int((np.sign(by_year) == np.sign(ic.mean())).sum()),
                         **{f'ic_{y}': round(v, 4) for y, v in by_year.items()}})
    table = pd.DataFrame(rows)
    return table.reindex(table.t_stat.abs().sort_values(ascending=False).index)


def market_facts(d):
    wide = d.pivot(index='date', columns='asset_id', values='return_1d')
    corr = wide.corr().to_numpy()
    avg_corr = corr[np.triu_indices_from(corr, 1)].mean()
    vol = wide.std()
    # One-way cost of a trade worth 4% of a $1M book, from the rules' formula.
    delta, nav = 0.04, 1_000_000
    part = delta * nav / (d.volume * d.close)
    impact = 0.10 * d.realized_vol_20d * np.sqrt(part) / np.sqrt(d.liquidity_score.clip(0.1, 1.0))
    rate_bps = (d.spread_bps / 20_000 + impact) * 10_000
    return {'avg_pairwise_corr': round(avg_corr, 3),
            'median_daily_vol': round(vol.median(), 4),
            'min_daily_vol': round(vol.min(), 4), 'max_daily_vol': round(vol.max(), 4),
            'median_one_way_cost_bps': round(rate_bps.median(), 1),
            'worst_asset_cost_bps': round(rate_bps.groupby(d.asset_id).median().max(), 1)}


def main():
    d = add_forward_returns(load_development())
    table = scan(d)
    table.to_csv(ROOT / 'analysis/signal_scan.csv', index=False)
    pd.set_option('display.width', 200)
    print(table.to_string(index=False))
    print()
    for k, v in market_facts(d).items():
        print(f'{k}: {v}')


if __name__ == '__main__':
    main()
