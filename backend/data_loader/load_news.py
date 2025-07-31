"""
load_news.py

News Data Loader for daily news articles in JSONL format.
Handles raw data loading and basic preprocessing of news articles.
Focuses on data I/O, parsing, and structure conversion, NOT sentiment analysis.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import pandas as pd

from core.logging_config import get_logger
from core.date_utils import parse_date
from core.data_types import NewsData, NewsArticle

logger = get_logger("load_news")

class NewsDataLoader:
    """Loader for daily news articles in JSONL format."""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the news data loader.
        
        Args:
            data_path (str, optional): Path to news data directory
        """
        if data_path is None:
            from core.config import config
            data_path = config.DATA_PATH
        
        self.data_path = Path(data_path) / "SP500_news"
        logger.info(f"News data loader initialized with path: {self.data_path}")
    
    def load_news_for_ticker(self, ticker: str, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> Optional[NewsData]:
        """
        Load news articles for a specific ticker within a date range.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AA')
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            NewsData or None: Structured news data or None if file not found
        """
        # Keep original case for file lookup, but store ticker in lowercase for consistency
        original_ticker = ticker
        ticker = ticker.lower()
        file_path = self.data_path / f"{original_ticker}.jsonl"
        
        if not file_path.exists():
            logger.warning(f"News file not found for ticker {ticker}: {file_path}")
            return None
        
        try:
            logger.info(f"Loading news for {ticker} from {file_path}")
            articles = self._parse_jsonl_file(file_path, start_date, end_date)
            
            if not articles:
                logger.warning(f"No news articles found for {ticker} in specified date range")
                return None
            
            # Group articles by date
            articles_by_date = self._group_articles_by_date(articles)
            
            # Create NewsData object
            news_data = NewsData(
                ticker=ticker,
                articles=articles,
                date=articles[0].published_date if articles else date.today(),
                total_articles=len(articles)
            )
            
            logger.info(f"Loaded {len(articles)} articles for {ticker}")
            return news_data
            
        except Exception as e:
            logger.error(f"Error loading news for {ticker}: {e}")
            return None
    
    def _parse_jsonl_file(self, file_path: Path, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> List[NewsArticle]:
        """
        Parse JSONL file and extract news articles.
        
        Args:
            file_path (Path): Path to JSONL file
            start_date (str, optional): Start date filter
            end_date (str, optional): End date filter
            
        Returns:
            List[NewsArticle]: List of parsed news articles
        """
        articles = []
        line_count = 0
        error_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line_count += 1
                    
                    try:
                        # Parse JSON line
                        data = json.loads(line.strip())
                        
                        # Extract and validate required fields
                        article_date = self._extract_date(data.get('Date'))
                        if article_date is None:
                            logger.warning(f"Invalid date format in line {line_num}: {data.get('Date')}")
                            error_count += 1
                            continue
                        
                        # Apply date filters
                        if start_date and article_date < parse_date(start_date):
                            continue
                        if end_date and article_date > parse_date(end_date):
                            continue
                        
                        # Create NewsArticle object
                        article = NewsArticle(
                            title=data.get('Article_title', '').strip(),
                            content=data.get('Article', '').strip(),
                            source=data.get('Url', '').strip(),
                            published_date=article_date,
                            keywords=[]  # Will be populated by sentiment expert if needed
                        )
                        
                        # Skip articles with no content
                        if not article.content:
                            logger.debug(f"Skipping article with no content in line {line_num}")
                            continue
                        
                        articles.append(article)
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON in line {line_num}: {e}")
                        error_count += 1
                        continue
                    except Exception as e:
                        logger.warning(f"Error processing line {line_num}: {e}")
                        error_count += 1
                        continue
            
            logger.info(f"Parsed {len(articles)} valid articles from {line_count} lines")
            if error_count > 0:
                logger.warning(f"Encountered {error_count} errors during parsing")
            
            return articles
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []
    
    def _extract_date(self, date_str: str) -> Optional[date]:
        """
        Extract and normalize date from various formats.
        
        Args:
            date_str (str): Date string in various formats
            
        Returns:
            date or None: Normalized date or None if invalid
        """
        if not date_str:
            return None
        
        try:
            # Try to parse the date using the core parse_date function
            return parse_date(date_str)
        except ValueError:
            # If parse_date fails, try additional formats
            try:
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                
                logger.warning(f"Could not parse date: {date_str}")
                return None
                
            except Exception as e:
                logger.warning(f"Error parsing date '{date_str}': {e}")
                return None
    
    def _group_articles_by_date(self, articles: List[NewsArticle]) -> Dict[date, List[NewsArticle]]:
        """
        Group articles by publication date.
        
        Args:
            articles (List[NewsArticle]): List of articles
            
        Returns:
            Dict[date, List[NewsArticle]]: Articles grouped by date
        """
        grouped = {}
        for article in articles:
            date_key = article.published_date
            if date_key not in grouped:
                grouped[date_key] = []
            grouped[date_key].append(article)
        
        return grouped
    
    def get_news_coverage(self, ticker: str) -> Dict[str, Any]:
        """
        Get news coverage statistics for a ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict[str, Any]: Coverage statistics
        """
        news_data = self.load_news_for_ticker(ticker)
        if not news_data:
            return {
                'ticker': ticker,
                'total_articles': 0,
                'date_range': None,
                'coverage_percentage': 0.0,
                'avg_articles_per_day': 0.0
            }
        
        articles = news_data.articles
        if not articles:
            return {
                'ticker': ticker,
                'total_articles': 0,
                'date_range': None,
                'coverage_percentage': 0.0,
                'avg_articles_per_day': 0.0
            }
        
        # Calculate statistics
        dates = [article.published_date for article in articles]
        min_date = min(dates)
        max_date = max(dates)
        total_days = (max_date - min_date).days + 1
        unique_dates = len(set(dates))
        
        return {
            'ticker': ticker,
            'total_articles': len(articles),
            'date_range': (min_date, max_date),
            'coverage_percentage': (unique_dates / total_days) * 100 if total_days > 0 else 0.0,
            'avg_articles_per_day': len(articles) / unique_dates if unique_dates > 0 else 0.0,
            'unique_dates': unique_dates,
            'total_days': total_days
        }

def load_news_for_ticker(ticker: str, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> Optional[NewsData]:
    """
    Convenience function to load news for a ticker.
    
    Args:
        ticker (str): Stock ticker symbol
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
        
    Returns:
        NewsData or None: Structured news data
    """
    loader = NewsDataLoader()
    return loader.load_news_for_ticker(ticker, start_date, end_date) 