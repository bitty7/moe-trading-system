#!/usr/bin/env python3
"""
Compare the chart expert with other experts to show its unique characteristics.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from experts.chart_expert import chart_expert
from experts.sentiment_expert import sentiment_expert
from experts.technical_timeseries_expert import technical_timeseries_expert
from experts.fundamental_expert import fundamental_expert
from data_loader.load_prices import load_prices_for_ticker

def compare_chart_expert():
    print("🔍 Chart Expert Comparison")
    print("=" * 60)
    print("📊 Comparing all experts for AA on 2025-04-21")
    print("-" * 60)
    
    # Load price data for technical expert
    df = load_prices_for_ticker('AA')
    
    # Run all experts
    chart_result = chart_expert('AA', '2025-04-21', 2)
    sentiment_result = sentiment_expert('AA', '2025-04-21', 7)
    technical_result = technical_timeseries_expert(df, 'AA')
    fundamental_result = fundamental_expert('AA', '2025-04-21', 2)
    
    # Display results
    print(f"\n📊 CHART EXPERT:")
    print(f"   Data Source: Candlestick chart images (PNG)")
    print(f"   Analysis: Visual pattern recognition")
    print(f"   Time Window: 2-year lookback")
    print(f"   Probabilities: {chart_result.probabilities}")
    print(f"   Method: {chart_result.metadata.additional_info.get('method')}")
    print(f"   Charts Analyzed: {chart_result.metadata.additional_info.get('charts_analyzed', 0)}")
    print(f"   Confidence: {chart_result.confidence.confidence_score:.3f}")
    print(f"   Processing Time: {chart_result.metadata.processing_time:.2f}s")
    
    print(f"\n📰 SENTIMENT EXPERT:")
    print(f"   Data Source: News articles (JSONL)")
    print(f"   Analysis: Text sentiment analysis")
    print(f"   Time Window: 7-day lookback")
    print(f"   Probabilities: {sentiment_result.probabilities}")
    print(f"   Method: {sentiment_result.metadata.additional_info.get('method')}")
    print(f"   Articles Analyzed: {sentiment_result.metadata.additional_info.get('articles_analyzed', 0)}")
    print(f"   Confidence: {sentiment_result.confidence.confidence_score:.3f}")
    print(f"   Processing Time: {sentiment_result.metadata.processing_time:.2f}s")
    
    print(f"\n📈 TECHNICAL TIMESERIES EXPERT:")
    print(f"   Data Source: OHLCV price data (CSV)")
    print(f"   Analysis: Technical indicators (MA, momentum)")
    print(f"   Time Window: Historical patterns")
    print(f"   Probabilities: {technical_result.probabilities}")
    print(f"   Method: {technical_result.metadata.additional_info.get('method')}")
    print(f"   Indicators Used: {technical_result.metadata.additional_info.get('indicators', [])}")
    print(f"   Confidence: {technical_result.confidence.confidence_score:.3f}")
    print(f"   Processing Time: {technical_result.metadata.processing_time:.2f}s")
    
    print(f"\n📊 FUNDAMENTAL EXPERT:")
    print(f"   Data Source: Financial statements (JSON)")
    print(f"   Analysis: Financial ratios and LLM interpretation")
    print(f"   Time Window: 2-year lookback")
    print(f"   Probabilities: {fundamental_result.probabilities}")
    print(f"   Method: {fundamental_result.metadata.additional_info.get('method')}")
    print(f"   Ratios Analyzed: {fundamental_result.metadata.additional_info.get('ratios_analyzed', 0)}")
    print(f"   Confidence: {fundamental_result.confidence.confidence_score:.3f}")
    print(f"   Processing Time: {fundamental_result.metadata.processing_time:.2f}s")
    
    print("\n" + "=" * 60)
    print("📊 COMPARISON SUMMARY:")
    print("-" * 60)
    
    # Decision comparison
    print("🎯 Decision Comparison:")
    print(f"   Chart: {chart_result.probabilities.buy_probability:.1%} buy, {chart_result.probabilities.hold_probability:.1%} hold, {chart_result.probabilities.sell_probability:.1%} sell")
    print(f"   Sentiment: {sentiment_result.probabilities.buy_probability:.1%} buy, {sentiment_result.probabilities.hold_probability:.1%} hold, {sentiment_result.probabilities.sell_probability:.1%} sell")
    print(f"   Technical: {technical_result.probabilities.buy_probability:.1%} buy, {technical_result.probabilities.hold_probability:.1%} hold, {technical_result.probabilities.sell_probability:.1%} sell")
    print(f"   Fundamental: {fundamental_result.probabilities.buy_probability:.1%} buy, {fundamental_result.probabilities.hold_probability:.1%} hold, {fundamental_result.probabilities.sell_probability:.1%} sell")
    
    # Confidence comparison
    print(f"\n🎯 Confidence Comparison:")
    print(f"   Chart: {chart_result.confidence.confidence_score:.3f}")
    print(f"   Sentiment: {sentiment_result.confidence.confidence_score:.3f}")
    print(f"   Technical: {technical_result.confidence.confidence_score:.3f}")
    print(f"   Fundamental: {fundamental_result.confidence.confidence_score:.3f}")
    
    # Processing time comparison
    print(f"\n⏱️  Processing Time Comparison:")
    print(f"   Chart: {chart_result.metadata.processing_time:.2f}s")
    print(f"   Sentiment: {sentiment_result.metadata.processing_time:.2f}s")
    print(f"   Technical: {technical_result.metadata.processing_time:.2f}s")
    print(f"   Fundamental: {fundamental_result.metadata.processing_time:.2f}s")
    
    print("\n" + "=" * 60)
    print("📋 CHART EXPERT CHARACTERISTICS:")
    print("-" * 60)
    print("🔹 Data Sources:")
    print("   • Candlestick chart images (PNG files)")
    print("   • Visual pattern recognition")
    print("   • Chart period analysis (H1/H2)")
    
    print("\n🔹 Analysis Methods:")
    print("   • LLM interpretation of chart patterns")
    print("   • Rule-based chart availability analysis")
    print("   • Visual trend and pattern recognition")
    
    print("\n🔹 Time Perspectives:")
    print("   • Medium-term chart patterns (2-year lookback)")
    print("   • Visual trend analysis")
    print("   • Chart period coverage assessment")
    
    print("\n🔹 Decision Factors:")
    print("   • Chart availability and coverage")
    print("   • Visual pattern recognition")
    print("   • Chart data quality and recency")
    print("   • Historical chart patterns")
    
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION BENEFITS:")
    print("-" * 60)
    print("✅ Visual pattern recognition (vs numerical/text analysis)")
    print("✅ Chart-specific insights and trends")
    print("✅ Medium-term visual perspective")
    print("✅ Robust fallback mechanisms")
    print("✅ Consistent output format for aggregation")
    print("✅ LLM + rule-based hybrid approach")
    
    print("\n" + "=" * 60)
    print("💡 KEY INSIGHTS:")
    print("-" * 60)
    print("🔸 Chart expert provides visual pattern analysis")
    print("🔸 Complements numerical and text-based analysis")
    print("🔸 Focuses on chart availability and visual trends")
    print("🔸 Uses chart period analysis for decision making")
    print("🔸 Provides robust fallback when LLM unavailable")
    
    return True

if __name__ == "__main__":
    compare_chart_expert() 