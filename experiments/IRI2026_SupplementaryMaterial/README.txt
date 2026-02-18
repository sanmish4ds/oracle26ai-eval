================================================================================
IRI 2026 SUPPLEMENTARY MATERIAL
================================================================================

Paper Title:
"Evaluating Oracle's Native AI SQL Generation on TPC-H Benchmark: 
 Schema Context as Production-Ready Accuracy Lever"

Authors: Sanjay Mishra
Date: February 17, 2026

================================================================================
CONTENTS OVERVIEW
================================================================================

1. code/
   - Complete Python source code for reproducing results
   - All experiments, utilities, and configuration
   - Ready to run with proper setup

2. data/
   - OUTPUT DIRECTORY: Where results will be generated
   - CSV files with detailed measurements after running experiments
   - Performance metrics and latency breakdowns
   - See data/DATA_README.md for data sources (TPC-H + Kaggle)

3. setup/
   - Database setup instructions
   - Configuration guide for Oracle 23c
   - TPC-H queries reference

4. results/
   - Detailed analysis and additional figures
   - Extended appendix with per-query results
   - Performance comparison visualizations

================================================================================
QUICK START REPRODUCIBILITY (5 STEPS)
================================================================================

Step 1: Read Setup Instructions
   $ cat setup/SETUP_GUIDE.md

Step 2: Prepare TPC-H Data
   $ see data/DATA_README.md
   Download TPC-H from http://www.tpc.org/tpch/ or Kaggle
   Follow setup/SETUP_GUIDE.md to load into Oracle

Step 3: Install Dependencies
   $ cd code
   $ pip install -r requirements.txt

Step 4: Configure Oracle Connection
   $ nano code/config.py
   Edit: host, port, username, service_name
   (Do NOT commit passwords to version control)

Step 5: Run Full Benchmark
   $ python main.py

Step 6: View Results
   $ cat ../data/enhanced_strategy_all_22_queries.csv

Expected Output: CSV with 22 rows (one per TPC-H query)
Expected Duration: 2-4 hours (depends on Oracle hardware)

================================================================================
KEY FILES EXPLAINED
================================================================================

code/main.py
   - Entry point for running full evaluation
   - Executes baseline and enhanced strategy
   - Outputs comprehensive results

code/config.py
   - Database connection settings
   - MODIFY: Your Oracle 23c credentials here
   - Default: Localhost, port 1521, service_name "orcl"

code/db_utils.py
   - Database connectivity utilities
   - Query execution framework
   - Result collection and measurement

code/experiments/
   - accuracy_experiment.py: Baseline evaluation (63.64% accuracy)
   - latency_experiment.py: Performance timing breakdown
   - Enhanced strategy implementation

code/requirements.txt
   - Python dependencies (cx_Oracle, pandas, numpy, etc.)
   - Install via: pip install -r requirements.txt

setup/SETUP_GUIDE.md
   - Detailed Oracle 23c installation
   - TPC-H schema creation
   - Data loading procedures

setup/REPRODUCIBILITY_CHECKLIST.txt
   - Verification checklist
   - Confirms all components in place
   - Hardware and version requirements

setup/TPCH_22_QUERIES.txt
   - Complete TPC-H benchmark queries
   - Reference for understanding methodology
   - Query complexity annotations

data/DATA_README.md
   - Where to get TPC-H benchmark data
   - Kaggle dataset references
   - Data generation and loading instructions
   - CSV format specifications

================================================================================
RESULTS SUMMARY
================================================================================

Baseline Accuracy:        63.64% (14 out of 22 queries)
Enhanced Accuracy:        86.36% (19 out of 22 queries)
Improvement:              +22.73 percentage points

Query Distribution:
  - Simple Tier (4 queries):   75% → 75%  (no change)
  - Medium Tier (8 queries):   50% → 75%  (+25pp)
  - Complex Tier (10 queries): 70% → 100% (+30pp)

Latency Analysis:
  - LLM Generation:    3,303 ms (92.5% of total)
  - Query Execution:      47 ms ( 1.3% of total)
  - Other components:    221 ms ( 6.2% of total)
  - Total:            3,571 ms

Failures (3 queries - 13.64%):
  - Q6:  ROWNUM pattern (Oracle-specific syntax)
  - Q10: Entity reference ambiguity
  - Q14: Schema comprehension gap

================================================================================
PREREQUISITES
================================================================================

Required Software:
  - Python 3.9 or higher
  - Oracle 23c database (23.1.0 or later tested)
  - cx_Oracle Python module
  - 4GB RAM minimum (8GB recommended)
  - 50GB disk space (for TPC-H 1GB scale factor)

Tested On:
  - macOS 14.3
  - Python 3.11
  - Oracle Database 23c Enterprise Edition
  - TeX Live 2025 (for paper compilation)

Network:
  - Connection to Oracle 23c instance (local or remote)
  - Stable network connection (for LLM API calls if using cloud)

================================================================================
ENVIRONMENT SETUP
================================================================================

1. Create Python Virtual Environment
   $ python3 -m venv venv
   $ source venv/bin/activate

2. Install Dependencies
   $ pip install --upgrade pip
   $ pip install -r code/requirements.txt

3. Configure Oracle Connection
   Edit code/config.py with your database details:
   - ORACLE_HOST = 'localhost'
   - ORACLE_PORT = 1521
   - ORACLE_USER = 'sys'
   - ORACLE_PASSWORD = 'your_password'
   - ORACLE_SERVICE = 'orcl'

4. Create/Prepare TPC-H Schema
   Follow setup/SETUP_GUIDE.md for data generation

5. Run Verification
   $ python -c "import cx_Oracle; print('Oracle connection OK')"

================================================================================
RUNNING EXPERIMENTS
================================================================================

Full Pipeline (All 22 Queries):
  $ python code/main.py

Baseline Only (Fast - ~30 minutes):
  $ python code/experiments/accuracy_experiment.py --mode baseline

Enhanced Strategy Only:
  $ python code/experiments/accuracy_experiment.py --mode enhanced

Latency Measurement:
  $ python code/experiments/latency_experiment.py

Single Query Testing:
  $ python -c "from experiments.accuracy_experiment import test_query; test_query(1)"

Usage:
  $ python code/main.py --help

Output Files:
  - enhanced_strategy_all_22_queries.csv (main results)
  - baseline_results.csv (63.64% baseline)
  - latency_breakdown.csv (timing measurements)
  - execution_log.txt (detailed execution trace)

================================================================================
TROUBLESHOOTING
================================================================================

Error: "cx_Oracle.DatabaseError: DPY-6010"
    → Oracle not running or port 1521 closed
    → Check: sqlplus sys/password@orcl

Error: "Unable to locate ORACLE_HOME"
    → Set ORACLE_HOME environment variable
    → macOS: export ORACLE_HOME=/Users/user/instantclient

Error: "ORA-01017: invalid username/password"
    → Verify credentials in code/config.py
    → Check Oracle user privileges (CREATE, SELECT, INDEX required)

Error: "TPC-H schema not found"
    → Run: setup/SETUP_GUIDE.md step 3
    → Generate TPC-H data: cd tpch-kit && ./dbgen

Error: "ModuleNotFoundError: No module named 'cx_Oracle'"
    → pip install cx_Oracle
    → Verify: python -c "import cx_Oracle"

Long Execution Times:
    → Normal: 2-4 hours for full 22-query benchmark
    → If > 8 hours: Check Oracle instance performance
    → Monitor: select * from v$sessions while running

================================================================================
DATA FORMAT SPECIFICATIONS
================================================================================

Main Results CSV (enhanced_strategy_all_22_queries.csv):
  Columns:
    - query_id: TPC-H query number (1-22)
    - query_tier: Complexity (Simple/Medium/Complex)
    - baseline_pass: Baseline semantic success (Yes/No)
    - enhanced_pass: Enhanced strategy success (Yes/No)
    - baseline_latency_ms: Query runtime (baseline)
    - enhanced_latency_ms: Query runtime (enhanced)
    - improvement_pct: Performance improvement percentage
    - llm_time_ms: LLM generation time
    - oracle_time_ms: Database execution time
    - failure_reason: If failed, why
    - notes: Additional observations

Latency CSV (latency_breakdown.csv):
  Columns:
    - component: Processing stage
    - time_ms: Duration in milliseconds
    - pct_of_total: Percentage of total time
    - description: What is this component

================================================================================
VERIFICATION CHECKLIST
================================================================================

Before Running Experiments:
  ☐ Python 3.9+ installed: python --version
  ☐ Virtual environment activated: which python (shows venv path)
  ☐ Dependencies installed: pip list | grep cx_Oracle
  ☐ Oracle 23c running: sqlplus -v
  ☐ Network connectivity: ping oracle_host
  ☐ config.py configured with correct credentials
  ☐ TPC-H schema created and data loaded
  ☐ Disk space: 50GB+ available
  ☐ Read setup/REPRODUCIBILITY_CHECKLIST.txt

Expected System Capabilities:
  ☐ CPU: 4+ cores recommended
  ☐ RAM: 8GB+ for comfortable execution
  ☐ I/O: SSD storage recommended
  ☐ Network: Stable connection to Oracle instance
  ☐ Time: Allow 2-4 hours for full execution

Post-Execution Verification:
  ☐ enhanced_strategy_all_22_queries.csv created
  ☐ CSV has 22 data rows + 1 header
  ☐ CSV columns match specification
  ☐ No NaN or error values
  ☐ Results file size: ~5KB
  ☐ Execution log shows no exceptions
  ☐ Final accuracy: 86.36% (19/22 passing)

================================================================================
CONTACT & ATTRIBUTION
================================================================================

Author: Sanjay Mishra
Email: sanmish4@icloud.com

GitHub Repository (Main Project):
  https://github.com/sanmish4ds/oracle26ai-eval

Data Sources:
  TPC-H Benchmark (Official):
    http://www.tpc.org/tpch/
  
  TPC-H on Kaggle (Pre-generated data):
    https://www.kaggle.com/search?q=tpc-h
    Search for TPC-H datasets in Kaggle for quick start

If you use this work, please cite:
  Mishra, S. (2026). "Evaluating Oracle's Native AI SQL Generation on TPC-H 
  Benchmark: Schema Context as Production-Ready Accuracy Lever." 
  IRI 2026 Conference.

Third-Party Attribution:

TPC-H Benchmark:
  © Transaction Processing Council
  http://www.tpc.org/tpch/
  License: TPC Benchmark License Agreement

Kaggle Datasets (if used):
  Various publishers on https://www.kaggle.com/datasets
  License: Varies by dataset publisher

Oracle Database 23c:
  © Oracle Corporation
  https://www.oracle.com/database/
  License: Oracle Technology Network License Agreement

================================================================================
LICENSE
================================================================================

This supplementary material is provided under MIT License.
See LICENSE file for details.

You are free to:
  ✓ Use this code for research and education
  ✓ Modify and redistribute with attribution
  ✓ Run commercial applications

You must:
  ✓ Include original license
  ✓ Provide attribution to authors
  ✓ List significant changes

================================================================================
REVISION HISTORY
================================================================================

Version 1.0 (February 17, 2026)
  - Initial supplementary material release
  - Complete source code for reproduction
  - Detailed setup and running instructions
  - README and documentation

================================================================================
