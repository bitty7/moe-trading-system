#!/usr/bin/env python3
"""
Portfolio Simulator Implementation

Simulates a realistic trading portfolio, tracking positions, cash, and portfolio value
over time based on expert trading decisions.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd

from core.data_types import (
    EvaluationPosition as Position, EvaluationPortfolioState as PortfolioState, TradeRecord, TradeAction, PositionStatus,
    PortfolioSimulatorConfig, create_evaluation_portfolio_state as create_portfolio_state, create_trade_record
)

logger = logging.getLogger(__name__)

class PortfolioSimulator:
    """
    Simulates a realistic trading portfolio with position management,
    cash handling, and risk controls.
    """
    
    def __init__(self, config: PortfolioSimulatorConfig):
        """
        Initialize portfolio simulator.
        
        Args:
            config: Portfolio simulation configuration
        """
        self.config = config
        self.initial_capital = config.initial_capital
        self.cash = config.initial_capital
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[TradeRecord] = []
        self.portfolio_history: List[PortfolioState] = []
        
        # Initialize portfolio state
        self.current_state = create_portfolio_state(
            cash=self.cash,
            positions=self.positions,
            date=datetime.now()
        )
        # Manually set the total value since it's calculated in __post_init__
        self.current_state.total_value = self.initial_capital
        
        logger.info(f"Portfolio simulator initialized with ${self.initial_capital:,.2f} capital")
        logger.info(f"Position sizing: {self.config.position_sizing:.1%}")
        logger.info(f"Cash reserve: {self.config.cash_reserve:.1%}")
        logger.info(f"Transaction cost: {self.config.transaction_cost:.3%}")
    
    def get_portfolio_state(self) -> PortfolioState:
        """Get current portfolio state."""
        return self.current_state
    
    def reset(self, initial_state: PortfolioState):
        """Reset portfolio to initial state."""
        self.cash = initial_state.cash
        self.positions = initial_state.positions.copy()
        self.current_state = initial_state
        self.portfolio_history = [initial_state]
        self.trade_history = []
        logger.info(f"Portfolio reset to initial state with ${self.cash:,.2f} cash")
    
    def calculate_position_size(self, ticker: str, price: float, confidence: float) -> int:
        """
        Calculate position size based on position sizing rules.
        
        Args:
            ticker: Stock ticker
            price: Current stock price
            confidence: Expert confidence score
            
        Returns:
            Number of shares to trade
        """
        # Validate inputs
        if price <= 0 or np.isnan(price):
            logger.warning(f"Invalid price for {ticker}: {price}")
            return 0
        
        if np.isnan(confidence):
            confidence = 0.5  # Default confidence if NaN
        
        # Base position size as percentage of portfolio
        base_size = self.current_state.total_value * self.config.position_sizing
        
        # Adjust for confidence (higher confidence = larger position)
        confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5 to 1.0
        adjusted_size = base_size * confidence_multiplier
        
        # Calculate number of shares
        shares = int(adjusted_size / price)
        
        # Apply maximum position size limit
        max_position_value = self.current_state.total_value * self.config.max_position_size
        max_shares = int(max_position_value / price)
        shares = min(shares, max_shares)
        
        # Ensure minimum position size
        min_position_value = self.current_state.total_value * 0.01  # 1% minimum
        min_shares = max(1, int(min_position_value / price))
        shares = max(shares, min_shares)
        
        return shares
    
    def check_cash_availability(self, required_cash: float) -> Tuple[bool, float, str]:
        """
        Check if sufficient cash is available for trade.
        
        Returns:
            (is_available, available_amount, message)
        """
        # Calculate required cash reserve
        required_reserve = self.current_state.total_value * self.config.min_cash_reserve
        
        # Available cash for trading
        available_cash = self.cash - required_reserve
        
        if available_cash >= required_cash:
            return True, available_cash, "Sufficient cash available"
        else:
            return False, available_cash, f"Insufficient cash. Required: ${required_cash:,.2f}, Available: ${available_cash:,.2f}"
    
    def execute_trade(self, ticker: str, action: TradeAction, price: float, 
                     confidence: float, reasoning: str, expert_outputs: Dict,
                     date: datetime) -> TradeRecord:
        """
        Execute a trading decision.
        
        Args:
            ticker: Stock ticker
            action: Trading action (BUY/SELL/HOLD)
            price: Current stock price
            confidence: Expert confidence score
            reasoning: Decision reasoning
            expert_outputs: Expert outputs
            date: Trade date
            
        Returns:
            Trade record
        """
        # Store portfolio state before trade
        portfolio_state_before = self.current_state
        
        if action == TradeAction.HOLD:
            # No trade execution for HOLD
            return create_trade_record(
                date=date,
                ticker=ticker,
                action=action,
                quantity=0,
                price=price,
                confidence=confidence,
                reasoning=reasoning,
                expert_outputs=expert_outputs,
                portfolio_state_before=portfolio_state_before,
                portfolio_state_after=self.current_state,
                success=True
            )
        
        # Calculate position size
        quantity = self.calculate_position_size(ticker, price, confidence)
        
        if action == TradeAction.BUY:
            return self._execute_buy(ticker, quantity, price, confidence, 
                                   reasoning, expert_outputs, date, portfolio_state_before)
        elif action == TradeAction.SELL:
            return self._execute_sell(ticker, quantity, price, confidence,
                                    reasoning, expert_outputs, date, portfolio_state_before)
        else:
            raise ValueError(f"Invalid action: {action}")
    
    def _execute_buy(self, ticker: str, quantity: int, price: float, confidence: float,
                    reasoning: str, expert_outputs: Dict, date: datetime,
                    portfolio_state_before: PortfolioState) -> TradeRecord:
        """Execute buy order."""
        # Calculate required cash
        trade_value = quantity * price
        transaction_cost = trade_value * self.config.transaction_cost
        slippage = trade_value * self.config.slippage
        total_cost = trade_value + transaction_cost + slippage
        
        # Check cash availability
        is_available, available_cash, message = self.check_cash_availability(total_cost)
        
        if not is_available:
            # Try partial execution
            denominator = price * (1 + self.config.transaction_cost + self.config.slippage)
            if denominator > 0 and not np.isnan(denominator):
                max_quantity = int(available_cash / denominator)
            else:
                max_quantity = 0
                
            if max_quantity > 0:
                quantity = max_quantity
                trade_value = quantity * price
                transaction_cost = trade_value * self.config.transaction_cost
                slippage = trade_value * self.config.slippage
                total_cost = trade_value + transaction_cost + slippage
                message = f"Partial execution: {quantity} shares (insufficient cash for full order)"
            else:
                # Cannot execute any part of the order
                return create_trade_record(
                    date=date,
                    ticker=ticker,
                    action=TradeAction.BUY,
                    quantity=0,
                    price=price,
                    confidence=confidence,
                    reasoning=reasoning,
                    expert_outputs=expert_outputs,
                    portfolio_state_before=portfolio_state_before,
                    portfolio_state_after=self.current_state,
                    success=False,
                    error_message=f"Cannot execute buy order: {message}"
                )
        
        # Execute the trade
        self.cash -= total_cost
        
        if ticker in self.positions:
            # Add to existing position
            self.positions[ticker].add_quantity(quantity, price)
        else:
            # Create new position
            self.positions[ticker] = Position(
                ticker=ticker,
                quantity=quantity,
                avg_price=price,
                current_price=price
            )
        
        # Update portfolio state
        self._update_portfolio_state(date)
        
        # Create trade record
        trade_record = create_trade_record(
            date=date,
            ticker=ticker,
            action=TradeAction.BUY,
            quantity=quantity,
            price=price,
            confidence=confidence,
            reasoning=reasoning,
            expert_outputs=expert_outputs,
            portfolio_state_before=portfolio_state_before,
            portfolio_state_after=self.current_state,
            success=True
        )
        
        if "Partial execution" in message:
            trade_record.error_message = message
        
        self.trade_history.append(trade_record)
        
        logger.info(f"BUY {quantity} shares of {ticker} at ${price:.2f} (${total_cost:,.2f})")
        return trade_record
    
    def _execute_sell(self, ticker: str, quantity: int, price: float, confidence: float,
                     reasoning: str, expert_outputs: Dict, date: datetime,
                     portfolio_state_before: PortfolioState) -> TradeRecord:
        """Execute sell order."""
        if ticker not in self.positions:
            return create_trade_record(
                date=date,
                ticker=ticker,
                action=TradeAction.SELL,
                quantity=0,
                price=price,
                confidence=confidence,
                reasoning=reasoning,
                expert_outputs=expert_outputs,
                portfolio_state_before=portfolio_state_before,
                portfolio_state_after=self.current_state,
                success=False,
                error_message=f"No position in {ticker} to sell"
            )
        
        position = self.positions[ticker]
        available_quantity = position.quantity
        
        if quantity > available_quantity:
            # Adjust quantity to available shares
            quantity = available_quantity
            message = f"Partial sell: {quantity} shares (insufficient shares for full order)"
        else:
            message = "Full sell order executed"
        
        # Calculate trade proceeds
        trade_value = quantity * price
        transaction_cost = trade_value * self.config.transaction_cost
        slippage = trade_value * self.config.slippage
        net_proceeds = trade_value - transaction_cost - slippage
        
        # Execute the trade
        self.cash += net_proceeds
        position.reduce_quantity(quantity, price)
        
        # Remove position if fully closed
        if position.quantity == 0:
            del self.positions[ticker]
        
        # Update portfolio state
        self._update_portfolio_state(date)
        
        # Create trade record
        trade_record = create_trade_record(
            date=date,
            ticker=ticker,
            action=TradeAction.SELL,
            quantity=quantity,
            price=price,
            confidence=confidence,
            reasoning=reasoning,
            expert_outputs=expert_outputs,
            portfolio_state_before=portfolio_state_before,
            portfolio_state_after=self.current_state,
            success=True
        )
        
        if "Partial sell" in message:
            trade_record.error_message = message
        
        self.trade_history.append(trade_record)
        
        logger.info(f"SELL {quantity} shares of {ticker} at ${price:.2f} (${net_proceeds:,.2f})")
        return trade_record
    
    def update_prices(self, price_updates: Dict[str, float], date: datetime):
        """
        Update stock prices and recalculate portfolio value.
        
        Args:
            price_updates: Dict of ticker -> new price
            date: Update date
        """
        for ticker, new_price in price_updates.items():
            # Validate price before updating
            if pd.isna(new_price) or new_price <= 0:
                logger.warning(f"Skipping invalid price update for {ticker}: {new_price}")
                continue
                
            if ticker in self.positions:
                self.positions[ticker].update_price(new_price)
        
        self._update_portfolio_state(date)
    
    def _update_portfolio_state(self, date: datetime):
        """Update current portfolio state."""
        # Calculate cash reserve
        cash_reserve = self.current_state.total_value * self.config.cash_reserve
        available_capital = self.cash - cash_reserve
        
        # Calculate daily return if we have previous state
        daily_return = 0.0
        if self.portfolio_history:
            prev_value = self.portfolio_history[-1].total_value
            if prev_value > 0 and not pd.isna(prev_value) and not pd.isna(self.current_state.total_value):
                daily_return = (self.current_state.total_value - prev_value) / prev_value
                # Handle any remaining NaN
                if pd.isna(daily_return):
                    daily_return = 0.0
        
        # Create new portfolio state
        self.current_state = create_portfolio_state(
            cash=self.cash,
            positions=self.positions,
            date=date,
            daily_return=daily_return
        )
        
        # Set additional fields
        self.current_state.cash_reserve = cash_reserve
        self.current_state.available_capital = available_capital
        
        # Add to history
        self.portfolio_history.append(self.current_state)
    
    def get_performance_summary(self) -> Dict:
        """Get portfolio performance summary."""
        if not self.portfolio_history:
            return {"error": "No portfolio history available"}
        
        initial_value = self.initial_capital
        final_value = self.current_state.total_value
        total_return = (final_value - initial_value) / initial_value
        
        # Calculate max drawdown
        peak_value = initial_value
        max_drawdown = 0.0
        
        for state in self.portfolio_history:
            if state.total_value > peak_value:
                peak_value = state.total_value
            else:
                drawdown = (peak_value - state.total_value) / peak_value
                max_drawdown = max(max_drawdown, drawdown)
        
        return {
            "initial_capital": initial_value,
            "final_value": final_value,
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown * 100,
            "total_trades": len(self.trade_history),
            "num_positions": len(self.positions),
            "cash": self.cash,
            "cash_pct": (self.cash / final_value) * 100 if final_value > 0 else 0
        }
    
    def get_position_summary(self) -> Dict[str, Dict]:
        """Get summary of all positions."""
        summary = {}
        for ticker, position in self.positions.items():
            summary[ticker] = {
                "quantity": position.quantity,
                "avg_price": position.avg_price,
                "current_price": position.current_price,
                "unrealized_pnl": position.unrealized_pnl,
                "realized_pnl": position.realized_pnl,
                "total_pnl": position.unrealized_pnl + position.realized_pnl,
                "return_pct": ((position.current_price - position.avg_price) / position.avg_price) * 100
            }
        return summary 