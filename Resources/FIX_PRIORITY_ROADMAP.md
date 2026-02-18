# Fix Priority Roadmap

Based on estimated confidence and effort:

## Priority Order


### Priority 1: Q21 - Find customers with no orders in 1996

| Metric | Value |
|--------|-------|
| Pattern | NOT EXISTS + Correlated Subquery + Date Extraction |
| Scenario | EXCEPTION |
| Fix Confidence | 80% |
| Effort | Low |
| Priority Score | 0.72 |
| Root Cause | Broken correlated subquery syntax |

**What's Needed:**

- Add explicit example for: DATE_FILTER, EXTRACT, CORRELATED_SUBQUERY
- Include in schema context: ✓ Syntax example ✓ Pattern explanation
- Verify with test query

### Priority 2: Q6 - Show top 5 most expensive orders

| Metric | Value |
|--------|-------|
| Pattern | ROWNUM + Nested SELECT * |
| Scenario | EXCEPTION |
| Fix Confidence | 70% |
| Effort | Low |
| Priority Score | 0.63 |
| Root Cause | Missing nested subquery structure |

**What's Needed:**

- Add explicit example for: NESTED_SELECT, ROWNUM
- Include in schema context: ✓ Syntax example ✓ Pattern explanation
- Verify with test query

### Priority 3: Q17 - Find top 5 customers by total spending

| Metric | Value |
|--------|-------|
| Pattern | JOIN + GROUP BY + Aggregation + FETCH |
| Scenario | SEMANTIC_MISMATCH |
| Fix Confidence | 75% |
| Effort | Medium |
| Priority Score | 0.52 |
| Root Cause | Missing JOIN or wrong aggregation |

**What's Needed:**

- Fix multi-pattern combination: AGGREGATION, JOIN, FETCH_FIRST
- Add comprehensive example showing all patterns working together
- Test with actual Oracle database

### Priority 4: Q10 - Find orders placed by Customer#1

| Metric | Value |
|--------|-------|
| Pattern | Entity Reference Disambiguation |
| Scenario | EXCEPTION |
| Fix Confidence | 60% |
| Effort | Medium |
| Priority Score | 0.42 |
| Root Cause | Wrong entity key (C_CUSTKEY vs O_CUSTKEY) |

**What's Needed:**

- Add explicit example for: ENTITY_REF, SIMPLE_FILTER
- Include in schema context: ✓ Syntax example ✓ Pattern explanation
- Verify with test query
