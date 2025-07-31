# enums.py
# Enumerations for system-wide constants, such as decision types or expert names.

"""
Enumerations Implementation

This module defines all system-wide constants and enumerations used across the backend.
It provides type safety and centralized management of constant values.

RESPONSIBILITIES:

1. TRADING DECISION ENUMERATIONS:
   - Buy/Hold/Sell decision types
   - Decision confidence levels
   - Signal strength classifications
   - Trading action types

2. EXPERT MODULE ENUMERATIONS:
   - Expert names and identifiers
   - Expert types and categories
   - Expert status and availability
   - Expert weighting schemes

3. DATA MODALITY ENUMERATIONS:
   - Data types (news, charts, fundamentals, prices)
   - Data source identifiers
   - Data quality levels
   - Data format types
   - Data availability status (available, missing, partial)
   - Missing data types (missing entries, missing files, sparse data)

4. FINANCIAL METRICS ENUMERATIONS:
   - Metric types and categories
   - Performance indicators
   - Risk measurement types
   - Evaluation periods

5. SYSTEM STATUS ENUMERATIONS:
   - Processing states
   - Error types and severity levels
   - Logging levels
   - Cache status indicators
   - Capital constraint types (insufficient cash, reserve requirements)
   - Trading constraint status (executed, partial, skipped)

6. CONFIGURATION ENUMERATIONS:
   - Environment types
   - Model types and versions
   - Backtesting modes
   - Aggregation strategies
"""

from enum import Enum, auto
from typing import List

# 1. TRADING DECISION ENUMERATIONS
class DecisionType(Enum):
    """Buy/Hold/Sell decision types."""
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"

class DecisionConfidenceLevel(Enum):
    """Decision confidence levels."""
    VERY_LOW = "very_low"      # 0.0 - 0.2
    LOW = "low"                # 0.2 - 0.4
    MEDIUM = "medium"          # 0.4 - 0.6
    HIGH = "high"              # 0.6 - 0.8
    VERY_HIGH = "very_high"    # 0.8 - 1.0

class SignalStrength(Enum):
    """Signal strength classifications."""
    WEAK = "weak"              # 0.0 - 0.3
    MODERATE = "moderate"      # 0.3 - 0.6
    STRONG = "strong"          # 0.6 - 0.8
    VERY_STRONG = "very_strong" # 0.8 - 1.0

class TradingActionType(Enum):
    """Trading action types."""
    MARKET_BUY = "market_buy"
    MARKET_SELL = "market_sell"
    LIMIT_BUY = "limit_buy"
    LIMIT_SELL = "limit_sell"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

# 2. EXPERT MODULE ENUMERATIONS
class ExpertType(Enum):
    """Expert names and identifiers."""
    SENTIMENT = "sentiment_expert"
    TECHNICAL_TIMESERIES = "technical_timeseries_expert"
    TECHNICAL_CHART = "technical_chart_expert"
    FUNDAMENTAL = "fundamental_expert"

class ExpertCategory(Enum):
    """Expert types and categories."""
    TEXT_ANALYSIS = "text_analysis"      # Sentiment expert
    TECHNICAL_ANALYSIS = "technical_analysis"  # Timeseries and chart experts
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"  # Fundamental expert

class ExpertStatus(Enum):
    """Expert status and availability."""
    AVAILABLE = "available"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    INITIALIZING = "initializing"

class ExpertWeightingScheme(Enum):
    """Expert weighting schemes."""
    UNIFORM = "uniform"           # Equal weights
    CONFIDENCE_BASED = "confidence_based"  # Weight by confidence
    PERFORMANCE_BASED = "performance_based"  # Weight by historical performance
    ADAPTIVE = "adaptive"         # Dynamic weighting

# 3. DATA MODALITY ENUMERATIONS
class DataModality(Enum):
    """Data types (news, charts, fundamentals, prices)."""
    NEWS = "news"
    CHARTS = "charts"
    FUNDAMENTALS = "fundamentals"
    PRICES = "prices"

class DataSource(Enum):
    """Data source identifiers."""
    SP500_NEWS = "sp500_news"
    SP500_CHARTS = "sp500_charts"
    SP500_FUNDAMENTALS = "sp500_fundamentals"
    SP500_PRICES = "sp500_prices"

class DataQualityLevel(Enum):
    """Data quality levels."""
    EXCELLENT = "excellent"    # 0.9 - 1.0
    GOOD = "good"              # 0.7 - 0.9
    FAIR = "fair"              # 0.5 - 0.7
    POOR = "poor"              # 0.3 - 0.5
    UNUSABLE = "unusable"      # 0.0 - 0.3

class DataFormat(Enum):
    """Data format types."""
    JSON = "json"
    CSV = "csv"
    PNG = "png"
    JSONL = "jsonl"
    TXT = "txt"

class AvailabilityStatus(Enum):
    """Data availability status (available, missing, partial)."""
    AVAILABLE = "available"
    MISSING = "missing"
    PARTIAL = "partial"
    OUTDATED = "outdated"
    PROCESSING = "processing"

class MissingDataType(Enum):
    """Missing data types (missing entries, missing files, sparse data)."""
    MISSING_ENTRIES = "missing_entries"  # Missing data within files
    MISSING_FILES = "missing_files"      # Entire files missing
    SPARSE_DATA = "sparse_data"          # Insufficient data coverage
    CORRUPTED_DATA = "corrupted_data"    # Data corruption issues
    OUTDATED_DATA = "outdated_data"      # Data too old

# 4. FINANCIAL METRICS ENUMERATIONS
class MetricType(Enum):
    """Metric types and categories."""
    RETURN_METRICS = "return_metrics"
    RISK_METRICS = "risk_metrics"
    RISK_ADJUSTED_METRICS = "risk_adjusted_metrics"
    TRADING_METRICS = "trading_metrics"
    PORTFOLIO_METRICS = "portfolio_metrics"

class PerformanceIndicator(Enum):
    """Performance indicators."""
    TOTAL_RETURN = "total_return"
    ANNUALIZED_RETURN = "annualized_return"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    CALMAR_RATIO = "calmar_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"

class RiskMeasurementType(Enum):
    """Risk measurement types."""
    VOLATILITY = "volatility"
    VAR = "value_at_risk"
    CVAR = "conditional_var"
    BETA = "beta"
    CORRELATION = "correlation"
    DRAWDOWN = "drawdown"

class EvaluationPeriod(Enum):
    """Evaluation periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"

# 5. SYSTEM STATUS ENUMERATIONS
class ProcessingState(Enum):
    """Processing states."""
    IDLE = "idle"
    LOADING_DATA = "loading_data"
    ANALYZING = "analyzing"
    AGGREGATING = "aggregating"
    TRADING = "trading"
    UPDATING_METRICS = "updating_metrics"
    COMPLETED = "completed"
    ERROR = "error"

class ErrorType(Enum):
    """Error types and severity levels."""
    DATA_ERROR = "data_error"
    LLM_ERROR = "llm_error"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class CacheStatus(Enum):
    """Cache status indicators."""
    HIT = "hit"
    MISS = "miss"
    EXPIRED = "expired"
    INVALID = "invalid"

class CapitalConstraintType(Enum):
    """Capital constraint types (insufficient cash, reserve requirements)."""
    INSUFFICIENT_CASH = "insufficient_cash"
    RESERVE_REQUIREMENT = "reserve_requirement"
    MAX_POSITION_LIMIT = "max_position_limit"
    SECTOR_LIMIT = "sector_limit"
    LEVERAGE_LIMIT = "leverage_limit"

class TradingConstraintStatus(Enum):
    """Trading constraint status (executed, partial, skipped)."""
    EXECUTED = "executed"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    PENDING = "pending"
    CANCELLED = "cancelled"

# 6. CONFIGURATION ENUMERATIONS
class EnvironmentType(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class ModelType(Enum):
    """Model types and versions."""
    LLAMA_3_1 = "llama3.1"
    LLAMA_3_1_70B = "llama3.1:70b"
    MISTRAL_7B = "mistral:7b"
    CODELLAMA_7B = "codellama:7b"
    CUSTOM = "custom"

class BacktestingMode(Enum):
    """Backtesting modes."""
    HISTORICAL = "historical"
    WALK_FORWARD = "walk_forward"
    MONTE_CARLO = "monte_carlo"
    STRESS_TEST = "stress_test"

class AggregationStrategy(Enum):
    """Aggregation strategies."""
    WEIGHTED_AVERAGE = "weighted_average"
    MAJORITY_VOTE = "majority_vote"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    PERFORMANCE_WEIGHTED = "performance_weighted"
    ADAPTIVE_WEIGHTING = "adaptive_weighting"

# Utility functions
def get_expert_types() -> List[ExpertType]:
    """Get all expert types."""
    return list(ExpertType)

def get_data_modalities() -> List[DataModality]:
    """Get all data modalities."""
    return list(DataModality)

def get_metric_types() -> List[MetricType]:
    """Get all metric types."""
    return list(MetricType)

def get_performance_indicators() -> List[PerformanceIndicator]:
    """Get all performance indicators."""
    return list(PerformanceIndicator)

def get_decision_types() -> List[DecisionType]:
    """Get all decision types."""
    return list(DecisionType)

def get_error_types() -> List[ErrorType]:
    """Get all error types."""
    return list(ErrorType)

# Mapping functions for convenience
def expert_type_to_category(expert_type: ExpertType) -> ExpertCategory:
    """Map expert type to category."""
    mapping = {
        ExpertType.SENTIMENT: ExpertCategory.TEXT_ANALYSIS,
        ExpertType.TECHNICAL_TIMESERIES: ExpertCategory.TECHNICAL_ANALYSIS,
        ExpertType.TECHNICAL_CHART: ExpertCategory.TECHNICAL_ANALYSIS,
        ExpertType.FUNDAMENTAL: ExpertCategory.FUNDAMENTAL_ANALYSIS
    }
    return mapping.get(expert_type, ExpertCategory.TECHNICAL_ANALYSIS)

def data_modality_to_format(data_modality: DataModality) -> DataFormat:
    """Map data modality to expected format."""
    mapping = {
        DataModality.NEWS: DataFormat.JSONL,
        DataModality.CHARTS: DataFormat.PNG,
        DataModality.FUNDAMENTALS: DataFormat.JSON,
        DataModality.PRICES: DataFormat.CSV
    }
    return mapping.get(data_modality, DataFormat.JSON)

def confidence_to_level(confidence_score: float) -> DecisionConfidenceLevel:
    """Convert confidence score to confidence level."""
    if confidence_score >= 0.8:
        return DecisionConfidenceLevel.VERY_HIGH
    elif confidence_score >= 0.6:
        return DecisionConfidenceLevel.HIGH
    elif confidence_score >= 0.4:
        return DecisionConfidenceLevel.MEDIUM
    elif confidence_score >= 0.2:
        return DecisionConfidenceLevel.LOW
    else:
        return DecisionConfidenceLevel.VERY_LOW

def quality_score_to_level(quality_score: float) -> DataQualityLevel:
    """Convert quality score to quality level."""
    if quality_score >= 0.9:
        return DataQualityLevel.EXCELLENT
    elif quality_score >= 0.7:
        return DataQualityLevel.GOOD
    elif quality_score >= 0.5:
        return DataQualityLevel.FAIR
    elif quality_score >= 0.3:
        return DataQualityLevel.POOR
    else:
        return DataQualityLevel.UNUSABLE

 