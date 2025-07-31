#!/usr/bin/env python3
"""
confidence_calculator.py

Dynamic confidence calculation for expert outputs.
Calculates confidence based on data quality, analysis quality, and decision certainty.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

@dataclass
class ConfidenceFactors:
    """Factors that influence confidence calculation."""
    data_quality: float  # 0.0 to 1.0
    llm_response_quality: float  # 0.0 to 1.0
    decision_certainty: float  # 0.0 to 1.0
    method_confidence: float  # 0.0 to 1.0 (LLM vs rule-based)
    data_completeness: float  # 0.0 to 1.0
    analysis_depth: float  # 0.0 to 1.0

class ConfidenceCalculator:
    """
    Calculates dynamic confidence scores for expert outputs.
    """
    
    @staticmethod
    def calculate_llm_confidence(response: str, data_quality: float, 
                                analysis_factors: Dict[str, Any]) -> float:
        """
        Calculate confidence for LLM-based analysis.
        
        Args:
            response (str): LLM response text
            data_quality (float): Quality of input data (0.0 to 1.0)
            analysis_factors (Dict[str, Any]): Additional analysis factors
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        # Base confidence from data quality
        base_confidence = data_quality * 0.4
        
        # LLM response quality assessment
        response_quality = ConfidenceCalculator._assess_llm_response_quality(response)
        
        # Decision certainty based on probability distribution
        decision_certainty = ConfidenceCalculator._calculate_decision_certainty(
            analysis_factors.get('probabilities', [0.33, 0.34, 0.33])
        )
        
        # Analysis depth (how many factors were considered)
        analysis_depth = ConfidenceCalculator._calculate_analysis_depth(analysis_factors)
        
        # Method confidence (LLM is generally more reliable than rule-based)
        method_confidence = 0.9
        
        # Weighted combination
        confidence = (
            base_confidence * 0.2 +
            response_quality * 0.3 +
            decision_certainty * 0.25 +
            analysis_depth * 0.15 +
            method_confidence * 0.1
        )
        
        return min(1.0, max(0.0, confidence))
    
    @staticmethod
    def calculate_rule_based_confidence(data_quality: float, 
                                      analysis_factors: Dict[str, Any]) -> float:
        """
        Calculate confidence for rule-based analysis.
        
        Args:
            data_quality (float): Quality of input data (0.0 to 1.0)
            analysis_factors (Dict[str, Any]): Additional analysis factors
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        # Base confidence from data quality
        base_confidence = data_quality * 0.3
        
        # Decision certainty
        decision_certainty = ConfidenceCalculator._calculate_decision_certainty(
            analysis_factors.get('probabilities', [0.33, 0.34, 0.33])
        )
        
        # Analysis depth
        analysis_depth = ConfidenceCalculator._calculate_analysis_depth(analysis_factors)
        
        # Method confidence (rule-based is less reliable than LLM)
        method_confidence = 0.6
        
        # Signal strength (how many rules triggered)
        signal_strength = ConfidenceCalculator._calculate_signal_strength(analysis_factors)
        
        # Weighted combination
        confidence = (
            base_confidence * 0.25 +
            decision_certainty * 0.25 +
            analysis_depth * 0.2 +
            method_confidence * 0.15 +
            signal_strength * 0.15
        )
        
        return min(1.0, max(0.0, confidence))
    
    @staticmethod
    def calculate_fallback_confidence(reason: str, data_quality: float) -> float:
        """
        Calculate confidence for fallback scenarios.
        
        Args:
            reason (str): Reason for fallback
            data_quality (float): Quality of input data (0.0 to 1.0)
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        # Very low base confidence for fallbacks
        base_confidence = 0.1
        
        # Slight boost if we have some data
        data_boost = data_quality * 0.1
        
        # Reason-specific adjustments
        reason_penalty = {
            'no_data': 0.0,
            'no_fundamental_data': 0.0,
            'no_news_data': 0.0,
            'no_text_content': 0.0,
            'no_ratios_available': 0.0,
            'error': 0.0,
            'llm_failed': 0.05,
            'insufficient_data': 0.02
        }
        
        reason_boost = reason_penalty.get(reason, 0.0)
        
        confidence = base_confidence + data_boost + reason_boost
        return min(1.0, max(0.0, confidence))
    
    @staticmethod
    def _assess_llm_response_quality(response: str) -> float:
        """
        Assess the quality of LLM response.
        
        Args:
            response (str): LLM response text
            
        Returns:
            float: Response quality score (0.0 to 1.0)
        """
        if not response or len(response.strip()) < 10:
            return 0.1
        
        quality_score = 0.5  # Base score
        
        # Check for probability array format
        prob_pattern = r'\[[0-9.,\s]+\]'
        if re.search(prob_pattern, response):
            quality_score += 0.3
        
        # Check for structured response
        if 'probability' in response.lower() or 'buy' in response.lower():
            quality_score += 0.1
        
        # Check for reasonable length
        if 50 <= len(response) <= 500:
            quality_score += 0.1
        
        # Penalize for error indicators
        if any(word in response.lower() for word in ['error', 'sorry', 'cannot', 'unable']):
            quality_score -= 0.2
        
        return min(1.0, max(0.0, quality_score))
    
    @staticmethod
    def _calculate_decision_certainty(probabilities: List[float]) -> float:
        """
        Calculate decision certainty based on probability distribution.
        
        Args:
            probabilities (List[float]): [buy, hold, sell] probabilities
            
        Returns:
            float: Decision certainty score (0.0 to 1.0)
        """
        if len(probabilities) != 3:
            return 0.5
        
        # Calculate entropy (lower entropy = higher certainty)
        import math
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        
        # Convert entropy to certainty (max entropy for 3 classes is log2(3) ≈ 1.585)
        max_entropy = math.log2(3)
        certainty = 1.0 - (entropy / max_entropy)
        
        return min(1.0, max(0.0, certainty))
    
    @staticmethod
    def _calculate_analysis_depth(analysis_factors: Dict[str, Any]) -> float:
        """
        Calculate analysis depth based on factors considered.
        
        Args:
            analysis_factors (Dict[str, Any]): Analysis factors
            
        Returns:
            float: Analysis depth score (0.0 to 1.0)
        """
        depth_score = 0.3  # Base score
        
        # Count factors considered
        factor_count = 0
        
        # Sentiment factors
        if 'articles_analyzed' in analysis_factors:
            articles = analysis_factors['articles_analyzed']
            if articles > 0:
                factor_count += 1
                depth_score += min(0.2, articles / 20.0)  # Bonus for more articles
        
        # Technical factors
        if 'indicators_used' in analysis_factors:
            indicators = analysis_factors['indicators_used']
            if isinstance(indicators, list) and len(indicators) > 0:
                factor_count += 1
                depth_score += min(0.2, len(indicators) / 10.0)
        
        # Fundamental factors
        if 'ratios_analyzed' in analysis_factors:
            ratios = analysis_factors['ratios_analyzed']
            if ratios > 0:
                factor_count += 1
                depth_score += min(0.2, ratios / 20.0)
        
        # Data quality factors
        if 'statements_available' in analysis_factors:
            statements = analysis_factors['statements_available']
            if statements > 0:
                factor_count += 1
                depth_score += min(0.1, statements / 5.0)
        
        # Bonus for multiple factor types
        if factor_count >= 2:
            depth_score += 0.1
        
        return min(1.0, max(0.0, depth_score))
    
    @staticmethod
    def _calculate_signal_strength(analysis_factors: Dict[str, Any]) -> float:
        """
        Calculate signal strength for rule-based analysis.
        
        Args:
            analysis_factors (Dict[str, Any]): Analysis factors
            
        Returns:
            float: Signal strength score (0.0 to 1.0)
        """
        strength_score = 0.3  # Base score
        
        # Count signals
        buy_signals = analysis_factors.get('buy_signals', 0)
        sell_signals = analysis_factors.get('sell_signals', 0)
        total_signals = analysis_factors.get('total_signals', 0)
        
        if total_signals > 0:
            # Stronger signals when there's clear direction
            signal_ratio = max(buy_signals, sell_signals) / total_signals
            strength_score += signal_ratio * 0.4
            
            # Bonus for having multiple signals
            if total_signals >= 3:
                strength_score += 0.2
        
        return min(1.0, max(0.0, strength_score)) 