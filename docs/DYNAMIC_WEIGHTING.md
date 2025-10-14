# Dynamic Weighting Strategies (Simple & Effective)

While fixed weights keep the pipeline minimal, dynamic weighting can improve performance by adapting to expert reliability. Here are simple approaches ranked by complexity:

---

## Option 1: Confidence-Based Weighting (Simplest)

Each expert outputs a `confidence` score. Weight by confidence, then aggregate.

```python
# Expert outputs
expert_outputs = [
    {"probs": [0.6, 0.3, 0.1], "confidence": 0.8},  # sentiment
    {"probs": [0.4, 0.5, 0.1], "confidence": 0.9},  # timeseries
    {"probs": [0.5, 0.4, 0.1], "confidence": 0.6},  # chart
    {"probs": [0.3, 0.6, 0.1], "confidence": 0.7},  # fundamental
]

# Normalize confidences to weights
weights = [e["confidence"] for e in expert_outputs]
weights = weights / sum(weights)  # [0.25, 0.28, 0.19, 0.22]

# Aggregate
final_probs = sum(w * e["probs"] for w, e in zip(weights, expert_outputs))
```

**Pros:**
- Simple to implement
- Expert-level self-calibration
- No training required

**Cons:**
- LLMs may not be well-calibrated
- Pre-trained models need calibration post-training

---

## Option 2: Performance-Based Weighting (Adaptive)

Track each expert's recent accuracy and adjust weights based on historical performance.

```python
# Maintain rolling accuracy per expert (last N days)
expert_accuracy = {
    "sentiment": 0.65,
    "timeseries": 0.72,
    "chart": 0.58,
    "fundamental": 0.68
}

# Convert to weights (softmax or normalize)
weights = softmax(expert_accuracy)  # or normalize directly
```

**Pros:**
- Data-driven adaptation
- Rewards consistently good experts
- Works for both LLM and pre-trained

**Cons:**
- Requires ground truth labels for "correct" predictions
- Need to define what "correct" means (profitable trade? direction?)
- Lookback window is a hyperparameter

---

## Option 3: Hybrid (Confidence + Performance)

Combine expert confidence with historical performance.

```python
# Combine both signals
raw_weights = [
    expert_accuracy[name] * expert_output["confidence"]
    for name, expert_output in zip(expert_names, expert_outputs)
]

# Normalize
weights = raw_weights / sum(raw_weights)
```

**Pros:**
- Balances self-assessment with track record
- More robust than either alone

**Cons:**
- More complex
- Still needs ground truth for performance tracking

---

## Option 4: Uncertainty-Based Weighting

Weight by inverse entropy of expert predictions. Low entropy = high confidence in one action.

```python
import numpy as np

def entropy(probs):
    return -sum(p * np.log(p + 1e-10) for p in probs)

# Lower entropy = more confident = higher weight
entropies = [entropy(e["probs"]) for e in expert_outputs]
weights = [1 / (ent + 1e-6) for ent in entropies]
weights = weights / sum(weights)
```

**Pros:**
- No external confidence score needed
- Works automatically from probability distributions
- No training or ground truth required

**Cons:**
- May favor overconfident experts
- Doesn't account for accuracy

---

## Recommended: Start with Option 1 or 4

**For immediate implementation:**
- **Option 4 (Entropy-based)**: Zero additional work; just compute from probabilities
- **Option 1 (Confidence-based)**: If experts already output confidence scores

**For research comparisons:**
Run multiple weighting strategies and compare:
1. Fixed uniform weights (baseline)
2. Entropy-based weights
3. Confidence-based weights (if available)

This lets you study: "Do dynamic weights improve performance? Which strategy works best for LLM vs pre-trained?"

---

## Implementation Notes

### Config Schema Addition
```json
{
  "aggregation": {
    "strategy": "fixed" | "entropy" | "confidence" | "performance" | "hybrid",
    "fixed_weights": [0.25, 0.25, 0.25, 0.25],
    "performance_window": 30,  // for performance-based
    "expert_order": ["sentiment", "timeseries", "chart", "fundamental"]
  }
}
```

### Comparability
- When comparing LLM vs pre-trained, use the **same weighting strategy** for both runs
- Include `aggregation.strategy` in logged `config.json`
- Can also run ablations: same expert type with different weighting strategies

### Simplicity vs Performance Trade-off
- Start with **fixed** (simplest) or **entropy** (simple + adaptive)
- Add **performance-based** only if you have clear ground truth labels
- Avoid **hybrid** until you validate simpler approaches

---

## Next Steps
1. Choose initial strategy (recommend: entropy-based)
2. Update `AGGREGATION_AND_SIZING.md` with chosen approach
3. Update config templates to include `aggregation.strategy`
4. Implement aggregator with strategy switch
5. Log weights used per decision in `tickers_daily.json`

