# MoE Trading System

A sophisticated Mixture of Experts (MoE) trading system that combines multiple AI experts to make trading decisions.

## 🏗️ System Architecture

The system uses four specialized AI experts:
- **Sentiment Expert**: Analyzes news sentiment
- **Technical Expert**: Performs technical analysis on time series data
- **Fundamental Expert**: Analyzes financial statements and ratios
- **Chart Expert**: Analyzes candlestick chart patterns

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install Ollama and models**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull required models
   ollama pull llama3.1:8b
   ```

4. **Run a test backtest**
   ```bash
   python test_backtesting.py
   ```

### EC2 Deployment (GPU Accelerated)

For running full backtests on large datasets, deploy to AWS EC2 with GPU:

1. **Launch EC2 instance**
   - Use `g4dn.xlarge` or `g5.xlarge` for GPU support
   - Ubuntu 22.04 LTS recommended
   - At least 50GB storage

2. **Run setup script**
   ```bash
   chmod +x ec2_setup.sh
   ./ec2_setup.sh
   ```

3. **Run full backtest**
   ```bash
   chmod +x run_full_backtest.sh
   ./run_full_backtest.sh
   ```

## 📊 Performance

### Local Performance
- Processing rate: ~0.14 days/second
- Suitable for testing and development

### EC2 GPU Performance
- Processing rate: ~2-5 days/second (estimated with GPU)
- Suitable for full historical backtests

## 📁 Project Structure

```
src/
├── backend/
│   ├── aggregation/          # Expert aggregation logic
│   ├── analysis/            # Analysis and visualization
│   ├── core/                # Core data types and utilities
│   ├── data_loader/         # Data loading modules
│   ├── evaluation/          # Backtesting and evaluation
│   ├── experts/             # Individual AI experts
│   ├── gating/              # Expert weighting network
│   ├── inference/           # Production inference
│   └── test/                # Test suite
├── dataset/                 # Sample data
├── docs/                    # Documentation
└── frontend/                # Web interface (future)
```

## 🔧 Configuration

### Backtester Configuration

```python
from core.data_types import BacktesterConfig

config = BacktesterConfig(
    start_date="2024-01-01",
    end_date="2024-01-10",
    tickers=["aa", "aaau"],
    initial_capital=100000,
    position_sizing=0.15,
    max_positions=3,
    cash_reserve=0.2,
    min_cash_reserve=0.1,
    transaction_cost=0.001,
    slippage=0.0005,
    log_level="WARNING"
)
```

### Environment Variables

Create a `.env` file:
```env
OLLAMA_HOST=localhost:11434
LOG_LEVEL=WARNING
```

## 📈 Results

The system generates comprehensive logs in the `logs/` directory:

- `config.json`: Backtest configuration
- `portfolio_daily.json`: Daily portfolio metrics
- `tickers_daily.json`: Daily ticker metrics
- `trades.json`: All trade records
- `results.json`: Final results summary

## 🧪 Testing

Run the test suite:
```bash
cd backend
python test/run_tests.py
```

Run individual tests:
```bash
python test_backtesting.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation in `docs/`
2. Review existing issues
3. Create a new issue with detailed information

## 🔮 Roadmap

- [ ] Parallel expert execution
- [ ] Real-time trading integration
- [ ] Web dashboard
- [ ] Additional expert types
- [ ] Advanced risk management 