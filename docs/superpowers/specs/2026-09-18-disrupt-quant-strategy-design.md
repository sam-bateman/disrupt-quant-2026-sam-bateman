# Disrupt Quant 2026 — Strategy Design

Date: 2026-09-18. Deadline: Sunday 2026-09-20, 11:59 PM Eastern.

## Goal

Submit one simple, well-evidenced long/short strategy for the 24-asset synthetic market, plus a README and a 2-page research note. Sam makes every strategy decision and must be able to explain each one in an interview. Claude writes the code.

## Guiding principles

- One signal, chosen from evidence in the development data. No machine learning.
- Every parameter has a one-sentence reason.
- Validation data (July–December 2024) is not read until the strategy is frozen. It is run once at 1x and 1.5x costs.
- Code stays small: `strategy.py` under about 100 lines, standard library plus numpy and pandas only.
- **Teach-back gate after every step.** When Claude finishes a step, Claude explains it in plain words, then Sam explains it back in their own words. Claude does not start the next step until Sam's explanation is accurate. If it is not, Claude re-explains the missing piece and asks again. The explanations Sam gives become raw material for the research note and interview.

## Workflow

Each step ends with a teach-back: Claude summarizes what was done and why, Sam describes it back, Claude confirms or corrects. The specific question for each step is listed under it.

### 1. Setup
- Copy the challenge folder to `~/disrupt-quant-2026` and initialize git.
- Create `.venv`, install `requirements.txt`, run `python starter/backtester.py` to confirm the equal-weight baseline works.
- Teach-back: what does the backtester do each day, when does it trade, and what does the equal-weight baseline score?

### 2. Data scan (development data only)
- Load `data/development.csv`. Never load `data/validation.csv` here.
- For each candidate signal (return_1d, return_5d, return_20d, price_strength_20, price_strength_60, volume_zscore, volume_trend, sentiment_score, flow_index, carry_score, event_intensity, realized vols, intraday_range, macro factors) compute the daily cross-sectional rank correlation between today's signal and the next 1-day and next 5-day return. Report mean, t-stat, and sign stability across years.
- Also report: average pairwise correlation of asset returns, per-asset daily volatility, and a rough one-way cost per trade from the cost formula, so we know how much turnover the edge can afford.
- Output: a short plain-English summary plus a small table saved in `analysis/`.
- Teach-back: what is a cross-sectional rank correlation, why do we look at it, and which signals looked real versus noise?

### 3. Hypothesis choice
- Sam picks one signal from 2–3 candidates. Each candidate comes with a one-line economic story and its scan numbers.
- Teach-back: state the hypothesis in one or two sentences, including why the relationship might exist and what evidence supports it.

### 4. Strategy construction
- Each day, rank the 24 assets by the chosen signal.
- Within each sector (4 assets each), go long the top 2 and short the bottom 2 by signal rank, so every sector is dollar-neutral and the whole book is dollar-neutral. Alternative if the scan favors it: weight by rank within sector instead of a hard 2/2 split.
- Scale each position by the inverse of its 20-day realized volatility, then normalize so gross exposure is a fixed modest target (start at 100%, well inside the 200% limit and the 20% per-asset limit).
- Rebalance on a fixed cadence (start weekly) to control turnover; adjust only if the cost stress in step 5 demands it.
- Internal chronological check: fit any parameters on 2021–2022, then evaluate untouched on 2023 to June 2024.
- Teach-back: walk through how a signal becomes a position, why sector-neutral, why inverse-volatility sizing, and what the internal split showed.

### 5. Stress and risk
- Run the backtester at cost multipliers 1x, 1.5x, 2x on development.
- Sensitivity: vary the lookback and the rebalance cadence by one step each way; results must not flip sign.
- Inspect monthly returns, drawdown, gross and net exposure, max sector net, turnover, and the diagnostics plot.
- Teach-back: how much do costs eat, what did the sensitivity check show, and when would this strategy fail?

### 6. Freeze and validate
- Freeze `strategy.py`. Run `--split validation` at 1x and 1.5x exactly once. Record metrics with the date. Any later change is documented as post-validation.
- Teach-back: why do we freeze before looking, and how do the validation numbers compare with development?

### 7. Deliverables
- `strategy.py` (entry point, self-contained).
- `README.md` with candidate name, strategy summary, reproduction command, dev and validation metrics with dates, assumptions, AI disclosure.
- `research_note.pdf`, 2 pages, following the 8 required headings, written by Sam.
- Private GitHub repo `disrupt-quant-2026-firstname-lastname`, run `validate_submission.py`, submit the 40-character SHA.
- Teach-back: give the two-minute interview version of the whole strategy, start to finish.

## Error handling and robustness in the strategy code
- The function must never raise: if the history is too short for the lookback, return `{}` (cash).
- Return only finite floats for known asset ids.
- Runtime: vectorized pandas on the latest window only; target well under one second per call.

## Testing
- Baseline run reproduces the starter output.
- A tiny sanity script checks the returned dict on a sample date: finite values, per-asset weights within 20%, sector nets near zero, gross near target.
- Backtester `constraint_adjustment_days` should be zero or near zero, meaning we never rely on the engine to clip us.

## Out of scope
- Multiple signals, machine learning, intraday logic, external data.
