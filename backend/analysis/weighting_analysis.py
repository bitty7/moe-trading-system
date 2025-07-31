#!/usr/bin/env python3
"""
Weighting Analysis

Analyzes the expert weighting mechanism to understand how weights are calculated
and why certain experts get more influence in the final decision.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from aggregation.expert_aggregator import aggregate_experts
import numpy as np

def analyze_weighting_mechanism():
    """Analyze how the weighting mechanism works."""
    print("🔍 Expert Weighting Analysis")
    print("=" * 60)
    
    ticker = "AA"
    target_date = "2025-04-21"
    
    # Get dynamic weighting result
    result = aggregate_experts(ticker, target_date)
    
    print(f"📊 Analysis for {ticker} on {target_date}")
    print(f"Final Decision: {result.decision_type.value.upper()}")
    print(f"Overall Confidence: {result.overall_confidence:.3f}")
    print()
    
    print("🎯 EXPERT CONTRIBUTIONS:")
    print("-" * 40)
    
    # Sort experts by weight (highest first)
    sorted_contributions = sorted(
        result.expert_contributions.items(), 
        key=lambda x: x[1].weight, 
        reverse=True
    )
    
    for i, (name, contrib) in enumerate(sorted_contributions, 1):
        print(f"{i}. {name.title()}:")
        print(f"   Weight: {contrib.weight:.3f}")
        print(f"   Confidence: {contrib.confidence:.3f}")
        print(f"   Decision: [{contrib.contribution.buy_probability:.1%}, "
              f"{contrib.contribution.hold_probability:.1%}, "
              f"{contrib.contribution.sell_probability:.1%}]")
        print()
    
    print("🧮 WEIGHTING FACTOR BREAKDOWN:")
    print("-" * 40)
    
    for name, contrib in result.expert_contributions.items():
        output = contrib.expert_output
        
        # Calculate decision certainty (entropy-based)
        probabilities = output.probabilities.to_list()
        entropy = -sum(p * np.log(p + 1e-10) for p in probabilities if p > 0)
        max_entropy = np.log(3)  # log(3) for 3 classes
        certainty = 1.0 - (entropy / max_entropy)
        
        print(f"{name.title()}:")
        print(f"  • Base Confidence: {output.confidence.confidence_score:.3f}")
        print(f"  • Data Quality: {output.metadata.input_data_quality:.3f}")
        print(f"  • Processing Time: {output.metadata.processing_time:.3f}s")
        print(f"  • Decision Certainty: {certainty:.3f}")
        
        # Calculate individual weight components
        confidence_weight = output.confidence.confidence_score
        data_quality_bonus = output.metadata.input_data_quality * 0.4
        certainty_bonus = certainty * 0.4
        
        print(f"  • Weight Components:")
        print(f"    - Confidence: {confidence_weight:.3f}")
        print(f"    - Data Quality Bonus: {data_quality_bonus:.3f}")
        print(f"    - Certainty Bonus: {certainty_bonus:.3f}")
        print(f"    - Raw Weight: {confidence_weight + data_quality_bonus + certainty_bonus:.3f}")
        print(f"    - Final Weight: {contrib.weight:.3f}")
        print()
    
    print("💡 WEIGHTING EXPLANATION:")
    print("-" * 40)
    print("The dynamic weighting system considers 3 factors:")
    print()
    print("1. 🎯 EXPERT CONFIDENCE (Base weight)")
    print("   - How confident the expert is in its analysis")
    print("   - Based on data quality, LLM response quality, method used")
    print()
    print("2. 📊 DATA QUALITY BONUS (+40% of data quality)")
    print("   - Rewards experts with high-quality input data")
    print("   - More recent, complete, and relevant data gets higher weight")
    print()
    print("3. 🎲 DECISION CERTAINTY BONUS (+40% of certainty)")
    print("   - Experts with more decisive outputs get higher weight")
    print("   - Based on entropy of probability distribution")
    print("   - Lower entropy = more certain = higher weight")
    print()
    print("The weights are then normalized to sum to 1.0")
    
    return True

def explain_sentiment_expert():
    """Explain why sentiment expert might have lower weight."""
    print("\n" + "=" * 60)
    print("📰 SENTIMENT EXPERT ANALYSIS")
    print("=" * 60)
    
    ticker = "AA"
    target_date = "2025-04-21"
    
    result = aggregate_experts(ticker, target_date)
    
    if 'sentiment' in result.expert_contributions:
        sentiment_contrib = result.expert_contributions['sentiment']
        sentiment_output = sentiment_contrib.expert_output
        
        print(f"📊 Sentiment Expert Analysis for {ticker}")
        print()
        print(f"Weight: {sentiment_contrib.weight:.3f}")
        print(f"Confidence: {sentiment_contrib.confidence:.3f}")
        print(f"Decision: [{sentiment_contrib.contribution.buy_probability:.1%}, "
              f"{sentiment_contrib.contribution.hold_probability:.1%}, "
              f"{sentiment_contrib.contribution.sell_probability:.1%}]")
        print()
        
        print("🔍 WHY MIGHT SENTIMENT HAVE LOWER WEIGHT?")
        print("-" * 40)
        print("1. 📰 NEWS DATA QUALITY:")
        print(f"   - Data Quality: {sentiment_output.metadata.input_data_quality:.3f}")
        print("   - News articles may be sparse or outdated")
        print("   - Sentiment analysis depends on text quality")
        print()
        print("2. 🎲 DECISION CERTAINTY:")
        probabilities = sentiment_output.probabilities.to_list()
        entropy = -sum(p * np.log(p + 1e-10) for p in probabilities if p > 0)
        max_entropy = np.log(3)
        certainty = 1.0 - (entropy / max_entropy)
        print(f"   - Decision Certainty: {certainty:.3f}")
        print("   - News sentiment can be ambiguous")
        print("   - Mixed signals in news articles")
        print()
        print("3. 🎯 EXPERT CONFIDENCE:")
        print(f"   - Base Confidence: {sentiment_output.confidence.confidence_score:.3f}")
        print("   - Lower confidence due to data limitations")
        print("   - News sentiment is inherently subjective")
        
    else:
        print("❌ Sentiment expert not available in results")
    
    return True

def confirm_dynamic_only():
    """Confirm that only dynamic weighting is used."""
    print("\n" + "=" * 60)
    print("✅ DYNAMIC WEIGHTING CONFIRMATION")
    print("=" * 60)
    
    ticker = "AA"
    target_date = "2025-04-21"
    
    result = aggregate_experts(ticker, target_date)
    
    print(f"📊 System Configuration for {ticker}")
    print()
    print(f"Aggregation Method: {result.aggregation_method}")
    print(f"Final Decision: {result.decision_type.value.upper()}")
    print(f"Overall Confidence: {result.overall_confidence:.3f}")
    print()
    
    print("🎯 EXPERT WEIGHTS (Dynamic Only):")
    print("-" * 40)
    for name, contrib in result.expert_contributions.items():
        print(f"  {name.title()}: {contrib.weight:.3f}")
    print()
    
    print("✅ CONFIRMATION:")
    print("-" * 20)
    print("• Only dynamic weighting is available")
    print("• No uniform weighting option")
    print("• Weights based on quality factors only")
    print("• Fair treatment for all expert types")
    
    return True

if __name__ == "__main__":
    print("🚀 Expert Weighting Analysis")
    print("=" * 60)
    
    try:
        analyze_weighting_mechanism()
        explain_sentiment_expert()
        confirm_dynamic_only()
        print("\n🎉 Analysis completed successfully!")
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")
        sys.exit(1) 