#!/usr/bin/env python3
"""
Test script for high-performance backtesting.
Demonstrates the optimized backtesting engine for EC2 instances.
"""

import sys
import os
from datetime import datetime
import time

# The run_tests.py script sets the working directory to backend/ and PYTHONPATH to backend/
# So we can import directly without adding to sys.path

from evaluation.backtester import run_high_performance_backtest
from core.data_types import BacktesterConfig

def test_high_performance_backtest():
    """Test the high-performance backtesting engine."""
    print("🚀 High-Performance Backtesting Test")
    print("=" * 50)
    
    # Create configuration for full dataset
    config = BacktesterConfig(
        start_date="2000-01-01",  # Full dataset
        end_date="2025-03-28",    # Full dataset
        tickers=["aa", "aaau", "aacg"],
        initial_capital=100000,
        position_sizing=0.15,
        max_positions=3,
        cash_reserve=0.2,
        min_cash_reserve=0.1,
        transaction_cost=0.001,
        slippage=0.0005,
        log_level="WARNING"  # Minimal logging for performance
    )
    
    print(f"📊 Configuration:")
    print(f"   Period: {config.start_date} to {config.end_date}")
    print(f"   Tickers: {config.tickers}")
    print(f"   Initial Capital: ${config.initial_capital:,.2f}")
    print(f"   Log Level: {config.log_level}")
    print()
    
    print("⏱️  Starting high-performance backtest...")
    start_time = time.time()
    
    try:
        results = run_high_performance_backtest(config)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print()
        print("✅ High-Performance Backtest Completed!")
        print("=" * 50)
        print(f"⏱️  Total Time: {total_time:.2f} seconds ({total_time/3600:.2f} hours)")
        print(f"📊 Trading Days: {results.total_days}")
        print(f"📈 Total Decisions: {results.data_coverage.get('total_decisions', 0)}")
        print(f"💰 Total Trades: {len(results.trade_log)}")
        
        # Performance metrics
        if results.total_days > 0:
            days_per_second = results.total_days / total_time
            print(f"⚡ Processing Rate: {days_per_second:.2f} days/second")
            print(f"⚡ Processing Rate: {days_per_second * 3600:.0f} days/hour")
        
        # Portfolio performance
        if results.portfolio_metrics:
            portfolio = results.portfolio_metrics
            print(f"📈 Portfolio Performance:")
            print(f"   Total Return: {portfolio.total_return:.2%}")
            print(f"   Annualized Return: {portfolio.annualized_return:.2%}")
            print(f"   Sharpe Ratio: {portfolio.sharpe_ratio:.3f}")
            print(f"   Max Drawdown: {portfolio.max_drawdown:.2%}")
            print(f"   Win Rate: {portfolio.win_rate:.1%}")
        
        # Ticker performance
        print(f"📊 Ticker Performance:")
        for ticker, metrics in results.ticker_metrics.items():
            print(f"   {ticker}: {metrics.total_return:.2%} return, {metrics.num_trades} trades")
        
        # Success rate
        success_rate = results.success_rate
        print(f"🎯 Success Rate: {success_rate:.1%}")
        
        print()
        print("📁 Performance logging files saved to logs/ directory")
        print("🎉 High-performance backtest completed successfully!")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in high-performance backtest: {e}")
        import traceback
        traceback.print_exc()
        return None

def estimate_full_dataset_performance():
    """Estimate performance for the full 25-year dataset."""
    print("\n🔮 Performance Estimation for Full Dataset")
    print("=" * 50)
    
    # Current test results (if available)
    test_days = 100  # Example: 100 days test
    test_time = 300  # Example: 5 minutes
    
    # Full dataset size
    full_days = 19_047  # ~25 years of trading days
    full_llm_requests = 57_141  # 3 experts × 19,047 days
    
    # Estimated performance
    days_per_second = test_days / test_time
    estimated_full_time = full_days / days_per_second
    estimated_hours = estimated_full_time / 3600
    
    print(f"📊 Dataset Size:")
    print(f"   Trading Days: {full_days:,}")
    print(f"   LLM Requests: {full_llm_requests:,}")
    print(f"   Tickers: 3")
    print()
    
    print(f"⚡ Performance Estimates:")
    print(f"   Processing Rate: {days_per_second:.2f} days/second")
    print(f"   Estimated Time: {estimated_hours:.1f} hours")
    print(f"   Estimated Cost (EC2 g4dn.12xlarge): ${estimated_hours * 3.912:.0f}")
    print()
    
    print(f"🚀 EC2 Instance Recommendations:")
    print(f"   g4dn.12xlarge: ~{estimated_hours:.1f} hours (${estimated_hours * 3.912:.0f})")
    print(f"   p3.8xlarge: ~{estimated_hours * 0.7:.1f} hours (${estimated_hours * 0.7 * 12.24:.0f})")
    print(f"   g5.12xlarge: ~{estimated_hours:.1f} hours (${estimated_hours * 4.096:.0f})")

if __name__ == "__main__":
    # Run performance estimation
    estimate_full_dataset_performance()
    
    print("\n" + "=" * 50)
    
    # Ask user if they want to run the actual test
    response = input("Do you want to run the high-performance backtest? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        test_high_performance_backtest()
    else:
        print("Test skipped. Use this script on an EC2 instance for full dataset testing.") 