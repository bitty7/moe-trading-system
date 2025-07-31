#!/usr/bin/env python3
"""
Test runner for the MoE trading system backend.
Runs all tests in the test folder.
"""

import sys
import subprocess
from pathlib import Path
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_runner")

def run_test(test_file: str) -> bool:
    """Run a specific test file in the main test folder."""
    test_path = Path(__file__).parent / test_file
    
    if not test_path.exists():
        logger.error(f"Test file not found: {test_path}")
        return False
    
    logger.info(f"Running test: {test_file}")
    
    try:
        # Set PYTHONPATH to include the backend directory
        env = os.environ.copy()
        backend_dir = str(Path(__file__).parent.parent)
        env['PYTHONPATH'] = backend_dir
        
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env
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

def run_test_in_subfolder(subfolder: str, test_file: str) -> bool:
    """Run a specific test file in a subfolder."""
    test_path = Path(__file__).parent / subfolder / test_file
    
    if not test_path.exists():
        logger.error(f"Test file not found: {test_path}")
        return False
    
    logger.info(f"Running test: {subfolder}/{test_file}")
    
    try:
        # Set PYTHONPATH to include the backend directory
        env = os.environ.copy()
        backend_dir = str(Path(__file__).parent.parent)
        env['PYTHONPATH'] = backend_dir
        
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {subfolder}/{test_file} PASSED")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            logger.error(f"❌ {subfolder}/{test_file} FAILED")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print(result.stdout)
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running {subfolder}/{test_file}: {e}")
        return False

def run_all_tests():
    """Run all test files in the test folder and subfolders."""
    test_folder = Path(__file__).parent
    
    # Find all test files in subfolders
    subfolder_tests = {}
    for subfolder in test_folder.iterdir():
        if subfolder.is_dir() and subfolder.name != "__pycache__":
            test_files = [f for f in subfolder.glob("test_*.py") if f.name != f"run_{subfolder.name}_tests.py"]
            if test_files:
                subfolder_tests[subfolder.name] = test_files
    
    # Find test files in the main test folder
    main_test_files = [f for f in test_folder.glob("test_*.py") if f.name != "run_tests.py"]
    
    if not subfolder_tests and not main_test_files:
        logger.warning("No test files found in test folder or subfolders")
        return True
    
    total_tests = sum(len(files) for files in subfolder_tests.values()) + len(main_test_files)
    logger.info(f"Found {total_tests} test files across {len(subfolder_tests)} subfolders and main folder")
    
    results = {}
    
    # Run subfolder tests
    for subfolder_name, test_files in subfolder_tests.items():
        logger.info(f"\n📁 Running tests in {subfolder_name}/...")
        for test_file in test_files:
            results[f"{subfolder_name}/{test_file.name}"] = run_test_in_subfolder(subfolder_name, test_file.name)
    
    # Run main folder tests
    if main_test_files:
        logger.info(f"\n📁 Running tests in main folder...")
        for test_file in main_test_files:
            results[test_file.name] = run_test(test_file.name)
    
    # Summary
    logger.info("=" * 50)
    logger.info("📊 Test Results Summary:")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_file, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"   {test_file}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return True
    else:
        logger.error(f"❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    logger.info("🚀 MoE Trading System Test Runner")
    logger.info("=" * 50)
    
    success = run_all_tests()
    
    sys.exit(0 if success else 1) 