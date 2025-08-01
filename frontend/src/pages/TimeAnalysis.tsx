import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  ToggleButton,
  ToggleButtonGroup,
  Switch,
  FormControlLabel,
  IconButton,
  Tooltip,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Timeline,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  ShowChart,
  Analytics,
  BarChart,
  Download,
  Refresh,
  Assessment,
  CalendarToday,
  Speed,
  Psychology,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  ComposedChart,
  Area,
} from 'recharts';
import { useData } from '../context/DataContext';

const PortfolioAnalysis: React.FC = () => {
  const { selectedRun, backtestData, loading, error } = useData();
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('daily');
  const [selectedMetric, setSelectedMetric] = useState<string>('returns');
  const [showVolatility, setShowVolatility] = useState<boolean>(true);
  const [showConfidence, setShowConfidence] = useState<boolean>(true);
  const [viewMode, setViewMode] = useState<'timeline' | 'heatmap' | 'patterns' | 'correlations'>('timeline');

  // Extract time series data from backtest data
  const timeSeriesData = useMemo(() => {
    if (!backtestData?.portfolio_daily) return [];

    const data = backtestData.portfolio_daily.map((day: any) => ({
      date: day.date,
      portfolioValue: day.total_value || 0,
      dailyReturn: day.daily_return || 0,
      cumulativeReturn: day.cumulative_return || 0,
      volatility: Math.abs(day.daily_return || 0) * 100,
      decision: 'N/A',
      confidence: 0,
      numTrades: day.num_positions || 0,
      cash: day.cash || 0,
      positionsValue: day.positions_value || 0,
    }));

    // Add decision and confidence data from tickers_daily
    if (backtestData.tickers_daily) {
      Object.entries(backtestData.tickers_daily).forEach(([ticker, dailyData]) => {
        dailyData.forEach((day: any) => {
          const portfolioDay = data.find(d => d.date === day.date);
          if (portfolioDay) {
            portfolioDay.decision = day.decision || 'N/A';
            portfolioDay.confidence = day.overall_confidence || 0;
          }
        });
      });
    }

    return data.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [backtestData]);

  // Calculate rolling metrics
  const rollingMetrics = useMemo(() => {
    const window = 30;
    const rollingData = [];

    for (let i = window - 1; i < timeSeriesData.length; i++) {
      const windowData = timeSeriesData.slice(i - window + 1, i + 1);
      const returns = windowData.map(d => d.dailyReturn);
      const avgReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
      const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
      const volatility = Math.sqrt(variance) * Math.sqrt(252);

      rollingData.push({
        date: timeSeriesData[i].date,
        rollingReturn: avgReturn * 252,
        rollingVolatility: volatility * 100,
        sharpeRatio: volatility > 0 ? (avgReturn * 252) / volatility : 0,
        maxDrawdown: Math.min(...returns),
        winRate: returns.filter(r => r > 0).length / returns.length * 100,
      });
    }

    return rollingData;
  }, [timeSeriesData]);

  // Calculate monthly performance
  const monthlyPerformance = useMemo(() => {
    const monthlyData: Record<string, any> = {};
    
    timeSeriesData.forEach(day => {
      const month = new Date(day.date).toISOString().slice(0, 7);
      if (!monthlyData[month]) {
        monthlyData[month] = {
          month,
          totalReturn: 0,
          avgDailyReturn: 0,
          volatility: 0,
          numDays: 0,
          positiveDays: 0,
          negativeDays: 0,
          maxGain: 0,
          maxLoss: 0,
        };
      }
      
      monthlyData[month].totalReturn += day.dailyReturn;
      monthlyData[month].numDays++;
      if (day.dailyReturn > 0) monthlyData[month].positiveDays++;
      if (day.dailyReturn < 0) monthlyData[month].negativeDays++;
      monthlyData[month].maxGain = Math.max(monthlyData[month].maxGain, day.dailyReturn);
      monthlyData[month].maxLoss = Math.min(monthlyData[month].maxLoss, day.dailyReturn);
    });

    return Object.values(monthlyData).map(data => ({
      ...data,
      avgDailyReturn: data.totalReturn / data.numDays,
      volatility: Math.sqrt(data.totalReturn * data.totalReturn / data.numDays) * Math.sqrt(252) * 100,
      winRate: (data.positiveDays / data.numDays) * 100,
    }));
  }, [timeSeriesData]);

  if (!selectedRun) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Timeline color="primary" />
          Time Analysis
        </Typography>
        <Alert severity="info">
          Please select a backtest run to view time analysis.
        </Alert>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px">
        <CircularProgress size={60} sx={{ mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          Loading time analysis...
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

  const getReturnColor = (returnValue: number) => {
    if (returnValue > 0) return 'success';
    if (returnValue < 0) return 'error';
    return 'default';
  };

  const getReturnIcon = (returnValue: number) => {
    if (returnValue > 0) return <TrendingUp />;
    if (returnValue < 0) return <TrendingDown />;
    return <TrendingFlat />;
  };

  return (
    <Box sx={{ width: '100%', maxWidth: '100%', flex: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Timeline color="primary" />
          Time Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive temporal analysis of portfolio performance, patterns, and trends
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3, mb: 4 }}>
        <Card elevation={2}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
              <Box sx={{ p: 1, borderRadius: 1, bgcolor: 'primary.light', color: 'primary.main' }}>
                <CalendarToday />
              </Box>
            </Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              Trading Days
            </Typography>
            <Typography variant="h4" component="div" fontWeight="bold">
              {timeSeriesData.length}
            </Typography>
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
              <Box sx={{ p: 1, borderRadius: 1, bgcolor: 'success.light', color: 'success.main' }}>
                <TrendingUp />
              </Box>
            </Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              Total Return
            </Typography>
            <Typography variant="h4" component="div" fontWeight="bold" color="success.main">
              {((timeSeriesData[timeSeriesData.length - 1]?.cumulativeReturn || 0) * 100).toFixed(2)}%
            </Typography>
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
              <Box sx={{ p: 1, borderRadius: 1, bgcolor: 'warning.light', color: 'warning.main' }}>
                <Speed />
              </Box>
            </Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              Avg Daily Return
            </Typography>
            <Typography variant="h4" component="div" fontWeight="bold" color="warning.main">
              {((timeSeriesData.reduce((sum, day) => sum + day.dailyReturn, 0) / timeSeriesData.length) * 100).toFixed(3)}%
            </Typography>
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
              <Box sx={{ p: 1, borderRadius: 1, bgcolor: 'error.light', color: 'error.main' }}>
                <ShowChart />
              </Box>
            </Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              Volatility (Annual)
            </Typography>
            <Typography variant="h4" component="div" fontWeight="bold" color="error.main">
              {(Math.sqrt(timeSeriesData.reduce((sum, day) => sum + Math.pow(day.dailyReturn, 2), 0) / timeSeriesData.length) * Math.sqrt(252) * 100).toFixed(2)}%
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Controls */}
      <Card elevation={3} sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <Analytics color="primary" />
            <Typography variant="h6">Analysis Controls</Typography>
          </Box>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }, gap: 3, mb: 3 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Timeframe</InputLabel>
              <Select
                value={selectedTimeframe}
                label="Timeframe"
                onChange={(e) => setSelectedTimeframe(e.target.value)}
              >
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
                <MenuItem value="quarterly">Quarterly</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth size="small">
              <InputLabel>Primary Metric</InputLabel>
              <Select
                value={selectedMetric}
                label="Primary Metric"
                onChange={(e) => setSelectedMetric(e.target.value)}
              >
                <MenuItem value="returns">Returns</MenuItem>
                <MenuItem value="volatility">Volatility</MenuItem>
                <MenuItem value="sharpe">Sharpe Ratio</MenuItem>
                <MenuItem value="drawdown">Drawdown</MenuItem>
                <MenuItem value="portfolio">Portfolio Value</MenuItem>
              </Select>
            </FormControl>

            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={(e, newMode) => newMode && setViewMode(newMode)}
              size="small"
            >
              <ToggleButton value="timeline">
                <Tooltip title="Timeline View">
                  <Timeline />
                </Tooltip>
              </ToggleButton>
              <ToggleButton value="heatmap">
                <Tooltip title="Heatmap View">
                  <ShowChart />
                </Tooltip>
              </ToggleButton>
              <ToggleButton value="patterns">
                <Tooltip title="Pattern Analysis">
                  <Analytics />
                </Tooltip>
              </ToggleButton>
              <ToggleButton value="correlations">
                <Tooltip title="Correlation Analysis">
                  <BarChart />
                </Tooltip>
              </ToggleButton>
            </ToggleButtonGroup>

            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={showVolatility}
                    onChange={(e) => setShowVolatility(e.target.checked)}
                  />
                }
                label="Show Volatility"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={showConfidence}
                    onChange={(e) => setShowConfidence(e.target.checked)}
                  />
                }
                label="Show Confidence"
              />
            </Box>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Analyzing {timeSeriesData.length} trading days from {timeSeriesData[0]?.date} to {timeSeriesData[timeSeriesData.length - 1]?.date}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton size="small">
                <Download />
              </IconButton>
              <IconButton size="small">
                <Refresh />
              </IconButton>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Main Analysis Charts */}
      {viewMode === 'timeline' && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 3, mb: 4 }}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <ShowChart color="primary" />
                <Typography variant="h6">Portfolio Performance Timeline</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <RechartsTooltip
                    formatter={(value: number) => [`$${value.toLocaleString()}`, 'Portfolio Value']}
                  />
                  <Line dataKey="portfolioValue" stroke="#1976d2" strokeWidth={2} name="Portfolio Value" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TrendingUp color="primary" />
                <Typography variant="h6">Daily Returns Distribution</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsBarChart data={timeSeriesData.slice(-30)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <RechartsTooltip
                    formatter={(value: number) => [`${(value * 100).toFixed(2)}%`, 'Daily Return']}
                  />
                  <Bar 
                    dataKey="dailyReturn" 
                    fill="#1976d2"
                    name="Daily Return"
                  />
                </RechartsBarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>
      )}

      {viewMode === 'patterns' && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 3, mb: 4 }}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Analytics color="primary" />
                <Typography variant="h6">Rolling Performance Metrics</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={rollingMetrics}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <RechartsTooltip
                    formatter={(value: number, name: string) => [
                      name === 'rollingReturn' ? `${value.toFixed(2)}%` :
                      name === 'rollingVolatility' ? `${value.toFixed(2)}%` :
                      name === 'sharpeRatio' ? value.toFixed(2) :
                      name === 'winRate' ? `${value.toFixed(1)}%` : value,
                      name === 'rollingReturn' ? 'Rolling Return' :
                      name === 'rollingVolatility' ? 'Rolling Volatility' :
                      name === 'sharpeRatio' ? 'Sharpe Ratio' :
                      name === 'winRate' ? 'Win Rate' : name
                    ]}
                  />
                  <Line dataKey="rollingReturn" stroke="#1976d2" strokeWidth={2} name="Rolling Return" />
                  <Line dataKey="rollingVolatility" stroke="#d32f2f" strokeWidth={2} name="Rolling Volatility" />
                  <Line dataKey="sharpeRatio" stroke="#2e7d32" strokeWidth={2} name="Sharpe Ratio" />
                </ComposedChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Psychology color="primary" />
                <Typography variant="h6">Decision Patterns Over Time</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <RechartsTooltip
                    formatter={(value: number, name: string) => [
                      name === 'confidence' ? `${(value * 100).toFixed(1)}%` : value,
                      name === 'confidence' ? 'Confidence' : name
                    ]}
                  />
                  <Bar 
                    dataKey="numTrades" 
                    fill="#1976d2" 
                    name="Number of Trades"
                  />
                  {showConfidence && <Line dataKey="confidence" stroke="#d32f2f" strokeWidth={2} name="Confidence" />}
                </ComposedChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>
      )}

      {viewMode === 'heatmap' && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 3, mb: 4 }}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <ShowChart color="primary" />
                <Typography variant="h6">Monthly Returns Heatmap</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsBarChart data={monthlyPerformance}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <RechartsTooltip
                    formatter={(value: number, name: string) => [
                      name === 'totalReturn' ? `${(value * 100).toFixed(2)}%` : value,
                      name === 'totalReturn' ? 'Monthly Return' : name
                    ]}
                  />
                  <Bar 
                    dataKey="totalReturn" 
                    fill="#1976d2"
                    name="Monthly Return"
                  />
                </RechartsBarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <CalendarToday color="primary" />
                <Typography variant="h6">Day-of-Week Performance</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsBarChart data={(() => {
                  const dayStats: Record<string, any> = {};
                  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
                  
                  days.forEach(day => {
                    dayStats[day] = {
                      day,
                      totalReturn: 0,
                      count: 0,
                      positiveDays: 0,
                      negativeDays: 0,
                    };
                  });

                  timeSeriesData.forEach(day => {
                    const dayOfWeek = new Date(day.date).toLocaleDateString('en-US', { weekday: 'long' });
                    if (dayStats[dayOfWeek]) {
                      dayStats[dayOfWeek].totalReturn += day.dailyReturn;
                      dayStats[dayOfWeek].count++;
                      if (day.dailyReturn > 0) dayStats[dayOfWeek].positiveDays++;
                      if (day.dailyReturn < 0) dayStats[dayOfWeek].negativeDays++;
                    }
                  });

                  return Object.values(dayStats).map(day => ({
                    ...day,
                    avgReturn: day.count > 0 ? (day.totalReturn / day.count) * 100 : 0,
                    winRate: day.count > 0 ? (day.positiveDays / day.count) * 100 : 0,
                  }));
                })()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <RechartsTooltip
                    formatter={(value: number, name: string) => [
                      name === 'avgReturn' ? `${value.toFixed(2)}%` : `${value.toFixed(1)}%`,
                      name === 'avgReturn' ? 'Avg Return' : 'Win Rate'
                    ]}
                  />
                  <Bar dataKey="avgReturn" fill="#1976d2" name="Avg Return" />
                  <Bar dataKey="winRate" fill="#2e7d32" name="Win Rate" />
                </RechartsBarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>
      )}

      {viewMode === 'correlations' && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 3, mb: 4 }}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <BarChart color="primary" />
                <Typography variant="h6">Return vs Volatility Correlation</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <ScatterChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="dailyReturn" 
                    name="Daily Return"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => `${(value * 100).toFixed(1)}%`}
                  />
                  <YAxis 
                    dataKey="volatility" 
                    name="Volatility"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => `${value.toFixed(1)}%`}
                  />
                  <RechartsTooltip
                    formatter={(value: number, name: string) => [
                      name === 'dailyReturn' ? `${(value * 100).toFixed(2)}%` : `${value.toFixed(1)}%`,
                      name === 'dailyReturn' ? 'Daily Return' : 'Volatility'
                    ]}
                  />
                  <Scatter dataKey="dailyReturn" fill="#1976d2" />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <PieChart />
                <Typography variant="h6">Return Distribution</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Positive Days', value: timeSeriesData.filter(d => d.dailyReturn > 0).length },
                      { name: 'Negative Days', value: timeSeriesData.filter(d => d.dailyReturn < 0).length },
                      { name: 'Neutral Days', value: timeSeriesData.filter(d => d.dailyReturn === 0).length },
                    ]}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  >
                    <Cell fill="#2e7d32" />
                    <Cell fill="#d32f2f" />
                    <Cell fill="#ed6c02" />
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Performance Summary Table */}
      <Card elevation={3}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Assessment color="primary" />
            <Typography variant="h6">Performance Summary</Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Metric</TableCell>
                  <TableCell>Value</TableCell>
                  <TableCell>Description</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {/* Profitability Metrics */}
                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableCell colSpan={3}>
                    <Typography variant="subtitle2" fontWeight="bold" color="primary">
                      📈 Profitability Metrics
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Total Return (TR)</TableCell>
                  <TableCell>
                    <Chip
                      icon={getReturnIcon(backtestData?.results?.portfolio_metrics?.total_return || 0)}
                      label={`${((backtestData?.results?.portfolio_metrics?.total_return || 0) * 100).toFixed(2)}%`}
                      color={getReturnColor(backtestData?.results?.portfolio_metrics?.total_return || 0) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>Overall percentage gain/loss over the entire period</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Annualized Return (AR)</TableCell>
                  <TableCell>
                    <Chip
                      label={`${((backtestData?.results?.portfolio_metrics?.annualized_return || 0) * 100).toFixed(2)}%`}
                      color="success"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>Normalized return to yearly rate</TableCell>
                </TableRow>

                {/* Risk-Adjusted Return Metrics */}
                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableCell colSpan={3}>
                    <Typography variant="subtitle2" fontWeight="bold" color="primary">
                      📊 Risk-Adjusted Return Metrics
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Sharpe Ratio (SR)</TableCell>
                  <TableCell>
                    <Chip
                      label={`${(backtestData?.results?.portfolio_metrics?.sharpe_ratio || 0).toFixed(3)}`}
                      color="info"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>Return per unit of overall volatility</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Sortino Ratio (SoR)</TableCell>
                  <TableCell>
                    <Chip
                      label={`${(backtestData?.results?.portfolio_metrics?.sortino_ratio || 0).toFixed(3)}`}
                      color="info"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>Return per unit of downside volatility</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Calmar Ratio (CR)</TableCell>
                  <TableCell>
                    <Chip
                      label={`${(backtestData?.results?.portfolio_metrics?.calmar_ratio || 0).toFixed(3)}`}
                      color="info"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>Return per unit of maximum drawdown</TableCell>
                </TableRow>

                {/* Risk Metrics */}
                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableCell colSpan={3}>
                    <Typography variant="subtitle2" fontWeight="bold" color="primary">
                      ⚠️ Risk Metrics
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Annualized Volatility (AV)</TableCell>
                  <TableCell>
                    <Chip
                      label={`${((backtestData?.results?.portfolio_metrics?.volatility || 0) * 100).toFixed(2)}%`}
                      color="warning"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>Standard deviation of returns, scaled to yearly basis</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Maximum Drawdown (MDD)</TableCell>
                  <TableCell>
                    <Chip
                      label={`${((backtestData?.results?.portfolio_metrics?.max_drawdown || 0) * 100).toFixed(2)}%`}
                      color="error"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>Largest percentage loss from peak to trough</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Drawdown Duration (DD)</TableCell>
                  <TableCell>
                    <Chip
                      label={`${backtestData?.results?.portfolio_metrics?.drawdown_duration || 0} days`}
                      color="error"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>Longest period below previous peak</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Win Rate</TableCell>
                  <TableCell>
                    <Chip
                      label={`${((backtestData?.results?.portfolio_metrics?.win_rate || 0) * 100).toFixed(1)}%`}
                      color="success"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>Percentage of days with positive returns</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PortfolioAnalysis; 