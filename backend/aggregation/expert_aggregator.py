#!/usr/bin/env python3
"""
expert_aggregator.py

Expert aggregation system that combines outputs from all four experts.
Implements both uniform and dynamic weighting strategies using a gating network.
Provides final trading decisions with confidence scores and reasoning.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass

from core.logging_config import get_logger
from core.data_types import ExpertOutput, DecisionProbabilities, TradeDecision, DecisionType, DecisionConfidence, DecisionMetadata
from experts.sentiment_expert import sentiment_expert
from experts.technical_timeseries_expert import technical_timeseries_expert
from experts.fundamental_expert import fundamental_expert
from experts.chart_expert import chart_expert
from data_loader.load_prices import load_prices_for_ticker

logger = get_logger("expert_aggregator")

@dataclass
class ExpertContribution:
    """Individual expert contribution to final decision."""
    expert_name: str
    expert_output: ExpertOutput
    weight: float
    contribution: DecisionProbabilities
    confidence: float
    processing_time: float

@dataclass
class AggregationResult:
    """Result of expert aggregation."""
    final_probabilities: DecisionProbabilities
    expert_contributions: Dict[str, ExpertContribution]
    aggregation_method: str
    gating_weights: Dict[str, float]
    overall_confidence: float
    decision_type: DecisionType
    reasoning: str
    processing_time: float

class ExpertAggregator:
    """
    Aggregates outputs from all four experts using dynamic weighting.
    """
    
    def __init__(self):
        """
        Initialize expert aggregator with dynamic weighting.
        """
        self.expert_names = ['sentiment', 'technical', 'fundamental', 'chart']
        logger.info("Expert aggregator initialized with dynamic weighting")
    
    def aggregate_experts(self, ticker: str, target_date: str, 
                         lookback_days: int = 7, lookback_years: int = 2) -> AggregationResult:
        """
        Run all experts and aggregate their outputs.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date for analysis (YYYY-MM-DD)
            lookback_days (int): Lookback period for sentiment and technical experts
            lookback_years (int): Lookback period for fundamental and chart experts
            
        Returns:
            AggregationResult: Aggregated expert outputs
        """
        start_time = time.time()
        
        try:
            # Run all experts
            expert_outputs = self._run_all_experts(ticker, target_date, lookback_days, lookback_years)
            
            if not expert_outputs:
                logger.warning(f"No expert outputs available for {ticker}")
                return self._create_fallback_result(start_time)
            
            # Calculate gating weights
            gating_weights = self._calculate_gating_weights(expert_outputs)
            
            # Aggregate expert outputs
            final_probabilities = self._aggregate_probabilities(expert_outputs, gating_weights)
            
            # Create expert contributions
            expert_contributions = self._create_expert_contributions(expert_outputs, gating_weights)
            
            # Determine final decision
            decision_type = self._determine_decision(final_probabilities)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(expert_contributions)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(expert_contributions, decision_type)
            
            processing_time = time.time() - start_time
            
            return AggregationResult(
                final_probabilities=final_probabilities,
                expert_contributions=expert_contributions,
                aggregation_method="dynamic_gating",
                gating_weights=gating_weights,
                overall_confidence=overall_confidence,
                decision_type=decision_type,
                reasoning=reasoning,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in expert aggregation for {ticker}: {e}")
            return self._create_fallback_result(start_time)
    
    def _run_all_experts(self, ticker: str, target_date: str, 
                        lookback_days: int, lookback_years: int) -> Dict[str, ExpertOutput]:
        """
        Run all four experts and collect their outputs.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date
            lookback_days (int): Lookback for sentiment/technical
            lookback_years (int): Lookback for fundamental/chart
            
        Returns:
            Dict[str, ExpertOutput]: Expert outputs by name
        """
        expert_outputs = {}
        
        try:
            # Run sentiment expert
            logger.info(f"Running sentiment expert for {ticker}")
            sentiment_result = sentiment_expert(ticker, target_date, lookback_days)
            if sentiment_result:
                expert_outputs['sentiment'] = sentiment_result
            
            # Run technical expert
            logger.info(f"Running technical expert for {ticker}")
            price_data = load_prices_for_ticker(ticker)
            if price_data is not None:
                technical_result = technical_timeseries_expert(price_data, ticker)
                if technical_result:
                    expert_outputs['technical'] = technical_result
            
            # Run fundamental expert
            logger.info(f"Running fundamental expert for {ticker}")
            fundamental_result = fundamental_expert(ticker, target_date, lookback_years)
            if fundamental_result:
                expert_outputs['fundamental'] = fundamental_result
            
            # Run chart expert
            logger.info(f"Running chart expert for {ticker}")
            chart_result = chart_expert(ticker, target_date, lookback_years)
            if chart_result:
                expert_outputs['chart'] = chart_result
            
            logger.info(f"Successfully ran {len(expert_outputs)} experts for {ticker}")
            return expert_outputs
            
        except Exception as e:
            logger.error(f"Error running experts for {ticker}: {e}")
            return expert_outputs
    
    def _calculate_gating_weights(self, expert_outputs: Dict[str, ExpertOutput]) -> Dict[str, float]:
        """
        Calculate dynamic weights for each expert using gating network logic.
        
        Args:
            expert_outputs (Dict[str, ExpertOutput]): Expert outputs
            
        Returns:
            Dict[str, float]: Weights for each expert
        """
        # Dynamic weighting based on confidence and data quality
        weights = {}
        total_weight = 0.0
        
        for name, output in expert_outputs.items():
            # Base weight from expert confidence
            confidence_weight = output.confidence.confidence_score
            
            # Data quality bonus
            data_quality_bonus = output.metadata.input_data_quality * 0.4
            
            # Decision certainty bonus (lower entropy = higher certainty)
            probabilities = output.probabilities.to_list()
            entropy = -sum(p * np.log(p + 1e-10) for p in probabilities if p > 0)
            certainty_bonus = (1.0 - entropy / np.log(3)) * 0.4  # Normalize to [0, 1]
            
            # Calculate final weight (removed processing time penalty)
            weight = confidence_weight + data_quality_bonus + certainty_bonus
            weights[name] = max(0.1, weight)  # Minimum weight of 0.1
            total_weight += weights[name]
        
        # Normalize weights to sum to 1.0
        if total_weight > 0:
            weights = {name: weight / total_weight for name, weight in weights.items()}
        else:
            # Fallback to uniform weights
            num_experts = len(expert_outputs)
            weights = {name: 1.0 / num_experts for name in expert_outputs.keys()}
        
        logger.info(f"Calculated gating weights: {weights}")
        return weights
    
    def _aggregate_probabilities(self, expert_outputs: Dict[str, ExpertOutput], 
                                weights: Dict[str, float]) -> DecisionProbabilities:
        """
        Aggregate expert probabilities using weighted average.
        
        Args:
            expert_outputs (Dict[str, ExpertOutput]): Expert outputs
            weights (Dict[str, float]): Expert weights
            
        Returns:
            DecisionProbabilities: Aggregated probabilities
        """
        aggregated_buy = 0.0
        aggregated_hold = 0.0
        aggregated_sell = 0.0
        
        for name, output in expert_outputs.items():
            weight = weights.get(name, 0.0)
            aggregated_buy += output.probabilities.buy_probability * weight
            aggregated_hold += output.probabilities.hold_probability * weight
            aggregated_sell += output.probabilities.sell_probability * weight
        
        # Normalize to ensure sum = 1.0
        total = aggregated_buy + aggregated_hold + aggregated_sell
        if total > 0:
            aggregated_buy /= total
            aggregated_hold /= total
            aggregated_sell /= total
        
        return DecisionProbabilities(aggregated_buy, aggregated_hold, aggregated_sell)
    
    def _create_expert_contributions(self, expert_outputs: Dict[str, ExpertOutput], 
                                   weights: Dict[str, float]) -> Dict[str, ExpertContribution]:
        """
        Create expert contribution objects for analysis.
        
        Args:
            expert_outputs (Dict[str, ExpertOutput]): Expert outputs
            weights (Dict[str, float]): Expert weights
            
        Returns:
            Dict[str, ExpertContribution]: Expert contributions
        """
        contributions = {}
        
        for name, output in expert_outputs.items():
            weight = weights.get(name, 0.0)
            contribution = ExpertContribution(
                expert_name=name,
                expert_output=output,
                weight=weight,
                contribution=output.probabilities,
                confidence=output.confidence.confidence_score,
                processing_time=output.metadata.processing_time
            )
            contributions[name] = contribution
        
        return contributions
    
    def _determine_decision(self, probabilities: DecisionProbabilities) -> DecisionType:
        """
        Determine final decision based on aggregated probabilities.
        
        Args:
            probabilities (DecisionProbabilities): Aggregated probabilities
            
        Returns:
            DecisionType: Final decision
        """
        buy_prob = probabilities.buy_probability
        hold_prob = probabilities.hold_probability
        sell_prob = probabilities.sell_probability
        
        # Find the highest probability
        max_prob = max(buy_prob, hold_prob, sell_prob)
        
        if max_prob == buy_prob:
            return DecisionType.BUY
        elif max_prob == sell_prob:
            return DecisionType.SELL
        else:
            return DecisionType.HOLD
    
    def _calculate_overall_confidence(self, contributions: Dict[str, ExpertContribution]) -> float:
        """
        Calculate overall confidence based on expert contributions.
        
        Args:
            contributions (Dict[str, ExpertContribution]): Expert contributions
            
        Returns:
            float: Overall confidence score
        """
        if not contributions:
            return 0.0
        
        # Weighted average of expert confidences
        total_confidence = 0.0
        total_weight = 0.0
        
        for contribution in contributions.values():
            total_confidence += contribution.confidence * contribution.weight
            total_weight += contribution.weight
        
        if total_weight > 0:
            return total_confidence / total_weight
        else:
            return 0.0
    
    def _generate_reasoning(self, contributions: Dict[str, ExpertContribution], 
                          decision: DecisionType) -> str:
        """
        Generate reasoning for the final decision.
        
        Args:
            contributions (Dict[str, ExpertContribution]): Expert contributions
            decision (DecisionType): Final decision
            
        Returns:
            str: Reasoning text
        """
        if not contributions:
            return "No expert outputs available"
        
        # Sort experts by weight (highest first)
        sorted_contributions = sorted(
            contributions.values(), 
            key=lambda x: x.weight, 
            reverse=True
        )
        
        reasoning_parts = [f"Decision: {decision.value.upper()}"]
        reasoning_parts.append(f"Top contributing experts:")
        
        for i, contrib in enumerate(sorted_contributions[:3], 1):
            reasoning_parts.append(
                f"  {i}. {contrib.expert_name.title()} "
                f"(weight: {contrib.weight:.2f}, "
                f"confidence: {contrib.confidence:.2f})"
            )
        
        # Add decision probabilities
        if sorted_contributions:
            first_contrib = sorted_contributions[0]
            probs = first_contrib.contribution
            reasoning_parts.append(
                f"Probabilities: Buy {probs.buy_probability:.1%}, "
                f"Hold {probs.hold_probability:.1%}, "
                f"Sell {probs.sell_probability:.1%}"
            )
        
        return " | ".join(reasoning_parts)
    
    def _create_fallback_result(self, start_time: float) -> AggregationResult:
        """
        Create fallback result when aggregation fails.
        
        Args:
            start_time (float): Start time
            
        Returns:
            AggregationResult: Fallback result
        """
        processing_time = time.time() - start_time
        
        return AggregationResult(
            final_probabilities=DecisionProbabilities(0.0, 1.0, 0.0),
            expert_contributions={},
            aggregation_method="fallback",
            gating_weights={},
            overall_confidence=0.1,
            decision_type=DecisionType.HOLD,
            reasoning="Aggregation failed - using fallback decision",
            processing_time=processing_time
        )

def aggregate_experts(ticker: str, target_date: str, 
                     lookback_days: int = 7, lookback_years: int = 2) -> AggregationResult:
    """
    Main interface for expert aggregation using dynamic weighting.
    
    Args:
        ticker (str): Stock ticker symbol
        target_date (str): Target date for analysis (YYYY-MM-DD)
        lookback_days (int): Lookback period for sentiment and technical experts
        lookback_years (int): Lookback period for fundamental and chart experts
        
    Returns:
        AggregationResult: Aggregated expert outputs
    """
    aggregator = ExpertAggregator()
    return aggregator.aggregate_experts(ticker, target_date, lookback_days, lookback_years) 