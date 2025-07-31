"""
test_load_news.py

Unit tests for news data loader.
Tests JSONL parsing, date handling, and data structure conversion.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import tempfile
import json
from pathlib import Path
from datetime import date
from data_loader.load_news import NewsDataLoader, load_news_for_ticker
from core.logging_config import get_logger

logger = get_logger("test_load_news")

def create_test_jsonl_file():
    """Create a temporary test JSONL file with sample news data."""
    test_data = [
        {
            "Date": "2024-01-15",
            "Url": "https://example.com/article1",
            "Article": "Positive news about company growth and strong earnings.",
            "Stock_symbol": "aa",
            "Article_title": "Company Reports Strong Growth"
        },
        {
            "Date": "2024-01-16",
            "Url": "https://example.com/article2",
            "Article": "Market analysis shows declining trends in the sector.",
            "Stock_symbol": "aa",
            "Article_title": "Sector Analysis Shows Decline"
        },
        {
            "Date": "2024-01-17",
            "Url": "https://example.com/article3",
            "Article": "Neutral market conditions with mixed signals.",
            "Stock_symbol": "aa",
            "Article_title": "Mixed Market Signals"
        }
    ]
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    
    for item in test_data:
        temp_file.write(json.dumps(item) + '\n')
    
    temp_file.close()
    return temp_file.name

def test_news_data_loader_initialization():
    """Test news data loader initialization."""
    print("🧪 test_news_data_loader_initialization: Testing loader initialization")
    
    loader = NewsDataLoader()
    
    if loader.data_path is not None:
        print(f"   ✅ News data loader initialized with path: {loader.data_path}")
        return True
    else:
        print("   ❌ News data loader failed to initialize")
        return False

def test_jsonl_parsing():
    """Test JSONL file parsing."""
    print("🧪 test_jsonl_parsing: Testing JSONL parsing")
    
    # Create test file
    test_file_path = create_test_jsonl_file()
    
    try:
        loader = NewsDataLoader()
        articles = loader._parse_jsonl_file(Path(test_file_path))
        
        if len(articles) == 3:
            print(f"   ✅ Successfully parsed {len(articles)} articles")
            
            # Check article structure
            first_article = articles[0]
            if (first_article.title == "Company Reports Strong Growth" and 
                first_article.published_date == date(2024, 1, 15)):
                print("   ✅ Article structure is correct")
                return True
            else:
                print("   ❌ Article structure is incorrect")
                return False
        else:
            print(f"   ❌ Expected 3 articles, got {len(articles)}")
            return False
            
    finally:
        # Clean up
        os.unlink(test_file_path)

def test_date_filtering():
    """Test date range filtering."""
    print("🧪 test_date_filtering: Testing date filtering")
    
    # Create test file
    test_file_path = create_test_jsonl_file()
    
    try:
        loader = NewsDataLoader()
        
        # Test with date range
        articles = loader._parse_jsonl_file(
            Path(test_file_path), 
            start_date="2024-01-15", 
            end_date="2024-01-16"
        )
        
        if len(articles) == 2:
            print(f"   ✅ Date filtering works: {len(articles)} articles in range")
            return True
        else:
            print(f"   ❌ Date filtering failed: expected 2, got {len(articles)}")
            return False
            
    finally:
        # Clean up
        os.unlink(test_file_path)

def test_date_extraction():
    """Test date extraction from various formats."""
    print("🧪 test_date_extraction: Testing date extraction")
    
    loader = NewsDataLoader()
    
    test_cases = [
        ("2024-01-15", date(2024, 1, 15)),
        ("2024/01/15", date(2024, 1, 15)),
        ("01/15/2024", date(2024, 1, 15)),
        ("invalid_date", None),
        ("", None)
    ]
    
    passed = 0
    for date_str, expected in test_cases:
        result = loader._extract_date(date_str)
        if result == expected:
            passed += 1
        else:
            print(f"   Date extraction failed for '{date_str}': expected {expected}, got {result}")
    
    if passed == len(test_cases):
        print(f"   ✅ All {passed} date extraction tests passed")
        return True
    else:
        print(f"   ❌ {len(test_cases) - passed} date extraction tests failed")
        return False

def test_article_grouping():
    """Test grouping articles by date."""
    print("🧪 test_article_grouping: Testing article grouping")
    
    # Create test file
    test_file_path = create_test_jsonl_file()
    
    try:
        loader = NewsDataLoader()
        articles = loader._parse_jsonl_file(Path(test_file_path))
        
        grouped = loader._group_articles_by_date(articles)
        
        if len(grouped) == 3:  # 3 different dates
            print(f"   ✅ Articles grouped into {len(grouped)} dates")
            
            # Check that each date has the right number of articles
            date_2024_01_15 = date(2024, 1, 15)
            if date_2024_01_15 in grouped and len(grouped[date_2024_01_15]) == 1:
                print("   ✅ Article grouping structure is correct")
                return True
            else:
                print("   ❌ Article grouping structure is incorrect")
                return False
        else:
            print(f"   ❌ Expected 3 dates, got {len(grouped)}")
            return False
            
    finally:
        # Clean up
        os.unlink(test_file_path)

def test_empty_content_handling():
    """Test handling of articles with empty content."""
    print("🧪 test_empty_content_handling: Testing empty content handling")
    
    # Create test data with empty content
    test_data = [
        {
            "Date": "2024-01-15",
            "Url": "https://example.com/article1",
            "Article": "",  # Empty content
            "Stock_symbol": "aa",
            "Article_title": "Empty Article"
        },
        {
            "Date": "2024-01-16",
            "Url": "https://example.com/article2",
            "Article": "Valid content here.",
            "Stock_symbol": "aa",
            "Article_title": "Valid Article"
        }
    ]
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    for item in test_data:
        temp_file.write(json.dumps(item) + '\n')
    temp_file.close()
    
    try:
        loader = NewsDataLoader()
        articles = loader._parse_jsonl_file(Path(temp_file.name))
        
        # Should only get 1 article (the one with valid content)
        if len(articles) == 1:
            print(f"   ✅ Correctly filtered out empty content: {len(articles)} articles")
            return True
        else:
            print(f"   ❌ Expected 1 article, got {len(articles)}")
            return False
            
    finally:
        # Clean up
        os.unlink(temp_file.name)

def test_convenience_function():
    """Test the convenience function load_news_for_ticker."""
    print("🧪 test_convenience_function: Testing convenience function")
    
    # This test will fail if no real news data exists, but that's expected
    try:
        result = load_news_for_ticker("aa", "2024-01-15", "2024-01-16")
        
        if result is None:
            print("   ✅ Convenience function returns None for non-existent data (expected)")
            return True
        else:
            print(f"   ✅ Convenience function returned data: {len(result.articles)} articles")
            return True
            
    except Exception as e:
        print(f"   ❌ Convenience function failed: {e}")
        return False

def run_all():
    """Run all news data loader tests."""
    logger.info("🚀 Running all news data loader tests")
    
    tests = [
        test_news_data_loader_initialization,
        test_jsonl_parsing,
        test_date_filtering,
        test_date_extraction,
        test_article_grouping,
        test_empty_content_handling,
        test_convenience_function
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
    
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    success = run_all()
    exit(0 if success else 1) 