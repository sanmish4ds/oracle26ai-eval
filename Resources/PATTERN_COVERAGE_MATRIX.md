# Pattern Coverage Analysis

Which SQL patterns can the AI handle correctly?

| Query | AGGREGATION | CORRELATED_SUBQUERY | DATE_FILTER | ENTITY_REF | EXTRACT | FETCH_FIRST | GROUP_BY | JOIN | NESTED_SELECT | NOT_EXISTS | ORDER_BY | ROWNUM | SELECT_STAR | SIMPLE_FILTER | WHERE | WRONG_ENTITY |
|-------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
Q6 | - | - | - | - | - | - | - | - | ❌ | - | ✅ | ❌ | ✅ | - | - | - |
Q10 | - | - | - | ❌ | - | - | - | - | - | - | - | - | - | ❌ | ✅ | - |
Q17 | ❌ | - | - | - | - | ❌ | ✅ | ❌ | - | - | ✅ | - | - | - | - | - |
Q21 | - | ❌ | ❌ | - | ❌ | - | - | - | - | ✅ | - | - | - | - | - | - |

## Key Insights

- **Most Problematic Patterns:**
  - Correlated subqueries (Q21) - Missing in AI generation
  - Multi-pattern combinations (Q17) - AI handles individual patterns but fails at combination
  - Oracle-specific syntax (Q6, Q21) - ROWNUM, NOT EXISTS need explicit examples

- **Patterns AI Handles Well:**
  - Basic WHERE clauses ✅
  - Simple ORDER BY ✅
  - GROUP BY (single table) ✅

- **Patterns Needing Work:**
  - ❌ Correlated subqueries with date extraction (Q21)
  - ❌ Multi-table aggregations with FETCH (Q17)
  - ❌ ROWNUM with nesting (Q6)
  - ❌ Entity reference disambiguation (Q10)

