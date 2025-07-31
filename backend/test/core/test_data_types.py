#!/usr/bin/env python3
"""
Unit tests for the unified data types in core/data_types.py.
"""

import pytest
from datetime import datetime, timedelta
from dataclasses import asdict

from core.data_types import (
    # Core types
    DecisionType, TradeAction, PositionStatus,
    DecisionProbabilities, ExpertConfidence, ExpertOutput, ExpertMetadata,
    
    # Evaluation types
    EvaluationPosition, EvaluationPortfolioState, TradeRecord, DailyMetrics,
    EvaluationTickerMetrics, EvaluationPortfolioMetrics, EvaluationBacktestResult,
    TradeLoggerConfig, PortfolioSimulatorConfig, BacktesterConfig,
    
    # Helper functions
    create_evaluation_portfolio_state, create_trade_record
)


class TestCoreDataTypes:
    """Test cases for core data types."""

    def test_decision_type_enum(self):
        """Test DecisionType enum."""
        assert DecisionType.BUY.value == "buy"
        assert DecisionType.SELL.value == "sell"
        assert DecisionType.HOLD.value == "hold"
        
        # Test comparison
        assert DecisionType.BUY == DecisionType.BUY
        assert DecisionType.BUY != DecisionType.SELL

    def test_trade_action_enum(self):
        """Test TradeAction enum."""
        assert TradeAction.BUY.value == "BUY"
        assert TradeAction.SELL.value == "SELL"
        
        # Test comparison
        assert TradeAction.BUY == TradeAction.BUY
        assert TradeAction.BUY != TradeAction.SELL

    def test_position_status_enum(self):
        """Test PositionStatus enum."""
        assert PositionStatus.OPEN.value == "OPEN"
        assert PositionStatus.CLOSED.value == "CLOSED"
        
        # Test comparison
        assert PositionStatus.OPEN == PositionStatus.OPEN
        assert PositionStatus.OPEN != PositionStatus.CLOSED

    def test_decision_probabilities(self):
        """Test DecisionProbabilities dataclass."""
        probs = DecisionProbabilities(0.6, 0.3, 0.1)
        
        assert probs.buy_probability == 0.6
        assert probs.hold_probability == 0.3
        assert probs.sell_probability == 0.1
        assert probs.to_list() == [0.6, 0.3, 0.1]
        
        # Test validation
        with pytest.raises(ValueError):
            DecisionProbabilities(0.6, 0.3, 0.2)  # Sum > 1

    def test_expert_confidence(self):
        """Test ExpertConfidence dataclass."""
        metadata = {"reasoning": "Test reasoning", "data_quality": 0.8}
        confidence = ExpertConfidence(0.7, 0.2, 0.8, metadata)
        
        assert confidence.confidence_score == 0.7
        assert confidence.data_quality == 0.2
        assert confidence.method_confidence == 0.8
        assert confidence.metadata == metadata
        assert confidence.metadata["reasoning"] == "Test reasoning"

    def test_expert_output(self):
        """Test ExpertOutput dataclass."""
        probabilities = DecisionProbabilities(0.6, 0.3, 0.1)
        confidence = ExpertConfidence(0.7, 0.2, 0.8, {"reasoning": "Test"})
        metadata = ExpertMetadata("sentiment", "llama2", 0.5, 0.8)
        
        output = ExpertOutput(probabilities, confidence, metadata)
        
        assert output.probabilities == probabilities
        assert output.confidence == confidence
        assert output.metadata == metadata


class TestEvaluationDataTypes:
    """Test cases for evaluation-specific data types."""

    def test_evaluation_position(self):
        """Test EvaluationPosition dataclass."""
        position = EvaluationPosition(
            ticker="aa",
            quantity=100,
            avg_price=50.0,
            current_price=55.0,
            status=PositionStatus.OPEN,
            unrealized_pnl=500.0,
            realized_pnl=0.0
        )
        
        assert position.ticker == "aa"
        assert position.quantity == 100
        assert position.avg_price == 50.0
        assert position.current_price == 55.0
        assert position.status == PositionStatus.OPEN
        assert position.unrealized_pnl == 500.0
        assert position.realized_pnl == 0.0
        
        # Test methods
        position.update_price(60.0)
        assert position.current_price == 60.0
        assert position.unrealized_pnl == 1000.0
        
        position.add_quantity(50, 52.0)
        assert position.quantity == 150
        assert position.avg_price == 50.67  # (100*50 + 50*52) / 150

    def test_evaluation_portfolio_state(self):
        """Test EvaluationPortfolioState dataclass."""
        positions = {
            "aa": EvaluationPosition("aa", 100, 50.0, 55.0, PositionStatus.OPEN, 500.0, 0.0)
        }
        
        portfolio_state = EvaluationPortfolioState(
            total_value=100500.0,
            cash=95000.0,
            positions=positions,
            date=datetime(2024, 1, 1),
            daily_return=0.005,
            total_pnl=500.0,
            cash_reserve=20000.0,
            available_capital=75000.0
        )
        
        assert portfolio_state.total_value == 100500.0
        assert portfolio_state.cash == 95000.0
        assert len(portfolio_state.positions) == 1
        assert portfolio_state.date == datetime(2024, 1, 1)
        assert portfolio_state.daily_return == 0.005
        assert portfolio_state.total_pnl == 500.0
        assert portfolio_state.cash_reserve == 20000.0
        assert portfolio_state.available_capital == 75000.0
        
        # Test methods
        total_value = portfolio_state.calculate_total_value()
        assert total_value == 100500.0
        
        total_pnl = portfolio_state.calculate_total_pnl()
        assert total_pnl == 500.0

    def test_trade_record(self):
        """Test TradeRecord dataclass."""
        portfolio_before = EvaluationPortfolioState(
            total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1)
        )
        portfolio_after = EvaluationPortfolioState(
            total_value=99950, cash=95000, positions={}, date=datetime(2024, 1, 1)
        )
        
        trade_record = TradeRecord(
            date=datetime(2024, 1, 1),
            ticker="aa",
            action=TradeAction.BUY,
            quantity=100,
            price=50.0,
            value=5000.0,
            transaction_cost=5.0,
            slippage=2.5,
            total_cost=5007.5,
            confidence=0.8,
            reasoning="Strong buy signal",
            expert_outputs={"sentiment": {"weight": 0.3, "confidence": 0.7}},
            portfolio_state_before=portfolio_before,
            portfolio_state_after=portfolio_after,
            success=True,
            error_message=None
        )
        
        assert trade_record.date == datetime(2024, 1, 1)
        assert trade_record.ticker == "aa"
        assert trade_record.action == TradeAction.BUY
        assert trade_record.quantity == 100
        assert trade_record.price == 50.0
        assert trade_record.value == 5000.0
        assert trade_record.transaction_cost == 5.0
        assert trade_record.slippage == 2.5
        assert trade_record.total_cost == 5007.5
        assert trade_record.confidence == 0.8
        assert trade_record.reasoning == "Strong buy signal"
        assert trade_record.success == True
        assert trade_record.error_message is None

    def test_daily_metrics(self):
        """Test DailyMetrics dataclass."""
        daily_metrics = DailyMetrics(
            date=datetime(2024, 1, 1),
            portfolio_value=100000,
            daily_return=0.001,
            cumulative_return=0.001,
            cash=100000,
            positions_value=0.0,
            total_pnl=0.0,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            num_positions=0,
            max_drawdown=0.0,
            volatility=0.01,
            sharpe_ratio=1.0,
            sortino_ratio=1.2
        )
        
        assert daily_metrics.date == datetime(2024, 1, 1)
        assert daily_metrics.portfolio_value == 100000
        assert daily_metrics.daily_return == 0.001
        assert daily_metrics.cumulative_return == 0.001
        assert daily_metrics.cash == 100000
        assert daily_metrics.positions_value == 0.0
        assert daily_metrics.num_positions == 0
        assert daily_metrics.volatility == 0.01
        assert daily_metrics.sharpe_ratio == 1.0
        assert daily_metrics.sortino_ratio == 1.2

    def test_evaluation_ticker_metrics(self):
        """Test EvaluationTickerMetrics dataclass."""
        ticker_metrics = EvaluationTickerMetrics(
            ticker="aa",
            total_return=0.1,
            annualized_return=0.12,
            sharpe_ratio=1.5,
            sortino_ratio=1.8,
            calmar_ratio=2.0,
            max_drawdown=0.05,
            drawdown_duration=10,
            volatility=0.15,
            win_rate=0.6,
            avg_win=0.02,
            avg_loss=-0.01,
            profit_factor=1.5,
            contribution_to_portfolio=0.08,
            num_trades=5,
            avg_hold_time=15.0
        )
        
        assert ticker_metrics.ticker == "aa"
        assert ticker_metrics.total_return == 0.1
        assert ticker_metrics.annualized_return == 0.12
        assert ticker_metrics.sharpe_ratio == 1.5
        assert ticker_metrics.sortino_ratio == 1.8
        assert ticker_metrics.calmar_ratio == 2.0
        assert ticker_metrics.max_drawdown == 0.05
        assert ticker_metrics.drawdown_duration == 10
        assert ticker_metrics.volatility == 0.15
        assert ticker_metrics.win_rate == 0.6
        assert ticker_metrics.avg_win == 0.02
        assert ticker_metrics.avg_loss == -0.01
        assert ticker_metrics.profit_factor == 1.5
        assert ticker_metrics.contribution_to_portfolio == 0.08
        assert ticker_metrics.num_trades == 5
        assert ticker_metrics.avg_hold_time == 15.0

    def test_evaluation_portfolio_metrics(self):
        """Test EvaluationPortfolioMetrics dataclass."""
        portfolio_metrics = EvaluationPortfolioMetrics(
            total_return=0.15,
            annualized_return=0.18,
            sharpe_ratio=1.2,
            sortino_ratio=1.5,
            calmar_ratio=1.8,
            max_drawdown=0.08,
            drawdown_duration=20,
            volatility=0.12,
            win_rate=0.55,
            profit_factor=1.3,
            total_trades=10,
            avg_trade_return=0.015,
            best_trade=0.05,
            worst_trade=-0.02,
            avg_hold_time=12.0,
            cash_drag=0.05,
            diversification_score=0.7
        )
        
        assert portfolio_metrics.total_return == 0.15
        assert portfolio_metrics.annualized_return == 0.18
        assert portfolio_metrics.sharpe_ratio == 1.2
        assert portfolio_metrics.sortino_ratio == 1.5
        assert portfolio_metrics.calmar_ratio == 1.8
        assert portfolio_metrics.max_drawdown == 0.08
        assert portfolio_metrics.drawdown_duration == 20
        assert portfolio_metrics.volatility == 0.12
        assert portfolio_metrics.win_rate == 0.55
        assert portfolio_metrics.profit_factor == 1.3
        assert portfolio_metrics.total_trades == 10
        assert portfolio_metrics.avg_trade_return == 0.015
        assert portfolio_metrics.best_trade == 0.05
        assert portfolio_metrics.worst_trade == -0.02
        assert portfolio_metrics.avg_hold_time == 12.0
        assert portfolio_metrics.cash_drag == 0.05
        assert portfolio_metrics.diversification_score == 0.7

    def test_evaluation_backtest_result(self):
        """Test EvaluationBacktestResult dataclass."""
        portfolio_history = [
            EvaluationPortfolioState(total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1))
        ]
        trade_log = []
        daily_metrics = []
        portfolio_metrics = EvaluationPortfolioMetrics(
            total_return=0.0, annualized_return=0.0, sharpe_ratio=0.0,
            sortino_ratio=0.0, calmar_ratio=0.0, max_drawdown=0.0,
            drawdown_duration=0, volatility=0.0, win_rate=0.0, profit_factor=0.0,
            total_trades=0, avg_trade_return=0.0, best_trade=0.0, worst_trade=0.0,
            avg_hold_time=0.0, cash_drag=0.0, diversification_score=0.0
        )
        ticker_metrics = {}
        data_coverage = {"total_decisions": 0, "successful_decisions": 0}
        configuration = {"initial_capital": 100000}
        
        backtest_result = EvaluationBacktestResult(
            portfolio_history=portfolio_history,
            trade_log=trade_log,
            daily_metrics=daily_metrics,
            portfolio_metrics=portfolio_metrics,
            ticker_metrics=ticker_metrics,
            data_coverage=data_coverage,
            configuration=configuration,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 5),
            total_days=5,
            trading_days=3,
            success_rate=1.0
        )
        
        assert len(backtest_result.portfolio_history) == 1
        assert len(backtest_result.trade_log) == 0
        assert len(backtest_result.daily_metrics) == 0
        assert backtest_result.portfolio_metrics == portfolio_metrics
        assert backtest_result.ticker_metrics == ticker_metrics
        assert backtest_result.data_coverage == data_coverage
        assert backtest_result.configuration == configuration
        assert backtest_result.start_date == datetime(2024, 1, 1)
        assert backtest_result.end_date == datetime(2024, 1, 5)
        assert backtest_result.total_days == 5
        assert backtest_result.trading_days == 3
        assert backtest_result.success_rate == 1.0


class TestConfigurationTypes:
    """Test cases for configuration dataclasses."""

    def test_trade_logger_config(self):
        """Test TradeLoggerConfig dataclass."""
        config = TradeLoggerConfig(
            output_dir="./logs",
            log_level="INFO",
            enable_compression=True,
            max_file_size_mb=100,
            backup_count=5,
            flush_interval=100
        )
        
        assert config.output_dir == "./logs"
        assert config.log_level == "INFO"
        assert config.enable_compression == True
        assert config.max_file_size_mb == 100
        assert config.backup_count == 5
        assert config.flush_interval == 100

    def test_portfolio_simulator_config(self):
        """Test PortfolioSimulatorConfig dataclass."""
        config = PortfolioSimulatorConfig(
            initial_capital=100000,
            position_sizing=0.08,
            max_positions=10,
            cash_reserve=0.2,
            min_cash_reserve=0.1,
            transaction_cost=0.001,
            slippage=0.0005,
            enable_short_selling=False,
            enable_margin=False,
            max_position_size=0.25
        )
        
        assert config.initial_capital == 100000
        assert config.position_sizing == 0.08
        assert config.max_positions == 10
        assert config.cash_reserve == 0.2
        assert config.min_cash_reserve == 0.1
        assert config.transaction_cost == 0.001
        assert config.slippage == 0.0005
        assert config.enable_short_selling == False
        assert config.enable_margin == False
        assert config.max_position_size == 0.25

    def test_backtester_config(self):
        """Test BacktesterConfig dataclass."""
        config = BacktesterConfig(
            start_date="2024-01-01",
            end_date="2024-12-31",
            tickers=["aa", "aaau"],
            initial_capital=100000,
            position_sizing=0.08,
            max_positions=10,
            cash_reserve=0.2,
            min_cash_reserve=0.1,
            transaction_cost=0.001,
            slippage=0.0005,
            log_level="INFO",
            enable_real_time_metrics=True,
            save_intermediate_results=True,
            checkpoint_interval=30
        )
        
        assert config.start_date == "2024-01-01"
        assert config.end_date == "2024-12-31"
        assert config.tickers == ["aa", "aaau"]
        assert config.initial_capital == 100000
        assert config.position_sizing == 0.08
        assert config.max_positions == 10
        assert config.cash_reserve == 0.2
        assert config.min_cash_reserve == 0.1
        assert config.transaction_cost == 0.001
        assert config.slippage == 0.0005
        assert config.log_level == "INFO"
        assert config.enable_real_time_metrics == True
        assert config.save_intermediate_results == True
        assert config.checkpoint_interval == 30


class TestHelperFunctions:
    """Test cases for helper functions."""

    def test_create_evaluation_portfolio_state(self):
        """Test create_evaluation_portfolio_state helper function."""
        positions = {
            "aa": EvaluationPosition("aa", 100, 50.0, 55.0, PositionStatus.OPEN, 500.0, 0.0)
        }
        
        portfolio_state = create_evaluation_portfolio_state(
            cash=95000.0,
            positions=positions,
            date=datetime(2024, 1, 1),
            daily_return=0.005
        )
        
        assert isinstance(portfolio_state, EvaluationPortfolioState)
        assert portfolio_state.cash == 95000.0
        assert portfolio_state.positions == positions
        assert portfolio_state.date == datetime(2024, 1, 1)
        assert portfolio_state.daily_return == 0.005
        assert portfolio_state.total_value == 100500.0  # 95000 + 100*55

    def test_create_trade_record(self):
        """Test create_trade_record helper function."""
        portfolio_before = EvaluationPortfolioState(
            total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1)
        )
        portfolio_after = EvaluationPortfolioState(
            total_value=99950, cash=95000, positions={}, date=datetime(2024, 1, 1)
        )
        
        trade_record = create_trade_record(
            date=datetime(2024, 1, 1),
            ticker="aa",
            action=TradeAction.BUY,
            quantity=100,
            price=50.0,
            confidence=0.8,
            reasoning="Test trade",
            expert_outputs={"sentiment": {"weight": 0.3}},
            portfolio_state_before=portfolio_before,
            portfolio_state_after=portfolio_after
        )
        
        assert isinstance(trade_record, TradeRecord)
        assert trade_record.date == datetime(2024, 1, 1)
        assert trade_record.ticker == "aa"
        assert trade_record.action == TradeAction.BUY
        assert trade_record.quantity == 100
        assert trade_record.price == 50.0
        assert trade_record.value == 5000.0
        assert trade_record.confidence == 0.8
        assert trade_record.reasoning == "Test trade"
        assert trade_record.expert_outputs == {"sentiment": {"weight": 0.3}}
        assert trade_record.portfolio_state_before == portfolio_before
        assert trade_record.portfolio_state_after == portfolio_after
        assert trade_record.success == True
        assert trade_record.error_message is None


if __name__ == "__main__":
    pytest.main([__file__]) 