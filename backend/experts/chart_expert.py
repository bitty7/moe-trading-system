#!/usr/bin/env python3
"""
chart_expert.py

Chart pattern analysis expert using candlestick chart images.
Analyzes chart patterns, trends, and visual indicators using LLM and rule-based methods.
Provides trading recommendations based on chart pattern recognition.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import cv2
from PIL import Image
import base64
import io

from core.logging_config import get_logger
from core.data_types import ExpertOutput, DecisionProbabilities, ExpertConfidence, ExpertMetadata, ChartData, ChartImage
from core.llm_client import get_llm_client
from core.confidence_calculator import ConfidenceCalculator
from data_loader.load_charts import load_charts_for_ticker

logger = get_logger("chart_expert")

class ChartExpert:
    """
    Chart pattern analysis expert using candlestick chart images.
    """
    
    def __init__(self):
        """Initialize chart expert with LLM client."""
        self.llm_client = get_llm_client()
        logger.info("Chart expert initialized with LLM client")
    
    def analyze_charts(self, ticker: str, target_date: str, 
                      lookback_years: int = 2) -> ExpertOutput:
        """
        Analyze chart patterns for trading decision.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date for analysis (YYYY-MM-DD)
            lookback_years (int): Number of years to look back for charts
            
        Returns:
            ExpertOutput: Chart analysis result
        """
        start_time = time.time()
        
        try:
            # Load chart data for the period
            chart_data = self._load_charts_for_period(ticker, target_date, lookback_years)
            
            if chart_data is None or len(chart_data.charts) == 0:
                logger.warning(f"No chart data available for {ticker} around {target_date}")
                return self._create_fallback_output("no_chart_data", start_time)
            
            # Try LLM analysis first
            llm_result = self._analyze_with_llm(ticker, target_date, chart_data, start_time)
            if llm_result:
                return llm_result
            
            # Fallback to rule-based analysis
            logger.info(f"LLM analysis failed for {ticker}, using rule-based analysis")
            return self._rule_based_chart_analysis(chart_data, start_time)
            
        except Exception as e:
            logger.error(f"Error in chart analysis for {ticker}: {e}")
            return self._create_fallback_output("error", start_time)
    
    def _load_charts_for_period(self, ticker: str, target_date: str, 
                               lookback_years: int) -> Optional[ChartData]:
        """
        Load chart data for the specified period.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date
            lookback_years (int): Number of years to look back
            
        Returns:
            ChartData or None: Chart data or None if not found
        """
        try:
            # Calculate date range
            from datetime import datetime, timedelta
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            start_dt = target_dt - timedelta(days=lookback_years * 365)
            
            start_date = start_dt.strftime("%Y-%m-%d")
            end_date = target_date
            
            # Load charts using the data loader
            chart_data = load_charts_for_ticker(ticker, start_date, end_date)
            
            if chart_data:
                logger.info(f"Loaded {len(chart_data.charts)} charts for {ticker}")
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error loading charts for {ticker}: {e}")
            return None
    
    def _analyze_with_llm(self, ticker: str, target_date: str, 
                         chart_data: ChartData, start_time: float) -> Optional[ExpertOutput]:
        """
        Analyze charts using LLM.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date
            chart_data (ChartData): Chart data object
            start_time (float): Analysis start time
            
        Returns:
            ExpertOutput or None: LLM analysis result or None if failed
        """
        try:
            # Create prompt with chart information
            prompt = self._create_chart_prompt(ticker, target_date, chart_data)
            
            # Get LLM response
            response = self.llm_client.generate(prompt)
            if response is None:
                logger.warning(f"LLM failed to generate response for {ticker}")
                return None
            
            # Parse probabilities
            probabilities = self.llm_client.parse_probabilities(response)
            if probabilities is None:
                logger.warning(f"Failed to parse LLM probabilities for {ticker}")
                return None
            
            processing_time = time.time() - start_time
            
            # Calculate dynamic confidence
            analysis_factors = {
                'probabilities': probabilities,
                'charts_analyzed': len(chart_data.charts),
                'method': 'llm_chart_analysis'
            }
            
            confidence_score = ConfidenceCalculator.calculate_llm_confidence(
                response, chart_data.data_quality, analysis_factors
            )
            
            return ExpertOutput(
                probabilities=DecisionProbabilities.from_list(probabilities),
                confidence=ExpertConfidence(
                    confidence_score=confidence_score,
                    uncertainty=1.0 - confidence_score,
                    reliability_score=0.9,
                    metadata={'llm_response': response[:200]}
                ),
                metadata=ExpertMetadata(
                    expert_type="chart",
                    model_name="llama3.1",
                    processing_time=processing_time,
                    input_data_quality=chart_data.data_quality,
                    additional_info={
                        'method': 'llm_chart_analysis',
                        'charts_analyzed': len(chart_data.charts),
                        'chart_summary': self._create_chart_summary(chart_data)
                    }
                )
            )
            
        except Exception as e:
            logger.error(f"Error in LLM chart analysis for {ticker}: {e}")
            return None
    
    def _create_chart_prompt(self, ticker: str, target_date: str, 
                           chart_data: ChartData) -> str:
        """
        Create prompt for LLM chart analysis.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date
            chart_data (ChartData): Chart data object
            
        Returns:
            str: Formatted prompt for LLM
        """
        # Create chart summary
        chart_summary = self._create_chart_summary(chart_data)
        
        prompt = f"""You are a financial analyst. Based on the chart data below, provide ONLY a probability array for trading {ticker}.

Date: {target_date}

Chart Information:
{chart_summary}

Respond with EXACTLY this format: [p_buy, p_hold, p_sell]
- p_buy: probability of BUY recommendation
- p_hold: probability of HOLD recommendation  
- p_sell: probability of SELL recommendation

Rules:
- All three numbers must sum to 1.0
- Use decimal format (e.g., 0.65 not 65%)
- Do not include explanations, code, or other text
- Only provide the three numbers in brackets

Your probabilities:"""
        
        return prompt
    
    def _create_chart_summary(self, chart_data: ChartData) -> str:
        """
        Create a summary of chart data for the prompt.
        
        Args:
            chart_data (ChartData): Chart data object
            
        Returns:
            str: Chart summary text
        """
        charts = chart_data.charts
        
        if not charts:
            return "No charts available"
        
        # Group charts by year
        charts_by_year = {}
        for chart in charts:
            if chart.year not in charts_by_year:
                charts_by_year[chart.year] = []
            charts_by_year[chart.year].append(chart)
        
        summary_lines = [
            f"Total Charts: {len(charts)}",
            f"Years Covered: {sorted(charts_by_year.keys())}",
            f"Data Quality: {chart_data.data_quality:.2f}"
        ]
        
        # Add chart details by year
        for year in sorted(charts_by_year.keys()):
            year_charts = charts_by_year[year]
            periods = [chart.half for chart in year_charts]
            summary_lines.append(f"  {year}: {', '.join(periods)} periods")
        
        return "\n".join(summary_lines)
    
    def _rule_based_chart_analysis(self, chart_data: ChartData, 
                                  start_time: float) -> ExpertOutput:
        """
        Rule-based chart analysis as fallback.
        
        Args:
            chart_data (ChartData): Chart data object
            start_time (float): Analysis start time
            
        Returns:
            ExpertOutput: Rule-based analysis result
        """
        processing_time = time.time() - start_time
        
        charts = chart_data.charts
        
        # Simple rule-based analysis based on chart availability and recency
        buy_signals = 0
        sell_signals = 0
        total_signals = 0
        
        # Analyze chart availability
        if len(charts) >= 5:
            buy_signals += 1  # Good chart coverage
        elif len(charts) <= 2:
            sell_signals += 1  # Poor chart coverage
        total_signals += 1
        
        # Analyze recency
        current_year = 2025  # Approximate current year
        recent_charts = sum(1 for chart in charts if chart.year >= current_year - 1)
        if recent_charts >= 2:
            buy_signals += 1  # Recent data available
        elif recent_charts == 0:
            sell_signals += 1  # No recent data
        total_signals += 1
        
        # Analyze data quality
        if chart_data.data_quality >= 0.8:
            buy_signals += 1
        elif chart_data.data_quality <= 0.3:
            sell_signals += 1
        total_signals += 1
        
        # Calculate probabilities
        if total_signals == 0:
            probabilities = [0.2, 0.6, 0.2]  # Neutral
        else:
            buy_prob = buy_signals / total_signals
            sell_prob = sell_signals / total_signals
            hold_prob = 1.0 - buy_prob - sell_prob
            
            # Normalize to ensure sum = 1.0
            total = buy_prob + hold_prob + sell_prob
            probabilities = [buy_prob/total, hold_prob/total, sell_prob/total]
        
        # Calculate dynamic confidence for rule-based analysis
        analysis_factors = {
            'probabilities': probabilities,
            'charts_analyzed': len(charts),
            'method': 'rule_based_chart',
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'total_signals': total_signals
        }
        
        confidence_score = ConfidenceCalculator.calculate_rule_based_confidence(
            chart_data.data_quality, analysis_factors
        )
        
        return ExpertOutput(
            probabilities=DecisionProbabilities.from_list(probabilities),
            confidence=ExpertConfidence(
                confidence_score=confidence_score,
                uncertainty=1.0 - confidence_score,
                reliability_score=0.7,
                metadata={'buy_signals': buy_signals, 'sell_signals': sell_signals}
            ),
            metadata=ExpertMetadata(
                expert_type="chart",
                model_name="rule_based",
                processing_time=processing_time,
                input_data_quality=chart_data.data_quality,
                additional_info={
                    'method': 'rule_based_chart',
                    'charts_analyzed': len(charts),
                    'buy_signals': buy_signals,
                    'sell_signals': sell_signals,
                    'total_signals': total_signals
                }
            )
        )
    
    def _create_fallback_output(self, reason: str, start_time: float) -> ExpertOutput:
        """
        Create fallback output when analysis fails.
        
        Args:
            reason (str): Reason for fallback
            start_time (float): Analysis start time
            
        Returns:
            ExpertOutput: Fallback result
        """
        processing_time = time.time() - start_time
        
        # Calculate fallback confidence
        confidence_score = ConfidenceCalculator.calculate_fallback_confidence(reason, 0.0)
        
        return ExpertOutput(
            probabilities=DecisionProbabilities(0.0, 1.0, 0.0),  # Hold
            confidence=ExpertConfidence(confidence_score, 1.0 - confidence_score, 0.1),
            metadata=ExpertMetadata(
                expert_type="chart",
                model_name="fallback",
                processing_time=processing_time,
                input_data_quality=0.0,
                additional_info={
                    'method': 'fallback',
                    'reason': reason
                }
            )
        )

def chart_expert(ticker: str, target_date: str, lookback_years: int = 2) -> ExpertOutput:
    """
    Main interface for chart expert analysis.
    
    Args:
        ticker (str): Stock ticker symbol
        target_date (str): Target date for analysis (YYYY-MM-DD)
        lookback_years (int): Number of years to look back for charts
        
    Returns:
        ExpertOutput: Chart analysis result
    """
    expert = ChartExpert()
    return expert.analyze_charts(ticker, target_date, lookback_years) 