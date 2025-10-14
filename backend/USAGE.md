# Usage Guide for MoE Trading System

## Quick Start

The MoE Trading System uses a single entry point: `run_backtest.py`

### Basic Usage

```bash
cd backend
python run_backtest.py --config <config_file.json>
```

---

## Available Configurations

### 1. Smoke Test (Fast - ~1 minute)
Quick validation with minimal data:
- 1 ticker (aa)
- 10 days (2024-01-01 to 2024-01-10)
- $100k initial capital

```bash
python run_backtest.py --config config_smoke_test.json
```

### 2. Small Test (1 month)
Standard test for development:
- 3 tickers (aa, aaau, aacg)
- 1 month (2024-01-01 to 2024-01-31)
- $100k initial capital

```bash
python run_backtest.py --config config_llm.json
```

### 3. Full Year Test (Long - several hours)
Comprehensive validation:
- 3 tickers (aa, aaau, aacg)
- 1 year (2020-01-01 to 2020-12-31)
- $1M initial capital

```bash
python run_backtest.py --config config_full_test.json
```

### 4. Pre-trained Models (When Ready)
Same as LLM but with pre-trained experts:

```bash
python run_backtest.py --config config_pretrained.json
```

---

## Output

All runs create a folder in `logs/` with these files:

```
logs/backtest_llm_<dates>/
├── config.json           # Configuration and experiment metadata
├── results.json          # Final metrics (Sharpe, returns, drawdown)
├── portfolio_daily.json  # Daily portfolio state
├── tickers_daily.json    # Daily decisions with expert weights
└── trades.json          # All executed trades
```

---

## Example Output

```bash
$ python run_backtest.py --config config_smoke_test.json

======================================================================
🚀 MoE Trading System - Backtest Runner
======================================================================

📄 Loading configuration from: config_smoke_test.json
✓ Configuration loaded successfully
  Run ID: backtest_llm_smoke_test
  Date range: 2024-01-01 to 2024-01-10
  Tickers: aa
  Strategy: entropy

🧠 Expert Configuration:
  - sentiment: llm (llama3.1:8b)
  - timeseries: llm (llama3.1:8b)
  - chart: llm (llama3.1:8b)
  - fundamental: llm (llama3.1:8b)

⚙️  Initializing backtester...
✓ Backtester initialized
  Output directory: logs/backtest_llm_smoke_test/

🏃 Running backtest...
  [Progress shown here]

======================================================================
✅ BACKTEST COMPLETED SUCCESSFULLY
======================================================================

📊 Results Summary:
  Duration: 45.2 seconds
  Output directory: logs/backtest_llm_smoke_test/

💰 Key Metrics:
  Total Return: 2.5%
  Sharpe Ratio: 1.234
  Max Drawdown: -1.2%
  Total Trades: 3

🎉 Backtest complete! Check logs/backtest_llm_smoke_test/ for detailed results.
```

---

## Creating Custom Configs

Copy an existing config and modify:

```bash
cp config_llm.json my_custom_config.json
# Edit dates, tickers, etc.
python run_backtest.py --config my_custom_config.json
```

Key fields to customize:
- `backtest.start_date` / `end_date` - Date range
- `backtest.tickers` - List of tickers
- `portfolio.initial_capital` - Starting cash
- `aggregation.strategy` - "entropy", "fixed", or "confidence"
- `logging.run_id` - Output folder name

---

## Troubleshooting

### Config file not found
```bash
# Make sure you're in the backend directory
cd backend
ls *.json  # Should show config files
```

### No data for tickers/dates
- Check that your date range has data in `dataset/`
- Verify tickers exist in `dataset/HS500-samples/`

### Out of memory
- Reduce date range or number of tickers
- Use smoke test config first

---

## Comparing Runs

To compare LLM vs Pre-trained:

```bash
# Run LLM baseline
python run_backtest.py --config config_llm.json

# Run pre-trained (when ready)
python run_backtest.py --config config_pretrained.json

# Compare results.json from both runs
```

See `docs/COMPARISON_GUIDE.md` for detailed comparison procedures.

