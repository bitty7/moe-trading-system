# Comparison Guide (LLM vs Pre-trained)

This guide explains how to run two comparable backtests and summarize results.

## 1) Prepare Two Configs
- `config_llm.json`: all experts `impl: "llm"` with model identifiers
- `config_pretrained.json`: experts `impl: "pretrained"` with corresponding model identifiers
- Keep dates, tickers, weights, and execution settings identical

## 2) Run Backtests
- Produce two run folders under `backend/logs/`, each with `config.json` and `results.json`

## 3) Summarize Metrics
Create a simple table with portfolio-level metrics (TR, AR, Sharpe, Sortino, Calmar, MDD, Volatility, total trades) for both runs. Optionally add per-ticker breakdowns and equity/drawdown plots.

## 4) Report
Include model identifiers, seeds, and any notes from `config.json` in the write-up for reproducibility.

See also: `FINANCIAL_METRICS.md` and `PERFORMANCE_LOGGING.md`.


