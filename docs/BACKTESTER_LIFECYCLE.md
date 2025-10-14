# Backtester Lifecycle (Daily Loop)

This describes the minimal deterministic steps executed for each trading day and ticker.

## Daily Steps
1. Load modality slices for `(ticker, date)` using data loaders
2. Build `ExpertInput` and call each expert implementation
3. Validate expert outputs (probabilities finite and normalized)
4. Aggregate with fixed weights → final `decision`
5. Apply sizing/execution rules and update portfolio
6. Log daily ticker entry (expert contributions, decision, probabilities)
7. Log daily portfolio snapshot and trades

## Failure and Degradation
- Missing modality data → mark as missing, skip that expert, renormalize remaining weights (or keep weights and pass neutral `[0,1,0]` HOLD vector, chosen consistently across runs)
- Validation errors → fail fast with explicit message and captured context

## Determinism
- Fixed `seed` for any stochastic components
- Single-threaded execution by default
- No hidden global state; all run parameters captured in `config.json`


