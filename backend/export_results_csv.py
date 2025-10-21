#!/usr/bin/env python3
"""
Export Backtest Results to CSV for Research Comparison

Usage:
    python export_results_csv.py <backtest_folder_name> [output.csv]
    
Example:
    python export_results_csv.py backtest_llm_full_historical_2000_2025
    python export_results_csv.py backtest_llm_full_historical_2000_2025 results.csv
"""

import json
import sys
import csv
from pathlib import Path


def export_to_csv(backtest_folder, output_file=None):
    """Export backtest results to CSV format"""
    
    # Construct path to results
    logs_dir = Path(__file__).parent / "logs"
    results_path = logs_dir / backtest_folder / "results.json"
    config_path = logs_dir / backtest_folder / "config.json"
    
    if not results_path.exists():
        print(f"❌ Error: Results file not found at {results_path}")
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
    runtime = results.get('runtime_metrics', {})
    
    # Prepare data for CSV (percentages for key metrics)
    csv_data = {
        'experiment_name': backtest_folder,
        'start_date': config.get('start_date', 'N/A'),
        'end_date': config.get('end_date', 'N/A'),
        'tickers': ', '.join(config.get('tickers', [])),
        'initial_capital': config.get('initial_capital', 0),
        'aggregation_strategy': config.get('experiment', {}).get('aggregation', {}).get('strategy', 'N/A'),
        
        # Key metrics as percentages
        'total_return_pct': portfolio.get('total_return', 0) * 100,
        'annualized_return_pct': portfolio.get('annualized_return', 0) * 100,
        'volatility_pct': portfolio.get('volatility', 0) * 100,
        'max_drawdown_pct': portfolio.get('max_drawdown', 0) * 100,
        
        # Ratios (as-is)
        'sharpe_ratio': portfolio.get('sharpe_ratio', 0),
        'sortino_ratio': portfolio.get('sortino_ratio', 0),
        'calmar_ratio': portfolio.get('calmar_ratio', 0),
        
        # Other metrics
        'win_rate_pct': portfolio.get('win_rate', 0) * 100,
        'profit_factor': portfolio.get('profit_factor', 0),
        'total_trades': portfolio.get('total_trades', 0),
        'avg_trade_return_pct': portfolio.get('avg_trade_return', 0) * 100,
        'best_trade_pct': portfolio.get('best_trade', 0) * 100,
        'worst_trade_pct': portfolio.get('worst_trade', 0) * 100,
        'avg_hold_time_days': portfolio.get('avg_hold_time', 0),
        'cash_drag_pct': portfolio.get('cash_drag', 0) * 100,
        'diversification_score': portfolio.get('diversification_score', 0),
        'drawdown_duration_days': portfolio.get('drawdown_duration', 0),
        
        # Runtime
        'runtime_hours': runtime.get('total_runtime_hours', 0),
        'runtime_minutes': runtime.get('total_runtime_minutes', 0),
    }
    
    # Set output file
    if output_file is None:
        output_file = f"{backtest_folder}_summary.csv"
    
    output_path = logs_dir / backtest_folder / output_file
    
    # Write to CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_data.keys())
        writer.writeheader()
        writer.writerow(csv_data)
    
    print(f"✅ Results exported to: {output_path}")
    print()
    print("📊 Summary (for research papers):")
    print("-" * 60)
    print(f"Annualized Return:  {csv_data['annualized_return_pct']:.2f}%")
    print(f"Volatility:         {csv_data['volatility_pct']:.2f}%")
    print(f"Sharpe Ratio:       {csv_data['sharpe_ratio']:.3f}")
    print(f"Max Drawdown:       {csv_data['max_drawdown_pct']:.2f}%")
    print(f"Win Rate:           {csv_data['win_rate_pct']:.2f}%")
    print(f"Total Trades:       {csv_data['total_trades']}")
    print(f"Runtime:            {csv_data['runtime_hours']:.2f} hours")
    print("-" * 60)
    
    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_results_csv.py <backtest_folder_name> [output.csv]")
        print("\nExample:")
        print("  python export_results_csv.py backtest_llm_full_historical_2000_2025")
        print("\nAvailable backtests:")
        
        logs_dir = Path(__file__).parent / "logs"
        if logs_dir.exists():
            for folder in sorted(logs_dir.iterdir()):
                if folder.is_dir():
                    print(f"  - {folder.name}")
        sys.exit(1)
    
    backtest_folder = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    export_to_csv(backtest_folder, output_file)


if __name__ == "__main__":
    main()


