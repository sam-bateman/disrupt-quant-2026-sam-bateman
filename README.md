# Disrupt Quant — 2026 Quantitative  Challenge

Markets rarely tell you which variables matter, which relationships will persist, or whether a pattern represents genuine structure rather than noise. Approach this unfamiliar multi-asset market as a quantitative researcher: develop a systematic strategy supported by evidence, disciplined validation, and sound risk management.

**Released:** Thursday, September 17, 2026  
**Deadline:** Sunday, September 20, 2026 at 11:59 PM Eastern Time

The challenge is designed for approximately **4–6 hours of focused work**. You are not expected to spend the entire three-day window working on it. The window lets you work around academic and personal commitments.

## Start here

Use Python 3.12 or 3.13; the evaluation environment uses Python 3.13. No GPU or container software is required on your laptop.

```bash
# Clone the challenge repository using the URL in your invitation,
# or unzip the supplied candidate archive and enter its directory.
cd Disrupt_Quant_2026_Challenge
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python starter/backtester.py
```

The command evaluates the equal-weight example on development data and writes metrics, daily returns and six diagnostic plots to `results/development/`.

1. Read [CHALLENGE.md](CHALLENGE.md), [RULES.md](RULES.md), and the [data dictionary](data/data_dictionary.md).
2. Research development data and edit **the root `strategy.py`**.
3. Freeze your approach before inspecting validation performance. Run validation explicitly:

```bash
python starter/backtester.py --split validation
python starter/backtester.py --split validation --cost-multiplier 1.5
python validate_submission.py --starter-check
```

4. Write a research note of at most two pages as `research_note.pdf` and update this README with reproduction instructions and AI disclosure.
5. Run `python validate_submission.py`. Submit your private repository URL and full 40-character commit SHA through the form linked in your invitation. Grant access to the reviewer account specified in that invitation.

Sophisticated machine-learning models are not inherently preferred. A simple strategy supported by strong reasoning, robust validation, and thoughtful risk management may score better than a complex model.

Your final ranking will not be determined solely by P&L or Sharpe ratio. We care about how you think, test hypotheses, manage risk, and support conclusions with evidence.

## Submission

- **Candidate name:** Sam Bateman
- **Strategy name and summary:** Sector-neutral carry. Every fifth session, rank the four assets in each sector by `carry_score`; long the top two, short the bottom two, sized by inverse 20-day volatility, dollar-neutral per sector and overall, 100% gross. Chosen because carry was the only provided signal with a consistent cross-sectional edge that survives transaction costs.
- **Reproduction command and environment:** Python 3.13 with the pinned `requirements.txt`. `python starter/backtester.py` (development), `python starter/backtester.py --split validation` (validation), `python starter/backtester.py --split validation --cost-multiplier 1.5`. Research scripts: `python analysis/scan_signals.py`, `python analysis/run_split.py`, `python analysis/sensitivity.py`, `python analysis/monthly.py results/development`. Sanity check: `python tests/check_strategy.py`.
- **Development metrics (2021-01-04 to 2024-06-28, run 2026-09-20):** Sharpe 1.34, total return +20.2%, annualized return 5.2%, annualized volatility 3.9%, max drawdown -3.2%, turnover 14.5x/yr, costs 3.2% of NAV. Internal split: 2021–2022 Sharpe 0.89, 2023–Jun 2024 Sharpe 2.00.
- **Validation metrics (2024-07-01 to 2024-12-31, run once on 2026-09-20 after freezing at git tag `frozen-before-validation`):** Sharpe -1.75, total return -3.6%, max drawdown -5.7%, costs 0.41%. At 1.5x costs: Sharpe -1.86, total return -3.8%. No changes were made to the strategy after validation. See `research_note.pdf` for the diagnosis.
- **Important assumptions and known limitations:** Cash earns zero and shorts carry no borrow cost, both simplifications that flatter a 50% short book. The carry mechanism is not observable in synthetic data; the edge is small (about 5 bps/day gross) and faded to zero in the second half of 2024. `strategy.py` is stateless and reads no files.
- **AI tools used:** Claude Code (Anthropic).
- **How they were used:** Claude wrote the Python scripts (`strategy.py`, `analysis/*`, `tests/*`), ran the backtests, and drafted the README and research note from the recorded results. The candidate set the plan, made every strategy decision (signal choice, construction, rebalance cadence, what to test and reject, keeping the frozen strategy after validation), and edited the note. Working notes and the candidate's own explanations of each step are in `docs/`.

Only documentation, the example, and market observations are provided. Any explanatory research examples in `starter/` demonstrate the API; they are not trading recommendations.
