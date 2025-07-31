#!/usr/bin/env python3
"""
Compare the fundamental expert with other experts to show its unique characteristics.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from experts.fundamental_expert import fundamental_expert
from experts.sentiment_expert import sentiment_expert
from experts.technical_timeseries_expert import technical_timeseries_expert
from data_loader.load_prices import load_prices_for_ticker

def compare_fundamental_expert():
    """Compare fundamental expert with other experts."""
    print("🔍 Fundamental Expert Comparison")
    print("=" * 60)
    
    ticker = "AA"
    date = "2025-04-21"
    
    print(f"📊 Comparing experts for {ticker} on {date}")
    print("-" * 60)
    
    # Get fundamental expert result
    print("\n📊 FUNDAMENTAL EXPERT:")
    print("   Data Source: Financial statements (JSON)")
    print("   Analysis: Financial ratios and LLM interpretation")
    print("   Time Window: 2-year lookback")
    
    fundamental_result = fundamental_expert(ticker, date, 2)
    print(f"   Probabilities: {fundamental_result.probabilities}")
    print(f"   Method: {fundamental_result.metadata.additional_info.get('method', 'unknown')}")
    print(f"   Ratios Analyzed: {fundamental_result.metadata.additional_info.get('ratios_analyzed', 0)}")
    print(f"   Statements: {fundamental_result.metadata.additional_info.get('statements_available', 0)}")
    print(f"   Confidence: {fundamental_result.confidence.confidence_score}")
    print(f"   Processing Time: {fundamental_result.metadata.processing_time:.2f}s")
    
    # Get sentiment expert result
    print("\n📰 SENTIMENT EXPERT:")
    print("   Data Source: News articles (JSONL)")
    print("   Analysis: Text sentiment analysis")
    print("   Time Window: 7-day lookback")
    
    sentiment_result = sentiment_expert(ticker, date, 7)
    print(f"   Probabilities: {sentiment_result.probabilities}")
    print(f"   Method: {sentiment_result.metadata.additional_info.get('method', 'unknown')}")
    print(f"   Articles Analyzed: {sentiment_result.metadata.additional_info.get('articles_analyzed', 0)}")
    print(f"   Confidence: {sentiment_result.confidence.confidence_score}")
    print(f"   Processing Time: {sentiment_result.metadata.processing_time:.2f}s")
    
    # Get technical expert result
    print("\n📈 TECHNICAL TIMESERIES EXPERT:")
    print("   Data Source: OHLCV price data (CSV)")
    print("   Analysis: Technical indicators (MA, momentum)")
    print("   Time Window: Historical patterns")
    
    price_data = load_prices_for_ticker(ticker)
    technical_result = technical_timeseries_expert(price_data, ticker)
    print(f"   Probabilities: {technical_result.probabilities}")
    print(f"   Method: {technical_result.metadata.additional_info.get('method', 'unknown')}")
    print(f"   Indicators Used: {technical_result.metadata.additional_info.get('indicators_used', [])}")
    print(f"   Confidence: {technical_result.confidence.confidence_score}")
    print(f"   Processing Time: {technical_result.metadata.processing_time:.2f}s")
    
    print("\n" + "=" * 60)
    print("📊 COMPARISON SUMMARY:")
    print("-" * 60)
    
    # Decision comparison
    decisions = {
        'Fundamental': fundamental_result.probabilities,
        'Sentiment': sentiment_result.probabilities,
        'Technical': technical_result.probabilities
    }
    
    print("🎯 Decision Comparison:")
    for expert_name, probs in decisions.items():
        decision = "BUY" if probs.buy_probability > max(probs.hold_probability, probs.sell_probability) else \
                   "SELL" if probs.sell_probability > max(probs.buy_probability, probs.hold_probability) else "HOLD"
        print(f"   {expert_name}: {decision} ({probs.buy_probability:.1%} buy, {probs.hold_probability:.1%} hold, {probs.sell_probability:.1%} sell)")
    
    # Confidence comparison
    confidences = {
        'Fundamental': fundamental_result.confidence.confidence_score,
        'Sentiment': sentiment_result.confidence.confidence_score,
        'Technical': technical_result.confidence.confidence_score
    }
    
    print("\n🎯 Confidence Comparison:")
    for expert_name, conf in confidences.items():
        print(f"   {expert_name}: {conf:.2f}")
    
    # Processing time comparison
    times = {
        'Fundamental': fundamental_result.metadata.processing_time,
        'Sentiment': sentiment_result.metadata.processing_time,
        'Technical': technical_result.metadata.processing_time
    }
    
    print("\n⏱️  Processing Time Comparison:")
    for expert_name, time_taken in times.items():
        print(f"   {expert_name}: {time_taken:.2f}s")
    
    print("\n" + "=" * 60)
    print("📋 FUNDAMENTAL EXPERT CHARACTERISTICS:")
    print("-" * 60)
    print("🔹 Data Sources:")
    print("   • Balance sheets, cash flow statements, equity statements")
    print("   • Financial ratios and metrics")
    print("   • Historical financial performance")
    
    print("\n🔹 Analysis Methods:")
    print("   • LLM interpretation of financial health")
    print("   • Rule-based ratio analysis")
    print("   • Financial strength assessment")
    
    print("\n🔹 Time Perspectives:")
    print("   • Long-term financial stability (2-year lookback)")
    print("   • Historical performance trends")
    print("   • Fundamental value assessment")
    
    print("\n🔹 Decision Factors:")
    print("   • Financial ratios (current ratio, debt-to-assets, etc.)")
    print("   • Company financial health and stability")
    print("   • Growth potential and profitability")
    print("   • Risk assessment and debt levels")
    
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION BENEFITS:")
    print("-" * 60)
    print("✅ Long-term fundamental perspective (vs short-term technical/sentiment)")
    print("✅ Financial health and stability focus")
    print("✅ Quantitative ratio analysis")
    print("✅ Robust fallback mechanisms")
    print("✅ Consistent output format for aggregation")
    print("✅ LLM + rule-based hybrid approach")
    
    print("\n" + "=" * 60)
    print("💡 KEY INSIGHTS:")
    print("-" * 60)
    print("🔸 Fundamental expert provides long-term financial perspective")
    print("🔸 Complements short-term technical and sentiment analysis")
    print("🔸 Focuses on company financial health and stability")
    print("🔸 Uses quantitative ratios for objective assessment")
    print("🔸 Provides robust fallback when LLM unavailable")
    
    return True

if __name__ == "__main__":
    compare_fundamental_expert() 