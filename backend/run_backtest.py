#!/usr/bin/env python3
"""
Clean entry point for running backtests with JSON config.

Usage:
    python run_backtest.py --config config_llm.json
    python run_backtest.py --config config_pretrained.json
"""

import argparse
import sys
import os
import logging
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config_loader import load_config
from evaluation.backtester import HighPerformanceBacktester

# Set up minimal logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for backtesting."""
    parser = argparse.ArgumentParser(
        description="Run backtest with JSON configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_backtest.py --config config_llm.json
  python run_backtest.py --config config_pretrained.json
  python run_backtest.py --config my_custom_config.json
        """
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to config JSON file (e.g., config_llm.json)"
    )
    
    args = parser.parse_args()
    
    try:
        print("\n" + "="*70)
        print("🚀 MoE Trading System - Backtest Runner")
        print("="*70)
        
        # Load configuration
        print(f"\n📄 Loading configuration from: {args.config}")
        config = load_config(args.config)
        
        print(f"✓ Configuration loaded successfully")
        print(f"  Run ID: {config.run_id}")
        print(f"  Date range: {config.start_date} to {config.end_date}")
        print(f"  Tickers: {', '.join(config.tickers)}")
        print(f"  Strategy: {config.aggregation.get('strategy', 'entropy')}")
        
        # Display expert configuration
        if config.experts:
            print(f"\n🧠 Expert Configuration:")
            for expert_name, expert_config in config.experts.items():
                impl = expert_config.get('impl', 'unknown')
                model = expert_config.get('model', 'unknown')
                print(f"  - {expert_name}: {impl} ({model})")
        
        # Create and run backtester
        print(f"\n⚙️  Initializing backtester...")
        backtester = HighPerformanceBacktester(config)
        
        print(f"✓ Backtester initialized")
        print(f"  Output directory: logs/{config.run_id}/")
        
        # Run backtest
        print(f"\n🏃 Running backtest...")
        print(f"  This may take a while depending on date range and number of tickers...")
        print(f"  Progress will be shown below:\n")
        
        start_time = datetime.now()
        results = backtester.run_backtest()
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        # Display results summary
        print("\n" + "="*70)
        print("✅ BACKTEST COMPLETED SUCCESSFULLY")
        print("="*70)
        
        print(f"\n📊 Results Summary:")
        print(f"  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"  Output directory: logs/{config.run_id}/")
        
        # Show key files
        print(f"\n📁 Generated Files:")
        print(f"  - config.json         (Configuration and experiment metadata)")
        print(f"  - results.json        (Final metrics and performance summary)")
        print(f"  - portfolio_daily.json (Daily portfolio state)")
        print(f"  - tickers_daily.json   (Daily ticker decisions and weights)")
        print(f"  - trades.json         (All executed trades)")
        
        # Show key metrics if available
        if results and hasattr(results, 'portfolio_metrics'):
            metrics = results.portfolio_metrics
            print(f"\n💰 Key Metrics:")
            print(f"  Total Return: {metrics.total_return*100:.2f}%")
            print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.3f}")
            print(f"  Max Drawdown: {metrics.max_drawdown*100:.2f}%")
            print(f"  Total Trades: {metrics.total_trades}")
        
        print(f"\n🎉 Backtest complete! Check logs/{config.run_id}/ for detailed results.")
        print("="*70 + "\n")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: Configuration file not found")
        print(f"   {e}")
        print(f"\n💡 Tip: Make sure the config file path is correct")
        print(f"   Available configs: config_llm.json, config_pretrained.json")
        return 1
        
    except ValueError as e:
        print(f"\n❌ Error: Invalid configuration")
        print(f"   {e}")
        print(f"\n💡 Tip: Check that all required fields are present in the config")
        return 1
        
    except Exception as e:
        print(f"\n❌ Error: Backtest failed")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

