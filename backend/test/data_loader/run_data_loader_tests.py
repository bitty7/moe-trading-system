#!/usr/bin/env python3
"""
Test runner for the data_loader module tests.
Runs all tests in the data_loader test folder.
"""

import sys
import subprocess
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("data_loader_test_runner")

def run_test(test_file: str) -> bool:
    """Run a specific test file."""
    test_path = Path(__file__).parent / test_file
    
    if not test_path.exists():
        logger.error(f"Test file not found: {test_path}")
        return False
    
    logger.info(f"Running test: {test_file}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent  # Go up to backend directory
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {test_file} PASSED")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            logger.error(f"❌ {test_file} FAILED")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print(result.stdout)
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running {test_file}: {e}")
        return False

def run_data_loader_tests():
    """Run all test files in the data_loader test folder."""
    test_folder = Path(__file__).parent
    test_files = [f for f in test_folder.glob("test_*.py") if f.name != "run_data_loader_tests.py"]
    
    if not test_files:
        logger.warning("No test files found in data_loader test folder")
        return True
    
    logger.info(f"Found {len(test_files)} data_loader test files")
    
    results = {}
    for test_file in test_files:
        results[test_file.name] = run_test(test_file.name)
    
    # Summary
    logger.info("=" * 50)
    logger.info("📊 Data Loader Test Results Summary:")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_file, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"   {test_file}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} data_loader tests passed")
    
    if passed == total:
        logger.info("🎉 All data_loader tests passed!")
        return True
    else:
        logger.error(f"❌ {total - passed} data_loader test(s) failed")
        return False

if __name__ == "__main__":
    logger.info("🚀 Data Loader Module Test Runner")
    logger.info("=" * 50)
    
    success = run_data_loader_tests()
    
    sys.exit(0 if success else 1) 