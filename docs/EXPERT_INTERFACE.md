# Expert Interface and Output Schema

This specification defines stable contracts that both LLM-based and pre-trained (non-LLM) experts must implement. Keeping these interfaces identical ensures fair comparisons and minimal pipeline complexity.

## ExpertInput
- `ticker` (string): Ticker symbol, canonicalized (lowercase internally)
- `date` (string): ISO `YYYY-MM-DD` representing the trading day under evaluation
- `modality_refs` (object): References to modality slices for the day
  - `news` (optional): Array of articles for the day; loader-normalized fields
  - `timeseries` (required): Recent price window ending at `date` (e.g., N prior days)
  - `chart_image_path` (optional): Path to PNG image on disk for `date` or nearest period
  - `fundamentals` (optional): Latest fundamentals snapshot as of `date`

Note: Each expert consumes only its relevant modality; unused fields can be ignored.

## ExpertOutput
- `probabilities` (length-3 list of floats): `[p_buy, p_hold, p_sell]`
  - Must sum to 1 (within numerical tolerance)
- `confidence` (optional float in [0,1]): Expert’s self-estimated reliability for this sample
- `reasoning` (optional string): Brief rationale; free text from LLMs or templated text for non-LLM

## Function Signature (conceptual)
```python
def run_expert(input: ExpertInput, *, model_id: str, seed: int | None = None) -> ExpertOutput:
    ...
```

Implementations must be pure with respect to input arguments (no hidden global state) and deterministic given fixed `seed` and identical inputs.

## Validation Rules
- Probabilities are finite numbers and approximately sum to 1.0
- No NaNs or infinities
- Optional fields may be omitted, but if present must be valid

## Notes for LLM vs Pre-trained
- LLM: Likely to produce `reasoning`; ensure final probabilities are normalized
- Pre-trained: May not produce `reasoning`; set `confidence` based on model calibration if available


