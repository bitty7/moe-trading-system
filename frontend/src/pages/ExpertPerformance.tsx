import React, { useState, useMemo } from 'react';
import {
  Box, Card, CardContent, Typography, Alert, CircularProgress,
  FormControl, InputLabel, Select, MenuItem, Chip, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow,
  Avatar, LinearProgress, Divider
} from '@mui/material';
import {
  Analytics, Psychology, TrendingUp, TrendingDown, TrendingFlat,
  ShowChart, Assessment, Star, StarBorder, CheckCircle, Cancel
} from '@mui/icons-material';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell
} from 'recharts';
import { useData } from '../context/DataContext';

const ExpertPerformance: React.FC = () => {
  const { selectedRun, backtestData, loading, error } = useData();
  const [selectedCompany, setSelectedCompany] = useState<string>('all');

  // Get available companies
  const availableCompanies = useMemo(() => {
    if (!backtestData?.results?.ticker_summary) return [];
    return Object.keys(backtestData.results.ticker_summary);
  }, [backtestData]);

  // Expert names and colors
  const experts = [
    { name: 'sentiment', label: 'Sentiment Expert', color: '#FF6B6B' },
    { name: 'technical', label: 'Technical Expert', color: '#4ECDC4' },
    { name: 'fundamental', label: 'Fundamental Expert', color: '#45B7D1' },
    { name: 'chart', label: 'Chart Expert', color: '#96CEB4' }
  ];

  // Calculate expert performance metrics
  const expertPerformanceData = useMemo(() => {
    if (!backtestData?.tickers_daily) return [];

    const companies = selectedCompany === 'all' ? availableCompanies : [selectedCompany];
    const expertStats: any = {};

    // Initialize expert stats
    experts.forEach(expert => {
      expertStats[expert.name] = {
        name: expert.label,
        totalDecisions: 0,
        avgConfidence: 0,
        avgWeight: 0,
        totalConfidence: 0,
        totalWeight: 0,
        buyDecisions: 0,
        holdDecisions: 0,
        sellDecisions: 0,
        confidenceHistory: [],
        weightHistory: []
      };
    });

    // Process data for each company
    companies.forEach(company => {
      const dailyData = backtestData.tickers_daily[company] || [];
      
      dailyData.forEach((day: any) => {
        const expertContributions = day.expert_contributions || {};
        
        experts.forEach(expert => {
          const contribution = expertContributions[expert.name];
          if (contribution) {
            expertStats[expert.name].totalDecisions++;
            expertStats[expert.name].totalConfidence += contribution.confidence || 0;
            expertStats[expert.name].totalWeight += contribution.weight || 0;
            
            // Track decision probabilities
            const probabilities = contribution.probabilities || [0, 0, 0];
            const maxIndex = probabilities.indexOf(Math.max(...probabilities));
            if (maxIndex === 0) expertStats[expert.name].buyDecisions++;
            else if (maxIndex === 1) expertStats[expert.name].holdDecisions++;
            else if (maxIndex === 2) expertStats[expert.name].sellDecisions++;
            
            // Track history
            expertStats[expert.name].confidenceHistory.push({
              date: day.date,
              company: company.toUpperCase(),
              confidence: contribution.confidence || 0
            });
            
            expertStats[expert.name].weightHistory.push({
              date: day.date,
              company: company.toUpperCase(),
              weight: contribution.weight || 0
            });
          }
        });
      });
    });

    // Calculate averages
    experts.forEach(expert => {
      const stats = expertStats[expert.name];
      if (stats.totalDecisions > 0) {
        stats.avgConfidence = stats.totalConfidence / stats.totalDecisions;
        stats.avgWeight = stats.totalWeight / stats.totalDecisions;
      }
    });

    return Object.values(expertStats);
  }, [backtestData, selectedCompany, availableCompanies, experts]);

  // Create time series data for expert confidence over time
  const expertConfidenceData = useMemo(() => {
    if (!backtestData?.tickers_daily) return [];

    const companies = selectedCompany === 'all' ? availableCompanies : [selectedCompany];
    const allData: any[] = [];

    companies.forEach(company => {
      const dailyData = backtestData.tickers_daily[company] || [];
      
      dailyData.forEach((day: any) => {
        const expertContributions = day.expert_contributions || {};
        const dayData: any = { date: day.date, company: company.toUpperCase() };
        
        experts.forEach(expert => {
          const contribution = expertContributions[expert.name];
          dayData[expert.name] = contribution?.confidence || 0;
        });
        
        allData.push(dayData);
      });
    });

    return allData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [backtestData, selectedCompany, availableCompanies, experts]);

  // Create time series data for expert weights over time
  const expertWeightData = useMemo(() => {
    if (!backtestData?.tickers_daily) return [];

    const companies = selectedCompany === 'all' ? availableCompanies : [selectedCompany];
    const allData: any[] = [];

    companies.forEach(company => {
      const dailyData = backtestData.tickers_daily[company] || [];
      
      dailyData.forEach((day: any) => {
        const expertContributions = day.expert_contributions || {};
        const dayData: any = { date: day.date, company: company.toUpperCase() };
        
        experts.forEach(expert => {
          const contribution = expertContributions[expert.name];
          dayData[expert.name] = contribution?.weight || 0;
        });
        
        allData.push(dayData);
      });
    });

    return allData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [backtestData, selectedCompany, availableCompanies, experts]);

  // Calculate expert ranking
  const expertRanking = useMemo(() => {
    return expertPerformanceData
      .sort((a: any, b: any) => b.avgConfidence - a.avgConfidence)
      .map((expert: any, index: number) => ({
        ...expert,
        rank: index + 1
      }));
  }, [expertPerformanceData]);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return 'success';
    if (confidence >= 0.5) return 'warning';
    return 'error';
  };

  const getWeightColor = (weight: number) => {
    if (weight >= 0.3) return 'success';
    if (weight >= 0.2) return 'warning';
    return 'error';
  };

  if (!selectedRun) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Analytics color="primary" />
          Expert Performance
        </Typography>
        <Alert severity="info">
          Please select a backtest run to view expert performance analysis.
        </Alert>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Analytics color="primary" />
          Expert Performance
        </Typography>
        <Alert severity="error">
          Error loading expert performance data: {error}
        </Alert>
      </Box>
    );
  }

  if (!backtestData) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Analytics color="primary" />
          Expert Performance
        </Typography>
        <Alert severity="warning">
          No backtest data available for analysis.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', maxWidth: '100%', flex: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Analytics color="primary" />
          Expert Performance Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive analysis of expert performance, confidence levels, and decision patterns
        </Typography>
      </Box>

      {/* Controls */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Select Company</InputLabel>
          <Select value={selectedCompany} onChange={(e) => setSelectedCompany(e.target.value)} label="Select Company">
            <MenuItem value="all">All Companies</MenuItem>
            {availableCompanies.map((company) => (
              <MenuItem key={company} value={company}>{company.toUpperCase()}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Expert Performance Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3, mb: 4 }}>
        {expertPerformanceData.map((expert: any) => (
          <Card key={expert.name} elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6" fontWeight="bold" color="primary">
                  {expert.name}
                </Typography>
                <Avatar sx={{ bgcolor: experts.find(e => e.label === expert.name)?.color || 'primary.main' }}>
                  <Psychology />
                </Avatar>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Average Confidence
                </Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  <LinearProgress
                    variant="determinate"
                    value={expert.avgConfidence * 100}
                    sx={{ flex: 1, height: 8, borderRadius: 4 }}
                    color={getConfidenceColor(expert.avgConfidence) as any}
                  />
                  <Typography variant="body2" fontWeight="bold">
                    {(expert.avgConfidence * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Average Weight
                </Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  <LinearProgress
                    variant="determinate"
                    value={expert.avgWeight * 100}
                    sx={{ flex: 1, height: 8, borderRadius: 4 }}
                    color={getWeightColor(expert.avgWeight) as any}
                  />
                  <Typography variant="body2" fontWeight="bold">
                    {(expert.avgWeight * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </Box>

              <Typography variant="body2" color="textSecondary">
                Total Decisions: {expert.totalDecisions}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Expert Confidence Over Time Chart */}
      <Card elevation={3} sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <ShowChart color="primary" />
            <Typography variant="h6">Expert Confidence Over Time</Typography>
          </Box>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={expertConfidenceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
              <RechartsTooltip
                formatter={(value: number, name: string) => [
                  `${(value * 100).toFixed(1)}%`,
                  experts.find(e => e.name === name)?.label || name
                ]}
              />
              {experts.map((expert) => (
                <Line
                  key={expert.name}
                  type="monotone"
                  dataKey={expert.name}
                  stroke={expert.color}
                  strokeWidth={2}
                  name={expert.label}
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Expert Weights Over Time Chart */}
      <Card elevation={3} sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Assessment color="primary" />
            <Typography variant="h6">Expert Weights Over Time</Typography>
          </Box>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={expertWeightData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
              <RechartsTooltip
                formatter={(value: number, name: string) => [
                  `${(value * 100).toFixed(1)}%`,
                  experts.find(e => e.name === name)?.label || name
                ]}
              />
              {experts.map((expert) => (
                <Line
                  key={expert.name}
                  type="monotone"
                  dataKey={expert.name}
                  stroke={expert.color}
                  strokeWidth={2}
                  name={expert.label}
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Expert Decision Distribution */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3, mb: 4 }}>
        {expertPerformanceData.map((expert: any) => (
          <Card key={expert.name} elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Psychology color="primary" />
                {expert.name} Decisions
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Buy', value: expert.buyDecisions, color: '#4CAF50' },
                      { name: 'Hold', value: expert.holdDecisions, color: '#FF9800' },
                      { name: 'Sell', value: expert.sellDecisions, color: '#F44336' }
                    ]}
                    cx="50%"
                    cy="50%"
                    outerRadius={60}
                    dataKey="value"
                  >
                    {[
                      { name: 'Buy', value: expert.buyDecisions, color: '#4CAF50' },
                      { name: 'Hold', value: expert.holdDecisions, color: '#FF9800' },
                      { name: 'Sell', value: expert.sellDecisions, color: '#F44336' }
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip formatter={(value: number) => [value, 'Decisions']} />
                </PieChart>
              </ResponsiveContainer>
              <Box sx={{ mt: 2, textAlign: 'center' }}>
                <Typography variant="body2" color="textSecondary">
                  Total: {expert.totalDecisions}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Expert Ranking Table */}
      <Card elevation={3}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Star color="primary" />
            <Typography variant="h6">Expert Performance Ranking</Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Rank</TableCell>
                  <TableCell>Expert</TableCell>
                  <TableCell>Avg Confidence</TableCell>
                  <TableCell>Avg Weight</TableCell>
                  <TableCell>Total Decisions</TableCell>
                  <TableCell>Decision Distribution</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {expertRanking.map((expert: any) => (
                  <TableRow key={expert.name}>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {expert.rank <= 3 ? (
                          <Star sx={{ color: '#FFD700' }} />
                        ) : (
                          <StarBorder />
                        )}
                        <Typography variant="subtitle2" fontWeight="bold">
                          #{expert.rank}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="subtitle2" fontWeight="bold">
                        {expert.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${(expert.avgConfidence * 100).toFixed(1)}%`}
                        color={getConfidenceColor(expert.avgConfidence) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${(expert.avgWeight * 100).toFixed(1)}%`}
                        color={getWeightColor(expert.avgWeight) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip label={expert.totalDecisions.toString()} color="info" size="small" />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={0.5}>
                        <Chip
                          icon={<TrendingUp />}
                          label={expert.buyDecisions}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                        <Chip
                          icon={<TrendingFlat />}
                          label={expert.holdDecisions}
                          size="small"
                          color="warning"
                          variant="outlined"
                        />
                        <Chip
                          icon={<TrendingDown />}
                          label={expert.sellDecisions}
                          size="small"
                          color="error"
                          variant="outlined"
                        />
                      </Box>
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

export default ExpertPerformance; 