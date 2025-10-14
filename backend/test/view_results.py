#!/usr/bin/env python3
"""
Quick script to view backtest results in a readable format
Usage: python test/view_results.py <run_id>
Example: python test/view_results.py backtest_llm_full_2019
"""

import json
import sys
import os

if len(sys.argv) > 1:
    run_id = sys.argv[1]
else:
    run_id = "backtest_llm_full_2019"  # Default

results_file = f"logs/{run_id}/results.json"

if not os.path.exists(results_file):
    print(f"❌ Results file not found: {results_file}")
    print(f"\nAvailable runs:")
    if os.path.exists("logs"):
        for d in os.listdir("logs"):
            if os.path.isdir(f"logs/{d}"):
                print(f"  - {d}")
    sys.exit(1)

with open(results_file, 'r') as f:
    results = json.load(f)

print("\n" + "="*80)
print(f"📊 BACKTEST RESULTS: {run_id}")
print("="*80)

# Portfolio metrics
pm = results['portfolio_metrics']
print(f"\n💰 PORTFOLIO PERFORMANCE:")
print(f"  Total Return:        {pm['total_return']*100:>8.2f}%")
print(f"  Annualized Return:   {pm['annualized_return']*100:>8.2f}%")
print(f"  Sharpe Ratio:        {pm['sharpe_ratio']:>8.3f}")
print(f"  Sortino Ratio:       {pm['sortino_ratio']:>8.3f}")
print(f"  Calmar Ratio:        {pm['calmar_ratio']:>8.3f}")

print(f"\n📉 RISK METRICS:")
print(f"  Max Drawdown:        {pm['max_drawdown']*100:>8.2f}%")
print(f"  Drawdown Duration:   {pm['drawdown_duration']:>8d} days")
print(f"  Volatility:          {pm['volatility']*100:>8.2f}%")

print(f"\n📈 TRADING METRICS:")
print(f"  Total Trades:        {pm['total_trades']:>8d}")
print(f"  Win Rate:            {pm['win_rate']*100:>8.1f}%")
print(f"  Profit Factor:       {pm['profit_factor']:>8.2f}")
print(f"  Avg Trade Return:    {pm['avg_trade_return']*100:>8.3f}%")
print(f"  Best Trade:          {pm['best_trade']*100:>8.2f}%")
print(f"  Worst Trade:         {pm['worst_trade']*100:>8.2f}%")

# Per-ticker summary
print(f"\n" + "="*80)
print("📊 PER-TICKER PERFORMANCE:")
print("="*80)

for ticker, metrics in results['ticker_summary'].items():
    print(f"\n{ticker.upper()}:")
    print(f"  Return:           {metrics['total_return']*100:>8.2f}%")
    print(f"  Trades:           {metrics['num_trades']:>8d}")
    print(f"  Sharpe:           {metrics['sharpe_ratio']:>8.3f}")
    print(f"  Max DD:           {metrics['max_drawdown']*100:>8.2f}%")
    print(f"  Contribution:     {metrics['contribution_to_portfolio']*100:>8.1f}%")

print("\n" + "="*80)
print("✅ Results loaded successfully!")
print("="*80 + "\n")

