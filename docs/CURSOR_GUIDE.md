# 📘 Cursor Guide: How to Assist This Project

This project implements a Mixture-of-Experts (MoE) system for financial trading with four parallel LLM-based experts:

> **Note:** The system is designed for **backtesting** using historical data, not for live daily inference. When running experiments, set a fixed historical start date (e.g., `2008-01-01`) and iterate over the available data for evaluation.

1. `sentiment_expert.py`: Reads daily news from JSON and outputs a value from -1 (very negative) to +1 (very positive).
2. `technical_timeseries_expert.py`: Uses daily OHLCV stock price CSVs and technical indicators.
3. `technical_chart_expert.py`: Uses annual stock chart images to generate image embeddings and predict trends.
4. `fundamental_expert.py`: Reads and interprets financial statements (balance sheets, cash flow, equity) from JSON files.

**Gating Network** in `gating_network.py` produces weights for each expert based on market regime signals.  
**Aggregator** in `aggregator.py` combines the expert outputs into one final decision (Buy/Hold/Sell).

> ✅ All experts are always active. No single-expert activation is used.

**Cursor Recommendations:**
- Suggest improvements to modular design, caching, batch processing
- Optimize image loading and chart embedding strategy
- Help parse irregular date formats and align them
- Assist with vector aggregation logic and backtesting

Data is structured under `/data/<company_symbol>/`. Inference is run in a backtest loop via `run_daily_inference.py` or similar scripts.

