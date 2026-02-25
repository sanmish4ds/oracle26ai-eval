# Oracle 23c Setup Guide for TPC-H Evaluation

## Overview

This guide walks through setting up Oracle Database 23c with TPC-H benchmark data for reproducing our research.

## Prerequisites

- **Oracle Database 23c** (23.1.0 or later)
- **TPC-H Kit** (for data generation)
- **Python 3.9+**
- **Minimum 50GB disk space** for scale factor 1 (1GB dataset)
- **SQL*Plus** (comes with Oracle)

## Step 1: Install Oracle Database 23c

### macOS (Homebrew)
```bash
brew install oracle-database-23c
brew services start oracle-database-23c
```

### Linux (Docker - Recommended)
```bash
docker pull container-registry.oracle.com/database/enterprise:23.1.0.0
docker run -d -e ORACLE_PWD=YourPassword123 \
  -p 1521:1521 \
  container-registry.oracle.com/database/enterprise:23.1.0.0
```

### Windows
Download from: https://www.oracle.com/database/download/
Follow official Oracle installation wizards.

### Verify Installation
```bash
sqlplus -v
# Should output: Release 23.x.x.x.x
```

## Step 2: Initial Database Setup

### Local Setup (Single Instance)
```bash
# Set environment variables
export ORACLE_HOME=/u01/app/oracle/product/23c/dbhome_1
export PATH=$ORACLE_HOME/bin:$PATH
export ORACLE_SID=orcl

# Start listener
lsnrctl start
```

### Test Connection
```bash
sqlplus sys/your_password@orcl as sysdba
SQL> SELECT * FROM v$version;
```

## Step 3: Create TPC-H Schema

### Option A: Using Official TPC-H Kit (Recommended)

**1. Download and compile TPC-H tools**
```bash
cd $HOME
wget -q http://www.tpc.org/tpch/tpch_2_20_1.zip
unzip -q tpch_2_20_1.zip
cd dbgen
make MACHINE=MACOS  # or LINUX, WINDOWS
```

**2. Generate TPC-H Data (1GB scale factor)**
```bash
# Scale factor 1 = 1GB (~5 minutes)
./dbgen -s 1 -f

# This creates files:
# customer.tbl, lineitem.tbl, orders.tbl, etc.
```

**3. Load Data into Oracle**
```bash
sqlplus sys/password@orcl as sysdba < dss.sql
```

**dss.sql** should contain:
```sql
-- Create TPC-H schema
CREATE TABLESPACE tpch_data
  DATAFILE 'tpch_data.dbf' SIZE 10G;

CREATE TABLESPACE tpch_index
  DATAFILE 'tpch_index.dbf' SIZE 5G;

-- Create tables
CREATE TABLE PART (
  p_partkey NUMBER PRIMARY KEY,
  p_name VARCHAR2(55),
  p_mfgr VARCHAR2(25),
  p_brand VARCHAR2(10),
  p_type VARCHAR2(25),
  p_size NUMBER,
  p_container VARCHAR2(10),
  p_retailprice NUMBER(12,2),
  p_comment VARCHAR2(23)
) TABLESPACE tpch_data;

-- ... (create remaining 7 tables)

-- Load data
LOAD DATA
  INFILE 'part.tbl'
  INTO TABLE part
  FIELDS TERMINATED BY '|'
  (p_partkey, p_name, ...);

COMMIT;
```

### Option B: Quick Setup (Python Script)

```bash
cd code
python -c "
import cx_Oracle
conn = cx_Oracle.connect('sys/password@orcl', mode=cx_Oracle.SYSDBA)
cursor = conn.cursor()
# Create schema and load data
cursor.execute(open('setup_tpch.sql').read())
conn.commit()
"
```

## Step 4: Configure Database Parameters

**For optimal TPC-H evaluation:**

```sql
-- Connect as SYSDBA
sqlplus sys/password@orcl as sysdba

-- Increase SGA for better performance
ALTER SYSTEM SET sga_target=8G SCOPE=BOTH;

-- Enable query optimizer improvements
ALTER SYSTEM SET optimizer_mode=ALL_ROWS SCOPE=BOTH;

-- Parallel execution setup
ALTER SYSTEM SET parallel_max_servers=8 SCOPE=BOTH;

-- Reduce I/O to simulate cached data
ALTER SYSTEM SET db_cache_size=4G SCOPE=BOTH;

-- Restart database
SHUTDOWN IMMEDIATE;
STARTUP;
```

**Verify Settings:**
```sql
sqlplus sys/password@orcl as sysdba
SQL> SHOW PARAMETER sga_target;
SQL> SHOW PARAMETER optimizer_mode;
```

## Step 5: Verify TPC-H Installation

```sql
sqlplus sys/password@orcl as sysdba <<EOF
SET PAGESIZE 0 FEEDBACK OFF VERIFY OFF HEADING OFF ECHO OFF

-- Check tables exist
SELECT table_name FROM user_tables WHERE table_name LIKE '%';

-- Check row counts
SELECT 'PART:' as table_name, COUNT(*) FROM PART;
SELECT 'CUSTOMER:' as table_name, COUNT(*) FROM CUSTOMER;
SELECT 'ORDERS:' as table_name, COUNT(*) FROM ORDERS;
SELECT 'LINEITEM:' as table_name, COUNT(*) FROM LINEITEM;

-- Verify indexes created
SELECT index_name FROM user_indexes WHERE table_name LIKE '%';

EXIT;
EOF
```

Expected row counts (Scale Factor 1):
- PART: 200,000
- CUSTOMER: 150,000
- ORDERS: 1,500,000
- LINEITEM: 6,000,000
- SUPPLIER: 10,000
- NATION: 25
- REGION: 5
- PARTSUPP: 800,000

## Step 6: Python Environment Setup

```bash
# Navigate to code directory
cd /path/to/oracle26ai-eval

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Expected packages:
# - cx_Oracle (Oracle database connectivity)
# - pandas (data analysis)
# - numpy (numerical computing)
# - flask (optional, for web interface)
```

## Step 7: Configure code/config.py

Edit `code/config.py` with your Oracle settings:

```python
# Database Configuration
ORACLE_HOST = 'localhost'           # Or your Oracle host
ORACLE_PORT = 1521                  # Default Oracle listener port
ORACLE_USER = 'sys'                 # Database user
ORACLE_PASSWORD = 'your_password'   # Your password
ORACLE_SERVICE = 'orcl'             # Service name

# TPC-H Configuration
TPCH_SCHEMA = 'dba'                 # Schema containing TPC-H tables
SCALE_FACTOR = 1                    # 1GB dataset

# Experiment Configuration
NUM_RUNS = 3                         # Number of iterations per query
WARMUP_RUNS = 1                      # Warm-up iterations (exclude from measurement)
TIMEOUT_SECONDS = 300                # Query timeout

# LLM Configuration
LLM_MODEL = 'gpt-4'                  # LLM model to use
LLM_TEMPERATURE = 0.3                # Deterministic vs creative
MAX_TOKENS = 2048                    # Response length limit

# Output Configuration
RESULTS_DIR = './results'            # Where to save results
LOG_LEVEL = 'INFO'                   # DEBUG, INFO, WARNING, ERROR
```

## Step 8: Test Connection

```bash
python -c "
import cx_Oracle
try:
    conn = cx_Oracle.connect('sys/password@localhost:1521/orcl')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM PART')
    print(f'PART table has {cursor.fetchone()[0]} rows')
    conn.close()
    print('✓ Connection successful!')
except Exception as e:
    print(f'✗ Connection failed: {e}')
"
```

## References & Resources

### GitHub Repository
Main project: https://github.com/sanmish4ds/oracle26ai-eval

### TPC-H Data Sources

**Official TPC-H Benchmark**
- http://www.tpc.org/tpch/
- Download: Free, requires registration
- License: TPC Benchmark License Agreement

**Kaggle Datasets**
- https://www.kaggle.com/search?q=tpc-h
- Pre-generated TPC-H data in various formats
- Quick start without compilation
- Multiple scale factors available

### Documentation Links

TPC-H Specification: http://www.tpc.org/tpch/
Oracle 23c: https://docs.oracle.com/en/database/

```bash
# Quick validation (3 queries)
python code/main.py --mode quick

# Should output:
# Query 1: PASS (latency: XXXms)
# Query 2: PASS (latency: XXXms)
# Query 3: PASS (latency: XXXms)
# ✓ Baseline test successful
```

## Troubleshooting

### Oracle Won't Start
```bash
# Check logs
tail -100 $ORACLE_BASE/diag/rdbms/orcl/orcl/trace/alert_orcl.log

# Restart listener
lsnrctl stop
lsnrctl start

# Start database
sqlplus / as sysdba
SQL> STARTUP;
```

### Connection Refused
```bash
# Ensure listener is running
lsnrctl status

# Check port is open
netstat -an | grep 1521

# Try direct connection
sqlplus sys/password@localhost:1521/orcl
```

### TPC-H Tables Not Found
```bash
# Login and check
sqlplus sys/password@orcl as sysdba

SQL> SELECT object_name FROM user_objects WHERE object_type='TABLE';

# If empty, run data generation again
# Make sure dss.sql is in correct directory
```

### Slow Query Execution
- Ensure database has enough memory: `SHOW PARAMETER sga_target`
- Enable parallel execution: `ALTER SYSTEM SET parallel_degree_policy=AUTO`
- Check table statistics: `ANALYZE TABLE PART COMPUTE STATISTICS`

## Hardware Recommendations

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8GB | 16GB+ |
| Storage | 100GB | 500GB+ SSD |
| Network | 100Mbps | 1Gbps (if remote) |

## Performance Tuning

For consistent benchmark results:

```sql
-- Disable automatic task execution
EXEC DBMS_AUTO_TASK_ADMIN.DISABLE;

-- Disable query result cache
ALTER SYSTEM SET result_cache_mode=OFF SCOPE=BOTH;

-- Set consistent seed for any random operations
ALTER SESSION SET seed=42;

-- Enable deterministic execution
ALTER SESSION SET plsql_code_type=INTERPRETED;
```

## Cleanup (If Needed)

```bash
# Remove TPC-H data (careful!)
sqlplus sys/password@orcl as sysdba <<EOF
DROP TABLE LINEITEM;
DROP TABLE ORDERS;
DROP TABLE CUSTOMER;
DROP TABLE PART;
DROP TABLE PARTSUPP;
DROP TABLE SUPPLIER;
DROP TABLE NATION;
DROP TABLE REGION;
COMMIT;
EXIT;
EOF

# Free disk space
rm -rf /path/to/tpch-kit/*.tbl
```

## Next Steps

1. Verify setup with: `python code/main.py --mode quick`
2. Run full evaluation: `python code/main.py`
3. Check results: `cat results/enhanced_strategy_all_22_queries.csv`

---

**For questions or issues, refer to:**
- code/README.txt (general help)
- setup/REPRODUCIBILITY_CHECKLIST.txt (verification steps)
- data/DATA_README.md (data sources)
- Oracle documentation: https://docs.oracle.com/en/database/
- GitHub: https://github.com/sanmish4ds/oracle26ai-eval
