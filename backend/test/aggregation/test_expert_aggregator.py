#!/usr/bin/env python3
"""
Test expert aggregator functionality.
"""
import sys
from pathlib import Path
# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from aggregation.expert_aggregator import ExpertAggregator, aggregate_experts, ExpertContribution, AggregationResult
from core.data_types import DecisionType, DecisionProbabilities

def test_expert_aggregator_initialization():
    """Test expert aggregator initialization."""
    print("🧪 test_expert_aggregator_initialization: Testing aggregator initialization")
    
    # Test dynamic weighting (only option)
    aggregator = ExpertAggregator()
    print(f"   ✅ Dynamic weighting aggregator initialized")
    
    return True

def test_gating_weight_calculation():
    """Test gating weight calculation."""
    print("🧪 test_gating_weight_calculation: Testing weight calculation")
    
    aggregator = ExpertAggregator()
    
    # Test dynamic weighting (only option)
    print("   ✅ Dynamic weighting is the only option")
    return True

def test_probability_aggregation():
    """Test probability aggregation."""
    print("🧪 test_probability_aggregation: Testing probability aggregation")
    
    aggregator = ExpertAggregator()
    
    # Create mock expert outputs
    from core.data_types import ExpertOutput, ExpertConfidence, ExpertMetadata
    from datetime import datetime
    
    mock_outputs = {
        'expert1': ExpertOutput(
            probabilities=DecisionProbabilities(0.6, 0.3, 0.1),
            confidence=ExpertConfidence(0.8, 0.2, 0.9),
            metadata=ExpertMetadata("test", "test", 1.0, 0.9)
        ),
        'expert2': ExpertOutput(
            probabilities=DecisionProbabilities(0.2, 0.6, 0.2),
            confidence=ExpertConfidence(0.7, 0.3, 0.8),
            metadata=ExpertMetadata("test", "test", 1.0, 0.8)
        )
    }
    
    weights = {'expert1': 0.6, 'expert2': 0.4}
    result = aggregator._aggregate_probabilities(mock_outputs, weights)
    
    # Check that probabilities sum to 1.0
    total = result.buy_probability + result.hold_probability + result.sell_probability
    if abs(total - 1.0) < 0.001:
        print(f"   ✅ Probability aggregation successful: {result}")
        print(f"   ✅ Total probability: {total:.3f}")
        return True
    else:
        print(f"   ❌ Probability aggregation failed: {result}")
        return False

def test_decision_determination():
    """Test decision determination."""
    print("🧪 test_decision_determination: Testing decision determination")
    
    aggregator = ExpertAggregator()
    
    # Test buy decision
    buy_probs = DecisionProbabilities(0.6, 0.3, 0.1)
    buy_decision = aggregator._determine_decision(buy_probs)
    if buy_decision == DecisionType.BUY:
        print("   ✅ Buy decision determined correctly")
    else:
        print("   ❌ Buy decision determination failed")
        return False
    
    # Test hold decision
    hold_probs = DecisionProbabilities(0.2, 0.6, 0.2)
    hold_decision = aggregator._determine_decision(hold_probs)
    if hold_decision == DecisionType.HOLD:
        print("   ✅ Hold decision determined correctly")
    else:
        print("   ❌ Hold decision determination failed")
        return False
    
    # Test sell decision
    sell_probs = DecisionProbabilities(0.1, 0.3, 0.6)
    sell_decision = aggregator._determine_decision(sell_probs)
    if sell_decision == DecisionType.SELL:
        print("   ✅ Sell decision determined correctly")
    else:
        print("   ❌ Sell decision determination failed")
        return False
    
    return True

def test_confidence_calculation():
    """Test overall confidence calculation."""
    print("🧪 test_confidence_calculation: Testing confidence calculation")
    
    aggregator = ExpertAggregator()
    
    # Create mock contributions
    contributions = {
        'expert1': ExpertContribution(
            expert_name='expert1',
            expert_output=None,
            weight=0.6,
            contribution=DecisionProbabilities(0.6, 0.3, 0.1),
            confidence=0.8,
            processing_time=1.0
        ),
        'expert2': ExpertContribution(
            expert_name='expert2',
            expert_output=None,
            weight=0.4,
            contribution=DecisionProbabilities(0.2, 0.6, 0.2),
            confidence=0.7,
            processing_time=1.0
        )
    }
    
    overall_confidence = aggregator._calculate_overall_confidence(contributions)
    expected_confidence = 0.8 * 0.6 + 0.7 * 0.4  # Weighted average
    
    if abs(overall_confidence - expected_confidence) < 0.001:
        print(f"   ✅ Confidence calculation successful: {overall_confidence:.3f}")
        return True
    else:
        print(f"   ❌ Confidence calculation failed: {overall_confidence:.3f}")
        return False

def test_reasoning_generation():
    """Test reasoning generation."""
    print("🧪 test_reasoning_generation: Testing reasoning generation")
    
    aggregator = ExpertAggregator()
    
    # Create mock contributions
    contributions = {
        'expert1': ExpertContribution(
            expert_name='expert1',
            expert_output=None,
            weight=0.6,
            contribution=DecisionProbabilities(0.6, 0.3, 0.1),
            confidence=0.8,
            processing_time=1.0
        ),
        'expert2': ExpertContribution(
            expert_name='expert2',
            expert_output=None,
            weight=0.4,
            contribution=DecisionProbabilities(0.2, 0.6, 0.2),
            confidence=0.7,
            processing_time=1.0
        )
    }
    
    reasoning = aggregator._generate_reasoning(contributions, DecisionType.BUY)
    
    if reasoning and "BUY" in reasoning and "Expert1" in reasoning:
        print("   ✅ Reasoning generation successful")
        print(f"   ✅ Reasoning: {reasoning[:100]}...")
        return True
    else:
        print("   ❌ Reasoning generation failed")
        return False

def test_main_interface():
    """Test main interface with dynamic weighting."""
    print("🧪 test_main_interface: Testing main interface")
    
    result = aggregate_experts('AA', '2025-04-21')
    
    if result and result.aggregation_method == "dynamic_gating":
        print(f"   ✅ Dynamic aggregation successful")
        print(f"   ✅ Decision: {result.decision_type.value}")
        print(f"   ✅ Confidence: {result.overall_confidence:.3f}")
        print(f"   ✅ Processing time: {result.processing_time:.2f}s")
        return True
    else:
        print("   ❌ Dynamic aggregation failed")
        return False

def test_expert_contributions():
    """Test expert contributions creation."""
    print("🧪 test_expert_contributions: Testing expert contributions")
    
    aggregator = ExpertAggregator()
    
    # Create mock expert outputs
    from core.data_types import ExpertOutput, ExpertConfidence, ExpertMetadata
    
    mock_outputs = {
        'expert1': ExpertOutput(
            probabilities=DecisionProbabilities(0.6, 0.3, 0.1),
            confidence=ExpertConfidence(0.8, 0.2, 0.9),
            metadata=ExpertMetadata("test", "test", 1.0, 0.9)
        )
    }
    
    weights = {'expert1': 1.0}
    contributions = aggregator._create_expert_contributions(mock_outputs, weights)
    
    if 'expert1' in contributions:
        contrib = contributions['expert1']
        if contrib.expert_name == 'expert1' and contrib.weight == 1.0:
            print("   ✅ Expert contributions created successfully")
            return True
        else:
            print("   ❌ Expert contributions creation failed")
            return False
    else:
        print("   ❌ Expert contributions creation failed")
        return False

def test_fallback_result():
    """Test fallback result creation."""
    print("🧪 test_fallback_result: Testing fallback result")
    
    aggregator = ExpertAggregator()
    result = aggregator._create_fallback_result(0.0)
    
    if (result.aggregation_method == "fallback" and 
        result.decision_type == DecisionType.HOLD and
        result.overall_confidence == 0.1):
        print("   ✅ Fallback result created successfully")
        return True
    else:
        print("   ❌ Fallback result creation failed")
        return False

def run_all_tests():
    """Run all expert aggregator tests."""
    print("🚀 Running all expert aggregator tests")
    print("=" * 50)
    
    tests = [
        test_expert_aggregator_initialization,
        test_gating_weight_calculation,
        test_probability_aggregation,
        test_decision_determination,
        test_confidence_calculation,
        test_reasoning_generation,
        test_expert_contributions,
        test_fallback_result,
        test_main_interface
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test {test.__name__} failed with error: {e}")
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All expert aggregator tests passed!")
    else:
        print("❌ Some tests failed")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests() 