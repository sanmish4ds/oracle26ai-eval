#!/usr/bin/env python
"""
Insert extended 22 TPC-H queries into NL_SQL_TEST_QUERIES table
"""

import sys
sys.path.insert(0, '/Users/sanjaymishra/oracle26ai-eval')

from db_utils import get_connection
import config

# Extended 22 TPC-H queries
EXTENDED_QUERIES = [
    # Simple Queries (1-5)
    (1, "What is the total quantity of items sold?", "SELECT SUM(L_QUANTITY) FROM LINEITEM", "simple"),
    (2, "How many customers are there?", "SELECT COUNT(*) FROM CUSTOMER", "simple"),
    (3, "What is the average retail price of parts?", "SELECT AVG(P_RETAILPRICE) FROM PART", "simple"),
    (4, "List all regions.", "SELECT * FROM REGION", "simple"),
    (5, "How many suppliers are there?", "SELECT COUNT(*) FROM SUPPLIER", "simple"),
    
    # Medium Queries (6-15)
    (6, "Show me all orders from 1996.", "SELECT * FROM ORDERS WHERE O_ORDERDATE BETWEEN TO_DATE('1996-01-01', 'YYYY-MM-DD') AND TO_DATE('1996-12-31', 'YYYY-MM-DD')", "medium"),
    (7, "Show top 5 most expensive orders.", "SELECT * FROM (SELECT * FROM ORDERS ORDER BY O_TOTALPRICE DESC) WHERE ROWNUM <= 5", "medium"),
    (8, "Which nation has the most customers?", "SELECT N_NAME, COUNT(*) FROM CUSTOMER JOIN NATION ON C_NATIONKEY = N_NATIONKEY GROUP BY N_NAME ORDER BY 2 DESC FETCH FIRST 1 ROW ONLY", "medium"),
    (9, "List the names of customers in the ASIA region.", "SELECT C.C_NAME FROM CUSTOMER C JOIN NATION N ON C.C_NATIONKEY = N.N_NATIONKEY JOIN REGION R ON N.N_REGIONKEY = R.R_REGIONKEY WHERE R.R_NAME = 'ASIA'", "medium"),
    (10, "Find orders placed by Customer#1.", "SELECT * FROM ORDERS WHERE O_CUSTKEY = 1", "medium"),
    (11, "What is the total discount given on all items?", "SELECT SUM(L_EXTENDEDPRICE * L_DISCOUNT) FROM LINEITEM", "medium"),
    (12, "How many unique parts were supplied by Supplier#1?", "SELECT COUNT(DISTINCT PS_PARTKEY) FROM PARTSUPP S JOIN SUPPLIER SUP ON S.PS_SUPPKEY = SUP.S_SUPPKEY WHERE SUP.S_NAME = 'Supplier#000000001'", "medium"),
    (13, "What is the average order value?", "SELECT AVG(O_TOTALPRICE) FROM ORDERS", "medium"),
    (14, "List all parts with price greater than 50.", "SELECT P_NAME, P_RETAILPRICE FROM PART WHERE P_RETAILPRICE > 50", "medium"),
    (15, "How many orders were placed in 1997?", "SELECT COUNT(*) FROM ORDERS WHERE EXTRACT(YEAR FROM O_ORDERDATE) = 1997", "medium"),
    
    # Complex Queries (16-22)
    (16, "Show revenue by region for year 1996.", "SELECT R.R_NAME, SUM(L.L_EXTENDEDPRICE * (1 - L.L_DISCOUNT)) FROM LINEITEM L JOIN ORDERS O ON L.L_ORDERKEY = O.O_ORDERKEY JOIN CUSTOMER C ON O.O_CUSTKEY = C.C_CUSTKEY JOIN NATION N ON C.C_NATIONKEY = N.N_NATIONKEY JOIN REGION R ON N.N_REGIONKEY = R.R_REGIONKEY WHERE EXTRACT(YEAR FROM O.O_ORDERDATE) = 1996 GROUP BY R.R_NAME", "complex"),
    (17, "Find the top 5 customers by total spending.", "SELECT C.C_CUSTKEY, C.C_NAME, SUM(O.O_TOTALPRICE) FROM CUSTOMER C JOIN ORDERS O ON C.C_CUSTKEY = O.O_CUSTKEY GROUP BY C.C_CUSTKEY, C.C_NAME ORDER BY 3 DESC FETCH FIRST 5 ROWS ONLY", "complex"),
    (18, "What is the total cost of parts supplied by each supplier?", "SELECT S.S_SUPPKEY, S.S_NAME, SUM(PS.PS_SUPPLYCOST * PS.PS_AVAILQTY) FROM SUPPLIER S JOIN PARTSUPP PS ON S.S_SUPPKEY = PS.PS_SUPPKEY GROUP BY S.S_SUPPKEY, S.S_NAME", "complex"),
    (19, "Average revenue by part type and year.", "SELECT P.P_TYPE, EXTRACT(YEAR FROM O.O_ORDERDATE) AS YEAR, AVG(L.L_EXTENDEDPRICE * (1 - L.L_DISCOUNT)) FROM LINEITEM L JOIN ORDERS O ON L.L_ORDERKEY = O.O_ORDERKEY JOIN PART P ON L.L_PARTKEY = P.P_PARTKEY GROUP BY P.P_TYPE, EXTRACT(YEAR FROM O.O_ORDERDATE)", "complex"),
    (20, "Count orders per customer per year.", "SELECT C.C_CUSTKEY, EXTRACT(YEAR FROM O.O_ORDERDATE) AS YEAR, COUNT(*) FROM CUSTOMER C LEFT JOIN ORDERS O ON C.C_CUSTKEY = O.O_CUSTKEY GROUP BY C.C_CUSTKEY, EXTRACT(YEAR FROM O.O_ORDERDATE)", "complex"),
    (21, "Find customers who placed no orders in 1996.", "SELECT C.C_CUSTKEY, C.C_NAME FROM CUSTOMER C WHERE NOT EXISTS (SELECT 1 FROM ORDERS O WHERE C.C_CUSTKEY = O.O_CUSTKEY AND EXTRACT(YEAR FROM O.O_ORDERDATE) = 1996)", "complex"),
    (22, "Total quantity shipped by line status.", "SELECT L.L_LINESTATUS, SUM(L.L_QUANTITY) FROM LINEITEM L GROUP BY L.L_LINESTATUS", "complex"),
]

def insert_extended_queries():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Insert all 22 queries (skip if exists)
                for qid, nl_question, ground_truth_sql, complexity in EXTENDED_QUERIES:
                    try:
                        cursor.execute("""
                            INSERT INTO NL_SQL_TEST_QUERIES (query_id, nl_question, ground_truth_sql, complexity)
                            VALUES (:1, :2, :3, :4)
                        """, (qid, nl_question, ground_truth_sql, complexity))
                        print(f"✅ Inserted Q{qid}: {nl_question[:50]}...")
                    except Exception as e:
                        if "unique constraint" in str(e).lower() or "already exists" in str(e).lower():
                            print(f"⏭️  Q{qid} already exists, skipping...")
                        else:
                            # Try update instead
                            cursor.execute("""
                                UPDATE NL_SQL_TEST_QUERIES 
                                SET nl_question = :1, ground_truth_sql = :2, complexity = :3
                                WHERE query_id = :4
                            """, (nl_question, ground_truth_sql, complexity, qid))
                            print(f"✅ Updated Q{qid}: {nl_question[:50]}...")
                
                conn.commit()
                print(f"\n✅ Successfully processed all {len(EXTENDED_QUERIES)} TPC-H queries!")
                
                # Verify
                cursor.execute("SELECT COUNT(*) FROM NL_SQL_TEST_QUERIES")
                count = cursor.fetchone()[0]
                print(f"✅ Database now contains {count} test queries")
                
                # Show summary by complexity
                cursor.execute("""
                    SELECT complexity, COUNT(*) 
                    FROM NL_SQL_TEST_QUERIES 
                    GROUP BY complexity
                """)
                for complexity, cnt in cursor.fetchall():
                    print(f"   - {complexity}: {cnt} queries")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    insert_extended_queries()
