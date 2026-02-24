#!/usr/bin/env python3
import sys, os, random, string
from datetime import datetime, timedelta
sys.path.insert(0, '/Users/sanjaymishra/oracle26ai-eval')
from src.core.db_utils import get_connection

r = random.Random(42)
rc = lambda: ''.join(r.choices(string.ascii_letters + string.digits, k=15))

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS REGION (R_REGIONKEY NUMBER(38,0) NOT NULL PRIMARY KEY, R_NAME CHAR(25), R_COMMENT VARCHAR2(152));
CREATE TABLE IF NOT EXISTS NATION (N_NATIONKEY NUMBER(38,0) NOT NULL PRIMARY KEY, N_NAME CHAR(25), N_REGIONKEY NUMBER(38,0), N_COMMENT VARCHAR2(152));
CREATE TABLE IF NOT EXISTS SUPPLIER (S_SUPPKEY NUMBER(38,0) NOT NULL PRIMARY KEY, S_NAME CHAR(25), S_ADDRESS VARCHAR2(40), S_NATIONKEY NUMBER(38,0), S_PHONE CHAR(15), S_ACCTBAL NUMBER(15,2), S_COMMENT VARCHAR2(101));
CREATE TABLE IF NOT EXISTS PART (P_PARTKEY NUMBER(38,0) NOT NULL PRIMARY KEY, P_NAME VARCHAR2(55), P_MFGR CHAR(25), P_BRAND CHAR(10), P_TYPE VARCHAR2(25), P_SIZE NUMBER(38,0), P_CONTAINER CHAR(10), P_RETAILPRICE NUMBER(15,2), P_COMMENT VARCHAR2(23));
CREATE TABLE IF NOT EXISTS PARTSUPP (PS_PARTKEY NUMBER(38,0), PS_SUPPKEY NUMBER(38,0), PS_AVAILQTY NUMBER(38,0), PS_SUPPLYCOST NUMBER(15,2), PS_COMMENT VARCHAR2(199), PRIMARY KEY (PS_PARTKEY, PS_SUPPKEY));
CREATE TABLE IF NOT EXISTS CUSTOMER (C_CUSTKEY NUMBER(38,0) NOT NULL PRIMARY KEY, C_NAME VARCHAR2(25), C_ADDRESS VARCHAR2(40), C_NATIONKEY NUMBER(38,0), C_PHONE CHAR(15), C_ACCTBAL NUMBER(15,2), C_MKTSEGMENT CHAR(10), C_COMMENT VARCHAR2(117));
CREATE TABLE IF NOT EXISTS ORDERS (O_ORDERKEY NUMBER(38,0) NOT NULL PRIMARY KEY, O_CUSTKEY NUMBER(38,0), O_ORDERSTATUS CHAR(1), O_TOTALPRICE NUMBER(15,2), O_ORDERDATE DATE, O_ORDERPRIORITY CHAR(15), O_CLERK CHAR(15), O_SHIPPRIORITY NUMBER(38,0), O_COMMENT VARCHAR2(79));
CREATE TABLE IF NOT EXISTS LINEITEM (L_ORDERKEY NUMBER(38,0), L_PARTKEY NUMBER(38,0), L_SUPPKEY NUMBER(38,0), L_LINENUMBER NUMBER(38,0), L_QUANTITY NUMBER(15,2), L_EXTENDEDPRICE NUMBER(15,2), L_DISCOUNT NUMBER(15,2), L_TAX NUMBER(15,2), L_RETURNFLAG CHAR(1), L_LINESTATUS CHAR(1), L_SHIPDATE DATE, L_COMMITDATE DATE, L_RECEIPTDATE DATE, L_SHIPMODE CHAR(10), L_SHIPINSTRUCT CHAR(25), L_COMMENT VARCHAR2(44));
CREATE TABLE IF NOT EXISTS NL_SQL_TEST_QUERIES (query_id NUMBER(38,0) PRIMARY KEY, nl_question VARCHAR2(500), ground_truth_sql VARCHAR2(2000), complexity CHAR(10), category VARCHAR2(50));
"""

def bulk_insert(cursor, table, cols, sql, data, chunk=1000, nolog=True):
 
    if nolog:
        cursor.execute(f"ALTER TABLE {table} NOLOGGING")
    for i in range(0, len(data), chunk):
        chunk_data = data[i:i+chunk]
        cursor.executemany(f"INSERT /*+ APPEND PARALLEL(8) */ INTO {table} ({cols}) VALUES ({sql})", chunk_data)
        if i % 100000 == 0 and i > 0:
            print(f"    {table}: {i:,} rows")
    if nolog:
        cursor.execute(f"ALTER TABLE {table} LOGGING")
    print(f"  [OK] {table}: {len(data):,} rows")

def create_tables(cursor):
    for stmt in CREATE_TABLES_SQL.split(';'):
        stmt = stmt.strip()
        if stmt:
            try:
                cursor.execute(stmt)
            except:
                pass

def truncate_tables(cursor):
    for tbl in ['LINEITEM', 'ORDERS', 'CUSTOMER', 'PARTSUPP', 'PART', 'SUPPLIER', 'NATION', 'REGION']:
        try:
            cursor.execute(f"TRUNCATE TABLE {tbl}")
        except:
            pass

def insert_data(cursor):

    base_date = datetime.now() - timedelta(days=365)
    
    # REGION (5)
    bulk_insert(cursor, "REGION", "R_REGIONKEY, R_NAME, R_COMMENT",
                ":1, :2, :3", [(i, f'Region#{i}', rc()) for i in range(5)])
    
    # NATION (25)
    nations = [(i, f'Nation#{i}', i % 5, rc()) for i in range(25)]
    bulk_insert(cursor, "NATION", "N_NATIONKEY, N_NAME, N_REGIONKEY, N_COMMENT",
                ":1, :2, :3, :4", nations)
    
    # SUPPLIER (10K)
    sup = [(i, f'Sup#{i}', f'Addr{i}', i%25, f'Ph{i}', 5000+i, rc()) for i in range(1, 10001)]
    bulk_insert(cursor, "SUPPLIER", "S_SUPPKEY, S_NAME, S_ADDRESS, S_NATIONKEY, S_PHONE, S_ACCTBAL, S_COMMENT",
                ":1, :2, :3, :4, :5, :6, :7", sup)
    
    # PART (20K)
    part = [(i, f'Part#{i}', 'Mfg1', 'B1', 'Type1', 10, 'Bag', 900+(i%500), rc()) for i in range(1, 20001)]
    bulk_insert(cursor, "PART", "P_PARTKEY, P_NAME, P_MFGR, P_BRAND, P_TYPE, P_SIZE, P_CONTAINER, P_RETAILPRICE, P_COMMENT",
                ":1, :2, :3, :4, :5, :6, :7, :8, :9", part)
    
    # PARTSUPP (80K)
    ps = [(i, (i%10000)+1, 100+(i%8000), 50+(i%100), rc()) for i in range(1, 80001)]
    bulk_insert(cursor, "PARTSUPP", "PS_PARTKEY, PS_SUPPKEY, PS_AVAILQTY, PS_SUPPLYCOST, PS_COMMENT",
                ":1, :2, :3, :4, :5", ps)
    
    # CUSTOMER (150K)
    cust = [(i, f'Cust#{i}', f'Addr{i}', i%25, f'Ph{i}', 1000+(i%100000), 'Seg', rc()) for i in range(1, 150001)]
    bulk_insert(cursor, "CUSTOMER", "C_CUSTKEY, C_NAME, C_ADDRESS, C_NATIONKEY, C_PHONE, C_ACCTBAL, C_MKTSEGMENT, C_COMMENT",
                ":1, :2, :3, :4, :5, :6, :7, :8", cust)
    
    # ORDERS (700K)
    ord = [(i, (i%150000)+1, 'O', 1500+(i%100000), base_date+timedelta(days=i%365), 'P1', 'C1', 0, rc()) for i in range(1, 700001)]
    bulk_insert(cursor, "ORDERS", "O_ORDERKEY, O_CUSTKEY, O_ORDERSTATUS, O_TOTALPRICE, O_ORDERDATE, O_ORDERPRIORITY, O_CLERK, O_SHIPPRIORITY, O_COMMENT",
                ":1, :2, :3, :4, :5, :6, :7, :8, :9", ord)
    
    # LINEITEM (4M)
    li = [(i, ((i-1)//6)+1, base_date+timedelta(days=i%365), (i%20000)+1, (i%10000)+1, 10.0, 200+(i%100000), 0.05, 0.02, 'N', 'O',
           base_date+timedelta(days=(i%365)+30), base_date+timedelta(days=(i%365)+45), 'Truck', 'Deliver', rc()) for i in range(1, 4000001)]
    bulk_insert(cursor, "LINEITEM", "L_ORDERKEY, L_LINENUMBER, L_SHIPDATE, L_PARTKEY, L_SUPPKEY, L_QUANTITY, L_EXTENDEDPRICE, L_DISCOUNT, L_TAX, L_RETURNFLAG, L_LINESTATUS, L_COMMITDATE, L_RECEIPTDATE, L_SHIPMODE, L_SHIPINSTRUCT, L_COMMENT",
                ":1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16", li, chunk=5000)

def verify(cursor):
    """Count rows in all tables"""
    print("\nTable Counts:")
    for tbl in ['REGION', 'NATION', 'SUPPLIER', 'PART', 'PARTSUPP', 'CUSTOMER', 'ORDERS', 'LINEITEM']:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            print(f"  {tbl:15} : {cursor.fetchone()[0]:,} rows")
        except:
            print(f"  {tbl:15} : error")

def main():
    print("\n=== TPC-H Data Setup ===")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                create_tables(cur)
                truncate_tables(cur)
                verify(cur)
                print("\nInserting data...")
                insert_data(cur)
                conn.commit()
                print("\nVerifying...")
                verify(cur)
        print("\n[SUCCESS] Setup complete!\n")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
