import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Chip,
  Divider,
  LinearProgress,
  Avatar,
  Stack,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  ShowChart,
  Speed,
  Warning,
  Info,
  Settings,
  Timeline,
  AttachMoney,
  TrendingFlat,
  CheckCircle,
  Schedule,
  Business,
  Analytics,
  Psychology,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useData } from '../context/DataContext';

const Overview: React.FC = () => {
  const { selectedRun, backtestData, loading, error, availableRuns, selectRun } = useData();

  if (!selectedRun) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Welcome to MoE Dashboard
        </Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          Please select a backtest run from the dropdown in the sidebar or header to view the overview.
        </Alert>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Available Runs
          </Typography>
          <Typography color="textSecondary" paragraph>
            The dashboard will automatically load available backtest runs from your logs directory.
          </Typography>
          {availableRuns.length > 0 ? (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Found {availableRuns.length} backtest run(s):
              </Typography>
              <Box sx={{ display: 'grid', gap: 1 }}>
                {availableRuns.map((run) => (
                  <Chip
                    key={run.id}
                    label={`${run.id} (${run.date_range})`}
                    variant="outlined"
                    onClick={() => selectRun(run.id)}
                    sx={{ justifyContent: 'flex-start' }}
                  />
                ))}
              </Box>
            </Box>
          ) : (
            <Typography color="textSecondary">
              No backtest runs found. Please ensure your backend has generated some runs in the logs directory.
            </Typography>
          )}
        </Paper>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px">
        <CircularProgress size={60} sx={{ mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          Loading backtest data...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!backtestData) {
    return (
      <Box>
        <Alert severity="warning">
          No data available for the selected run.
        </Alert>
      </Box>
    );
  }

  const { portfolio_daily, results, config, tickers_daily, trades } = backtestData;
  

  
  // Check if results exist, if not show a message
  if (!results || !results.portfolio_metrics) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TimelineIcon color="primary" />
          Backtest in Progress
        </Typography>
        <Alert severity="info" sx={{ mb: 3 }}>
          This backtest is still running. Results will be available once the backtest completes.
        </Alert>
        
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 3, width: '100%' }}>
          {/* Configuration Card */}
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Settings color="primary" />
                <Typography variant="h6">Configuration</Typography>
              </Box>
              {config && (
                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">Start Date</Typography>
                    <Typography variant="body1" fontWeight="medium">{config.start_date}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">End Date</Typography>
                    <Typography variant="body1" fontWeight="medium">{config.end_date}</Typography>
                  </Box>
                  <Box sx={{ gridColumn: '1 / -1' }}>
                    <Typography variant="body2" color="text.secondary">Tickers</Typography>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                      {config.tickers.map((ticker) => (
                        <Chip key={ticker} label={ticker} size="small" color="primary" variant="outlined" />
                      ))}
                    </Box>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">Initial Capital</Typography>
                    <Typography variant="body1" fontWeight="medium" color="primary.main">
                      ${config.initial_capital.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">Status</Typography>
                    <Chip 
                      label={config.status} 
                      size="small" 
                      color={config.status === 'completed' ? 'success' : 'warning'}
                      variant="outlined"
                    />
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Progress Card */}
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Analytics color="primary" />
                <Typography variant="h6">Progress</Typography>
              </Box>
              
              {portfolio_daily && portfolio_daily.length > 0 ? (
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Data Available
                  </Typography>
                  <Box sx={{ display: 'grid', gap: 1, mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Portfolio Records</Typography>
                      <Typography variant="body2" fontWeight="medium">{portfolio_daily.length} days</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Latest Date</Typography>
                      <Typography variant="body2" fontWeight="medium">{portfolio_daily[portfolio_daily.length - 1]?.date}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Ticker Data</Typography>
                      <Typography variant="body2" fontWeight="medium">{Object.keys(tickers_daily || {}).length} tickers</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Trades</Typography>
                      <Typography variant="body2" fontWeight="medium">{trades?.length || 0} trades</Typography>
                    </Box>
                  </Box>
                  
                  {portfolio_daily.length > 1 && portfolio_daily[portfolio_daily.length - 1]?.total_value && (
                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Current Portfolio Value
                      </Typography>
                      <Typography variant="h5" color="primary.main" fontWeight="bold">
                        ${portfolio_daily[portfolio_daily.length - 1].total_value.toLocaleString()}
                      </Typography>
                    </Box>
                  )}
                </Box>
              ) : (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <CircularProgress size={40} sx={{ mb: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Waiting for portfolio data...
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    );
  }

  // Check if we have portfolio data
  if (!portfolio_daily || portfolio_daily.length === 0) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Warning color="warning" />
          No Portfolio Data Available
        </Typography>
        <Alert severity="warning" sx={{ mb: 3 }}>
          No portfolio daily data is available for this run yet.
        </Alert>
        
        <Card elevation={3}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Settings color="primary" />
              <Typography variant="h6">Configuration</Typography>
            </Box>
            {config && (
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Start Date</Typography>
                  <Typography variant="body1" fontWeight="medium">{config.start_date}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">End Date</Typography>
                  <Typography variant="body1" fontWeight="medium">{config.end_date}</Typography>
                </Box>
                <Box sx={{ gridColumn: '1 / -1' }}>
                  <Typography variant="body2" color="text.secondary">Tickers</Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                    {config.tickers.map((ticker) => (
                      <Chip key={ticker} label={ticker} size="small" color="primary" variant="outlined" />
                    ))}
                  </Box>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Initial Capital</Typography>
                  <Typography variant="body1" fontWeight="medium" color="primary.main">
                    ${config.initial_capital.toLocaleString()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip 
                    label={config.status} 
                    size="small" 
                    color={config.status === 'completed' ? 'success' : 'warning'}
                    variant="outlined"
                  />
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      </Box>
    );
  }

  const { portfolio_metrics } = results;

  // Format portfolio data for charts
  const chartData = portfolio_daily.map((day) => ({
    date: new Date(day.date).toLocaleDateString(),
    value: day.total_value,
    return: day.daily_return * 100,
    cumulative: day.cumulative_return * 100,
    cash: day.cash,
    positions: day.positions_value,
  }));

  // Calculate some additional metrics
  const latestPortfolio = portfolio_daily[portfolio_daily.length - 1];
  const totalReturn = latestPortfolio?.total_value ? 
    ((latestPortfolio.total_value - config.initial_capital) / config.initial_capital) * 100 : 0;
  const isPositive = totalReturn >= 0;

  // Color scheme for charts
  const colors = {
    primary: '#1976d2',
    success: '#2e7d32',
    warning: '#ed6c02',
    error: '#d32f2f',
    secondary: '#9c27b0',
  };

  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    change?: string;
    icon: React.ReactNode;
    color?: 'success' | 'error' | 'warning' | 'info' | 'primary';
    subtitle?: string;
  }> = ({ title, value, change, icon, color = 'info', subtitle }) => (
    <Card elevation={2} sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Box
            sx={{
              p: 1,
              borderRadius: 1,
              bgcolor: `${color}.light`,
              color: `${color}.main`,
            }}
          >
            {icon}
          </Box>
          {change && (
            <Chip
              label={change}
              size="small"
              color={change.startsWith('+') ? 'success' : 'error'}
              variant="outlined"
            />
          )}
        </Box>
        <Typography color="textSecondary" gutterBottom variant="body2">
          {title}
        </Typography>
        <Typography variant="h4" component="div" fontWeight="bold">
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ 
      width: '100%', 
      maxWidth: '100%', 
      flex: 1
    }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AccountBalance color="primary" />
          Portfolio Overview
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive analysis of your backtest performance and configuration
        </Typography>
      </Box>

      {/* Key Metrics Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3, mb: 4, width: '100%' }}>
        <MetricCard
          title="Total Portfolio Value"
          value={`$${portfolio_metrics?.final_value?.toLocaleString() || '0'}`}
          change={`${isPositive ? '+' : ''}${totalReturn.toFixed(2)}%`}
          icon={<AccountBalance />}
          color="success"
          subtitle={`From $${config.initial_capital.toLocaleString()}`}
        />
        <MetricCard
          title="Sharpe Ratio"
          value={portfolio_metrics?.sharpe_ratio?.toFixed(2) || '0.00'}
          icon={<ShowChart />}
          color="primary"
          subtitle="Risk-adjusted return"
        />
        <MetricCard
          title="Max Drawdown"
          value={`${((portfolio_metrics?.max_drawdown || 0) * 100).toFixed(2)}%`}
          icon={<Warning />}
          color="error"
          subtitle={`${portfolio_metrics?.drawdown_duration || 0} days`}
        />
        <MetricCard
          title="Total Trades"
          value={portfolio_metrics?.total_trades || 0}
          icon={<Speed />}
          color="warning"
          subtitle={`${((portfolio_metrics?.win_rate || 0) * 100).toFixed(1)}% win rate`}
        />
      </Box>

      {/* Charts Section */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' }, gap: 3, mb: 4, width: '100%' }}>
        <Card elevation={3}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Timeline color="primary" />
              <Typography variant="h6">Portfolio Value Over Time</Typography>
            </Box>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                />
                <RechartsTooltip
                  formatter={(value: number) => [`$${value.toLocaleString()}`, 'Portfolio Value']}
                  labelFormatter={(label) => `Date: ${label}`}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #ccc',
                    borderRadius: '8px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke={colors.primary}
                  strokeWidth={3}
                  dot={false}
                  activeDot={{ r: 6, stroke: colors.primary, strokeWidth: 2, fill: 'white' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        <Card elevation={3}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <TrendingUp color="primary" />
              <Typography variant="h6">Cumulative Returns</Typography>
            </Box>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `${value.toFixed(1)}%`}
                />
                <RechartsTooltip
                  formatter={(value: number) => [`${value.toFixed(2)}%`, 'Cumulative Return']}
                  labelFormatter={(label) => `Date: ${label}`}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #ccc',
                    borderRadius: '8px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="cumulative"
                  stroke={colors.success}
                  fill={colors.success}
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Box>

      {/* Performance Metrics */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mb: 4, width: '100%' }}>
        <Card elevation={3}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Analytics color="primary" />
              <Typography variant="h6">Performance Metrics</Typography>
            </Box>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">Annualized Return</Typography>
                <Typography variant="h6" color={(portfolio_metrics?.annualized_return || 0) >= 0 ? 'success.main' : 'error.main'}>
                  {((portfolio_metrics?.annualized_return || 0) * 100).toFixed(2)}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Volatility</Typography>
                <Typography variant="h6">
                  {((portfolio_metrics?.volatility || 0) * 100).toFixed(2)}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Win Rate</Typography>
                <Typography variant="h6" color="success.main">
                  {((portfolio_metrics?.win_rate || 0) * 100).toFixed(2)}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Sortino Ratio</Typography>
                <Typography variant="h6">
                  {(portfolio_metrics?.sortino_ratio || 0).toFixed(2)}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Calmar Ratio</Typography>
                <Typography variant="h6">
                  {(portfolio_metrics?.calmar_ratio || 0).toFixed(2)}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Profit Factor</Typography>
                <Typography variant="h6" color={(portfolio_metrics?.profit_factor || 0) >= 1 ? 'success.main' : 'error.main'}>
                  {(portfolio_metrics?.profit_factor || 0).toFixed(2)}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card elevation={3}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Psychology color="primary" />
              <Typography variant="h6">Risk Metrics</Typography>
            </Box>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">Drawdown Duration</Typography>
                <Typography variant="h6">
                  {portfolio_metrics?.drawdown_duration || 0} days
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Avg Trade Return</Typography>
                <Typography variant="h6" color={(portfolio_metrics?.avg_trade_return || 0) >= 0 ? 'success.main' : 'error.main'}>
                  {((portfolio_metrics?.avg_trade_return || 0) * 100).toFixed(2)}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Best Trade</Typography>
                <Typography variant="h6" color="success.main">
                  {((portfolio_metrics?.best_trade || 0) * 100).toFixed(2)}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Worst Trade</Typography>
                <Typography variant="h6" color="error.main">
                  {((portfolio_metrics?.worst_trade || 0) * 100).toFixed(2)}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Avg Hold Time</Typography>
                <Typography variant="h6">
                  {(portfolio_metrics?.avg_hold_time || 0).toFixed(1)} days
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Cash Drag</Typography>
                <Typography variant="h6" color="warning.main">
                  {((portfolio_metrics?.cash_drag || 0) * 100).toFixed(2)}%
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Configuration Details */}
      <Card elevation={3}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <Settings color="primary" />
            <Typography variant="h6">Backtest Configuration</Typography>
          </Box>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, width: '100%' }}>
            <Box>
              <Typography variant="subtitle1" gutterBottom fontWeight="medium">Basic Settings</Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Start Date</Typography>
                  <Typography variant="body1" fontWeight="medium">{config.start_date}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">End Date</Typography>
                  <Typography variant="body1" fontWeight="medium">{config.end_date}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Initial Capital</Typography>
                  <Typography variant="body1" fontWeight="medium" color="primary.main">
                    ${config.initial_capital.toLocaleString()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip 
                    label={config.status} 
                    size="small" 
                    color={config.status === 'completed' ? 'success' : 'warning'}
                    variant="outlined"
                  />
                </Box>
              </Box>
            </Box>
            
            <Box>
              <Typography variant="subtitle1" gutterBottom fontWeight="medium">Trading Parameters</Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Position Sizing</Typography>
                  <Typography variant="body1" fontWeight="medium">{(config.position_sizing * 100).toFixed(1)}%</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Max Positions</Typography>
                  <Typography variant="body1" fontWeight="medium">{config.max_positions}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Cash Reserve</Typography>
                  <Typography variant="body1" fontWeight="medium">{(config.cash_reserve * 100).toFixed(1)}%</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Transaction Cost</Typography>
                  <Typography variant="body1" fontWeight="medium">{(config.transaction_cost * 100).toFixed(3)}%</Typography>
                </Box>
              </Box>
            </Box>
            
            <Box sx={{ gridColumn: '1 / -1' }}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" gutterBottom fontWeight="medium">Tickers</Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {config.tickers.map((ticker) => (
                  <Chip 
                    key={ticker} 
                    label={ticker.toUpperCase()} 
                    color="primary" 
                    variant="outlined"
                    icon={<Business />}
                  />
                ))}
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Overview; 