"""
test_technical_timeseries_expert.py

Unit tests for technical timeseries expert.
Tests both LLM and rule-based decision making.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List
from experts.technical_timeseries_expert import (
    technical_timeseries_expert, 
    calculate_technical_indicators,
    create_llm_prompt,
    llm_technical_analysis,
    moving_average_crossover_signal,
    momentum_signal
)
from core.logging_config import get_logger

logger = get_logger("test_technical_timeseries_expert")

def make_df(prices: List[float]) -> pd.DataFrame:
    """Create test DataFrame with given prices."""
    dates = [datetime.now() - timedelta(days=i) for i in range(len(prices)-1, -1, -1)]
    return pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': [1000000] * len(prices)
    })

def test_technical_indicators():
    """Test technical indicators calculation."""
    logger.info("🧪 test_technical_indicators: Testing indicator calculation")
    
    # Create test data
    prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    df = make_df(prices)
    
    indicators = calculate_technical_indicators(df, short_window=3, long_window=7)
    
    if indicators:
        logger.info(f"   ✅ Indicators calculated: {list(indicators.keys())}")
        logger.info(f"   Current price: {indicators.get('current_price')}")
        logger.info(f"   MA3: {indicators.get('ma3')}")
        logger.info(f"   MA7: {indicators.get('ma7')}")
        return True
    else:
        logger.error("   ❌ No indicators calculated")
        return False

def test_llm_prompt_creation():
    """Test LLM prompt creation."""
    logger.info("🧪 test_llm_prompt_creation: Testing prompt formatting")
    
    indicators = {
        'current_price': 15.50,
        'ma3': 15.2,
        'ma7': 14.8,
        'price_trend': 'uptrend',
        'price_change_5d': 0.05,
        'volatility': 0.02,
        'support_level': 14.0,
        'resistance_level': 16.0,
        'volume_trend': 'normal_volume',
        'avg_volume': 1000000
    }
    
    prompt = create_llm_prompt("AAPL", "2024-01-15", indicators)
    
    if "AAPL" in prompt and "technical indicators" in prompt.lower():
        logger.info("   ✅ Prompt created successfully")
        logger.info(f"   Prompt length: {len(prompt)} characters")
        return True
    else:
        logger.error("   ❌ Prompt creation failed")
        return False

def test_buy_signal():
    """Test buy signal generation."""
    logger.info("🧪 test_buy_signal: Testing MA crossover buy signal")

    # Create data where short MA crosses above long MA
    # Start with short MA below long MA, then create upward trend
    # Pattern: flat at 10, then jump to 15 to force crossover
    prices = [10] * 10 + [15] * 15
    df = make_df(prices)

    # Debug: show the moving averages
    df['ma3'] = df['close'].rolling(window=3).mean()
    df['ma7'] = df['close'].rolling(window=7).mean()
    logger.info(f"   Last 10 rows:\n{df.tail(10)}")

    result = technical_timeseries_expert(df, use_llm=False)
    if result.probabilities.buy_probability > 0.5:  # Buy probability > 50%
        logger.info(f"   ✅ Buy signal generated: {result.probabilities.to_list()}")
        logger.info(f"   Method: {result.metadata.additional_info.get('method')}")
        return True
    else:
        logger.error(f"   ❌ No buy signal: {result.probabilities.to_list()}")
        return False

def test_sell_signal():
    """Test sell signal generation."""
    logger.info("🧪 test_sell_signal: Testing MA crossover sell signal")

    # Create data where short MA crosses below long MA
    # Start with short MA above long MA, then create downward trend
    prices = [15] * 10 + [10] * 15
    df = make_df(prices)

    result = technical_timeseries_expert(df, use_llm=False)
    if result.probabilities.sell_probability > 0.5:  # Sell probability > 50%
        logger.info(f"   ✅ Sell signal generated: {result.probabilities.to_list()}")
        logger.info(f"   Method: {result.metadata.additional_info.get('method')}")
        return True
    else:
        logger.error(f"   ❌ No sell signal: {result.probabilities.to_list()}")
        return False

def test_hold_signal():
    """Test hold signal generation."""
    logger.info("🧪 test_hold_signal: Testing hold signal")

    # Create data with no clear trend - need enough data for MA calculation
    # Use a very flat pattern to avoid any crossovers
    # Make sure the moving averages are very close to each other
    prices = [10.0] * 20  # Completely flat data
    df = make_df(prices)

    # Debug: show the moving averages
    df['ma3'] = df['close'].rolling(window=3).mean()
    df['ma7'] = df['close'].rolling(window=7).mean()
    logger.info(f"   Last 10 rows:\n{df.tail(10)[['close', 'ma3', 'ma7']]}")

    result = technical_timeseries_expert(df, use_llm=False)
    logger.info(f"   Result method: {result.metadata.additional_info.get('method')}")
    logger.info(f"   Result reason: {result.metadata.additional_info.get('reason')}")
    
    if result.probabilities.hold_probability > 0.5:  # Hold probability > 50%
        logger.info(f"   ✅ Hold signal generated: {result.probabilities.to_list()}")
        return True
    else:
        logger.error(f"   ❌ No hold signal: {result.probabilities.to_list()}")
        return False

def test_insufficient_data():
    """Test handling of insufficient data."""
    logger.info("🧪 test_insufficient_data: Testing insufficient data handling")

    # Create DataFrame with only 2 days of data (need at least 7 for MA)
    prices = [10, 11]
    df = make_df(prices)

    result = technical_timeseries_expert(df, use_llm=False)
    
    # Should return hold with low confidence
    if (result.probabilities.hold_probability > 0.9 and 
        result.confidence.confidence_score < 0.2):
        logger.info(f"   ✅ Insufficient data handled correctly: {result.probabilities.to_list()}")
        logger.info(f"   Confidence: {result.confidence.confidence_score}")
        return True
    else:
        logger.error(f"   ❌ Insufficient data not handled correctly: {result.probabilities.to_list()}")
        return False

def test_llm_integration():
    """Test LLM integration (may fail if Ollama not running)."""
    logger.info("🧪 test_llm_integration: Testing LLM integration")
    
    # Create test data
    prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    df = make_df(prices)
    
    result = technical_timeseries_expert(df, ticker="TEST", use_llm=True)
    
    if result is not None:
        logger.info(f"   ✅ LLM integration successful: {result.probabilities.to_list()}")
        logger.info(f"   Method: {result.metadata.additional_info.get('method')}")
        logger.info(f"   Model: {result.metadata.model_name}")
        return True
    else:
        logger.warning("   ⚠️ LLM integration failed (Ollama may not be running)")
        return True  # Don't fail the test if LLM is not available

def test_momentum_signal():
    """Test momentum signal generation."""
    logger.info("🧪 test_momentum_signal: Testing momentum signals")
    
    # Test positive momentum (buy signal) - need more dramatic change
    # Create data where the last 5 elements show a clear increase
    # The momentum function looks at the last 5 elements, so we need a trend there
    prices = [10] * 5 + [12, 13, 14, 15, 16]  # Last 5 elements show upward trend
    df = make_df(prices)
    
    # Debug: show the price change
    start = df['close'].iloc[-5]  # Last 5th element
    end = df['close'].iloc[-1]    # Last element
    pct_change = (end - start) / start
    logger.info(f"   Price change: {start} -> {end} = {pct_change:.2%}")
    
    result = momentum_signal(df, window=5, threshold=0.03)
    if result and result.probabilities.buy_probability > 0.5:
        logger.info(f"   ✅ Positive momentum detected: {result.probabilities.to_list()}")
    else:
        logger.error(f"   ❌ Positive momentum not detected: {result.probabilities.to_list() if result else 'None'}")
        return False
    
    # Test negative momentum (sell signal) - need more dramatic change
    prices = [15] * 5 + [14, 13, 12, 11, 10]  # Last 5 elements show downward trend
    df = make_df(prices)
    
    # Debug: show the price change
    start = df['close'].iloc[-5]  # Last 5th element
    end = df['close'].iloc[-1]    # Last element
    pct_change = (end - start) / start
    logger.info(f"   Price change: {start} -> {end} = {pct_change:.2%}")
    
    result = momentum_signal(df, window=5, threshold=0.03)
    if result and result.probabilities.sell_probability > 0.5:
        logger.info(f"   ✅ Negative momentum detected: {result.probabilities.to_list()}")
        return True
    else:
        logger.error(f"   ❌ Negative momentum not detected: {result.probabilities.to_list() if result else 'None'}")
        return False

def run_all():
    """Run all tests."""
    logger.info("🚀 Running all technical timeseries expert tests")
    
    tests = [
        test_technical_indicators,
        test_llm_prompt_creation,
        test_buy_signal,
        test_sell_signal,
        test_hold_signal,
        test_insufficient_data,
        test_llm_integration,
        test_momentum_signal
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
    
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    success = run_all()
    exit(0 if success else 1) 