#!/usr/bin/env python3
"""
Master test runner for ALL PHASES
Runs the complete test suite from Phase 1 to Phase 7
"""

import sys
import os
import subprocess
import time

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

def run_phase_tests(phase_file, phase_name):
    """Run a phase test file."""
    print(f"\n{'='*80}")
    print(f"{'🚀 ' + phase_name + ' 🚀':^80}")
    print('='*80)
    
    start = time.time()
    result = subprocess.run(
        [sys.executable, phase_file],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True
    )
    duration = time.time() - start
    
    # Show output
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[:500])
    
    success = result.returncode == 0
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"\n{status} - Duration: {duration:.1f}s")
    
    return success

def main():
    """Run all phase tests."""
    print("\n" + "🏆 "*30)
    print("COMPLETE TEST SUITE - ALL PHASES")
    print("🏆 "*30)
    
    start_time = time.time()
    
    phases = [
        ("run_phase1_tests.py", "PHASE 1: Configuration & Setup"),
        ("test_phase2_aggregation.py", "PHASE 2: Aggregation & Weighting"),
        ("test_phase3_logging.py", "PHASE 3: Logging & Metadata"),
        ("test_phase4_entry_point.py", "PHASE 4: Entry Point & Runner"),
        ("test_phase5_expert_alignment.py", "PHASE 5: Expert Alignment"),
        ("test_phase6_cleanup.py", "PHASE 6: Cleanup"),
        ("test_phase7_unit_tests.py", "PHASE 7 Step 1: Unit Tests"),
        ("test_phase7_smoke_test.py", "PHASE 7 Step 2: Smoke Test Validation"),
    ]
    
    results = {}
    for phase_file, phase_name in phases:
        try:
            results[phase_name] = run_phase_tests(phase_file, phase_name)
        except Exception as e:
            print(f"\n❌ {phase_name} CRASHED: {e}")
            results[phase_name] = False
    
    total_duration = time.time() - start_time
    
    # Final Summary
    print("\n" + "="*80)
    print("🏆 FINAL SUMMARY - ALL PHASES")
    print("="*80)
    
    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)
    
    for phase_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {phase_name}")
    
    all_passed = all(results.values())
    
    print(f"\n{'='*80}")
    print(f"Results: {passed_count}/{total_count} phases passed")
    print(f"Total Duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
    print(f"{'='*80}")
    
    if all_passed:
        print("\n" + "🎉 "*30)
        print("ALL PHASES COMPLETE!")
        print("🎉 "*30)
        print("\n✨ The MoE Trading System backend is fully implemented and validated!")
        print("\n📊 System Features:")
        print("   ✅ Entropy-based dynamic weighting")
        print("   ✅ Configurable expert implementations (LLM/pre-trained)")
        print("   ✅ Complete experiment tracking")
        print("   ✅ Robust error handling")
        print("   ✅ Reproducible comparisons")
        print("\n🚀 Ready for:")
        print("   - Thesis/research work")
        print("   - LLM baseline runs")
        print("   - Pre-trained model implementation")
        print("   - Performance comparisons")
    else:
        print("\n" + "⚠️  "*30)
        print(f"SOME PHASES FAILED: {total_count - passed_count} failures")
        print("⚠️  "*30)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

