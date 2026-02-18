# IRI 2026 Results Summary

## Paper Results Overview

### Accuracy Comparison

| Metric | Baseline | Enhanced | Change |
|--------|----------|----------|--------|
| Overall Accuracy | 63.64% (14/22) | 86.36% (19/22) | +22.73pp |
| Simple Tier | 75.00% (3/4) | 75.00% (3/4) | No change |
| Medium Tier | 50.00% (4/8) | 75.00% (6/8) | +25pp |
| Complex Tier | 70.00% (7/10) | 100.00% (10/10) | +30pp |

### Latency Analysis

| Component | Time (ms) | % of Total |
|-----------|-----------|-----------|
| LLM Generation | 3,303 | 92.5% |
| Query Execution | 47 | 1.3% |
| Parsing/Validation | 23 | 0.6% |
| Result Serialization | 99 | 2.8% |
| Network | 99 | 2.8% |
| **Total** | **3,571** | **100%** |

### Key Findings

1. **Schema context improves accuracy by 22.73 percentage points** without model fine-tuning
2. **LLM generation dominates deployment overhead** (92.5% of total time)
3. **Medium and complex queries benefit most** from schema context
4. **Three queries remain unfixable** (Q6, Q10, Q14) due to fundamental model limitations
5. **Five queries fixed** by enhanced strategy (Q9, Q11, Q17, Q19, Q21)

## Reproducible Results

All 22 TPC-H queries evaluated with:
- Baseline: Oracle native AI generation with minimal context
- Enhanced: Augmented prompts with schema documentation and domain hints
- Latency: Detailed timing breakdown of all components

Expected execution time: 2-4 hours on modern hardware
Dataset: TPC-H Scale Factor 1 (1GB)
Database: Oracle 23c 23.1.0

## Data Files

### Main Results
- `enhanced_strategy_all_22_queries.csv`: Complete results for all 22 queries

### Supplementary Data (Optional)
- `baseline_results.csv`: Baseline evaluation details
- `latency_breakdown.csv`: Component-level timing data
- `failure_analysis.csv`: Detailed failure modes for unfixed queries

## Output Format

CSV file contains columns:
- query_id: TPC-H query number (1-22)
- query_tier: Complexity level (Simple/Medium/Complex)
- baseline_pass: Baseline semantic success
- enhanced_pass: Enhanced strategy success
- baseline_latency_ms: Baseline query time
- enhanced_latency_ms: Enhanced query time
- improvement_pct: Performance improvement percentage
- llm_time_ms: LLM generation time
- oracle_time_ms: Database execution time
- failure_reason: Explanation if failed
- notes: Additional observations

## How to Use Results

1. **Verify Reproducibility**: Check if your results match expected values
2. **Compare Performance**: Use baseline vs enhanced columns to validate improvements
3. **Analyze Failures**: Review failure_reason column for Q6, Q10, Q14
4. **Understand Latency**: Study latency breakdown for optimization insights

## Citation

If you use these results, please cite:

Mishra, S. (2026). "Evaluating Oracle's Native AI SQL Generation on TPC-H Benchmark: 
Schema Context as Production-Ready Accuracy Lever." IRI 2026 Conference.

## GitHub & Data Sources

**Project Repository:**
https://github.com/sanmish4ds/oracle26ai-eval

**TPC-H Data:**
- Official: http://www.tpc.org/tpch/
- Kaggle: https://www.kaggle.com/search?q=tpc-h

---

For questions about specific results, see setup/REPRODUCIBILITY_CHECKLIST.txt
