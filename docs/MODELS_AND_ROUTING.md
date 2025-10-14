# 🤖 Models & Routing Logic (Comparable Baselines)

This system defines four experts and a minimal aggregation mechanism to enable clean comparisons between:

- LLM-based experts (baseline today, local via Ollama)
- Pre-trained, non-LLM experts (future work using the same interfaces)

> **Note:** The system is designed for **backtesting** using historical data, not for live daily inference. When running, set a fixed historical start date (e.g., `2008-01-01`) and iterate over the available data for evaluation.

---

## 🧠 Expert Outputs

Each expert receives a specific data modality and must produce the same output schema regardless of implementation (LLM or non-LLM):

| Expert Name                  | Input Type              | Output Type                        |
|-----------------------------|--------------------------|-------------------------------------|
| Sentiment Expert            | News text (JSONL)        | `[p_buy, p_hold, p_sell]` from daily news sentiment |
| Technical Timeseries Expert | OHLCV CSV                | `[p_buy, p_hold, p_sell]` from price trend/momentum |
| Technical Chart Expert      | Chart image (PNG)        | `[p_buy, p_hold, p_sell]` from chart pattern recognition |
| Fundamental Expert          | Financials (JSON)        | `[p_buy, p_hold, p_sell]` from balance sheet / cash flow |

---

## 🔀 Routing & Aggregation (Simple, No Gating)

There is **no gating** or regime switching. The system **aggregates all expert outputs** using **fixed weights** (initially uniform) for clarity and repeatability:

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

Comparison protocol:
- Keep weights fixed across runs when comparing LLM vs non-LLM experts
- Hold dataset, dates, and portfolio config constant
- Record model identifiers in `config.json` and store runs under distinct `backend/logs/<run_id>/`

See `docs/FINANCIAL_METRICS.md` for evaluation metrics and `docs/PERFORMANCE_LOGGING.md` for logged file formats.
