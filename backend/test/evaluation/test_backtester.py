#!/usr/bin/env python3
"""
Unit tests for the Backtester class with performance logging integration.
"""

import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pytest
import pandas as pd

from evaluation.backtester import Backtester, run_backtest
from core.data_types import (
    BacktesterConfig, EvaluationPortfolioState as PortfolioState, TradeRecord,
    EvaluationPortfolioMetrics as PortfolioMetrics, EvaluationTickerMetrics as TickerMetrics,
    TradeAction, DecisionType
)
from aggregation.expert_aggregator import AggregationResult, ExpertContribution
from core.data_types import (
    DecisionProbabilities, ExpertConfidence, ExpertOutput, ExpertMetadata
)


class TestBacktester:
    """Test cases for Backtester class."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        os.makedirs("logs", exist_ok=True)
        
        self.config = BacktesterConfig(
            start_date="2024-01-01", end_date="2024-01-05", tickers=["aa"],
            initial_capital=100000, position_sizing=0.15, max_positions=3,
            cash_reserve=0.2, min_cash_reserve=0.1, transaction_cost=0.001,
            slippage=0.0005, log_level="INFO"
        )

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    @patch('evaluation.backtester.PortfolioSimulator')
    @patch('evaluation.backtester.TradeLogger')
    @patch('evaluation.backtester.MetricsCalculator')
    @patch('evaluation.backtester.PerformanceLogger')
    @patch('evaluation.backtester.ExpertAggregator')
    @patch('evaluation.backtester.load_prices')
    def test_initialization(self, mock_load_prices, mock_aggregator, mock_perf_logger,
                           mock_metrics, mock_trade_logger, mock_portfolio):
        """Test Backtester initialization."""
        # Mock the data loading
        mock_price_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-05'),
            'close': [50.0, 51.0, 52.0, 53.0, 54.0]
        })
        mock_load_prices.return_value = mock_price_data
        
        backtester = Backtester(self.config)
        
        assert backtester.config == self.config
        assert backtester.portfolio_simulator is not None
        assert backtester.trade_logger is not None
        assert backtester.metrics_calculator is not None
        assert backtester.performance_logger is not None
        assert backtester.expert_aggregator is not None
        assert backtester.portfolio_history == []
        assert backtester.trade_log == []
        assert backtester.total_decisions == 0
        assert backtester.successful_decisions == 0

    @patch('evaluation.backtester.PortfolioSimulator')
    @patch('evaluation.backtester.TradeLogger')
    @patch('evaluation.backtester.MetricsCalculator')
    @patch('evaluation.backtester.PerformanceLogger')
    @patch('evaluation.backtester.ExpertAggregator')
    @patch('evaluation.backtester.load_prices')
    def test_backtest_id_generation(self, mock_load_prices, mock_aggregator, mock_perf_logger,
                                   mock_metrics, mock_trade_logger, mock_portfolio):
        """Test that backtest ID is generated correctly."""
        mock_price_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-05'),
            'close': [50.0, 51.0, 52.0, 53.0, 54.0]
        })
        mock_load_prices.return_value = mock_price_data
        
        backtester = Backtester(self.config)
        
        # Check that backtest_id follows expected pattern
        assert backtester.backtest_id.startswith("backtest_")
        assert "aa" in backtester.backtest_id
        assert len(backtester.backtest_id) > 20  # Should have timestamp

    @patch('evaluation.backtester.PortfolioSimulator')
    @patch('evaluation.backtester.TradeLogger')
    @patch('evaluation.backtester.MetricsCalculator')
    @patch('evaluation.backtester.PerformanceLogger')
    @patch('evaluation.backtester.ExpertAggregator')
    @patch('evaluation.backtester.load_prices')
    def test_process_ticker_with_buy_decision(self, mock_load_prices, mock_aggregator, mock_perf_logger,
                                             mock_metrics, mock_trade_logger, mock_portfolio):
        """Test processing a ticker with BUY decision."""
        # Mock price data
        mock_price_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-05'),
            'close': [50.0, 51.0, 52.0, 53.0, 54.0]
        })
        mock_load_prices.return_value = mock_price_data
        
        # Mock portfolio simulator
        mock_portfolio_instance = Mock()
        mock_portfolio_instance.get_portfolio_state.return_value = PortfolioState(
            total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1)
        )
        mock_portfolio_instance.positions = {}
        mock_portfolio_instance.execute_trade.return_value = TradeRecord(
            date=datetime(2024, 1, 1), ticker="aa", action=TradeAction.BUY,
            quantity=100, price=50.0, value=5000.0, transaction_cost=5.0, slippage=2.5,
            total_cost=5007.5, confidence=0.8, reasoning="Test", expert_outputs={},
            portfolio_state_before=PortfolioState(total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1)),
            portfolio_state_after=PortfolioState(total_value=99950, cash=95000, positions={}, date=datetime(2024, 1, 1))
        )
        mock_portfolio.return_value = mock_portfolio_instance
        
        # Mock expert aggregator
        mock_aggregator_instance = Mock()
        expert_output = ExpertOutput(
            probabilities=DecisionProbabilities(0.7, 0.2, 0.1),
            confidence=ExpertConfidence(0.8, 0.2, 0.8, {"reasoning": "Strong buy"}),
            metadata=ExpertMetadata("test", "test", 0.5, 0.8)
        )
        contribution = ExpertContribution(
            expert_name="test", expert_output=expert_output, weight=1.0,
            contribution=DecisionProbabilities(0.7, 0.2, 0.1), confidence=0.8, processing_time=0.1
        )
        aggregation_result = AggregationResult(
            final_probabilities=DecisionProbabilities(0.7, 0.2, 0.1),
            expert_contributions={"test": contribution}, aggregation_method="test",
            gating_weights={"test": 1.0}, overall_confidence=0.8,
            decision_type=DecisionType.BUY, reasoning="Strong buy", processing_time=0.1
        )
        mock_aggregator_instance.aggregate_experts.return_value = aggregation_result
        mock_aggregator.return_value = mock_aggregator_instance
        
        # Mock performance logger
        mock_perf_logger_instance = Mock()
        mock_perf_logger.return_value = mock_perf_logger_instance
        
        backtester = Backtester(self.config)
        
        # Process ticker
        current_date = datetime(2024, 1, 1)
        backtester._process_ticker("aa", current_date, mock_price_data)
        
        # Verify performance logger was called
        mock_perf_logger_instance.log_daily_ticker.assert_called_once()
        mock_perf_logger_instance.log_trade.assert_called_once()
        
        # Verify trade was executed
        mock_portfolio_instance.execute_trade.assert_called_once()
        
        # Verify decision count increased
        assert backtester.total_decisions == 1

    @patch('evaluation.backtester.PortfolioSimulator')
    @patch('evaluation.backtester.TradeLogger')
    @patch('evaluation.backtester.MetricsCalculator')
    @patch('evaluation.backtester.PerformanceLogger')
    @patch('evaluation.backtester.ExpertAggregator')
    @patch('evaluation.backtester.load_prices')
    def test_process_ticker_with_hold_decision(self, mock_load_prices, mock_aggregator, mock_perf_logger,
                                              mock_metrics, mock_trade_logger, mock_portfolio):
        """Test processing a ticker with HOLD decision."""
        # Mock price data
        mock_price_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-05'),
            'close': [50.0, 51.0, 52.0, 53.0, 54.0]
        })
        mock_load_prices.return_value = mock_price_data
        
        # Mock portfolio simulator
        mock_portfolio_instance = Mock()
        mock_portfolio_instance.get_portfolio_state.return_value = PortfolioState(
            total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1)
        )
        mock_portfolio_instance.positions = {}
        mock_portfolio.return_value = mock_portfolio_instance
        
        # Mock expert aggregator with HOLD decision
        mock_aggregator_instance = Mock()
        expert_output = ExpertOutput(
            probabilities=DecisionProbabilities(0.2, 0.7, 0.1),
            confidence=ExpertConfidence(0.6, 0.3, 0.6, {"reasoning": "Neutral"}),
            metadata=ExpertMetadata("test", "test", 0.5, 0.6)
        )
        contribution = ExpertContribution(
            expert_name="test", expert_output=expert_output, weight=1.0,
            contribution=DecisionProbabilities(0.2, 0.7, 0.1), confidence=0.6, processing_time=0.1
        )
        aggregation_result = AggregationResult(
            final_probabilities=DecisionProbabilities(0.2, 0.7, 0.1),
            expert_contributions={"test": contribution}, aggregation_method="test",
            gating_weights={"test": 1.0}, overall_confidence=0.6,
            decision_type=DecisionType.HOLD, reasoning="Neutral", processing_time=0.1
        )
        mock_aggregator_instance.aggregate_experts.return_value = aggregation_result
        mock_aggregator.return_value = mock_aggregator_instance
        
        # Mock performance logger
        mock_perf_logger_instance = Mock()
        mock_perf_logger.return_value = mock_perf_logger_instance
        
        backtester = Backtester(self.config)
        
        # Process ticker
        current_date = datetime(2024, 1, 1)
        backtester._process_ticker("aa", current_date, mock_price_data)
        
        # Verify performance logger was called
        mock_perf_logger_instance.log_daily_ticker.assert_called_once()
        
        # Verify no trade was executed
        mock_portfolio_instance.execute_trade.assert_not_called()
        
        # Verify decision count increased
        assert backtester.total_decisions == 1

    @patch('evaluation.backtester.PortfolioSimulator')
    @patch('evaluation.backtester.TradeLogger')
    @patch('evaluation.backtester.MetricsCalculator')
    @patch('evaluation.backtester.PerformanceLogger')
    @patch('evaluation.backtester.ExpertAggregator')
    @patch('evaluation.backtester.load_prices')
    def test_calculate_daily_metrics(self, mock_load_prices, mock_aggregator, mock_perf_logger,
                                    mock_metrics, mock_trade_logger, mock_portfolio):
        """Test daily metrics calculation with performance logging."""
        # Mock price data
        mock_price_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-05'),
            'close': [50.0, 51.0, 52.0, 53.0, 54.0]
        })
        mock_load_prices.return_value = mock_price_data
        
        # Mock portfolio simulator
        mock_portfolio_instance = Mock()
        portfolio_state = PortfolioState(
            total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1)
        )
        mock_portfolio_instance.get_portfolio_state.return_value = portfolio_state
        mock_portfolio.return_value = mock_portfolio_instance
        
        # Mock metrics calculator
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_daily_metrics.return_value = [
            Mock(date=datetime(2024, 1, 1), portfolio_value=100000, daily_return=0.0)
        ]
        mock_metrics.return_value = mock_metrics_instance
        
        # Mock performance logger
        mock_perf_logger_instance = Mock()
        mock_perf_logger.return_value = mock_perf_logger_instance
        
        backtester = Backtester(self.config)
        
        # Add some portfolio history
        backtester.portfolio_history = [portfolio_state]
        
        # Calculate daily metrics
        current_date = datetime(2024, 1, 1)
        backtester._calculate_daily_metrics(current_date)
        
        # Verify performance logger was called
        mock_perf_logger_instance.log_daily_portfolio.assert_called_once_with(current_date, portfolio_state)
        
        # Verify metrics calculator was called
        mock_metrics_instance.calculate_daily_metrics.assert_called_once()

    @patch('evaluation.backtester.PortfolioSimulator')
    @patch('evaluation.backtester.TradeLogger')
    @patch('evaluation.backtester.MetricsCalculator')
    @patch('evaluation.backtester.PerformanceLogger')
    @patch('evaluation.backtester.ExpertAggregator')
    @patch('evaluation.backtester.load_prices')
    def test_run_backtest_integration(self, mock_load_prices, mock_aggregator, mock_perf_logger,
                                     mock_metrics, mock_trade_logger, mock_portfolio):
        """Test complete backtest run with performance logging."""
        # Mock price data
        mock_price_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-03'),
            'close': [50.0, 51.0, 52.0]
        })
        mock_load_prices.return_value = mock_price_data
        
        # Mock portfolio simulator
        mock_portfolio_instance = Mock()
        portfolio_state = PortfolioState(
            total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1)
        )
        mock_portfolio_instance.get_portfolio_state.return_value = portfolio_state
        mock_portfolio_instance.positions = {}
        mock_portfolio.return_value = mock_portfolio_instance
        
        # Mock expert aggregator
        mock_aggregator_instance = Mock()
        expert_output = ExpertOutput(
            probabilities=DecisionProbabilities(0.7, 0.2, 0.1),
            confidence=ExpertConfidence(0.8, 0.2, 0.8, {"reasoning": "Test"}),
            metadata=ExpertMetadata("test", "test", 0.5, 0.8)
        )
        contribution = ExpertContribution(
            expert_name="test", expert_output=expert_output, weight=1.0,
            contribution=DecisionProbabilities(0.7, 0.2, 0.1), confidence=0.8, processing_time=0.1
        )
        aggregation_result = AggregationResult(
            final_probabilities=DecisionProbabilities(0.7, 0.2, 0.1),
            expert_contributions={"test": contribution}, aggregation_method="test",
            gating_weights={"test": 1.0}, overall_confidence=0.8,
            decision_type=DecisionType.BUY, reasoning="Test", processing_time=0.1
        )
        mock_aggregator_instance.aggregate_experts.return_value = aggregation_result
        mock_aggregator.return_value = mock_aggregator_instance
        
        # Mock metrics calculator
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_daily_metrics.return_value = [
            Mock(date=datetime(2024, 1, 1), portfolio_value=100000, daily_return=0.0)
        ]
        mock_metrics_instance.calculate_portfolio_metrics.return_value = PortfolioMetrics(
            total_return=0.0, annualized_return=0.0, sharpe_ratio=0.0,
            sortino_ratio=0.0, calmar_ratio=0.0, max_drawdown=0.0,
            drawdown_duration=0, volatility=0.0, win_rate=0.0, profit_factor=0.0,
            total_trades=0, avg_trade_return=0.0, best_trade=0.0, worst_trade=0.0,
            avg_hold_time=0.0, cash_drag=0.0, diversification_score=0.0
        )
        mock_metrics_instance.calculate_ticker_metrics.return_value = {}
        mock_metrics.return_value = mock_metrics_instance
        
        # Mock performance logger
        mock_perf_logger_instance = Mock()
        mock_perf_logger.return_value = mock_perf_logger_instance
        
        # Run backtest
        result = run_backtest(self.config)
        
        # Verify performance logger was called for final results
        mock_perf_logger_instance.save_final_results.assert_called_once()
        
        # Verify result has expected structure
        assert hasattr(result, 'portfolio_history')
        assert hasattr(result, 'trade_log')
        assert hasattr(result, 'portfolio_metrics')
        assert hasattr(result, 'ticker_metrics')

    def test_backtest_config_validation(self):
        """Test backtest configuration validation."""
        # Test with invalid date range
        invalid_config = BacktesterConfig(
            start_date="2024-01-10", end_date="2024-01-01",  # End before start
            tickers=["aa"], initial_capital=100000
        )
        
        with pytest.raises(ValueError):
            Backtester(invalid_config)
        
        # Test with empty tickers
        empty_config = BacktesterConfig(
            start_date="2024-01-01", end_date="2024-01-05",
            tickers=[], initial_capital=100000
        )
        
        with pytest.raises(ValueError):
            Backtester(empty_config)

    @patch('evaluation.backtester.PortfolioSimulator')
    @patch('evaluation.backtester.TradeLogger')
    @patch('evaluation.backtester.MetricsCalculator')
    @patch('evaluation.backtester.PerformanceLogger')
    @patch('evaluation.backtester.ExpertAggregator')
    @patch('evaluation.backtester.load_prices')
    def test_error_handling(self, mock_load_prices, mock_aggregator, mock_perf_logger,
                           mock_metrics, mock_trade_logger, mock_portfolio):
        """Test error handling in backtester."""
        # Mock price data
        mock_price_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-05'),
            'close': [50.0, 51.0, 52.0, 53.0, 54.0]
        })
        mock_load_prices.return_value = mock_price_data
        
        # Mock portfolio simulator
        mock_portfolio_instance = Mock()
        mock_portfolio_instance.get_portfolio_state.return_value = PortfolioState(
            total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1)
        )
        mock_portfolio_instance.positions = {}
        mock_portfolio.return_value = mock_portfolio_instance
        
        # Mock expert aggregator to raise exception
        mock_aggregator_instance = Mock()
        mock_aggregator_instance.aggregate_experts.side_effect = Exception("Expert error")
        mock_aggregator.return_value = mock_aggregator_instance
        
        # Mock performance logger
        mock_perf_logger_instance = Mock()
        mock_perf_logger.return_value = mock_perf_logger_instance
        
        backtester = Backtester(self.config)
        
        # Process ticker should handle exception gracefully
        current_date = datetime(2024, 1, 1)
        backtester._process_ticker("aa", current_date, mock_price_data)
        
        # Should still increment decision count
        assert backtester.total_decisions == 1


if __name__ == "__main__":
    pytest.main([__file__]) 