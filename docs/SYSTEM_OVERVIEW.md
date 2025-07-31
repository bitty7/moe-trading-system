# 🧠 System Overview

This is a fully local **LLM-driven financial trading system** built using a **Mixture-of-Experts (MoE)** architecture. The system is designed to simulate real-world daily trading decisions by leveraging four **parallel LLM-based experts**, each specializing in a different financial data modality.

---

## ⚙️ Daily Workflow (Backtesting Mode)

> **Note:** This system is primarily intended for **backtesting** over historical data, not for live daily inference. Since the available data is historical and not updated daily, users should specify a fixed historical start date (e.g., `2008-01-01`) and run the system over the available data range for testing and evaluation purposes.

Each day (in the backtest loop), for every stock ticker, the system:
1. Loads the latest available data from multiple modalities (as of the current backtest date)
2. Passes each modality to its corresponding **LLM-powered expert** using **Ollama**
3. Aggregates all expert outputs using a simple or learned weighting mechanism
4. Produces a final trading decision: **Buy**, **Hold**, or **Sell**

---

## 🧠 LLM-Based Expert Modules

All experts use **local LLMs via Ollama**, which may later be replaced with remote APIs (e.g., DeepSeek, Groq, TogetherAI, etc.). For now, the system is designed to work **offline**, ensuring privacy and low latency.

| Expert Name                  | Input Type                             | LLM Role |
|-----------------------------|-----------------------------------------|----------|
| **Sentiment Expert**        | Daily news articles (`.jsonl`)          | Analyze daily news to produce a sentiment score (-1 to 1) or classification (Positive/Neutral/Negative) |
| **Technical Timeseries Expert** | Daily OHLCV data (`.csv`)           | Interpret short-term price movements, detect momentum patterns, trend reversals |
| **Technical Chart Expert**  | Candlestick chart images (`.png`)       | Analyze visual chart patterns (e.g., head & shoulders, breakouts) and summarize trends |
| **Fundamental Expert**      | Financial statements (`.json`)          | Extract signals from earnings, balance sheets, cash flow, and equity statements |

All experts generate a 3-class probability distribution:  
`[p_buy, p_hold, p_sell]`

---

## 🔁 Aggregation Strategy

All experts are **always active**. The system uses a **simple weighted aggregation** (initially uniform), but may evolve to support:
- Learned attention-based routing
- Conditional weighting based on confidence scores
- External macro-indicators (future enhancement)

```python
final_score = (
    w1 * sentiment_output +
    w2 * timeseries_output +
    w3 * chart_output +
    w4 * fundamental_output
)
decision = argmax(final_score)

```
