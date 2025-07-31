#!/usr/bin/env python3
"""
Compare the outputs of different experts to show similarities and differences.
This helps understand how each expert contributes to the overall decision-making process.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from experts.sentiment_expert import sentiment_expert
from experts.technical_timeseries_expert import technical_timeseries_expert
from data_loader.load_prices import load_prices_for_ticker

def compare_expert_outputs():
    """Compare outputs of different experts for the same ticker and date."""
    print("🔍 Expert Output Comparison")
    print("=" * 60)
    
    ticker = "AA"
    date = "2025-04-21"
    
    print(f"📊 Comparing experts for {ticker} on {date}")
    print("-" * 60)
    
    # Get sentiment expert output
    print("\n📰 SENTIMENT EXPERT:")
    print("   Data Source: News articles (JSONL)")
    print("   Analysis: Text sentiment analysis")
    print("   Time Window: 7-day lookback")
    
    sentiment_result = sentiment_expert(ticker, date, 7)
    print(f"   Probabilities: {sentiment_result.probabilities}")
    print(f"   Method: {sentiment_result.metadata.additional_info.get('method', 'unknown')}")
    print(f"   Articles Analyzed: {sentiment_result.metadata.additional_info.get('articles_analyzed', 0)}")
    print(f"   Confidence: {sentiment_result.confidence.confidence_score:.2f}")
    print(f"   Processing Time: {sentiment_result.metadata.processing_time:.2f}s")
    
    # Get technical expert output
    print("\n📈 TECHNICAL TIMESERIES EXPERT:")
    print("   Data Source: OHLCV price data (CSV)")
    print("   Analysis: Technical indicators (MA, momentum)")
    print("   Time Window: Historical patterns")
    
    # Load price data for technical expert
    price_df = load_prices_for_ticker(ticker)
    if price_df is not None:
        technical_result = technical_timeseries_expert(price_df, ticker)
        print(f"   Probabilities: {technical_result.probabilities}")
        print(f"   Method: {technical_result.metadata.additional_info.get('method', 'unknown')}")
        print(f"   Indicators Used: {technical_result.metadata.additional_info.get('indicators_used', [])}")
        print(f"   Confidence: {technical_result.confidence.confidence_score:.2f}")
        print(f"   Processing Time: {technical_result.metadata.processing_time:.2f}s")
    else:
        print("   ❌ Could not load price data")
        technical_result = None
    
    # Compare the outputs
    print("\n" + "=" * 60)
    print("📊 COMPARISON SUMMARY:")
    print("-" * 60)
    
    if technical_result:
        print("✅ Both experts returned valid outputs")
        print(f"   Sentiment: {sentiment_result.probabilities}")
        print(f"   Technical: {technical_result.probabilities}")
        
        # Compare confidence levels
        print(f"\n🎯 Confidence Comparison:")
        print(f"   Sentiment: {sentiment_result.confidence.confidence_score:.2f}")
        print(f"   Technical: {technical_result.confidence.confidence_score:.2f}")
        
        # Compare processing times
        print(f"\n⏱️  Processing Time Comparison:")
        print(f"   Sentiment: {sentiment_result.metadata.processing_time:.2f}s")
        print(f"   Technical: {technical_result.metadata.processing_time:.2f}s")
        
        # Compare decision alignment
        sentiment_decision = max(['buy', 'hold', 'sell'], 
                               key=lambda x: getattr(sentiment_result.probabilities, f'{x}_probability'))
        technical_decision = max(['buy', 'hold', 'sell'], 
                               key=lambda x: getattr(technical_result.probabilities, f'{x}_probability'))
        
        print(f"\n🎯 Decision Alignment:")
        print(f"   Sentiment Decision: {sentiment_decision.upper()}")
        print(f"   Technical Decision: {technical_decision.upper()}")
        
        if sentiment_decision == technical_decision:
            print(f"   ✅ DECISIONS ALIGN: Both experts suggest {sentiment_decision.upper()}")
        else:
            print(f"   ⚠️  DECISIONS DIFFER: Sentiment suggests {sentiment_decision.upper()}, Technical suggests {technical_decision.upper()}")
    
    print("\n" + "=" * 60)
    print("📋 KEY DIFFERENCES:")
    print("-" * 60)
    print("🔹 Data Sources:")
    print("   • Sentiment: Text-based news articles")
    print("   • Technical: Numerical price/volume data")
    print("\n🔹 Analysis Methods:")
    print("   • Sentiment: LLM text interpretation + keyword counting")
    print("   • Technical: Mathematical indicators + LLM pattern recognition")
    print("\n🔹 Time Perspectives:")
    print("   • Sentiment: Recent news events (7-day lookback)")
    print("   • Technical: Historical price patterns (all available data)")
    print("\n🔹 Decision Factors:")
    print("   • Sentiment: Market sentiment, news impact, public opinion")
    print("   • Technical: Price trends, momentum, moving averages")
    
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION BENEFITS:")
    print("-" * 60)
    print("✅ Complementary perspectives (fundamental vs technical)")
    print("✅ Different time horizons (short-term vs medium-term)")
    print("✅ Robust fallback mechanisms for both experts")
    print("✅ Consistent output format for easy aggregation")
    print("✅ LLM + rule-based hybrid approach in both")
    
    return True

if __name__ == "__main__":
    compare_expert_outputs() 