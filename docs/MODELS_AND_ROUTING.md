# 🤖 Models & Routing Logic

This system uses four **LLM-based experts**, each activated in parallel.  
Each expert outputs a prediction distribution for a given trading day in the format:

> **Note:** The system is designed for **backtesting** using historical data, not for live daily inference. When running, set a fixed historical start date (e.g., `2008-01-01`) and iterate over the available data for evaluation.

---

## 🧠 Expert Outputs

Each expert receives a specific data modality and processes it using a **local LLM via Ollama**:

| Expert Name                  | Input Type              | Output Type                        |
|-----------------------------|--------------------------|-------------------------------------|
| Sentiment Expert            | News text (JSONL)        | `[p_buy, p_hold, p_sell]` based on daily news sentiment |
| Technical Timeseries Expert | OHLCV CSV                | `[p_buy, p_hold, p_sell]` based on price trend/momentum |
| Technical Chart Expert      | Chart image (PNG)        | `[p_buy, p_hold, p_sell]` based on chart pattern recognition |
| Fundamental Expert          | Financials (JSON)        | `[p_buy, p_hold, p_sell]` based on balance sheet / cash flow |

---

## 🔀 Routing & Aggregation

There is **no gating network** or regime-switching mechanism.  
Instead, the system **aggregates all expert outputs** using **fixed weights** (initially uniform):

```python
final_score = (
    w1 * sentiment_output +
    w2 * timeseries_output +
    w3 * chart_output +
    w4 * fundamental_output
)
final_decision = argmax(final_score)  # Buy / Hold / Sell

w1 = w2 = w3 = w4 = 0.25

```
