import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import axios from 'axios';

// Types
export interface BacktestConfig {
  backtest_id: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  tickers: string[];
  position_sizing: number;
  max_positions: number;
  cash_reserve: number;
  min_cash_reserve: number;
  transaction_cost: number;
  slippage: number;
  created_at: string;
  completed_at?: string;
  total_trading_days?: number;
  status: string;
}

export interface PortfolioDaily {
  date: string;
  total_value: number;
  cash: number;
  positions_value: number;
  daily_return: number;
  cumulative_return: number;
  num_positions: number;
  cash_reserve: number;
  available_capital: number;
}

export interface ExpertContribution {
  weight: number;
  confidence: number;
  probabilities: [number, number, number]; // [buy, hold, sell]
  reasoning: string;
}

export interface TickerDaily {
  date: string;
  price: number;
  decision: 'BUY' | 'HOLD' | 'SELL';
  overall_confidence: number;
  expert_contributions: Record<string, ExpertContribution>;
  final_probabilities: [number, number, number]; // [buy, hold, sell]
  reasoning: string;
  position?: {
    quantity: number;
    avg_price: number;
    current_value: number;
    unrealized_pnl: number;
    status: string;
  };
}

export interface Trade {
  trade_id: string;
  date: string;
  ticker: string;
  action: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  value: number;
  transaction_cost: number;
  slippage: number;
  total_cost: number;
  overall_confidence: number;
  expert_contributions: Record<string, ExpertContribution>;
  reasoning: string;
  success: boolean;
  portfolio_before: {
    total_value: number;
    cash: number;
    positions_value: number;
  };
  portfolio_after: {
    total_value: number;
    cash: number;
    positions_value: number;
  };
}

export interface PortfolioMetrics {
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  max_drawdown: number;
  drawdown_duration: number;
  volatility: number;
  win_rate: number;
  profit_factor: number;
  total_trades: number;
  avg_trade_return: number;
  best_trade: number;
  worst_trade: number;
  avg_hold_time: number;
  cash_drag: number;
  diversification_score: number;
  final_value: number;
}

export interface TickerSummary {
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  volatility: number;
  num_trades: number;
  final_value: number;
  contribution_to_portfolio: number;
}

export interface BacktestResults {
  portfolio_metrics: PortfolioMetrics;
  ticker_summary: Record<string, TickerSummary>;
}

export interface BacktestData {
  config: BacktestConfig;
  portfolio_daily: PortfolioDaily[];
  tickers_daily: Record<string, TickerDaily[]>;
  trades: Trade[];
  results: BacktestResults;
}

export interface BacktestRun {
  id: string;
  start_date: string;
  end_date: string;
  date_range: string;
  tickers: string;
  initial_capital: number;
  created_at: string;
  status: string;
  total_trading_days?: number;
  final_value?: number;
  total_return?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  total_trades?: number;
}

interface DataContextType {
  // State
  availableRuns: BacktestRun[];
  selectedRun: string | null;
  backtestData: BacktestData | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  loadAvailableRuns: () => Promise<void>;
  selectRun: (runId: string) => Promise<void>;
  clearData: () => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const useData = () => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

interface DataProviderProps {
  children: ReactNode;
}

export const DataProvider: React.FC<DataProviderProps> = ({ children }) => {
  const [availableRuns, setAvailableRuns] = useState<BacktestRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<string | null>(null);
  const [backtestData, setBacktestData] = useState<BacktestData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // API base URL - points to our Express server
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

  const loadAvailableRuns = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/api/runs`);
      setAvailableRuns(response.data);
    } catch (err) {
      console.error('Error loading available runs:', err);
      setError('Failed to load available runs');
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);

  const selectRun = useCallback(async (runId: string) => {
    try {
      setLoading(true);
      setError(null);
      setSelectedRun(runId);
      
      // Load the specific run data from API
      const response = await axios.get(`${API_BASE_URL}/api/runs/${runId}`);
      setBacktestData(response.data);
    } catch (err) {
      console.error('Error loading run data:', err);
      setError('Failed to load run data');
      setSelectedRun(null);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);



  const clearData = useCallback(() => {
    setSelectedRun(null);
    setBacktestData(null);
    setError(null);
  }, []);

  // Load available runs on mount
  useEffect(() => {
    loadAvailableRuns();
  }, [loadAvailableRuns]);

  const value: DataContextType = {
    availableRuns,
    selectedRun,
    backtestData,
    loading,
    error,
    loadAvailableRuns,
    selectRun,
    clearData,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
}; 