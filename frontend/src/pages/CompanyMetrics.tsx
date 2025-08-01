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
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Business,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  ShowChart,
  Analytics,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from 'recharts';
import { useData } from '../context/DataContext';

const CompanyMetrics: React.FC = () => {
  const { selectedRun, backtestData, loading, error } = useData();
  const [selectedCompany, setSelectedCompany] = useState<string>('all');

  // Extract available companies from data
  const availableCompanies = useMemo(() => {
    if (!backtestData?.results?.ticker_summary) return [];
    return Object.keys(backtestData.results.ticker_summary);
  }, [backtestData]);

  // Extract company data
  const companyData = useMemo(() => {
    if (!backtestData?.results?.ticker_summary || !backtestData?.tickers_daily) return [];

    if (selectedCompany === 'all') {
      return Object.entries(backtestData.results.ticker_summary).map(([ticker, data]: [string, any]) => ({
        ticker,
        ...data,
        dailyData: backtestData.tickers_daily[ticker] || [],
      }));
    } else {
      const data = backtestData.results.ticker_summary[selectedCompany];
      return [{
        ticker: selectedCompany,
        ...data,
        dailyData: backtestData.tickers_daily[selectedCompany] || [],
      }];
    }
  }, [backtestData, selectedCompany]);

  // Create time series data for portfolio contribution over time
  const portfolioContributionData = useMemo(() => {
    if (!backtestData?.tickers_daily || !backtestData?.portfolio_daily) return [];

    const companies = selectedCompany === 'all' ? availableCompanies : [selectedCompany];
    const allData: any[] = [];

    companies.forEach(company => {
      const dailyData = backtestData.tickers_daily[company] || [];
      
      dailyData.forEach((day: any) => {
        // Find corresponding portfolio day
        const portfolioDay = backtestData.portfolio_daily.find((p: any) => p.date === day.date);
        const totalPortfolioValue = portfolioDay?.total_value || 0;
        
        // Get position value from the day's data
        const positionValue = day.position?.current_value || 0;
        
        // Calculate contribution as percentage of total portfolio value
        const contribution = totalPortfolioValue > 0 ? (positionValue / totalPortfolioValue) * 100 : 0;
        
        allData.push({
          date: day.date,
          company: company.toUpperCase(),
          portfolioContribution: contribution,
        });
      });
    });

    return allData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [backtestData, selectedCompany, availableCompanies]);

  // Calculate performance metrics
  const performanceMetrics = useMemo(() => {
    if (!companyData.length) return [];

    return companyData.map(company => {
      const dailyData = company.dailyData || [];
      const priceChanges = dailyData.slice(1).map((day: any, index: number) => {
        const prevDay = dailyData[index];
        return prevDay?.price ? (day.price - prevDay.price) / prevDay.price : 0;
      }).filter((change: number) => !isNaN(change));

      const positiveDays = priceChanges.filter((change: number) => change > 0).length;
      const negativeDays = priceChanges.filter((change: number) => change < 0).length;
      const totalDays = priceChanges.length;

      return {
        ticker: company.ticker,
        totalReturn: company.total_return || 0,
        annualizedReturn: company.annualized_return || 0,
        sharpeRatio: company.sharpe_ratio || 0,
        sortinoRatio: company.sortino_ratio || 0,
        maxDrawdown: company.max_drawdown || 0,
        volatility: company.volatility || 0,
        winRate: company.win_rate || 0,
        numTrades: company.num_trades || 0,
        avgHoldTime: company.avg_hold_time || 0,
        contributionToPortfolio: company.contribution_to_portfolio || 0,
        positiveDays,
        negativeDays,
        totalDays,
        avgWin: company.avg_win || 0,
        avgLoss: company.avg_loss || 0,
        profitFactor: company.profit_factor || 0,
      };
    });
  }, [companyData]);

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

  if (!selectedRun) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Business color="primary" />
          Company Metrics
        </Typography>
        <Alert severity="info">
          Please select a backtest run to view company metrics.
        </Alert>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px">
        <CircularProgress size={60} sx={{ mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          Loading company metrics...
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

  return (
    <Box sx={{ width: '100%', maxWidth: '100%', flex: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Business color="primary" />
          Company Metrics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Individual company performance analysis, risk metrics, and trading patterns
        </Typography>
      </Box>

      {/* Controls */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Select Company</InputLabel>
          <Select
            value={selectedCompany}
            onChange={(e) => setSelectedCompany(e.target.value)}
            label="Select Company"
          >
            <MenuItem value="all">All Companies</MenuItem>
            {availableCompanies.map((company) => (
              <MenuItem key={company} value={company}>
                {company.toUpperCase()}
              </MenuItem>
            ))}
          </Select>
        </FormControl>


      </Box>

      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3, mb: 4 }}>
        {performanceMetrics.map((company) => (
          <Card key={company.ticker} elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                <Typography variant="h6" fontWeight="bold" color="primary">
                  {company.ticker.toUpperCase()}
                </Typography>
                <Chip
                  icon={getReturnIcon(company.totalReturn)}
                  label={`${(company.totalReturn * 100).toFixed(2)}%`}
                  color={getReturnColor(company.totalReturn) as any}
                  size="small"
                />
              </Box>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Return
              </Typography>
              <Typography variant="h4" component="div" fontWeight="bold" color={getReturnColor(company.totalReturn) + '.main'}>
                ${(company.contributionToPortfolio * 1000000).toLocaleString()}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Portfolio Contribution
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Portfolio Contribution Chart */}
      <Card elevation={3} sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <ShowChart color="primary" />
            <Typography variant="h6">Portfolio Contribution Over Time</Typography>
          </Box>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={portfolioContributionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis />
              <RechartsTooltip
                formatter={(value: number, name: string) => [
                  `${value.toFixed(2)}%`,
                  name
                ]}
              />
              {selectedCompany === 'all' ? (
                availableCompanies.map((company, index) => (
                  <Line
                    key={company}
                    dataKey="portfolioContribution"
                    data={portfolioContributionData.filter((d: any) => d.company === company.toUpperCase())}
                    stroke={`hsl(${index * 60}, 70%, 50%)`}
                    strokeWidth={2}
                    name={company.toUpperCase()}
                    dot={false}
                  />
                ))
              ) : (
                <Line
                  dataKey="portfolioContribution"
                  stroke="#1976d2"
                  strokeWidth={2}
                  name={selectedCompany.toUpperCase()}
                  dot={false}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Metrics Table */}
      <Card elevation={3}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Analytics color="primary" />
            <Typography variant="h6">Company Metrics Summary</Typography>
          </Box>
          <TableContainer>
            <Table>
                                <TableHead>
                    <TableRow>
                      <TableCell>Company</TableCell>
                      <TableCell>Total Return</TableCell>
                      <TableCell>Num Trades</TableCell>
                      <TableCell>Portfolio Contribution</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {performanceMetrics.map((company) => (
                      <TableRow key={company.ticker}>
                        <TableCell>
                          <Typography variant="subtitle2" fontWeight="bold">
                            {company.ticker.toUpperCase()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getReturnIcon(company.totalReturn)}
                            label={`${(company.totalReturn * 100).toFixed(2)}%`}
                            color={getReturnColor(company.totalReturn) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={company.numTrades.toString()}
                            color="info"
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${(company.contributionToPortfolio * 100).toFixed(2)}%`}
                            color="primary"
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CompanyMetrics; 