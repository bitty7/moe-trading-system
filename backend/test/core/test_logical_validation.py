#!/usr/bin/env python3
"""
Logical validation tests for the MoE trading system.
Checks for inconsistencies, illogical results, and edge cases.
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
logger = logging.getLogger("logical_validation")

def test_date_logic():
    """Test date-related logic for consistency."""
    logger.info("📅 Testing Date Logic...")
    
    try:
        from core.date_utils import get_backtest_range, parse_date
        from core.config import config
        from datetime import date
        
        # Test 1: Config dates should be logical
        start_date = parse_date(config.BACKTEST_START_DATE)
        end_date = parse_date(config.BACKTEST_END_DATE)
        
        logger.info(f"   Config start date: {start_date}")
        logger.info(f"   Config end date: {end_date}")
        
        if start_date >= end_date:
            logger.error("   ❌ Start date should be before end date")
            return False
        
        if start_date.year < 1900 or end_date.year > 2030:
            logger.error("   ❌ Date range seems unrealistic")
            return False
        
        # Test 2: Trading days calculation
        backtest_range = get_backtest_range(config.BACKTEST_START_DATE, config.BACKTEST_END_DATE)
        trading_days = len(backtest_range['trading_days'])
        
        logger.info(f"   Total trading days: {trading_days}")
        
        # Calculate expected range
        total_days = (end_date - start_date).days
        expected_trading_days = total_days * 5 // 7  # Rough estimate (5/7 of total days)
        
        logger.info(f"   Total calendar days: {total_days}")
        logger.info(f"   Expected trading days (rough): {expected_trading_days}")
        
        if trading_days < expected_trading_days * 0.8 or trading_days > expected_trading_days * 1.2:
            logger.warning(f"   ⚠️ Trading days ({trading_days}) seems outside expected range ({expected_trading_days})")
        
        # Test 3: Short range test
        short_range = get_backtest_range("2022-01-01", "2022-01-31")
        short_trading_days = len(short_range['trading_days'])
        logger.info(f"   Short range (Jan 2022): {short_trading_days} trading days")
        
        if short_trading_days < 15 or short_trading_days > 25:
            logger.warning(f"   ⚠️ Short range trading days ({short_trading_days}) seems unusual")
        
        logger.info("   ✅ Date logic tests passed")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Date logic error: {e}")
        return False

def test_config_logic():
    """Test configuration logic for consistency."""
    logger.info("⚙️ Testing Configuration Logic...")
    
    try:
        from core.config import config
        
        # Test 1: Portfolio configuration
        portfolio = config.PORTFOLIO_CONFIG
        
        # Check position sizing logic
        if portfolio['position_sizing'] <= 0 or portfolio['position_sizing'] > 1:
            logger.error(f"   ❌ Position sizing should be between 0 and 1, got {portfolio['position_sizing']}")
            return False
        
        # Check cash reserve logic
        if portfolio['cash_reserve'] < portfolio['min_cash_reserve']:
            logger.error(f"   ❌ Cash reserve ({portfolio['cash_reserve']}) should be >= min cash reserve ({portfolio['min_cash_reserve']})")
            return False
        
        # Check max positions logic
        if portfolio['max_positions'] <= 0:
            logger.error(f"   ❌ Max positions should be positive, got {portfolio['max_positions']}")
            return False
        
        # Check if position sizing * max positions makes sense
        max_allocation = portfolio['position_sizing'] * portfolio['max_positions']
        if max_allocation + portfolio['cash_reserve'] > 1.0:
            logger.warning(f"   ⚠️ Total allocation ({max_allocation + portfolio['cash_reserve']:.2%}) exceeds 100%")
        
        logger.info(f"   Position sizing: {portfolio['position_sizing']:.1%}")
        logger.info(f"   Max positions: {portfolio['max_positions']}")
        logger.info(f"   Cash reserve: {portfolio['cash_reserve']:.1%}")
        logger.info(f"   Min cash reserve: {portfolio['min_cash_reserve']:.1%}")
        logger.info(f"   Max allocation: {max_allocation:.1%}")
        
        # Test 2: Risk management configuration
        risk = config.RISK_MANAGEMENT_CONFIG
        
        if risk['stop_loss'] <= 0 or risk['take_profit'] <= 0:
            logger.error("   ❌ Stop loss and take profit should be positive")
            return False
        
        if risk['max_drawdown_limit'] <= 0 or risk['max_drawdown_limit'] > 1:
            logger.error(f"   ❌ Max drawdown should be between 0 and 1, got {risk['max_drawdown_limit']}")
            return False
        
        logger.info(f"   Stop loss: {risk['stop_loss']:.1%}")
        logger.info(f"   Take profit: {risk['take_profit']:.1%}")
        logger.info(f"   Max drawdown: {risk['max_drawdown_limit']:.1%}")
        
        # Test 3: Data validation configuration
        data_val = config.DATA_VALIDATION_CONFIG
        
        if data_val['min_data_coverage'] <= 0 or data_val['min_data_coverage'] > 1:
            logger.error(f"   ❌ Min data coverage should be between 0 and 1, got {data_val['min_data_coverage']}")
            return False
        
        logger.info(f"   Min data coverage: {data_val['min_data_coverage']:.1%}")
        
        logger.info("   ✅ Configuration logic tests passed")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Configuration logic error: {e}")
        return False

def test_data_types_logic():
    """Test data types logic for consistency."""
    logger.info("🏷️ Testing Data Types Logic...")
    
    try:
        from core.data_types import DecisionProbabilities, ExpertOutput, create_expert_output
        from core.enums import DecisionType
        
        # Test 1: Probability validation
        try:
            # Valid probabilities
            probs = DecisionProbabilities(0.3, 0.5, 0.2)
            prob_list = probs.to_list()
            
            if abs(sum(prob_list) - 1.0) > 1e-6:
                logger.error(f"   ❌ Probabilities should sum to 1.0, got {sum(prob_list)}")
                return False
            
            logger.info(f"   Valid probabilities: {prob_list}")
            
            # Invalid probabilities should raise error
            try:
                DecisionProbabilities(0.3, 0.5, 0.1)  # Sum = 0.9
                logger.error("   ❌ Invalid probabilities should raise ValueError")
                return False
            except ValueError:
                logger.info("   ✅ Invalid probabilities correctly rejected")
                
        except Exception as e:
            logger.error(f"   ❌ Probability validation error: {e}")
            return False
        
        # Test 2: Expert output creation
        expert_output = create_expert_output([0.4, 0.4, 0.2], "test_expert", 0.8)
        
        if expert_output.probabilities.buy_probability != 0.4:
            logger.error(f"   ❌ Buy probability should be 0.4, got {expert_output.probabilities.buy_probability}")
            return False
        
        if expert_output.confidence.confidence_score != 0.8:
            logger.error(f"   ❌ Confidence should be 0.8, got {expert_output.confidence.confidence_score}")
            return False
        
        logger.info(f"   Expert output created: {expert_output.probabilities.to_list()}")
        logger.info(f"   Confidence: {expert_output.confidence.confidence_score}")
        
        # Test 3: Enum consistency
        decision_types = [DecisionType.BUY, DecisionType.HOLD, DecisionType.SELL]
        decision_values = [d.value for d in decision_types]
        
        expected_values = ['buy', 'hold', 'sell']
        if decision_values != expected_values:
            logger.error(f"   ❌ Decision types should be {expected_values}, got {decision_values}")
            return False
        
        logger.info(f"   Decision types: {decision_values}")
        
        logger.info("   ✅ Data types logic tests passed")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Data types logic error: {e}")
        return False

def test_expert_config_logic():
    """Test expert configuration logic."""
    logger.info("🤖 Testing Expert Configuration Logic...")
    
    try:
        from core.config import config
        from core.enums import ExpertType, get_expert_types
        
        expert_configs = config.EXPERT_CONFIGS
        expert_types = [e.value for e in get_expert_types()]
        
        # Test 1: All expert types should have configs
        for expert_type in expert_types:
            if expert_type not in expert_configs:
                logger.error(f"   ❌ Missing config for expert type: {expert_type}")
                return False
        
        logger.info(f"   Expert types: {expert_types}")
        
        # Test 2: Config validation for each expert
        for expert_type, config_data in expert_configs.items():
            logger.info(f"   Checking {expert_type}...")
            
            # Check confidence threshold
            if 'confidence_threshold' not in config_data:
                logger.error(f"   ❌ Missing confidence_threshold for {expert_type}")
                return False
            
            conf_threshold = config_data['confidence_threshold']
            if conf_threshold < 0 or conf_threshold > 1:
                logger.error(f"   ❌ Confidence threshold should be between 0 and 1 for {expert_type}, got {conf_threshold}")
                return False
            
            # Check max_tokens
            if 'max_tokens' not in config_data:
                logger.error(f"   ❌ Missing max_tokens for {expert_type}")
                return False
            
            max_tokens = config_data['max_tokens']
            if max_tokens <= 0:
                logger.error(f"   ❌ Max tokens should be positive for {expert_type}, got {max_tokens}")
                return False
            
            # Check temperature
            if 'temperature' not in config_data:
                logger.error(f"   ❌ Missing temperature for {expert_type}")
                return False
            
            temperature = config_data['temperature']
            if temperature < 0 or temperature > 2:
                logger.error(f"   ❌ Temperature should be between 0 and 2 for {expert_type}, got {temperature}")
                return False
            
            logger.info(f"     Confidence: {conf_threshold}, Max tokens: {max_tokens}, Temp: {temperature}")
        
        logger.info("   ✅ Expert configuration logic tests passed")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Expert configuration logic error: {e}")
        return False

def test_performance_logic():
    """Test performance-related logic."""
    logger.info("⚡ Testing Performance Logic...")
    
    try:
        from core.config import config
        
        # Test 1: Memory configuration
        memory_config = config.MEMORY_CONFIG
        
        if memory_config['max_memory_mb'] <= 0:
            logger.error(f"   ❌ Max memory should be positive, got {memory_config['max_memory_mb']}")
            return False
        
        if memory_config['memory_warning_threshold'] <= 0 or memory_config['memory_warning_threshold'] > 1:
            logger.error(f"   ❌ Memory warning threshold should be between 0 and 1, got {memory_config['memory_warning_threshold']}")
            return False
        
        logger.info(f"   Max memory: {memory_config['max_memory_mb']} MB")
        logger.info(f"   Warning threshold: {memory_config['memory_warning_threshold']:.1%}")
        
        # Test 2: Cache configuration
        cache_config = config.CACHE_CONFIG
        
        if cache_config['cache_ttl'] <= 0:
            logger.error(f"   ❌ Cache TTL should be positive, got {cache_config['cache_ttl']}")
            return False
        
        if cache_config['max_cache_size_mb'] <= 0:
            logger.error(f"   ❌ Max cache size should be positive, got {cache_config['max_cache_size_mb']}")
            return False
        
        logger.info(f"   Cache TTL: {cache_config['cache_ttl']} seconds")
        logger.info(f"   Max cache size: {cache_config['max_cache_size_mb']} MB")
        
        # Test 3: Batch configuration
        batch_config = config.BATCH_CONFIG
        
        if batch_config['batch_size'] <= 0:
            logger.error(f"   ❌ Batch size should be positive, got {batch_config['batch_size']}")
            return False
        
        if batch_config['max_workers'] <= 0:
            logger.error(f"   ❌ Max workers should be positive, got {batch_config['max_workers']}")
            return False
        
        logger.info(f"   Batch size: {batch_config['batch_size']}")
        logger.info(f"   Max workers: {batch_config['max_workers']}")
        
        logger.info("   ✅ Performance logic tests passed")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Performance logic error: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔍 Logical Validation Testing")
    logger.info("=" * 50)
    
    # Run all logical validation tests
    tests = [
        ("Date Logic", test_date_logic),
        ("Configuration Logic", test_config_logic),
        ("Data Types Logic", test_data_types_logic),
        ("Expert Configuration Logic", test_expert_config_logic),
        ("Performance Logic", test_performance_logic),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name}...")
        results[test_name] = test_func()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 Logical Validation Summary:")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} logical validation tests passed")
    
    if passed == total:
        logger.info("🎉 All logical validations passed! System is logically consistent.")
        sys.exit(0)
    else:
        logger.error(f"❌ {total - passed} logical validation test(s) failed. Issues need to be addressed.")
        sys.exit(1) 