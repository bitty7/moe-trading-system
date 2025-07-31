#!/usr/bin/env python3
"""
test_expert_on_real_data.py

Integration test for technical timeseries expert on real data.
Tests both LLM and rule-based modes on actual ticker data.
Optimized for efficiency - uses small data subsets for testing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from pathlib import Path
import pandas as pd
from data_loader.load_prices import load_prices_for_ticker
from experts.technical_timeseries_expert import technical_timeseries_expert
from core.logging_config import get_logger

logger = get_logger("test_expert_on_real_data")

def run_expert_on_ticker_subset(ticker: str, data_dir: Path = Path("../dataset/HS500-samples/SP500_time_series"), 
                               short_window: int = 3, long_window: int = 7, use_llm: bool = True,
                               max_days: int = 50):
    """
    Run expert on a subset of real data for a specific ticker.
    
    Args:
        ticker (str): Stock ticker
        data_dir (Path): Path to time series data
        short_window (int): Short MA window
        long_window (int): Long MA window
        use_llm (bool): Whether to use LLM analysis
        max_days (int): Maximum number of days to test (for efficiency)
    """
    mode = "LLM" if use_llm else "Rule-based"
    logger.info(f"🚀 Running {mode} expert on subset of real data for ticker: {ticker} (MA {short_window}/{long_window})")
    
    df = load_prices_for_ticker(ticker, data_dir)
    if df is None or len(df) == 0:
        logger.error(f"No data found for ticker '{ticker}'")
        return
    
    df = df[df['close'].notnull()].reset_index(drop=True)
    
    # Take only the last max_days for efficiency
    if len(df) > max_days:
        df = df.tail(max_days).reset_index(drop=True)
        logger.info(f"Using last {max_days} days from {len(df)} total rows for {ticker}")
    else:
        logger.info(f"Using all {len(df)} rows for {ticker}")
    
    logger.info(f"Data range: {df['date'].iloc[0]} to {df['date'].iloc[-1]}")
    
    results = []
    # Test only every 5th day to reduce computational load
    test_indices = list(range(0, len(df), 5)) + [len(df) - 1]  # Include the last day
    test_indices = sorted(list(set(test_indices)))  # Remove duplicates
    
    for i in test_indices:
        sub_df = df.iloc[:i+1].copy()
        result = technical_timeseries_expert(
            sub_df, 
            ticker=ticker,
            short_window=short_window, 
            long_window=long_window,
            use_llm=use_llm
        )
        results.append({
            'date': sub_df['date'].iloc[-1],
            'close': sub_df['close'].iloc[-1],
            'probabilities': result.probabilities.to_list(),
            'reason': result.metadata.additional_info.get('reason', 'Unknown'),
            'meta_type': result.metadata.additional_info.get('method', 'unknown'),
            'confidence': result.confidence.confidence_score
        })
    
    # Count signals
    buy_count = sum(1 for r in results if r['probabilities'][0] > 0.5)
    sell_count = sum(1 for r in results if r['probabilities'][2] > 0.5)
    hold_count = sum(1 for r in results if r['probabilities'][1] > 0.5)
    
    logger.info(f"Summary for {ticker} ({mode}, MA {short_window}/{long_window}): BUY={buy_count}, SELL={sell_count}, HOLD={hold_count}")
    
    # Show first signals
    first_buy = next((r for r in results if r['probabilities'][0] > 0.5), None)
    first_sell = next((r for r in results if r['probabilities'][2] > 0.5), None)
    
    if first_buy:
        logger.info(f"First BUY signal: {first_buy['date']} | close=${first_buy['close']:.2f} | probs={first_buy['probabilities']} | type={first_buy['meta_type']} | conf={first_buy['confidence']:.2f}")
    if first_sell:
        logger.info(f"First SELL signal: {first_sell['date']} | close=${first_sell['close']:.2f} | probs={first_sell['probabilities']} | type={first_sell['meta_type']} | conf={first_sell['confidence']:.2f}")
    
    # Show some recent decisions (last 5)
    recent_results = results[-5:] if len(results) >= 5 else results
    logger.info(f"Recent decisions for {ticker}:")
    for r in recent_results:
        decision = "BUY" if r['probabilities'][0] > 0.5 else "SELL" if r['probabilities'][2] > 0.5 else "HOLD"
        logger.info(f"  {r['date']}: {decision} (${r['close']:.2f}) - {r['meta_type']} (conf: {r['confidence']:.2f})")

def compare_llm_vs_rules_subset(ticker: str, data_dir: Path = Path("../dataset/HS500-samples/SP500_time_series"), max_days: int = 30):
    """
    Compare LLM vs rule-based decisions on a subset of the same data.
    
    Args:
        ticker (str): Stock ticker to test
        data_dir (Path): Path to time series data
        max_days (int): Maximum days to test
    """
    logger.info(f"🔄 Comparing LLM vs Rule-based decisions for {ticker} (subset)")
    
    df = load_prices_for_ticker(ticker, data_dir)
    if df is None or len(df) == 0:
        logger.error(f"No data found for ticker '{ticker}'")
        return
    
    df = df[df['close'].notnull()].reset_index(drop=True)
    
    # Test on last max_days of data
    test_df = df.tail(max_days).reset_index(drop=True)
    logger.info(f"Testing on last {len(test_df)} days of {ticker} data")
    
    # Get decisions from both modes
    llm_result = technical_timeseries_expert(test_df, ticker=ticker, use_llm=True)
    rule_result = technical_timeseries_expert(test_df, ticker=ticker, use_llm=False)
    
    logger.info(f"LLM Decision: {llm_result.probabilities.to_list()} - {llm_result.metadata.additional_info.get('method')} (conf: {llm_result.confidence.confidence_score:.2f})")
    logger.info(f"Rule Decision: {rule_result.probabilities.to_list()} - {rule_result.metadata.additional_info.get('method')} (conf: {rule_result.confidence.confidence_score:.2f})")
    
    # Compare decisions
    llm_decision = "BUY" if llm_result.probabilities.buy_probability > 0.5 else "SELL" if llm_result.probabilities.sell_probability > 0.5 else "HOLD"
    rule_decision = "BUY" if rule_result.probabilities.buy_probability > 0.5 else "SELL" if rule_result.probabilities.sell_probability > 0.5 else "HOLD"
    
    if llm_decision == rule_decision:
        logger.info(f"✅ Both modes agree: {llm_decision}")
    else:
        logger.info(f"⚠️ Modes disagree: LLM={llm_decision}, Rules={rule_decision}")

def run_efficient_tests():
    """Run efficient integration tests on small data subsets."""
    logger.info("🚀 Running efficient technical timeseries expert integration tests")
    
    data_dir = Path("../dataset/HS500-samples/SP500_time_series")
    tickers = ['aa']  # Test only one ticker for efficiency
    
    # Test configurations (reduced for efficiency)
    configs = [
        (3, 7, True),   # LLM with short MA
        (3, 7, False),  # Rules with short MA
    ]
    
    for ticker in tickers:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing ticker: {ticker}")
        logger.info(f"{'='*60}")
        
        for short_window, long_window, use_llm in configs:
            try:
                run_expert_on_ticker_subset(ticker, data_dir, short_window, long_window, use_llm, max_days=30)
                logger.info("")  # Empty line for readability
            except Exception as e:
                logger.error(f"Error testing {ticker} with config ({short_window}, {long_window}, LLM={use_llm}): {e}")
        
        # Compare LLM vs rules on subset
        try:
            compare_llm_vs_rules_subset(ticker, data_dir, max_days=20)
        except Exception as e:
            logger.error(f"Error comparing modes for {ticker}: {e}")

if __name__ == "__main__":
    run_efficient_tests() 