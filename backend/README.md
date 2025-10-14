## 🧠 Developer & Assistant Guide (Research Orientation)

This backend is optimized for a minimal, research-friendly pipeline. Focus on correctness, simplicity, and reproducibility. For design details and how to interpret this codebase, see:

- [Cursor Guide](../docs/CURSOR_GUIDE.md)
- [System Overview](../docs/SYSTEM_OVERVIEW.md)
- [Data Description](../docs/DATA_DESCRIPTION.md)
- [Data Robustness & Error Handling](../docs/DATA_ROBUSTNESS.md) ⭐
- [Models & Routing Logic](../docs/MODELS_AND_ROUTING.md)
- [Financial Metrics for Comparative Evaluation](../docs/FINANCIAL_METRICS.md)
- [Performance Logging System (Comparison-Ready)](../docs/PERFORMANCE_LOGGING.md)
- [Expert Interface and Output Schema](../docs/EXPERT_INTERFACE.md)
- [Config Schema](../docs/CONFIG_SCHEMA.md)
- [Aggregation & Sizing Rules](../docs/AGGREGATION_AND_SIZING.md)
- [Dynamic Weighting Strategies](../docs/DYNAMIC_WEIGHTING.md)
- [Backtester Lifecycle](../docs/BACKTESTER_LIFECYCLE.md)
- [Comparison Guide](../docs/COMPARISON_GUIDE.md)
- [Config Templates (Plug-and-Play)](../docs/CONFIG_TEMPLATES.md)
- [Backend Implementation Plan](../docs/IMPLEMENTATION_PLAN_BACKEND.md) ⭐

Comparison protocol in brief:
- Keep dataset, date range, and portfolio config identical across runs
- Use fixed aggregation weights when comparing LLM vs non-LLM experts
- Record expert implementations and model identifiers in `logs/<run>/config.json`

## ✅ Implementation Status

**All 7 phases complete!** See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for details.

- ✅ Phase 1-6: Core implementation
- ✅ Phase 7: Testing & validation (36/36 tests passed)
- ✅ Smoke test: System validated end-to-end

## 🚀 Quick Start

```bash
# Smoke test (1 ticker, 10 days - ~1 minute)
python run_backtest.py --config config_smoke_test.json

# Small test (3 tickers, 1 month)
python run_backtest.py --config config_llm.json

# Full year test (3 tickers, 1 year)
python run_backtest.py --config config_full_test.json
```

See [USAGE.md](USAGE.md) for detailed usage instructions.

Available configs:
- `config_smoke_test.json` — Quick validation (1 ticker, 10 days)
- `config_llm.json` — LLM baseline (3 tickers, 1 month)
- `config_full_test.json` — Full year test (3 tickers, 2020)
- `config_pretrained.json` — Pre-trained baseline (update model paths when ready)
