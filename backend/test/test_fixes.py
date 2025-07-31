#!/usr/bin/env python3
"""
Quick test to verify the fixes for ExpertConfidence and folder structure.
"""

import sys
import os
# The run_tests.py script sets the working directory to backend/ and PYTHONPATH to backend/
# So we can import directly without adding to sys.path

from evaluation.backtester import run_backtest
from core.data_types import BacktesterConfig

def test_fixes():
    """Test the fixes for ExpertConfidence and folder structure."""
    print("🧪 Testing ExpertConfidence Fix and Folder Structure")
    print("=" * 50)
    
    # Create a very short test configuration
    config = BacktesterConfig(
        start_date="2024-01-01",
        end_date="2024-01-03",  # Just 3 days
        tickers=["aa"],
        initial_capital=100000,
        position_sizing=0.15,
        max_positions=3,
        cash_reserve=0.2,
        min_cash_reserve=0.1,
        transaction_cost=0.001,
        slippage=0.0005,
        log_level="INFO"
    )
    
    print("🚀 Running 3-day backtest...")
    
    try:
        results = run_backtest(config)
        
        print("✅ Backtest completed!")
        print(f"   Total Trading Days: {results.total_days}")
        print(f"   Total Decisions: {results.data_coverage.get('total_decisions', 0)}")
        print(f"   Total Trades: {len(results.trade_log)}")
        
        # Check for performance logging files
        print(f"   📁 Performance Logging Validation:")
        import glob
        
        # Look for log directories
        log_dirs = glob.glob("logs/backtest_*")
        if log_dirs:
            print(f"     Found {len(log_dirs)} log directory(ies)")
            latest_log_dir = max(log_dirs, key=os.path.getctime)
            print(f"     Latest log directory: {latest_log_dir}")
            
            # Check for required files
            required_files = ["config.json", "portfolio_daily.json", "tickers_daily.json", "trades.json", "results.json"]
            
            for file in required_files:
                file_path = os.path.join(latest_log_dir, file)
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"     ✅ {file}: {file_size} bytes")
                else:
                    print(f"     ❌ {file}: MISSING")
                    
            # Show sample of logged data
            try:
                import json
                config_file = os.path.join(latest_log_dir, "config.json")
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    print(f"     📋 Backtest ID: {config_data.get('backtest_id', 'N/A')}")
                    print(f"     📅 Period: {config_data.get('start_date', 'N/A')} to {config_data.get('end_date', 'N/A')}")
                    print(f"     📊 Status: {config_data.get('status', 'N/A')}")
                    
                # Check if we have actual data in portfolio_daily.json
                portfolio_file = os.path.join(latest_log_dir, "portfolio_daily.json")
                if os.path.exists(portfolio_file):
                    with open(portfolio_file, 'r') as f:
                        portfolio_data = json.load(f)
                    print(f"     📊 Portfolio records: {len(portfolio_data)}")
                    if portfolio_data:
                        first_record = portfolio_data[0]
                        print(f"     📊 First record total_value: ${first_record.get('total_value', 0):,.2f}")
                        print(f"     📊 First record daily_return: {first_record.get('daily_return', 0):.4f}")
                        
            except Exception as e:
                print(f"     ⚠️  Could not read files: {e}")
        else:
            print(f"     ❌ No log directories found")
            
    except Exception as e:
        print(f"   ❌ Error in backtest: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixes() 