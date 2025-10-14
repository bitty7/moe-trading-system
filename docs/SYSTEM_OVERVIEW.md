# 🧠 System Overview (Research-Focused)

This project is a minimal-yet-complete **Mixture-of-Experts (MoE)** backtesting system intended for comparative research. The current baseline uses **local LLM-based experts** (via Ollama). Later, we will introduce **pre-trained, non-LLM expert implementations** that follow the same interfaces to enable apples-to-apples comparisons.

---

## ⚙️ Daily Workflow (Backtesting Mode)

> **Note:** This system is intended for **backtesting** over historical data, not live daily inference. Use a fixed historical start date (e.g., `2008-01-01`) and run across the available range for evaluation.

Each day (in the backtest loop), for every stock ticker, the system:
1. Loads the latest available data from multiple modalities (as of the current backtest date)
2. Passes each modality to its corresponding expert implementation (LLM baseline today; pre-trained variants later)
3. Aggregates all expert outputs using a simple or learned weighting mechanism
4. Produces a final trading decision: **Buy**, **Hold**, or **Sell**

---

## 🧠 Expert Modules

Baseline experts use **local LLMs via Ollama**. Future variants may use pre-trained, non-LLM models. Both must output the same schema for fair comparison. The system runs fully **offline** in the baseline.

| Expert Name                  | Input Type                             | LLM Role |
|-----------------------------|-----------------------------------------|----------|
| **Sentiment Expert**        | Daily news articles (`.jsonl`)          | Analyze daily news to produce a sentiment score (-1 to 1) or classification (Positive/Neutral/Negative) |
| **Technical Timeseries Expert** | Daily OHLCV data (`.csv`)           | Interpret short-term price movements, detect momentum patterns, trend reversals |
| **Technical Chart Expert**  | Candlestick chart images (`.png`)       | Analyze visual chart patterns (e.g., head & shoulders, breakouts) and summarize trends |
| **Fundamental Expert**      | Financial statements (`.json`)          | Extract signals from earnings, balance sheets, cash flow, and equity statements |

All experts generate a 3-class probability distribution:
`[p_buy, p_hold, p_sell]`

---

## 🔁 Aggregation Strategy (Simple)

All experts are **always active**. The system uses a **simple weighted aggregation** (initially uniform). This keeps the pipeline minimal for research comparability. Potential future extensions:
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
