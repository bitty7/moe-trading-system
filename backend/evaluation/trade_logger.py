#!/usr/bin/env python3
"""
Trade Logger Implementation

Records and stores all trading decisions, position changes, and portfolio snapshots
for comprehensive analysis and evaluation.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

from core.data_types import (
    TradeRecord, EvaluationPortfolioState as PortfolioState, DailyMetrics, 
    EvaluationTickerMetrics as TickerMetrics, EvaluationPortfolioMetrics as PortfolioMetrics,
    TradeLoggerConfig, EvaluationBacktestResult as BacktestResult
)

logger = logging.getLogger(__name__)

class TradeLogger:
    """
    Records and stores all trading decisions, portfolio snapshots, and performance metrics.
    """
    
    def __init__(self, config: TradeLoggerConfig):
        """
        Initialize trade logger.
        
        Args:
            config: Trade logger configuration
        """
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage
        self.trade_log: List[TradeRecord] = []
        self.portfolio_snapshots: List[PortfolioState] = []
        self.daily_metrics: List[DailyMetrics] = []
        self.portfolio_metrics: Optional[PortfolioMetrics] = None
        self.ticker_metrics: Dict[str, TickerMetrics] = {}
        
        # Create log files
        self.trade_log_file = self.output_dir / "trade_log.jsonl"
        self.portfolio_file = self.output_dir / "portfolio_snapshots.jsonl"
        self.metrics_file = self.output_dir / "daily_metrics.jsonl"
        self.summary_file = self.output_dir / "backtest_summary.json"
        
        logger.info(f"Trade logger initialized with output directory: {self.output_dir}")
    
    def log_decision(self, date: datetime, ticker: str, action: str, confidence: float,
                    expert_outputs: Dict[str, Any], reasoning: str):
        """
        Log a trading decision.
        
        Args:
            date: Decision date
            ticker: Stock ticker
            action: Trading action (BUY/SELL/HOLD)
            confidence: Expert confidence score
            expert_outputs: Expert outputs
            reasoning: Decision reasoning
        """
        decision_record = {
            "timestamp": date.isoformat(),
            "ticker": ticker,
            "action": action,
            "confidence": confidence,
            "expert_outputs": expert_outputs,
            "reasoning": reasoning
        }
        
        # Append to trade log file
        with open(self.trade_log_file, 'a') as f:
            f.write(json.dumps(decision_record) + '\n')
        
        logger.debug(f"Logged decision: {action} {ticker} (confidence: {confidence:.3f})")
    
    def log_trade(self, trade_record: TradeRecord):
        """
        Log a completed trade.
        
        Args:
            trade_record: Trade record to log
        """
        self.trade_log.append(trade_record)
        
        # Convert to dict for JSON serialization
        trade_dict = {
            "date": trade_record.date.isoformat(),
            "ticker": trade_record.ticker,
            "action": trade_record.action.value,
            "quantity": trade_record.quantity,
            "price": trade_record.price,
            "value": trade_record.value,
            "transaction_cost": trade_record.transaction_cost,
            "slippage": trade_record.slippage,
            "total_cost": trade_record.total_cost,
            "confidence": trade_record.confidence,
            "reasoning": trade_record.reasoning,
            "expert_outputs": trade_record.expert_outputs,
            "success": trade_record.success,
            "error_message": trade_record.error_message,
            "portfolio_value_before": trade_record.portfolio_state_before.total_value,
            "portfolio_value_after": trade_record.portfolio_state_after.total_value,
            "cash_before": trade_record.portfolio_state_before.cash,
            "cash_after": trade_record.portfolio_state_after.cash
        }
        
        # Append to trade log file
        with open(self.trade_log_file, 'a') as f:
            f.write(json.dumps(trade_dict) + '\n')
        
        logger.info(f"Logged trade: {trade_record.action.value} {trade_record.quantity} {trade_record.ticker} at ${trade_record.price:.2f}")
    
    def log_portfolio_snapshot(self, portfolio_state: PortfolioState):
        """
        Log a portfolio snapshot.
        
        Args:
            portfolio_state: Current portfolio state
        """
        self.portfolio_snapshots.append(portfolio_state)
        
        # Convert positions to serializable format
        positions_dict = {}
        for ticker, position in portfolio_state.positions.items():
            positions_dict[ticker] = {
                "quantity": position.quantity,
                "avg_price": position.avg_price,
                "current_price": position.current_price,
                "unrealized_pnl": position.unrealized_pnl,
                "realized_pnl": position.realized_pnl,
                "status": position.status.value
            }
        
        snapshot_dict = {
            "date": portfolio_state.date.isoformat(),
            "total_value": portfolio_state.total_value,
            "cash": portfolio_state.cash,
            "positions": positions_dict,
            "daily_return": portfolio_state.daily_return,
            "total_pnl": portfolio_state.total_pnl,
            "cash_reserve": portfolio_state.cash_reserve,
            "available_capital": portfolio_state.available_capital
        }
        
        # Append to portfolio file
        with open(self.portfolio_file, 'a') as f:
            f.write(json.dumps(snapshot_dict) + '\n')
        
        logger.debug(f"Logged portfolio snapshot: ${portfolio_state.total_value:,.2f} (cash: ${portfolio_state.cash:,.2f})")
    
    def log_daily_metrics(self, daily_metrics: DailyMetrics):
        """
        Log daily performance metrics.
        
        Args:
            daily_metrics: Daily metrics to log
        """
        self.daily_metrics.append(daily_metrics)
        
        metrics_dict = {
            "date": daily_metrics.date.isoformat(),
            "portfolio_value": daily_metrics.portfolio_value,
            "daily_return": daily_metrics.daily_return,
            "cumulative_return": daily_metrics.cumulative_return,
            "cash": daily_metrics.cash,
            "positions_value": daily_metrics.positions_value,
            "total_pnl": daily_metrics.total_pnl,
            "unrealized_pnl": daily_metrics.unrealized_pnl,
            "realized_pnl": daily_metrics.realized_pnl,
            "num_positions": daily_metrics.num_positions,
            "max_drawdown": daily_metrics.max_drawdown,
            "volatility": daily_metrics.volatility,
            "sharpe_ratio": daily_metrics.sharpe_ratio,
            "sortino_ratio": daily_metrics.sortino_ratio
        }
        
        # Append to metrics file
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metrics_dict) + '\n')
        
        logger.debug(f"Logged daily metrics: return={daily_metrics.daily_return:.3%}, value=${daily_metrics.portfolio_value:,.2f}")
    
    def log_data_coverage(self, date: datetime, ticker: str, data_availability: Dict[str, bool]):
        """
        Log data availability for a ticker on a specific date.
        
        Args:
            date: Date
            ticker: Stock ticker
            data_availability: Dict of data type -> availability
        """
        coverage_record = {
            "date": date.isoformat(),
            "ticker": ticker,
            "data_availability": data_availability,
            "timestamp": datetime.now().isoformat()
        }
        
        coverage_file = self.output_dir / "data_coverage.jsonl"
        with open(coverage_file, 'a') as f:
            f.write(json.dumps(coverage_record) + '\n')
    
    def log_error(self, date: datetime, ticker: str, error_type: str, error_message: str, 
                  context: Optional[Dict] = None):
        """
        Log system errors and exceptions.
        
        Args:
            date: Error date
            ticker: Related ticker (if applicable)
            error_type: Type of error
            error_message: Error message
            context: Additional context
        """
        error_record = {
            "date": date.isoformat(),
            "ticker": ticker,
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        error_file = self.output_dir / "errors.jsonl"
        with open(error_file, 'a') as f:
            f.write(json.dumps(error_record) + '\n')
        
        logger.error(f"Logged error: {error_type} for {ticker}: {error_message}")
    
    def save_final_metrics(self, portfolio_metrics: PortfolioMetrics, 
                          ticker_metrics: Dict[str, TickerMetrics]):
        """
        Save final performance metrics.
        
        Args:
            portfolio_metrics: Overall portfolio metrics
            ticker_metrics: Individual ticker metrics
        """
        self.portfolio_metrics = portfolio_metrics
        self.ticker_metrics = ticker_metrics
        
        # Convert metrics to serializable format
        portfolio_dict = {
            "total_return": portfolio_metrics.total_return,
            "annualized_return": portfolio_metrics.annualized_return,
            "sharpe_ratio": portfolio_metrics.sharpe_ratio,
            "sortino_ratio": portfolio_metrics.sortino_ratio,
            "calmar_ratio": portfolio_metrics.calmar_ratio,
            "max_drawdown": portfolio_metrics.max_drawdown,
            "drawdown_duration": portfolio_metrics.drawdown_duration,
            "volatility": portfolio_metrics.volatility,
            "win_rate": portfolio_metrics.win_rate,
            "profit_factor": portfolio_metrics.profit_factor,
            "total_trades": portfolio_metrics.total_trades,
            "avg_trade_return": portfolio_metrics.avg_trade_return,
            "best_trade": portfolio_metrics.best_trade,
            "worst_trade": portfolio_metrics.worst_trade,
            "avg_hold_time": portfolio_metrics.avg_hold_time,
            "cash_drag": portfolio_metrics.cash_drag,
            "diversification_score": portfolio_metrics.diversification_score
        }
        
        ticker_dict = {}
        for ticker, metrics in ticker_metrics.items():
            ticker_dict[ticker] = {
                "total_return": metrics.total_return,
                "annualized_return": metrics.annualized_return,
                "sharpe_ratio": metrics.sharpe_ratio,
                "sortino_ratio": metrics.sortino_ratio,
                "calmar_ratio": metrics.calmar_ratio,
                "max_drawdown": metrics.max_drawdown,
                "drawdown_duration": metrics.drawdown_duration,
                "volatility": metrics.volatility,
                "win_rate": metrics.win_rate,
                "avg_win": metrics.avg_win,
                "avg_loss": metrics.avg_loss,
                "profit_factor": metrics.profit_factor,
                "contribution_to_portfolio": metrics.contribution_to_portfolio,
                "num_trades": metrics.num_trades,
                "avg_hold_time": metrics.avg_hold_time
            }
        
        summary = {
            "portfolio_metrics": portfolio_dict,
            "ticker_metrics": ticker_dict,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save to summary file
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("Saved final performance metrics")
    
    def load_trade_log(self) -> List[Dict]:
        """Load trade log from file."""
        trades = []
        if self.trade_log_file.exists():
            with open(self.trade_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        trades.append(json.loads(line))
        return trades
    
    def load_portfolio_snapshots(self) -> List[Dict]:
        """Load portfolio snapshots from file."""
        snapshots = []
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                for line in f:
                    if line.strip():
                        snapshots.append(json.loads(line))
        return snapshots
    
    def load_daily_metrics(self) -> List[Dict]:
        """Load daily metrics from file."""
        metrics = []
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    if line.strip():
                        metrics.append(json.loads(line))
        return metrics
    
    def generate_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate comprehensive trading report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Trading report
        """
        # Load data
        trades = self.load_trade_log()
        snapshots = self.load_portfolio_snapshots()
        metrics = self.load_daily_metrics()
        
        # Filter by date range
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        filtered_trades = [
            trade for trade in trades 
            if start_dt <= datetime.fromisoformat(trade['date']) <= end_dt
        ]
        
        filtered_snapshots = [
            snapshot for snapshot in snapshots
            if start_dt <= datetime.fromisoformat(snapshot['date']) <= end_dt
        ]
        
        filtered_metrics = [
            metric for metric in metrics
            if start_dt <= datetime.fromisoformat(metric['date']) <= end_dt
        ]
        
        # Calculate summary statistics
        total_trades = len(filtered_trades)
        successful_trades = len([t for t in filtered_trades if t.get('success', True)])
        success_rate = successful_trades / total_trades if total_trades > 0 else 0
        
        buy_trades = len([t for t in filtered_trades if t['action'] == 'BUY'])
        sell_trades = len([t for t in filtered_trades if t['action'] == 'SELL'])
        hold_decisions = len([t for t in filtered_trades if t['action'] == 'HOLD'])
        
        total_volume = sum(t['value'] for t in filtered_trades if t['action'] in ['BUY', 'SELL'])
        total_costs = sum(t['total_cost'] for t in filtered_trades if t['action'] in ['BUY', 'SELL'])
        
        # Portfolio performance
        if filtered_snapshots:
            initial_value = filtered_snapshots[0]['total_value']
            final_value = filtered_snapshots[-1]['total_value']
            total_return = (final_value - initial_value) / initial_value if initial_value > 0 else 0
        else:
            total_return = 0
        
        report = {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "total_days": len(filtered_snapshots)
            },
            "trading_summary": {
                "total_trades": total_trades,
                "successful_trades": successful_trades,
                "success_rate": success_rate,
                "buy_trades": buy_trades,
                "sell_trades": sell_trades,
                "hold_decisions": hold_decisions,
                "total_volume": total_volume,
                "total_costs": total_costs
            },
            "portfolio_performance": {
                "total_return": total_return,
                "total_return_pct": total_return * 100
            },
            "data_summary": {
                "trades_loaded": len(trades),
                "snapshots_loaded": len(snapshots),
                "metrics_loaded": len(metrics)
            }
        }
        
        return report
    
    def export_to_csv(self, output_dir: Optional[str] = None):
        """
        Export log data to CSV files for external analysis.
        
        Args:
            output_dir: Output directory (defaults to config output_dir)
        """
        export_dir = Path(output_dir) if output_dir else self.output_dir / "csv_export"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Export trade log
        trades = self.load_trade_log()
        if trades:
            df_trades = pd.DataFrame(trades)
            df_trades.to_csv(export_dir / "trade_log.csv", index=False)
        
        # Export portfolio snapshots
        snapshots = self.load_portfolio_snapshots()
        if snapshots:
            df_snapshots = pd.DataFrame(snapshots)
            df_snapshots.to_csv(export_dir / "portfolio_snapshots.csv", index=False)
        
        # Export daily metrics
        metrics = self.load_daily_metrics()
        if metrics:
            df_metrics = pd.DataFrame(metrics)
            df_metrics.to_csv(export_dir / "daily_metrics.csv", index=False)
        
        logger.info(f"Exported data to CSV files in {export_dir}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        return {
            "trade_log_entries": len(self.trade_log),
            "portfolio_snapshots": len(self.portfolio_snapshots),
            "daily_metrics": len(self.daily_metrics),
            "output_directory": str(self.output_dir),
            "files_created": [
                str(self.trade_log_file),
                str(self.portfolio_file),
                str(self.metrics_file),
                str(self.summary_file)
            ]
        } 