#!/usr/bin/env python3
"""
Run all tests in the aggregation folder.
"""
import sys
from pathlib import Path
import importlib.util

def run_aggregation_tests():
    """Run all aggregation tests."""
    print("🚀 Running aggregation tests")
    print("=" * 40)
    
    # Get the aggregation test directory
    test_dir = Path(__file__).parent
    
    # Find all test files
    test_files = list(test_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found in aggregation folder")
        return False
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        print(f"\n📋 Running {test_file.name}...")
        try:
            # Import and run the test module
            spec = importlib.util.spec_from_file_location(test_file.stem, test_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the module has a run_all_tests function
            if hasattr(module, 'run_all_tests'):
                if module.run_all_tests():
                    passed += 1
                    print(f"✅ {test_file.name} passed")
                else:
                    print(f"❌ {test_file.name} failed")
            else:
                print(f"⚠️  {test_file.name} has no run_all_tests function")
                
        except Exception as e:
            print(f"❌ {test_file.name} failed with error: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Aggregation Test Results: {passed}/{total} test files passed")
    
    if passed == total:
        print("🎉 All aggregation tests passed!")
        return True
    else:
        print("❌ Some aggregation tests failed")
        return False

if __name__ == "__main__":
    run_aggregation_tests() 