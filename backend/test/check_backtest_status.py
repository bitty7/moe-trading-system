#!/usr/bin/env python3
"""
Quick script to check backtest status
"""

import os
import json
from datetime import datetime

def check_status(run_id="backtest_llm_full_2019"):
    log_dir = f"../logs/{run_id}"
    
    if not os.path.exists(log_dir):
        print(f"❌ Run not started yet: {log_dir}")
        return
    
    config_path = f"{log_dir}/config.json"
    if not os.path.exists(config_path):
        print(f"⚠️  Config not found: {run_id}")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    status = config.get('status', 'unknown')
    created = config.get('created_at', 'unknown')
    completed = config.get('completed_at', None)
    
    print(f"\n📊 Backtest Status: {run_id}")
    print(f"  Status: {status}")
    print(f"  Started: {created}")
    
    if completed:
        print(f"  Completed: {completed}")
        
        # Check if results exist
        if os.path.exists(f"{log_dir}/results.json"):
            with open(f"{log_dir}/results.json", 'r') as f:
                results = json.load(f)
            
            pm = results.get('portfolio_metrics', {})
            rt = results.get('runtime_metrics', {})
            
            print(f"\n💰 Results:")
            print(f"  Total Return: {pm.get('total_return', 0)*100:.2f}%")
            print(f"  Sharpe Ratio: {pm.get('sharpe_ratio', 0):.3f}")
            print(f"  Total Trades: {pm.get('total_trades', 0)}")
            
            if rt:
                print(f"\n⏱️  Runtime:")
                print(f"  {rt.get('total_runtime_minutes', 0):.1f} minutes")
                print(f"  ({rt.get('total_runtime_hours', 0):.2f} hours)")
    else:
        print(f"  Status: Running...")
        
        # Check partial progress
        if os.path.exists(f"{log_dir}/tickers_daily.json"):
            with open(f"{log_dir}/tickers_daily.json", 'r') as f:
                tickers = json.load(f)
            
            total_days = sum(len(days) for days in tickers.values())
            print(f"  Progress: {total_days} decisions processed")

if __name__ == "__main__":
    check_status()

