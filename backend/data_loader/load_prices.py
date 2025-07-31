"""
load_prices.py

Loads OHLCV (Open, High, Low, Close, Volume) time series data for a given ticker from CSV files.
Handles missing days, fills gaps, and provides clean, chronologically ordered data.
Tracks data coverage and missing data for reporting and downstream processing.

RESPONSIBILITIES:
- Read OHLCV CSV files for each ticker
- Handle missing days (insert None/NaN for missing dates)
- Return clean, chronologically ordered time series for each ticker
- Track and report data coverage and missing data
- Use logging for errors/warnings

TODO:
- Implement efficient batch loading for multiple tickers
- Add support for different file formats (if needed)
- Optimize for large datasets
- Add caching for repeated loads
- Integrate with config for data paths
- Add more granular missing data reporting
- Add unit tests for edge cases
"""

import logging
from pathlib import Path
import pandas as pd
from typing import Optional, Dict, Any
from core.logging_config import get_logger

logger = get_logger("load_prices")

def load_prices_for_ticker(ticker: str, data_dir: Optional[Path] = None) -> Optional[pd.DataFrame]:
    """
    Load OHLCV time series data for a given ticker from CSV.
    Handles missing days and returns a clean, chronologically ordered DataFrame.
    Logs missing data and coverage.

    Args:
        ticker (str): The ticker symbol (e.g., 'aa', 'aacg')
        data_dir (Optional[Path]): Directory containing the CSV files. If None, uses default from config.

    Returns:
        Optional[pd.DataFrame]: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
            and a row for each trading day (missing days filled with NaN/None).
            Returns None if file not found or error occurs.
    """
    try:
        # Use config.DATA_PATH if data_dir is None
        if data_dir is None:
            from core.config import config
            data_dir = config.DATA_PATH / "SP500_time_series"
        else:
            data_dir = Path(data_dir)
        csv_path = data_dir / f"{ticker}.csv"
        if not csv_path.exists():
            logger.warning(f"Price file not found for ticker '{ticker}': {csv_path}")
            return None
        # Read CSV
        df = pd.read_csv(csv_path)
        # Normalize columns
        col_map = {c.lower(): c for c in df.columns}
        required = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required if col not in [c.lower() for c in df.columns]]
        if missing:
            logger.error(f"Missing required columns in {csv_path}: {missing}")
            return None
        # Select and rename columns
        df = df[[col_map['date'], col_map['open'], col_map['high'], col_map['low'], col_map['close'], col_map['volume']]].copy()
        df.columns = required
        # Parse date
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Remove timezone from all dates (force naive)
        if pd.api.types.is_datetime64tz_dtype(df['date']):
            df['date'] = df['date'].dt.tz_localize(None)
        else:
            # If any timezone-aware values are present, convert all to naive
            df['date'] = df['date'].apply(lambda d: d.tz_localize(None) if hasattr(d, 'tz_localize') and d.tzinfo is not None else d)
        
        logger.debug(f"Date dtype after tz removal: {df['date'].dtype}")
        
        # Remove any rows with invalid dates
        df = df.dropna(subset=['date'])
        
        if df.empty:
            logger.error(f"No valid dates found for ticker '{ticker}'")
            return None
        
        df = df.sort_values('date').reset_index(drop=True)
        
        # Fill missing days - but only for business days that actually have data
        min_date = df['date'].min()
        max_date = df['date'].max()
        logger.debug(f"min_date: {min_date}, max_date: {max_date}")
        
        # Create business day range
        all_days = pd.date_range(min_date, max_date, freq='B')  # Business days
        
        # Reindex and fill missing values with forward fill for OHLCV data
        df_reindexed = df.set_index('date').reindex(all_days)
        
        # Forward fill OHLCV data (this is more realistic than leaving NaN)
        df_reindexed = df_reindexed.ffill()
        
        # Reset index to get date column back
        df_reindexed = df_reindexed.reset_index()
        df_reindexed = df_reindexed.rename(columns={'index': 'date'})
        
        # After reindexing, ensure 'date' is datetime
        df_reindexed['date'] = pd.to_datetime(df_reindexed['date'], errors='coerce')
        
        # Remove any rows that still have invalid dates
        df_reindexed = df_reindexed.dropna(subset=['date'])
        
        # Output 'date' as string (YYYY-MM-DD)
        df_reindexed['date'] = df_reindexed['date'].dt.strftime('%Y-%m-%d')
        
        # Log missing data - count actual missing OHLCV data, not just dates
        n_missing = df_reindexed[['open', 'high', 'low', 'close', 'volume']].isnull().any(axis=1).sum()
        coverage = 1 - n_missing / len(df_reindexed) if len(df_reindexed) > 0 else 0
        logger.info(f"Loaded {len(df_reindexed)} rows for '{ticker}'. Data coverage: {coverage:.1%}. Missing days: {n_missing}")
        
        if n_missing > 0:
            logger.warning(f"Ticker '{ticker}' has {n_missing} missing trading days in price data.")
        
        return df_reindexed
    except Exception as e:
        logger.error(f"Error loading prices for ticker '{ticker}': {e}")
        return None 