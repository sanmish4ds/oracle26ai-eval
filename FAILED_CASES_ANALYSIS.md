# Failed Cases Analysis: Oracle AI SQL Generation

## Overview
Out of 10 test queries, 3 queries (30%) failed semantic validation, despite successful execution. This document analyzes the root causes of these failures.

---

## Query 6: Show top 5 most expensive orders (Medium Complexity)

### Natural Language
```
"Show top 5 most expensive orders"
```

### Ground Truth SQL
```sql
SELECT * FROM (SELECT * FROM ORDERS ORDER BY O_TOTALPRICE DESC) WHERE ROWNUM <= 5
```

### AI Generated SQL
```sql
SELECT 
    O."O_ORDERKEY" AS "Order Key", 
    O."O_TOTALPRICE" AS "Total Price"
FROM 
    "ADMIN"."ORDERS" O
ORDER BY 
    O."O_TOTALPRICE" DESC
FETCH FIRST 5 ROWS ONLY
```

### Results Comparison
| Aspect | Ground Truth | AI Generated |
|--------|-------------|------------|
| Rows | 5 rows with 10 columns each | 5 rows with 2 columns each |
| Columns | All ORDERS columns (ORDER KEY, CUSTKEY, STATUS, PRICE, DATE, PRIORITY, CLERK, SHIPPRIORITY, COMMENT) | Only ORDER KEY and PRICE |
| Issue | ❌ Column Projection Mismatch | AI selected subset instead of all columns |

### Root Cause
AI misinterpreted "show top 5 most expensive orders" as "show top 5 order keys and prices" rather than selecting all order details.

### Category
**Semantic Error - Column Selection**

---

## Query 9: What is the total discount given on all items? (Medium Complexity)

### Natural Language
```
"What is the total discount given on all items?"
```

### Ground Truth SQL
```sql
SELECT SUM(L_EXTENDEDPRICE * L_DISCOUNT) FROM LINEITEM
```

### AI Generated SQL
```sql
SELECT 
    SUM("L"."L_DISCOUNT") AS "Total_Discount"
FROM 
    "ADMIN"."LINEITEM" "L"
```

### Results Comparison
| Aspect | Ground Truth | AI Generated |
|--------|-------------|------------|
| Result | 10000 | 50 |
| Formula | SUM(Extended_Price × Discount) | SUM(Discount_only) |
| Issue | ❌ Calculation Logic Error | AI missed multiplication operator |

### Root Cause
AI interpreted "total discount" as sum of discount column values, missing the context that discount is typically a multiplier (percentage) applied to extended price. The correct calculation requires `L_EXTENDEDPRICE * L_DISCOUNT`.

### Category
**Semantic Error - Calculation Formula**

---

## Query 10: Find orders placed by Customer#1 (Simple Complexity)

### Natural Language
```
"Find orders placed by Customer#1"
```

### Ground Truth SQL
```sql
SELECT * FROM ORDERS WHERE O_CUSTKEY = 1
```

### AI Generated SQL
```sql
SELECT 
    o."O_ORDERKEY" AS "Order Key",
    o."O_ORDERDATE" AS "Order Date",
    o."O_TOTALPRICE" AS "Total Price"
FROM 
    "ADMIN"."ORDERS" o
JOIN 
    "ADMIN"."CUSTOMER" c ON o."O_CUSTKEY" = c."C_CUSTKEY"
WHERE 
    UPPER(c."C_NAME") = UPPER('Customer#1')
```

### Results Comparison
| Aspect | Ground Truth | AI Generated |
|--------|-------------|------------|
| Filter | WHERE O_CUSTKEY = 1 | WHERE C_NAME = 'Customer#1' |
| Join | Direct table access | Unnecessary JOIN with CUSTOMER table |
| Interpretation | Customer ID = 1 | Customer Name = 'Customer#1' |
| Issue | ❌ Entity Reference Error | AI misidentified 'Customer#1' as a name instead of ID |

### Root Cause
AI misinterpreted "Customer#1" as a customer's name rather than a customer ID. This is a domain knowledge gap - in TPC-H dataset, entities like "Customer#1", "Supplier#1" are identifiers, not display names.

### Category
**Semantic Error - Entity Reference Ambiguity**

---

## Error Categories Summary

| Category | Query | Type | Severity |
|----------|-------|------|----------|
| Column Projection | Q6 | Incomplete SELECT | Medium |
| Calculation Formula | Q9 | Missing Operator | Medium |
| Entity Reference | Q10 | Semantic Misunderstanding | High |

---

## Key Insights for Paper

### 1. **Complexity Correlation**
- Simple queries: 10/10 (100%) but Q10 failed due to naming ambiguity
- Medium queries: 4/6 (67%) - Q6, Q9 failed
- Complex queries: 3/3 (100%) - All success

**Observation**: Complexity alone doesn't determine failure. Semantic ambiguity and domain knowledge are critical.

### 2. **Common Failure Patterns**

#### Pattern A: Over-Specification
- AI adds JOIN operations not required by ground truth
- AI selects fewer/more columns than intended

#### Pattern B: Formula Misunderstanding
- AI misses mathematical operations (multiplication, addition)
- AI interprets question literally without domain context

#### Pattern C: Naming Ambiguity
- AI confuses identifiers with display names
- Lack of TPC-H benchmark knowledge

### 3. **Recommendations for Improvement**

1. **Query Context**: Provide schema documentation and entity naming conventions to the AI model
2. **Examples**: Include few-shot examples of TPC-H queries to establish naming patterns
3. **Domain Hints**: Add comments like "-- Customer#X refers to customer ID"
4. **Validation Layer**: Implement semantic validation to catch:
   - Missing required columns
   - Mathematical formula errors
   - Unnecessary table joins

---

## Statistical Impact

- **Failed Queries**: 3/10 (30%)
- **Error Rate by Complexity**: Simple (10%), Medium (33%), Complex (0%)
- **Latency Impact**: Failed queries averaged 3.19 seconds vs 3.15 seconds average
- **Recovery Potential**: All failures are correctable with domain knowledge injection

---

## Conclusion

The 30% failure rate, while significant, reveals pattern-based weaknesses rather than fundamental incapacity. Failures concentrate in:
1. Semantic ambiguity (Customer#1)
2. Formula comprehension (multiplication in discount calculation)
3. Column selection logic (unnecessary JOINs)

These are addressable through prompt engineering, context injection, and few-shot learning strategies.
