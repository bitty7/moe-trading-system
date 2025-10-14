# MoE Trading System (Research Edition)

A simple, reproducible Mixture of Experts (MoE) trading system intended for study and comparison. The current focus is to make it work reliably for backtesting so we can compare:

- Local LLM-based experts (via Ollama)
- Future pre-trained, non-LLM models (to be added later)

This repository prioritizes simplicity, clarity, and repeatability over feature completeness. It is designed to support a research/thesis workflow rather than a production MVP.

## 🏗️ System Architecture (Minimum Necessary)

The system uses four specialized experts. Today these are LLM-driven; later equivalents may be implemented using pre-trained non-LLM models for apples-to-apples comparison:
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

3. **Install Ollama and models** (for the LLM-based baseline)
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull required models
   ollama pull llama3.1:8b
   ```

4. **Run a test backtest** (historical, offline)
   ```bash
   python test_backtesting.py
   ```

### EC2 Deployment (Optional)

For larger historical runs, you can deploy to AWS EC2. GPU is optional for the current setup; use if you plan to experiment with heavier models.

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

## 📊 Performance Notes

These figures are indicative only and depend on your hardware and chosen models.

When using GPU-capable models, backtests may accelerate significantly.

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
└── frontend/                # Web interface (optional for visualization)
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

## 📈 Results & Reproducibility

The system writes all results to `backend/logs/` for offline analysis and reproducible comparisons:

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

## 🔬 Study Focus & Comparison Protocol

We aim to compare two approaches on the same backtesting pipeline:

1. LLM-based experts (current implementation)
2. Pre-trained, non-LLM models (future work)

Guidelines for fair comparison:
- Keep data, dates, and portfolio settings identical between runs
- Log experiment metadata (model names, versions, weights) in `config.json`
- Use the same evaluation metrics (see `docs/FINANCIAL_METRICS.md`)
- Store each run in a separate `backend/logs/<run_id>/` directory

See `docs/PERFORMANCE_LOGGING.md` for the exact files produced and `docs/SYSTEM_OVERVIEW.md` for the minimal pipeline description.

Key docs:
- `docs/DATA_DESCRIPTION.md` — Dataset layout, formats, schemas, and loader behavior
- `docs/MODELS_AND_ROUTING.md` — Expert interfaces and aggregation
- `docs/FINANCIAL_METRICS.md` — Metrics used for evaluation and comparison
- `docs/CONFIG_TEMPLATES.md` — Plug-and-play configs for LLM vs pre-trained runs

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

## 🔮 Roadmap (Research-Oriented)

- [ ] Add pre-trained non-LLM expert variants (same interfaces)
- [ ] Simple experiment registry and comparison tables
- [ ] Minimal plots for side-by-side runs
- [ ] Optional parallel expert execution
- [ ] Optional web dashboard for visualization