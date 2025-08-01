# React Frontend Dashboard Requirements

## Overview

This document outlines the requirements for building a comprehensive, interactive React-based dashboard for visualizing MoE backtesting results. The dashboard will provide a professional, enterprise-grade experience with rich visualizations, real-time data exploration, and advanced analytics capabilities.

## Technology Stack

### Core Framework
- **React 18+**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **Material-UI (MUI)**: Professional UI components and theming
- **React Router**: Client-side routing and navigation

### Visualization Libraries
- **Recharts**: Interactive charts and graphs
- **MUI X Charts**: Advanced charting capabilities
- **MUI X Data Grid**: Professional data tables with sorting, filtering, pagination

### Data & State Management
- **Axios**: HTTP client for API calls
- **React Query/TanStack Query**: Server state management and caching
- **React Context**: Local state management

### Additional Libraries
- **Day.js**: Lightweight date manipulation
- **React Hook Form**: Form handling and validation
- **React Virtualized**: Performance optimization for large datasets

## Dashboard Structure

### Navigation Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Header: Logo | Run Selector | Date Range | User Menu        │
├─────────────────────────────────────────────────────────────┤
│ Sidebar Navigation                                          │
│ ├── 📊 Overview                                            │
│ ├── 🧠 Expert Recommendations                              │
│ ├── ⏰ Time Analysis                                       │
│ ├── 💼 Portfolio Analysis                                  │
│ ├── 🏢 Company Metrics                                     │
│ ├── 🔍 Expert Performance                                  │
│ └── 📈 Decision Analysis                                   │
├─────────────────────────────────────────────────────────────┤
│ Main Content Area                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Interactive Charts, Tables, and Visualizations         │ │
│ │ (Zoom, Pan, Hover, Drill-down, Export)                 │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Core Features & Tabs

### 1. 📊 Overview Tab
**Purpose**: High-level system performance and key metrics

**Components**:
- **System Performance Cards**:
  - Total Portfolio Value
  - Overall Return (Total & Annualized)
  - Sharpe Ratio
  - Maximum Drawdown
  - Win Rate
  - Number of Trades
  - Portfolio Volatility

- **Performance Summary Chart**:
  - Portfolio value over time (line chart)
  - Benchmark comparison (if available)
  - Interactive tooltips with detailed metrics

- **Key Metrics Dashboard**:
  - Risk-adjusted returns
  - Performance attribution
  - Asset allocation summary
  - Trading activity summary

**Interactive Features**:
- Date range selector for performance analysis
- Hover details with exact values and percentages
- Zoom and pan capabilities
- Export functionality (PNG, PDF, CSV)

### 2. 🧠 Expert Recommendations Tab
**Purpose**: Display expert recommendations and insights by year

**Components**:
- **Year Selector**: Dropdown to select specific year
- **Expert Recommendations Table**:
  - Expert name
  - Company/ticker
  - Recommendation (Buy/Hold/Sell)
  - Confidence level
  - Reasoning/justification
  - Date of recommendation

- **Expert Performance Summary**:
  - Success rate by expert
  - Average confidence levels
  - Number of recommendations per expert
  - Performance comparison chart

- **Recommendation Timeline**:
  - Visual timeline of all expert recommendations
  - Color-coded by recommendation type
  - Interactive filtering by expert, company, or recommendation type

**Interactive Features**:
- Filter by expert, company, recommendation type
- Sort by date, confidence, or performance
- Search functionality
- Export recommendations to CSV/Excel

### 3. ⏰ Time Analysis Tab
**Purpose**: Temporal analysis of system performance and patterns

**Components**:
- **Time Series Analysis**:
  - Daily returns distribution
  - Rolling performance metrics (30-day, 90-day, 1-year)
  - Volatility clustering analysis
  - Seasonal performance patterns

- **Performance Heatmaps**:
  - Monthly returns heatmap
  - Day-of-week performance patterns
  - Intraday performance (if available)

- **Trend Analysis**:
  - Moving averages
  - Performance momentum
  - Trend strength indicators

**Interactive Features**:
- Adjustable time windows
- Multiple timeframe analysis
- Statistical significance indicators
- Pattern recognition highlights

### 4. 💼 Portfolio Analysis Tab
**Purpose**: Comprehensive portfolio performance and risk metrics

**Components**:
- **Portfolio Metrics Dashboard**:
  - Risk metrics (VaR, CVaR, Beta)
  - Return metrics (Sharpe, Sortino, Calmar ratios)
  - Drawdown analysis
  - Correlation matrix

- **Asset Allocation Analysis**:
  - Current allocation pie chart
  - Historical allocation changes
  - Rebalancing analysis
  - Sector/industry breakdown

- **Risk-Return Analysis**:
  - Efficient frontier visualization
  - Risk-adjusted return scatter plot
  - Performance attribution analysis

- **Trading Analysis**:
  - Trade frequency analysis
  - Position sizing analysis
  - Transaction cost analysis
  - Turnover analysis

**Interactive Features**:
- Interactive correlation matrix
- Risk-return scatter plot with hover details
- Portfolio optimization suggestions
- Stress testing scenarios

### 5. 🏢 Company Metrics Tab
**Purpose**: Individual company performance analysis with selection capability

**Components**:
- **Company Selector**:
  - Multi-select dropdown for companies in portfolio
  - Search and filter functionality
  - Quick selection presets

- **Company Performance Dashboard**:
  - Individual stock performance charts
  - Risk metrics (volatility, beta, VaR)
  - Return metrics (total return, alpha, information ratio)
  - Risk-adjusted metrics (Sharpe, Sortino ratios)

- **Comparative Analysis**:
  - Side-by-side company comparison
  - Performance ranking table
  - Risk-adjusted performance comparison
  - Correlation analysis between selected companies

- **Company-Specific Metrics**:
  - Technical indicators
  - Fundamental metrics (if available)
  - Expert confidence trends
  - Decision frequency analysis

**Interactive Features**:
- Multi-company selection and comparison
- Interactive performance charts
- Risk-return visualization
- Export company-specific reports

### 6. 🔍 Expert Performance Tab
**Purpose**: Compare expert performance on individual companies

**Components**:
- **Company Selector**: Choose specific company for analysis
- **Expert Performance Comparison**:
  - Success rate by expert for selected company
  - Average confidence levels
  - Decision accuracy metrics
  - Performance over time

- **Expert Ranking Table**:
  - Expert name
  - Success rate
  - Average confidence
  - Number of decisions
  - Performance score

- **Performance Visualization**:
  - Expert performance radar chart
  - Confidence vs accuracy scatter plot
  - Decision timeline by expert
  - Performance trends over time

**Interactive Features**:
- Company-specific expert analysis
- Performance filtering and sorting
- Expert comparison charts
- Historical performance tracking

### 7. 📈 Decision Analysis Tab
**Purpose**: Visualize expert decisions, confidence levels, and aggregation

**Components**:
- **Decision Timeline**:
  - Daily decisions for selected company
  - Expert confidence levels over time
  - Decision probabilities (Buy/Hold/Sell)
  - Final aggregated decisions

- **Expert Decision Breakdown**:
  - Individual expert decisions and reasoning
  - Confidence levels for each expert
  - Decision probabilities visualization
  - Expert agreement/disagreement patterns

- **Aggregation Analysis**:
  - How expert decisions are combined
  - Final confidence calculation
  - Decision consensus analysis
  - Weight evolution over time

- **Decision Quality Metrics**:
  - Decision success rate
  - Confidence vs outcome analysis
  - Expert agreement patterns
  - Decision impact analysis

**Interactive Features**:
- Interactive decision timeline
- Expert decision drill-down
- Confidence level visualization
- Decision outcome tracking

## Data Integration

### API Structure
```typescript
interface BacktestData {
  config: BacktestConfig;
  portfolio_daily: PortfolioDaily[];
  tickers_daily: Record<string, TickerDaily[]>;
  trades: Trade[];
  results: BacktestResults;
}

interface BacktestConfig {
  backtest_id: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  tickers: string[];
  // ... other config fields
}

interface PortfolioDaily {
  date: string;
  total_value: number;
  cash: number;
  positions_value: number;
  daily_return: number;
  cumulative_return: number;
  // ... other portfolio metrics
}

interface TickerDaily {
  date: string;
  price: number;
  decision: 'BUY' | 'HOLD' | 'SELL';
  overall_confidence: number;
  expert_contributions: Record<string, ExpertContribution>;
  final_probabilities: [number, number, number]; // [buy, hold, sell]
  reasoning: string;
}

interface ExpertContribution {
  weight: number;
  confidence: number;
  probabilities: [number, number, number];
  reasoning: string;
}
```

### Data Loading Strategy
- **Lazy Loading**: Load data on demand for each tab
- **Caching**: Cache processed data for performance
- **Real-time Updates**: Refresh data when new runs complete
- **Error Handling**: Graceful handling of missing or corrupted data

## User Experience Requirements

### Performance
- **Load Time**: < 2 seconds for initial page load
- **Chart Rendering**: < 500ms for chart updates
- **Data Processing**: < 1 second for large datasets
- **Responsive Design**: Works on desktop, tablet, and mobile

### Interactivity
- **Hover Details**: Rich tooltips with detailed information
- **Zoom & Pan**: Interactive chart navigation
- **Drill-down**: Click to explore deeper levels
- **Filters**: Multi-dimensional filtering and search
- **Export**: Multiple export formats (PNG, PDF, CSV, Excel)

### Accessibility
- **WCAG 2.1 AA Compliance**: Full accessibility support
- **Keyboard Navigation**: Complete keyboard accessibility
- **Screen Reader Support**: Proper ARIA labels and descriptions
- **Color Contrast**: High contrast ratios for readability

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
1. **Project Setup**
   - React app with TypeScript
   - Material-UI theming and components
   - Routing and navigation structure
   - Basic layout and styling

2. **Data Integration**
   - API client setup with Axios
   - Data loading and caching
   - Error handling and loading states
   - Type definitions

3. **Basic Components**
   - Header with run selector
   - Sidebar navigation
   - Basic chart components
   - Data tables

### Phase 2: Overview & Portfolio Analysis (Week 3-4)
1. **Overview Tab**
   - System performance cards
   - Portfolio value charts
   - Key metrics dashboard
   - Interactive features

2. **Portfolio Analysis Tab**
   - Risk metrics visualization
   - Asset allocation charts
   - Performance attribution
   - Trading analysis

### Phase 3: Expert Analysis (Week 5-6)
1. **Expert Recommendations Tab**
   - Year-based recommendations
   - Expert performance summary
   - Recommendation timeline
   - Filtering and search

2. **Expert Performance Tab**
   - Company-specific expert analysis
   - Performance comparison
   - Ranking and metrics
   - Historical tracking

### Phase 4: Company & Decision Analysis (Week 7-8)
1. **Company Metrics Tab**
   - Multi-company selection
   - Individual performance analysis
   - Comparative analysis
   - Risk-adjusted metrics

2. **Decision Analysis Tab**
   - Decision timeline visualization
   - Expert decision breakdown
   - Aggregation analysis
   - Decision quality metrics

### Phase 5: Time Analysis & Advanced Features (Week 9-10)
1. **Time Analysis Tab**
   - Time series analysis
   - Performance heatmaps
   - Trend analysis
   - Pattern recognition

2. **Advanced Features**
   - Export functionality
   - Advanced filtering
   - Performance optimization
   - Mobile responsiveness

### Phase 6: Polish & Deployment (Week 11-12)
1. **UI/UX Polish**
   - Final styling and branding
   - Animation and transitions
   - Performance optimization
   - Accessibility improvements

2. **Testing & Deployment**
   - Comprehensive testing
   - Performance optimization
   - Production deployment
   - Documentation

## Success Criteria

### Functional Requirements
- [ ] All 7 tabs implemented with full functionality
- [ ] Data loads correctly from all backtest runs
- [ ] All interactive features work properly
- [ ] Export functionality works for all data types
- [ ] Performance meets requirements

### User Experience Requirements
- [ ] Intuitive navigation and layout
- [ ] Fast loading and responsive interactions
- [ ] Professional appearance and branding
- [ ] Full accessibility compliance
- [ ] Mobile-responsive design

### Technical Requirements
- [ ] Scalable React architecture
- [ ] Comprehensive error handling
- [ ] Efficient data processing
- [ ] Type-safe development
- [ ] Comprehensive testing

This React-based dashboard will provide an enterprise-grade, interactive experience for analyzing MoE backtesting results with all the rich features and visualizations you requested. 