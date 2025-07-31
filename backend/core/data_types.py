# data_types.py
# Type definitions and data structures used across the system (PortfolioState, TradeDecision, ExpertOutput, etc.).

"""
Type Definitions Implementation

This module defines all data structures and type hints used across the system.
It provides type safety and consistent data structures for all components.

RESPONSIBILITIES:

1. EXPERT OUTPUT TYPES:
   - ExpertOutput: Standard output format for all experts
   - DecisionProbabilities: [p_buy, p_hold, p_sell] structure
   - ExpertConfidence: Confidence scores and metadata
   - ExpertMetadata: Additional expert-specific information

2. TRADING DECISION TYPES:
   - TradeDecision: Final aggregated trading decision
   - DecisionType: Enum for Buy/Hold/Sell actions
   - DecisionConfidence: Confidence levels and reasoning
   - DecisionMetadata: Supporting information for decisions

3. PORTFOLIO STATE TYPES:
   - PortfolioState: Current portfolio status and positions
   - Position: Individual stock position information
   - CashBalance: Available cash and allocation
   - PortfolioMetrics: Performance and risk metrics
   - CashReserve: Reserve requirements and available trading capital
   - CapitalAllocation: Position sizing and allocation constraints

4. DATA MODALITY TYPES:
   - NewsData: Structured news article data
   - ChartData: Image and chart period information
   - FundamentalData: Financial statement data
   - PriceData: OHLCV time series data
   - DataAvailability: Coverage and missing data tracking
   - DataQuality: Quality metrics and validation results

5. DATA AVAILABILITY TYPES:
   - DataCoverage: Per-ticker data availability tracking
   - MissingDataReport: Gaps and missing periods analysis
   - DataQualityMetrics: Quality scores and validation results
   - AvailabilityStatus: Real-time data availability status

6. EVALUATION TYPES:
   - TradeLog: Record of all trading decisions
   - PortfolioMetrics: Portfolio-level performance data
   - TickerMetrics: Individual ticker performance data
   - BacktestResult: Complete backtesting results
   - EvaluationMetadata: Evaluation configuration and settings
   - MetricsHistory: Time-series metrics for both levels

7. SYSTEM TYPES:
   - Config: Configuration settings and parameters
   - LogEntry: Logging and debugging information
   - ErrorInfo: Error handling and reporting
   - CacheEntry: Caching and performance data
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any, Tuple
from datetime import date, datetime
from enum import Enum
from pathlib import Path
import numpy as np

# 1. EXPERT OUTPUT TYPES
@dataclass
class DecisionProbabilities:
    """[p_buy, p_hold, p_sell] structure for expert decisions."""
    buy_probability: float
    hold_probability: float
    sell_probability: float
    
    def __post_init__(self):
        """Validate probabilities sum to 1.0."""
        total = self.buy_probability + self.hold_probability + self.sell_probability
        if not np.isclose(total, 1.0, atol=1e-6):
            raise ValueError(f"Probabilities must sum to 1.0, got {total}")
    
    def to_list(self) -> List[float]:
        """Convert to list format [p_buy, p_hold, p_sell]."""
        return [self.buy_probability, self.hold_probability, self.sell_probability]
    
    @classmethod
    def from_list(cls, probabilities: List[float]) -> 'DecisionProbabilities':
        """Create from list format [p_buy, p_hold, p_sell]."""
        if len(probabilities) != 3:
            raise ValueError("Probabilities must have exactly 3 values")
        return cls(probabilities[0], probabilities[1], probabilities[2])

@dataclass
class ExpertConfidence:
    """Confidence scores and metadata for expert decisions."""
    confidence_score: float  # 0.0 to 1.0
    uncertainty: float  # 0.0 to 1.0
    reliability_score: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExpertMetadata:
    """Additional expert-specific information."""
    expert_type: str  # "sentiment", "technical_timeseries", "technical_chart", "fundamental"
    model_name: str
    processing_time: float  # seconds
    input_data_quality: float  # 0.0 to 1.0
    additional_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExpertOutput:
    """Standard output format for all experts."""
    probabilities: DecisionProbabilities
    confidence: ExpertConfidence
    metadata: ExpertMetadata
    timestamp: datetime = field(default_factory=datetime.now)

# 2. TRADING DECISION TYPES
class DecisionType(Enum):
    """Enum for Buy/Hold/Sell actions."""
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"

class TradeAction(Enum):
    """Trading actions (alias for DecisionType with uppercase values)."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class PositionStatus(Enum):
    """Position status."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PARTIAL = "PARTIAL"

@dataclass
class DecisionConfidence:
    """Confidence levels and reasoning for trading decisions."""
    overall_confidence: float  # 0.0 to 1.0
    expert_agreement: float  # 0.0 to 1.0
    market_conditions: str  # "bullish", "bearish", "neutral"
    reasoning: str
    risk_assessment: Dict[str, float] = field(default_factory=dict)

@dataclass
class DecisionMetadata:
    """Supporting information for trading decisions."""
    expert_contributions: Dict[str, float]  # Expert name -> contribution weight
    data_quality_scores: Dict[str, float]  # Modality -> quality score
    market_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class TradeDecision:
    """Final aggregated trading decision."""
    action: DecisionType
    confidence: DecisionConfidence
    metadata: DecisionMetadata
    ticker: str
    date: date

# 3. PORTFOLIO STATE TYPES
@dataclass
class Position:
    """Individual stock position information."""
    ticker: str
    shares: int
    average_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    entry_date: date
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class CashBalance:
    """Available cash and allocation information."""
    total_cash: float
    available_cash: float
    reserved_cash: float
    cash_reserve_ratio: float
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class CashReserve:
    """Reserve requirements and available trading capital."""
    required_reserve: float
    current_reserve: float
    available_trading_capital: float
    reserve_ratio: float
    min_reserve_ratio: float = 0.1  # 10% minimum

@dataclass
class CapitalAllocation:
    """Position sizing and allocation constraints."""
    max_position_size: float  # Maximum % of portfolio per position
    target_position_size: float  # Target % of portfolio per position
    min_position_size: float  # Minimum % of portfolio per position
    max_positions: int  # Maximum number of concurrent positions
    sector_limits: Dict[str, float] = field(default_factory=dict)  # Sector -> max %

@dataclass
class PortfolioState:
    """Current portfolio status and positions."""
    total_value: float
    cash_balance: CashBalance
    positions: Dict[str, Position]  # ticker -> position
    cash_reserve: CashReserve
    capital_allocation: CapitalAllocation
    date: date
    last_updated: datetime = field(default_factory=datetime.now)

# 4. DATA MODALITY TYPES
@dataclass
class NewsArticle:
    """Individual news article data."""
    title: str
    content: str
    source: str
    published_date: date
    sentiment_score: Optional[float] = None
    keywords: List[str] = field(default_factory=list)
    url: Optional[str] = None

@dataclass
class NewsData:
    """Structured news article data."""
    ticker: str
    articles: List[NewsArticle]
    date: date
    total_articles: int
    average_sentiment: Optional[float] = None

@dataclass
class ChartData:
    """Image and chart period information."""
    ticker: str
    period: str  # "H1", "H2", "Q1", etc.
    year: int
    image_path: Path
    image_data: Optional[bytes] = None
    chart_type: str = "candlestick"
    resolution: Tuple[int, int] = (800, 600)

@dataclass
class FinancialMetric:
    """Individual financial metric with time series data."""
    name: str
    values: List[float]
    dates: List[str]
    unit: str = "USD"
    
    def get_latest_value(self) -> Optional[float]:
        """Get the most recent value."""
        return self.values[-1] if self.values else None
    
    def get_latest_date(self) -> Optional[str]:
        """Get the most recent date."""
        return self.dates[-1] if self.dates else None

@dataclass
class FinancialStatement:
    """Individual financial statement data."""
    statement_type: str  # "balance_sheet", "income_statement", "cash_flow"
    company_name: str
    cik: str
    filings: List[Dict[str, Any]]
    metrics: Dict[str, FinancialMetric]
    filing_count: int

@dataclass
class FundamentalData:
    """Financial statement data."""
    ticker: str
    statements: Dict[str, FinancialStatement]  # statement_type -> statement
    total_statements: int
    data_quality: float  # 0.0 to 1.0

@dataclass
class ChartImage:
    """Individual chart image data."""
    file_path: str
    date: str  # YYYY-H1 or YYYY-H2
    year: int
    half: str  # H1 or H2
    start_date: str
    end_date: str
    width: int
    height: int
    image_data: np.ndarray  # Preprocessed image array
    metadata: Dict[str, Any]

@dataclass
class ChartData:
    """Chart image data."""
    ticker: str
    charts: List[ChartImage]
    total_charts: int
    data_quality: float  # 0.0 to 1.0

@dataclass
class PricePoint:
    """Individual OHLCV data point."""
    date: date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    adjusted_close: Optional[float] = None

@dataclass
class PriceData:
    """OHLCV time series data."""
    ticker: str
    prices: List[PricePoint]
    date_range: Tuple[date, date]
    data_points: int
    missing_dates: List[date] = field(default_factory=list)

# 5. DATA AVAILABILITY TYPES
class AvailabilityStatus(Enum):
    """Real-time data availability status."""
    AVAILABLE = "available"
    MISSING = "missing"
    PARTIAL = "partial"
    OUTDATED = "outdated"

@dataclass
class DataQuality:
    """Quality metrics and validation results."""
    completeness_score: float  # 0.0 to 1.0
    accuracy_score: float  # 0.0 to 1.0
    consistency_score: float  # 0.0 to 1.0
    timeliness_score: float  # 0.0 to 1.0
    overall_score: float  # 0.0 to 1.0
    issues: List[str] = field(default_factory=list)

@dataclass
class MissingDataReport:
    """Gaps and missing periods analysis."""
    ticker: str
    modality: str
    missing_dates: List[date]
    missing_periods: List[str]  # "2022_H1", "2022-Q1", etc.
    coverage_percentage: float
    gaps_analysis: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataCoverage:
    """Per-ticker data availability tracking."""
    ticker: str
    available_dates: List[date]
    missing_dates: List[date]
    coverage_percentage: float
    modality: str
    date_range: Tuple[date, date]
    quality: DataQuality = field(default_factory=lambda: DataQuality(1.0, 1.0, 1.0, 1.0, 1.0))

# 6. EVALUATION TYPES
@dataclass
class PortfolioMetrics:
    """Portfolio-level performance data."""
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    annualized_volatility: float
    max_drawdown: float
    drawdown_duration: int  # days
    win_rate: float
    profit_factor: float
    date: date

@dataclass
class TickerMetrics:
    """Individual ticker performance data."""
    ticker: str
    total_return: float
    contribution_to_portfolio: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trade_count: int
    average_hold_period: float  # days
    date: date

@dataclass
class MetricsHistory:
    """Time-series metrics for both levels."""
    portfolio_history: List[PortfolioMetrics]
    ticker_history: Dict[str, List[TickerMetrics]]  # ticker -> metrics list
    dates: List[date]

@dataclass
class TradeLog:
    """Record of all trading decisions."""
    date: date
    ticker: str
    action: DecisionType
    shares: int
    price: float
    value: float
    decision: TradeDecision
    portfolio_state: PortfolioState
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class BacktestResult:
    """Complete backtesting results."""
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    total_return: float
    portfolio_metrics: PortfolioMetrics
    ticker_metrics: Dict[str, TickerMetrics]
    trade_logs: List[TradeLog]
    metrics_history: MetricsHistory
    data_coverage: Dict[str, DataCoverage]
    execution_time: float  # seconds

@dataclass
class EvaluationMetadata:
    """Evaluation configuration and settings."""
    backtest_config: Dict[str, Any]
    expert_configs: Dict[str, Dict[str, Any]]
    data_config: Dict[str, Any]
    portfolio_config: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

# 7. SYSTEM TYPES
@dataclass
class LogEntry:
    """Logging and debugging information."""
    level: str  # "INFO", "WARNING", "ERROR", "DEBUG"
    message: str
    module: str
    timestamp: datetime = field(default_factory=datetime.now)
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ErrorInfo:
    """Error handling and reporting."""
    error_type: str
    error_message: str
    stack_trace: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CacheEntry:
    """Caching and performance data."""
    key: str
    data: Any
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)

# Type aliases for convenience
ExpertOutputList = List[ExpertOutput]
TradeDecisionList = List[TradeDecision]
PortfolioMetricsList = List[PortfolioMetrics]
TickerMetricsDict = Dict[str, TickerMetrics]
DataCoverageDict = Dict[str, DataCoverage]
ModalityData = Dict[str, Union[NewsData, ChartData, FundamentalData, PriceData]]

# Example usage functions
def create_expert_output(probabilities: List[float], expert_type: str, 
                        confidence: float = 0.8) -> ExpertOutput:
    """Helper function to create ExpertOutput."""
    return ExpertOutput(
        probabilities=DecisionProbabilities.from_list(probabilities),
        confidence=ExpertConfidence(
            confidence_score=confidence,
            uncertainty=1.0 - confidence,
            reliability_score=confidence
        ),
        metadata=ExpertMetadata(
            expert_type=expert_type,
            model_name="llama3.1",
            processing_time=0.5,
            input_data_quality=0.9
        )
    )

def create_trade_decision(action: DecisionType, ticker: str, 
                         confidence: float = 0.7) -> TradeDecision:
    """Helper function to create TradeDecision."""
    return TradeDecision(
        action=action,
        confidence=DecisionConfidence(
            overall_confidence=confidence,
            expert_agreement=confidence,
            market_conditions="neutral",
            reasoning="Expert consensus"
        ),
        metadata=DecisionMetadata(
            expert_contributions={"sentiment": 0.25, "technical": 0.25, 
                                "chart": 0.25, "fundamental": 0.25},
            data_quality_scores={"news": 0.9, "prices": 0.95, 
                               "charts": 0.8, "fundamentals": 0.7}
        ),
        ticker=ticker,
        date=date.today()
    )

# EVALUATION-SPECIFIC DATA TYPES (Unified from evaluation/data_types.py)
@dataclass
class EvaluationPosition:
    """Individual stock position for evaluation."""
    ticker: str
    quantity: int
    avg_price: float
    current_price: float
    status: PositionStatus = PositionStatus.OPEN
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate unrealized P&L after initialization."""
        self.unrealized_pnl = (self.current_price - self.avg_price) * self.quantity
    
    def update_price(self, new_price: float):
        """Update current price and recalculate P&L."""
        self.current_price = new_price
        self.unrealized_pnl = (self.current_price - self.avg_price) * self.quantity
        self.last_updated = datetime.now()
    
    def add_quantity(self, quantity: int, price: float):
        """Add to position (average down/up)."""
        total_cost = (self.quantity * self.avg_price) + (quantity * price)
        self.quantity += quantity
        self.avg_price = total_cost / self.quantity
        self.update_price(self.current_price)
    
    def reduce_quantity(self, quantity: int, price: float):
        """Reduce position."""
        if quantity >= self.quantity:
            # Close position
            self.realized_pnl += (price - self.avg_price) * self.quantity
            self.quantity = 0
            self.status = PositionStatus.CLOSED
        else:
            # Partial reduction
            self.realized_pnl += (price - self.avg_price) * quantity
            self.quantity -= quantity
            self.status = PositionStatus.PARTIAL
        
        self.update_price(price)

@dataclass
class EvaluationPortfolioState:
    """Current portfolio state for evaluation."""
    total_value: float
    cash: float
    positions: Dict[str, EvaluationPosition]
    date: datetime
    daily_return: float = 0.0
    total_pnl: float = 0.0
    cash_reserve: float = 0.0
    available_capital: float = 0.0
    
    def __post_init__(self):
        """Calculate derived values."""
        self.calculate_total_value()
        self.calculate_total_pnl()
    
    def calculate_total_value(self):
        """Calculate total portfolio value."""
        positions_value = sum(pos.quantity * pos.current_price for pos in self.positions.values())
        self.total_value = self.cash + positions_value
    
    def calculate_total_pnl(self):
        """Calculate total P&L."""
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
        self.total_pnl = unrealized_pnl + realized_pnl

@dataclass
class TradeRecord:
    """Individual trade record."""
    date: datetime
    ticker: str
    action: TradeAction
    quantity: int
    price: float
    value: float
    transaction_cost: float
    slippage: float
    total_cost: float
    confidence: float
    reasoning: str
    expert_outputs: Dict[str, Any]
    portfolio_state_before: EvaluationPortfolioState
    portfolio_state_after: EvaluationPortfolioState
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Calculate total cost."""
        self.total_cost = self.value + self.transaction_cost + self.slippage

@dataclass
class DailyMetrics:
    """Daily performance metrics."""
    date: datetime
    portfolio_value: float
    daily_return: float
    cumulative_return: float
    cash: float
    positions_value: float
    total_pnl: float
    unrealized_pnl: float
    realized_pnl: float
    num_positions: int
    max_drawdown: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float

@dataclass
class EvaluationTickerMetrics:
    """Individual ticker performance metrics for evaluation."""
    ticker: str
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    drawdown_duration: int
    volatility: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    contribution_to_portfolio: float
    num_trades: int
    avg_hold_time: float

@dataclass
class EvaluationPortfolioMetrics:
    """Overall portfolio performance metrics for evaluation."""
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    drawdown_duration: int
    volatility: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_return: float
    best_trade: float
    worst_trade: float
    avg_hold_time: float
    cash_drag: float
    diversification_score: float

@dataclass
class EvaluationBacktestResult:
    """Complete backtest results for evaluation."""
    portfolio_history: List[EvaluationPortfolioState]
    trade_log: List[TradeRecord]
    daily_metrics: List[DailyMetrics]
    portfolio_metrics: EvaluationPortfolioMetrics
    ticker_metrics: Dict[str, EvaluationTickerMetrics]
    data_coverage: Dict[str, Any]
    configuration: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    total_days: int
    trading_days: int
    success_rate: float

@dataclass
class TradeLoggerConfig:
    """Configuration for trade logging."""
    output_dir: str = "./logs"
    log_level: str = "INFO"
    enable_compression: bool = True
    max_file_size_mb: int = 100
    backup_count: int = 5
    flush_interval: int = 100

@dataclass
class PortfolioSimulatorConfig:
    """Configuration for portfolio simulation."""
    initial_capital: float = 100000
    position_sizing: float = 0.08  # 8% per position
    max_positions: int = 10
    cash_reserve: float = 0.2  # 20% cash reserve
    min_cash_reserve: float = 0.1  # 10% minimum
    transaction_cost: float = 0.001  # 0.1%
    slippage: float = 0.0005  # 0.05%
    enable_short_selling: bool = False
    enable_margin: bool = False
    max_position_size: float = 0.25  # 25% max per position

@dataclass
class BacktesterConfig:
    """Configuration for backtesting."""
    start_date: str = "2008-01-01"
    end_date: str = "2022-12-31"
    tickers: List[str] = field(default_factory=list)
    initial_capital: float = 100000
    position_sizing: float = 0.08
    max_positions: int = 10
    cash_reserve: float = 0.2
    min_cash_reserve: float = 0.1
    transaction_cost: float = 0.001
    slippage: float = 0.0005
    log_level: str = "INFO"
    enable_real_time_metrics: bool = True
    save_intermediate_results: bool = True
    checkpoint_interval: int = 30  # days

def create_evaluation_portfolio_state(
    cash: float,
    positions: Dict[str, EvaluationPosition],
    date: datetime,
    daily_return: float = 0.0
) -> EvaluationPortfolioState:
    """Create an evaluation portfolio state."""
    return EvaluationPortfolioState(
        total_value=cash + sum(pos.quantity * pos.current_price for pos in positions.values()),
        cash=cash,
        positions=positions,
        date=date,
        daily_return=daily_return
    )

def create_trade_record(
    date: datetime,
    ticker: str,
    action: TradeAction,
    quantity: int,
    price: float,
    confidence: float,
    reasoning: str,
    expert_outputs: Dict[str, Any],
    portfolio_state_before: EvaluationPortfolioState,
    portfolio_state_after: EvaluationPortfolioState,
    transaction_cost: float = 0.001,
    slippage: float = 0.0005,
    success: bool = True,
    error_message: Optional[str] = None
) -> TradeRecord:
    """Create a trade record."""
    value = quantity * price
    return TradeRecord(
        date=date,
        ticker=ticker,
        action=action,
        quantity=quantity,
        price=price,
        value=value,
        transaction_cost=transaction_cost,
        slippage=slippage,
        total_cost=value + transaction_cost + slippage,
        confidence=confidence,
        reasoning=reasoning,
        expert_outputs=expert_outputs,
        portfolio_state_before=portfolio_state_before,
        portfolio_state_after=portfolio_state_after,
        success=success,
        error_message=error_message
    ) 