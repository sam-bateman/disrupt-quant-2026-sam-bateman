"""Change one setting at a time and re-run development. Strategy is stateless so
setting module attributes is enough."""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from starter.backtester import load_data, simulate  # noqa: E402
from starter.metrics import summarize  # noqa: E402
import strategy  # noqa: E402

TRIALS = [('REBALANCE_EVERY', [1, 3, 5, 10, 20]), ('GROSS', [0.6, 1.0, 1.4]), ('PER_SIDE', [1, 2])]
KEEP = ['sharpe', 'total_return', 'maximum_drawdown', 'annualized_turnover', 'transaction_costs']


def main():
    data = load_data(ROOT / 'data/development.csv')
    rows = []
    for name, values in TRIALS:
        original = getattr(strategy, name)
        for v in values:
            setattr(strategy, name, v)
            daily, _ = simulate(data, strategy.generate_positions)
            m = summarize(daily)
            rows.append({'setting': name, 'value': v, **{k: round(m[k], 3) for k in KEEP}})
        setattr(strategy, name, original)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == '__main__':
    main()
