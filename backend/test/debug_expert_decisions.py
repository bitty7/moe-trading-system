#!/usr/bin/env python3

from aggregation.expert_aggregator import aggregate_experts
from core.data_types import DecisionType

def test_expert_decisions():
    print("🧪 Testing Expert Decisions")
    print("=" * 50)
    
    # Test a few dates
    test_dates = ['2025-01-01', '2025-01-02', '2025-01-03']
    
    for date in test_dates:
        print(f"\n📅 Testing date: {date}")
        try:
            result = aggregate_experts('aa', date, 7, 2)
            print(f"   Decision: {result.decision_type.value}")
            print(f"   Confidence: {result.overall_confidence:.3f}")
            print(f"   Reasoning: {result.reasoning[:100]}...")
            print("   Expert outputs:")
            for name, contrib in result.expert_contributions.items():
                probs = contrib.expert_output.probabilities.to_list()
                print(f"     {name}: {probs}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_expert_decisions() 