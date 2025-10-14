"""
Config Loader for JSON-based Backtester Configuration

This module loads backtester configuration from JSON files (config_llm.json, config_pretrained.json)
and converts them to BacktesterConfig objects for use in the backtesting pipeline.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from core.data_types import BacktesterConfig

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> BacktesterConfig:
    """
    Load backtester configuration from JSON file.
    
    Args:
        config_path: Path to JSON config file (e.g., 'config_llm.json')
        
    Returns:
        BacktesterConfig: Parsed configuration object
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid or missing required fields
        json.JSONDecodeError: If JSON is malformed
    """
    # Resolve path
    config_path = Path(config_path)
    if not config_path.is_absolute():
        # If relative, assume it's relative to backend directory
        backend_dir = Path(__file__).parent.parent
        config_path = backend_dir / config_path
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # Load JSON
    logger.info(f"Loading config from: {config_path}")
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    
    # Validate structure
    _validate_config_structure(config_dict)
    
    # Convert to BacktesterConfig
    backtester_config = _parse_config(config_dict)
    
    logger.info(f"Config loaded successfully: {backtester_config.run_id}")
    return backtester_config


def _validate_config_structure(config_dict: Dict[str, Any]) -> None:
    """
    Validate that config has required sections and fields.
    
    Args:
        config_dict: Parsed JSON config
        
    Raises:
        ValueError: If required sections or fields are missing
    """
    required_sections = ["backtest", "portfolio", "execution", "experts", "aggregation", "logging"]
    missing_sections = [s for s in required_sections if s not in config_dict]
    
    if missing_sections:
        raise ValueError(f"Config missing required sections: {missing_sections}")
    
    # Validate backtest section
    backtest = config_dict["backtest"]
    required_backtest_fields = ["start_date", "end_date", "tickers"]
    missing_fields = [f for f in required_backtest_fields if f not in backtest]
    if missing_fields:
        raise ValueError(f"Backtest section missing required fields: {missing_fields}")
    
    # Validate tickers is not empty
    if not backtest.get("tickers"):
        raise ValueError("Tickers list cannot be empty")
    
    logger.debug("Config structure validation passed")


def _parse_config(config_dict: Dict[str, Any]) -> BacktesterConfig:
    """
    Parse JSON config dict into BacktesterConfig object.
    
    Args:
        config_dict: Parsed JSON config
        
    Returns:
        BacktesterConfig: Configured object
    """
    # Extract sections
    backtest = config_dict["backtest"]
    portfolio = config_dict["portfolio"]
    execution = config_dict["execution"]
    experts = config_dict["experts"]
    aggregation = config_dict["aggregation"]
    logging_config = config_dict["logging"]
    
    # Create BacktesterConfig
    config = BacktesterConfig(
        # Backtest settings
        start_date=backtest["start_date"],
        end_date=backtest["end_date"],
        tickers=backtest["tickers"],
        seed=backtest.get("seed", 42),
        
        # Portfolio settings
        initial_capital=portfolio.get("initial_capital", 100000),
        position_sizing=portfolio.get("position_sizing", 0.15),
        max_positions=portfolio.get("max_positions", 3),
        cash_reserve=portfolio.get("cash_reserve", 0.2),
        min_cash_reserve=portfolio.get("min_cash_reserve", 0.1),
        
        # Execution settings
        transaction_cost=execution.get("transaction_cost", 0.001),
        slippage=execution.get("slippage", 0.0005),
        
        # Expert and aggregation settings
        experts=experts,
        aggregation=aggregation,
        
        # Logging settings
        run_id=logging_config.get("run_id", ""),
        notes=config_dict.get("notes", ""),
        log_level="WARNING"  # Use WARNING for performance
    )
    
    # Generate run_id if not provided
    if not config.run_id:
        # Extract implementation type from first expert
        impl_type = "unknown"
        if experts:
            first_expert = next(iter(experts.values()))
            impl_type = first_expert.get("impl", "unknown")
        
        # Format: backtest_{impl}_{start}_{end}
        start = backtest["start_date"].replace("-", "")
        end = backtest["end_date"].replace("-", "")
        tickers_str = "_".join(backtest["tickers"][:3])  # Max 3 tickers in ID
        config.run_id = f"backtest_{impl_type}_{start}_{end}_{tickers_str}"
    
    return config


def save_config(config: BacktesterConfig, output_path: str) -> None:
    """
    Save BacktesterConfig back to JSON file.
    
    Args:
        config: BacktesterConfig object
        output_path: Path to save JSON file
    """
    config_dict = {
        "backtest": {
            "start_date": config.start_date,
            "end_date": config.end_date,
            "tickers": config.tickers,
            "seed": config.seed
        },
        "portfolio": {
            "initial_capital": config.initial_capital,
            "position_sizing": config.position_sizing,
            "max_positions": config.max_positions,
            "cash_reserve": config.cash_reserve,
            "min_cash_reserve": config.min_cash_reserve
        },
        "execution": {
            "transaction_cost": config.transaction_cost,
            "slippage": config.slippage
        },
        "experts": config.experts,
        "aggregation": config.aggregation,
        "logging": {
            "run_id": config.run_id,
            "log_dir": "backend/logs/"
        },
        "notes": config.notes
    }
    
    with open(output_path, 'w') as f:
        json.dump(config_dict, f, indent=2)
    
    logger.info(f"Config saved to: {output_path}")

