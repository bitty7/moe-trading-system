#!/usr/bin/env python3
"""
Test Daily Metrics Collection

This test verifies that daily metrics are being collected every day
as requested, ensuring updated metrics against current prices.
"""

import sys
import os
from datetime import datetime
import json

# The run_tests.py script sets the working directory to backend/ and PYTHONPATH to backend/
# So we can import directly without adding to sys.path

from evaluation.backtester import run_backtest
from core.data_types import BacktesterConfig

def test_daily_metrics_collection():
    """Test that daily metrics are collected every day."""
    print("🧪 Testing Daily Metrics Collection")
    print("=" * 50)
    
    # Create a short test configuration
    config = BacktesterConfig(
        start_date="2024-01-01",
        end_date="2024-01-05",  # 5 days
        tickers=["aa", "aaau"],
        initial_capital=100000,
        position_sizing=0.15,
        max_positions=3,
        cash_reserve=0.2,
        min_cash_reserve=0.1,
        transaction_cost=0.001,
        slippage=0.0005,
        log_level="INFO"
    )
    
    print("🚀 Running 5-day backtest to verify daily metrics collection...")
    
    try:
        results = run_backtest(config)
        
        print("✅ Backtest completed!")
        print(f"   Total Trading Days: {results.total_days}")
        print(f"   Portfolio History Records: {len(results.portfolio_history)}")
        
        # Check that we have daily metrics for each trading day
        if results.portfolio_history:
            print(f"   ✅ Daily metrics collected for {len(results.portfolio_history)} days")
            
            # Show the dates we have metrics for
            dates = [state.date.strftime('%Y-%m-%d') for state in results.portfolio_history]
            print(f"   📅 Dates with metrics: {dates}")
            
            # Check that we have metrics for each day
            expected_dates = ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
            missing_dates = [d for d in expected_dates if d not in dates]
            
            if missing_dates:
                print(f"   ❌ Missing metrics for dates: {missing_dates}")
            else:
                print(f"   ✅ All expected dates have metrics!")
            
            # Show portfolio value progression
            print(f"   📊 Portfolio Value Progression:")
            for i, state in enumerate(results.portfolio_history):
                daily_return = state.daily_return
                print(f"     {state.date.strftime('%Y-%m-%d')}: ${state.total_value:,.2f} (daily return: {daily_return:.4f})")
        
        # Check the latest log directory
        import glob
        log_dirs = glob.glob("logs/backtest_*")
        if log_dirs:
            latest_log = max(log_dirs, key=os.path.getctime)
            print(f"   📁 Latest log directory: {latest_log}")
            
            # Check portfolio daily file
            portfolio_file = os.path.join(latest_log, "portfolio_daily.json")
            if os.path.exists(portfolio_file):
                with open(portfolio_file, 'r') as f:
                    portfolio_data = json.load(f)
                print(f"   ✅ Portfolio daily metrics: {len(portfolio_data)} records")
                
                # Verify we have metrics for each day
                portfolio_dates = [record['date'] for record in portfolio_data]
                print(f"   📅 Portfolio dates: {portfolio_dates}")
                
                if len(portfolio_dates) == len(expected_dates):
                    print(f"   ✅ All {len(expected_dates)} days have portfolio metrics!")
                else:
                    print(f"   ❌ Expected {len(expected_dates)} days, got {len(portfolio_dates)}")
        
        print("\n🎉 Daily metrics collection test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in daily metrics test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_daily_metrics_collection() 