# Config Schema (Backtests and Expert Selection)

This schema defines a minimal, explicit configuration for reproducible backtests and for switching between LLM-based and pre-trained experts.

## Required Fields (conceptual)
```json
{
  "backtest": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "tickers": ["aa", "aaau", "aacg"],
    "seed": 42
  },
  "portfolio": {
    "initial_capital": 100000,
    "position_sizing": 0.15,
    "max_positions": 3,
    "cash_reserve": 0.2,
    "min_cash_reserve": 0.1
  },
  "execution": {
    "transaction_cost": 0.001,
    "slippage": 0.0005
  },
  "experts": {
    "sentiment": {"impl": "llm", "model": "llama3.1:8b"},
    "timeseries": {"impl": "llm", "model": "llama3.1:8b"},
    "chart": {"impl": "llm", "model": "llama3.1:8b"},
    "fundamental": {"impl": "llm", "model": "llama3.1:8b"}
  },
  "aggregation": {
    "strategy": "entropy",
    "fixed_weights": [0.25, 0.25, 0.25, 0.25],
    "expert_order": ["sentiment", "timeseries", "chart", "fundamental"],
    "performance_window": 30
  },
  "logging": {
    "log_dir": "backend/logs/",
    "run_id": "backtest_2024_01_15_aa_aaau"
  }
}
```

## Expert Implementation Switch
- `impl`: `"llm" | "pretrained"`
- `model`: Identifier string (e.g., `"llama3.1:8b"` or a local path/name for pre-trained models)

All other pipeline settings remain identical between runs to ensure fairness.

## Aggregation Strategy
- `strategy`: Weighting method (`"fixed"`, `"entropy"`, `"confidence"`, `"performance"`)
- `fixed_weights`: Used when `strategy: "fixed"`; fallback for other strategies
- `performance_window`: Rolling window size for performance-based weighting

## Run Metadata and Reproducibility
- Always set `seed`
- Record exact model identifiers and aggregation strategy
- Keep `strategy`, `transaction_cost`, and `slippage` constant across comparative runs
- Store the full config in `logs/<run_id>/config.json`


