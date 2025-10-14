# Backend Implementation Plan (LLM Baseline)

This document provides a step-by-step plan to implement the simplified, research-focused backend with entropy-based dynamic weighting for the LLM baseline.

---

## 🎯 **Goals**
1. Create a minimal, robust pipeline for LLM-based experts
2. Implement entropy-based dynamic weighting
3. Ensure clean logging with experiment metadata
4. Enable plug-and-play config switching for future pre-trained comparison
5. Validate with small smoke tests before full runs

---

## 📋 **Implementation Steps**

### **Phase 1: Configuration & Setup** ⚙️

#### **Step 1.1: Extend BacktesterConfig**
**File:** `backend/core/data_types.py`

**Changes:**
- Add new fields to `BacktesterConfig`:
  ```python
  seed: int = 42
  experts: Dict[str, Dict[str, str]] = field(default_factory=dict)
  aggregation: Dict[str, Any] = field(default_factory=dict)
  run_id: str = ""
  notes: str = ""
  ```
- Keep existing fields unchanged for backward compatibility
- Add validation in `__post_init__` if needed

**Test:** Create a config object manually and verify all fields work

---

#### **Step 1.2: Create Config Loader**
**File:** `backend/core/config_loader.py` (NEW)

**Implementation:**
- Function: `load_config(config_path: str) -> BacktesterConfig`
- Read JSON file (`config_llm.json` or `config_pretrained.json`)
- Parse and validate all fields
- Convert to `BacktesterConfig` object
- Handle missing/invalid fields gracefully

**Test:** Load `config_llm.json` and print the BacktesterConfig object

---

### **Phase 2: Aggregation & Weighting** 🔀

#### **Step 2.1: Implement Entropy Calculation**
**File:** `backend/aggregation/expert_aggregator.py`

**Changes:**
- Add entropy calculation function:
  ```python
  def calculate_entropy(probabilities: List[float]) -> float:
      """Calculate Shannon entropy of probability distribution."""
      return -sum(p * np.log(p + 1e-10) for p in probabilities)
  ```
- Add entropy-based weighting function:
  ```python
  def calculate_entropy_weights(expert_outputs: List[ExpertOutput]) -> List[float]:
      """Calculate weights based on inverse entropy."""
      entropies = [calculate_entropy(output.probabilities.to_list()) 
                   for output in expert_outputs]
      inverse_entropies = [1.0 / (e + 1e-6) for e in entropies]
      total = sum(inverse_entropies)
      return [w / total for w in inverse_entropies]
  ```

**Test:** 
- Test with mock expert outputs
- Verify: high certainty → low entropy → high weight
- Verify: weights sum to 1.0

---

#### **Step 2.2: Add Strategy Switch to Aggregator**
**File:** `backend/aggregation/expert_aggregator.py`

**Changes:**
- Modify `aggregate_experts()` to accept `strategy` parameter
- Implement strategy switch:
  ```python
  if strategy == "fixed":
      weights = fixed_weights
  elif strategy == "entropy":
      weights = calculate_entropy_weights(expert_outputs)
  elif strategy == "confidence":
      weights = [e.confidence.confidence_score for e in expert_outputs]
      weights = normalize(weights)
  ```
- Default to `"entropy"`
- Log which strategy was used and the resulting weights

**Test:** Run aggregation with different strategies and verify weight calculations

---

#### **Step 2.3: Update Aggregation to Use Config**
**File:** `backend/aggregation/expert_aggregator.py`

**Changes:**
- Pass `aggregation_config: Dict` to aggregator
- Extract `strategy` from config
- Extract `fixed_weights` as fallback
- Use config values instead of hardcoded defaults

**Test:** Pass mock config dict and verify strategy selection works

---

### **Phase 3: Logging & Metadata** 📝

#### **Step 3.1: Add Experiment Metadata to Logging**
**File:** `backend/evaluation/performance_logger.py`

**Changes:**
- Update `_save_config()` method to include experiment metadata:
  ```python
  config_data = {
      # ... existing fields ...
      "experiment": {
          "experts": config.experts,  # {"sentiment": {"impl": "llm", "model": "..."}, ...}
          "aggregation": {
              "strategy": config.aggregation.get("strategy", "entropy"),
              "fixed_weights": config.aggregation.get("fixed_weights", [0.25]*4),
              "expert_order": config.aggregation.get("expert_order", [...])
          },
          "seed": config.seed,
          "notes": config.notes
      }
  }
  ```

**Test:** Create logger, save config, verify `config.json` has experiment section

---

#### **Step 3.2: Log Dynamic Weights Per Decision**
**File:** `backend/evaluation/performance_logger.py`

**Changes:**
- In `log_daily_ticker()`, ensure we capture the weights used:
  ```python
  "expert_contributions": {
      "sentiment": {
          "weight": actual_weight_used,  # from aggregation
          "confidence": expert_confidence,
          "probabilities": [p_buy, p_hold, p_sell],
          "reasoning": "..."
      },
      # ... other experts
  }
  ```
- Verify `AggregationResult` already provides this info
- If not, add `actual_weights_used` field to `AggregationResult`

**Test:** Run one day, check `tickers_daily.json` for weight values

---

#### **Step 3.3: Update Backtest ID Format**
**File:** `backend/evaluation/backtester.py` or wherever backtest_id is generated

**Changes:**
- Change ID format from:
  - `backtest_20250801_102305_aa_aaau_aacg`
- To:
  - `backtest_llm_20240101_20240131` (or use run_id from config)
- Use config.run_id if provided, otherwise generate with impl type prefix

**Test:** Verify folder names include "llm" or "pretrained"

---

### **Phase 4: Entry Point & Runner** 🚀

#### **Step 4.1: Create New Entry Point**
**File:** `backend/run_backtest.py` (NEW)

**Implementation:**
```python
#!/usr/bin/env python3
"""
Clean entry point for running backtests with JSON config.
Usage: python run_backtest.py --config config_llm.json
"""

import argparse
from core.config_loader import load_config
from evaluation.backtester import HighPerformanceBacktester

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config JSON")
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Run backtest
    backtester = HighPerformanceBacktester(config)
    results = backtester.run()
    
    print(f"Backtest completed: {config.run_id}")
    print(f"Results saved to: logs/{config.run_id}/")
    
    return results

if __name__ == "__main__":
    main()
```

**Test:** Run with `config_llm.json` on 1 ticker, 1 day

---

#### **Step 4.2: Update Backtester to Use Aggregation Config**
**File:** `backend/evaluation/backtester.py`

**Changes:**
- Pass `config.aggregation` to expert aggregator
- Pass `config.seed` to experts (if they support it)
- Ensure deterministic execution with seed

**Test:** Run twice with same config, verify identical results

---

### **Phase 5: Expert Alignment** 🧠

#### **Step 5.1: Verify Expert Outputs**
**File:** `backend/experts/*.py`

**Checks:**
- All return `ExpertOutput` with probabilities and confidence ✓
- All handle missing data consistently
- All have similar fallback behavior (return neutral HOLD)

**Action:** Document any inconsistencies, fix if needed

---

#### **Step 5.2: Add Seed Support to Experts (if needed)**
**File:** `backend/experts/*.py` and `backend/core/llm_client.py`

**Changes (if LLM calls aren't deterministic):**
- Add `seed` parameter to LLM client
- Pass seed through from config
- Verify same input + same seed = same output

**Test:** Run same ticker/date twice, verify identical probabilities

---

### **Phase 6: Cleanup** 🧹

#### **Step 6.1: Delete Unused Files**
**Files to delete:**
- `backend/aggregation/aggregator.py` (empty template)
- Any other unused/obsolete files

**Action:** Move to archive or delete after confirming they're not imported anywhere

---

#### **Step 6.2: Update Documentation**
**Files to update:**
- `backend/README.md` — Add usage instructions for `run_backtest.py`
- `docs/CONFIG_TEMPLATES.md` — Add example commands
- Add any clarifications from implementation

---

### **Phase 7: Testing & Validation** ✅

#### **Step 7.1: Unit Tests**
**Tests to create/update:**
- Config loader test
- Entropy calculation test
- Strategy switch test
- Logging metadata test

**Action:** Create `test/test_implementation.py` with focused tests

---

#### **Step 7.2: Smoke Test (1 ticker, 10 days)**
**Test:** `python run_backtest.py --config config_smoke_test.json`

**Config:**
```json
{
  "backtest": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-10",
    "tickers": ["aa"],
    "seed": 42
  },
  ...
}
```

**Verify:**
- Runs without errors
- Creates log folder
- `config.json` has experiment metadata
- `results.json` has metrics
- Weights in `tickers_daily.json` are entropy-based (not uniform)

---

#### **Step 7.3: Small Test (3 tickers, 1 month)**
**Test:** Update config to 3 tickers, 30 days

**Verify:**
- Processing speed reasonable (~0.1-1 days/sec)
- All tickers have data
- Metrics calculated correctly
- No NaN values

---

#### **Step 7.4: Full Test (3 tickers, 1 year)**
**Test:** `python run_backtest.py --config config_llm.json`

**Verify:**
- Completes successfully
- Results look reasonable (returns, Sharpe, etc.)
- Ready for comparison with pre-trained baseline

---

## 📊 **Success Criteria**

### **Minimal Success (Phase 1-4):**
- ✅ Config loads from JSON
- ✅ Entropy weighting implemented
- ✅ Experiment metadata logged
- ✅ New entry point works
- ✅ Smoke test passes

### **Full Success (Phase 1-7):**
- ✅ All tests pass
- ✅ 1-month backtest runs successfully
- ✅ Logging matches specification
- ✅ Code is clean and documented
- ✅ Ready for pre-trained implementation

---

## 🔄 **Order of Implementation**

**Recommended sequence (can work in parallel on some):**
1. Step 1.1 → 1.2 (Config foundation)
2. Step 2.1 → 2.2 → 2.3 (Aggregation)
3. Step 3.1 → 3.2 → 3.3 (Logging)
4. Step 4.1 → 4.2 (Entry point)
5. Step 5.1 → 5.2 (Expert alignment)
6. Step 6.1 → 6.2 (Cleanup)
7. Step 7.1 → 7.2 → 7.3 → 7.4 (Testing)

**Time estimate:**
- Phases 1-4: ~4-6 hours (core implementation)
- Phases 5-6: ~1-2 hours (alignment & cleanup)
- Phase 7: ~2-3 hours (testing & validation)
- **Total: ~7-11 hours** (assuming no major issues)

---

## 🚨 **Common Pitfalls to Avoid**

1. **Don't change too much at once** — implement incrementally
2. **Test after each step** — don't wait until the end
3. **Keep backward compatibility** — old tests should still work
4. **Log everything** — weights, strategies, metadata
5. **Handle missing data consistently** — across all experts
6. **Verify determinism** — same config = same results

---

## 📝 **Notes**

- **Entropy is the chosen strategy** for dynamic weighting (not confidence)
- **Fixed weights remain as fallback** and comparison baseline
- **Confidence-based weighting** can be added later as an option
- **Pre-trained implementation** will follow the same pattern with different expert implementations

---

**Ready to start implementation when you are!** 🚀

