#!/usr/bin/env python3
"""
Unit tests for the PerformanceLogger class.
"""

import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pytest

from evaluation.performance_logger import PerformanceLogger
from core.data_types import (
    BacktesterConfig, EvaluationPortfolioState as PortfolioState, TradeRecord,
    EvaluationPortfolioMetrics as PortfolioMetrics, EvaluationTickerMetrics as TickerMetrics,
    EvaluationPosition as Position, TradeAction
)
from aggregation.expert_aggregator import AggregationResult, ExpertContribution
from core.data_types import (
    DecisionProbabilities, ExpertConfidence, ExpertOutput, DecisionType, ExpertMetadata
)


class TestPerformanceLogger:
    """Test cases for PerformanceLogger class."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        os.makedirs("logs", exist_ok=True)
        
        self.config = BacktesterConfig(
            start_date="2024-01-01", end_date="2024-01-10", tickers=["aa", "aaau"],
            initial_capital=100000, position_sizing=0.15, max_positions=3,
            cash_reserve=0.2, min_cash_reserve=0.1, transaction_cost=0.001,
            slippage=0.0005, log_level="INFO"
        )
        self.backtest_id = "test_backtest_20240101_aa_aaau"
        self.logger = PerformanceLogger(self.backtest_id, self.config)

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test PerformanceLogger initialization."""
        assert self.logger.backtest_id == self.backtest_id
        assert self.logger.config == self.config
        assert self.logger.output_dir == f"logs/{self.backtest_id}"
        assert os.path.exists(self.logger.output_dir)
        assert self.logger.portfolio_daily_data == []
        assert self.logger.tickers_daily_data == {}
        assert self.logger.trades_data == []

    def test_log_daily_portfolio(self):
        """Test logging daily portfolio data."""
        date = datetime(2024, 1, 2)
        portfolio_state = PortfolioState(
            total_value=100250.00, cash=95493.25, positions={}, date=date,
            daily_return=0.0025, cash_reserve=20050.00, available_capital=75443.25
        )
        
        self.logger.log_daily_portfolio(date, portfolio_state)
        
        assert len(self.logger.portfolio_daily_data) == 1
        daily_data = self.logger.portfolio_daily_data[0]
        assert daily_data["date"] == "2024-01-02"
        assert daily_data["total_value"] == 95493.25  # Should equal cash when no positions
        assert daily_data["cash"] == 95493.25
        assert daily_data["positions_value"] == 0.0
        assert daily_data["daily_return"] == 0.0025
        assert daily_data["num_positions"] == 0

    def test_log_daily_ticker(self):
        """Test logging daily ticker data."""
        date = datetime(2024, 1, 2)
        ticker = "aa"
        price = 45.20
        
        # Create expert output
        expert_output = ExpertOutput(
            probabilities=DecisionProbabilities(0.6, 0.3, 0.1),
            confidence=ExpertConfidence(0.7, 0.3, 0.8, {"reasoning": "Positive sentiment"}),
            metadata=ExpertMetadata("sentiment", "llama2", 0.5, 0.8)
        )
        
        # Create expert contribution
        contribution = ExpertContribution(
            expert_name="sentiment", expert_output=expert_output, weight=0.25,
            contribution=DecisionProbabilities(0.6, 0.3, 0.1), confidence=0.7, processing_time=0.5
        )
        
        # Create aggregation result
        aggregation_result = AggregationResult(
            final_probabilities=DecisionProbabilities(0.55, 0.35, 0.10),
            expert_contributions={"sentiment": contribution}, aggregation_method="dynamic_gating",
            gating_weights={"sentiment": 0.25}, overall_confidence=0.75,
            decision_type=DecisionType.BUY, reasoning="Strong consensus for buy", processing_time=0.5
        )
        
        position_data = {
            "quantity": 100, "avg_price": 45.00, "current_value": 4520.00,
            "unrealized_pnl": 20.00, "status": "OPEN"
        }
        
        self.logger.log_daily_ticker(date, ticker, price, aggregation_result, position_data)
        
        assert ticker in self.logger.tickers_daily_data
        assert len(self.logger.tickers_daily_data[ticker]) == 1
        
        ticker_data = self.logger.tickers_daily_data[ticker][0]
        assert ticker_data["date"] == "2024-01-02"
        assert ticker_data["price"] == 45.20
        assert ticker_data["decision"] == "buy"
        assert ticker_data["overall_confidence"] == 0.75
        assert ticker_data["position"] == position_data
        
        # Check expert contributions
        expert_contrib = ticker_data["expert_contributions"]["sentiment"]
        assert expert_contrib["weight"] == 0.25
        assert expert_contrib["confidence"] == 0.7
        assert expert_contrib["probabilities"] == [0.6, 0.3, 0.1]
        assert expert_contrib["reasoning"] == "Positive sentiment"

    def test_log_trade(self):
        """Test logging trade data."""
        date = datetime(2024, 1, 2)
        ticker = "aa"
        
        # Create portfolio states
        portfolio_before = PortfolioState(
            total_value=100000, cash=100000, positions={}, date=date
        )
        portfolio_after = PortfolioState(
            total_value=99950, cash=95000, positions={}, date=date
        )
        
        # Create trade record
        trade_record = TradeRecord(
            date=date, ticker=ticker, action=TradeAction.BUY, quantity=100,
            price=50.0, value=5000.0, transaction_cost=5.0, slippage=2.5,
            total_cost=5007.5, confidence=0.8, reasoning="Strong buy signal",
            expert_outputs={"sentiment": {"weight": 0.3, "confidence": 0.7}},
            portfolio_state_before=portfolio_before, portfolio_state_after=portfolio_after
        )
        
        self.logger.log_trade(trade_record)
        
        assert len(self.logger.trades_data) == 1
        trade_data = self.logger.trades_data[0]
        assert trade_data["trade_id"] == "trade_001"
        assert trade_data["date"] == "2024-01-02"
        assert trade_data["ticker"] == "aa"
        assert trade_data["action"] == "BUY"
        assert trade_data["quantity"] == 100
        assert trade_data["price"] == 50.0
        assert trade_data["value"] == 5000.0
        assert trade_data["overall_confidence"] == 0.8
        assert trade_data["success"] == True

    def test_save_final_results(self):
        """Test saving final results."""
        # Create sample data
        self.logger.portfolio_daily_data = [
            {"date": "2024-01-01", "total_value": 100000},
            {"date": "2024-01-02", "total_value": 100250}
        ]
        self.logger.tickers_daily_data = {
            "aa": [{"date": "2024-01-01", "price": 45.00}],
            "aaau": [{"date": "2024-01-01", "price": 20.50}]
        }
        self.logger.trades_data = [
            {"trade_id": "trade_001", "ticker": "aa", "action": "BUY"}
        ]
        
        # Create metrics
        portfolio_metrics = PortfolioMetrics(
            total_return=0.2554, annualized_return=0.2556, sharpe_ratio=1.940,
            sortino_ratio=2.150, calmar_ratio=3.408, max_drawdown=0.075,
            drawdown_duration=15, volatility=0.132, win_rate=0.0, profit_factor=0.0,
            total_trades=11, avg_trade_return=0.0, best_trade=0.0, worst_trade=0.0,
            avg_hold_time=0.0, cash_drag=0.078, diversification_score=0.5
        )
        
        ticker_metrics = {
            "aa": TickerMetrics(
                ticker="aa", total_return=0.4788, annualized_return=0.4792,
                sharpe_ratio=2.1, sortino_ratio=2.3, calmar_ratio=4.2,
                max_drawdown=0.05, drawdown_duration=8, volatility=0.15,
                win_rate=0.0, avg_win=0.0, avg_loss=0.0, profit_factor=0.0,
                contribution_to_portfolio=0.036, num_trades=1, avg_hold_time=0.0
            )
        }
        
        self.logger.save_final_results(portfolio_metrics, ticker_metrics)
        
        # Check that files were created
        config_file = os.path.join(self.logger.output_dir, "config.json")
        portfolio_file = os.path.join(self.logger.output_dir, "portfolio_daily.json")
        tickers_file = os.path.join(self.logger.output_dir, "tickers_daily.json")
        trades_file = os.path.join(self.logger.output_dir, "trades.json")
        results_file = os.path.join(self.logger.output_dir, "results.json")
        
        assert os.path.exists(config_file)
        assert os.path.exists(portfolio_file)
        assert os.path.exists(tickers_file)
        assert os.path.exists(trades_file)
        assert os.path.exists(results_file)
        
        # Verify config file content
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        assert config_data["backtest_id"] == self.backtest_id
        assert config_data["start_date"] == "2024-01-01"
        assert config_data["end_date"] == "2024-01-10"
        assert config_data["status"] == "completed"

    def test_error_handling(self):
        """Test error handling in performance logger."""
        # Test with invalid date
        with pytest.raises(Exception):
            self.logger.log_daily_portfolio("invalid_date", None)
        
        # Test with invalid portfolio state
        with pytest.raises(Exception):
            self.logger.log_daily_portfolio(datetime.now(), "invalid_state")
        
        # Test with invalid ticker data
        with pytest.raises(Exception):
            self.logger.log_daily_ticker(datetime.now(), "ticker", 100, None)

    def test_multiple_trades_same_ticker(self):
        """Test logging multiple trades for the same ticker."""
        date = datetime(2024, 1, 2)
        ticker = "aa"
        
        # Create multiple trade records
        for i in range(3):
            portfolio_before = PortfolioState(
                total_value=100000 - i*100, cash=100000 - i*100, positions={}, date=date
            )
            portfolio_after = PortfolioState(
                total_value=99950 - i*100, cash=95000 - i*100, positions={}, date=date
            )
            
            trade_record = TradeRecord(
                date=date, ticker=ticker, action=TradeAction.BUY, quantity=100,
                price=50.0 + i, value=5000.0 + i*100, transaction_cost=5.0, slippage=2.5,
                total_cost=5007.5 + i*100, confidence=0.8, reasoning=f"Trade {i+1}",
                expert_outputs={}, portfolio_state_before=portfolio_before,
                portfolio_state_after=portfolio_after
            )
            
            self.logger.log_trade(trade_record)
        
        assert len(self.logger.trades_data) == 3
        assert self.logger.trades_data[0]["trade_id"] == "trade_001"
        assert self.logger.trades_data[1]["trade_id"] == "trade_002"
        assert self.logger.trades_data[2]["trade_id"] == "trade_003"

    def test_empty_data_handling(self):
        """Test handling of empty data scenarios."""
        # Test with no portfolio data
        portfolio_metrics = PortfolioMetrics(
            total_return=0.0, annualized_return=0.0, sharpe_ratio=0.0,
            sortino_ratio=0.0, calmar_ratio=0.0, max_drawdown=0.0,
            drawdown_duration=0, volatility=0.0, win_rate=0.0, profit_factor=0.0,
            total_trades=0, avg_trade_return=0.0, best_trade=0.0, worst_trade=0.0,
            avg_hold_time=0.0, cash_drag=0.0, diversification_score=0.0
        )
        
        self.logger.save_final_results(portfolio_metrics, {})
        
        # Should still create files
        config_file = os.path.join(self.logger.output_dir, "config.json")
        assert os.path.exists(config_file)


def test_performance_logger_integration():
    """Integration test for PerformanceLogger."""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        os.makedirs("logs", exist_ok=True)
        
        config = BacktesterConfig(
            start_date="2024-01-01", end_date="2024-01-05", tickers=["aa"],
            initial_capital=100000, position_sizing=0.15, max_positions=3,
            cash_reserve=0.2, min_cash_reserve=0.1, transaction_cost=0.001,
            slippage=0.0005, log_level="INFO"
        )
        
        logger = PerformanceLogger("test_integration", config)
        
        # Simulate a complete backtest
        for i in range(3):
            date = datetime(2024, 1, 1 + i)
            
            # Log portfolio
            portfolio_state = PortfolioState(
                total_value=100000 - i*100, cash=100000 - i*100, positions={}, date=date
            )
            logger.log_daily_portfolio(date, portfolio_state)
            
            # Log ticker decision
            expert_output = ExpertOutput(
                probabilities=DecisionProbabilities(0.6, 0.3, 0.1),
                confidence=ExpertConfidence(0.7, 0.3, 0.8, {"reasoning": "Test"}),
                metadata=ExpertMetadata("test", "test", 0.5, 0.8)
            )
            contribution = ExpertContribution(
                expert_name="test", expert_output=expert_output, weight=1.0,
                contribution=DecisionProbabilities(0.6, 0.3, 0.1), confidence=0.7, processing_time=0.1
            )
            aggregation_result = AggregationResult(
                final_probabilities=DecisionProbabilities(0.6, 0.3, 0.1),
                expert_contributions={"test": contribution}, aggregation_method="test",
                gating_weights={"test": 1.0}, overall_confidence=0.7,
                decision_type=DecisionType.BUY, reasoning="Test", processing_time=0.1
            )
            logger.log_daily_ticker(date, "aa", 50.0, aggregation_result)
            
            # Log trade
            portfolio_before = PortfolioState(
                total_value=100000 - i*100, cash=100000 - i*100, positions={}, date=date
            )
            portfolio_after = PortfolioState(
                total_value=99950 - i*100, cash=95000 - i*100, positions={}, date=date
            )
            trade_record = TradeRecord(
                date=date, ticker="aa", action=TradeAction.BUY, quantity=100,
                price=50.0, value=5000.0, transaction_cost=5.0, slippage=2.5,
                total_cost=5007.5, confidence=0.8, reasoning="Test trade",
                expert_outputs={}, portfolio_state_before=portfolio_before,
                portfolio_state_after=portfolio_after
            )
            logger.log_trade(trade_record)
        
        # Save final results
        portfolio_metrics = PortfolioMetrics(
            total_return=0.0, annualized_return=0.0, sharpe_ratio=0.0,
            sortino_ratio=0.0, calmar_ratio=0.0, max_drawdown=0.0,
            drawdown_duration=0, volatility=0.0, win_rate=0.0, profit_factor=0.0,
            total_trades=3, avg_trade_return=0.0, best_trade=0.0, worst_trade=0.0,
            avg_hold_time=0.0, cash_drag=0.0, diversification_score=0.0
        )
        ticker_metrics = {}
        
        logger.save_final_results(portfolio_metrics, ticker_metrics)
        
        # Verify all files exist and have content
        required_files = ["config.json", "portfolio_daily.json", "tickers_daily.json", "trades.json", "results.json"]
        for file in required_files:
            file_path = os.path.join(logger.output_dir, file)
            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0


if __name__ == "__main__":
    pytest.main([__file__]) 