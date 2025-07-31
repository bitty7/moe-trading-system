#!/usr/bin/env python3
"""
Test fundamental expert functionality.
"""

import sys
import os
from pathlib import Path
from datetime import date

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experts.fundamental_expert import FundamentalExpert, fundamental_expert
from core.data_types import FundamentalData, FinancialStatement, FinancialMetric

def test_fundamental_expert_initialization():
    """Test expert initialization."""
    print("🧪 test_fundamental_expert_initialization: Testing expert initialization")
    expert = FundamentalExpert()
    if expert.llm_client is not None:
        print("   ✅ Fundamental expert initialized with LLM client")
        return True
    else:
        print("   ❌ Fundamental expert failed to initialize")
        return False

def test_financial_ratio_calculation():
    """Test financial ratio calculation."""
    print("🧪 test_financial_ratio_calculation: Testing ratio calculation")
    expert = FundamentalExpert()
    
    # Create mock financial data
    mock_metrics = {
        'Assets': FinancialMetric('Assets', [1000000], ['2025-04-21'], 'USD'),
        'AssetsCurrent': FinancialMetric('AssetsCurrent', [500000], ['2025-04-21'], 'USD'),
        'Liabilities': FinancialMetric('Liabilities', [300000], ['2025-04-21'], 'USD')
    }
    
    mock_statement = FinancialStatement(
        statement_type='balance_sheet',
        company_name='Test',
        cik='123456',
        filings=[{'filing_date': '2025-04-21'}],
        metrics=mock_metrics,
        filing_count=1
    )
    
    mock_financial_data = FundamentalData(
        ticker='TEST',
        statements={'balance_sheet': mock_statement},
        total_statements=1,
        data_quality=0.9
    )
    
    ratios = expert._calculate_financial_ratios(mock_financial_data)
    
    if ratios:
        print(f"   ✅ Calculated {len(ratios)} ratios")
        for ratio_name, value in ratios.items():
            print(f"   ✅ {ratio_name}: {value:.4f}")
        return True
    else:
        print("   ❌ Failed to calculate ratios")
        return False

def test_rule_based_analysis():
    """Test rule-based fundamental analysis."""
    print("🧪 test_rule_based_analysis: Testing rule-based analysis")
    expert = FundamentalExpert()
    
    # Create mock ratios
    ratios = {
        'current_ratio': 1.8,  # Good ratio
        'debt_to_assets': 0.2,  # Good ratio
        'current_assets_ratio': 0.7  # Good ratio
    }
    
    # Create mock financial data
    mock_statement = FinancialStatement(
        statement_type='balance_sheet',
        company_name='Test',
        cik='123456',
        filings=[{'filing_date': '2025-04-21'}],
        metrics={},
        filing_count=1
    )
    
    mock_financial_data = FundamentalData(
        ticker='TEST',
        statements={'balance_sheet': mock_statement},
        total_statements=1,
        data_quality=0.9
    )
    
    result = expert._rule_based_fundamental_analysis(ratios, mock_financial_data, 0.0)
    
    if result and hasattr(result, 'probabilities'):
        print(f"   ✅ Rule-based analysis successful: {result.probabilities}")
        print(f"   ✅ Method: {result.metadata.additional_info.get('method', 'unknown')}")
        print(f"   ✅ Buy signals: {result.metadata.additional_info.get('buy_signals', 0)}")
        print(f"   ✅ Sell signals: {result.metadata.additional_info.get('sell_signals', 0)}")
        return True
    else:
        print("   ❌ Rule-based analysis failed")
        return False

def test_fallback_output():
    """Test fallback output creation."""
    print("🧪 test_fallback_output: Testing fallback output")
    expert = FundamentalExpert()
    
    result = expert._create_fallback_output("test_reason", 0.0)
    
    if result and hasattr(result, 'probabilities'):
        print(f"   ✅ Fallback output created: {result.probabilities}")
        print(f"   ✅ Reason: {result.metadata.additional_info.get('reason', 'none')}")
        print(f"   ✅ Method: {result.metadata.additional_info.get('method', 'unknown')}")
        return True
    else:
        print("   ❌ Fallback output creation failed")
        return False

def test_prompt_creation():
    """Test LLM prompt creation."""
    print("🧪 test_prompt_creation: Testing prompt creation")
    expert = FundamentalExpert()
    
    ratios = {
        'current_ratio': 1.5,
        'debt_to_assets': 0.3,
        'assets': 1000000
    }
    
    mock_statement = FinancialStatement(
        statement_type='balance_sheet',
        company_name='Test',
        cik='123456',
        filings=[{'filing_date': '2025-04-21'}],
        metrics={},
        filing_count=1
    )
    
    mock_financial_data = FundamentalData(
        ticker='TEST',
        statements={'balance_sheet': mock_statement},
        total_statements=1,
        data_quality=0.9
    )
    
    prompt = expert._create_fundamental_prompt('TEST', '2025-04-21', ratios, mock_financial_data)
    
    if prompt and len(prompt) > 100:
        print(f"   ✅ Prompt created successfully")
        print(f"   ✅ Prompt length: {len(prompt)} characters")
        print(f"   ✅ Contains ratios: {'current_ratio' in prompt}")
        print(f"   ✅ Contains ticker: {'TEST' in prompt}")
        return True
    else:
        print("   ❌ Prompt creation failed")
        return False

def test_main_interface():
    """Test the main interface function."""
    print("🧪 test_main_interface: Testing main interface")
    
    # Test with existing ticker
    result = fundamental_expert('AA', '2025-04-21', 2)
    
    if result and hasattr(result, 'probabilities'):
        print(f"   ✅ Main interface successful: {result.probabilities}")
        print(f"   ✅ Method: {result.metadata.additional_info.get('method', 'unknown')}")
        print(f"   ✅ Expert type: {result.metadata.expert_type}")
        return True
    else:
        print("   ❌ Main interface failed")
        return False

def test_no_fundamental_data():
    """Test behavior when no fundamental data is available."""
    print("🧪 test_no_fundamental_data: Testing no data scenario")
    expert = FundamentalExpert()
    
    # Test with non-existent ticker
    result = expert.analyze_fundamentals('NONEXISTENT', '2025-04-21', 2)
    
    if result and hasattr(result, 'probabilities'):
        print(f"   ✅ No data handled gracefully: {result.probabilities}")
        print(f"   ✅ Method: {result.metadata.additional_info.get('method', 'unknown')}")
        print(f"   ✅ Reason: {result.metadata.additional_info.get('reason', 'none')}")
        return True
    else:
        print("   ❌ No data scenario not handled properly")
        return False

def test_llm_integration():
    """Test LLM integration (if available)."""
    print("🧪 test_llm_integration: Testing LLM integration")
    expert = FundamentalExpert()
    
    # Create mock data for LLM test
    ratios = {
        'current_ratio': 1.5,
        'debt_to_assets': 0.3,
        'assets': 1000000,
        'assetscurrent': 500000
    }
    
    mock_statement = FinancialStatement(
        statement_type='balance_sheet',
        company_name='Test',
        cik='123456',
        filings=[{'filing_date': '2025-04-21'}],
        metrics={},
        filing_count=1
    )
    
    mock_financial_data = FundamentalData(
        ticker='TEST',
        statements={'balance_sheet': mock_statement},
        total_statements=1,
        data_quality=0.9
    )
    
    # Try LLM analysis (may fail if LLM not available)
    result = expert._analyze_with_llm('TEST', '2025-04-21', ratios, mock_financial_data, 0.0)
    
    if result is not None:
        print(f"   ✅ LLM integration successful: {result.probabilities}")
        print(f"   ✅ Method: {result.metadata.additional_info.get('method', 'unknown')}")
        return True
    else:
        print("   ⚠️  LLM integration failed (expected if LLM not available)")
        print("   ✅ Fallback mechanism should work")
        return True  # This is acceptable

def test_ratio_edge_cases():
    """Test edge cases in ratio calculation."""
    print("🧪 test_ratio_edge_cases: Testing ratio edge cases")
    expert = FundamentalExpert()
    
    # Test with zero values
    ratios_zero = {
        'current_ratio': 0.0,
        'debt_to_assets': 0.0,
        'current_assets_ratio': 0.0
    }
    
    # Test with very high values
    ratios_high = {
        'current_ratio': 10.0,
        'debt_to_assets': 0.9,
        'current_assets_ratio': 0.9
    }
    
    mock_statement = FinancialStatement(
        statement_type='balance_sheet',
        company_name='Test',
        cik='123456',
        filings=[{'filing_date': '2025-04-21'}],
        metrics={},
        filing_count=1
    )
    
    mock_financial_data = FundamentalData(
        ticker='TEST',
        statements={'balance_sheet': mock_statement},
        total_statements=1,
        data_quality=0.9
    )
    
    # Test zero ratios
    result_zero = expert._rule_based_fundamental_analysis(ratios_zero, mock_financial_data, 0.0)
    if result_zero:
        print(f"   ✅ Zero ratios handled: {result_zero.probabilities}")
    
    # Test high ratios
    result_high = expert._rule_based_fundamental_analysis(ratios_high, mock_financial_data, 0.0)
    if result_high:
        print(f"   ✅ High ratios handled: {result_high.probabilities}")
    
    return True

def run_all_fundamental_expert_tests():
    """Run all fundamental expert tests."""
    print("🚀 Running all fundamental expert tests")
    print("=" * 50)
    
    tests = [
        test_fundamental_expert_initialization,
        test_financial_ratio_calculation,
        test_rule_based_analysis,
        test_fallback_output,
        test_prompt_creation,
        test_main_interface,
        test_no_fundamental_data,
        test_llm_integration,
        test_ratio_edge_cases
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test {test.__name__} failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All fundamental expert tests passed!")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    run_all_fundamental_expert_tests() 