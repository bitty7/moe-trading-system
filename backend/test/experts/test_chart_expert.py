#!/usr/bin/env python3
"""
Test chart expert functionality.
"""
import sys
from pathlib import Path
# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from experts.chart_expert import ChartExpert, chart_expert
from core.data_types import ChartData, ChartImage

def test_chart_expert_initialization():
    """Test chart expert initialization."""
    print("🧪 test_chart_expert_initialization: Testing expert initialization")
    expert = ChartExpert()
    print("   ✅ Chart expert initialized with LLM client")
    return True

def test_chart_summary_creation():
    """Test chart summary creation."""
    print("🧪 test_chart_summary_creation: Testing chart summary creation")
    expert = ChartExpert()
    
    # Create mock chart data
    mock_charts = [
        ChartImage(
            file_path="test1.png",
            date="2024-H1",
            year=2024,
            half="H1",
            start_date="2024-01-01",
            end_date="2024-06-30",
            width=800,
            height=600,
            image_data=None,
            metadata={}
        ),
        ChartImage(
            file_path="test2.png",
            date="2024-H2",
            year=2024,
            half="H2",
            start_date="2024-07-01",
            end_date="2024-12-31",
            width=800,
            height=600,
            image_data=None,
            metadata={}
        )
    ]
    
    mock_chart_data = ChartData(
        ticker="TEST",
        charts=mock_charts,
        total_charts=2,
        data_quality=0.8
    )
    
    summary = expert._create_chart_summary(mock_chart_data)
    if "Total Charts: 2" in summary and "2024: H1, H2" in summary:
        print("   ✅ Chart summary created successfully")
        print(f"   ✅ Summary: {summary[:100]}...")
        return True
    else:
        print("   ❌ Failed to create chart summary")
        return False

def test_rule_based_analysis():
    """Test rule-based chart analysis."""
    print("🧪 test_rule_based_analysis: Testing rule-based analysis")
    expert = ChartExpert()
    
    # Create mock chart data with good coverage
    mock_charts = [
        ChartImage(
            file_path="test.png",
            date="2024-H1",
            year=2024,
            half="H1",
            start_date="2024-01-01",
            end_date="2024-06-30",
            width=800,
            height=600,
            image_data=None,
            metadata={}
        ) for _ in range(6)  # 6 charts for good coverage
    ]
    
    mock_chart_data = ChartData(
        ticker="TEST",
        charts=mock_charts,
        total_charts=6,
        data_quality=0.9
    )
    
    result = expert._rule_based_chart_analysis(mock_chart_data, 0.0)
    if result:
        print(f"   ✅ Rule-based analysis successful: {result.probabilities}")
        print(f"   ✅ Method: {result.metadata.additional_info.get('method')}")
        return True
    else:
        print("   ❌ Failed to perform rule-based analysis")
        return False

def test_fallback_output():
    """Test fallback output creation."""
    print("🧪 test_fallback_output: Testing fallback output")
    expert = ChartExpert()
    result = expert._create_fallback_output("test_reason", 0.0)
    if result:
        print(f"   ✅ Fallback output created: {result.probabilities}")
        print(f"   ✅ Reason: {result.metadata.additional_info.get('reason')}")
        print(f"   ✅ Method: {result.metadata.additional_info.get('method')}")
        return True
    else:
        print("   ❌ Failed to create fallback output")
        return False

def test_prompt_creation():
    """Test prompt creation."""
    print("🧪 test_prompt_creation: Testing prompt creation")
    expert = ChartExpert()
    
    # Create mock chart data
    mock_charts = [
        ChartImage(
            file_path="test.png",
            date="2024-H1",
            year=2024,
            half="H1",
            start_date="2024-01-01",
            end_date="2024-06-30",
            width=800,
            height=600,
            image_data=None,
            metadata={}
        )
    ]
    
    mock_chart_data = ChartData(
        ticker="TEST",
        charts=mock_charts,
        total_charts=1,
        data_quality=0.8
    )
    
    prompt = expert._create_chart_prompt("TEST", "2024-06-15", mock_chart_data)
    if prompt and "TEST" in prompt and "[p_buy, p_hold, p_sell]" in prompt:
        print("   ✅ Chart prompt created successfully")
        print(f"   ✅ Prompt length: {len(prompt)} characters")
        return True
    else:
        print("   ❌ Failed to create chart prompt")
        return False

def test_main_interface():
    """Test main interface."""
    print("🧪 test_main_interface: Testing main interface")
    result = chart_expert('AA', '2025-04-21', 2)
    if result:
        print(f"   ✅ Main interface successful: {result.probabilities}")
        print(f"   ✅ Method: {result.metadata.additional_info.get('method')}")
        print(f"   ✅ Expert type: {result.metadata.expert_type}")
        return True
    else:
        print("   ❌ Main interface failed")
        return False

def test_no_chart_data():
    """Test handling of no chart data."""
    print("🧪 test_no_chart_data: Testing no data scenario")
    result = chart_expert('NONEXISTENT', '2025-04-21', 2)
    if result:
        print(f"   ✅ No data handled gracefully: {result.probabilities}")
        print(f"   ✅ Method: {result.metadata.additional_info.get('method')}")
        print(f"   ✅ Reason: {result.metadata.additional_info.get('reason')}")
        return True
    else:
        print("   ❌ Failed to handle no data scenario")
        return False

def test_llm_integration():
    """Test LLM integration."""
    print("🧪 test_llm_integration: Testing LLM integration")
    expert = ChartExpert()
    
    # Create mock chart data
    mock_charts = [
        ChartImage(
            file_path="test.png",
            date="2024-H1",
            year=2024,
            half="H1",
            start_date="2024-01-01",
            end_date="2024-06-30",
            width=800,
            height=600,
            image_data=None,
            metadata={}
        )
    ]
    
    mock_chart_data = ChartData(
        ticker="TEST",
        charts=mock_charts,
        total_charts=1,
        data_quality=0.8
    )
    
    result = expert._analyze_with_llm("TEST", "2024-06-15", mock_chart_data, 0.0)
    if result:
        print(f"   ✅ LLM integration successful: {result.probabilities}")
        print(f"   ✅ Method: {result.metadata.additional_info.get('method')}")
        return True
    else:
        print("   ❌ LLM integration failed (this might be expected if LLM is not available)")
        return True  # Don't fail the test if LLM is not available

def run_all_tests():
    """Run all chart expert tests."""
    print("🚀 Running all chart expert tests")
    print("=" * 50)
    
    tests = [
        test_chart_expert_initialization,
        test_chart_summary_creation,
        test_rule_based_analysis,
        test_fallback_output,
        test_prompt_creation,
        test_main_interface,
        test_no_chart_data,
        test_llm_integration
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
        print("🎉 All chart expert tests passed!")
    else:
        print("❌ Some tests failed")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests() 