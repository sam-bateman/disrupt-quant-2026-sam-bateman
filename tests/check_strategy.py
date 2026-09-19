"""Plain-Python sanity checks for strategy.generate_positions. Run: .venv/bin/python tests/check_strategy.py"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import strategy  # noqa: E402

data = pd.read_csv(ROOT / 'data/development.csv', parse_dates=['date'])
data = data.sort_values(['date', 'asset_id']).reset_index(drop=True)
dates = data.date.unique()
sectors = data.drop_duplicates('asset_id').set_index('asset_id').sector

for when in [dates[0], dates[30], dates[-1]]:
    history = data[data.date <= when].copy()
    out = strategy.generate_positions(history, pd.Timestamp(when))
    assert isinstance(out, dict), 'must return a dict'
    assert all(k in set(sectors.index) for k in out), 'unknown asset id'
    w = pd.Series(out, dtype=float)
    assert np.isfinite(w).all(), 'nonfinite weight'
    assert (w.abs() <= 0.20 + 1e-9).all(), f'per-asset limit broken: {w.abs().max():.3f}'
    gross, net = w.abs().sum(), w.sum()
    assert gross <= 2.0 + 1e-9, 'gross limit broken'
    assert abs(net) < 1e-6, f'book not dollar-neutral: net={net:.4f}'
    sector_net = w.groupby(sectors.reindex(w.index)).sum()
    assert (sector_net.abs() < 1e-6).all(), f'sector not neutral: {sector_net.to_dict()}'
    print(f'{pd.Timestamp(when).date()}: {len(w)} positions, gross={gross:.2f}, net={net:+.4f}, max|w|={w.abs().max():.3f}')
print('sanity checks passed')
