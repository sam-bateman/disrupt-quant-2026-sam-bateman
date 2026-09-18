# Disrupt Quant 2026 Strategy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Every task ends with a **teach-back gate**: Claude explains, Sam explains back, Claude confirms before the next task starts.

**Goal:** Submit one simple, evidence-backed, sector-neutral long/short strategy for the 24-asset synthetic market, with README and 2-page research note, by Sunday 2026-09-20 11:59 PM ET.

**Architecture:** A stateless `strategy.py` ranks the 24 assets by one chosen signal, goes long the top 2 and short the bottom 2 in each of the 6 sectors, sizes by inverse 20-day volatility, and rebalances every N sessions. Research scripts live in `analysis/` and use only development data until the explicit validation step.

**Tech Stack:** Python 3.13, numpy 2.3.5, pandas 2.3.3, matplotlib 3.10.7 (pinned by the challenge). Git + GitHub CLI for the private repo. Chrome headless to turn the note into a PDF.

---

## File structure

| Path | Responsibility |
|---|---|
| `strategy.py` | Submission entry point. One function, no state, no files read. |
| `analysis/scan_signals.py` | Step 2 evidence: rank-correlation of each signal with forward returns, plus cost/vol/correlation facts. Writes `analysis/signal_scan.csv`. |
| `analysis/run_split.py` | Runs the strategy on 2021–2022 and on 2023–Jun 2024 separately. |
| `analysis/sensitivity.py` | Re-runs development with one setting changed at a time. |
| `analysis/monthly.py` | Monthly return table and sector attribution from a results folder. |
| `tests/check_strategy.py` | Plain-Python sanity checks on the returned weights. |
| `docs/hypothesis.md` | Sam's one-paragraph hypothesis, written before building. |
| `docs/teach-backs.md` | Sam's explanations from each gate, raw material for the note. |
| `research_note.md` → `research_note.pdf` | The 2-page note. |
| `README.md` | Reproduction and disclosure. |

---

### Task 1: Setup

**Files:**
- Create: `~/disrupt-quant-2026/` (copy of the challenge folder)
- Create: `~/disrupt-quant-2026/docs/teach-backs.md`

- [ ] **Step 1: Copy the project to a real folder and move the session there**

Run:
```bash
cp -R "<scratch>/Disrupt_Quant_2026_Challenge-main" ~/disrupt-quant-2026
```
Then call `change_directory` with `/Users/sbateman/disrupt-quant-2026` (Sam approves).

- [ ] **Step 2: Install Python 3.13**

Only Python 3.14 is on the machine; the pinned packages target 3.13.
Run: `brew install python@3.13`
Expected: ends with `python@3.13` installed; `/opt/homebrew/opt/python@3.13/bin/python3.13 --version` prints `Python 3.13.x`.

- [ ] **Step 3: Create the environment and install pinned packages**

Run:
```bash
cd ~/disrupt-quant-2026
/opt/homebrew/opt/python@3.13/bin/python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```
Expected: `Successfully installed numpy-2.3.5 pandas-2.3.3 scipy-1.16.3 scikit-learn-1.7.2 matplotlib-3.10.7 ...`

- [ ] **Step 4: Run the baseline once**

Run: `.venv/bin/python starter/backtester.py`
Expected: JSON metrics printed, `Results: .../results/development`. Note the baseline `sharpe`, `maximum_drawdown`, `transaction_costs` in `docs/teach-backs.md`.

- [ ] **Step 5: Start git**

```bash
git init
printf 'analysis/*.png\n' >> .gitignore
git add -A
git commit -m "chore: challenge files, design spec and plan"
```

- [ ] **Step 6: Teach-back gate**

Claude explains: what the backtester does each day (observe close t, trade at open t+1, pay costs from cash, earn open-to-close), what the three data periods are for, what the baseline scored. Sam explains back. Record Sam's version in `docs/teach-backs.md` under `## 1. Setup`. Do not continue until accurate.

---

### Task 2: Signal scan (development data only)

**Files:**
- Create: `analysis/scan_signals.py`
- Output: `analysis/signal_scan.csv`

- [ ] **Step 1: Write the scan script**

```python
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
```

- [ ] **Step 2: Run it**

Run: `.venv/bin/python analysis/scan_signals.py`
Expected: a table sorted by absolute t-stat, then six market facts. Takes under a minute.

- [ ] **Step 3: Write the plain-English summary**

Claude writes `analysis/scan_summary.md`: top 3 signals with sign (positive = buy high, negative = buy low), whether the sign held every year, how the 1-day and 5-day horizons compare, and what the cost figures mean for how often we can trade. Signals with |t| < 2 or a sign that flips across years are labelled noise.

- [ ] **Step 4: Commit**

```bash
git add analysis/
git commit -m "research: signal scan on development data"
```

- [ ] **Step 5: Teach-back gate**

Claude explains rank IC in one paragraph (rank stocks by signal, rank by what they earned next, correlate; positive means the signal orders winners correctly). Sam explains back and names which signals looked real vs noise. Record under `## 2. Signal scan` in `docs/teach-backs.md`.

---

### Task 3: Hypothesis choice

**Files:**
- Create: `docs/hypothesis.md`

- [ ] **Step 1: Present 2–3 candidates**

For each: the signal, its sign, mean IC and t-stat at both horizons, years with the same sign, and a one-line economic story (for example "short-term reversal: last week's losers bounce because price overshoots"). Ask Sam to pick one. Multiple choice.

- [ ] **Step 2: Sam writes the hypothesis**

Sam dictates or types 2–4 sentences; Claude saves them verbatim to `docs/hypothesis.md` with the date, the chosen signal, sign, and the evidence numbers.

- [ ] **Step 3: Commit**

```bash
git add docs/hypothesis.md
git commit -m "research: hypothesis chosen"
```

- [ ] **Step 4: Teach-back gate**

Sam states the hypothesis without looking at the file: what relationship, why it might exist, what evidence supports it, what evidence was against it. Record under `## 3. Hypothesis`.

---

### Task 4: Strategy and sanity check

**Files:**
- Modify: `strategy.py` (replace entirely)
- Create: `tests/check_strategy.py`

- [ ] **Step 1: Write the sanity check first**

```python
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
```

- [ ] **Step 2: Run it to see it fail on the baseline**

Run: `.venv/bin/python tests/check_strategy.py`
Expected: `AssertionError: book not dollar-neutral: net=1.0000` (the equal-weight baseline is 100% long).

- [ ] **Step 3: Write the strategy**

Replace `strategy.py` with the following. `SIGNAL` and `SIGN` come from `docs/hypothesis.md`.

```python
"""Disrupt Quant 2026 submission.

One signal, ranked within each sector. Long the top 2 and short the bottom 2
of each sector's 4 assets, so every sector and the whole book are
dollar-neutral. Positions are sized by inverse 20-day volatility so no single
asset dominates. Weights are recomputed every REBALANCE_EVERY sessions and
held in between. The function is stateless: it re-derives the last rebalance
date from the history it is given.
"""
import numpy as np
import pandas as pd

SIGNAL = 'return_5d'      # column used to rank assets (set from docs/hypothesis.md)
SIGN = -1                 # +1: buy high values of SIGNAL; -1: buy low values
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
```

- [ ] **Step 4: Run the sanity check**

Run: `.venv/bin/python tests/check_strategy.py`
Expected: three lines like `2021-01-01: 24 positions, gross=1.00, net=+0.0000, max|w|=0.0xx` and `sanity checks passed`.

- [ ] **Step 5: Run the full development backtest**

Run: `.venv/bin/python starter/backtester.py`
Expected: metrics JSON with `constraint_adjustment_days: 0`, `average_gross_exposure` near 1.0, `average_net_exposure` near 0. Open `results/development/diagnostics.png` and show it to Sam.

- [ ] **Step 6: Commit**

```bash
git add strategy.py tests/
git commit -m "feat: sector-neutral single-signal strategy"
```

- [ ] **Step 7: Teach-back gate**

Claude walks through the code top to bottom in plain words. Sam explains back: how a signal becomes a position, why sector-neutral, why inverse-vol sizing, why rebalance every 5 days, what happens on days in between. Record under `## 4. Strategy`.

---

### Task 5: Internal chronological split

**Files:**
- Create: `analysis/run_split.py`

- [ ] **Step 1: Write the split runner**

```python
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
```

- [ ] **Step 2: Run it**

Run: `.venv/bin/python analysis/run_split.py`
Expected: two columns of metrics. The hold-out Sharpe should have the same sign as the tune window. If the tune window is good and the hold-out is bad, that is evidence of overfitting and goes in the note.

- [ ] **Step 3: If tuning is needed, tune on the first window only**

Allowed knobs, one at a time: `REBALANCE_EVERY` in {3, 5, 10}, `GROSS` in {0.6, 1.0, 1.4}. Pick by the tune window, then re-run the hold-out once. Write every trial and result into `docs/teach-backs.md` under `## 5. Split trials` so nothing is hidden.

- [ ] **Step 4: Commit**

```bash
git add analysis/run_split.py strategy.py docs/
git commit -m "research: chronological split check"
```

- [ ] **Step 5: Teach-back gate**

Sam explains: why we split in time rather than shuffle, what the tune window is for, what the hold-out is for, and what the numbers said. Record under `## 5. Split`.

---

### Task 6: Cost stress, sensitivity, monthly view

**Files:**
- Create: `analysis/sensitivity.py`
- Create: `analysis/monthly.py`

- [ ] **Step 1: Cost stress with the official tool**

```bash
.venv/bin/python starter/backtester.py --cost-multiplier 1.5 --out results_cost15
.venv/bin/python starter/backtester.py --cost-multiplier 2.0 --out results_cost20
```
Expected: three sets of metrics (1x from Task 4, 1.5x, 2x). Record `sharpe`, `total_return`, `transaction_costs` for each. If Sharpe drops below zero at 1.5x, raise `REBALANCE_EVERY` (trade less) and redo Task 5.

- [ ] **Step 2: Write the sensitivity script**

```python
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

TRIALS = [('REBALANCE_EVERY', [3, 5, 10]), ('GROSS', [0.6, 1.0, 1.4]), ('PER_SIDE', [1, 2])]
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
```

- [ ] **Step 3: Run it**

Run: `.venv/bin/python analysis/sensitivity.py`
Expected: 8 rows. Pass condition: Sharpe keeps its sign for every neighbour of the chosen setting. Note any setting that flips it.

- [ ] **Step 4: Write the monthly view**

```python
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
```

- [ ] **Step 5: Run it on development**

Run: `.venv/bin/python analysis/monthly.py results/development`
Expected: a monthly table, count of positive months, sector and asset contributions. Concern flag: one asset or one sector supplying most of the return.

- [ ] **Step 6: Commit**

```bash
git add analysis/ strategy.py docs/
git commit -m "research: cost stress, sensitivity, monthly attribution"
```

- [ ] **Step 7: Teach-back gate**

Sam explains: how costs are computed in this challenge (spread plus impact, size matters), how much they ate, which setting mattered most, and two ways this strategy could fail. Record under `## 6. Stress and risk`.

---

### Task 7: Freeze and validate (run once)

- [ ] **Step 1: Freeze**

```bash
git add -A
git commit -m "freeze: strategy frozen before validation"
git tag frozen-before-validation
```

- [ ] **Step 2: Run validation exactly once at 1x and 1.5x**

```bash
.venv/bin/python starter/backtester.py --split validation
.venv/bin/python starter/backtester.py --split validation --cost-multiplier 1.5 --out results_val15
.venv/bin/python analysis/monthly.py results/validation
.venv/bin/python validate_submission.py --starter-check
```
Expected: two metric sets and `Structure OK`. Copy the numbers, with today's date, into `docs/teach-backs.md` under `## 7. Validation`.

- [ ] **Step 3: Decide, once**

If validation is bad, the default is to keep the strategy and explain honestly in the note. Any change after this point is written in the note as "changed after seeing validation", and validation is not re-run more than once more.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "research: validation results recorded"
```

- [ ] **Step 5: Teach-back gate**

Sam explains: why freeze before looking, how validation compared to development, and what they would say if asked "did you tune to validation?". Record under `## 7. Validation`.

---

### Task 8: Write-up and submission

**Files:**
- Create: `research_note.md`, `research_note.pdf`
- Modify: `README.md`
- Create: private GitHub repo via `gh`

- [ ] **Step 1: Give Sam the note skeleton**

Claude writes `research_note.md` with the 8 required headings and, under each, only the numbers, table stubs and plot references. Sam writes the prose in their own words, mostly by pasting from `docs/teach-backs.md`.

```markdown
# <Strategy name> — Disrupt Quant 2026 research note
Sam Bateman · 2026-09-xx

## 1. Hypothesis
## 2. Evidence
(rank IC table: signal, horizon, mean IC, t-stat, years same sign; plus the signals that did NOT work)
## 3. Construction
(signal → sector ranks → top 2 / bottom 2 → inverse-vol → gross 1.0 → rebalance every N)
## 4. Risk
(per-asset max, sector neutral, dollar neutral, gross, what the drawdown was)
## 5. Costs
(1x / 1.5x / 2x table; turnover; what changed because of costs)
## 6. Validation
(dev tune / dev hold-out / validation table; sensitivity table; post-validation changes: none or listed)
## 7. Limitations
## 8. Next step
```

- [ ] **Step 2: Turn the note into a 2-page PDF**

```bash
.venv/bin/python -m pip install markdown
.venv/bin/python -c "
import markdown, pathlib
body = markdown.markdown(pathlib.Path('research_note.md').read_text(), extensions=['tables'])
css = '<style>body{font-family:Helvetica,Arial;font-size:10.5pt;line-height:1.3;margin:0.6in} h1{font-size:15pt;margin:0 0 4pt} h2{font-size:11.5pt;margin:8pt 0 2pt} table{border-collapse:collapse;font-size:9pt} td,th{border:1px solid #999;padding:2px 5px} p{margin:2pt 0}</style>'
pathlib.Path('research_note.html').write_text(css + body)
"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=research_note.pdf research_note.html
```
Expected: `research_note.pdf` exists. Check page count is 2 or fewer:
```bash
.venv/bin/python -c "import re,pathlib;print(len(re.findall(rb'/Type\s*/Page[^s]', pathlib.Path('research_note.pdf').read_bytes())), 'pages')"
```
If Chrome is missing, Sam pastes the markdown into Google Docs and exports a PDF.

- [ ] **Step 3: Fill the README**

Replace the "Your submission README" section with real values: candidate name, strategy name and summary, `python starter/backtester.py` and `--split validation` as reproduction, Python 3.13 and pinned packages, development and validation metrics with dates, assumptions (zero cash yield, no borrow cost, synthetic data), AI disclosure ("Claude Code was used to write the Python scripts, the backtest harness calls, and to structure the note; every strategy decision, parameter and the note's text were made and written by the candidate, who explained each step back before proceeding").

- [ ] **Step 4: Final validator and commit**

```bash
.venv/bin/python validate_submission.py
git add -A
git commit -m "docs: research note, README, disclosure"
```
Expected: `Structure OK. ...`

- [ ] **Step 5: Create the private repo and push (ask Sam first)**

```bash
gh repo create disrupt-quant-2026-sam-bateman --private --source=. --push
git rev-parse HEAD
```
Expected: repo URL printed and a 40-character SHA. Sam grants the reviewer account access on GitHub and submits the URL and SHA through the invitation form.

- [ ] **Step 6: Teach-back gate**

Sam gives the two-minute interview version of the strategy start to finish. Claude asks two follow-up questions an interviewer would ask (for example "why not use two signals?" and "what would make you turn it off?"). Record under `## 8. Interview rehearsal`.
