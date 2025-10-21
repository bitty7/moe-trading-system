#!/usr/bin/env python3
"""
View Backtest Results - Formatted for Research Comparison

Usage:
    python view_results.py <backtest_folder_name>
    
Example:
    python view_results.py backtest_llm_full_historical_2000_2025
"""

import json
import sys
import os
from pathlib import Path


def format_percentage(value, decimals=2):
    """Convert decimal to percentage string"""
    return f"{value * 100:.{decimals}f}%"


def format_number(value, decimals=2):
    """Format number with specified decimals"""
    if isinstance(value, (int, float)):
        if value == float('inf'):
            return "∞"
        return f"{value:.{decimals}f}"
    return str(value)


def view_results(backtest_folder):
    """Display backtest results in a research-friendly format"""
    
    # Construct path to results
    logs_dir = Path(__file__).parent / "logs"
    results_path = logs_dir / backtest_folder / "results.json"
    config_path = logs_dir / backtest_folder / "config.json"
    
    if not results_path.exists():
        print(f"❌ Error: Results file not found at {results_path}")
        print(f"\nAvailable backtests:")
        if logs_dir.exists():
            for folder in sorted(logs_dir.iterdir()):
                if folder.is_dir():
                    print(f"  - {folder.name}")
        return
    
    # Load results
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    # Load config
    config = {}
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    portfolio = results.get('portfolio_metrics', {})
    tickers = results.get('ticker_summary', {})
    runtime = results.get('runtime_metrics', {})
    
    # Print header
    print("=" * 80)
    print(f"📊 BACKTEST RESULTS: {backtest_folder}")
    print("=" * 80)
    print()
    
    # Configuration info
    if config:
        print("📋 Configuration:")
        print(f"  Date Range: {config.get('start_date', 'N/A')} to {config.get('end_date', 'N/A')}")
        print(f"  Tickers: {', '.join(config.get('tickers', []))}")
        print(f"  Initial Capital: ${config.get('initial_capital', 0):,.2f}")
        if 'experiment' in config:
            exp = config['experiment']
            print(f"  Aggregation Strategy: {exp.get('aggregation', {}).get('strategy', 'N/A')}")
        print()
    
    # Portfolio Performance (formatted for research)
    print("📈 Portfolio Performance:")
    print("-" * 80)
    print(f"  Total Return:              {format_percentage(portfolio.get('total_return', 0))}")
    print(f"  Annualized Return:         {format_percentage(portfolio.get('annualized_return', 0))}")
    print(f"  Volatility (Annual):       {format_percentage(portfolio.get('volatility', 0))}")
    print(f"  Max Drawdown:              {format_percentage(portfolio.get('max_drawdown', 0))}")
    print()
    print(f"  Sharpe Ratio:              {format_number(portfolio.get('sharpe_ratio', 0), 3)}")
    print(f"  Sortino Ratio:             {format_number(portfolio.get('sortino_ratio', 0), 3)}")
    print(f"  Calmar Ratio:              {format_number(portfolio.get('calmar_ratio', 0), 3)}")
    print()
    print(f"  Win Rate:                  {format_percentage(portfolio.get('win_rate', 0))}")
    print(f"  Profit Factor:             {format_number(portfolio.get('profit_factor', 0), 3)}")
    print(f"  Total Trades:              {portfolio.get('total_trades', 0)}")
    print(f"  Avg Trade Return:          {format_percentage(portfolio.get('avg_trade_return', 0), 4)}")
    print(f"  Best Trade:                {format_percentage(portfolio.get('best_trade', 0))}")
    print(f"  Worst Trade:               {format_percentage(portfolio.get('worst_trade', 0))}")
    print(f"  Avg Hold Time (days):      {format_number(portfolio.get('avg_hold_time', 0), 0)}")
    print(f"  Cash Drag:                 {format_percentage(portfolio.get('cash_drag', 0))}")
    print(f"  Diversification Score:     {format_number(portfolio.get('diversification_score', 0), 3)}")
    print()
    
    # Individual Ticker Performance
    if tickers:
        print("📊 Individual Ticker Performance:")
        print("-" * 80)
        for ticker, metrics in sorted(tickers.items()):
            print(f"\n  {ticker.upper()}:")
            print(f"    Total Return:          {format_percentage(metrics.get('total_return', 0))}")
            print(f"    Annualized Return:     {format_percentage(metrics.get('annualized_return', 0))}")
            print(f"    Volatility:            {format_percentage(metrics.get('volatility', 0))}")
            print(f"    Max Drawdown:          {format_percentage(metrics.get('max_drawdown', 0))}")
            print(f"    Sharpe Ratio:          {format_number(metrics.get('sharpe_ratio', 0), 3)}")
            print(f"    Win Rate:              {format_percentage(metrics.get('win_rate', 0))}")
            print(f"    Profit Factor:         {format_number(metrics.get('profit_factor', 0), 3)}")
            print(f"    Contribution:          {format_percentage(metrics.get('contribution_to_portfolio', 0))}")
            print(f"    Num Trades:            {metrics.get('num_trades', 0)}")
        print()
    
    # Runtime Metrics
    if runtime:
        print("⏱️  Runtime Metrics:")
        print("-" * 80)
        print(f"  Total Runtime:             {format_number(runtime.get('total_runtime_hours', 0), 2)} hours")
        print(f"                             ({format_number(runtime.get('total_runtime_minutes', 0), 1)} minutes)")
        print(f"                             ({format_number(runtime.get('total_runtime_seconds', 0), 0)} seconds)")
        print()
    
    # Summary for Research Papers
    print("=" * 80)
    print("📝 Summary for Research Comparison:")
    print("=" * 80)
    print(f"Annualized Return:  {format_percentage(portfolio.get('annualized_return', 0))}")
    print(f"Volatility:         {format_percentage(portfolio.get('volatility', 0))}")
    print(f"Sharpe Ratio:       {format_number(portfolio.get('sharpe_ratio', 0), 3)}")
    print(f"Max Drawdown:       {format_percentage(portfolio.get('max_drawdown', 0))}")
    print(f"Win Rate:           {format_percentage(portfolio.get('win_rate', 0))}")
    print(f"Total Trades:       {portfolio.get('total_trades', 0)}")
    print("=" * 80)
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python view_results.py <backtest_folder_name>")
        print("\nExample:")
        print("  python view_results.py backtest_llm_full_historical_2000_2025")
        print("\nAvailable backtests:")
        
        logs_dir = Path(__file__).parent / "logs"
        if logs_dir.exists():
            for folder in sorted(logs_dir.iterdir()):
                if folder.is_dir():
                    print(f"  - {folder.name}")
        sys.exit(1)
    
    backtest_folder = sys.argv[1]
    view_results(backtest_folder)


if __name__ == "__main__":
    main()


