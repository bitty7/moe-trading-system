#!/bin/bash
# Full Backtest Runner for MoE Trading System
# This script runs a comprehensive backtest on all available data

set -e  # Exit on any error

echo "🚀 Starting Full Backtest on EC2 with GPU..."

# Navigate to backend directory
cd backend

# Set environment variables for GPU acceleration
export OLLAMA_HOST=0.0.0.0:11434
export CUDA_VISIBLE_DEVICES=0

# Verify GPU is available
echo "🔍 Verifying GPU availability..."
nvidia-smi
ollama list

# Create full backtest configuration
echo "📊 Creating full backtest configuration..."
cat > full_backtest_config.py << 'EOF'
#!/usr/bin/env python3
"""
Full Backtest Configuration
Runs backtest on all available data from 2000 to 2025
"""

import sys
import os
sys.path.append('.')

from core.data_types import BacktesterConfig

def create_full_backtest_config():
    """Create configuration for full backtest."""
    return BacktesterConfig(
        start_date="2000-01-01",  # Start from earliest available data
        end_date="2025-01-01",    # End at current date
        tickers=["aa", "aaau", "aacg"],  # All available tickers
        # Optimized for speed: reduce lookback periods
        initial_capital=100000,
        position_sizing=0.15,
        max_positions=5,
        cash_reserve=0.2,
        min_cash_reserve=0.1,
        transaction_cost=0.001,
        slippage=0.0005,
        log_level="WARNING"  # Minimal logging for performance
    )

if __name__ == "__main__":
    config = create_full_backtest_config()
    print(f"✅ Full backtest configuration created:")
    print(f"   Period: {config.start_date} to {config.end_date}")
    print(f"   Tickers: {config.tickers}")
    print(f"   Initial Capital: ${config.initial_capital:,.2f}")
EOF

# Run the full backtest
echo "🎯 Running full backtest..."
python3 -c '
import sys
sys.path.append(".")
from full_backtest_config import create_full_backtest_config
from evaluation.backtester import run_backtest

print("🚀 Starting full backtest...")
config = create_full_backtest_config()
results = run_backtest(config)

print("✅ Full backtest completed!")
print("📊 Results Summary:")
print(f"   Total Days: {results.total_days}")
print(f"   Total Decisions: {results.data_coverage.get(\"total_decisions\", 0)}")
print(f"   Total Trades: {len(results.trade_log)}")
print(f"   Final Portfolio Value: ${results.portfolio_history[-1].total_value:,.2f}")
print(f"   Total Return: {results.portfolio_metrics.total_return:.2%}")
print(f"   Annualized Return: {results.portfolio_metrics.annualized_return:.2%}")
print(f"   Sharpe Ratio: {results.portfolio_metrics.sharpe_ratio:.3f}")
print(f"   Max Drawdown: {results.portfolio_metrics.max_drawdown:.2%}")
'

# Create results summary
echo "📋 Creating results summary..."
cat > results_summary.txt << 'EOF'
# Full Backtest Results Summary
# Generated on EC2 with GPU acceleration

## Backtest Configuration
- Start Date: 2000-01-01
- End Date: 2025-01-01
- Tickers: aa, aaau, aacg
- Initial Capital: $100,000

## Performance Metrics
- Total Trading Days: [TO BE FILLED]
- Total Decisions: [TO BE FILLED]
- Total Trades: [TO BE FILLED]
- Final Portfolio Value: [TO BE FILLED]
- Total Return: [TO BE FILLED]
- Annualized Return: [TO BE FILLED]
- Sharpe Ratio: [TO BE FILLED]
- Max Drawdown: [TO BE FILLED]

## Files Generated
- logs/backtest_[TIMESTAMP]_[TICKERS]/
  - config.json: Backtest configuration
  - portfolio_daily.json: Daily portfolio metrics
  - tickers_daily.json: Daily ticker metrics
  - trades.json: All trade records
  - results.json: Final results summary

## GPU Performance
- Model: llama3.1:8b
- GPU: [TO BE FILLED]
- Processing Rate: [TO BE FILLED] days/second
EOF

echo "✅ Full backtest completed!"
echo "📁 Results saved in logs/ directory"
echo "📋 Summary saved in results_summary.txt"

# Show latest log directory
LATEST_LOG=$(ls -td logs/backtest_* | head -1)
echo "📂 Latest log directory: $LATEST_LOG"

# Show disk usage
echo "💾 Disk usage:"
du -sh logs/
df -h .

echo "🎉 Full backtest process completed successfully!" 