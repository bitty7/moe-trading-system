# Config Templates (Plug-and-Play)

Two ready-to-use config templates are provided in the `backend/` directory for quick comparison runs.

## 1. LLM Baseline: `backend/config_llm.json`
- All experts use `impl: "llm"` with `llama3.1:8b` via Ollama
- Identical dates, tickers, portfolio settings, and weights for fair comparison
- Use this to establish the LLM baseline

## 2. Pre-trained Baseline: `backend/config_pretrained.json`
- All experts use `impl: "pretrained"` with custom model paths
- Identical settings to `config_llm.json` except expert implementation
- Update the `model` paths to point to your trained model files

## Quick Start

### Run LLM Baseline
```bash
cd backend
python run_backtest.py --config config_llm.json
```

### Run Pre-trained Baseline
```bash
cd backend
python run_backtest.py --config config_pretrained.json
```

### Compare Results
```bash
python compare_runs.py \
  --run1 logs/backtest_llm_20240101_20240131/results.json \
  --run2 logs/backtest_pretrained_20240101_20240131/results.json
```

## Customization

To modify for your study:
1. Adjust `start_date`, `end_date`, and `tickers` (keep identical across both configs)
2. Update `seed` if testing sensitivity
3. Change `model` identifiers to your specific LLM or pre-trained model paths
4. Keep `weights`, `portfolio`, and `execution` settings constant for fair comparison
5. Update `run_id` to meaningful names for your experiments

## Notes
- Both configs use the same `seed`, `weights`, and transaction assumptions
- Model identifiers are saved in `logs/<run_id>/config.json` for reproducibility
- See `COMPARISON_GUIDE.md` for full comparison workflow

