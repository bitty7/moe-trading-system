#!/usr/bin/env python3
"""
fundamental_expert.py

Fundamental expert that analyzes financial statements to generate trading signals.
Uses LLM to interpret financial ratios, trends, and fundamental indicators.
Provides rule-based fallback for when LLM analysis fails.

RESPONSIBILITIES:
- Analyze balance sheets, income statements, and cash flow statements
- Calculate key financial ratios (P/E, ROE, debt-to-equity, etc.)
- Use LLM to interpret financial health and growth prospects
- Generate buy/hold/sell signals based on fundamental analysis
- Handle missing financial data gracefully
- Provide robust fallback mechanisms

TODO:
- Implement more sophisticated financial ratio calculations
- Add industry-specific analysis
- Optimize LLM prompts for financial analysis
- Add more granular fundamental indicators
- Implement trend analysis across multiple periods
- Add unit tests for edge cases
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import re

from core.logging_config import get_logger
from core.data_types import ExpertOutput, DecisionProbabilities, ExpertConfidence, ExpertMetadata, FundamentalData
from core.llm_client import get_llm_client
from core.confidence_calculator import ConfidenceCalculator
from data_loader.load_fundamentals import load_fundamentals_for_ticker

logger = get_logger("fundamental_expert")

class FundamentalExpert:
    """
    Fundamental expert that analyzes financial statements.
    """
    
    def __init__(self):
        """Initialize the fundamental expert."""
        self.llm_client = get_llm_client()
        logger.info("Fundamental expert initialized with LLM client")
    
    def analyze_fundamentals(self, ticker: str, target_date: str, 
                           lookback_years: int = 2) -> ExpertOutput:
        """
        Analyze fundamental financial data for a specific date and generate trading signals.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date for analysis (YYYY-MM-DD)
            lookback_years (int): Number of years to look back for financial data
            
        Returns:
            ExpertOutput: Fundamental analysis result with trading probabilities
        """
        start_time = time.time()
        
        try:
            # Load fundamental data for the period
            financial_data = self._load_fundamentals_for_period(ticker, target_date, lookback_years)
            
            if not financial_data or not financial_data.statements:
                logger.warning(f"No fundamental data available for {ticker} around {target_date}")
                return self._create_fallback_output("no_fundamental_data", start_time)
            
            # Calculate key financial ratios
            ratios = self._calculate_financial_ratios(financial_data)
            
            if not ratios:
                logger.warning(f"No financial ratios could be calculated for {ticker}")
                return self._create_fallback_output("no_ratios_available", start_time)
            
            # Analyze fundamentals using LLM
            result = self._analyze_with_llm(ticker, target_date, ratios, financial_data, start_time)
            
            if result is not None:
                return result
            
            # Fallback to rule-based analysis if LLM fails
            logger.info(f"LLM analysis failed for {ticker}, using rule-based fallback")
            return self._rule_based_fundamental_analysis(ratios, financial_data, start_time)
            
        except Exception as e:
            logger.error(f"Error in fundamental analysis for {ticker}: {e}")
            return self._create_fallback_output("error", start_time)
    
    def _load_fundamentals_for_period(self, ticker: str, target_date: str, 
                                    lookback_years: int) -> Optional[FundamentalData]:
        """
        Load fundamental data for the specified period.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date
            lookback_years (int): Number of years to look back
            
        Returns:
            FinancialData or None: Fundamental data for the period
        """
        try:
            # Calculate date range
            target = datetime.strptime(target_date, "%Y-%m-%d").date()
            start_date = date(target.year - lookback_years, target.month, target.day)
            
            # Load fundamental data
            financial_data = load_fundamentals_for_ticker(ticker, start_date.strftime("%Y-%m-%d"), target_date)
            
            if financial_data:
                logger.info(f"Loaded {financial_data.total_statements} statement types for {ticker}")
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Error loading fundamentals for period: {e}")
            return None
    
    def _calculate_financial_ratios(self, financial_data: FundamentalData) -> Dict[str, float]:
        """
        Calculate key financial ratios from fundamental data.
        
        Args:
            financial_data (FinancialData): Fundamental financial data
            
        Returns:
            Dict[str, float]: Calculated financial ratios
        """
        ratios = {}
        
        try:
            # Get balance sheet data
            balance_sheet = financial_data.statements.get('balance_sheet')
            if not balance_sheet:
                logger.warning("No balance sheet data available")
                return ratios
            
            # Get cash flow data
            cash_flow = financial_data.statements.get('cash_flow')
            
            # Extract key metrics
            metrics = balance_sheet.metrics
            
            # Calculate ratios if we have the necessary data
            if 'Assets' in metrics and 'AssetsCurrent' in metrics:
                assets = metrics['Assets'].get_latest_value()
                current_assets = metrics['AssetsCurrent'].get_latest_value()
                if assets and current_assets and assets > 0:
                    ratios['current_ratio'] = current_assets / assets
            
            if 'Assets' in metrics and 'Liabilities' in metrics:
                assets = metrics['Assets'].get_latest_value()
                liabilities = metrics['Liabilities'].get_latest_value()
                if assets and liabilities and assets > 0:
                    ratios['debt_to_assets'] = liabilities / assets
            
            if 'Assets' in metrics and 'AssetsCurrent' in metrics:
                assets = metrics['Assets'].get_latest_value()
                current_assets = metrics['AssetsCurrent'].get_latest_value()
                if assets and current_assets and assets > 0:
                    ratios['current_assets_ratio'] = current_assets / assets
            
            # Add raw metrics as ratios for LLM analysis
            for metric_name, metric in metrics.items():
                latest_value = metric.get_latest_value()
                if latest_value is not None:
                    ratios[f"{metric_name.lower()}"] = latest_value
            
            logger.info(f"Calculated {len(ratios)} financial ratios")
            return ratios
            
        except Exception as e:
            logger.error(f"Error calculating financial ratios: {e}")
            return {}
    
    def _analyze_with_llm(self, ticker: str, target_date: str, 
                         ratios: Dict[str, float], financial_data: FundamentalData, 
                         start_time: float) -> Optional[ExpertOutput]:
        """
        Analyze fundamentals using LLM.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date
            ratios (Dict[str, float]): Financial ratios
            financial_data (FinancialData): Financial data object
            
        Returns:
            ExpertOutput or None: LLM analysis result
        """
        try:
            # Create prompt for fundamental analysis
            prompt = self._create_fundamental_prompt(ticker, target_date, ratios, financial_data)
            
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
                'ratios_analyzed': len(ratios),
                'statements_available': financial_data.total_statements,
                'method': 'llm_fundamental_analysis'
            }
            
            confidence_score = ConfidenceCalculator.calculate_llm_confidence(
                response, financial_data.data_quality, analysis_factors
            )
            
            # Create ExpertOutput
            return ExpertOutput(
                probabilities=DecisionProbabilities.from_list(probabilities),
                confidence=ExpertConfidence(
                    confidence_score=confidence_score,
                    uncertainty=1.0 - confidence_score,
                    reliability_score=0.9,
                    metadata={'llm_response': response[:200]}  # First 200 chars
                ),
                metadata=ExpertMetadata(
                    expert_type="fundamental",
                    model_name="llama3.1",
                    processing_time=processing_time,
                    input_data_quality=financial_data.data_quality,
                    additional_info={
                        'method': 'llm_fundamental_analysis',
                        'ratios_analyzed': len(ratios),
                        'statements_available': financial_data.total_statements,
                        'key_ratios': list(ratios.keys())[:5]  # First 5 ratios
                    }
                )
            )
            
        except Exception as e:
            logger.error(f"Error in LLM fundamental analysis for {ticker}: {e}")
            return None
    
    def _create_fundamental_prompt(self, ticker: str, target_date: str, 
                                 ratios: Dict[str, float], financial_data: FundamentalData) -> str:
        """
        Create prompt for LLM fundamental analysis.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date
            ratios (Dict[str, float]): Financial ratios
            financial_data (FinancialData): Financial data
            
        Returns:
            str: Formatted prompt for LLM
        """
        # Format ratios for prompt
        ratios_text = "\n".join([f"  {name}: {value:,.2f}" for name, value in ratios.items()])
        
        prompt = f"""You are a financial analyst. Based on the fundamental data below, provide ONLY a probability array for trading {ticker}.

Date: {target_date}

Financial Ratios:
{ratios_text}

Statements Available: {financial_data.total_statements} types

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
    
    def _rule_based_fundamental_analysis(self, ratios: Dict[str, float], 
                                       financial_data: FundamentalData, 
                                       start_time: float) -> ExpertOutput:
        """
        Rule-based fundamental analysis as fallback.
        
        Args:
            ratios (Dict[str, float]): Financial ratios
            financial_data (FinancialData): Financial data
            
        Returns:
            ExpertOutput: Rule-based analysis result
        """
        processing_time = time.time() - start_time
        
        # Simple rule-based analysis based on key ratios
        buy_signals = 0
        sell_signals = 0
        total_signals = 0
        
        # Analyze current ratio
        if 'current_ratio' in ratios:
            current_ratio = ratios['current_ratio']
            if current_ratio > 1.5:
                buy_signals += 1
            elif current_ratio < 1.0:
                sell_signals += 1
            total_signals += 1
        
        # Analyze debt-to-assets ratio
        if 'debt_to_assets' in ratios:
            debt_ratio = ratios['debt_to_assets']
            if debt_ratio < 0.3:
                buy_signals += 1
            elif debt_ratio > 0.7:
                sell_signals += 1
            total_signals += 1
        
        # Analyze current assets ratio
        if 'current_assets_ratio' in ratios:
            current_assets_ratio = ratios['current_assets_ratio']
            if current_assets_ratio > 0.6:
                buy_signals += 1
            elif current_assets_ratio < 0.3:
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
            'ratios_analyzed': len(ratios),
            'statements_available': financial_data.total_statements,
            'method': 'rule_based_fundamental',
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'total_signals': total_signals
        }
        
        confidence_score = ConfidenceCalculator.calculate_rule_based_confidence(
            financial_data.data_quality, analysis_factors
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
                expert_type="fundamental",
                model_name="rule_based",
                processing_time=processing_time,
                input_data_quality=financial_data.data_quality,
                additional_info={
                    'method': 'rule_based_fundamental',
                    'ratios_analyzed': len(ratios),
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
                expert_type="fundamental",
                model_name="fallback",
                processing_time=processing_time,
                input_data_quality=0.0,
                additional_info={
                    'method': 'fallback',
                    'reason': reason
                }
            )
        )

def fundamental_expert(ticker: str, target_date: str, lookback_years: int = 2) -> ExpertOutput:
    """
    Main interface for fundamental expert analysis.
    
    Args:
        ticker (str): Stock ticker symbol
        target_date (str): Target date for analysis (YYYY-MM-DD)
        lookback_years (int): Number of years to look back for financial data
        
    Returns:
        ExpertOutput: Fundamental analysis result
    """
    expert = FundamentalExpert()
    return expert.analyze_fundamentals(ticker, target_date, lookback_years) 