"""
Performance Logging System for MoE Trading Backtesting Engine.

This module provides comprehensive logging capabilities to capture all performance data,
decisions, and metrics for a single backtest run to enable frontend visualization
without requiring re-execution of the backtest.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import logging

from core.data_types import (
    EvaluationPortfolioState as PortfolioState, TradeRecord, EvaluationPortfolioMetrics as PortfolioMetrics, 
    EvaluationTickerMetrics as TickerMetrics, BacktesterConfig
)
from aggregation.expert_aggregator import AggregationResult

logger = logging.getLogger(__name__)


class PerformanceLogger:
    """
    Comprehensive performance logger for backtesting results.
    
    Captures all performance data, decisions, and metrics for a single backtest run
    to enable frontend visualization without requiring re-execution.
    """
    
    def __init__(self, backtest_id: str, config: BacktesterConfig):
        """
        Initialize the performance logger.
        
        Args:
            backtest_id: Unique identifier for the backtest run
            config: Backtester configuration
        """
        self.backtest_id = backtest_id
        self.config = config
        self.log_dir = f"logs/{backtest_id}"
        
        # Initialize data storage
        self.portfolio_daily_data: List[Dict] = []
        self.tickers_daily_data: Dict[str, List[Dict]] = {}
        self.trades_data: List[Dict] = []
        
        # Create log directory
        self._create_log_directory()
        
        # Save initial configuration
        self._save_config()
        
        logger.info(f"Performance logger initialized for backtest: {backtest_id}")
    
    def _create_log_directory(self):
        """Create the log directory structure."""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            logger.debug(f"Created log directory: {self.log_dir}")
        except Exception as e:
            logger.error(f"Failed to create log directory {self.log_dir}: {e}")
            raise
    
    def _save_config(self):
        """Save backtest configuration and metadata."""
        config_data = {
            "backtest_id": self.backtest_id,
            "start_date": self.config.start_date,
            "end_date": self.config.end_date,
            "initial_capital": self.config.initial_capital,
            "position_sizing": self.config.position_sizing,
            "max_positions": self.config.max_positions,
            "cash_reserve": self.config.cash_reserve,
            "min_cash_reserve": self.config.min_cash_reserve,
            "transaction_cost": self.config.transaction_cost,
            "slippage": self.config.slippage,
            "tickers": self.config.tickers,
            "created_at": datetime.now().isoformat(),
            "status": "running"
        }
        
        self._write_json_file("config.json", config_data)
        logger.debug("Saved backtest configuration")
    
    def log_daily_portfolio(self, date: datetime, portfolio_state: PortfolioState):
        """
        Log daily portfolio performance.
        
        Args:
            date: Trading date
            portfolio_state: Current portfolio state
        """
        daily_data = {
            "date": date.strftime("%Y-%m-%d"),
            "total_value": portfolio_state.total_value,
            "cash": portfolio_state.cash,
            "positions_value": portfolio_state.total_value - portfolio_state.cash,
            "daily_return": portfolio_state.daily_return,
            "cumulative_return": self._calculate_cumulative_return(portfolio_state),
            "num_positions": len(portfolio_state.positions),
            "cash_reserve": portfolio_state.cash_reserve,
            "available_capital": portfolio_state.available_capital
        }
        
        self.portfolio_daily_data.append(daily_data)
        logger.debug(f"Logged portfolio data for {date.strftime('%Y-%m-%d')}")
    
    def log_daily_ticker(self, date: datetime, ticker: str, price: float,
                        aggregation_result: AggregationResult, position: Optional[Dict] = None):
        """
        Log daily ticker performance and expert decisions.
        
        Args:
            date: Trading date
            ticker: Stock ticker
            price: Current stock price
            aggregation_result: Expert aggregation result
            position: Current position data (if any)
        """
        # Initialize ticker data if not exists
        if ticker not in self.tickers_daily_data:
            self.tickers_daily_data[ticker] = []
        
        # Extract expert contributions
        expert_contributions = {}
        for expert_name, contribution in aggregation_result.expert_contributions.items():
            expert_contributions[expert_name] = {
                "weight": contribution.weight,
                "confidence": contribution.expert_output.confidence.confidence_score,
                "probabilities": contribution.expert_output.probabilities.to_list(),
                "reasoning": contribution.expert_output.confidence.metadata.get("reasoning", "No reasoning provided")
            }
        
        ticker_data = {
            "date": date.strftime("%Y-%m-%d"),
            "price": price,
            "decision": aggregation_result.decision_type.value,
            "overall_confidence": aggregation_result.overall_confidence,
            "expert_contributions": expert_contributions,
            "final_probabilities": aggregation_result.final_probabilities.to_list(),
            "reasoning": aggregation_result.reasoning,
            "position": position
        }
        
        self.tickers_daily_data[ticker].append(ticker_data)
        logger.debug(f"Logged ticker data for {ticker} on {date.strftime('%Y-%m-%d')}")
    
    def log_trade(self, trade_record: TradeRecord):
        """
        Log trade execution details.
        
        Args:
            trade_record: Trade record to log
        """
        # Extract expert contributions for trade
        expert_contributions = {}
        if hasattr(trade_record, 'expert_outputs') and trade_record.expert_outputs:
            for expert_name, expert_data in trade_record.expert_outputs.items():
                if isinstance(expert_data, dict) and 'confidence' in expert_data:
                    expert_contributions[expert_name] = {
                        "weight": expert_data.get("weight", 0.25),  # Default weight
                        "confidence": expert_data.get("confidence", 0.5)
                    }
        
        trade_data = {
            "trade_id": f"trade_{len(self.trades_data) + 1:03d}",
            "date": trade_record.date.strftime("%Y-%m-%d"),
            "ticker": trade_record.ticker,
            "action": trade_record.action.value,
            "quantity": trade_record.quantity,
            "price": trade_record.price,
            "value": trade_record.value,
            "transaction_cost": trade_record.transaction_cost,
            "slippage": trade_record.slippage,
            "total_cost": trade_record.total_cost,
            "overall_confidence": trade_record.confidence,
            "expert_contributions": expert_contributions,
            "reasoning": trade_record.reasoning,
            "success": trade_record.success,
            "portfolio_before": {
                "total_value": trade_record.portfolio_state_before.total_value,
                "cash": trade_record.portfolio_state_before.cash,
                "positions_value": trade_record.portfolio_state_before.total_value - trade_record.portfolio_state_before.cash
            },
            "portfolio_after": {
                "total_value": trade_record.portfolio_state_after.total_value,
                "cash": trade_record.portfolio_state_after.cash,
                "positions_value": trade_record.portfolio_state_after.total_value - trade_record.portfolio_state_after.cash
            }
        }
        
        self.trades_data.append(trade_data)
        logger.debug(f"Logged trade: {trade_data['trade_id']} for {trade_record.ticker}")
    
    def save_final_results(self, portfolio_metrics: PortfolioMetrics, 
                          ticker_metrics: Dict[str, TickerMetrics]):
        """
        Save final backtest results and complete the logging.
        
        Args:
            portfolio_metrics: Final portfolio performance metrics
            ticker_metrics: Final ticker-specific metrics
        """
        # Update config status
        self._update_config_status("completed")
        
        # Save all daily data
        self._save_portfolio_daily()
        self._save_tickers_daily()
        self._save_trades()
        
        # Save final results
        self._save_final_results(portfolio_metrics, ticker_metrics)
        
        logger.info(f"Completed performance logging for backtest: {self.backtest_id}")
    
    def _calculate_cumulative_return(self, portfolio_state: PortfolioState) -> float:
        """Calculate cumulative return from portfolio state."""
        if len(self.portfolio_daily_data) == 0:
            return 0.0
        
        initial_value = self.config.initial_capital
        current_value = portfolio_state.total_value
        return (current_value - initial_value) / initial_value
    
    def _update_config_status(self, status: str):
        """Update the status in config file."""
        config_file = os.path.join(self.log_dir, "config.json")
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            config_data["status"] = status
            config_data["completed_at"] = datetime.now().isoformat()
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update config status: {e}")
    
    def _write_json_file(self, filename: str, data: Any):
        """Write data to JSON file."""
        filepath = os.path.join(self.log_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write {filename}: {e}")
            raise
    
    def _save_portfolio_daily(self):
        """Save daily portfolio performance data."""
        self._write_json_file("portfolio_daily.json", self.portfolio_daily_data)
        logger.debug(f"Saved portfolio daily data: {len(self.portfolio_daily_data)} records")
    
    def _save_tickers_daily(self):
        """Save daily ticker performance data."""
        self._write_json_file("tickers_daily.json", self.tickers_daily_data)
        logger.debug(f"Saved tickers daily data for {len(self.tickers_daily_data)} tickers")
    
    def _save_trades(self):
        """Save trade history data."""
        self._write_json_file("trades.json", self.trades_data)
        logger.debug(f"Saved trade data: {len(self.trades_data)} trades")
    
    def _save_final_results(self, portfolio_metrics: PortfolioMetrics, 
                           ticker_metrics: Dict[str, TickerMetrics]):
        """Save final results summary."""
        # Convert portfolio metrics to dict
        portfolio_dict = asdict(portfolio_metrics)
        
        # Convert ticker metrics to dict
        ticker_dict = {}
        for ticker, metrics in ticker_metrics.items():
            ticker_dict[ticker] = asdict(metrics)
        
        results_data = {
            "portfolio_metrics": portfolio_dict,
            "ticker_summary": ticker_dict
        }
        
        self._write_json_file("results.json", results_data)
        logger.debug("Saved final results summary") 