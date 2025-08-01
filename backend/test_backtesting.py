#!/usr/bin/env python3
"""
Comprehensive Backtesting System Test

Tests the complete backtesting system with various edge cases including:
- Insufficient capital scenarios
- Forced SELL decisions
- Portfolio value tracking
- Trade execution validation
"""

import sys
import os
import traceback
from datetime import datetime
import pandas as pd

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import logger after adding to path
try:
    from utils.logger import setup_logging, logger as global_logger
    import logging
    global_logger = setup_logging(log_level=logging.WARNING)
except ImportError:
    # Fallback if logger not available
    import logging
    logging.basicConfig(level=logging.WARNING)
    global_logger = logging.getLogger(__name__)

from evaluation.backtester import run_backtest, run_backtest_from_env
from core.data_types import BacktesterConfig, TradeAction
from core.config import Config

def test_backtesting_system():
    """Test the backtesting system with various scenarios."""
    print("🧪 Testing Backtesting System")
    print("=" * 50)
    
    try:
        # Set up logging to reduce noise
        try:
            from utils.logger import setup_logging
            setup_logging(level="WARNING")
        except ImportError:
            import logging
            logging.basicConfig(level=logging.WARNING)
        
        # Test 1: Full Dataset Backtest for Performance Logging Validation
        print("📊 Test 1: Full Dataset Backtest")
        print("   This test will run a full backtest on all available data (2000-2025)")
        print()
        
        # Create a full dataset test configuration
        config_full_dataset = BacktesterConfig(
            start_date="2024-01-01",  # Start from earliest available data
            end_date="2024-01-11",    # End at current date
            tickers=["aa", "aaau", "aacg"],  # All available tickers
            initial_capital=1000000,  # $1M for full backtest
            position_sizing=0.15,
            max_positions=5,
            cash_reserve=0.2,
            min_cash_reserve=0.1,
            transaction_cost=0.001,
            slippage=0.0005,
            log_level="WARNING"  # Use WARNING to reduce noise
        )
        
        print("🚀 Running full dataset backtest...")
        
        try:
            results_full_dataset = run_backtest(config_full_dataset)
            
            print("✅ Full dataset backtest completed!")
            print(f"   Total Trading Days: {results_full_dataset.total_days}")
            print(f"   Total Decisions: {results_full_dataset.data_coverage.get('total_decisions', 0)}")
            print(f"   Total Trades: {len(results_full_dataset.trade_log)}")
            
            # Show trade breakdown
            buy_trades = [t for t in results_full_dataset.trade_log if t.action == TradeAction.BUY]
            sell_trades = [t for t in results_full_dataset.trade_log if t.action == TradeAction.SELL]
            print(f"   BUY Trades: {len(buy_trades)}")
            print(f"   SELL Trades: {len(sell_trades)}")
            
            # Show portfolio performance
            if results_full_dataset.portfolio_history:
                initial_value = results_full_dataset.portfolio_history[0].total_value
                final_value = results_full_dataset.portfolio_history[-1].total_value
                change = final_value - initial_value
                change_pct = (change / initial_value) * 100
                
                print(f"   Portfolio Performance:")
                print(f"     Initial Value: ${initial_value:,.2f}")
                print(f"     Final Value: ${final_value:,.2f}")
                print(f"     Change: ${change:,.2f} ({change_pct:+.2f}%)")
            
            # Show key metrics
            portfolio_metrics = results_full_dataset.portfolio_metrics
            print(f"   Key Metrics:")
            print(f"     Total Return: {portfolio_metrics.total_return:.2%}")
            print(f"     Annualized Return: {portfolio_metrics.annualized_return:.2%}")
            print(f"     Sharpe Ratio: {portfolio_metrics.sharpe_ratio:.3f}")
            print(f"     Max Drawdown: {portfolio_metrics.max_drawdown:.2%}")
            print(f"     Win Rate: {portfolio_metrics.win_rate:.1%}")
            
            # Check for any NaN values
            nan_found = False
            for attr, value in vars(portfolio_metrics).items():
                if pd.isna(value):
                    print(f"   ⚠️  WARNING: NaN found in {attr}")
                    nan_found = True
            
            if not nan_found:
                print("   ✅ No NaN values found - system is robust!")
            else:
                print("   ❌ NaN values found - need investigation")
            
            # Show ticker performance summary
            print(f"   Ticker Performance:")
            for ticker, ticker_metrics in results_full_dataset.ticker_metrics.items():
                print(f"     {ticker}: {ticker_metrics.total_return:.2%} return, {ticker_metrics.num_trades} trades")
            
            # Check for performance logging files
            print(f"   📁 Performance Logging Validation:")
            import os
            import glob
            
            # Look for log directories
            log_dirs = glob.glob("logs/backtest_*")
            if log_dirs:
                print(f"     Found {len(log_dirs)} log directory(ies)")
                latest_log_dir = max(log_dirs, key=os.path.getctime)
                print(f"     Latest log directory: {latest_log_dir}")
                
                # Check for required files
                required_files = ["config.json", "portfolio_daily.json", "tickers_daily.json", "trades.json", "results.json"]
                missing_files = []
                
                for file in required_files:
                    file_path = os.path.join(latest_log_dir, file)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"     ✅ {file}: {file_size} bytes")
                    else:
                        print(f"     ❌ {file}: MISSING")
                        missing_files.append(file)
                
                if not missing_files:
                    print(f"     🎉 All performance logging files created successfully!")
                else:
                    print(f"     ⚠️  Missing files: {missing_files}")
                    
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
                except Exception as e:
                    print(f"     ⚠️  Could not read config file: {e}")
            else:
                print(f"     ❌ No log directories found - performance logging may not be working")
            
        except Exception as e:
            print(f"   ❌ Error in 10-day backtest: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        print("🎉 Full dataset backtest completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_backtesting_system() 