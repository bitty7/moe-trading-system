# Test Suite

This directory contains all tests for the MoE trading system backend, organized by component.

## Test Structure

```
test/
├── README.md                    # This file
├── run_tests.py                 # Main test runner (runs all tests)
├── core/                        # Core module tests
│   ├── run_core_tests.py       # Core-specific test runner
│   ├── test_phase1.py          # Phase 1 integration tests
│   └── test_logical_validation.py # Logical validation tests
├── data_loader/                 # Data loader tests (future)
├── experts/                     # Expert module tests (future)
├── aggregation/                 # Aggregation tests (future)
├── gating/                      # Gating network tests (future)
├── inference/                   # Inference tests (future)
└── evaluation/                  # Evaluation tests (future)
```

## Running Tests

### Run All Tests
```bash
python test/run_tests.py
```

### Run Core Module Tests Only
```bash
python test/core/run_core_tests.py
```

### Run Individual Tests
```bash
# Core tests
python test/core/test_phase1.py
python test/core/test_logical_validation.py

# Future component tests
python test/data_loader/test_load_prices.py
python test/experts/test_sentiment_expert.py
# etc.
```

## Test Categories

### Core Module Tests (`test/core/`)
- **test_phase1.py**: Phase 1 integration tests
  - Configuration management (`core/config.py`)
  - Date utilities (`core/date_utils.py`)
  - Enumerations (`core/enums.py`)
  - Data types (`core/data_types.py`)
  - Logging system (`core/logging_config.py`)
- **test_logical_validation.py**: Logical validation tests
  - Date logic consistency
  - Configuration parameter validation
  - Data type validation
  - Expert configuration validation
  - Performance parameter validation

### Future Test Categories
- **Data Loader Tests** (`test/data_loader/`): Tests for data loading modules
- **Expert Tests** (`test/experts/`): Tests for expert modules
- **Aggregation Tests** (`test/aggregation/`): Tests for aggregation logic
- **Gating Tests** (`test/gating/`): Tests for gating network
- **Inference Tests** (`test/inference/`): Tests for inference modules
- **Evaluation Tests** (`test/evaluation/`): Tests for evaluation and metrics

## Adding New Tests

1. **Create the appropriate test folder** (if it doesn't exist):
   ```bash
   mkdir test/<component_name>/
   ```

2. **Create a test runner** for the component:
   ```bash
   # Create test/<component_name>/run_<component_name>_tests.py
   ```

3. **Create test files** with the naming convention: `test_<module_name>.py`

4. **Use the logging system** for output instead of print statements

5. **Follow the existing test structure** with proper error handling

6. **Update this README** with the new test description

### Example for Data Loader Tests
```bash
mkdir test/data_loader/
# Create test/data_loader/run_data_loader_tests.py
# Create test/data_loader/test_load_prices.py
# Create test/data_loader/test_load_news.py
# etc.
```

## Test Output

Tests use structured logging with the following format:
```
YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message
```

Example:
```
2025-07-26 06:19:46,169 - test_phase1 - INFO - 🚀 Phase 1 Core Infrastructure Testing
2025-07-26 06:19:46,185 - moe_trading.config - INFO - All required environment variables validated successfully
```

## Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about test progress
- **WARNING**: Warning messages
- **ERROR**: Error messages when tests fail
- **CRITICAL**: Critical errors that prevent testing

## Environment

Tests require the following environment variables (set in `.env`):
- `DATA_PATH`: Path to the dataset
- `LLM_MODEL_NAME`: Name of the LLM model
- `BACKTEST_START_DATE`: Start date for backtesting
- `LOG_LEVEL`: Logging level (default: INFO) 