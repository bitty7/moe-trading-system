#!/usr/bin/env python3
"""
Expert Aggregation Demo

Demonstrates the expert aggregation system combining outputs from all four experts.
Shows both dynamic and uniform weighting strategies.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from aggregation.expert_aggregator import aggregate_experts
from core.data_types import DecisionType

def demo_expert_aggregation():
    """Demonstrate expert aggregation with different strategies."""
    print("🔍 Expert Aggregation Demo")
    print("=" * 60)
    
    # Test parameters
    ticker = "AA"
    target_date = "2025-04-21"
    
    print(f"📊 Analyzing {ticker} for {target_date}")
    print()
    
    # Test dynamic weighting
    print("🎯 Dynamic Weighting Strategy")
    print("-" * 30)
    dynamic_result = aggregate_experts(ticker, target_date, use_dynamic_weighting=True)
    
    print(f"Final Decision: {dynamic_result.decision_type.value.upper()}")
    print(f"Probabilities: Buy {dynamic_result.final_probabilities.buy_probability:.1%}, "
          f"Hold {dynamic_result.final_probabilities.hold_probability:.1%}, "
          f"Sell {dynamic_result.final_probabilities.sell_probability:.1%}")
    print(f"Overall Confidence: {dynamic_result.overall_confidence:.3f}")
    print(f"Processing Time: {dynamic_result.processing_time:.2f}s")
    print()
    
    print("Expert Contributions (Dynamic):")
    for name, contrib in dynamic_result.expert_contributions.items():
        print(f"  {name.title()}: weight={contrib.weight:.3f}, "
              f"confidence={contrib.confidence:.3f}, "
              f"decision=[{contrib.contribution.buy_probability:.1%}, "
              f"{contrib.contribution.hold_probability:.1%}, "
              f"{contrib.contribution.sell_probability:.1%}]")
    print()
    
    # Test uniform weighting
    print("⚖️  Uniform Weighting Strategy")
    print("-" * 30)
    uniform_result = aggregate_experts(ticker, target_date, use_dynamic_weighting=False)
    
    print(f"Final Decision: {uniform_result.decision_type.value.upper()}")
    print(f"Probabilities: Buy {uniform_result.final_probabilities.buy_probability:.1%}, "
          f"Hold {uniform_result.final_probabilities.hold_probability:.1%}, "
          f"Sell {uniform_result.final_probabilities.sell_probability:.1%}")
    print(f"Overall Confidence: {uniform_result.overall_confidence:.3f}")
    print(f"Processing Time: {uniform_result.processing_time:.2f}s")
    print()
    
    print("Expert Contributions (Uniform):")
    for name, contrib in uniform_result.expert_contributions.items():
        print(f"  {name.title()}: weight={contrib.weight:.3f}, "
              f"confidence={contrib.confidence:.3f}, "
              f"decision=[{contrib.contribution.buy_probability:.1%}, "
              f"{contrib.contribution.hold_probability:.1%}, "
              f"{contrib.contribution.sell_probability:.1%}]")
    print()
    
    # Compare strategies
    print("📈 Strategy Comparison")
    print("-" * 30)
    print(f"Decision Agreement: {'✅' if dynamic_result.decision_type == uniform_result.decision_type else '❌'}")
    print(f"Dynamic Confidence: {dynamic_result.overall_confidence:.3f}")
    print(f"Uniform Confidence: {uniform_result.overall_confidence:.3f}")
    print(f"Confidence Difference: {abs(dynamic_result.overall_confidence - uniform_result.overall_confidence):.3f}")
    print()
    
    # Show reasoning
    print("🧠 Decision Reasoning")
    print("-" * 30)
    print(f"Dynamic: {dynamic_result.reasoning}")
    print()
    print(f"Uniform: {uniform_result.reasoning}")
    print()
    
    # Key insights
    print("💡 Key Insights")
    print("-" * 30)
    print("• Dynamic weighting adjusts expert influence based on:")
    print("  - Expert confidence scores")
    print("  - Data quality metrics")
    print("  - Processing time efficiency")
    print("  - Decision certainty (entropy)")
    print()
    print("• Uniform weighting gives equal importance to all experts")
    print()
    print("• The gating network ensures robust aggregation even when")
    print("  some experts fail or provide low-quality outputs")
    
    return True

def demo_multiple_tickers():
    """Demonstrate aggregation across multiple tickers."""
    print("\n" + "=" * 60)
    print("📊 Multi-Ticker Analysis")
    print("=" * 60)
    
    tickers = ["AA", "AAAU", "AACG"]
    target_date = "2025-04-21"
    
    results = {}
    
    for ticker in tickers:
        print(f"\n🔍 Analyzing {ticker}...")
        try:
            result = aggregate_experts(ticker, target_date, use_dynamic_weighting=True)
            results[ticker] = result
            
            print(f"  Decision: {result.decision_type.value.upper()}")
            print(f"  Confidence: {result.overall_confidence:.3f}")
            print(f"  Top Expert: {max(result.expert_contributions.items(), key=lambda x: x[1].weight)[0].title()}")
            
        except Exception as e:
            print(f"  ❌ Error analyzing {ticker}: {e}")
    
    # Summary
    print(f"\n📋 Summary for {target_date}:")
    print("-" * 30)
    decisions = [r.decision_type.value.upper() for r in results.values()]
    print(f"Decisions: {', '.join(decisions)}")
    
    avg_confidence = sum(r.overall_confidence for r in results.values()) / len(results)
    print(f"Average Confidence: {avg_confidence:.3f}")
    
    return True

if __name__ == "__main__":
    print("🚀 Expert Aggregation System Demo")
    print("=" * 60)
    
    try:
        demo_expert_aggregation()
        demo_multiple_tickers()
        print("\n🎉 Demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1) 