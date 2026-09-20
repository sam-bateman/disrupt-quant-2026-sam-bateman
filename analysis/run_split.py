"""Run the strategy on two non-overlapping development windows.

2021-2022 is where we are allowed to tune. 2023 to June 2024 is an internal
hold-out: look, but do not tune to it.
"""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from starter.backtester import load_data, simulate  # noqa: E402
from starter.metrics import summarize  # noqa: E402
from strategy import generate_positions  # noqa: E402

KEEP = ['sessions', 'total_return', 'annualized_return', 'annualized_volatility',
        'sharpe', 'maximum_drawdown', 'hit_rate', 'annualized_turnover', 'transaction_costs']


def main(cost_multiplier=1.0):
    data = load_data(ROOT / 'data/development.csv')
    windows = {'tune 2021-2022': ('2021-01-04', '2022-12-30'),
               'holdout 2023-Jun2024': ('2023-01-02', '2024-06-28')}
    rows = {}
    for name, (start, end) in windows.items():
        daily, _ = simulate(data, generate_positions, start=start, end=end, cost_multiplier=cost_multiplier)
        rows[name] = {k: summarize(daily)[k] for k in KEEP}
    print(pd.DataFrame(rows).round(3).to_string())


if __name__ == '__main__':
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 1.0)
