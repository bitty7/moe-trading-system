#!/usr/bin/env python3
"""
Short Backtest Runner for Testing
Runs a 10-day backtest to verify logging and functionality
"""

import sys
import os

# Add current directory to path (we're already in backend/)
sys.path.append('.')

from core.data_types import BacktesterConfig
from evaluation.backtester import run_backtest

def create_short_backtest_config():
    """Create configuration for short backtest."""
    return BacktesterConfig(
        start_date="2020-01-01",  # Start from historical date with data
        end_date="2020-01-15",    # 15 days of data
        tickers=["aa", "aaau", "aacg"],  # All available tickers
        initial_capital=100000,  # Smaller capital for testing
        position_sizing=0.15,
        max_positions=5,
        cash_reserve=0.2,
        min_cash_reserve=0.1,
        transaction_cost=0.001,
        slippage=0.0005,
        log_level="INFO"  # More verbose for debugging
    )

def main():
    """Run the short backtest."""
    print("🧪 Starting short backtest for testing...")
    
    # Create configuration
    config = create_short_backtest_config()
    print(f"✅ Configuration created:")
    print(f"   Period: {config.start_date} to {config.end_date}")
    print(f"   Tickers: {config.tickers}")
    print(f"   Initial Capital: ${config.initial_capital:,.2f}")
    print(f"   Log Level: {config.log_level}")
    
    # Run backtest
    results = run_backtest(config)
    
    # Print results
    print("✅ Short backtest completed!")
    
    if results is None:
        print("❌ Backtest failed - no results returned")
        print("   This usually means no data was loaded successfully")
        return
    
    print("📊 Results Summary:")
    print(f"   Total Days: {results.total_days}")
    print(f"   Total Decisions: {results.data_coverage.get('total_decisions', 0)}")
    print(f"   Total Trades: {len(results.trade_log)}")
    print(f"   Final Portfolio Value: ${results.portfolio_history[-1].total_value:,.2f}")
    print(f"   Total Return: {results.portfolio_metrics.total_return:.2%}")
    print(f"   Annualized Return: {results.portfolio_metrics.annualized_return:.2%}")
    print(f"   Sharpe Ratio: {results.portfolio_metrics.sharpe_ratio:.3f}")
    print(f"   Max Drawdown: {results.portfolio_metrics.max_drawdown:.2%}")
    
    # Check log files
    print("\n📁 Checking log files...")
    log_dir = f"logs/backtest_*"
    import glob
    log_dirs = glob.glob(log_dir)
    if log_dirs:
        latest_log = max(log_dirs, key=os.path.getctime)
        print(f"   Latest log directory: {latest_log}")
        
        # Check what files were created
        log_files = os.listdir(latest_log)
        print(f"   Files created: {log_files}")
        
        # Check file sizes
        for file in log_files:
            file_path = os.path.join(latest_log, file)
            size = os.path.getsize(file_path)
            print(f"   {file}: {size:,} bytes")
    else:
        print("   No log directories found")

if __name__ == "__main__":
    main() 