# AI SQL Failure Scenarios - Detailed Comparison Matrix

## Overview

We identify two distinct failure scenarios:

| Scenario | Definition | Query Count | Fix Difficulty | Example |
|----------|------------|-------------|-----------------|---------|
| **Scenario 1: SQL Exception** | AI-generated SQL throws an Oracle error code | 3 (Q6, Q10, Q21) | Medium | ORA-00933, ORA-00904 |
| **Scenario 2: Semantic Mismatch** | AI SQL executes but returns wrong results | 1 (Q17) | Hard | 5 rows but wrong ranking |

---

## Detailed Scenario Breakdown

### Scenario 1: SQL Exception (3 Queries)

When the AI-generated SQL throws an Oracle error. These are easier to diagnose but block execution.


#### Q6: Show top 5 most expensive orders
**Pattern:** ROWNUM + Nested SELECT * | **Complexity:** Medium

| Aspect | Details |
|--------|---------|
| Ground Truth | SUCCESS (5 rows) |
| AI Generated | ERROR: ORA-00933 (Invalid syntax) |
| Root Cause | Missing nested subquery structure |
| Error Type | **Exception-based (Immediate failure)** |

**Pattern Analysis:**
- Expected patterns: ROWNUM, NESTED_SELECT, ORDER_BY, SELECT_STAR
- Generated patterns: ORDER_BY, SELECT_STAR
- Missing patterns: NESTED_SELECT, ROWNUM

**Fix Confidence:** 70% | **Effort:** Low

---

#### Q10: Find orders placed by Customer#1
**Pattern:** Entity Reference Disambiguation | **Complexity:** Medium

| Aspect | Details |
|--------|---------|
| Ground Truth | SUCCESS (6 rows) |
| AI Generated | ERROR: ORA-00904 (Invalid column) |
| Root Cause | Wrong entity key (C_CUSTKEY vs O_CUSTKEY) |
| Error Type | **Exception-based (Immediate failure)** |

**Pattern Analysis:**
- Expected patterns: WHERE, SIMPLE_FILTER, ENTITY_REF
- Generated patterns: WHERE, WRONG_ENTITY
- Missing patterns: ENTITY_REF, SIMPLE_FILTER

**Fix Confidence:** 60% | **Effort:** Medium

---

#### Q21: Find customers with no orders in 1996
**Pattern:** NOT EXISTS + Correlated Subquery + Date Extraction | **Complexity:** Complex

| Aspect | Details |
|--------|---------|
| Ground Truth | SUCCESS (87 rows) |
| AI Generated | ERROR: ORA-00907 (Missing parenthesis) |
| Root Cause | Broken correlated subquery syntax |
| Error Type | **Exception-based (Immediate failure)** |

**Pattern Analysis:**
- Expected patterns: NOT_EXISTS, CORRELATED_SUBQUERY, EXTRACT, DATE_FILTER
- Generated patterns: NOT_EXISTS
- Missing patterns: DATE_FILTER, EXTRACT, CORRELATED_SUBQUERY

**Fix Confidence:** 80% | **Effort:** Low

---

### Scenario 2: Semantic Mismatch (1 Query)

When AI-generated SQL executes without error but returns wrong/incomplete results.


#### Q17: Find top 5 customers by total spending
**Pattern:** JOIN + GROUP BY + Aggregation + FETCH | **Complexity:** Complex

| Aspect | Details |
|--------|---------|
| Ground Truth | SUCCESS (5 rows) |
| AI Generated | SUCCESS (5 rows, wrong values) |
| Root Cause | Missing JOIN or wrong aggregation |
| Error Type | **Logic-based (Returns wrong data)** |

**Pattern Analysis:**
- Expected patterns: JOIN, GROUP_BY, AGGREGATION, FETCH_FIRST, ORDER_BY
- Generated patterns: GROUP_BY, ORDER_BY
- Missing patterns: AGGREGATION, JOIN, FETCH_FIRST

**Fix Confidence:** 75% | **Effort:** Medium

---
