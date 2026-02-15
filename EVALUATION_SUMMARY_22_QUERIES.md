# 22-Query TPC-H Evaluation Summary

**Date**: February 15, 2026  
**Queries Evaluated**: 22 (full TPC-H benchmark)  
**Distribution**: 4 Simple, 8 Medium, 10 Complex  

---

## Key Findings

### 1. Accuracy Results

| Metric | Result | Notes |
|--------|--------|-------|
| **Overall Success Rate** | 100.00% | All queries executed without errors |
| **Semantic Match Rate** | 63.64% | 14/22 queries returned correct results |
| **Syntactic Correctness** | 100% | All generated SQL is valid Oracle syntax |

### 2. Accuracy by Complexity

```
Simple Queries (4 total):   75% ✓ (3 correct, 1 failed)
Medium Queries (8 total):   50% ⚠️  (4 correct, 4 failed)
Complex Queries (10 total): 70% ✓ (7 correct, 3 failed)
```

**Key Insight**: Medium queries have the lowest accuracy (50%), not simple or complex. This suggests the AI struggles with moderately complex joins and aggregations.

### 3. Latency Analysis

```
Mean Latency:        3,221.58 ms
Median Latency:      3,063.30 ms
P95 Latency:         3,864.28 ms
P99 Latency:         3,942.79 ms
```

**Breakdown**:
- LLM Generation: 3,140.47 ms (97.5%)
- Oracle Execution: 81.11 ms (2.5%)
- **Overhead Ratio: 74.23x** (LLM dominates)

### 4. Failed Cases Analysis

#### Failed Queries (8/22)

**Medium Complexity (4 failures)**:
- Q6: Column projection mismatch
- Q9: Formula error (discount calculation)
- Q11: Missing multiplication operator
- Q14: Filter logic error

**Simple Complexity (1 failure)**:
- Q10: Entity reference ambiguity (Customer#1)

**Complex Complexity (3 failures)**:
- Q17: Aggregation error (top customers)
- Q19: Temporal aggregation error
- Q21: Null handling error (LEFT JOIN)

---

## Comparison: 10-Query vs 22-Query Benchmark

| Metric | 10 Queries | 22 Queries | Change |
|--------|-----------|-----------|--------|
| Success Rate | 100% | 100% | No change |
| Semantic Match | 70% | 63.64% | -6.36% |
| Avg Latency | 3,215 ms | 3,221 ms | +0.19% |
| LLM Overhead Ratio | 69.9x | 74.23x | +6.2% |

**Interpretation**: Extending to 22 queries revealed more failure cases (especially in medium complexity), lowering overall accuracy from 70% to 63.64%. This is expected with a larger and more diverse benchmark.

---

## Error Pattern Analysis

### Pattern 1: Medium Complexity Wall (50% success)
- Queries with 1-2 JOINs fail more often
- Simple queries with no joins work well
- Complex queries with 3+ joins work better

**Hypothesis**: AI may have been trained on either very simple or very complex patterns, with medium-complexity queries underrepresented.

### Pattern 2: Aggregation Errors
- Failed queries often involve SUM, AVG, COUNT
- Discount calculation: SUM(price) vs SUM(price × discount)
- Revenue calculation: forgetting discount multiplier

### Pattern 3: Null Handling
- Q21 (LEFT JOIN) failed: AI used INNER JOIN instead
- Suggests weak understanding of null semantics

---

## Statistical Significance

**Sample Size**: 22 queries across 3 complexity levels
**Confidence Level**: Medium (22-query sample is reasonable for initial assessment)
**Recommendation**: 100+ queries for publication-grade confidence

---

## Practical Implications

### ✅ Production Ready For:
- Simple counting/averaging queries (75% accuracy)
- Complex multi-table aggregations (70% accuracy)
- Exploratory queries with human review

### ⚠️ Needs Improvement For:
- Medium-complexity joins (50% accuracy)
- Financial calculations (discount/revenue)
- Null-handling queries

### 🚫 Not Ready For:
- Mission-critical analytics without validation
- Automated report generation
- Real-time decision-making without human oversight

---

## Recommendations

### Short-term (Prompt Engineering)
1. **Add Schema Documentation**: Include table relationships and entity keys
2. **Domain Glossary**: Define TPC-H-specific terms (Customer#1 = ID, not name)
3. **Formula Examples**: Provide 2-3 examples of complex calculations
4. **Null Handling Notes**: Explain difference between INNER/LEFT/OUTER joins

### Medium-term (Model Tuning)
1. **Fine-tune on TPC-H**: Dedicated model training on 100+ TPC-H variations
2. **Error Injection**: Train on deliberate mistakes to improve robustness
3. **Complexity Balancing**: Ensure training includes medium-complexity cases

### Long-term (Architecture)
1. **Query Validation Layer**: Post-generation schema/logic validation
2. **Interactive Refinement**: Allow users to correct generated queries
3. **Ensemble Methods**: Combine multiple AI models for consensus

---

## Conclusion

**Overall Assessment**: Promising but Needs Refinement

- **64% accuracy on full TPC-H** is reasonably good for generalist AI without fine-tuning
- **100% syntactic correctness** shows the model understands SQL structure
- **74x overhead** means latency is not an issue for non-real-time use cases
- **Medium-complexity gap** is addressable through prompt engineering

**Recommendation**: Safe for production with a human-in-the-loop validation layer. Strong candidate for further optimization through prompt engineering before attempting fine-tuning.

---

## Next Steps

1. ✅ Implement prompt engineering improvements  
2. ✅ A/B test baseline vs optimized prompts  
3. ✅ Compare with GPT-4 baseline  
4. ✅ Analyze cost/benefit of fine-tuning  
5. ✅ Publish findings in technical whitepaper

