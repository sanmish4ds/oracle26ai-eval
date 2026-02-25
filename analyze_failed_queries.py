#!/usr/bin/env python
"""
Extract and compare AI-generated vs ground truth SQL for all 4 failed queries
"""

import pandas as pd
from db_utils import get_connection, init_ai_session

FAILED_QUERIES = {
    6: {
        'question': "Show top 5 most expensive orders.",
        'ground_truth': "SELECT * FROM (SELECT * FROM ORDERS ORDER BY O_TOTALPRICE DESC) WHERE ROWNUM <= 5"
    },
    10: {
        'question': "Find orders placed by Customer#1.",
        'ground_truth': "SELECT * FROM ORDERS WHERE O_CUSTKEY = 1"
    },
    17: {
        'question': "Find the top 5 customers by total spending.",
        'ground_truth': "SELECT C.C_CUSTKEY, C.C_NAME, SUM(O.O_TOTALPRICE) FROM CUSTOMER C JOIN ORDERS O ON C.C_CUSTKEY = O.O_CUSTKEY GROUP BY C.C_CUSTKEY, C.C_NAME ORDER BY 3 DESC FETCH FIRST 5 ROWS ONLY"
    },
    21: {
        'question': "Find customers who placed no orders in 1996.",
        'ground_truth': "SELECT C.C_CUSTKEY, C.C_NAME FROM CUSTOMER C WHERE NOT EXISTS (SELECT 1 FROM ORDERS O WHERE C.C_CUSTKEY = O.O_CUSTKEY AND EXTRACT(YEAR FROM O.O_ORDERDATE) = 1996)"
    }
}

SCHEMA_CONTEXT = """
DATABASE SCHEMA (TPC-H Benchmark):
- CUSTOMER: C_CUSTKEY (ID), C_NAME, C_NATIONKEY, C_ADDRESS, C_PHONE
- ORDERS: O_ORDERKEY, O_CUSTKEY, O_ORDERDATE, O_TOTALPRICE, O_ORDERSTATUS, O_ORDERPRIORITY
- LINEITEM: L_ORDERKEY, L_PARTKEY, L_SUPPKEY, L_LINENUMBER, L_QUANTITY, L_EXTENDEDPRICE, L_DISCOUNT, L_TAX, L_LINESTATUS
- PART: P_PARTKEY (ID), P_NAME, P_RETAILPRICE, P_TYPE, P_SIZE, P_BRAND
- SUPPLIER: S_SUPPKEY (ID), S_NAME, S_ADDRESS, S_NATIONKEY
- PARTSUPP: PS_PARTKEY, PS_SUPPKEY, PS_AVAILQTY, PS_SUPPLYCOST
- NATION: N_NATIONKEY, N_NAME, N_REGIONKEY
- REGION: R_REGIONKEY, R_NAME

ORACLE SQL GENERATION RULES:
1. QUOTE SYNTAX: Never use empty quotes (""), never quote aliases unnecessarily
2. ENTITY REFS: "Customer#1" = C_CUSTKEY=1, "Supplier#5" = S_SUPPKEY=5
3. COLUMN SELECTION: For "List X with criteria", include identifying column + filter column, exclude IDs
4. CALCULATIONS: Discount = SUM(price * (1 - discount))
5. SORTING/LIMITING: Use FETCH FIRST N ROWS ONLY for TOP
6. JOINS: Use INNER JOIN for required, LEFT JOIN only when needed
"""

def generate_ai_sql(cursor, question):
    """Generate SQL using Oracle AI"""
    prompt = f"""{SCHEMA_CONTEXT}

TASK: Generate Oracle SQL for the following question.

Question: {question}

Generate only the SQL query. No explanations."""
    
    try:
        safe_prompt = prompt.replace("'", "''")
        gen_cmd = f"""
        SELECT DBMS_CLOUD_AI.GENERATE(
            prompt => '{safe_prompt}',
            action => 'showsql'
        ) FROM DUAL
        """
        cursor.execute(gen_cmd)
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        return f"ERROR: {str(e)}"

def compare_queries(query_id, question, gt_sql):
    """Compare AI-generated vs ground truth for a query"""
    
    with get_connection() as conn:
        with conn.cursor() as cursor:
            init_ai_session(cursor)
            
            ai_sql = generate_ai_sql(cursor, question)
            
            print(f"\n{'='*90}")
            print(f"Q{query_id}: {question}")
            print(f"{'='*90}")
            
            print(f"\n📌 GROUND TRUTH SQL:")
            print(f"{'-'*90}")
            print(gt_sql)
            
            print(f"\n🤖 AI-GENERATED SQL:")
            print(f"{'-'*90}")
            print(ai_sql if ai_sql else "(None)")
            
            if ai_sql and not ai_sql.startswith("ERROR"):
                print(f"\n🔍 COMPARISON:")
                print(f"{'-'*90}")
                
                # Try to execute both
                try:
                    cursor.execute(gt_sql)
                    gt_results = cursor.fetchall()
                    gt_status = f"✓ SUCCESS ({len(gt_results)} rows)"
                except Exception as e:
                    gt_results = None
                    gt_status = f"✗ ERROR: {str(e)[:50]}"
                
                try:
                    cursor.execute(ai_sql)
                    ai_results = cursor.fetchall()
                    ai_status = f"✓ EXECUTED ({len(ai_results)} rows)"
                except Exception as e:
                    ai_results = None
                    ai_status = f"✗ ERROR: {str(e)[:50]}"
                
                print(f"Ground Truth:  {gt_status}")
                print(f"AI Generated:  {ai_status}")
                
                if gt_results and ai_results:
                    match = set(tuple(str(x) for x in row) for row in gt_results) == set(tuple(str(x) for x in row) for row in ai_results)
                    print(f"Results Match: {'✓ YES' if match else '✗ NO'}")
                
                # Analysis
                print(f"\n📊 PATTERN DIFFERENCES:")
                gt_upper = gt_sql.upper()
                ai_upper = ai_sql.upper() if isinstance(ai_sql, str) else ""
                
                patterns = {
                    'ROWNUM': ('ROWNUM' in gt_upper, 'ROWNUM' in ai_upper),
                    'FETCH FIRST': ('FETCH FIRST' in gt_upper, 'FETCH FIRST' in ai_upper),
                    'NOT EXISTS': ('NOT EXISTS' in gt_upper, 'NOT EXISTS' in ai_upper),
                    'LEFT JOIN': ('LEFT JOIN' in gt_upper, 'LEFT JOIN' in ai_upper),
                    'GROUP BY': ('GROUP BY' in gt_upper, 'GROUP BY' in ai_upper),
                    'SELECT *': ('SELECT *' in gt_upper, 'SELECT *' in ai_upper),
                }
                
                for pattern, (gt_has, ai_has) in patterns.items():
                    if gt_has or ai_has:
                        status = "✓" if gt_has == ai_has else "✗"
                        print(f"  {status} {pattern:15s}: GT={gt_has:5} AI={ai_has:5}")

if __name__ == "__main__":
    print("\n" + "="*90)
    print("FAILED QUERIES - DETAILED COMPARISON")
    print("="*90)
    
    for qid in [6, 10, 17, 21]:
        info = FAILED_QUERIES[qid]
        compare_queries(qid, info['question'], info['ground_truth'])
    
    print(f"\n" + "="*90)
    print("ANALYSIS COMPLETE")
    print("="*90)
