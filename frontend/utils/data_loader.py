#!/usr/bin/env python3
"""
Data Loader for MoE Dashboard
Handles loading and processing of backtest data from JSON files.
"""

import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class BacktestDataLoader:
    """Loads and processes backtest data from JSON files."""
    
    def __init__(self, logs_dir: str = "../logs"):
        """
        Initialize the data loader.
        
        Args:
            logs_dir: Path to the logs directory containing backtest results
        """
        self.logs_dir = Path(logs_dir)
        self.logger = logging.getLogger(__name__)
        
        # Ensure logs directory exists
        if not self.logs_dir.exists():
            self.logger.warning(f"Logs directory {self.logs_dir} does not exist")
    
    def get_available_runs(self) -> List[Dict[str, Any]]:
        """
        Get list of available backtest runs.
        
        Returns:
            List of dictionaries containing run information
        """
        runs = []
        
        if not self.logs_dir.exists():
            return runs
        
        for run_dir in self.logs_dir.iterdir():
            if run_dir.is_dir() and run_dir.name.startswith('backtest_'):
                run_info = self._extract_run_info(run_dir)
                if run_info:
                    runs.append(run_info)
        
        # Sort by creation date (newest first)
        runs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return runs
    
    def _extract_run_info(self, run_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Extract basic information about a backtest run.
        
        Args:
            run_dir: Path to the run directory
            
        Returns:
            Dictionary with run information or None if invalid
        """
        try:
            config_file = run_dir / "config.json"
            results_file = run_dir / "results.json"
            
            if not config_file.exists():
                return None
            
            # Load config
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Load results if available
            results = {}
            if results_file.exists():
                with open(results_file, 'r') as f:
                    results = json.load(f)
            
            # Extract run info
            run_info = {
                'id': run_dir.name,
                'start_date': config.get('start_date', 'Unknown'),
                'end_date': config.get('end_date', 'Unknown'),
                'date_range': f"{config.get('start_date', 'Unknown')} to {config.get('end_date', 'Unknown')}",
                'tickers': ', '.join(config.get('tickers', [])),
                'initial_capital': config.get('initial_capital', 0),
                'created_at': config.get('created_at', ''),
                'status': config.get('status', 'unknown'),
                'total_trading_days': config.get('total_trading_days', 0)
            }
            
            # Add results if available
            if results:
                portfolio_metrics = results.get('portfolio_metrics', {})
                run_info.update({
                    'final_value': portfolio_metrics.get('final_value', 0),
                    'total_return': portfolio_metrics.get('total_return', 0),
                    'sharpe_ratio': portfolio_metrics.get('sharpe_ratio', 0),
                    'max_drawdown': portfolio_metrics.get('max_drawdown', 0),
                    'total_trades': portfolio_metrics.get('total_trades', 0)
                })
            
            return run_info
            
        except Exception as e:
            self.logger.error(f"Error extracting run info from {run_dir}: {e}")
            return None
    
    def load_run(self, run_id: str) -> Dict[str, Any]:
        """
        Load complete data for a specific backtest run.
        
        Args:
            run_id: ID of the backtest run
            
        Returns:
            Dictionary containing all run data
        """
        if not run_id:
            raise ValueError("Run ID cannot be None or empty")
            
        run_dir = self.logs_dir / run_id
        
        if not run_dir.exists():
            raise FileNotFoundError(f"Run directory {run_id} not found")
        
        data = {}
        
        # Load config
        config_file = run_dir / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                data['config'] = json.load(f)
        
        # Load portfolio daily data
        portfolio_file = run_dir / "portfolio_daily.json"
        if portfolio_file.exists():
            with open(portfolio_file, 'r') as f:
                data['portfolio_daily'] = json.load(f)
        
        # Load tickers daily data
        tickers_file = run_dir / "tickers_daily.json"
        if tickers_file.exists():
            with open(tickers_file, 'r') as f:
                data['tickers_daily'] = json.load(f)
        
        # Load trades
        trades_file = run_dir / "trades.json"
        if trades_file.exists():
            with open(trades_file, 'r') as f:
                data['trades'] = json.load(f)
        
        # Load results
        results_file = run_dir / "results.json"
        if results_file.exists():
            with open(results_file, 'r') as f:
                data['results'] = json.load(f)
                # Flatten results for easier access
                data['portfolio_metrics'] = data['results'].get('portfolio_metrics', {})
                data['ticker_summary'] = data['results'].get('ticker_summary', {})
        
        return data
    
    def get_portfolio_dataframe(self, run_id: str) -> Optional[pd.DataFrame]:
        """
        Get portfolio daily data as a pandas DataFrame.
        
        Args:
            run_id: ID of the backtest run
            
        Returns:
            DataFrame with portfolio daily data or None if not available
        """
        try:
            data = self.load_run(run_id)
            portfolio_data = data.get('portfolio_daily', [])
            
            if not portfolio_data:
                return None
            
            df = pd.DataFrame(portfolio_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading portfolio data for {run_id}: {e}")
            return None
    
    def get_ticker_dataframe(self, run_id: str, ticker: str) -> Optional[pd.DataFrame]:
        """
        Get daily data for a specific ticker as a pandas DataFrame.
        
        Args:
            run_id: ID of the backtest run
            ticker: Ticker symbol
            
        Returns:
            DataFrame with ticker daily data or None if not available
        """
        try:
            data = self.load_run(run_id)
            tickers_data = data.get('tickers_daily', {})
            
            if ticker not in tickers_data:
                return None
            
            ticker_data = tickers_data[ticker]
            df = pd.DataFrame(ticker_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading ticker data for {ticker} in {run_id}: {e}")
            return None
    
    def get_trades_dataframe(self, run_id: str) -> Optional[pd.DataFrame]:
        """
        Get trades data as a pandas DataFrame.
        
        Args:
            run_id: ID of the backtest run
            
        Returns:
            DataFrame with trades data or None if not available
        """
        try:
            data = self.load_run(run_id)
            trades_data = data.get('trades', [])
            
            if not trades_data:
                return None
            
            df = pd.DataFrame(trades_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading trades data for {run_id}: {e}")
            return None
    
    def get_expert_contributions(self, run_id: str, ticker: str, date: str) -> Dict[str, Any]:
        """
        Get expert contributions for a specific ticker and date.
        
        Args:
            run_id: ID of the backtest run
            ticker: Ticker symbol
            date: Date string (YYYY-MM-DD)
            
        Returns:
            Dictionary with expert contributions
        """
        try:
            df = self.get_ticker_dataframe(run_id, ticker)
            if df is None or date not in df.index:
                return {}
            
            row = df.loc[date]
            return row.get('expert_contributions', {})
            
        except Exception as e:
            self.logger.error(f"Error getting expert contributions: {e}")
            return {}
    
    def get_portfolio_allocation(self, run_id: str, date: str = None) -> Dict[str, float]:
        """
        Get portfolio allocation for a specific date.
        
        Args:
            run_id: ID of the backtest run
            date: Date string (YYYY-MM-DD), if None use latest
            
        Returns:
            Dictionary with allocation percentages
        """
        try:
            df = self.get_portfolio_dataframe(run_id)
            if df is None:
                return {}
            
            if date is None:
                # Use latest date
                row = df.iloc[-1]
            else:
                if date not in df.index:
                    return {}
                row = df.loc[date]
            
            total_value = row['total_value']
            cash = row['cash']
            positions_value = row['positions_value']
            
            allocation = {
                'Cash': cash / total_value if total_value > 0 else 0
            }
            
            # Add individual positions if available
            # This would need to be implemented based on actual data structure
            
            return allocation
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio allocation: {e}")
            return {}
    
    def validate_data_completeness(self, run_id: str) -> Dict[str, bool]:
        """
        Validate that all required data files are present for a run.
        
        Args:
            run_id: ID of the backtest run
            
        Returns:
            Dictionary indicating which files are present
        """
        run_dir = self.logs_dir / run_id
        
        if not run_dir.exists():
            return {'valid': False, 'error': 'Run directory not found'}
        
        required_files = ['config.json', 'portfolio_daily.json', 'tickers_daily.json', 'trades.json', 'results.json']
        
        validation = {'valid': True}
        
        for file_name in required_files:
            file_path = run_dir / file_name
            validation[file_name] = file_path.exists()
            if not file_path.exists():
                validation['valid'] = False
        
        return validation 