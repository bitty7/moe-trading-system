"""
Test suite for the Performance Logging System.

Tests the comprehensive logging capabilities for backtesting results.
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
    """Test the PerformanceLogger class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Test configuration
        self.config = BacktesterConfig(
            start_date="2024-01-01",
            end_date="2024-01-10",
            tickers=["aa", "aaau"],
            initial_capital=100000,
            position_sizing=0.15,
            max_positions=3,
            cash_reserve=0.2,
            min_cash_reserve=0.1,
            transaction_cost=0.001,
            slippage=0.0005,
            log_level="INFO"
        )
        
        self.backtest_id = "test_backtest_20240101_aa_aaau"
        self.logger = PerformanceLogger(self.backtest_id, self.config)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test PerformanceLogger initialization."""
        assert self.logger.backtest_id == self.backtest_id
        assert self.logger.config == self.config
        assert self.logger.log_dir == f"logs/{self.backtest_id}"
        
        # Check that log directory was created
        assert os.path.exists(self.logger.log_dir)
        
        # Check that config.json was created
        config_file = os.path.join(self.logger.log_dir, "config.json")
        assert os.path.exists(config_file)
        
        # Verify config content
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        assert config_data["backtest_id"] == self.backtest_id
        assert config_data["start_date"] == "2024-01-01"
        assert config_data["status"] == "running"
    
    def test_log_daily_portfolio(self):
        """Test logging daily portfolio performance."""
        date = datetime(2024, 1, 2)
        portfolio_state = PortfolioState(
            total_value=100250.00,
            cash=95493.25,
            positions={},
            date=date,
            daily_return=0.0025,
            cash_reserve=20050.00,
            available_capital=75443.25
        )
        
        # The __post_init__ method recalculates total_value, so we need to account for that
        # Since there are no positions, total_value should equal cash
        expected_total_value = 95493.25
        
        self.logger.log_daily_portfolio(date, portfolio_state)
        
        assert len(self.logger.portfolio_daily_data) == 1
        daily_data = self.logger.portfolio_daily_data[0]
        
        assert daily_data["date"] == "2024-01-02"
        assert daily_data["total_value"] == expected_total_value
        assert daily_data["cash"] == 95493.25
        assert daily_data["positions_value"] == 0.0  # No positions
        assert daily_data["daily_return"] == 0.0025
        assert daily_data["num_positions"] == 0
    
    def test_log_daily_ticker(self):
        """Test logging daily ticker performance."""
        date = datetime(2024, 1, 2)
        ticker = "aa"
        price = 45.20
        
        # Create mock aggregation result
        expert_output = ExpertOutput(
            probabilities=DecisionProbabilities(0.6, 0.3, 0.1),  # buy, hold, sell
            confidence=ExpertConfidence(0.7, 0.3, 0.8, {"reasoning": "Positive sentiment"}),
            metadata=ExpertMetadata("sentiment", "llama2", 0.5, 0.8)
        )
        
        contribution = ExpertContribution(
            expert_name="sentiment",
            expert_output=expert_output,
            weight=0.25,
            contribution=DecisionProbabilities(0.6, 0.3, 0.1),
            confidence=0.7,
            processing_time=0.5
        )
        
        aggregation_result = AggregationResult(
            final_probabilities=DecisionProbabilities(0.55, 0.35, 0.10),
            expert_contributions={"sentiment": contribution},
            aggregation_method="dynamic_gating",
            gating_weights={"sentiment": 0.25},
            overall_confidence=0.75,
            decision_type=DecisionType.BUY,
            reasoning="Strong consensus for buy",
            processing_time=0.5
        )
        
        position_data = {
            "quantity": 100,
            "avg_price": 45.00,
            "current_value": 4520.00,
            "unrealized_pnl": 20.00,
            "status": "OPEN"
        }
        
        self.logger.log_daily_ticker(date, ticker, price, aggregation_result, position_data)
        
        assert ticker in self.logger.tickers_daily_data
        assert len(self.logger.tickers_daily_data[ticker]) == 1
        
        ticker_data = self.logger.tickers_daily_data[ticker][0]
        assert ticker_data["date"] == "2024-01-02"
        assert ticker_data["price"] == 45.20
        assert ticker_data["decision"] == "buy"  # DecisionType enum returns lowercase
        assert ticker_data["overall_confidence"] == 0.75
        assert ticker_data["position"] == position_data
        
        # Check expert contributions
        assert "sentiment" in ticker_data["expert_contributions"]
        expert_data = ticker_data["expert_contributions"]["sentiment"]
        assert expert_data["weight"] == 0.25
        assert expert_data["confidence"] == 0.7
        assert expert_data["probabilities"] == [0.6, 0.3, 0.1]
    
    def test_log_trade(self):
        """Test logging trade execution."""
        date = datetime(2024, 1, 2)
        
        # Create mock portfolio states
        portfolio_before = PortfolioState(
            date=date,
            total_value=100000.00,
            cash=100000.00,
            positions={},
            daily_return=0.0,
            cash_reserve=20000.00,
            available_capital=80000.00
        )
        
        portfolio_after = PortfolioState(
            date=date,
            total_value=100000.00,
            cash=95493.25,
            positions={},
            daily_return=0.0,
            cash_reserve=20000.00,
            available_capital=75493.25
        )
        
        # Create trade record
        trade_record = TradeRecord(
            date=date,
            ticker="aa",
            action=TradeAction.BUY,
            quantity=100,
            price=45.00,
            value=4500.00,
            transaction_cost=4.50,
            slippage=2.25,
            total_cost=4506.75,
            confidence=0.75,
            reasoning="Strong buy signal",
            success=True,
            portfolio_state_before=portfolio_before,
            portfolio_state_after=portfolio_after,
            expert_outputs={
                "sentiment": {"confidence": 0.7, "weight": 0.25}
            }
        )
        
        self.logger.log_trade(trade_record)
        
        assert len(self.logger.trades_data) == 1
        trade_data = self.logger.trades_data[0]
        
        assert trade_data["trade_id"] == "trade_001"
        assert trade_data["date"] == "2024-01-02"
        assert trade_data["ticker"] == "aa"
        assert trade_data["action"] == "BUY"
        assert trade_data["quantity"] == 100
        assert trade_data["price"] == 45.00
        assert trade_data["success"] == True
        
        # Check expert contributions
        assert "sentiment" in trade_data["expert_contributions"]
        expert_data = trade_data["expert_contributions"]["sentiment"]
        assert expert_data["confidence"] == 0.7
        assert expert_data["weight"] == 0.25
    
    def test_save_final_results(self):
        """Test saving final results."""
        # Create mock metrics
        portfolio_metrics = PortfolioMetrics(
            total_return=0.2554,
            annualized_return=0.2556,
            sharpe_ratio=1.940,
            sortino_ratio=2.150,
            calmar_ratio=3.408,
            max_drawdown=0.075,
            drawdown_duration=15,
            volatility=0.132,
            win_rate=0.0,
            profit_factor=0.0,
            total_trades=11,
            avg_trade_return=0.0,
            best_trade=0.0,
            worst_trade=0.0,
            avg_hold_time=0.0,
            cash_drag=0.078,
            diversification_score=0.5
        )
        
        ticker_metrics = {
            "aa": TickerMetrics(
                ticker="aa",
                total_return=0.4788,
                annualized_return=0.4792,
                sharpe_ratio=2.1,
                sortino_ratio=2.3,
                calmar_ratio=4.2,
                max_drawdown=0.05,
                drawdown_duration=8,
                volatility=0.15,
                win_rate=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                profit_factor=0.0,
                contribution_to_portfolio=0.036,
                num_trades=1,
                avg_hold_time=0.0
            )
        }
        
        # Add some test data first
        self.logger.portfolio_daily_data = [{"date": "2024-01-01", "total_value": 100000}]
        self.logger.tickers_daily_data = {"aa": [{"date": "2024-01-01", "price": 45.00}]}
        self.logger.trades_data = [{"trade_id": "trade_001", "ticker": "aa"}]
        
        # Save final results
        self.logger.save_final_results(portfolio_metrics, ticker_metrics)
        
        # Check that all files were created
        expected_files = [
            "config.json",
            "portfolio_daily.json", 
            "tickers_daily.json",
            "trades.json",
            "results.json"
        ]
        
        for filename in expected_files:
            filepath = os.path.join(self.logger.log_dir, filename)
            assert os.path.exists(filepath), f"File {filename} was not created"
        
        # Verify results.json content
        results_file = os.path.join(self.logger.log_dir, "results.json")
        with open(results_file, 'r') as f:
            results_data = json.load(f)
        
        assert "portfolio_metrics" in results_data
        assert "ticker_summary" in results_data
        
        portfolio_data = results_data["portfolio_metrics"]
        assert portfolio_data["total_return"] == 0.2554
        assert portfolio_data["sharpe_ratio"] == 1.940
        
        ticker_data = results_data["ticker_summary"]["aa"]
        assert ticker_data["total_return"] == 0.4788
        assert ticker_data["num_trades"] == 1
        
        # Check that config status was updated
        config_file = os.path.join(self.logger.log_dir, "config.json")
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        assert config_data["status"] == "completed"
        assert "completed_at" in config_data
    
    def test_error_handling(self):
        """Test error handling in performance logger."""
        # Test invalid directory creation
        with patch('os.makedirs', side_effect=OSError("Permission denied")):
            with pytest.raises(OSError):
                PerformanceLogger("invalid_test", self.config)
        
        # Test invalid JSON writing
        with patch('builtins.open', side_effect=OSError("Disk full")):
            with pytest.raises(OSError):
                self.logger._write_json_file("test.json", {"data": "test"})


def test_performance_logging_integration():
    """Test integration with actual backtesting components."""
    # This test would integrate with the actual backtester
    # For now, we'll create a simple integration test
    pass


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 