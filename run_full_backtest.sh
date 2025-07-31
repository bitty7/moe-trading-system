#!/bin/bash
# Full Backtest Runner for MoE Trading System
# This script runs a comprehensive backtest on all available data

set -e  # Exit on any error

echo "🚀 Starting Full Backtest on EC2 with GPU..."

# Set environment variables for GPU acceleration
export OLLAMA_HOST=0.0.0.0:11434
export CUDA_VISIBLE_DEVICES=0

# Verify GPU is available
echo "🔍 Verifying GPU availability..."
nvidia-smi
ollama list

# Run the full backtest
echo "🎯 Running full backtest..."
cd backend
python3 ../run_backtest.py

# Create results summary
echo "📋 Creating results summary..."
cat > results_summary.txt << 'EOF'
# Full Backtest Results Summary
# Generated on EC2 with GPU acceleration

## Backtest Configuration
- Start Date: 2000-01-01
- End Date: 2025-01-01
- Tickers: aa, aaau, aacg
- Initial Capital: $1,000,000

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
- Model: llama3.2:latest
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