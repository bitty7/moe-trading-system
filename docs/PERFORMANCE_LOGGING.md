# Performance Logging System Documentation

## Overview

This document outlines the comprehensive performance logging system for the MoE trading backtesting engine. The system captures all performance data, decisions, and metrics for a single backtest run to enable frontend visualization without requiring re-execution of the backtest.

## Objectives

1. **Permanent Data Storage**: Save all backtest results permanently to avoid re-running expensive computations
2. **Single Run Focus**: Capture complete data for one backtest run at a time
3. **Frontend Ready**: JSON format for easy frontend integration
4. **Drill-Down Capability**: Enable portfolio-level and individual company analysis
5. **Expert Explainability**: Track expert contributions and confidence levels
6. **Complete Decision History**: Log all decisions, trades, and performance metrics

## Data Structure

### 1. Backtest Configuration & Metadata (`config.json`)

```json
{
  "backtest_id": "backtest_2024_01_15_aa_aaau",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "position_sizing": 0.15,
  "max_positions": 3,
  "cash_reserve": 0.2,
  "min_cash_reserve": 0.1,
  "transaction_cost": 0.001,
  "slippage": 0.0005,
  "tickers": ["aa", "aaau"],
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T11:45:00Z",
  "total_trading_days": 262,
  "status": "completed"
}
```

### 2. Daily Portfolio Performance (`portfolio_daily.json`)

Time series array of daily portfolio states:

```json
[
  {
    "date": "2024-01-01",
    "total_value": 100000.00,
    "cash": 100000.00,
    "positions_value": 0.00,
    "daily_return": 0.0,
    "cumulative_return": 0.0,
    "num_positions": 0,
    "cash_reserve": 20000.00,
    "available_capital": 80000.00
  },
  {
    "date": "2024-01-02",
    "total_value": 100250.00,
    "cash": 95493.25,
    "positions_value": 4756.75,
    "daily_return": 0.0025,
    "cumulative_return": 0.0025,
    "num_positions": 1,
    "cash_reserve": 20050.00,
    "available_capital": 75443.25
  }
]
```

### 3. Daily Ticker Performance (`tickers_daily.json`)

Nested structure with ticker as key and time series array as value:

```json
{
  "aa": [
    {
      "date": "2024-01-01",
      "price": 45.00,
      "decision": "HOLD",
      "overall_confidence": 0.45,
      "expert_contributions": {
        "sentiment": {
          "weight": 0.25,
          "confidence": 0.40,
          "probabilities": [0.3, 0.5, 0.2],
          "reasoning": "Limited news data available"
        },
        "technical": {
          "weight": 0.30,
          "confidence": 0.55,
          "probabilities": [0.4, 0.4, 0.2],
          "reasoning": "Mixed technical indicators"
        },
        "fundamental": {
          "weight": 0.25,
          "confidence": 0.50,
          "probabilities": [0.35, 0.45, 0.20],
          "reasoning": "Stable financial ratios"
        },
        "chart": {
          "weight": 0.20,
          "confidence": 0.35,
          "probabilities": [0.25, 0.55, 0.20],
          "reasoning": "Neutral chart patterns"
        }
      },
      "final_probabilities": [0.33, 0.34, 0.33],
      "reasoning": "Mixed signals from experts, maintaining current position",
      "position": null
    },
    {
      "date": "2024-01-02",
      "price": 45.20,
      "decision": "BUY",
      "overall_confidence": 0.75,
      "expert_contributions": {
        "sentiment": {
          "weight": 0.25,
          "confidence": 0.70,
          "probabilities": [0.6, 0.3, 0.1],
          "reasoning": "Positive news sentiment"
        },
        "technical": {
          "weight": 0.30,
          "confidence": 0.80,
          "probabilities": [0.7, 0.2, 0.1],
          "reasoning": "Strong upward momentum"
        },
        "fundamental": {
          "weight": 0.25,
          "confidence": 0.75,
          "probabilities": [0.5, 0.4, 0.1],
          "reasoning": "Improving financial metrics"
        },
        "chart": {
          "weight": 0.20,
          "confidence": 0.65,
          "probabilities": [0.4, 0.5, 0.1],
          "reasoning": "Bullish chart patterns"
        }
      },
      "final_probabilities": [0.55, 0.35, 0.10],
      "reasoning": "Strong consensus among experts for buy decision",
      "position": {
        "quantity": 100,
        "avg_price": 45.00,
        "current_value": 4520.00,
        "unrealized_pnl": 20.00,
        "status": "OPEN"
      }
    }
  ],
  "aaau": [
    // Similar structure for each ticker
  ]
}
```

### 4. Trade History (`trades.json`)

Array of all executed trades:

```json
[
  {
    "trade_id": "trade_001",
    "date": "2024-01-02",
    "ticker": "aa",
    "action": "BUY",
    "quantity": 100,
    "price": 45.00,
    "value": 4500.00,
    "transaction_cost": 4.50,
    "slippage": 2.25,
    "total_cost": 4506.75,
    "overall_confidence": 0.75,
    "expert_contributions": {
      "sentiment": {"weight": 0.25, "confidence": 0.70},
      "technical": {"weight": 0.30, "confidence": 0.80},
      "fundamental": {"weight": 0.25, "confidence": 0.75},
      "chart": {"weight": 0.20, "confidence": 0.65}
    },
    "reasoning": "Strong consensus among experts for buy decision",
    "success": true,
    "portfolio_before": {
      "total_value": 100000.00,
      "cash": 100000.00,
      "positions_value": 0.00
    },
    "portfolio_after": {
      "total_value": 100000.00,
      "cash": 95493.25,
      "positions_value": 4493.25
    }
  }
]
```

### 5. Final Results Summary (`results.json`)

```json
{
  "portfolio_metrics": {
    "total_return": 0.2554,
    "annualized_return": 0.2556,
    "sharpe_ratio": 1.940,
    "sortino_ratio": 2.150,
    "calmar_ratio": 3.408,
    "max_drawdown": 0.075,
    "drawdown_duration": 15,
    "volatility": 0.132,
    "win_rate": 0.0,
    "profit_factor": 0.0,
    "total_trades": 11,
    "avg_trade_return": 0.0,
    "best_trade": 0.0,
    "worst_trade": 0.0,
    "avg_hold_time": 0.0,
    "cash_drag": 0.078,
    "diversification_score": 0.5,
    "final_value": 125544.99
  },
  "ticker_summary": {
    "aa": {
      "total_return": 0.4788,
      "annualized_return": 0.4792,
      "sharpe_ratio": 2.1,
      "max_drawdown": 0.05,
      "volatility": 0.15,
      "num_trades": 1,
      "final_value": 4520.00,
      "contribution_to_portfolio": 0.036
    },
    "aaau": {
      "total_return": 0.2848,
      "annualized_return": 0.2852,
      "sharpe_ratio": 1.8,
      "max_drawdown": 0.08,
      "volatility": 0.18,
      "num_trades": 10,
      "final_value": 12880.00,
      "contribution_to_portfolio": 0.103
    }
  }
}
```

## File Structure

```
logs/
├── backtest_2024_01_15_aa_aaau/
│   ├── config.json
│   ├── portfolio_daily.json
│   ├── tickers_daily.json
│   ├── trades.json
│   └── results.json
└── backtest_2024_01_16_aa_aaau_aacg/
    └── ...
```

## Implementation Steps

### Phase 1: Core Logging Infrastructure

1. **Create PerformanceLogger Class**
   - Initialize with backtest_id and config
   - Create log directory structure
   - Handle file creation and writing

2. **Implement Daily Portfolio Logging**
   - Log portfolio state after each trading day
   - Calculate and store daily metrics
   - Handle portfolio value updates

3. **Implement Daily Ticker Logging**
   - Log expert decisions and contributions
   - Store confidence levels for each expert
   - Track position changes

4. **Implement Trade Logging**
   - Log all executed trades
   - Store pre/post portfolio states
   - Include expert contribution details

### Phase 2: Data Collection Integration

5. **Integrate with Backtester**
   - Hook into daily processing loop
   - Capture expert aggregation results
   - Log portfolio state updates

6. **Integrate with Portfolio Simulator**
   - Capture trade execution details
   - Log position changes
   - Track cash and value updates

7. **Integrate with Expert Aggregator**
   - Capture expert weights and confidence
   - Store individual expert probabilities
   - Log reasoning and decision process

### Phase 3: Final Results Processing

8. **Calculate Final Metrics**
   - Compute all portfolio metrics
   - Calculate ticker-specific metrics
   - Generate comprehensive summary

9. **Save Final Results**
   - Write results.json with all metrics
   - Validate data completeness
   - Handle any missing data gracefully

### Phase 4: Testing and Validation

10. **Test Data Completeness**
    - Verify all required fields are captured
    - Check for missing dates or data
    - Validate JSON structure

11. **Test Edge Cases**
    - No trades scenario
    - Failed trades
    - Missing expert data
    - Invalid prices or calculations

12. **Test Data Accuracy**
    - Verify calculations match expected results
    - Check for NaN or invalid values
    - Validate time series continuity

## Key Requirements

### Expert Confidence Tracking
- **Individual Expert Confidence**: Each expert's confidence level (0.0-1.0)
- **Overall Decision Confidence**: Weighted average of expert confidences
- **Expert Weights**: Dynamic weights assigned by gating network
- **Expert Probabilities**: Individual [buy, hold, sell] probabilities
- **Final Probabilities**: Aggregated [buy, hold, sell] probabilities

### Data Validation
- **No NaN Values**: All numeric fields must be valid numbers
- **Date Continuity**: All trading days must be present
- **Consistency**: Portfolio values must match sum of cash + positions
- **Completeness**: All required fields must be present

### Error Handling
- **Graceful Degradation**: Continue logging even if some data is missing
- **File I/O Errors**: Handle disk space and permission issues
- **Data Corruption**: Validate JSON structure and data types
- **Recovery**: Ability to resume logging after interruptions

## Testing Strategy

### Unit Tests
1. **PerformanceLogger Tests**
   - File creation and writing
   - JSON structure validation
   - Error handling scenarios

2. **Data Structure Tests**
   - Validate all required fields
   - Check data type consistency
   - Test edge cases

### Integration Tests
1. **Full Backtest Logging**
   - Run complete backtest with logging
   - Verify all files are created
   - Check data completeness

2. **Data Accuracy Tests**
   - Compare logged data with expected results
   - Verify calculations are correct
   - Test with known scenarios

### Validation Tests
1. **JSON Schema Validation**
   - Ensure all files follow defined structure
   - Check for missing or extra fields
   - Validate data types

2. **Business Logic Validation**
   - Portfolio values must be consistent
   - Trade records must match portfolio changes
   - Expert contributions must sum correctly

## Success Criteria

1. **Complete Data Capture**: All required data is logged without loss
2. **Data Accuracy**: Logged data matches actual backtest results
3. **JSON Validity**: All files are valid JSON and follow defined schema
4. **No NaN Values**: All numeric fields contain valid numbers
5. **Time Series Completeness**: All trading days are present
6. **Expert Explainability**: All expert contributions and confidence levels captured
7. **Frontend Ready**: Data structure supports easy frontend integration

## Future Considerations

1. **Data Compression**: Implement compression for long backtests
2. **Incremental Updates**: Support for real-time logging during backtest
3. **Data Versioning**: Track changes to logging format
4. **Performance Optimization**: Efficient file I/O for large datasets
5. **Backup and Recovery**: Data backup and recovery mechanisms

This documentation serves as a comprehensive reference for implementing the performance logging system. All requirements, data structures, and implementation steps are detailed to ensure successful development and testing. 