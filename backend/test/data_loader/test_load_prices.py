#!/usr/bin/env python3
"""
Tests for the price data loader (load_prices.py).
Covers real data integration and mock edge cases.
"""

import sys
from pathlib import Path
import logging
import tempfile
import pandas as pd

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.logging_config import get_logger
from data_loader.load_prices import load_prices_for_ticker

logger = get_logger("test_load_prices")

def test_real_sample():
    """Test loading a real sample from the dataset."""
    logger.info("🧪 test_real_sample: Loading real OHLCV data for 'aa'")
    data_dir = Path("../dataset/HS500-samples/SP500_time_series")
    df = load_prices_for_ticker("aa", data_dir)
    if df is None:
        logger.error("   ❌ Failed to load real data for 'aa'")
        return False
    logger.info(f"   ✅ Loaded {len(df)} rows for 'aa'")
    logger.info(f"   Columns: {list(df.columns)}")
    # Check required columns
    required = {'date', 'open', 'high', 'low', 'close', 'volume'}
    if not required.issubset(df.columns):
        logger.error(f"   ❌ Missing required columns: {required - set(df.columns)}")
        return False
    return True

def test_missing_file():
    """Test handling of missing file."""
    logger.info("🧪 test_missing_file: Loading non-existent ticker")
    data_dir = Path("../dataset/HS500-samples/SP500_time_series")
    df = load_prices_for_ticker("not_a_ticker", data_dir)
    if df is not None:
        logger.error("   ❌ Should return None for missing file")
        return False
    logger.info("   ✅ Correctly handled missing file")
    return True

def test_mock_csv():
    """Test loading from a mock CSV with missing days."""
    logger.info("🧪 test_mock_csv: Loading from mock CSV with missing days")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        csv_path = tmpdir / "mock.csv"
        # Create a CSV with missing days
        csv_content = """date,open,high,low,close,volume\n2022-01-03,10,12,9,11,1000\n2022-01-05,11,13,10,12,1100\n"""
        csv_path.write_text(csv_content)
        # Patch loader to use this file
        df = load_prices_for_ticker("mock", tmpdir)
        if df is None:
            logger.error("   ❌ Failed to load mock CSV")
            return False
        logger.info(f"   ✅ Loaded {len(df)} rows from mock CSV")
        logger.info(f"   Dates: {list(df['date'])}")
        # Should have at least 3 rows (including the missing 2022-01-04 which gets forward-filled)
        if len(df) >= 3:
            # Check that 2022-01-04 exists and has forward-filled values
            mask = (df['date'] == '2022-01-04')
            if mask.any():
                row = df[mask].iloc[0]
                # Should have forward-filled values (same as 2022-01-03)
                if row['open'] == 10 and row['high'] == 12 and row['low'] == 9 and row['close'] == 11 and row['volume'] == 1000:
                    logger.info("   ✅ Missing day (2022-01-04) handled with forward fill")
                    return True
                else:
                    logger.error(f"   ❌ Row for missing day has unexpected values: {row.to_dict()}")
                    return False
            else:
                logger.error("   ❌ Missing day row not present in DataFrame")
                return False
        else:
            logger.error(f"   ❌ Expected at least 3 rows, got {len(df)}")
            return False

def run_all():
    logger.info("🚀 Running price data loader tests...")
    results = {
        'test_real_sample': test_real_sample(),
        'test_missing_file': test_missing_file(),
        'test_mock_csv': test_mock_csv(),
    }
    logger.info("\n📊 Test Results:")
    for name, result in results.items():
        logger.info(f"   {name}: {'✅ PASSED' if result else '❌ FAILED'}")
    passed = sum(results.values())
    total = len(results)
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    if passed == total:
        logger.info("🎉 All price data loader tests passed!")
        return 0
    else:
        logger.error(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_all()) 