#!/usr/bin/env python3
"""
Unit tests for the MetricsCalculator class with unified data types.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pytest

from evaluation.metrics import MetricsCalculator
from core.data_types import (
    TradeRecord, EvaluationPortfolioState as PortfolioState, DailyMetrics,
    EvaluationTickerMetrics as TickerMetrics, EvaluationPortfolioMetrics as PortfolioMetrics,
    TradeAction, PositionStatus
)


class TestMetricsCalculator:
    """Test cases for MetricsCalculator class."""

    def setup_method(self):
        """Set up test environment."""
        self.calculator = MetricsCalculator()

    def test_calculate_daily_metrics(self):
        """Test daily metrics calculation."""
        # Create sample portfolio history
        portfolio_history = []
        for i in range(5):
            date = datetime(2024, 1, 1 + i)
            portfolio_state = PortfolioState(
                total_value=100000 + i * 100,
                cash=100000 - i * 50,
                positions={},
                date=date,
                daily_return=0.001 * (i + 1)
            )
            portfolio_history.append(portfolio_state)

        # Create sample trade log
        trade_log = [
            TradeRecord(
                date=datetime(2024, 1, 2), ticker="aa", action=TradeAction.BUY,
                quantity=100, price=50.0, value=5000.0, transaction_cost=5.0, slippage=2.5,
                total_cost=5007.5, confidence=0.8, reasoning="Test", expert_outputs={},
                portfolio_state_before=PortfolioState(total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 2)),
                portfolio_state_after=PortfolioState(total_value=99950, cash=95000, positions={}, date=datetime(2024, 1, 2))
            )
        ]

        daily_metrics = self.calculator.calculate_daily_metrics(portfolio_history, trade_log)

        assert isinstance(daily_metrics, list)
        assert len(daily_metrics) == 5
        
        # Check first daily metrics
        first_metrics = daily_metrics[0]
        assert first_metrics.date == datetime(2024, 1, 1)
        assert first_metrics.portfolio_value == 100000
        assert first_metrics.daily_return == 0.001
        assert first_metrics.cash == 100000
        assert first_metrics.positions_value == 0.0

    def test_calculate_portfolio_metrics(self):
        """Test portfolio metrics calculation."""
        # Create sample daily metrics
        daily_metrics = []
        for i in range(10):
            daily_return = 0.001 * (i % 3 - 1)  # Mix of positive and negative returns
            daily_metrics.append(DailyMetrics(
                date=datetime(2024, 1, 1 + i),
                portfolio_value=100000 + i * 100,
                daily_return=daily_return,
                cumulative_return=0.001 * i,
                cash=100000 - i * 50,
                positions_value=i * 50,
                total_pnl=i * 100,
                unrealized_pnl=i * 50,
                realized_pnl=i * 50,
                num_positions=i % 3,
                max_drawdown=0.0,
                volatility=0.01,
                sharpe_ratio=1.0,
                sortino_ratio=1.2
            ))

        # Create sample trade log
        trade_log = [
            TradeRecord(
                date=datetime(2024, 1, 2), ticker="aa", action=TradeAction.BUY,
                quantity=100, price=50.0, value=5000.0, transaction_cost=5.0, slippage=2.5,
                total_cost=5007.5, confidence=0.8, reasoning="Test", expert_outputs={},
                portfolio_state_before=PortfolioState(total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 2)),
                portfolio_state_after=PortfolioState(total_value=99950, cash=95000, positions={}, date=datetime(2024, 1, 2))
            ),
            TradeRecord(
                date=datetime(2024, 1, 5), ticker="aa", action=TradeAction.SELL,
                quantity=100, price=55.0, value=5500.0, transaction_cost=5.5, slippage=2.75,
                total_cost=5508.25, confidence=0.7, reasoning="Test sell", expert_outputs={},
                portfolio_state_before=PortfolioState(total_value=100500, cash=95000, positions={}, date=datetime(2024, 1, 5)),
                portfolio_state_after=PortfolioState(total_value=100500, cash=100500, positions={}, date=datetime(2024, 1, 5))
            )
        ]

        portfolio_metrics = self.calculator.calculate_portfolio_metrics(daily_metrics, trade_log)

        assert isinstance(portfolio_metrics, PortfolioMetrics)
        assert portfolio_metrics.total_trades == 2
        assert portfolio_metrics.total_return > 0  # Should be positive based on our data
        assert portfolio_metrics.sharpe_ratio is not None
        assert portfolio_metrics.max_drawdown >= 0
        assert portfolio_metrics.volatility > 0

    def test_calculate_ticker_metrics(self):
        """Test ticker-specific metrics calculation."""
        # Create sample trade log with multiple tickers
        trade_log = [
            TradeRecord(
                date=datetime(2024, 1, 2), ticker="aa", action=TradeAction.BUY,
                quantity=100, price=50.0, value=5000.0, transaction_cost=5.0, slippage=2.5,
                total_cost=5007.5, confidence=0.8, reasoning="Buy aa", expert_outputs={},
                portfolio_state_before=PortfolioState(total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 2)),
                portfolio_state_after=PortfolioState(total_value=99950, cash=95000, positions={}, date=datetime(2024, 1, 2))
            ),
            TradeRecord(
                date=datetime(2024, 1, 5), ticker="aa", action=TradeAction.SELL,
                quantity=100, price=55.0, value=5500.0, transaction_cost=5.5, slippage=2.75,
                total_cost=5508.25, confidence=0.7, reasoning="Sell aa", expert_outputs={},
                portfolio_state_before=PortfolioState(total_value=100500, cash=95000, positions={}, date=datetime(2024, 1, 5)),
                portfolio_state_after=PortfolioState(total_value=100500, cash=100500, positions={}, date=datetime(2024, 1, 5))
            ),
            TradeRecord(
                date=datetime(2024, 1, 3), ticker="aaau", action=TradeAction.BUY,
                quantity=200, price=20.0, value=4000.0, transaction_cost=4.0, slippage=2.0,
                total_cost=4006.0, confidence=0.6, reasoning="Buy aaau", expert_outputs={},
                portfolio_state_before=PortfolioState(total_value=100100, cash=95000, positions={}, date=datetime(2024, 1, 3)),
                portfolio_state_after=PortfolioState(total_value=100100, cash=91000, positions={}, date=datetime(2024, 1, 3))
            )
        ]

        ticker_metrics = self.calculator.calculate_ticker_metrics(trade_log)

        assert isinstance(ticker_metrics, dict)
        assert "aa" in ticker_metrics
        assert "aaau" in ticker_metrics

        # Check aa metrics
        aa_metrics = ticker_metrics["aa"]
        assert isinstance(aa_metrics, TickerMetrics)
        assert aa_metrics.ticker == "aa"
        assert aa_metrics.num_trades == 2
        assert aa_metrics.total_return > 0  # Should be positive (buy at 50, sell at 55)

        # Check aaau metrics
        aaau_metrics = ticker_metrics["aaau"]
        assert isinstance(aaau_metrics, TickerMetrics)
        assert aaau_metrics.ticker == "aaau"
        assert aaau_metrics.num_trades == 1
        assert aaau_metrics.total_return == 0.0  # No sell trade yet

    def test_calculate_returns(self):
        """Test return calculations."""
        # Test simple return calculation
        initial_value = 100000
        final_value = 110000
        total_return = self.calculator._calculate_total_return(initial_value, final_value)
        assert total_return == 0.1  # 10% return

        # Test annualized return calculation
        days = 365
        annualized_return = self.calculator._calculate_annualized_return(total_return, days)
        assert annualized_return == 0.1  # Same as total return for 1 year

        # Test for shorter period
        days_short = 30
        annualized_return_short = self.calculator._calculate_annualized_return(total_return, days_short)
        assert annualized_return_short > total_return  # Should be higher for shorter period

    def test_calculate_risk_metrics(self):
        """Test risk metrics calculations."""
        # Create sample returns
        returns = [0.01, -0.005, 0.02, -0.01, 0.015, -0.008, 0.012, -0.003, 0.018, -0.006]
        
        # Test volatility calculation
        volatility = self.calculator._calculate_volatility(returns)
        assert volatility > 0
        assert isinstance(volatility, float)

        # Test Sharpe ratio calculation
        risk_free_rate = 0.02  # 2% annual risk-free rate
        sharpe_ratio = self.calculator._calculate_sharpe_ratio(returns, risk_free_rate)
        assert isinstance(sharpe_ratio, float)

        # Test Sortino ratio calculation
        sortino_ratio = self.calculator._calculate_sortino_ratio(returns, risk_free_rate)
        assert isinstance(sortino_ratio, float)

        # Test maximum drawdown calculation
        portfolio_values = [100000, 101000, 100495, 102504.9, 101479.85, 102998.26, 101773.23, 102994.42, 104847.71, 104218.71]
        max_drawdown, drawdown_duration = self.calculator._calculate_max_drawdown(portfolio_values)
        assert max_drawdown >= 0
        assert drawdown_duration >= 0

    def test_calculate_trade_metrics(self):
        """Test trade-specific metrics calculation."""
        # Create sample trade log
        trade_log = [
            TradeRecord(
                date=datetime(2024, 1, 2), ticker="aa", action=TradeAction.BUY,
                quantity=100, price=50.0, value=5000.0, transaction_cost=5.0, slippage=2.5,
                total_cost=5007.5, confidence=0.8, reasoning="Buy", expert_outputs={},
                portfolio_state_before=PortfolioState(total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 2)),
                portfolio_state_after=PortfolioState(total_value=99950, cash=95000, positions={}, date=datetime(2024, 1, 2))
            ),
            TradeRecord(
                date=datetime(2024, 1, 5), ticker="aa", action=TradeAction.SELL,
                quantity=100, price=55.0, value=5500.0, transaction_cost=5.5, slippage=2.75,
                total_cost=5508.25, confidence=0.7, reasoning="Sell", expert_outputs={},
                portfolio_state_before=PortfolioState(total_value=100500, cash=95000, positions={}, date=datetime(2024, 1, 5)),
                portfolio_state_after=PortfolioState(total_value=100500, cash=100500, positions={}, date=datetime(2024, 1, 5))
            ),
            TradeRecord(
                date=datetime(2024, 1, 8), ticker="aa", action=TradeAction.BUY,
                quantity=100, price=45.0, value=4500.0, transaction_cost=4.5, slippage=2.25,
                total_cost=4506.75, confidence=0.9, reasoning="Buy again", expert_outputs={},
                portfolio_state_before=PortfolioState(total_value=100600, cash=100500, positions={}, date=datetime(2024, 1, 8)),
                portfolio_state_after=PortfolioState(total_value=100600, cash=95993.25, positions={}, date=datetime(2024, 1, 8))
            )
        ]

        # Calculate trade metrics
        win_rate, avg_win, avg_loss, profit_factor = self.calculator._calculate_trade_metrics(trade_log)

        assert win_rate >= 0 and win_rate <= 1
        assert avg_win >= 0
        assert avg_loss <= 0
        assert profit_factor >= 0

    def test_empty_data_handling(self):
        """Test handling of empty data scenarios."""
        # Test with empty portfolio history
        empty_daily_metrics = self.calculator.calculate_daily_metrics([], [])
        assert empty_daily_metrics == []

        # Test with empty trade log
        portfolio_history = [
            PortfolioState(
                total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1)
            )
        ]
        daily_metrics = self.calculator.calculate_daily_metrics(portfolio_history, [])
        assert len(daily_metrics) == 1

        # Test portfolio metrics with empty data
        portfolio_metrics = self.calculator.calculate_portfolio_metrics([], [])
        assert isinstance(portfolio_metrics, PortfolioMetrics)
        assert portfolio_metrics.total_trades == 0
        assert portfolio_metrics.total_return == 0.0

        # Test ticker metrics with empty data
        ticker_metrics = self.calculator.calculate_ticker_metrics([])
        assert ticker_metrics == {}

    def test_edge_cases(self):
        """Test edge cases in metrics calculation."""
        # Test with single day
        single_day_metrics = self.calculator.calculate_daily_metrics([
            PortfolioState(total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1))
        ], [])
        assert len(single_day_metrics) == 1

        # Test with zero returns
        zero_returns = [0.0, 0.0, 0.0, 0.0, 0.0]
        volatility = self.calculator._calculate_volatility(zero_returns)
        assert volatility == 0.0

        # Test with all negative returns
        negative_returns = [-0.01, -0.02, -0.015, -0.025, -0.01]
        sharpe_ratio = self.calculator._calculate_sharpe_ratio(negative_returns, 0.02)
        assert sharpe_ratio < 0

        # Test with all positive returns
        positive_returns = [0.01, 0.02, 0.015, 0.025, 0.01]
        sharpe_ratio = self.calculator._calculate_sharpe_ratio(positive_returns, 0.02)
        assert sharpe_ratio > 0

    def test_data_type_compatibility(self):
        """Test that metrics calculator works with unified data types."""
        # Test that we can create all required data types
        portfolio_state = PortfolioState(
            total_value=100000, cash=100000, positions={}, date=datetime(2024, 1, 1)
        )
        assert isinstance(portfolio_state, PortfolioState)

        trade_record = TradeRecord(
            date=datetime(2024, 1, 1), ticker="aa", action=TradeAction.BUY,
            quantity=100, price=50.0, value=5000.0, transaction_cost=5.0, slippage=2.5,
            total_cost=5007.5, confidence=0.8, reasoning="Test", expert_outputs={},
            portfolio_state_before=portfolio_state, portfolio_state_after=portfolio_state
        )
        assert isinstance(trade_record, TradeRecord)

        daily_metrics = DailyMetrics(
            date=datetime(2024, 1, 1), portfolio_value=100000, daily_return=0.001,
            cumulative_return=0.001, cash=100000, positions_value=0.0, total_pnl=0.0,
            unrealized_pnl=0.0, realized_pnl=0.0, num_positions=0, max_drawdown=0.0,
            volatility=0.01, sharpe_ratio=1.0, sortino_ratio=1.2
        )
        assert isinstance(daily_metrics, DailyMetrics)


if __name__ == "__main__":
    pytest.main([__file__]) 