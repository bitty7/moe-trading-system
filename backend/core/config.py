# config.py
# Configuration settings and environment variable loading for the backend system.

"""
Configuration Implementation

This module handles all configuration settings and environment variables for the backend system.
It provides centralized configuration management for all components.

RESPONSIBILITIES:

1. ENVIRONMENT VARIABLE LOADING:
   - Load environment variables from .env file using python-dotenv
   - Set default values for missing environment variables
   - Validate required environment variables are present
   - Handle different environment configurations (dev, test, prod)

2. SYSTEM-WIDE CONFIGURATION:
   - Data paths and file locations
   - LLM model configurations (Ollama settings)
   - Database connections (if applicable)
   - Logging configuration and levels
   - Cache settings and memory limits

3. EXPERT-SPECIFIC CONFIGURATIONS:
   - Model parameters for each expert
   - Prompt templates and configurations
   - Confidence thresholds and decision parameters
   - Performance settings (batch sizes, timeouts)

4. DATA PROCESSING CONFIGURATIONS:
   - Date range settings for backtesting
   - Data validation parameters
   - File format specifications
   - Error handling thresholds
   - Missing data handling thresholds and policies
   - Data coverage requirements and minimum thresholds

5. EVALUATION CONFIGURATIONS:
   - Financial metrics parameters
   - Backtesting simulation settings
   - Portfolio configuration (initial capital, position sizing)
   - Transaction cost and slippage settings
   - Cash reserve requirements and minimum thresholds
   - Capital allocation and risk management parameters

6. PERFORMANCE CONFIGURATIONS:
   - Caching settings and TTL values
   - Batch processing parameters
   - Memory usage limits
   - Parallel processing settings
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from dataclasses import dataclass
from core.logging_config import get_logger

# Get logger for this module
logger = get_logger("config")

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    """
    Centralized configuration class for the backend system.
    Handles all environment variables and system settings.
    """
    
    # 1. ENVIRONMENT VARIABLE LOADING
    def __post_init__(self):
        """Validate required environment variables and set defaults."""
        self._validate_required_env_vars()
        self._set_defaults()
    
    def _validate_required_env_vars(self):
        """Validate that required environment variables are present."""
        # Only DATA_PATH is truly required, others have defaults
        required_vars = [
            'DATA_PATH'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        logger.info("All required environment variables validated successfully")
    
    def _set_defaults(self):
        """Set default values for optional environment variables."""
        # System defaults
        if not hasattr(self, 'LOG_LEVEL'):
            self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        if not hasattr(self, 'CACHE_TTL'):
            self.CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour
        
        if not hasattr(self, 'MAX_MEMORY_MB'):
            self.MAX_MEMORY_MB = int(os.getenv('MAX_MEMORY_MB', '2048'))  # 2GB
        
        logger.debug("Default values set for optional environment variables")
    
    # 2. SYSTEM-WIDE CONFIGURATION
    @property
    def DATA_PATH(self) -> Path:
        """Data paths and file locations."""
        return Path(os.getenv('DATA_PATH', '../dataset/HS500-samples'))
    
    @property
    def LLM_MODEL_NAME(self) -> str:
        """LLM model configurations (Ollama settings)."""
        return os.getenv('LLM_MODEL_NAME', 'llama3.1')
    
    @property
    def OLLAMA_BASE_URL(self) -> str:
        """Ollama server URL."""
        return os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    @property
    def LOG_LEVEL(self) -> str:
        """Logging configuration and levels."""
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def CACHE_TTL(self) -> int:
        """Cache settings and memory limits."""
        return int(os.getenv('CACHE_TTL', '3600'))
    
    # Backtesting configuration properties
    @property
    def INITIAL_CAPITAL(self) -> float:
        """Initial capital for backtesting."""
        return float(os.getenv('INITIAL_CAPITAL', '100000'))
    
    @property
    def POSITION_SIZING(self) -> float:
        """Position sizing percentage."""
        return float(os.getenv('POSITION_SIZING', '0.08'))
    
    @property
    def MAX_POSITIONS(self) -> int:
        """Maximum number of positions."""
        return int(os.getenv('MAX_POSITIONS', '10'))
    
    @property
    def CASH_RESERVE(self) -> float:
        """Cash reserve percentage."""
        return float(os.getenv('CASH_RESERVE', '0.2'))
    
    @property
    def MIN_CASH_RESERVE(self) -> float:
        """Minimum cash reserve percentage."""
        return float(os.getenv('MIN_CASH_RESERVE', '0.1'))
    
    @property
    def TRANSACTION_COST(self) -> float:
        """Transaction cost percentage."""
        return float(os.getenv('TRANSACTION_COST', '0.001'))
    
    @property
    def SLIPPAGE(self) -> float:
        """Slippage percentage."""
        return float(os.getenv('SLIPPAGE', '0.0005'))
    
    # 3. EXPERT-SPECIFIC CONFIGURATIONS
    @property
    def EXPERT_CONFIGS(self) -> Dict[str, Dict[str, Any]]:
        """Model parameters for each expert."""
        return {
            'sentiment_expert': {
                'model_name': self.LLM_MODEL_NAME,
                'confidence_threshold': 0.6,
                'max_tokens': 1000,
                'temperature': 0.1,
                'prompt_template': 'sentiment_analysis_prompt.txt'
            },
            'technical_timeseries_expert': {
                'model_name': self.LLM_MODEL_NAME,
                'confidence_threshold': 0.7,
                'max_tokens': 800,
                'temperature': 0.1,
                'lookback_periods': 30,
                'prompt_template': 'technical_analysis_prompt.txt'
            },
            'technical_chart_expert': {
                'model_name': self.LLM_MODEL_NAME,
                'confidence_threshold': 0.65,
                'max_tokens': 1200,
                'temperature': 0.1,
                'image_quality': 'high',
                'prompt_template': 'chart_analysis_prompt.txt'
            },
            'fundamental_expert': {
                'model_name': self.LLM_MODEL_NAME,
                'confidence_threshold': 0.75,
                'max_tokens': 1500,
                'temperature': 0.1,
                'prompt_template': 'fundamental_analysis_prompt.txt'
            }
        }
    
    # 4. DATA PROCESSING CONFIGURATIONS
    @property
    def BACKTEST_START_DATE(self) -> str:
        """Date range settings for backtesting."""
        return os.getenv('BACKTEST_START_DATE', '2008-01-01')
    
    @property
    def BACKTEST_END_DATE(self) -> str:
        """End date for backtesting."""
        return os.getenv('BACKTEST_END_DATE', '2022-12-31')
    
    @property
    def DATA_VALIDATION_CONFIG(self) -> Dict[str, Any]:
        """Data validation parameters."""
        return {
            'min_data_coverage': 0.8,  # Minimum 80% data coverage required
            'max_missing_days': 30,     # Maximum consecutive missing days
            'min_news_articles': 1,     # Minimum news articles per day
            'min_price_points': 20,     # Minimum price data points for analysis
            'min_financial_periods': 4,  # Minimum financial reporting periods
            'min_chart_periods': 2      # Minimum chart periods per year
        }
    
    @property
    def MISSING_DATA_CONFIG(self) -> Dict[str, Any]:
        """Missing data handling thresholds and policies."""
        return {
            'allow_partial_data': True,
            'interpolation_method': 'forward_fill',
            'max_interpolation_gap': 5,  # Max days to interpolate
            'skip_incomplete_tickers': False,
            'warn_on_missing_data': True,
            'log_missing_data': True
        }
    
    @property
    def DATA_COVERAGE_CONFIG(self) -> Dict[str, Any]:
        """Data coverage requirements and minimum thresholds."""
        return {
            'min_ticker_coverage': 0.7,  # Minimum coverage per ticker
            'min_date_coverage': 0.6,    # Minimum coverage per date
            'required_modalities': ['prices', 'news'],  # Must have these
            'optional_modalities': ['charts', 'fundamentals'],  # Nice to have
            'coverage_reporting': True
        }
    
    # 5. EVALUATION CONFIGURATIONS
    @property
    def PORTFOLIO_CONFIG(self) -> Dict[str, Any]:
        """Portfolio configuration (initial capital, position sizing)."""
        return {
            'initial_capital': float(os.getenv('INITIAL_CAPITAL', '100000')),  # $100k
            'position_sizing': float(os.getenv('POSITION_SIZING', '0.1')),     # 10% per position
            'max_positions': int(os.getenv('MAX_POSITIONS', '10')),           # Max 10 positions
            'cash_reserve': float(os.getenv('CASH_RESERVE', '0.2')),          # 20% cash reserve
            'min_cash_reserve': float(os.getenv('MIN_CASH_RESERVE', '0.1')),  # 10% minimum
            'transaction_cost': float(os.getenv('TRANSACTION_COST', '0.001')), # 0.1% per trade
            'slippage': float(os.getenv('SLIPPAGE', '0.0005'))               # 0.05% slippage
        }
    
    @property
    def RISK_MANAGEMENT_CONFIG(self) -> Dict[str, Any]:
        """Capital allocation and risk management parameters."""
        return {
            'max_drawdown_limit': 0.25,    # 25% maximum drawdown
            'stop_loss': 0.15,             # 15% stop loss per position
            'take_profit': 0.30,           # 30% take profit per position
            'max_sector_exposure': 0.4,    # 40% max exposure per sector
            'volatility_target': 0.15,     # 15% target volatility
            'rebalance_frequency': 'monthly'
        }
    
    @property
    def METRICS_CONFIG(self) -> Dict[str, Any]:
        """Financial metrics parameters."""
        return {
            'risk_free_rate': 0.02,        # 2% risk-free rate
            'benchmark': 'SPY',            # S&P 500 as benchmark
            'calculation_frequency': 'daily',
            'rolling_window': 252,         # 1 year rolling window
            'min_periods_for_metrics': 30  # Minimum periods for reliable metrics
        }
    
    # 6. PERFORMANCE CONFIGURATIONS
    @property
    def CACHE_CONFIG(self) -> Dict[str, Any]:
        """Caching settings and TTL values."""
        return {
            'enable_caching': True,
            'cache_ttl': self.CACHE_TTL,
            'max_cache_size_mb': 512,
            'cache_cleanup_interval': 3600,  # 1 hour
            'cacheable_operations': [
                'data_loading',
                'expert_analysis',
                'date_parsing',
                'metrics_calculation'
            ]
        }
    
    @property
    def BATCH_CONFIG(self) -> Dict[str, Any]:
        """Batch processing parameters."""
        return {
            'batch_size': int(os.getenv('BATCH_SIZE', '10')),
            'max_workers': int(os.getenv('MAX_WORKERS', '4')),
            'timeout_seconds': int(os.getenv('TIMEOUT_SECONDS', '30')),
            'retry_attempts': int(os.getenv('RETRY_ATTEMPTS', '3')),
            'parallel_processing': True
        }
    
    @property
    def MEMORY_CONFIG(self) -> Dict[str, Any]:
        """Memory usage limits."""
        return {
            'max_memory_mb': self.MAX_MEMORY_MB,
            'memory_warning_threshold': 0.8,  # 80% of max
            'garbage_collection_frequency': 100,  # Every 100 operations
            'data_cleanup_interval': 3600  # 1 hour
        }

# Global configuration instance
config = Config()

# Convenience access to common configurations
DATA_PATH = config.DATA_PATH
LLM_MODEL_NAME = config.LLM_MODEL_NAME
BACKTEST_START_DATE = config.BACKTEST_START_DATE
PORTFOLIO_CONFIG = config.PORTFOLIO_CONFIG
EXPERT_CONFIGS = config.EXPERT_CONFIGS 