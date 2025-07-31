#!/usr/bin/env python3
"""
Test script for Phase 1 modules (core infrastructure).
Tests the integration between config, date_utils, enums, and data_types.
"""

import sys
from pathlib import Path
import logging

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Set up logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_phase1")

def test_phase1_integration():
    """Test that all Phase 1 modules work together."""
    logger.info("🧪 Testing Phase 1 Integration...")
    
    try:
        # Test config module
        logger.info("1. Testing config module...")
        from core.config import config, DATA_PATH, LLM_MODEL_NAME
        logger.info("   ✅ Config loaded successfully")
        logger.info(f"   📁 Data path: {DATA_PATH}")
        logger.info(f"   🤖 LLM model: {LLM_MODEL_NAME}")
        
        # Test date_utils module
        logger.info("2. Testing date_utils module...")
        from core.date_utils import parse_date, get_backtest_range, align_dates
        from datetime import date
        
        # Test date parsing
        test_date = parse_date("2022-01-15")
        logger.info(f"   ✅ Date parsing: 2022-01-15 -> {test_date}")
        
        # Test backtest range
        backtest_range = get_backtest_range("2022-01-01", "2022-01-31")
        logger.info(f"   ✅ Backtest range: {len(backtest_range['trading_days'])} trading days")
        
        # Test enums module
        logger.info("3. Testing enums module...")
        from core.enums import ExpertType, DataModality, DecisionType, get_expert_types
        
        expert_types = get_expert_types()
        logger.info(f"   ✅ Expert types: {[e.value for e in expert_types]}")
        
        # Test data_types module
        logger.info("4. Testing data_types module...")
        from core.data_types import (
            ExpertOutput, DecisionProbabilities, TradeDecision, 
            PortfolioState, NewsData, PriceData, create_expert_output
        )
        
        # Test creating expert output
        expert_output = create_expert_output([0.3, 0.5, 0.2], "sentiment_expert", 0.8)
        logger.info(f"   ✅ Expert output created: {expert_output.probabilities.to_list()}")
        
        # Test integration between modules
        logger.info("5. Testing module integration...")
        
        # Use config with date_utils
        start_date = config.BACKTEST_START_DATE
        end_date = config.BACKTEST_END_DATE
        backtest_range = get_backtest_range(start_date, end_date)
        logger.info(f"   ✅ Config + Date utils: {len(backtest_range['trading_days'])} trading days")
        
        # Use enums with data_types
        expert_type = ExpertType.SENTIMENT
        decision_type = DecisionType.BUY
        logger.info(f"   ✅ Enums + Data types: {expert_type.value} -> {decision_type.value}")
        
        logger.info("🎉 All Phase 1 modules working correctly!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during Phase 1 testing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_data_structures():
    """Test the data structures and type safety."""
    logger.info("🔧 Testing Data Structures...")
    
    try:
        from core.data_types import (
            DecisionProbabilities, ExpertOutput, PortfolioState,
            NewsData, PriceData, DataCoverage
        )
        from core.enums import ExpertType, DecisionType
        from datetime import date
        
        # Test DecisionProbabilities validation
        logger.info("   Testing DecisionProbabilities...")
        try:
            # This should work
            probs = DecisionProbabilities(0.3, 0.5, 0.2)
            logger.info(f"   ✅ Valid probabilities: {probs.to_list()}")
            
            # This should fail
            try:
                DecisionProbabilities(0.3, 0.5, 0.1)  # Doesn't sum to 1.0
                logger.error("   ❌ Should have failed validation")
            except ValueError:
                logger.info("   ✅ Invalid probabilities correctly rejected")
        except Exception as e:
            logger.error(f"   ❌ DecisionProbabilities error: {e}")
        
        # Test ExpertOutput creation
        logger.info("   Testing ExpertOutput...")
        expert_output = ExpertOutput(
            probabilities=DecisionProbabilities(0.4, 0.4, 0.2),
            confidence=None,  # Will be set by helper function
            metadata=None     # Will be set by helper function
        )
        logger.info(f"   ✅ ExpertOutput created: {expert_output.probabilities.to_list()}")
        
        logger.info("   ✅ All data structures working correctly!")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Data structure error: {e}")
        return False

def test_logging():
    """Test that logging is working correctly."""
    logger.info("📝 Testing Logging Configuration...")
    
    try:
        from core.logging_config import setup_logging, get_logger
        
        # Test logger creation
        test_logger = get_logger("test_module")
        test_logger.info("   ✅ Logger created successfully")
        
        # Test different log levels
        test_logger.debug("   Debug message (should not appear with INFO level)")
        test_logger.info("   Info message")
        test_logger.warning("   Warning message")
        
        logger.info("   ✅ Logging system working correctly!")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Logging error: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Phase 1 Core Infrastructure Testing")
    logger.info("=" * 50)
    
    # Test logging first
    logging_success = test_logging()
    
    # Test integration
    integration_success = test_phase1_integration()
    
    # Test data structures
    data_structures_success = test_data_structures()
    
    # Summary
    logger.info("=" * 50)
    logger.info("📊 Test Summary:")
    logger.info(f"   Logging Tests: {'✅ PASSED' if logging_success else '❌ FAILED'}")
    logger.info(f"   Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    logger.info(f"   Data Structures: {'✅ PASSED' if data_structures_success else '❌ FAILED'}")
    
    if logging_success and integration_success and data_structures_success:
        logger.info("🎉 Phase 1 is ready! Moving to Phase 2...")
        sys.exit(0)
    else:
        logger.error("❌ Phase 1 has issues that need to be fixed.")
        sys.exit(1) 