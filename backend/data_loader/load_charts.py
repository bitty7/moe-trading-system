#!/usr/bin/env python3
"""
load_charts.py

Loads candlestick chart images from PNG files.
Handles image loading, preprocessing, and metadata extraction.
Tracks chart availability and missing data for reporting and downstream processing.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
import cv2
import numpy as np
from PIL import Image

from core.logging_config import get_logger
from core.date_utils import parse_date
from core.data_types import ChartData, ChartImage

logger = get_logger("load_charts")

class ChartDataLoader:
    """
    Loads and preprocesses candlestick chart images.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize chart data loader.
        
        Args:
            data_path (str, optional): Path to chart data directory
        """
        if data_path is None:
            from core.config import config
            data_path = config.DATA_PATH
        
        self.data_path = Path(data_path) / "SP500_images"
        logger.info(f"Chart data loader initialized with path: {self.data_path}")
    
    def load_charts_for_ticker(self, ticker: str, start_date: Optional[str] = None, 
                              end_date: Optional[str] = None) -> Optional[ChartData]:
        """
        Load chart images for a given ticker and date range.
        
        Args:
            ticker (str): Stock ticker symbol
            start_date (str, optional): Start date (YYYY-MM-DD)
            end_date (str, optional): End date (YYYY-MM-DD)
            
        Returns:
            ChartData or None: Chart data object or None if not found
        """
        try:
            # Convert ticker to lowercase for directory lookup
            ticker_lower = ticker.lower()
            ticker_dir = self.data_path / ticker_lower
            
            if not ticker_dir.exists():
                logger.warning(f"Chart directory not found for ticker {ticker}: {ticker_dir}")
                return None
            
            # Find all PNG files in the ticker directory
            chart_files = list(ticker_dir.glob("*.png"))
            if not chart_files:
                logger.warning(f"No chart files found for ticker {ticker}")
                return None
            
            # Parse chart metadata from filenames
            charts = []
            for chart_file in chart_files:
                chart_info = self._parse_chart_filename(chart_file.name)
                if chart_info:
                    # Apply date filtering if specified
                    if start_date or end_date:
                        if not self._is_date_in_range(chart_info['date'], start_date, end_date):
                            continue
                    
                    # Load and preprocess the image
                    chart_image = self._load_chart_image(chart_file, chart_info)
                    if chart_image:
                        charts.append(chart_image)
            
            if not charts:
                logger.warning(f"No valid charts found for ticker {ticker} in specified date range")
                return None
            
            # Sort charts by date
            charts.sort(key=lambda x: x.date)
            
            # Calculate data quality score
            data_quality = self._calculate_data_quality(charts)
            
            return ChartData(
                ticker=ticker,
                charts=charts,
                total_charts=len(charts),
                data_quality=data_quality
            )
            
        except Exception as e:
            logger.error(f"Error loading charts for ticker {ticker}: {e}")
            return None
    
    def _parse_chart_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Parse chart metadata from filename.
        Expected format: {ticker}_{year}_{half}_candlestick.png
        Example: aa_2024_H1_candlestick.png
        
        Args:
            filename (str): Chart filename
            
        Returns:
            Dict or None: Parsed metadata or None if invalid
        """
        try:
            # Remove .png extension
            name = filename.replace('.png', '')
            
            # Split by underscore
            parts = name.split('_')
            if len(parts) != 4 or parts[3] != 'candlestick':
                logger.debug(f"Invalid chart filename format: {filename}")
                return None
            
            ticker = parts[0]
            year = int(parts[1])
            half = parts[2]  # H1 or H2
            
            # Convert half to date range
            if half == 'H1':
                start_date = f"{year}-01-01"
                end_date = f"{year}-06-30"
            elif half == 'H2':
                start_date = f"{year}-07-01"
                end_date = f"{year}-12-31"
            else:
                logger.debug(f"Invalid half format in filename: {filename}")
                return None
            
            return {
                'ticker': ticker,
                'year': year,
                'half': half,
                'start_date': start_date,
                'end_date': end_date,
                'date': f"{year}-{half}"  # Use year-half as date identifier
            }
            
        except Exception as e:
            logger.debug(f"Error parsing chart filename {filename}: {e}")
            return None
    
    def _is_date_in_range(self, chart_date: str, start_date: Optional[str], 
                          end_date: Optional[str]) -> bool:
        """
        Check if chart date is within specified range.
        
        Args:
            chart_date (str): Chart date (YYYY-H1 or YYYY-H2)
            start_date (str, optional): Start date (YYYY-MM-DD)
            end_date (str, optional): End date (YYYY-MM-DD)
            
        Returns:
            bool: True if in range, False otherwise
        """
        try:
            # Parse chart date (YYYY-H1 or YYYY-H2)
            year, half = chart_date.split('-')
            year = int(year)
            
            # Convert to start of period
            if half == 'H1':
                chart_start = f"{year}-01-01"
            else:  # H2
                chart_start = f"{year}-07-01"
            
            # Check start date
            if start_date and chart_start < start_date:
                return False
            
            # Check end date
            if end_date and chart_start > end_date:
                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Error checking date range for {chart_date}: {e}")
            return False
    
    def _load_chart_image(self, file_path: Path, metadata: Dict[str, Any]) -> Optional[ChartImage]:
        """
        Load and preprocess chart image.
        
        Args:
            file_path (Path): Path to chart image file
            metadata (Dict[str, Any]): Chart metadata
            
        Returns:
            ChartImage or None: Loaded chart image or None if error
        """
        try:
            # Load image using PIL
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Get image dimensions
                width, height = img.size
                
                # Convert to numpy array for OpenCV processing
                img_array = np.array(img)
                
                # Basic preprocessing
                processed_image = self._preprocess_image(img_array)
                
                return ChartImage(
                    file_path=str(file_path),
                    date=metadata['date'],
                    year=metadata['year'],
                    half=metadata['half'],
                    start_date=metadata['start_date'],
                    end_date=metadata['end_date'],
                    width=width,
                    height=height,
                    image_data=processed_image,
                    metadata={
                        'original_size': (width, height),
                        'file_size': file_path.stat().st_size,
                        'format': 'PNG'
                    }
                )
                
        except Exception as e:
            logger.error(f"Error loading chart image {file_path}: {e}")
            return None
    
    def _preprocess_image(self, image_array: np.ndarray) -> np.ndarray:
        """
        Preprocess chart image for analysis.
        
        Args:
            image_array (np.ndarray): Input image array
            
        Returns:
            np.ndarray: Preprocessed image array
        """
        try:
            # Convert to grayscale for chart analysis
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            # Resize to standard size for consistency
            target_size = (800, 600)  # Standard chart size
            resized = cv2.resize(gray, target_size)
            
            # Normalize pixel values
            normalized = resized.astype(np.float32) / 255.0
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image_array
    
    def _calculate_data_quality(self, charts: List[ChartImage]) -> float:
        """
        Calculate data quality score based on chart availability and quality.
        
        Args:
            charts (List[ChartImage]): List of chart images
            
        Returns:
            float: Data quality score (0.0 to 1.0)
        """
        if not charts:
            return 0.0
        
        # Base quality score
        quality_score = 0.5
        
        # Bonus for having multiple charts
        if len(charts) >= 5:
            quality_score += 0.2
        elif len(charts) >= 3:
            quality_score += 0.1
        
        # Bonus for recent data
        current_year = datetime.now().year
        recent_charts = sum(1 for chart in charts if chart.year >= current_year - 2)
        if recent_charts > 0:
            quality_score += 0.2 * (recent_charts / len(charts))
        
        # Bonus for consistent image quality
        valid_sizes = sum(1 for chart in charts if chart.width >= 600 and chart.height >= 400)
        if valid_sizes > 0:
            quality_score += 0.1 * (valid_sizes / len(charts))
        
        return min(1.0, quality_score)
    
    def get_chart_coverage(self, ticker: str) -> Dict[str, Any]:
        """
        Get chart data coverage information for a ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict[str, Any]: Coverage information
        """
        try:
            ticker_lower = ticker.lower()
            ticker_dir = self.data_path / ticker_lower
            
            if not ticker_dir.exists():
                return {
                    'ticker': ticker,
                    'available': False,
                    'total_files': 0,
                    'years_covered': [],
                    'data_quality': 0.0
                }
            
            # Find all chart files
            chart_files = list(ticker_dir.glob("*.png"))
            
            # Parse years covered
            years_covered = set()
            for chart_file in chart_files:
                metadata = self._parse_chart_filename(chart_file.name)
                if metadata:
                    years_covered.add(metadata['year'])
            
            return {
                'ticker': ticker,
                'available': True,
                'total_files': len(chart_files),
                'years_covered': sorted(list(years_covered)),
                'data_quality': self._calculate_data_quality([]) if not chart_files else 0.8
            }
            
        except Exception as e:
            logger.error(f"Error getting chart coverage for {ticker}: {e}")
            return {
                'ticker': ticker,
                'available': False,
                'total_files': 0,
                'years_covered': [],
                'data_quality': 0.0
            }

def load_charts_for_ticker(ticker: str, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None) -> Optional[ChartData]:
    """
    Convenience function to load charts for a ticker.
    
    Args:
        ticker (str): Stock ticker symbol
        start_date (str, optional): Start date (YYYY-MM-DD)
        end_date (str, optional): End date (YYYY-MM-DD)
        
    Returns:
        ChartData or None: Chart data object or None if not found
    """
    loader = ChartDataLoader()
    return loader.load_charts_for_ticker(ticker, start_date, end_date) 