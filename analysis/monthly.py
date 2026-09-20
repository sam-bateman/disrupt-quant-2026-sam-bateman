"""Monthly returns and sector attribution from a results folder.
Run: .venv/bin/python analysis/monthly.py results/development"""
from pathlib import Path
import sys
import pandas as pd

folder = Path(sys.argv[1] if len(sys.argv) > 1 else 'results/development')
daily = pd.read_csv(folder / 'daily.csv', parse_dates=['date'])
attr = pd.read_csv(folder / 'attribution.csv', parse_dates=['date'])

monthly = (1 + daily.set_index('date').net_return).resample('ME').prod() - 1
print('Monthly net returns (%):')
print((monthly * 100).round(2).to_string())
print(f'\nPositive months: {(monthly > 0).sum()} of {len(monthly)}')

by_sector = attr.groupby('sector').net_contribution.sum().sort_values()
print('\nNet contribution by sector (fraction of NAV, summed):')
print(by_sector.round(4).to_string())

by_asset = attr.groupby('asset_id').net_contribution.sum().sort_values()
print('\nBest and worst assets:')
print(pd.concat([by_asset.head(3), by_asset.tail(3)]).round(4).to_string())
