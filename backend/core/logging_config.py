# logging_config.py
# Centralized logging configuration for the backend system.

"""
Logging Configuration Implementation

This module provides centralized logging configuration for the entire backend system.
It ensures consistent logging across all modules with proper formatting and output handling.

RESPONSIBILITIES:

1. LOGGER SETUP:
   - Create and configure loggers for different modules
   - Set appropriate log levels based on environment
   - Configure log formatting with timestamps and module names
   - Handle logger hierarchy and inheritance

2. OUTPUT HANDLING:
   - Console output for development and debugging
   - File output for production logging
   - Rotating file handlers to manage log file sizes
   - Structured log format for easy parsing

3. LOG LEVEL MANAGEMENT:
   - Environment-based log level configuration
   - Different levels for different environments (dev, test, prod)
   - Dynamic log level adjustment
   - Performance optimization through appropriate log levels

4. MODULE-SPECIFIC LOGGING:
   - Separate loggers for each module
   - Consistent naming convention for loggers
   - Module-specific log formatting
   - Easy identification of log sources
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    module_name: str = "moe_trading"
) -> logging.Logger:
    """
    Set up logging configuration for a module.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        module_name: Name of the module for the logger
        
    Returns:
        Configured logger instance
    """
    # Get log level from config if not provided
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    # Create logger
    logger = logging.getLogger(module_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file provided)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        module_name: Name of the module
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"moe_trading.{module_name}")

# Default logger for core modules
core_logger = get_logger("core") 