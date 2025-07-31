# 🚀 Implementation Plan

This document outlines the **recommended implementation order** for building the Mixture-of-Experts (MoE) LLM-based financial trading system. It breaks down the project into five logical development phases to ensure smooth progression, early testing, and minimal integration issues.

---

## ✅ Recommended Implementation Order

---

### 📦 Phase 1: Core Infrastructure (Foundation)

These components are foundational and will be reused across all modules.

- `core/config.py` — Environment variables and system settings
- `core/date_utils.py` — Standardized date parsing and formatting
- `core/types.py` — Shared data structures (e.g., DailySignal, ExpertOutput)
- `core/enums.py` — Constants and enums (e.g., Buy/Hold/Sell labels)

---

### 📊 Phase 2: Data Loaders + Experts (Incremental Development)

Build and test experts one at a time. Each expert has a paired data loader module.

1. **Time Series Expert**
   - `data_loader/load_prices.py`  
   - `experts/technical_timeseries_expert.py`  
   - ✅ Most straightforward — work with structured CSVs

2. **Sentiment Expert**
   - `data_loader/load_news.py`  
   - `experts/sentiment_expert.py`  
   - 📄 Add text processing, date normalization, and LLM calls

3. **Fundamental Expert**
   - `data_loader/load_fundamentals.py`  
   - `experts/fundamental_expert.py`  
   - 📊 Parse deeply nested financial statements (JSON)

4. **Chart Expert**
   - `data_loader/load_charts.py`  
   - `experts/technical_chart_expert.py`  
   - 🖼️ Load and preprocess images, most complex due to embeddings

---

### 🔁 Phase 3: Integration & Aggregation

- `aggregation/aggregator.py` — Combine outputs of all experts
- `gating/gating_network.py` — (Optional) Assign weights dynamically or uniformly

---

### 💼 Phase 4: Backtesting Engine

- `evaluation/portfolio_simulator.py` — Tracks positions and cash
- `evaluation/metrics.py` — Computes all financial KPIs (Sharpe, SoR, etc.)
- `evaluation/trade_logger.py` — Logs daily expert outputs and trades
- `evaluation/backtester.py` — Runs full backtest loop over historical data

---

### 🎯 Phase 5: User Interface & Inference

- `inference/run_daily_inference.py` — Entry point to run daily analysis and predictions
- Prepare for frontend/dashboard integration (e.g., Streamlit)

---

## 💡 Why This Order Works

---

### 🔧 Phase 1: Core Benefits
- Foundation for all other files
- Ensures consistent types and configs from the beginning
- Early structure avoids repeated refactoring

---

### 📊 Phase 2: Expert Benefits
- Experts are independent and testable in isolation
- Fast feedback loop: You can test each expert on real data as soon as it's built
- Ollama LLM integration can be validated early

---

### 🔄 Phase 3: Aggregation Benefits
- Combines outputs in a modular way
- Lets you run small pipelines with 1–4 experts easily
- Enables early ensemble experiments

---

### 🧪 Phase 4: Backtesting Benefits
- Evaluate end-to-end profitability and risk
- Track key metrics like Sharpe Ratio and Max Drawdown
- Enables comparison across strategies and time periods

---

### 🎯 Phase 5: UX Benefits
- Makes your system usable for both CLI and frontend demos
- Gets you ready for hackathon demos, judges, and teammates
- Encourages reusability by wrapping core logic behind one inference function

---

Let us know when you're ready to scaffold each phase — or if you'd like to auto-generate the base structure with placeholders for each module.
