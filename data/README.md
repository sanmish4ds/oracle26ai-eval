# Data Directory

## Overview

This `data/` directory is where experimental results will be generated after running the evaluation.

## Data Sources

This research uses:

1. **TPC-H Benchmark Data** (Synthetic - Generated locally)
   - Official benchmark from Transaction Processing Council
   - Generated using TPC-H dbgen tool
   - Scale Factor 1 (1GB dataset)
   - Download: http://www.tpc.org/tpch/
   - License: TPC Benchmark License Agreement

2. **Kaggle Datasets** (For reference and supplementary analysis)
   - TPC-H dataset available at Kaggle
   - Link: https://www.kaggle.com/datasets
   - Search: "TPC-H" or "transaction processing benchmark"
   - License: Varies by dataset publisher

## Generated Output Files

After running the evaluation pipeline, this directory will contain:

### Primary Results
- `enhanced_strategy_all_22_queries.csv` (Main results for all 22 queries)
  - Query ID, complexity tier, baseline/enhanced accuracy, latency, LLM time, etc.

### Supporting Data (Optional)
- `baseline_results.csv` (Detailed baseline evaluation)
- `latency_breakdown.csv` (Component-level timing data)
- `failure_analysis.csv` (Detailed failure information)
- `execution_log.txt` (Full execution trace)

## CSV Format Example

```
query_id,query_tier,baseline_pass,enhanced_pass,baseline_latency_ms,enhanced_latency_ms,improvement_pct,llm_time_ms,oracle_time_ms,failure_reason,notes
1,Simple,Yes,Yes,1245,1198,3.8,1187,47,,
2,Simple,Yes,Yes,1089,1045,4.0,1032,45,,
3,Simple,Yes,Yes,1567,1512,3.5,1499,48,,
...
```

## How to Use

### Step 1: Generate TPC-H Data
```bash
cd setup
bash generate_tpch_data.sh 1  # Scale factor 1
```

### Step 2: Load into Oracle
```bash
cd setup
sqlplus sys/password@orcl as sysdba < load_tpch_data.sql
```

### Step 3: Run Evaluation
```bash
cd code
python main.py
```

### Step 4: Results Appear Here
```
data/enhanced_strategy_all_22_queries.csv
data/baseline_results.csv
data/latency_breakdown.csv
```

## TPC-H Data Generation

### Official TPC-H Kit
Download from: http://www.tpc.org/tpch/

Compilation:
```bash
wget http://www.tpc.org/tpch/tpch_2_20_1.zip
unzip tpch_2_20_1.zip
cd dbgen
make MACHINE=MACOS  # or LINUX, WINDOWS
./dbgen -s 1 -f    # Generate scale factor 1 (1GB)
```

### Pre-Generated Data Sources

**Option 1: Kaggle TPC-H Datasets**
- Search: https://www.kaggle.com/search?q=tpc-h
- Multiple publishers provide pre-generated TPC-H data
- Sizes: 1GB to 100GB+
- Format: CSV, Parquet, SQL dumps

**Option 2: GitHub Repositories**
- Popular TPC-H data repositories
- Ready-to-use SQL scripts
- Pre-compiled dbgen tools

**Option 3: Docker Images**
```bash
docker run -it tpc-h-data /bin/bash
# Pre-generated data available inside
```

## Data Privacy

This research uses:
- ✓ Synthetic benchmark data (no personal information)
- ✓ Published TPC-H specification
- ✓ No real customer/transaction data
- ✓ GDPR compliant (no PII)

## Storage Requirements

- **TPC-H Scale Factor 1**: 1 GB
- **Scale Factor 10**: 10 GB
- **Scale Factor 100**: 100 GB

Recommended: Use Scale Factor 1 for quick testing, Scale Factor 10+ for detailed benchmarking

## Attribution

When using TPC-H data, cite:

**TPC-H Benchmark**
```
Transaction Processing Council. TPC Benchmark H (Decision Support). 
Version 2.20.1. http://www.tpc.org/tpch/
```

**Kaggle Datasets** (if used)
```
[Dataset Name]. Kaggle. Retrieved from https://www.kaggle.com/datasets/[dataset-id]/
```

## Troubleshooting

### Q: Where do I get the data?
A: Use official TPC-H kit or pre-generated data from Kaggle

### Q: Can I use different data?
A: Yes, but ensure it loads into Oracle successfully and pass the verification steps

### Q: How long does data generation take?
A: Scale Factor 1: ~5-10 minutes. Scale Factor 10: ~1 hour

### Q: Is the data uploaded to GitHub?
A: No - data is too large. Generate locally or download pre-generated versions from Kaggle

## Data Verification

After loading data, verify:
```sql
SELECT 'PART' as table_name, COUNT(*) as rows FROM PART
UNION ALL
SELECT 'CUSTOMER', COUNT(*) FROM CUSTOMER
UNION ALL
SELECT 'ORDERS', COUNT(*) FROM ORDERS
UNION ALL
SELECT 'LINEITEM', COUNT(*) FROM LINEITEM;
```

Expected output (Scale Factor 1):
```
PART      200000
CUSTOMER  150000
ORDERS   1500000
LINEITEM 6000000
```

## Next Steps

1. Download TPC-H from: http://www.tpc.org/tpch/
2. Generate data: `./dbgen -s 1 -f`
3. Load into Oracle (see setup/SETUP_GUIDE.md)
4. Run evaluation: `python code/main.py`
5. Results appear in this directory

---

For more information, see:
- setup/SETUP_GUIDE.md (detailed database setup)
- results/RESULTS_README.md (results interpretation)
- README.txt (general overview)
