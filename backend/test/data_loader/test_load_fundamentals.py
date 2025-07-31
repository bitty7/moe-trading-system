#!/usr/bin/env python3
"""
Test fundamental data loader functionality.
"""

import sys
import os
from pathlib import Path
import json
from datetime import date

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_loader.load_fundamentals import FundamentalDataLoader, load_fundamentals_for_ticker

def test_fundamental_data_loader_initialization():
    """Test loader initialization."""
    print("🧪 test_fundamental_data_loader_initialization: Testing loader initialization")
    loader = FundamentalDataLoader()
    if loader.data_path is not None:
        print(f"   ✅ Fundamental data loader initialized with path: {loader.data_path}")
        return True
    else:
        print("   ❌ Fundamental data loader failed to initialize")
        return False

def test_load_fundamentals_for_ticker():
    """Test loading fundamental data for a ticker."""
    print("🧪 test_load_fundamentals_for_ticker: Testing fundamental data loading")
    loader = FundamentalDataLoader()
    
    # Test with existing ticker
    data = loader.load_fundamentals_for_ticker('AA', '2023-01-01', '2025-04-21')
    
    if data is not None:
        print(f"   ✅ Successfully loaded fundamental data for AA")
        print(f"   ✅ Statements available: {data.total_statements}")
        print(f"   ✅ Data quality: {data.data_quality:.2f}")
        
        # Check statement types
        for stmt_type, statement in data.statements.items():
            print(f"   ✅ {stmt_type}: {statement.filing_count} filings, {len(statement.metrics)} metrics")
        
        return True
    else:
        print("   ❌ Failed to load fundamental data")
        return False

def test_load_nonexistent_ticker():
    """Test loading data for non-existent ticker."""
    print("🧪 test_load_nonexistent_ticker: Testing non-existent ticker")
    loader = FundamentalDataLoader()
    
    data = loader.load_fundamentals_for_ticker('NONEXISTENT', '2023-01-01', '2025-04-21')
    
    if data is None:
        print("   ✅ Correctly returned None for non-existent ticker")
        return True
    else:
        print("   ❌ Should have returned None for non-existent ticker")
        return False

def test_date_filtering():
    """Test date filtering functionality."""
    print("🧪 test_date_filtering: Testing date filtering")
    loader = FundamentalDataLoader()
    
    # Test with very old date range (should have no data)
    data = loader.load_fundamentals_for_ticker('AA', '2000-01-01', '2001-01-01')
    
    if data is None:
        print("   ✅ Correctly filtered out old dates (no data)")
        return True
    else:
        print("   ❌ Should have returned None for old date range")
        return False

def test_statement_type_detection():
    """Test statement type detection from filenames."""
    print("🧪 test_statement_type_detection: Testing statement type detection")
    loader = FundamentalDataLoader()
    
    # Test different filename patterns
    test_cases = [
        ('condensed_consolidated_balance_sheets.json', 'balance_sheet'),
        ('condensed_consolidated_statement_of_cash_flows.json', 'cash_flow'),
        ('condensed_consolidated_statement_of_equity.json', 'equity'),
        ('income_statement.json', 'income'),
        ('unknown.json', 'unknown')
    ]
    
    all_passed = True
    for filename, expected_type in test_cases:
        detected_type = loader._determine_statement_type(filename)
        if detected_type == expected_type:
            print(f"   ✅ {filename} -> {detected_type}")
        else:
            print(f"   ❌ {filename} -> {detected_type} (expected {expected_type})")
            all_passed = False
    
    return all_passed

def test_financial_metric_extraction():
    """Test extraction of financial metrics from filings."""
    print("🧪 test_financial_metric_extraction: Testing metric extraction")
    loader = FundamentalDataLoader()
    
    # Create mock filing data that matches the expected structure
    mock_filings = [
        {
            'filing_date': '2025-04-21',
            'facts': {
                'us-gaap': {
                    'Assets': {
                        'units': {
                            'USD': [
                                {'val': 1000000, 'end': '2025-04-21'}
                            ]
                        }
                    },
                    'AssetsCurrent': {
                        'units': {
                            'USD': [
                                {'val': 500000, 'end': '2025-04-21'}
                            ]
                        }
                    }
                }
            }
        }
    ]
    
    try:
        metrics = loader._extract_metrics_from_filings(mock_filings)
        
        if metrics and 'Assets' in metrics and 'AssetsCurrent' in metrics:
            print(f"   ✅ Successfully extracted {len(metrics)} metrics")
            print(f"   ✅ Assets: {metrics['Assets'].values[-1] if metrics['Assets'].values else 'N/A'}")
            print(f"   ✅ Current Assets: {metrics['AssetsCurrent'].values[-1] if metrics['AssetsCurrent'].values else 'N/A'}")
            return True
        else:
            print("   ❌ Failed to extract metrics from mock data")
            print(f"   Available metrics: {list(metrics.keys()) if metrics else 'None'}")
            return False
    except Exception as e:
        print(f"   ❌ Error during metric extraction: {e}")
        return False

def test_data_quality_calculation():
    """Test data quality score calculation."""
    print("🧪 test_data_quality_calculation: Testing quality calculation")
    loader = FundamentalDataLoader()
    
    # Test with empty statements
    quality_empty = loader._calculate_data_quality({})
    if quality_empty == 0.0:
        print("   ✅ Empty statements quality: 0.0")
    else:
        print(f"   ❌ Empty statements quality: {quality_empty} (expected 0.0)")
        return False
    
    # Test with mock statements
    from core.data_types import FinancialStatement, FinancialMetric
    
    mock_metrics = {
        'test': FinancialMetric('test', [100], ['2025-04-21'], 'USD')
    }
    
    mock_statement = FinancialStatement(
        statement_type='balance_sheet',
        company_name='Test',
        cik='123456',
        filings=[{'filing_date': '2025-04-21'}],
        metrics=mock_metrics,
        filing_count=1
    )
    
    mock_statements = {'balance_sheet': mock_statement}
    quality_mock = loader._calculate_data_quality(mock_statements)
    
    if 0.0 < quality_mock <= 1.0:
        print(f"   ✅ Mock statements quality: {quality_mock:.2f}")
        return True
    else:
        print(f"   ❌ Mock statements quality: {quality_mock} (should be 0.0-1.0)")
        return False

def test_convenience_function():
    """Test the convenience function."""
    print("🧪 test_convenience_function: Testing convenience function")
    
    # Test with existing ticker
    data = load_fundamentals_for_ticker('AA', '2023-01-01', '2025-04-21')
    
    if data is not None:
        print("   ✅ Convenience function works with existing ticker")
        return True
    else:
        print("   ❌ Convenience function failed")
        return False

def test_fundamental_coverage():
    """Test fundamental data coverage reporting."""
    print("🧪 test_fundamental_coverage: Testing coverage reporting")
    loader = FundamentalDataLoader()
    
    coverage = loader.get_fundamental_coverage('AA')
    
    if coverage['available']:
        print(f"   ✅ Coverage available for AA")
        print(f"   ✅ Total filings: {coverage['total_filings']}")
        for stmt_type, info in coverage['statements'].items():
            if info['available']:
                print(f"   ✅ {stmt_type}: {info['filings_count']} filings")
            else:
                print(f"   ⚠️  {stmt_type}: {info.get('reason', 'unknown')}")
        return True
    else:
        print(f"   ❌ Coverage not available: {coverage.get('reason', 'unknown')}")
        return False

def run_all_fundamental_tests():
    """Run all fundamental data loader tests."""
    print("🚀 Running all fundamental data loader tests")
    print("=" * 50)
    
    tests = [
        test_fundamental_data_loader_initialization,
        test_load_fundamentals_for_ticker,
        test_load_nonexistent_ticker,
        test_date_filtering,
        test_statement_type_detection,
        test_financial_metric_extraction,
        test_data_quality_calculation,
        test_convenience_function,
        test_fundamental_coverage
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
        print("🎉 All fundamental data loader tests passed!")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    run_all_fundamental_tests() 