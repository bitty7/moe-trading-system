# date_utils.py
# Utility functions for date parsing, normalization, and alignment across data modalities.

"""
Date Utilities Implementation

This module provides utility functions for date handling across all data modalities.
It ensures consistent date processing and alignment throughout the system.

RESPONSIBILITIES:

1. DATE PARSING & NORMALIZATION:
   - Parse various date formats from different data sources
   - Convert dates to standard datetime objects
   - Handle timezone conversions and standardization
   - Normalize date strings to consistent format
   - Validate date ranges and chronological order

2. DATE ALIGNMENT ACROSS MODALITIES:
   - Align dates between different data types (news, charts, fundamentals, prices)
   - Handle irregular reporting periods (annual vs quarterly vs daily)
   - Map chart periods (H1/H2) to specific date ranges
   - Create consistent date ranges for analysis
   - Handle missing dates and data gaps
   - Identify and track data availability per ticker and date
   - Provide data coverage analysis and reporting

3. BACKTESTING DATE UTILITIES:
   - Generate date ranges for backtesting periods
   - Handle market holidays and trading days
   - Create rolling windows for analysis
   - Manage date boundaries and transitions
   - Support flexible date range queries

4. DATA QUALITY DATE FUNCTIONS:
   - Detect and handle date inconsistencies
   - Validate date relationships (start < end)
   - Handle future dates and data freshness
   - Process date outliers and anomalies
   - Provide date validation and cleaning
   - Track data availability gaps and missing periods
   - Generate data coverage reports per ticker
   - Handle sparse data scenarios gracefully

5. PERFORMANCE DATE OPTIMIZATIONS:
   - Cache parsed date objects
   - Optimize date range calculations
   - Efficient date filtering and sorting
   - Batch date processing operations
   - Memory-efficient date handling

6. INTEGRATION UTILITIES:
   - Convert between different date formats
   - Provide date formatting for output
   - Handle date serialization for storage
   - Support date comparison operations
   - Enable date arithmetic operations
"""

import re
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional, Set, Union, Any
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from enum import Enum
from core.logging_config import get_logger

# Get logger for this module
logger = get_logger("date_utils")

class DateFormat(Enum):
    """Supported date formats."""
    ISO = "YYYY-MM-DD"
    US = "MM/DD/YYYY"
    EUROPEAN = "DD/MM/YYYY"
    FILENAME = "YYYY_H1"  # For chart filenames like "2022_H1"
    QUARTERLY = "YYYY-Q1"  # For financial periods

@dataclass
class DataCoverage:
    """Data coverage information for a ticker."""
    ticker: str
    available_dates: List[date]
    missing_dates: List[date]
    coverage_percentage: float
    modality: str
    date_range: Tuple[date, date]

@dataclass
class DateAlignment:
    """Result of date alignment across modalities."""
    aligned_dates: List[date]
    modality_coverage: Dict[str, float]
    missing_periods: Dict[str, List[date]]
    alignment_quality: float

class DateUtils:
    """
    Utility class for date handling across all data modalities.
    Ensures consistent date processing and alignment throughout the system.
    """
    
    def __init__(self):
        self._date_cache = {}
        self._alignment_cache = {}
        
    # 1. DATE PARSING & NORMALIZATION
    def parse_date(self, date_str: str, format_hint: Optional[str] = None) -> date:
        """
        Parse various date formats from different data sources.
        
        Args:
            date_str: Date string to parse
            format_hint: Optional hint about the expected format
            
        Returns:
            Parsed date object
            
        Raises:
            ValueError: If date cannot be parsed
        """
        if not date_str:
            raise ValueError("Date string cannot be empty")
        
        # Check cache first
        cache_key = f"{date_str}_{format_hint}"
        if cache_key in self._date_cache:
            return self._date_cache[cache_key]
        
        # Try different parsing strategies
        parsed_date = self._try_parse_date(date_str, format_hint)
        
        # Cache the result
        self._date_cache[cache_key] = parsed_date
        return parsed_date
    
    def _try_parse_date(self, date_str: str, format_hint: Optional[str] = None) -> date:
        """Try multiple date parsing strategies."""
        # Remove common separators and normalize
        normalized = re.sub(r'[_\-\s]', '', date_str.strip())
        
        # Try ISO format first (YYYY-MM-DD)
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass
        
        # Try filename format (YYYY_H1, YYYY_H2)
        if '_H' in date_str:
            try:
                year = int(date_str.split('_')[0])
                half = date_str.split('_')[1]
                if half == 'H1':
                    return date(year, 6, 30)  # End of H1
                elif half == 'H2':
                    return date(year, 12, 31)  # End of H2
            except (ValueError, IndexError):
                logger.debug(f"Failed to parse filename format: {date_str}")
                pass
        
        # Try quarterly format (YYYY-Q1, YYYY-Q2, etc.)
        if '-Q' in date_str:
            try:
                year = int(date_str.split('-')[0])
                quarter = int(date_str.split('-')[1][1])
                month = quarter * 3
                return date(year, month, 1)
            except (ValueError, IndexError):
                logger.debug(f"Failed to parse quarterly format: {date_str}")
                pass
        
        # Try US format (MM/DD/YYYY)
        try:
            return datetime.strptime(date_str, "%m/%d/%Y").date()
        except ValueError:
            pass
        
        # Try YYYY/MM/DD format
        try:
            return datetime.strptime(date_str, "%Y/%m/%d").date()
        except ValueError:
            pass
        
        # Try European format (DD/MM/YYYY)
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            pass
        
        # Try just year (YYYY)
        if len(normalized) == 4 and normalized.isdigit():
            year = int(normalized)
            return date(year, 12, 31)  # End of year
        
        logger.error(f"Unable to parse date: {date_str}")
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def normalize_date(self, date_obj: Union[date, datetime, str]) -> date:
        """Convert dates to standard datetime objects."""
        if isinstance(date_obj, str):
            return self.parse_date(date_obj)
        elif isinstance(date_obj, datetime):
            return date_obj.date()
        elif isinstance(date_obj, date):
            return date_obj
        else:
            raise ValueError(f"Unsupported date type: {type(date_obj)}")
    
    def validate_date_range(self, start_date: date, end_date: date) -> bool:
        """Validate date ranges and chronological order."""
        if start_date > end_date:
            raise ValueError(f"Start date {start_date} cannot be after end date {end_date}")
        
        # Check for reasonable date range (not too far in future/past)
        current_year = datetime.now().year
        if start_date.year < 1900 or end_date.year > current_year + 10:
            raise ValueError(f"Date range {start_date} to {end_date} is outside reasonable bounds")
        
        return True
    
    # 2. DATE ALIGNMENT ACROSS MODALITIES
    def align_dates(self, modality_dates: Dict[str, List[date]], 
                   min_coverage: float = 0.8) -> DateAlignment:
        """
        Align dates between different data types (news, charts, fundamentals, prices).
        
        Args:
            modality_dates: Dictionary mapping modality names to date lists
            min_coverage: Minimum coverage required for alignment
            
        Returns:
            DateAlignment object with aligned dates and coverage info
        """
        if not modality_dates:
            logger.error("No modality dates provided for alignment")
            raise ValueError("No modality dates provided")
        
        # Find common date range
        all_dates = []
        for dates in modality_dates.values():
            all_dates.extend(dates)
        
        if not all_dates:
            logger.error("No dates found in any modality for alignment")
            raise ValueError("No dates found in any modality")
        
        start_date = min(all_dates)
        end_date = max(all_dates)
        
        # Generate full date range
        full_range = self._generate_date_range(start_date, end_date)
        
        # Calculate coverage per modality
        modality_coverage = {}
        missing_periods = {}
        
        for modality, dates in modality_dates.items():
            date_set = set(dates)
            available_in_range = sum(1 for d in full_range if d in date_set)
            coverage = available_in_range / len(full_range) if full_range else 0
            modality_coverage[modality] = coverage
            
            # Find missing periods
            missing = [d for d in full_range if d not in date_set]
            missing_periods[modality] = missing
        
        # Find aligned dates (dates present in all modalities with sufficient coverage)
        aligned_dates = []
        for d in full_range:
            present_in_modalities = sum(1 for dates in modality_dates.values() if d in dates)
            if present_in_modalities / len(modality_dates) >= min_coverage:
                aligned_dates.append(d)
        
        # Calculate overall alignment quality
        alignment_quality = len(aligned_dates) / len(full_range) if full_range else 0
        
        return DateAlignment(
            aligned_dates=aligned_dates,
            modality_coverage=modality_coverage,
            missing_periods=missing_periods,
            alignment_quality=alignment_quality
        )
    
    def map_chart_periods_to_dates(self, chart_periods: List[str]) -> Dict[str, date]:
        """
        Map chart periods (H1/H2) to specific date ranges.
        
        Args:
            chart_periods: List of chart period strings like ["2022_H1", "2022_H2"]
            
        Returns:
            Dictionary mapping period strings to end dates
        """
        period_mapping = {}
        
        for period in chart_periods:
            try:
                parsed_date = self.parse_date(period, format_hint="filename")
                period_mapping[period] = parsed_date
            except ValueError as e:
                logger.warning(f"Could not parse chart period {period}: {e}")
        
        return period_mapping
    
    def handle_irregular_periods(self, dates: List[date], 
                               period_type: str = "daily") -> List[date]:
        """
        Handle irregular reporting periods (annual vs quarterly vs daily).
        
        Args:
            dates: List of dates to process
            period_type: Type of period ("daily", "quarterly", "annual")
            
        Returns:
            Normalized list of dates
        """
        if not dates:
            return []
        
        if period_type == "daily":
            return sorted(dates)
        elif period_type == "quarterly":
            # Group by quarter and take end of quarter
            quarterly_dates = []
            for d in dates:
                quarter_end = date(d.year, ((d.month - 1) // 3 + 1) * 3, 1)
                if quarter_end not in quarterly_dates:
                    quarterly_dates.append(quarter_end)
            return sorted(quarterly_dates)
        elif period_type == "annual":
            # Group by year and take end of year
            annual_dates = []
            for d in dates:
                year_end = date(d.year, 12, 31)
                if year_end not in annual_dates:
                    annual_dates.append(year_end)
            return sorted(annual_dates)
        else:
            raise ValueError(f"Unsupported period type: {period_type}")
    
    # 3. BACKTESTING DATE UTILITIES
    def get_backtest_range(self, start_date: str, end_date: str, 
                          tickers: Optional[List[str]] = None) -> Dict[str, List[date]]:
        """
        Generate date ranges for backtesting periods.
        
        Args:
            start_date: Start date string
            end_date: End date string
            tickers: Optional list of tickers to check data availability
            
        Returns:
            Dictionary with backtest date range and data availability info
        """
        start = self.parse_date(start_date)
        end = self.parse_date(end_date)
        self.validate_date_range(start, end)
        
        # Generate trading days (exclude weekends)
        trading_days = []
        current = start
        while current <= end:
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                trading_days.append(current)
            current += timedelta(days=1)
        
        result = {
            'start_date': start,
            'end_date': end,
            'trading_days': trading_days,
            'total_days': len(trading_days)
        }
        
        # If tickers provided, check data availability
        if tickers:
            result['data_availability'] = self._check_data_availability(tickers, trading_days)
        
        return result
    
    def create_rolling_windows(self, dates: List[date], window_size: int = 30, 
                              step_size: int = 1) -> List[Tuple[date, List[date]]]:
        """
        Create rolling windows for analysis.
        
        Args:
            dates: List of dates to create windows from
            window_size: Size of each window in days
            step_size: Step size between windows
            
        Returns:
            List of tuples (window_end_date, window_dates)
        """
        if len(dates) < window_size:
            return []
        
        windows = []
        for i in range(window_size - 1, len(dates), step_size):
            window_dates = dates[i - window_size + 1:i + 1]
            windows.append((dates[i], window_dates))
        
        return windows
    
    # 4. DATA QUALITY DATE FUNCTIONS
    def detect_date_inconsistencies(self, dates: List[date]) -> List[Dict[str, Any]]:
        """
        Detect and handle date inconsistencies.
        
        Args:
            dates: List of dates to check
            
        Returns:
            List of inconsistency reports
        """
        if not dates:
            return []
        
        sorted_dates = sorted(dates)
        inconsistencies = []
        
        # Check for duplicates
        seen_dates = set()
        for d in sorted_dates:
            if d in seen_dates:
                inconsistencies.append({
                    'type': 'duplicate',
                    'date': d,
                    'message': f'Duplicate date found: {d}'
                })
            seen_dates.add(d)
        
        # Check for gaps
        for i in range(1, len(sorted_dates)):
            gap = (sorted_dates[i] - sorted_dates[i-1]).days
            if gap > 7:  # Gap larger than a week
                inconsistencies.append({
                    'type': 'gap',
                    'start_date': sorted_dates[i-1],
                    'end_date': sorted_dates[i],
                    'gap_days': gap,
                    'message': f'Gap of {gap} days between {sorted_dates[i-1]} and {sorted_dates[i]}'
                })
        
        # Check for future dates
        current_date = datetime.now().date()
        future_dates = [d for d in sorted_dates if d > current_date]
        if future_dates:
            inconsistencies.append({
                'type': 'future_dates',
                'dates': future_dates,
                'message': f'Found {len(future_dates)} future dates'
            })
        
        return inconsistencies
    
    def generate_data_coverage_report(self, ticker: str, 
                                    modality_dates: Dict[str, List[date]]) -> DataCoverage:
        """
        Generate data coverage reports per ticker.
        
        Args:
            ticker: Ticker symbol
            modality_dates: Dictionary mapping modalities to date lists
            
        Returns:
            DataCoverage object with coverage information
        """
        if not modality_dates:
            return DataCoverage(
                ticker=ticker,
                available_dates=[],
                missing_dates=[],
                coverage_percentage=0.0,
                modality="all",
                date_range=(date.today(), date.today())
            )
        
        # Combine all dates
        all_dates = []
        for dates in modality_dates.values():
            all_dates.extend(dates)
        
        if not all_dates:
            return DataCoverage(
                ticker=ticker,
                available_dates=[],
                missing_dates=[],
                coverage_percentage=0.0,
                modality="all",
                date_range=(date.today(), date.today())
            )
        
        # Find date range
        start_date = min(all_dates)
        end_date = max(all_dates)
        
        # Generate full range
        full_range = self._generate_date_range(start_date, end_date)
        available_dates = sorted(list(set(all_dates)))
        missing_dates = [d for d in full_range if d not in available_dates]
        
        coverage_percentage = len(available_dates) / len(full_range) if full_range else 0.0
        
        return DataCoverage(
            ticker=ticker,
            available_dates=available_dates,
            missing_dates=missing_dates,
            coverage_percentage=coverage_percentage,
            modality="all",
            date_range=(start_date, end_date)
        )
    
    def handle_sparse_data(self, dates: List[date], 
                          min_coverage: float = 0.5) -> Tuple[List[date], List[date]]:
        """
        Handle sparse data scenarios gracefully.
        
        Args:
            dates: List of available dates
            min_coverage: Minimum coverage threshold
            
        Returns:
            Tuple of (usable_dates, excluded_dates)
        """
        if not dates:
            return [], []
        
        sorted_dates = sorted(dates)
        start_date = sorted_dates[0]
        end_date = sorted_dates[-1]
        
        # Calculate coverage
        full_range = self._generate_date_range(start_date, end_date)
        coverage = len(sorted_dates) / len(full_range) if full_range else 0.0
        
        if coverage >= min_coverage:
            return sorted_dates, []
        else:
            # Find densest region
            window_size = max(30, len(sorted_dates) // 2)
            best_window = self._find_densest_window(sorted_dates, window_size)
            excluded = [d for d in sorted_dates if d not in best_window]
            return best_window, excluded
    
    # 5. PERFORMANCE DATE OPTIMIZATIONS
    def _generate_date_range(self, start_date: date, end_date: date) -> List[date]:
        """Generate a list of dates from start to end."""
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(days=1)
        return dates
    
    def _find_densest_window(self, dates: List[date], window_size: int) -> List[date]:
        """Find the densest window of dates."""
        if len(dates) <= window_size:
            return dates
        
        best_window = dates[:window_size]
        best_density = len(best_window) / window_size
        
        for i in range(1, len(dates) - window_size + 1):
            window = dates[i:i + window_size]
            density = len(window) / window_size
            if density > best_density:
                best_density = density
                best_window = window
        
        return best_window
    
    def _check_data_availability(self, tickers: List[str], 
                                trading_days: List[date]) -> Dict[str, float]:
        """Check data availability for given tickers and dates."""
        # This would be implemented based on actual data structure
        # For now, return placeholder values
        return {ticker: 0.8 for ticker in tickers}
    
    # 6. INTEGRATION UTILITIES
    def format_date_for_output(self, date_obj: date, format_type: str = "iso") -> str:
        """Convert between different date formats."""
        if format_type == "iso":
            return date_obj.strftime("%Y-%m-%d")
        elif format_type == "us":
            return date_obj.strftime("%m/%d/%Y")
        elif format_type == "european":
            return date_obj.strftime("%d/%m/%Y")
        elif format_type == "filename":
            return date_obj.strftime("%Y_%m_%d")
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def date_arithmetic(self, base_date: date, operation: str, 
                       value: int) -> date:
        """Enable date arithmetic operations."""
        if operation == "add_days":
            return base_date + timedelta(days=value)
        elif operation == "add_weeks":
            return base_date + timedelta(weeks=value)
        elif operation == "add_months":
            # Approximate month addition
            year = base_date.year + (base_date.month + value - 1) // 12
            month = ((base_date.month + value - 1) % 12) + 1
            return date(year, month, min(base_date.day, 28))
        elif operation == "add_years":
            return date(base_date.year + value, base_date.month, base_date.day)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

# Global instance for convenience
date_utils = DateUtils()

# Convenience functions
def parse_date(date_str: str, format_hint: Optional[str] = None) -> date:
    """Parse a date string."""
    return date_utils.parse_date(date_str, format_hint)

def align_dates(modality_dates: Dict[str, List[date]], 
                min_coverage: float = 0.8) -> DateAlignment:
    """Align dates across modalities."""
    return date_utils.align_dates(modality_dates, min_coverage)

def get_backtest_range(start_date: str, end_date: str, 
                      tickers: Optional[List[str]] = None) -> Dict[str, List[date]]:
    """Generate backtest date range."""
    return date_utils.get_backtest_range(start_date, end_date, tickers)

 