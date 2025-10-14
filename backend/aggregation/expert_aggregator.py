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
    Aggregates outputs from all four experts using configurable weighting strategies.
    Supports: fixed, entropy, confidence, and performance-based weighting.
    """
    
    def __init__(self, aggregation_config: Optional[Dict[str, Any]] = None):
        """
        Initialize expert aggregator with configurable weighting strategy.
        
        Args:
            aggregation_config: Configuration dict with 'strategy' and 'fixed_weights'
        """
        self.expert_names = ['sentiment', 'technical', 'fundamental', 'chart']
        self.aggregation_config = aggregation_config or {}
        self.strategy = self.aggregation_config.get('strategy', 'entropy')
        self.fixed_weights_list = self.aggregation_config.get('fixed_weights', [0.25, 0.25, 0.25, 0.25])
        self.expert_order = self.aggregation_config.get('expert_order', ['sentiment', 'timeseries', 'chart', 'fundamental'])
        
        logger.info(f"Expert aggregator initialized with strategy: {self.strategy}")
    
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
                aggregation_method=self.strategy,
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
    
    def _calculate_entropy(self, probabilities: List[float]) -> float:
        """
        Calculate Shannon entropy of probability distribution.
        Lower entropy = more certain/confident prediction.
        
        Args:
            probabilities: List of probabilities [p_buy, p_hold, p_sell]
            
        Returns:
            float: Entropy value
        """
        return -sum(p * np.log(p + 1e-10) for p in probabilities if p > 0)
    
    def _calculate_entropy_weights(self, expert_outputs: Dict[str, ExpertOutput]) -> Dict[str, float]:
        """
        Calculate weights based on inverse entropy (lower entropy = higher weight).
        
        Args:
            expert_outputs: Outputs from all experts
            
        Returns:
            Dict[str, float]: Normalized weights for each expert
        """
        entropies = {}
        inverse_entropies = {}
        
        for name, output in expert_outputs.items():
            probabilities = output.probabilities.to_list()
            entropy = self._calculate_entropy(probabilities)
            entropies[name] = entropy
            # Inverse entropy with small epsilon to avoid division by zero
            inverse_entropies[name] = 1.0 / (entropy + 1e-6)
        
        # Normalize to sum to 1.0
        total = sum(inverse_entropies.values())
        weights = {name: inv_ent / total for name, inv_ent in inverse_entropies.items()}
        
        logger.debug(f"Entropy-based weights: {weights} (entropies: {entropies})")
        return weights
    
    def _calculate_confidence_weights(self, expert_outputs: Dict[str, ExpertOutput]) -> Dict[str, float]:
        """
        Calculate weights based on expert-reported confidence scores.
        
        Args:
            expert_outputs: Outputs from all experts
            
        Returns:
            Dict[str, float]: Normalized weights for each expert
        """
        confidences = {name: output.confidence.confidence_score 
                      for name, output in expert_outputs.items()}
        
        total = sum(confidences.values())
        if total > 0:
            weights = {name: conf / total for name, conf in confidences.items()}
        else:
            # Fallback to uniform if all confidences are zero
            num_experts = len(expert_outputs)
            weights = {name: 1.0 / num_experts for name in expert_outputs.keys()}
        
        logger.debug(f"Confidence-based weights: {weights}")
        return weights
    
    def _calculate_fixed_weights(self, expert_outputs: Dict[str, ExpertOutput]) -> Dict[str, float]:
        """
        Use fixed predefined weights from configuration.
        
        Args:
            expert_outputs: Outputs from all experts
            
        Returns:
            Dict[str, float]: Fixed weights for each expert
        """
        # Map fixed weights list to expert names based on expert_order
        weights = {}
        for idx, expert_name in enumerate(self.expert_order):
            if expert_name in expert_outputs or expert_name == 'timeseries':
                # Handle 'timeseries' vs 'technical' naming
                actual_name = 'technical' if expert_name == 'timeseries' else expert_name
                if actual_name in expert_outputs:
                    weights[actual_name] = self.fixed_weights_list[idx] if idx < len(self.fixed_weights_list) else 0.25
        
        # Normalize in case not all experts are present
        total = sum(weights.values())
        if total > 0:
            weights = {name: w / total for name, w in weights.items()}
        
        logger.debug(f"Fixed weights: {weights}")
        return weights
    
    def _calculate_gating_weights(self, expert_outputs: Dict[str, ExpertOutput]) -> Dict[str, float]:
        """
        Calculate weights for experts based on configured strategy.
        
        Args:
            expert_outputs (Dict[str, ExpertOutput]): Expert outputs
            
        Returns:
            Dict[str, float]: Weights for each expert
        """
        if self.strategy == "fixed":
            weights = self._calculate_fixed_weights(expert_outputs)
        elif self.strategy == "entropy":
            weights = self._calculate_entropy_weights(expert_outputs)
        elif self.strategy == "confidence":
            weights = self._calculate_confidence_weights(expert_outputs)
        else:
            # Default to entropy if unknown strategy
            logger.warning(f"Unknown strategy '{self.strategy}', defaulting to entropy")
            weights = self._calculate_entropy_weights(expert_outputs)
        
        logger.info(f"Calculated weights using '{self.strategy}' strategy: {weights}")
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
                     lookback_days: int = 7, lookback_years: int = 2,
                     aggregation_config: Optional[Dict[str, Any]] = None) -> AggregationResult:
    """
    Main interface for expert aggregation using configurable weighting strategy.
    
    Args:
        ticker (str): Stock ticker symbol
        target_date (str): Target date for analysis (YYYY-MM-DD)
        lookback_days (int): Lookback period for sentiment and technical experts
        lookback_years (int): Lookback period for fundamental and chart experts
        aggregation_config (Optional[Dict]): Aggregation configuration with strategy and weights
        
    Returns:
        AggregationResult: Aggregated expert outputs
    """
    aggregator = ExpertAggregator(aggregation_config)
    return aggregator.aggregate_experts(ticker, target_date, lookback_days, lookback_years) 