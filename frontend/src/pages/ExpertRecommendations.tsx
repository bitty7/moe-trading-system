import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Avatar,
  LinearProgress,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Psychology,
  Business,
  Schedule,
  Star,
  Assessment,
  Timeline,
  Analytics,
  CheckCircle,
  Cancel,
  Help,
  ShowChart
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area
} from 'recharts';
import { useData } from '../context/DataContext';

const ExpertRecommendations: React.FC = () => {
  const { selectedRun, backtestData, loading, error } = useData();
  const [selectedExpert, setSelectedExpert] = useState<string>('all');
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

  // Calculate recommendation patterns over time
  const recommendationPatterns = useMemo(() => {
    if (!backtestData?.tickers_daily) return [];

    const companies = selectedCompany === 'all' ? availableCompanies : [selectedCompany];
    const allData: any[] = [];

    companies.forEach(company => {
      const dailyData = backtestData.tickers_daily[company] || [];
      
      dailyData.forEach((day: any) => {
        const expertContributions = day.expert_contributions || {};
        const dayData: any = { 
          date: day.date, 
          company: company.toUpperCase(),
          final_decision: day.decision || 'hold',
          overall_confidence: day.overall_confidence || 0
        };
        
                 // Add individual expert recommendations
         experts.forEach(expert => {
           const contribution = expertContributions[expert.name];
           if (contribution) {
             const probabilities = contribution.probabilities || [0, 0, 0];
             const maxIndex = probabilities.indexOf(Math.max(...probabilities));
             const recommendation = maxIndex === 0 ? 'buy' : maxIndex === 1 ? 'hold' : 'sell';
             
             dayData[`${expert.name}_recommendation`] = recommendation;
             dayData[`${expert.name}_confidence`] = contribution.confidence || 0;
             dayData[`${expert.name}_buy_prob`] = probabilities[0] || 0;
             dayData[`${expert.name}_hold_prob`] = probabilities[1] || 0;
             dayData[`${expert.name}_sell_prob`] = probabilities[2] || 0;
             
             // Calculate agreement with final decision
             const finalDecision = dayData.final_decision;
             const agreement = recommendation === finalDecision ? 1 : 0;
             dayData[`${expert.name}_agreement`] = agreement;
           }
         });
        
        allData.push(dayData);
      });
    });

    return allData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [backtestData, selectedCompany, availableCompanies, experts]);

  // Calculate recommendation statistics
  const recommendationStats = useMemo(() => {
    if (!backtestData?.tickers_daily) return {};

    const companies = selectedCompany === 'all' ? availableCompanies : [selectedCompany];
    const stats: any = {};

    // Initialize stats for each expert
    experts.forEach(expert => {
      stats[expert.name] = {
        name: expert.label,
        totalRecommendations: 0,
        buyRecommendations: 0,
        holdRecommendations: 0,
        sellRecommendations: 0,
        avgConfidence: 0,
        totalConfidence: 0,
        avgBuyProb: 0,
        avgHoldProb: 0,
        avgSellProb: 0,
        totalBuyProb: 0,
        totalHoldProb: 0,
        totalSellProb: 0
      };
    });

    // Process data
    companies.forEach(company => {
      const dailyData = backtestData.tickers_daily[company] || [];
      
      dailyData.forEach((day: any) => {
        const expertContributions = day.expert_contributions || {};
        
                 experts.forEach(expert => {
           const contribution = expertContributions[expert.name];
           if (contribution) {
             const expertStats = stats[expert.name];
             expertStats.totalRecommendations++;
             expertStats.totalConfidence += contribution.confidence || 0;
             
             const probabilities = contribution.probabilities || [0, 0, 0];
             expertStats.totalBuyProb += probabilities[0] || 0;
             expertStats.totalHoldProb += probabilities[1] || 0;
             expertStats.totalSellProb += probabilities[2] || 0;
             
             const maxIndex = probabilities.indexOf(Math.max(...probabilities));
             if (maxIndex === 0) expertStats.buyRecommendations++;
             else if (maxIndex === 1) expertStats.holdRecommendations++;
             else if (maxIndex === 2) expertStats.sellRecommendations++;
           }
         });
      });
    });

    // Calculate averages
    experts.forEach(expert => {
      const stat = stats[expert.name];
      if (stat.totalRecommendations > 0) {
        stat.avgConfidence = stat.totalConfidence / stat.totalRecommendations;
        stat.avgBuyProb = stat.totalBuyProb / stat.totalRecommendations;
        stat.avgHoldProb = stat.totalHoldProb / stat.totalRecommendations;
        stat.avgSellProb = stat.totalSellProb / stat.totalRecommendations;
      }
    });

    return stats;
  }, [backtestData, selectedCompany, availableCompanies, experts]);





  const getRecommendationColor = (recommendation: string) => {
    if (recommendation === 'buy') return 'success';
    if (recommendation === 'sell') return 'error';
    return 'warning';
  };

  const getRecommendationIcon = (recommendation: string) => {
    if (recommendation === 'buy') return <TrendingUp />;
    if (recommendation === 'sell') return <TrendingDown />;
    return <TrendingFlat />;
  };

  if (!selectedRun) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Psychology color="primary" />
          Expert Recommendations
        </Typography>
        <Alert severity="info">
          Please select a backtest run to view expert recommendations analysis.
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
          <Psychology color="primary" />
          Expert Recommendations
        </Typography>
        <Alert severity="error">
          Error loading expert recommendations data: {error}
        </Alert>
      </Box>
    );
  }

  if (!backtestData) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Psychology color="primary" />
          Expert Recommendations
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
          <Psychology color="primary" />
          Expert Recommendations Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Analysis of expert recommendations, decision patterns, and recommendation accuracy
        </Typography>
      </Box>

      {/* Controls */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Select Expert</InputLabel>
          <Select value={selectedExpert} onChange={(e) => setSelectedExpert(e.target.value)} label="Select Expert">
            <MenuItem value="all">All Experts</MenuItem>
            {experts.map((expert) => (
              <MenuItem key={expert.name} value={expert.name}>{expert.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
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

      {/* Recommendation Statistics Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3, mb: 4 }}>
        {Object.values(recommendationStats).map((expert: any) => (
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
                  Total Recommendations
                </Typography>
                <Typography variant="h4" fontWeight="bold">
                  {expert.totalRecommendations}
                </Typography>
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
                    color={expert.avgConfidence >= 0.7 ? 'success' : expert.avgConfidence >= 0.5 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" fontWeight="bold">
                    {(expert.avgConfidence * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </Box>

              <Box display="flex" gap={1}>
                <Chip
                  icon={<TrendingUp />}
                  label={`${expert.buyRecommendations}`}
                  size="small"
                  color="success"
                  variant="outlined"
                />
                <Chip
                  icon={<TrendingFlat />}
                  label={`${expert.holdRecommendations}`}
                  size="small"
                  color="warning"
                  variant="outlined"
                />
                <Chip
                  icon={<TrendingDown />}
                  label={`${expert.sellRecommendations}`}
                  size="small"
                  color="error"
                  variant="outlined"
                />
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Decision Change Analysis */}
      <Card elevation={3} sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Timeline color="primary" />
            <Typography variant="h6">Decision Change Analysis</Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Expert</TableCell>
                  <TableCell>Decision Consistency</TableCell>
                  <TableCell>Agreement with Final</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                                 {Object.values(recommendationStats).map((expert: any) => {
                   // Calculate consistency
                   const expertName = experts.find(e => e.label === expert.name)?.name;
                   const expertDecisions = recommendationPatterns
                     .filter((day: any) => day[`${expertName}_recommendation`])
                     .map((day: any) => day[`${expertName}_recommendation`]);
                   
                   // Find most common decision and calculate consistency
                   const decisionCounts = expertDecisions.reduce((acc: any, decision: string) => {
                     acc[decision] = (acc[decision] || 0) + 1;
                     return acc;
                   }, {});
                   const mostCommonDecision = Object.keys(decisionCounts).reduce((a, b) => 
                     decisionCounts[a] > decisionCounts[b] ? a : b
                   );
                   
                   // Calculate consistency (how often they stick to their most common decision)
                   const consistency = expertDecisions.length > 0 
                     ? (decisionCounts[mostCommonDecision] / expertDecisions.length) * 100 
                     : 0;
                  
                  // Calculate agreement with final decisions
                  const agreementData = recommendationPatterns.filter((day: any) => 
                    day[`${expertName}_agreement`] === 1
                  );
                  const agreementRate = expertDecisions.length > 0 
                    ? (agreementData.length / expertDecisions.length) * 100 
                    : 0;
                  
                                     return (
                     <TableRow key={expert.name}>
                       <TableCell>
                         <Typography variant="subtitle2" fontWeight="bold">
                           {expert.name}
                         </Typography>
                       </TableCell>
                       <TableCell>
                         <Box display="flex" alignItems="center" gap={1}>
                           <LinearProgress
                             variant="determinate"
                             value={consistency}
                             sx={{ flex: 1, height: 8, borderRadius: 4 }}
                             color={consistency >= 70 ? 'success' : consistency >= 50 ? 'warning' : 'error'}
                           />
                           <Typography variant="body2" fontWeight="bold">
                             {consistency.toFixed(1)}%
                           </Typography>
                         </Box>
                       </TableCell>
                       <TableCell>
                         <Chip
                           label={`${agreementRate.toFixed(1)}%`}
                           color={agreementRate >= 70 ? 'success' : agreementRate >= 50 ? 'warning' : 'error'}
                           size="small"
                         />
                       </TableCell>
                     </TableRow>
                   );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Expert Agreement with Final Decisions */}
      <Card elevation={3} sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Assessment color="primary" />
            <Typography variant="h6">Expert Agreement with Final Decisions</Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Expert</TableCell>
                  <TableCell>Total Recommendations</TableCell>
                  <TableCell>Agreed with Final Decision</TableCell>
                  <TableCell>Agreement Rate</TableCell>
                  <TableCell>Performance</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.values(recommendationStats).map((expert: any) => {
                  // Calculate agreement rate
                  const agreementData = recommendationPatterns.filter((day: any) => 
                    day[`${experts.find(e => e.label === expert.name)?.name}_agreement`] === 1
                  );
                  const agreementRate = expert.totalRecommendations > 0 
                    ? (agreementData.length / expert.totalRecommendations) * 100 
                    : 0;
                  
                  return (
                    <TableRow key={expert.name}>
                      <TableCell>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {expert.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={expert.totalRecommendations.toString()} color="info" size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip label={agreementData.length.toString()} color="success" size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${agreementRate.toFixed(1)}%`}
                          color={agreementRate >= 70 ? 'success' : agreementRate >= 50 ? 'warning' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <LinearProgress
                            variant="determinate"
                            value={agreementRate}
                            sx={{ flex: 1, height: 8, borderRadius: 4 }}
                            color={agreementRate >= 70 ? 'success' : agreementRate >= 50 ? 'warning' : 'error'}
                          />
                          <Typography variant="body2" fontWeight="bold">
                            {agreementRate.toFixed(1)}%
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      

      {/* Company Trading Activity */}
      <Card elevation={3}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Business color="primary" />
            <Typography variant="h6">Company Trading Activity & Performance</Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Company</TableCell>
                  <TableCell>Trading Days</TableCell>
                  <TableCell>Buy Decisions</TableCell>
                  <TableCell>Hold Decisions</TableCell>
                  <TableCell>Sell Decisions</TableCell>
                  <TableCell>Portfolio Contribution</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {availableCompanies.map((company) => {
                  const companyData = recommendationPatterns.filter((day: any) => day.company === company.toUpperCase());
                  const buyDecisions = companyData.filter((day: any) => day.final_decision === 'buy').length;
                  const holdDecisions = companyData.filter((day: any) => day.final_decision === 'hold').length;
                  const sellDecisions = companyData.filter((day: any) => day.final_decision === 'sell').length;
                  const totalDays = companyData.length;
                  
                  // Get portfolio contribution from results
                  const companySummary = backtestData?.results?.ticker_summary?.[company];
                  const portfolioContribution = companySummary?.contribution_to_portfolio || 0;
                  
                  return (
                    <TableRow key={company}>
                      <TableCell>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {company.toUpperCase()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={totalDays.toString()} color="info" size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          icon={<TrendingUp />}
                          label={buyDecisions.toString()} 
                          color="success" 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          icon={<TrendingFlat />}
                          label={holdDecisions.toString()} 
                          color="warning" 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          icon={<TrendingDown />}
                          label={sellDecisions.toString()} 
                          color="error" 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${(portfolioContribution * 100).toFixed(2)}%`}
                          color={portfolioContribution > 0.1 ? 'success' : portfolioContribution > 0.05 ? 'warning' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ExpertRecommendations; 