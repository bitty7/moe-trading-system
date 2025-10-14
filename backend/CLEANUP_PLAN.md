# Final Cleanup Plan

## 🗑️ **Files to REMOVE**

### **Backend Root - Analysis Reports (Temporary):**
- ❌ `DIAGNOSTIC_REPORT.md` - Temporary diagnostic
- ❌ `PHASE_A_ANALYSIS.md` - Temporary phase analysis
- ❌ `PHASE_B_ANALYSIS.md` - Temporary phase analysis
- ❌ `CHANGES.md` - Migration doc (not needed long-term)
- ✅ **KEEP:** `IMPLEMENTATION_SUMMARY.md`, `FULL_YEAR_TEST_ANALYSIS.md`, `USAGE.md`, `README.md`

### **Test Directory - Phase-Specific Tests:**
- ❌ `test_phase1_step1.py` - Implementation test
- ❌ `test_phase1_step2.py` - Implementation test
- ❌ `test_phase2_aggregation.py` - Implementation test
- ❌ `test_phase3_logging.py` - Implementation test
- ❌ `test_phase4_entry_point.py` - Implementation test
- ❌ `test_phase5_expert_alignment.py` - Implementation test
- ❌ `test_phase6_cleanup.py` - Implementation test
- ❌ `test_phase7_unit_tests.py` - Implementation test
- ❌ `test_phase7_smoke_test.py` - Implementation test (functionality now in run_backtest.py)
- ❌ `run_phase1_tests.py` - Implementation test runner
- ❌ `run_phase7_tests.py` - Implementation test runner

### **Test Directory - Old/Debug Tests:**
- ❌ `test_backtesting.py` - Old test
- ❌ `test_daily_metrics.py` - Old test
- ❌ `test_fixes.py` - Old test
- ❌ `test_high_performance.py` - Old test
- ❌ `debug_decision_test.py` - Debug script
- ❌ `debug_expert_decisions.py` - Debug script

### **Test Directory - Temporary Analysis Scripts:**
- ❌ `analyze_decisions.py` - Temporary analysis
- ❌ `analyze_aa_ticker.py` - Temporary analysis (findings documented)

### **Test Logs (Temporary):**
- ❌ `test/logs/*` - All temporary test log folders

### **Empty Directories:**
- ❌ `gating/` - Empty folder
- ❌ `inference/` - Empty folder

---

## ✅ **Files to KEEP**

### **Essential Tests:**
- ✅ `run_all_tests.py` - Master test runner
- ✅ `run_tests.py` - Original test runner
- ✅ `test/core/*` - Core data type tests
- ✅ `test/data_loader/*` - Data loader tests
- ✅ `test/experts/*` - Expert tests
- ✅ `test/aggregation/*` - Aggregation tests
- ✅ `test/evaluation/*` - Evaluation tests

### **Useful Scripts:**
- ✅ `test/view_results.py` - Results viewer (useful for research)

### **Documentation:**
- ✅ `README.md` - Main readme
- ✅ `USAGE.md` - Usage guide
- ✅ `IMPLEMENTATION_SUMMARY.md` - Complete overview
- ✅ `FULL_YEAR_TEST_ANALYSIS.md` - Test results

### **Configs:**
- ✅ `config_llm.json` - LLM baseline
- ✅ `config_pretrained.json` - Pre-trained template
- ✅ `config_smoke_test.json` - Quick test
- ✅ `config_full_test.json` - Full year test

---

## 📊 **Summary**

**Remove:**
- 21 phase-specific test files
- 6 old/debug test files
- 2 temporary analysis scripts
- 4 temporary analysis docs
- Test log folders
- 2 empty directories

**Keep:**
- 4 essential docs
- 4 config files
- Core/data_loader/expert/evaluation tests (functional tests)
- Master test runners
- Results viewer

**Result:** Clean, research-focused codebase with only essential files.

