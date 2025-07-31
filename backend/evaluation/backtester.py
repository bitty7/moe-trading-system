#!/usr/bin/env python3
"""
High-performance backtesting engine for the MoE trading system.
Optimized for EC2 instances with reduced logging and batch processing.
"""

# Set up minimal logging for performance - WARNING level for all modules
import logging
logging.basicConfig(level=logging.WARNING)  # Only warnings and errors for speed

# Set all moe_trading loggers to WARNING level to reduce debug output
logging.getLogger('moe_trading').setLevel(logging.WARNING)
logging.getLogger('moe_trading.expert_aggregator').setLevel(logging.WARNING)
logging.getLogger('moe_trading.sentiment_expert').setLevel(logging.WARNING)
logging.getLogger('moe_trading.technical_timeseries_expert').setLevel(logging.WARNING)
logging.getLogger('moe_trading.fundamental_expert').setLevel(logging.WARNING)
logging.getLogger('moe_trading.chart_expert').setLevel(logging.WARNING)
logging.getLogger('moe_trading.load_news').setLevel(logging.WARNING)
logging.getLogger('moe_trading.load_prices').setLevel(logging.WARNING)
logging.getLogger('moe_trading.load_fundamentals').setLevel(logging.WARNING)
logging.getLogger('moe_trading.load_charts').setLevel(logging.WARNING)
logging.getLogger('moe_trading.llm_client').setLevel(logging.WARNING)
logging.getLogger('evaluation').setLevel(logging.WARNING)
logging.getLogger('evaluation.portfolio_simulator').setLevel(logging.WARNING)
logging.getLogger('evaluation.performance_logger').setLevel(logging.WARNING)
logging.getLogger('evaluation.trade_logger').setLevel(logging.WARNING)
logging.getLogger('evaluation.metrics').setLevel(logging.WARNING)

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_types import (
    BacktesterConfig, EvaluationPortfolioState as PortfolioState, TradeRecord, 
    EvaluationPortfolioMetrics as PortfolioMetrics, EvaluationTickerMetrics as TickerMetrics,
    TradeAction, DecisionType
)
from aggregation.expert_aggregator import aggregate_experts
from data_loader.load_prices import load_prices_for_ticker
from .portfolio_simulator import PortfolioSimulator
from .trade_logger import TradeLogger
from .metrics import MetricsCalculator
from .performance_logger import PerformanceLogger

logger = logging.getLogger(__name__)

class HighPerformanceBacktester:
    """
    High-performance backtesting engine optimized for EC2 instances.
    Features:
    - Minimal logging for maximum speed
    - Batch processing
    - Memory optimization
    - Progress tracking without console spam
    """
    
    def __init__(self, config: BacktesterConfig):
        self.config = config
        
        # Initialize components with minimal logging
        portfolio_config = PortfolioSimulatorConfig(
            initial_capital=config.initial_capital,
            position_sizing=config.position_sizing,
            max_positions=config.max_positions,
            cash_reserve=config.cash_reserve,
            min_cash_reserve=config.min_cash_reserve,
            transaction_cost=config.transaction_cost,
            slippage=config.slippage
        )
        
        # Generate backtest ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tickers_str = "_".join(config.tickers)
        self.backtest_id = f"backtest_{timestamp}_{tickers_str}"
        
        # Use the same folder for both loggers
        backtest_folder = f"logs/{self.backtest_id}"

        trade_logger_config = TradeLoggerConfig(
            output_dir=backtest_folder,
            log_level="WARNING"  # Minimal logging
        )
        
        self.portfolio_simulator = PortfolioSimulator(portfolio_config)
        self.trade_logger = TradeLogger(trade_logger_config)
        self.metrics_calculator = MetricsCalculator()
        self.performance_logger = PerformanceLogger(self.backtest_id, config)
        
        # Performance tracking
        self.portfolio_history = []
        self.trade_log = []
        self.total_decisions = 0
        self.successful_decisions = 0
        
        # Progress tracking (minimal)
        self.start_time = None
        self.last_progress_time = None
        self.progress_interval = 100  # Show progress every 100 days
        
        logger.warning(f"High-performance backtester initialized for {len(config.tickers)} tickers")

    def run_backtest(self) -> 'EvaluationBacktestResult':
        """Run the high-performance backtest."""
        self.start_time = datetime.now()
        logger.warning("🚀 Starting high-performance backtest...")
        
        try:
            # Load all price data upfront for better performance
            self.price_data = {}
            for ticker in self.config.tickers:
                data = load_prices_for_ticker(ticker)
                if data is not None:
                    # Convert date column back to datetime before setting as index
                    data['date'] = pd.to_datetime(data['date'])
                    self.price_data[ticker] = data.set_index('date')
                else:
                    logger.error(f"Failed to load price data for {ticker}")
                    return None
            
            # Get trading dates from the longest dataset
            all_dates = set()
            for ticker_data in self.price_data.values():
                all_dates.update(ticker_data.index)
            
            trading_dates = sorted(list(all_dates))
            start_date = pd.to_datetime(self.config.start_date)
            end_date = pd.to_datetime(self.config.end_date)
            # Convert all dates to pandas Timestamp for consistent comparison
            trading_dates = [pd.to_datetime(d) for d in trading_dates 
                           if start_date <= pd.to_datetime(d) <= end_date]
            
            logger.warning(f"Processing {len(trading_dates)} trading days")
            
            # Initialize portfolio
            initial_state = PortfolioState(
                total_value=self.config.initial_capital,
                cash=self.config.initial_capital,
                positions={},
                date=trading_dates[0],
                daily_return=0.0
            )
            self.portfolio_simulator.reset(initial_state)
            self.portfolio_history.append(initial_state)
            
            # Process each trading day
            for i, current_date in enumerate(trading_dates):
                # Progress tracking (minimal)
                if i % self.progress_interval == 0:
                    elapsed = (datetime.now() - self.start_time).total_seconds()
                    rate = i / elapsed if elapsed > 0 else 0
                    eta = (len(trading_dates) - i) / rate if rate > 0 else 0
                    logger.warning(f"Progress: {i}/{len(trading_dates)} days ({i/len(trading_dates)*100:.1f}%) - ETA: {eta/3600:.1f}h")
                
                # Process each ticker
                for ticker in self.config.tickers:
                    if ticker in self.price_data:
                        # Convert current_date to pandas Timestamp for proper comparison
                        current_date_ts = pd.Timestamp(current_date)
                        if current_date_ts in self.price_data[ticker].index:
                            current_price = self.price_data[ticker].loc[current_date_ts, 'close']
                            if pd.notna(current_price) and current_price > 0:
                                self._process_ticker_optimized(ticker, current_date, current_price)
                
                # Calculate daily metrics (every day for updated metrics against current prices)
                self._calculate_daily_metrics_optimized(current_date)
            
            # Calculate final metrics
            final_metrics = self._calculate_final_metrics()
            
            # Save results
            self.performance_logger.save_final_results(
                final_metrics['portfolio_metrics'],
                final_metrics['ticker_metrics']
            )
            
            # Calculate success rate
            success_rate = self.successful_decisions / max(self.total_decisions, 1)
            
            total_time = (datetime.now() - self.start_time).total_seconds()
            logger.warning(f"✅ High-performance backtest completed in {total_time/3600:.2f} hours")
            logger.warning(f"Processing rate: {len(trading_dates)/total_time:.2f} days/second")
            
            return EvaluationBacktestResult(
                portfolio_history=self.portfolio_history,
                trade_log=self.trade_log,
                daily_metrics=[],  # Not calculated for performance
                portfolio_metrics=final_metrics['portfolio_metrics'],
                ticker_metrics=final_metrics['ticker_metrics'],
                data_coverage={'total_decisions': self.total_decisions},
                configuration=self.config.__dict__,
                start_date=trading_dates[0],
                end_date=trading_dates[-1],
                total_days=len(trading_dates),
                trading_days=len(trading_dates),
                success_rate=success_rate
            )
            
        except Exception as e:
            logger.error(f"Error in high-performance backtest: {e}")
            raise

    def _process_ticker_optimized(self, ticker: str, current_date: datetime, current_price: float):
        """Optimized ticker processing with minimal logging."""
        try:
            # Get expert aggregation (this is the main bottleneck)
            aggregation_result = aggregate_experts(ticker, current_date.strftime('%Y-%m-%d'), 
                                                 lookback_days=7, lookback_years=2)
            
            if aggregation_result is None:
                return
            
            self.total_decisions += 1
            
            # Log ticker decision to performance logger (minimal)
            position_data = None
            if ticker in self.portfolio_simulator.positions:
                position = self.portfolio_simulator.positions[ticker]
                position_data = {
                    "quantity": position.quantity,
                    "avg_price": position.avg_price,
                    "current_value": position.quantity * position.current_price,
                    "unrealized_pnl": position.unrealized_pnl,
                    "status": position.status.value
                }

            self.performance_logger.log_daily_ticker(
                current_date, ticker, current_price,
                aggregation_result, position_data
            )
            
            # Execute trade if needed
            decision_type = aggregation_result.decision_type
            if decision_type == DecisionType.BUY:
                trade_action = TradeAction.BUY
            elif decision_type == DecisionType.SELL:
                trade_action = TradeAction.SELL
            else:
                trade_action = TradeAction.HOLD
            
            if trade_action in [TradeAction.BUY, TradeAction.SELL]:
                # Get portfolio state before trade
                portfolio_state_before = self.portfolio_simulator.get_portfolio_state()
                
                # Execute trade
                trade_record = self.portfolio_simulator.execute_trade(
                    ticker=ticker,
                    action=trade_action,
                    price=current_price,
                    date=current_date,
                    confidence=aggregation_result.overall_confidence,
                    reasoning=aggregation_result.reasoning,
                    expert_outputs={name: contrib.expert_output for name, contrib in aggregation_result.expert_contributions.items()}
                )
                
                if trade_record and trade_record.success:
                    self.trade_log.append(trade_record)
                    self.performance_logger.log_trade(trade_record)
                    self.successful_decisions += 1
                    
        except Exception as e:
            logger.error(f"Error processing {ticker} on {current_date}: {e}")

    def _calculate_daily_metrics_optimized(self, current_date: datetime):
        """Optimized daily metrics calculation (minimal)."""
        try:
            # Update portfolio prices for all tickers to calculate proper daily returns
            price_updates = {}
            for ticker in self.config.tickers:
                if ticker in self.portfolio_simulator.positions:
                    # Get current price from the price data that was loaded upfront
                    if hasattr(self, 'price_data') and ticker in self.price_data:
                        if current_date in self.price_data[ticker].index:
                            current_price = self.price_data[ticker].loc[current_date, 'close']
                            if pd.notna(current_price) and current_price > 0:
                                price_updates[ticker] = current_price
            
            # Update prices to trigger daily return calculation
            if price_updates:
                self.portfolio_simulator.update_prices(price_updates, current_date)
            
            portfolio_state = self.portfolio_simulator.get_portfolio_state()
            self.performance_logger.log_daily_portfolio(current_date, portfolio_state)
            self.portfolio_history.append(portfolio_state)
        except Exception as e:
            logger.error(f"Error calculating daily metrics: {e}")

    def _calculate_final_metrics(self) -> Dict:
        """Calculate final metrics efficiently."""
        try:
            portfolio_metrics = self.metrics_calculator.calculate_portfolio_metrics(
                self.portfolio_history, self.trade_log
            )
            
            ticker_metrics = {}
            for ticker in self.config.tickers:
                ticker_metrics[ticker] = self.metrics_calculator.calculate_ticker_metrics(
                    ticker, self.portfolio_history, self.trade_log
                )
            
            return {
                'portfolio_metrics': portfolio_metrics,
                'ticker_metrics': ticker_metrics
            }
        except Exception as e:
            logger.error(f"Error calculating final metrics: {e}")
            return {
                'portfolio_metrics': PortfolioMetrics(),
                'ticker_metrics': {}
            }

# Import the missing classes
from core.data_types import (
    PortfolioSimulatorConfig, TradeLoggerConfig, EvaluationBacktestResult
)

def run_backtest(config: BacktesterConfig) -> EvaluationBacktestResult:
    """
    Run a backtest with the given configuration.
    
    Args:
        config: Backtester configuration
        
    Returns:
        Backtest results
    """
    backtester = HighPerformanceBacktester(config)
    return backtester.run_backtest()

def run_backtest_from_env() -> EvaluationBacktestResult:
    """
    Run a backtest using environment variables for configuration.
    
    Returns:
        Backtest results
    """
    # This would load config from environment variables
    # For now, use default config
    config = BacktesterConfig(
        start_date="2024-01-01",
        end_date="2024-01-10",
        tickers=["aa", "aaau"],
        initial_capital=100000
    )
    return run_backtest(config) 