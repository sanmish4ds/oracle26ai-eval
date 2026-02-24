import time
import pandas as pd
from ..core.db_utils import init_ai_session

def run_latency_test(cursor):
    """
    Measures the breakdown of latency into:
    1. LLM Generation (Thinking)
    2. Oracle Execution (Doing)
    """
    init_ai_session(cursor)
    
    # Fetch test queries from your Ground Truth table
    cursor.execute("SELECT query_id, nl_question, ground_truth_sql FROM NL_SQL_TEST_QUERIES")
    rows = cursor.fetchall()
    
    results = []

    for row in rows:
        qid, nl, gt_sql = row
        print(f"⏱️ Timing Q{qid}: {nl[:50]}...")
        
        try:
            # STAGE 1: Measure LLM Generation (The 'Thinking' phase)
            # action => 'showsql' stops Oracle from running the query, giving us pure LLM time.
            start_llm = time.time()
            gen_cmd = f"SELECT DBMS_CLOUD_AI.GENERATE(prompt => '{nl}', action => 'showsql') FROM DUAL"
            cursor.execute(gen_cmd)
            generated_sql = cursor.fetchone()[0]
            #print(f"Generated SQL: {generated_sql}")  # Debug: print generated SQL
            llm_ms = (time.time() - start_llm) * 1000

            # STAGE 2: Measure Oracle Execution (The 'Doing' phase)
            # We execute the SQL string returned by the AI directly.
            start_exe = time.time()
            cursor.execute(generated_sql)
            ai_results = cursor.fetchall()
            exe_ms = (time.time() - start_exe) * 1000
            
            # STAGE 3: Get Ground Truth Results
            cursor.execute(gt_sql)
            gt_results = cursor.fetchall()
            
            total_ms = llm_ms + exe_ms
            
            # Convert results to string for CSV storage
            ai_results_str = str(ai_results) if ai_results else ""
            gt_results_str = str(gt_results) if gt_results else ""

            results.append({
                'query_id': qid,
                'nl_question': nl,
                'generated_sql': generated_sql,
                'ground_truth_sql': gt_sql,
                'ai_results': ai_results_str,
                'gt_results': gt_results_str,
                'llm_latency_ms': round(llm_ms, 2),
                'oracle_exe_ms': round(exe_ms, 2),
                'total_latency_ms': round(total_ms, 2),
                'overhead_ratio': round(llm_ms / exe_ms, 2) if exe_ms > 0 else 0
            })

        except Exception as e:
            print(f"❌ Latency Error Q{qid}: {e}")

    df = pd.DataFrame(results)
    
    # Save to CSV
    df.to_csv('latency_results.csv', index=False)
    print("\n✅ Results saved to latency_results.csv")
    
    # Statistical analysis
    print("\n=== LATENCY STATISTICS ===")
    print(f"Mean: {df['total_latency_ms'].mean():.2f} ms")
    print(f"Median: {df['total_latency_ms'].median():.2f} ms")
    print(f"P95: {df['total_latency_ms'].quantile(0.95):.2f} ms")
    print(f"P99: {df['total_latency_ms'].quantile(0.99):.2f} ms")
    
    print("\n=== BREAKDOWN ANALYSIS ===")
    print(f"Avg LLM Generation Time: {df['llm_latency_ms'].mean():.2f} ms")
    print(f"Avg Oracle Execution Time: {df['oracle_exe_ms'].mean():.2f} ms")
    print(f"Avg Overhead Ratio: {df['overhead_ratio'].mean():.2f}x")
    
    return df
