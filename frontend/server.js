const express = require('express');
const path = require('path');
const fs = require('fs').promises;
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

// Enable CORS
app.use(cors());

// Serve static files from the React build
app.use(express.static(path.join(__dirname, 'build')));

// API endpoint to get available runs
app.get('/api/runs', async (req, res) => {
  try {
    const logsPath = path.join(__dirname, '..', 'backend', 'logs');
    const directories = await fs.readdir(logsPath);
    
    const runs = [];
    
    for (const dir of directories) {
      if (dir.startsWith('backtest_')) {
        const configPath = path.join(logsPath, dir, 'config.json');
        try {
          const configData = await fs.readFile(configPath, 'utf8');
          const config = JSON.parse(configData);
          
          // Try to read results.json to get final metrics
          let finalValue, totalReturn, sharpeRatio, maxDrawdown, totalTrades;
          try {
            const resultsPath = path.join(logsPath, dir, 'results.json');
            const resultsData = await fs.readFile(resultsPath, 'utf8');
            const results = JSON.parse(resultsData);
            finalValue = results.portfolio_metrics.final_value;
            totalReturn = results.portfolio_metrics.total_return;
            sharpeRatio = results.portfolio_metrics.sharpe_ratio;
            maxDrawdown = results.portfolio_metrics.max_drawdown;
            totalTrades = results.portfolio_metrics.total_trades;
          } catch (error) {
            // results.json might not exist yet - this is normal for running backtests
            // Silently ignore file not found errors
          }
          
          runs.push({
            id: config.backtest_id,
            start_date: config.start_date,
            end_date: config.end_date,
            date_range: `${config.start_date} to ${config.end_date}`,
            tickers: config.tickers.join(', '),
            initial_capital: config.initial_capital,
            created_at: config.created_at,
            status: config.status,
            total_trading_days: config.total_trading_days,
            final_value: finalValue,
            total_return: totalReturn,
            sharpe_ratio: sharpeRatio,
            max_drawdown: maxDrawdown,
            total_trades: totalTrades
          });
        } catch (error) {
          console.error(`Error reading config for ${dir}:`, error);
        }
      }
    }
    
    res.json(runs);
  } catch (error) {
    console.error('Error loading runs:', error);
    res.status(500).json({ error: 'Failed to load runs' });
  }
});

// API endpoint to get specific run data
app.get('/api/runs/*', async (req, res) => {
  try {
    const runId = req.params[0]; // Get the full path after /api/runs/
    const runPath = path.join(__dirname, '..', 'backend', 'logs', runId);
    
    // Check if run directory exists
    try {
      await fs.access(runPath);
    } catch (error) {
      return res.status(404).json({ error: 'Run not found' });
    }
    
    // Load all JSON files
    const configPath = path.join(runPath, 'config.json');
    const portfolioPath = path.join(runPath, 'portfolio_daily.json');
    const tickersPath = path.join(runPath, 'tickers_daily.json');
    const tradesPath = path.join(runPath, 'trades.json');
    const resultsPath = path.join(runPath, 'results.json');
    
    const [configData, portfolioData, tickersData, tradesData, resultsData] = await Promise.allSettled([
      fs.readFile(configPath, 'utf8'),
      fs.readFile(portfolioPath, 'utf8'),
      fs.readFile(tickersPath, 'utf8'),
      fs.readFile(tradesPath, 'utf8'),
      fs.readFile(resultsPath, 'utf8')
    ]);
    
    // Log which files are available for debugging (only if some files are missing)
    const availableFiles = [];
    if (configData.status === 'fulfilled') availableFiles.push('config.json');
    if (portfolioData.status === 'fulfilled') availableFiles.push('portfolio_daily.json');
    if (tickersData.status === 'fulfilled') availableFiles.push('tickers_daily.json');
    if (tradesData.status === 'fulfilled') availableFiles.push('trades.json');
    if (resultsData.status === 'fulfilled') availableFiles.push('results.json');
    
    if (availableFiles.length < 5) {
      console.log(`Run ${runId} - Available files: ${availableFiles.join(', ')}`);
    }
    
    const backtestData = {
      config: configData.status === 'fulfilled' ? JSON.parse(configData.value) : null,
      portfolio_daily: portfolioData.status === 'fulfilled' ? JSON.parse(portfolioData.value) : [],
      tickers_daily: tickersData.status === 'fulfilled' ? JSON.parse(tickersData.value) : {},
      trades: tradesData.status === 'fulfilled' ? JSON.parse(tradesData.value) : [],
      results: resultsData.status === 'fulfilled' ? JSON.parse(resultsData.value) : null
    };
    
    res.json(backtestData);
  } catch (error) {
    console.error('Error loading run data:', error);
    res.status(500).json({ error: 'Failed to load run data' });
  }
});

// Serve React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`API available at http://localhost:${PORT}/api`);
}); 