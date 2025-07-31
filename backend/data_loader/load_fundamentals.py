#!/usr/bin/env python3
"""
load_fundamentals.py

Loads fundamental financial data from JSON files containing financial statements.
Handles balance sheets, income statements, cash flow statements, and equity statements.
Parses deeply nested JSON structures and extracts key financial metrics.
Tracks data coverage and missing data for reporting and downstream processing.

RESPONSIBILITIES:
- Read financial statement JSON files for each ticker
- Parse deeply nested JSON structures (company -> filings -> facts -> metrics)
- Extract key financial metrics (revenue, assets, liabilities, etc.)
- Handle missing data and date filtering
- Return clean, structured financial data
- Use logging for errors/warnings

TODO:
- Implement efficient batch loading for multiple tickers
- Add support for different statement types
- Optimize for large datasets
- Add caching for repeated loads
- Integrate with config for data paths
- Add more granular missing data reporting
- Add unit tests for edge cases
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
import pandas as pd

from core.logging_config import get_logger
from core.date_utils import parse_date
from core.data_types import FundamentalData, FinancialStatement, FinancialMetric

logger = get_logger("load_fundamentals")

class FundamentalDataLoader:
    """
    Loads and parses fundamental financial data from JSON files.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the fundamental data loader.
        
        Args:
            data_path (str, optional): Path to the fundamental data directory.
                If None, uses default from config.
        """
        if data_path is None:
            from core.config import config
            self.data_path = Path(config.DATA_PATH) / "SP500_tabular"
        else:
            self.data_path = Path(data_path)
        
        logger.info(f"Fundamental data loader initialized with path: {self.data_path}")
    
    def load_fundamentals_for_ticker(self, ticker: str, start_date: Optional[str] = None, 
                                   end_date: Optional[str] = None) -> Optional[FundamentalData]:
        """
        Load fundamental financial data for a specific ticker within a date range.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AA')
            start_date (str, optional): Start date filter (YYYY-MM-DD)
            end_date (str, optional): End date filter (YYYY-MM-DD)
            
        Returns:
            FinancialData or None: Structured financial data or None if not found
        """
        ticker = ticker.upper()
        ticker_path = self.data_path / ticker.lower()
        
        if not ticker_path.exists():
            logger.warning(f"Fundamental data directory not found for ticker {ticker}: {ticker_path}")
            return None
        
        try:
            logger.info(f"Loading fundamental data for {ticker} from {ticker_path}")
            
            # Load all available statement types
            statements = {}
            
            # Balance Sheet
            balance_sheet_path = ticker_path / "condensed_consolidated_balance_sheets.json"
            if balance_sheet_path.exists():
                balance_sheet = self._load_statement_file(balance_sheet_path, start_date, end_date)
                if balance_sheet is not None:
                    statements['balance_sheet'] = balance_sheet
            
            # Cash Flow Statement
            cash_flow_path = ticker_path / "condensed_consolidated_statement_of_cash_flows.json"
            if cash_flow_path.exists():
                cash_flow = self._load_statement_file(cash_flow_path, start_date, end_date)
                if cash_flow is not None:
                    statements['cash_flow'] = cash_flow
            
            # Equity Statement
            equity_path = ticker_path / "condensed_consolidated_statement_of_equity.json"
            if equity_path.exists():
                equity = self._load_statement_file(equity_path, start_date, end_date)
                if equity is not None:
                    statements['equity'] = equity
            
            if not statements:
                logger.warning(f"No fundamental data files found for {ticker}")
                return None
            
            # Create FundamentalData object
            financial_data = FundamentalData(
                ticker=ticker,
                statements=statements,
                total_statements=len(statements),
                data_quality=self._calculate_data_quality(statements)
            )
            
            logger.info(f"Loaded {len(statements)} statement types for {ticker}")
            return financial_data
            
        except Exception as e:
            logger.error(f"Error loading fundamental data for {ticker}: {e}")
            return None
    
    def _load_statement_file(self, file_path: Path, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> Optional[FinancialStatement]:
        """
        Load and parse a single financial statement file.
        
        Args:
            file_path (Path): Path to the JSON statement file
            start_date (str, optional): Start date filter
            end_date (str, optional): End date filter
            
        Returns:
            FinancialStatement or None: Parsed statement data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract company info
            company_name = data.get('company_name', 'Unknown')
            cik = data.get('cik', 'Unknown')
            filings = data.get('filings', [])
            
            # Filter filings by date if specified
            if start_date or end_date:
                filings = self._filter_filings_by_date(filings, start_date, end_date)
            
            if not filings:
                logger.warning(f"No filings found in date range for {file_path.name}")
                return None
            
            # Extract metrics from filings
            metrics = self._extract_metrics_from_filings(filings)
            
            # Determine statement type from filename
            statement_type = self._determine_statement_type(file_path.name)
            
            return FinancialStatement(
                statement_type=statement_type,
                company_name=company_name,
                cik=cik,
                filings=filings,
                metrics=metrics,
                filing_count=len(filings)
            )
            
        except Exception as e:
            logger.error(f"Error loading statement file {file_path}: {e}")
            return None
    
    def _filter_filings_by_date(self, filings: List[Dict], start_date: Optional[str] = None, 
                               end_date: Optional[str] = None) -> List[Dict]:
        """
        Filter filings by date range.
        
        Args:
            filings (List[Dict]): List of filing dictionaries
            start_date (str, optional): Start date filter
            end_date (str, optional): End date filter
            
        Returns:
            List[Dict]: Filtered filings
        """
        filtered_filings = []
        
        for filing in filings:
            filing_date_str = filing.get('filing_date')
            if not filing_date_str:
                continue
            
            try:
                filing_date = parse_date(filing_date_str)
                
                # Apply date filters
                if start_date and filing_date < parse_date(start_date):
                    continue
                if end_date and filing_date > parse_date(end_date):
                    continue
                
                filtered_filings.append(filing)
                
            except ValueError:
                logger.warning(f"Invalid filing date: {filing_date_str}")
                continue
        
        return filtered_filings
    
    def _extract_metrics_from_filings(self, filings: List[Dict]) -> Dict[str, FinancialMetric]:
        """
        Extract key financial metrics from filings.
        
        Args:
            filings (List[Dict]): List of filing dictionaries
            
        Returns:
            Dict[str, FinancialMetric]: Extracted metrics
        """
        metrics = {}
        
        for filing in filings:
            filing_date = filing.get('filing_date')
            facts = filing.get('facts', {})
            
            # Extract metrics from US-GAAP facts
            us_gaap = facts.get('us-gaap', {})
            
            for metric_name, metric_data in us_gaap.items():
                if isinstance(metric_data, dict) and 'units' in metric_data:
                    units = metric_data['units']
                    
                    # Look for USD values
                    if 'USD' in units:
                        usd_data = units['USD']
                        if isinstance(usd_data, list) and len(usd_data) > 0:
                            # Get the most recent value
                            latest_value = usd_data[0]
                            value = latest_value.get('val', 0)
                            end_date = latest_value.get('end', filing_date)
                            
                            if metric_name not in metrics:
                                metrics[metric_name] = FinancialMetric(
                                    name=metric_name,
                                    values=[],
                                    dates=[],
                                    unit='USD'
                                )
                            
                            metrics[metric_name].values.append(value)
                            metrics[metric_name].dates.append(end_date)
        
        return metrics
    
    def _determine_statement_type(self, filename: str) -> str:
        """
        Determine the type of financial statement from filename.
        
        Args:
            filename (str): Name of the statement file
            
        Returns:
            str: Statement type
        """
        filename_lower = filename.lower()
        
        if 'balance' in filename_lower:
            return 'balance_sheet'
        elif 'cash_flow' in filename_lower or 'cash_flows' in filename_lower:
            return 'cash_flow'
        elif 'equity' in filename_lower:
            return 'equity'
        elif 'income' in filename_lower:
            return 'income'
        else:
            return 'unknown'
    
    def _calculate_data_quality(self, statements: Dict[str, FinancialStatement]) -> float:
        """
        Calculate overall data quality score.
        
        Args:
            statements (Dict[str, FinancialStatement]): Dictionary of statements
            
        Returns:
            float: Data quality score (0.0 to 1.0)
        """
        if not statements:
            return 0.0
        
        total_filings = sum(stmt.filing_count for stmt in statements.values())
        total_metrics = sum(len(stmt.metrics) for stmt in statements.values())
        
        # Simple quality score based on data availability
        quality_score = min(1.0, (total_filings * total_metrics) / 100.0)
        
        return quality_score
    
    def get_fundamental_coverage(self, ticker: str) -> Dict[str, Any]:
        """
        Get fundamental data coverage information for a ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict[str, Any]: Coverage information
        """
        ticker = ticker.upper()
        ticker_path = self.data_path / ticker.lower()
        
        if not ticker_path.exists():
            return {'available': False, 'reason': 'ticker_not_found'}
        
        coverage = {
            'available': True,
            'ticker': ticker,
            'statements': {},
            'total_filings': 0
        }
        
        # Check each statement type
        statement_files = {
            'balance_sheet': 'condensed_consolidated_balance_sheets.json',
            'cash_flow': 'condensed_consolidated_statement_of_cash_flows.json',
            'equity': 'condensed_consolidated_statement_of_equity.json'
        }
        
        for stmt_type, filename in statement_files.items():
            file_path = ticker_path / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    filings_count = len(data.get('filings', []))
                    coverage['statements'][stmt_type] = {
                        'available': True,
                        'filings_count': filings_count
                    }
                    coverage['total_filings'] += filings_count
                except Exception as e:
                    coverage['statements'][stmt_type] = {
                        'available': False,
                        'error': str(e)
                    }
            else:
                coverage['statements'][stmt_type] = {
                    'available': False,
                    'reason': 'file_not_found'
                }
        
        return coverage

def load_fundamentals_for_ticker(ticker: str, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None) -> Optional[FundamentalData]:
    """
    Convenience function to load fundamental data for a ticker.
    
    Args:
        ticker (str): Stock ticker symbol
        start_date (str, optional): Start date filter
        end_date (str, optional): End date filter
        
    Returns:
        FinancialData or None: Fundamental data or None if not available
    """
    loader = FundamentalDataLoader()
    return loader.load_fundamentals_for_ticker(ticker, start_date, end_date) 