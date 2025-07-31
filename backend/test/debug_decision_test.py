#!/usr/bin/env python3
"""
Debug script to test expert aggregator decisions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aggregation.expert_aggregator import aggregate_experts
from core.data_types import DecisionType

def test_expert_decisions():
    """Test expert aggregator decisions."""
    print("🧪 Testing Expert Aggregator Decisions")
    print("=" * 50)
    
    # Test with a specific date
    ticker = "aa"
    target_date = "2024-01-02"
    
    print(f"Testing {ticker} on {target_date}")
    print()
    
    try:
        # Get expert aggregation result
        result = aggregate_experts(ticker, target_date, lookback_days=7, lookback_years=2)
        
        print(f"✅ Expert aggregation completed!")
        print(f"   Decision Type: {result.decision_type}")
        print(f"   Decision Value: '{result.decision_type.value}'")
        print(f"   Overall Confidence: {result.overall_confidence:.3f}")
        print(f"   Reasoning: {result.reasoning}")
        print()
        
        print("📊 Final Probabilities:")
        print(f"   Buy: {result.final_probabilities.buy_probability:.3f}")
        print(f"   Hold: {result.final_probabilities.hold_probability:.3f}")
        print(f"   Sell: {result.final_probabilities.sell_probability:.3f}")
        print()
        
        print("🔍 Expert Contributions:")
        for name, contrib in result.expert_contributions.items():
            print(f"   {name.title()}:")
            print(f"     Weight: {contrib.weight:.3f}")
            print(f"     Confidence: {contrib.confidence:.3f}")
            print(f"     Probabilities: Buy={contrib.contribution.buy_probability:.3f}, Hold={contrib.contribution.hold_probability:.3f}, Sell={contrib.contribution.sell_probability:.3f}")
            print()
        
        # Test decision mapping
        print("🔄 Testing Decision Mapping:")
        action_mapping = {
            'BUY': 'BUY',
            'SELL': 'SELL', 
            'HOLD': 'HOLD',
            'buy': 'BUY',
            'sell': 'SELL',
            'hold': 'HOLD'
        }
        
        mapped_action = action_mapping.get(result.decision_type.value, 'HOLD')
        print(f"   Original: '{result.decision_type.value}'")
        print(f"   Mapped: '{mapped_action}'")
        print(f"   Would execute trade: {mapped_action in ['BUY', 'SELL']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_expert_decisions() 