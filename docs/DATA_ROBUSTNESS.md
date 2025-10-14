# Data Robustness & Error Handling

This document describes how the MoE Trading System handles real-world data issues like missing values, date gaps, and varying availability.

---

## ✅ Current Protections

### **1. Data Loaders (First Line of Defense)**

#### **Price Data (`load_prices.py`)**
✅ **Handles:**
- Missing CSV files → Returns `None`
- Missing columns → Returns `None` with error log
- Invalid dates → Dropped with `errors='coerce'`
- Date gaps → Forward-fills OHLCV data (realistic approach)
- Timezone issues → Normalizes all to naive datetime
- Business days → Only considers trading days

```python
# Forward fill missing days (realistic for prices)
df_reindexed = df.ffill()
```

#### **News Data (`load_news.py`)**
✅ **Handles:**
- Missing JSONL files → Returns `None`
- Invalid JSON lines → Skips with warning, continues processing
- Invalid dates → Skips article, continues
- Empty content → Skips article
- Missing fields → Uses defaults or skips

```python
try:
    data = json.loads(line.strip())
except json.JSONDecodeError:
    logger.warning(f"Invalid JSON in line {line_num}")
    continue  # Skip bad line, keep going
```

#### **Fundamental Data (`load_fundamentals.py`)**
✅ **Handles:**
- Missing directories → Returns `None`
- Missing JSON files → Returns `None`
- Invalid JSON → Caught and logged
- Missing fields → Uses defaults

#### **Chart Data (`load_charts.py`)**
✅ **Handles:**
- Missing image directories → Returns `None`
- Missing chart periods → Returns partial data
- Invalid image files → Skips and continues

---

### **2. Experts (Second Line of Defense)**

All experts follow the **same defensive pattern**:

```python
def analyze_X(self, ticker, date):
    try:
        # Try to load data
        data = load_data(ticker, date)
        
        if not data:  # ← Missing data check
            return self._create_fallback_output("no_data")
        
        # Try LLM analysis
        result = analyze_with_llm(data)
        
        if result:
            return result
        
        # Fallback to rules
        return rule_based_analysis(data)
        
    except Exception as e:  # ← Catch-all safety net
        logger.error(f"Error: {e}")
        return self._create_fallback_output("error")
```

#### **Fallback Behavior (All Experts)**
When data is missing or invalid:
- Return neutral HOLD: `[0.0, 1.0, 0.0]`
- Low confidence: `0.1` to signal uncertainty
- Log warning for debugging
- **Never crash** - always return valid ExpertOutput

---

### **3. Aggregation (Third Line of Defense)**

The aggregator handles missing expert outputs:

```python
def aggregate_experts(...):
    expert_outputs = run_all_experts(...)
    
    if not expert_outputs:  # ← No experts succeeded
        return _create_fallback_result()  # HOLD with low confidence
    
    # Calculate weights with available experts
    weights = calculate_weights(expert_outputs)  # ← Adapts to available experts
```

**Dynamic Handling:**
- If 3/4 experts have data → Uses 3 experts, renormalizes weights
- If 1/4 experts have data → Uses 1 expert (better than nothing)
- If 0/4 experts have data → Returns HOLD with low confidence

---

### **4. Backtester (Fourth Line of Defense)**

```python
def _process_ticker(ticker, date, price):
    aggregation_result = aggregate_experts(ticker, date)
    
    if aggregation_result is None:  # ← Expert aggregation failed
        return  # Skip this ticker/date, continue backtest
```

**Behavior:**
- Missing data for one ticker/date → Skips that decision, continues
- System never crashes due to one bad data point
- Logs warnings for analysis

---

## 🔍 Real-World Scenarios

### **Scenario 1: Ticker has partial date coverage**
Example: `aa` has data 2010-2020, but we request 2005-2025

**What Happens:**
1. Loaders return `None` for dates outside coverage
2. Experts return fallback HOLD
3. Aggregator uses fallback result
4. Backtester skips those dates
5. **Result:** Only processes dates with data (2010-2020)

### **Scenario 2: One modality missing**
Example: News data missing for `aaau`

**What Happens:**
1. News loader returns `None`
2. Sentiment expert returns fallback HOLD with low conf
3. Other 3 experts work normally
4. Aggregator weights remaining 3 experts higher (entropy/confidence)
5. **Result:** System continues with 3/4 experts

### **Scenario 3: NaN in price data**
Example: CSV has `NaN` for some close prices

**What Happens:**
1. Price loader forward-fills NaN values
2. Expert receives valid data
3. **Result:** Uses last known price (realistic approach)

### **Scenario 4: Corrupted JSON in news**
Example: One line of `aa.jsonl` is malformed

**What Happens:**
1. News loader catches `JSONDecodeError`
2. Skips that line, logs warning
3. Continues reading other lines
4. **Result:** Uses all valid articles, ignores bad ones

### **Scenario 5: All data missing for a date**
Example: Request analysis for holiday (no trading)

**What Happens:**
1. All loaders return `None` or empty
2. All experts return fallback HOLD
3. Aggregator returns fallback result
4. Backtester skips (no decision made)
5. **Result:** No trade that day (correct behavior)

---

## 🛡️ Safety Guarantees

### **Never Crashes Due To:**
✅ Missing files
✅ Missing columns
✅ Invalid dates
✅ NaN/None values
✅ Corrupted JSON
✅ Empty datasets
✅ Partial data coverage
✅ LLM failures
✅ Network errors (Ollama down)

### **Always Returns:**
✅ Valid `ExpertOutput` or `None`
✅ Probabilities summing to 1.0
✅ Confidence in [0, 1]
✅ Proper fallback behavior
✅ Informative log messages

---

## ⚠️ Current Limitations (By Design)

### **1. Forward Fill for Prices**
- **Behavior:** Missing price days use last known price
- **Why:** Realistic for stocks (price doesn't change on non-trading days)
- **Risk:** Long gaps might propagate stale prices
- **Mitigation:** Log warnings for large gaps

### **2. No Imputation for News/Fundamentals**
- **Behavior:** Missing data → HOLD
- **Why:** Can't invent news or financial statements
- **Risk:** Reduced expert confidence
- **Mitigation:** Aggregator adapts weights

### **3. No Data Validation**
- **Behavior:** Assumes data is semantically correct
- **Why:** Focus on robustness, not data quality
- **Risk:** Bad data → bad signals
- **Mitigation:** Log data quality metrics

---

## 📊 Testing Coverage

Our Phase 5 tests verify robustness:

| Test | What It Checks |
|------|----------------|
| Missing Data Handling | All experts return HOLD for fake ticker |
| Fallback Consistency | All fallbacks have same behavior |
| Expert Output Structure | Probabilities sum to 1.0, no NaN |
| Real Data | System works when data available |

---

## 🔧 Recommendations for Production

### **If you want additional safety:**

1. **Add data validation:**
   ```python
   def validate_price_data(df):
       # Check for reasonable price ranges
       if (df['close'] < 0).any():
           logger.error("Negative prices detected!")
       # Check for extreme gaps
       if df['close'].pct_change().abs().max() > 0.5:
           logger.warning("50%+ price change detected")
   ```

2. **Add data quality metrics:**
   ```python
   def calculate_data_quality(df):
       coverage = len(df.dropna()) / len(df)
       return coverage  # 0.0 to 1.0
   ```

3. **Add circuit breakers:**
   ```python
   if missing_data_count > threshold:
       logger.error("Too much missing data, stopping backtest")
       return
   ```

4. **Add data checksums:**
   ```python
   # Detect if dataset changed mid-backtest
   checksum = hashlib.md5(open('data.csv','rb').read()).hexdigest()
   ```

---

## ✅ Summary

**The system is already robust!**

- ✅ All data loaders handle missing files
- ✅ All experts handle missing data
- ✅ Aggregator adapts to missing experts
- ✅ Backtester continues despite failures
- ✅ Never crashes on bad data
- ✅ Always logs issues for debugging

**Your data can have:**
- Missing tickers ✓
- Missing dates ✓
- Partial coverage ✓
- NaN values ✓
- Corrupted files ✓

**System will:**
- Log warnings ✓
- Use fallbacks ✓
- Continue processing ✓
- Return valid results ✓

The system is designed for **real-world messy data** from day one!

