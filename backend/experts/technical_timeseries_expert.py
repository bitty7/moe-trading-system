"""
technical_timeseries_expert.py

Technical Timeseries Expert for OHLCV data.
Uses LLM for advanced signal generation with rule-based fallback.
Computes technical indicators and asks LLM to interpret them for trading decisions.
Handles insufficient data gracefully. Logs all decisions.

TODO:
- Add more technical indicators (RSI, MACD, Bollinger Bands)
- Support configurable window sizes
- Add batch processing for multiple tickers
- Add unit tests for edge cases
- Optimize LLM prompt engineering
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from core.logging_config import get_logger
from core.data_types import ExpertOutput, DecisionProbabilities, ExpertConfidence, ExpertMetadata
from core.llm_client import get_llm_client
from core.confidence_calculator import ConfidenceCalculator

logger = get_logger("technical_timeseries_expert")

def calculate_technical_indicators(df: pd.DataFrame, short_window: int = 3, long_window: int = 7) -> Dict[str, Any]:
    """
    Calculate technical indicators from OHLCV data.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV columns
        short_window (int): Short MA window
        long_window (int): Long MA window
        
    Returns:
        Dict[str, Any]: Technical indicators
    """
    if df is None or len(df) < long_window:
        return {}
    
    df = df.copy()
    df = df[df['close'].notnull()]
    
    if len(df) < long_window:
        return {}
    
    indicators = {}
    
    # Current price
    indicators['current_price'] = df['close'].iloc[-1]
    
    # Moving averages
    indicators[f'ma{short_window}'] = df['close'].rolling(window=short_window).mean().iloc[-1]
    indicators[f'ma{long_window}'] = df['close'].rolling(window=long_window).mean().iloc[-1]
    
    # Price trend (5-day)
    if len(df) >= 5:
        price_5d_ago = df['close'].iloc[-5]
        price_now = df['close'].iloc[-1]
        if price_now > price_5d_ago:
            indicators['price_trend'] = 'uptrend'
        elif price_now < price_5d_ago:
            indicators['price_trend'] = 'downtrend'
        else:
            indicators['price_trend'] = 'sideways'
        
        # Price change percentage
        indicators['price_change_5d'] = (price_now - price_5d_ago) / price_5d_ago if price_5d_ago != 0 else 0
    else:
        indicators['price_trend'] = 'insufficient_data'
        indicators['price_change_5d'] = 0
    
    # Volatility (standard deviation of returns)
    if len(df) >= 10:
        returns = df['close'].pct_change().dropna()
        indicators['volatility'] = returns.std()
    else:
        indicators['volatility'] = 0
    
    # Support and resistance levels (simplified)
    if len(df) >= 20:
        recent_high = df['high'].tail(20).max()
        recent_low = df['low'].tail(20).min()
        current_price = df['close'].iloc[-1]
        
        indicators['resistance_level'] = recent_high
        indicators['support_level'] = recent_low
    else:
        indicators['resistance_level'] = df['close'].iloc[-1] * 1.05  # 5% above current
        indicators['support_level'] = df['close'].iloc[-1] * 0.95   # 5% below current
    
    # Volume indicators
    if 'volume' in df.columns and len(df) >= 10:
        avg_volume = df['volume'].tail(10).mean()
        current_volume = df['volume'].iloc[-1]
        
        indicators['avg_volume'] = avg_volume
        
        if current_volume > avg_volume * 1.5:
            indicators['volume_trend'] = 'high_volume'
        elif current_volume < avg_volume * 0.5:
            indicators['volume_trend'] = 'low_volume'
        else:
            indicators['volume_trend'] = 'normal_volume'
    
    return indicators

def create_llm_prompt(ticker: str, date: str, indicators: Dict[str, Any]) -> str:
    """
    Create a prompt for the LLM to analyze technical indicators.
    
    Args:
        ticker (str): Stock ticker symbol
        date (str): Current date
        indicators (Dict[str, Any]): Technical indicators
        
    Returns:
        str: Formatted prompt for LLM
    """
    # Helper function to safely format values
    def safe_format(value, format_spec):
        if value is None or value == 'N/A':
            return 'N/A'
        try:
            if format_spec == '.2f':
                return f"{float(value):.2f}"
            elif format_spec == '.2%':
                return f"{float(value):.2%}"
            elif format_spec == '.0f':
                return f"{float(value):.0f}"
            else:
                return str(value)
        except (ValueError, TypeError):
            return str(value)
    
    prompt = f"""You are a financial analyst. Based on the technical indicators below, provide ONLY a probability array for trading {ticker}.

Date: {date}

Technical Indicators:
- Current Price: ${safe_format(indicators.get('current_price'), '.2f')}
- {list(indicators.keys())[1]} (Short MA): ${safe_format(indicators.get(list(indicators.keys())[1]), '.2f')}
- {list(indicators.keys())[2]} (Long MA): ${safe_format(indicators.get(list(indicators.keys())[2]), '.2f')}
- Price Trend (5-day): {indicators.get('price_trend', 'N/A')}
- Price Change (5-day): {safe_format(indicators.get('price_change_5d'), '.2%')}
- Volatility: {safe_format(indicators.get('volatility'), '.2%')}
- Support Level: ${safe_format(indicators.get('support_level'), '.2f')}
- Resistance Level: ${safe_format(indicators.get('resistance_level'), '.2f')}"""

    if 'volume_trend' in indicators:
        prompt += f"\n- Volume Trend: {indicators['volume_trend']}"
        prompt += f"\n- Average Volume: {safe_format(indicators.get('avg_volume'), '.0f')}"

    prompt += """

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

def llm_technical_analysis(ticker: str, date: str, df: pd.DataFrame, short_window: int = 3, long_window: int = 7) -> Optional[ExpertOutput]:
    """
    Perform LLM-based technical analysis.
    
    Args:
        ticker (str): Stock ticker
        date (str): Current date
        df (pd.DataFrame): OHLCV data
        short_window (int): Short MA window
        long_window (int): Long MA window
        
    Returns:
        ExpertOutput or None: LLM analysis result
    """
    start_time = time.time()
    
    try:
        # Calculate technical indicators
        indicators = calculate_technical_indicators(df, short_window, long_window)
        if not indicators:
            logger.warning(f"Insufficient data for LLM analysis on {ticker}")
            return None
        
        # Create prompt
        prompt = create_llm_prompt(ticker, date, indicators)
        
        # Get LLM response
        llm_client = get_llm_client()
        response = llm_client.generate(prompt)
        
        if response is None:
            logger.warning(f"LLM failed to generate response for {ticker}")
            return None
        
        # Parse probabilities
        probabilities = llm_client.parse_probabilities(response)
        if probabilities is None:
            logger.warning(f"Failed to parse LLM probabilities for {ticker}")
            return None
        
        processing_time = time.time() - start_time
        
        # Calculate dynamic confidence
        analysis_factors = {
            'probabilities': probabilities,
            'indicators_used': indicators,
            'method': 'llm_analysis'
        }
        
        confidence_score = ConfidenceCalculator.calculate_llm_confidence(
            response, 1.0, analysis_factors
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
                expert_type="technical_timeseries",
                model_name="llama3.1",
                processing_time=processing_time,
                input_data_quality=0.9 if len(df) >= 20 else 0.7,
                additional_info={
                    'indicators': indicators,
                    'method': 'llm_analysis',
                    'short_window': short_window,
                    'long_window': long_window
                }
            )
        )
        
    except Exception as e:
        logger.error(f"Error in LLM technical analysis for {ticker}: {e}")
        return None

def moving_average_crossover_signal(df: pd.DataFrame, short_window: int = 3, long_window: int = 7) -> Optional[ExpertOutput]:
    """
    Generate ExpertOutput using short/long moving average crossover.
    
    Args:
        df (pd.DataFrame): DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
        short_window (int): Short moving average window
        long_window (int): Long moving average window
        
    Returns:
        ExpertOutput or None: Crossover analysis result
    """
    start_time = time.time()
    
    if df is None or len(df) < long_window or df['close'].isnull().all():
        logger.warning(f"Insufficient data for moving average crossover (need at least {long_window} days)")
        return None
    
    df = df.copy()
    df = df[df['close'].notnull()]
    if len(df) < long_window:
        logger.warning(f"Not enough valid close prices for moving average crossover (need {long_window})")
        return None
    
    df[f'ma{short_window}'] = df['close'].rolling(window=short_window).mean()
    df[f'ma{long_window}'] = df['close'].rolling(window=long_window).mean()
    
    # Find the most recent crossover
    crossover_found = False
    crossover_type = None
    
    # Start from the end and work backwards to find the most recent crossover
    for i in range(len(df) - 1, long_window, -1):
        curr = df.iloc[i]
        prev = df.iloc[i-1]
        
        # Check if we have valid moving averages
        if (np.isnan(curr[f'ma{short_window}']) or np.isnan(curr[f'ma{long_window}']) or
            np.isnan(prev[f'ma{short_window}']) or np.isnan(prev[f'ma{long_window}'])):
            continue
        
        # Buy signal: short MA crosses above long MA
        if prev[f'ma{short_window}'] <= prev[f'ma{long_window}'] and curr[f'ma{short_window}'] > curr[f'ma{long_window}']:
            crossover_found = True
            crossover_type = 'buy'
            logger.info(f"Buy signal: {short_window}MA crossed above {long_window}MA at row {i}")
            break
        
        # Sell signal: short MA crosses below long MA
        if prev[f'ma{short_window}'] >= prev[f'ma{long_window}'] and curr[f'ma{short_window}'] < curr[f'ma{long_window}']:
            crossover_found = True
            crossover_type = 'sell'
            logger.info(f"Sell signal: {short_window}MA crossed below {long_window}MA at row {i}")
            break
    
    processing_time = time.time() - start_time
    
    if crossover_found:
        if crossover_type == 'buy':
            # Calculate dynamic confidence for rule-based analysis
            analysis_factors = {
                'probabilities': [0.8, 0.1, 0.1],
                'indicators_used': [f'MA{short_window}', f'MA{long_window}'],
                'method': 'ma_crossover',
                'buy_signals': 1,
                'total_signals': 1
            }
            
            confidence_score = ConfidenceCalculator.calculate_rule_based_confidence(
                0.9, analysis_factors
            )
            
            return ExpertOutput(
                probabilities=DecisionProbabilities(0.8, 0.1, 0.1),
                confidence=ExpertConfidence(confidence_score, 1.0 - confidence_score, 0.95),
                metadata=ExpertMetadata(
                    expert_type="technical_timeseries",
                    model_name="rule_based",
                    processing_time=processing_time,
                    input_data_quality=0.9,
                    additional_info={
                        'method': 'ma_crossover',
                        'crossover_type': 'buy',
                        'short_window': short_window,
                        'long_window': long_window,
                        'reason': f'{short_window}MA crossed above {long_window}MA'
                    }
                )
            )
        else:  # sell
            # Calculate dynamic confidence for rule-based analysis
            analysis_factors = {
                'probabilities': [0.1, 0.1, 0.8],
                'indicators_used': [f'MA{short_window}', f'MA{long_window}'],
                'method': 'ma_crossover',
                'sell_signals': 1,
                'total_signals': 1
            }
            
            confidence_score = ConfidenceCalculator.calculate_rule_based_confidence(
                0.9, analysis_factors
            )
            
            return ExpertOutput(
                probabilities=DecisionProbabilities(0.1, 0.1, 0.8),
                confidence=ExpertConfidence(confidence_score, 1.0 - confidence_score, 0.95),
                metadata=ExpertMetadata(
                    expert_type="technical_timeseries",
                    model_name="rule_based",
                    processing_time=processing_time,
                    input_data_quality=0.9,
                    additional_info={
                        'method': 'ma_crossover',
                        'crossover_type': 'sell',
                        'short_window': short_window,
                        'long_window': long_window,
                        'reason': f'{short_window}MA crossed below {long_window}MA'
                    }
                )
            )
    
    # No crossover found
    logger.info("Hold signal: No crossover")
    return ExpertOutput(
        probabilities=DecisionProbabilities(0.1, 0.8, 0.1),
        confidence=ExpertConfidence(0.7, 0.3, 0.8),
        metadata=ExpertMetadata(
            expert_type="technical_timeseries",
            model_name="rule_based",
            processing_time=processing_time,
            input_data_quality=0.9,
            additional_info={
                'method': 'ma_crossover',
                'crossover_type': 'none',
                'short_window': short_window,
                'long_window': long_window,
                'reason': 'No crossover'
            }
        )
    )

def momentum_signal(df: pd.DataFrame, window: int = 5, threshold: float = 0.03) -> Optional[ExpertOutput]:
    """
    Simple momentum rule: if close increases >threshold over window, buy; if decreases >threshold, sell.
    
    Args:
        df (pd.DataFrame): DataFrame with 'close' column
        window (int): Lookback window
        threshold (float): Percentage threshold (e.g., 0.03 for 3%)
        
    Returns:
        ExpertOutput or None: Momentum analysis result
    """
    start_time = time.time()
    
    if df is None or len(df) < window or df['close'].isnull().all():
        logger.warning(f"Insufficient data for momentum rule (need at least {window} days)")
        return None
    
    df = df.copy()
    df = df[df['close'].notnull()]
    if len(df) < window:
        logger.warning(f"Not enough valid close prices for momentum rule (need {window})")
        return None
    
    start = df['close'].iloc[-window]
    end = df['close'].iloc[-1]
    pct_change = (end - start) / start if start != 0 else 0
    
    processing_time = time.time() - start_time
    
    if pct_change > threshold:
        logger.info(f"Buy signal: close increased {pct_change:.2%} over {window} days")
        return ExpertOutput(
            probabilities=DecisionProbabilities(0.7, 0.2, 0.1),
            confidence=ExpertConfidence(0.8, 0.2, 0.85),
            metadata=ExpertMetadata(
                expert_type="technical_timeseries",
                model_name="rule_based",
                processing_time=processing_time,
                input_data_quality=0.8,
                additional_info={
                    'method': 'momentum',
                    'pct_change': pct_change,
                    'window': window,
                    'threshold': threshold,
                    'reason': f'Close increased {pct_change:.2%} over {window} days'
                }
            )
        )
    
    if pct_change < -threshold:
        logger.info(f"Sell signal: close decreased {pct_change:.2%} over {window} days")
        return ExpertOutput(
            probabilities=DecisionProbabilities(0.1, 0.2, 0.7),
            confidence=ExpertConfidence(0.8, 0.2, 0.85),
            metadata=ExpertMetadata(
                expert_type="technical_timeseries",
                model_name="rule_based",
                processing_time=processing_time,
                input_data_quality=0.8,
                additional_info={
                    'method': 'momentum',
                    'pct_change': pct_change,
                    'window': window,
                    'threshold': threshold,
                    'reason': f'Close decreased {pct_change:.2%} over {window} days'
                }
            )
        )
    
    # No significant momentum
    logger.info(f"Hold signal: no significant momentum ({pct_change:.2%})")
    return ExpertOutput(
        probabilities=DecisionProbabilities(0.2, 0.6, 0.2),
        confidence=ExpertConfidence(0.6, 0.4, 0.7),
        metadata=ExpertMetadata(
            expert_type="technical_timeseries",
            model_name="rule_based",
            processing_time=processing_time,
            input_data_quality=0.8,
            additional_info={
                'method': 'momentum',
                'pct_change': pct_change,
                'window': window,
                'threshold': threshold,
                'reason': f'No significant momentum ({pct_change:.2%})'
            }
        )
    )

def technical_timeseries_expert(df: pd.DataFrame, ticker: str = "UNKNOWN", short_window: int = 3, long_window: int = 7, momentum_window: int = 5, momentum_threshold: float = 0.03, use_llm: bool = True) -> ExpertOutput:
    """
    Technical timeseries expert that analyzes OHLCV data.
    
    Args:
        df (pd.DataFrame): DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
        ticker (str): Stock ticker symbol
        short_window (int): Short moving average window
        long_window (int): Long moving average window
        momentum_window (int): Momentum calculation window
        momentum_threshold (float): Momentum threshold for buy/sell signals
        use_llm (bool): Whether to use LLM analysis (falls back to rules if False or fails)
        
    Returns:
        ExpertOutput: Expert analysis result
    """
    current_date = df['date'].iloc[-1] if df is not None and len(df) > 0 else "UNKNOWN"
    
    # Try LLM analysis first if enabled
    if use_llm:
        result = llm_technical_analysis(ticker, current_date, df, short_window, long_window)
        if result is not None:
            return result
        else:
            logger.info(f"LLM analysis failed for {ticker}, falling back to rule-based logic")
    
    # Fallback to rule-based methods
    result = moving_average_crossover_signal(df, short_window, long_window)
    if result is not None:
        return result
    
    result = momentum_signal(df, momentum_window, momentum_threshold)
    if result is not None:
        return result
    
    # Final fallback: insufficient data
    logger.warning("Fallback: Insufficient data for any rule, returning hold")
    return ExpertOutput(
        probabilities=DecisionProbabilities(0.0, 1.0, 0.0),
        confidence=ExpertConfidence(0.1, 0.9, 0.1),
        metadata=ExpertMetadata(
            expert_type="technical_timeseries",
            model_name="fallback",
            processing_time=0.001,
            input_data_quality=0.0,
            additional_info={
                'method': 'fallback',
                'reason': 'Insufficient data',
                'data_points': len(df) if df is not None else 0
            }
        )
    ) 