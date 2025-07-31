# Analysis Scripts

This folder contains analysis and demonstration scripts for the MoE trading system.

## Purpose

These scripts are designed for:
- **System Analysis:** Understanding how different components work together
- **Performance Monitoring:** Comparing processing times and resource usage
- **Decision Validation:** Analyzing expert outputs and decision conflicts
- **Demonstration:** Showcasing system capabilities
- **Debugging:** Investigating system behavior

## Scripts

### `expert_comparison_analysis.py`
Compares outputs from different experts to show:
- Similarities and differences in decision-making
- Processing time comparisons
- Decision alignment/conflicts
- Integration benefits

**Usage:**
```bash
python analysis/expert_comparison_analysis.py
```

### `fundamental_expert_comparison.py`
Compares the fundamental expert with other experts to show:
- Unique characteristics of fundamental analysis
- Long-term vs short-term perspectives
- Financial health focus vs technical/sentiment analysis
- Integration benefits in the MoE system

**Usage:**
```bash
python analysis/fundamental_expert_comparison.py
```

### `chart_expert_comparison.py`
Compares all four experts (Chart, Sentiment, Technical, and Fundamental) to show:
- Complete Mixture-of-Experts system overview
- Visual pattern analysis vs numerical/text analysis
- Decision diversity across all modalities
- Integration benefits of all four expert types

**Usage:**
```bash
python analysis/chart_expert_comparison.py
```

### `expert_aggregation_demo.py`
Demonstrates the expert aggregation system combining outputs from all four experts:
- Dynamic vs uniform weighting strategies
- Expert contribution analysis
- Decision reasoning and confidence scoring
- Multi-ticker analysis capabilities

**Usage:**
```bash
python analysis/expert_aggregation_demo.py
```

## Note

These are **analysis scripts**, not unit tests. They:
- Take longer to run (due to LLM calls)
- Provide insights rather than pass/fail results
- Are useful for development and debugging
- May need updates as the system evolves

## Future Scripts

Potential additions:
- `performance_benchmark.py` - System performance analysis
- `decision_analysis.py` - Expert decision pattern analysis
- `data_coverage_analysis.py` - Data availability analysis
- `integration_demo.py` - Full system demonstration 