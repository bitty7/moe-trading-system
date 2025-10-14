# Aggregation and Position Sizing (Minimal Rules)

## Aggregation (Simple Dynamic Weighting)
- Inputs: Four expert `probabilities` vectors
- Weighting strategy: configurable via `aggregation.strategy` in config
  - `"fixed"`: Use predefined weights (e.g., `[0.25, 0.25, 0.25, 0.25]`)
  - `"entropy"`: ⭐ **RECOMMENDED** — Weight by inverse entropy of probabilities (lower entropy = higher weight)
  - `"confidence"`: Weight by expert-reported confidence scores (future option)
  - `"performance"`: Weight by recent historical accuracy (requires ground truth, future option)
- Rule: Weighted sum, then `argmax`
```python
final_score = w1*sentiment + w2*timeseries + w3*chart + w4*fundamental
decision = argmax(final_score)  # BUY/HOLD/SELL
```
- For comparability: use the same weighting strategy across LLM vs pre-trained runs
- Recommended start: `"entropy"` (simple, adaptive, no extra data needed)

See `DYNAMIC_WEIGHTING.md` for detailed strategy descriptions.

## Position Sizing (Deterministic)
- If BUY: allocate `position_sizing * total_equity` subject to
  - reserve `cash_reserve`
  - respect `min_cash_reserve`
  - cap at `max_positions`
- If SELL: close position for the ticker
- If HOLD: maintain current position

## Transaction Assumptions
- Apply `transaction_cost` and `slippage` uniformly to all trades
- Use daily close prices for fills

## Rationale
These rules keep the pipeline simple, deterministic, and comparable while still producing realistic portfolio dynamics.


