#!/usr/bin/env python3
"""
Test chart data loader functionality.
"""
import sys
from pathlib import Path
# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from data_loader.load_charts import ChartDataLoader, load_charts_for_ticker

def test_chart_data_loader_initialization():
    """Test chart data loader initialization."""
    print("🧪 test_chart_data_loader_initialization: Testing loader initialization")
    loader = ChartDataLoader()
    print(f"   ✅ Chart data loader initialized with path: {loader.data_path}")
    return True

def test_load_charts_for_ticker():
    """Test loading chart data for a ticker."""
    print("🧪 test_load_charts_for_ticker: Testing chart data loading")
    loader = ChartDataLoader()
    data = loader.load_charts_for_ticker('AA', '2023-01-01', '2025-12-31')
    if data is not None:
        print(f"   ✅ Successfully loaded chart data for AA")
        print(f"   ✅ Charts available: {data.total_charts}")
        print(f"   ✅ Data quality: {data.data_quality:.2f}")
        print(f"   ✅ Years covered: {sorted(set(chart.year for chart in data.charts))}")
        return True
    else:
        print("   ❌ Failed to load chart data")
        return False

def test_load_nonexistent_ticker():
    """Test loading charts for non-existent ticker."""
    print("🧪 test_load_nonexistent_ticker: Testing non-existent ticker")
    loader = ChartDataLoader()
    data = loader.load_charts_for_ticker('NONEXISTENT', '2023-01-01', '2025-12-31')
    if data is None:
        print("   ✅ Correctly returned None for non-existent ticker")
        return True
    else:
        print("   ❌ Should have returned None for non-existent ticker")
        return False

def test_date_filtering():
    """Test date filtering functionality."""
    print("🧪 test_date_filtering: Testing date filtering")
    loader = ChartDataLoader()
    # Test with old dates (should return None or empty)
    data = loader.load_charts_for_ticker('AA', '1990-01-01', '1995-12-31')
    if data is None or len(data.charts) == 0:
        print("   ✅ Correctly filtered out old dates (no data)")
        return True
    else:
        print("   ❌ Should have filtered out old dates")
        return False

def test_filename_parsing():
    """Test chart filename parsing."""
    print("🧪 test_filename_parsing: Testing filename parsing")
    loader = ChartDataLoader()
    
    # Test valid filename
    valid_filename = "aa_2024_H1_candlestick.png"
    result = loader._parse_chart_filename(valid_filename)
    if result:
        print(f"   ✅ Successfully parsed: {valid_filename}")
        print(f"   ✅ Ticker: {result['ticker']}")
        print(f"   ✅ Year: {result['year']}")
        print(f"   ✅ Half: {result['half']}")
        return True
    else:
        print("   ❌ Failed to parse valid filename")
        return False

def test_invalid_filename_parsing():
    """Test invalid filename parsing."""
    print("🧪 test_invalid_filename_parsing: Testing invalid filename parsing")
    loader = ChartDataLoader()
    
    # Test invalid filename
    invalid_filename = "invalid_filename.png"
    result = loader._parse_chart_filename(invalid_filename)
    if result is None:
        print("   ✅ Correctly rejected invalid filename")
        return True
    else:
        print("   ❌ Should have rejected invalid filename")
        return False

def test_chart_coverage():
    """Test chart coverage reporting."""
    print("🧪 test_chart_coverage: Testing coverage reporting")
    loader = ChartDataLoader()
    coverage = loader.get_chart_coverage('AA')
    if coverage['available']:
        print(f"   ✅ Coverage available for AA")
        print(f"   ✅ Total files: {coverage['total_files']}")
        print(f"   ✅ Years covered: {coverage['years_covered'][:5]}...")  # Show first 5 years
        return True
    else:
        print("   ❌ No coverage found for AA")
        return False

def test_convenience_function():
    """Test convenience function."""
    print("🧪 test_convenience_function: Testing convenience function")
    data = load_charts_for_ticker('AA', '2023-01-01', '2025-12-31')
    if data is not None:
        print(f"   ✅ Convenience function works with existing ticker")
        print(f"   ✅ Charts loaded: {data.total_charts}")
        return True
    else:
        print("   ❌ Convenience function failed")
        return False

def run_all_tests():
    """Run all chart data loader tests."""
    print("🚀 Running all chart data loader tests")
    print("=" * 50)
    
    tests = [
        test_chart_data_loader_initialization,
        test_load_charts_for_ticker,
        test_load_nonexistent_ticker,
        test_date_filtering,
        test_filename_parsing,
        test_invalid_filename_parsing,
        test_chart_coverage,
        test_convenience_function
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
        print("🎉 All chart data loader tests passed!")
    else:
        print("❌ Some tests failed")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests() 