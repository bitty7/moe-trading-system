# 💰 Financial Metrics for Evaluation

This system is evaluated using **realistic financial performance metrics** to simulate and analyze the profitability and risk of its daily trading decisions. These metrics offer a well-rounded view of both return potential and exposure to losses, which is essential in assessing trading strategies in volatile markets.

All metrics are computed using the system’s generated daily decisions for each ticker, based on historical price data.

---

## 📈 Profitability Metrics

### ✅ Total Return (TR)
- **Definition**: Measures the overall percentage gain or loss of the portfolio over the entire backtest period.
- **Formula**:
  TR = (Final Portfolio Value - Initial Portfolio Value) / Initial Portfolio Value
- **Benefit**: Provides a simple snapshot of total performance without regard to time or risk.
- **Use Case**: Compare different strategies or assets in raw profitability terms.

---

### ✅ Annualized Return (AR)
- **Definition**: Normalizes the total return to a yearly rate, accounting for the length of the evaluation period.
- **Formula**:
  AR = (1 + TR)^(1 / Years) - 1
- **Benefit**: Allows fair comparison between strategies run over different time spans.
- **Use Case**: Compare with traditional investment benchmarks (e.g., S&P 500, bonds).

---

## 📊 Risk-Adjusted Return Metrics

### 📌 Sharpe Ratio (SR)
- **Definition**: Measures return per unit of overall volatility, including both upside and downside.
- **Formula**:
  Sharpe Ratio = (Mean Daily Return - Risk-Free Rate) / StdDev(Daily Returns)
- **Benefit**: Adjusts for risk and rewards consistency. A higher value indicates better risk-adjusted performance.
- **Use Case**: Compare trading systems that have similar returns but different volatilities.

---

### 📌 Sortino Ratio (SoR)
- **Definition**: A variation of the Sharpe Ratio that only considers downside volatility (i.e., harmful risk).
- **Formula**:
  Sortino Ratio = (Mean Daily Return - Risk-Free Rate) / StdDev(Negative Daily Returns)
- **Benefit**: More appropriate in finance where investors care more about losses than volatility overall.
- **Use Case**: Evaluate aggressive strategies that may have high volatility but limited downside.

---

### 📌 Calmar Ratio (CR)
- **Definition**: Evaluates return per unit of maximum drawdown.
- **Formula**:
  Calmar Ratio = Annualized Return / Maximum Drawdown
- **Benefit**: Focuses on downside risk by incorporating the worst observed loss.
- **Use Case**: Evaluate strategies on their ability to avoid catastrophic losses while generating return.

---

## ⚠️ Risk Metrics

### 📉 Annualized Volatility (AV)
- **Definition**: Measures the standard deviation of returns, scaled to a yearly basis.
- **Formula**:
  AV = StdDev(Daily Returns) * sqrt(252)
- **Benefit**: Quantifies how “bumpy” the ride is. Helps detect unstable or overly risky systems.
- **Use Case**: Risk profiling, volatility targeting, or filtering noisy strategies.

---

### 📉 Maximum Drawdown (MDD)
- **Definition**: The largest observed percentage loss from a peak to a trough during the test period.
- **Formula**:
  MDD = (Peak Portfolio Value - Trough Value) / Peak Portfolio Value
- **Benefit**: Directly measures the worst-case scenario. Critical for real-world investors and risk control.
- **Use Case**: Stress testing, comparing downside tolerance across strategies.

---

### 📉 Drawdown Duration (DD)
- **Definition**: The longest period (in days) the portfolio remained below its previous peak.
- **Benefit**: Captures how long the strategy stays "underwater," which affects investor confidence.
- **Use Case**: Psychological evaluation — useful for understanding recovery periods after losses.

---

## 🧪 Evaluation Notes

- All metrics will be computed **per company** and **aggregated globally** across tickers.
- Risk-free rate is assumed to be 0 initially for simplicity.
- Each daily decision (Buy/Hold/Sell) affects a simulated position, which affects the portfolio value.
- Backtesting uses **daily closing prices**, with assumptions on transaction logic defined in the simulator.

---

## 🛠️ Implementation Tip

Implement all metric calculations inside: backend/evaluation/metrics.py

Daily trade logs, cash/position changes, and value snapshots should be stored during the backtest process to allow:
- Post-hoc analysis
- Plotting
- Weekly or monthly summaries

