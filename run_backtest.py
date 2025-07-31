#!/usr/bin/env python3
"""
Full Backtest Runner
Runs the complete backtest on all available data
"""

import sys
import os
sys.path.append('.')

from core.data_types import BacktesterConfig
from evaluation.backtester import run_backtest

def create_full_backtest_config():
    """Create configuration for full backtest."""
    return BacktesterConfig(
        start_date="2000-01-01",  # Start from earliest available data
        end_date="2025-01-01",    # End at current date
        tickers=["aa", "aaau", "aacg"],  # All available tickers
        initial_capital=100000,
        position_sizing=0.15,
        max_positions=5,
        cash_reserve=0.2,
        min_cash_reserve=0.1,
        transaction_cost=0.001,
        slippage=0.0005,
        log_level="WARNING"  # Minimal logging for performance
    )

def main():
    """Run the full backtest."""
    print("🚀 Starting full backtest...")
    
    # Create configuration
    config = create_full_backtest_config()
    print(f"✅ Configuration created:")
    print(f"   Period: {config.start_date} to {config.end_date}")
    print(f"   Tickers: {config.tickers}")
    print(f"   Initial Capital: ${config.initial_capital:,.2f}")
    
    # Run backtest
    results = run_backtest(config)
    
    # Print results
    print("✅ Full backtest completed!")
    print("📊 Results Summary:")
    print(f"   Total Days: {results.total_days}")
    print(f"   Total Decisions: {results.data_coverage.get('total_decisions', 0)}")
    print(f"   Total Trades: {len(results.trade_log)}")
    print(f"   Final Portfolio Value: ${results.portfolio_history[-1].total_value:,.2f}")
    print(f"   Total Return: {results.portfolio_metrics.total_return:.2%}")
    print(f"   Annualized Return: {results.portfolio_metrics.annualized_return:.2%}")
    print(f"   Sharpe Ratio: {results.portfolio_metrics.sharpe_ratio:.3f}")
    print(f"   Max Drawdown: {results.portfolio_metrics.max_drawdown:.2%}")

if __name__ == "__main__":
    main() 