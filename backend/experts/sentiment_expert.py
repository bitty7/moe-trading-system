"""
sentiment_expert.py

Sentiment Expert for analyzing daily news sentiment and producing trading signals.
Uses LLM to analyze news text and extract sentiment signals that may impact stock prices.
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import re

from core.logging_config import get_logger
from core.data_types import ExpertOutput, DecisionProbabilities, ExpertConfidence, ExpertMetadata, NewsData, NewsArticle
from core.llm_client import get_llm_client
from core.confidence_calculator import ConfidenceCalculator
from data_loader.load_news import load_news_for_ticker

logger = get_logger("sentiment_expert")

class SentimentExpert:
    """Expert for analyzing news sentiment and generating trading signals."""
    
    def __init__(self):
        """Initialize the sentiment expert."""
        self.llm_client = get_llm_client()
        logger.info("Sentiment expert initialized")
    
    def analyze_sentiment(self, ticker: str, target_date: str, 
                         lookback_days: int = 7) -> ExpertOutput:
        """
        Analyze news sentiment for a specific date and generate trading signals.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date for analysis (YYYY-MM-DD)
            lookback_days (int): Number of days to look back for news
            
        Returns:
            ExpertOutput: Sentiment analysis result with trading probabilities
        """
        start_time = time.time()
        
        try:
            # Load news data for the period
            news_data = self._load_news_for_period(ticker, target_date, lookback_days)
            
            if not news_data or not news_data.articles:
                logger.warning(f"No news data available for {ticker} around {target_date}")
                return self._create_fallback_output("no_news_data", start_time)
            
            # Prepare text for LLM analysis
            consolidated_text = self._prepare_text_for_analysis(news_data.articles)
            
            if not consolidated_text.strip():
                logger.warning(f"No valid text content for {ticker} around {target_date}")
                return self._create_fallback_output("no_text_content", start_time)
            
            # Analyze sentiment using LLM
            result = self._analyze_with_llm(ticker, target_date, consolidated_text, news_data, start_time)
            
            if result is not None:
                return result
            
            # Fallback to rule-based sentiment if LLM fails
            logger.info(f"LLM analysis failed for {ticker}, using rule-based fallback")
            return self._rule_based_sentiment_analysis(news_data, start_time)
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis for {ticker}: {e}")
            return self._create_fallback_output("error", start_time)
    
    def _load_news_for_period(self, ticker: str, target_date: str, 
                             lookback_days: int) -> Optional[NewsData]:
        """
        Load news data for the specified period.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date
            lookback_days (int): Number of days to look back
            
        Returns:
            NewsData or None: News data for the period
        """
        try:
            # Calculate date range
            target = datetime.strptime(target_date, "%Y-%m-%d").date()
            start_date = target - timedelta(days=lookback_days)
            
            # Load news data
            news_data = load_news_for_ticker(ticker, start_date.strftime("%Y-%m-%d"), target_date)
            
            if news_data:
                logger.info(f"Loaded {len(news_data.articles)} articles for {ticker} from {start_date} to {target_date}")
            
            return news_data
            
        except Exception as e:
            logger.error(f"Error loading news for period: {e}")
            return None
    
    def _prepare_text_for_analysis(self, articles: List[NewsArticle]) -> str:
        """
        Prepare consolidated text for LLM analysis.
        
        Args:
            articles (List[NewsArticle]): List of news articles
            
        Returns:
            str: Consolidated text for analysis
        """
        if not articles:
            return ""
        
        # Sort articles by date (most recent first)
        sorted_articles = sorted(articles, key=lambda x: x.published_date, reverse=True)
        
        # Prepare text with titles and content
        text_parts = []
        for i, article in enumerate(sorted_articles[:10]):  # Limit to 10 most recent articles
            if article.title:
                text_parts.append(f"Title {i+1}: {article.title}")
            if article.content:
                # Truncate very long content
                content = article.content[:2000] if len(article.content) > 2000 else article.content
                text_parts.append(f"Content {i+1}: {content}")
        
        consolidated_text = "\n\n".join(text_parts)
        
        # Basic text cleaning
        consolidated_text = re.sub(r'\s+', ' ', consolidated_text)  # Normalize whitespace
        consolidated_text = consolidated_text.strip()
        
        return consolidated_text
    
    def _analyze_with_llm(self, ticker: str, target_date: str, 
                         text: str, news_data: NewsData, start_time: float) -> Optional[ExpertOutput]:
        """
        Analyze sentiment using LLM.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date
            text (str): Consolidated text for analysis
            news_data (NewsData): News data object
            
        Returns:
            ExpertOutput or None: LLM analysis result
        """
        try:
            # Create prompt for sentiment analysis
            prompt = self._create_sentiment_prompt(ticker, target_date, text, news_data)
            
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
                'articles_analyzed': len(news_data.articles),
                'method': 'llm_sentiment_analysis'
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
                    expert_type="sentiment",
                    model_name="llama3.1",
                    processing_time=processing_time,
                    input_data_quality=0.9 if len(news_data.articles) >= 3 else 0.7,
                    additional_info={
                        'method': 'llm_sentiment_analysis',
                        'articles_analyzed': len(news_data.articles),
                        'text_length': len(text),
                        'date_range': f"{min(a.published_date for a in news_data.articles)} to {max(a.published_date for a in news_data.articles)}"
                    }
                )
            )
            
        except Exception as e:
            logger.error(f"Error in LLM sentiment analysis for {ticker}: {e}")
            return None
    
    def _create_sentiment_prompt(self, ticker: str, target_date: str, 
                               text: str, news_data: NewsData) -> str:
        """
        Create prompt for LLM sentiment analysis.
        
        Args:
            ticker (str): Stock ticker symbol
            target_date (str): Target date
            text (str): Consolidated text
            news_data (NewsData): News data object
            
        Returns:
            str: Formatted prompt for LLM
        """
        prompt = f"""You are a financial analyst. Based on the news articles below, provide ONLY a probability array for trading {ticker}.

Target Date: {target_date}
Number of Articles: {len(news_data.articles)}

News Articles:
{text[:3000]}

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
    
    def _rule_based_sentiment_analysis(self, news_data: NewsData, 
                                     start_time: float) -> ExpertOutput:
        """
        Fallback rule-based sentiment analysis.
        
        Args:
            news_data (NewsData): News data object
            start_time (float): Analysis start time
            
        Returns:
            ExpertOutput: Rule-based analysis result
        """
        processing_time = time.time() - start_time
        
        # Simple rule-based analysis based on news volume and content
        articles = news_data.articles
        
        # Count positive/negative keywords
        positive_keywords = ['positive', 'growth', 'profit', 'increase', 'up', 'gain', 'strong', 'beat', 'exceed']
        negative_keywords = ['negative', 'decline', 'loss', 'decrease', 'down', 'fall', 'weak', 'miss', 'below']
        
        positive_count = 0
        negative_count = 0
        
        for article in articles:
            text = f"{article.title} {article.content}".lower()
            positive_count += sum(1 for keyword in positive_keywords if keyword in text)
            negative_count += sum(1 for keyword in negative_keywords if keyword in text)
        
        # Calculate sentiment score
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            # No sentiment keywords found, neutral
            probabilities = [0.2, 0.6, 0.2]
            sentiment_score = 0.0
        else:
            sentiment_score = (positive_count - negative_count) / total_keywords
            
            # Map sentiment score to probabilities
            if sentiment_score > 0.3:
                probabilities = [0.7, 0.2, 0.1]  # Positive sentiment -> Buy
            elif sentiment_score < -0.3:
                probabilities = [0.1, 0.2, 0.7]  # Negative sentiment -> Sell
            else:
                probabilities = [0.2, 0.6, 0.2]  # Neutral sentiment -> Hold
        
        # Calculate dynamic confidence for rule-based analysis
        analysis_factors = {
            'probabilities': probabilities,
            'articles_analyzed': len(news_data.articles),
            'method': 'rule_based_sentiment',
            'sentiment_score': sentiment_score
        }
        
        confidence_score = ConfidenceCalculator.calculate_rule_based_confidence(
            1.0, analysis_factors
        )
        
        return ExpertOutput(
            probabilities=DecisionProbabilities.from_list(probabilities),
            confidence=ExpertConfidence(
                confidence_score=confidence_score,
                uncertainty=1.0 - confidence_score,
                reliability_score=0.7,
                metadata={'sentiment_score': sentiment_score}
            ),
            metadata=ExpertMetadata(
                expert_type="sentiment",
                model_name="rule_based",
                processing_time=processing_time,
                input_data_quality=0.8,
                additional_info={
                    'method': 'rule_based_sentiment',
                    'articles_analyzed': len(articles),
                    'positive_keywords': positive_count,
                    'negative_keywords': negative_count,
                    'sentiment_score': sentiment_score
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
                expert_type="sentiment",
                model_name="fallback",
                processing_time=processing_time,
                input_data_quality=0.0,
                additional_info={
                    'method': 'fallback',
                    'reason': reason
                }
            )
        )

def sentiment_expert(ticker: str, target_date: str, lookback_days: int = 7) -> ExpertOutput:
    """
    Main interface for sentiment expert analysis.
    
    Args:
        ticker (str): Stock ticker symbol
        target_date (str): Target date for analysis (YYYY-MM-DD)
        lookback_days (int): Number of days to look back for news
        
    Returns:
        ExpertOutput: Sentiment analysis result
    """
    expert = SentimentExpert()
    return expert.analyze_sentiment(ticker, target_date, lookback_days) 