import sys
import time
import pandas as pd
sys.path.insert(0, '/Users/sanjaymishra/oracle26ai-eval')
from src.core.db_utils import init_ai_session

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
        print(f"Timing Q{qid}: {nl[:50]}...")
        
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
            # Execute full SQL and measure TRUE execution time (including network transfer)
            if qid == 21:
                cursor.execute("BEGIN DBMS_SESSION.SET_TIME_LIMIT(60); END;", ())  # 60 sec timeout for Q21
            
            start_exe = time.time()
            cursor.execute(generated_sql)
            ai_results = cursor.fetchall()  # Fetch actual results for true latency
            exe_ms = (time.time() - start_exe) * 1000
            ai_count = len(ai_results)
            ai_results = f"[{ai_count} rows]"
            
            # STAGE 3: Get Ground Truth Results (measure true execution time)
            if qid == 21:
                cursor.execute("BEGIN DBMS_SESSION.SET_TIME_LIMIT(60); END;", ())  # 60 sec timeout for Q21
            
            start_gt = time.time()
            cursor.execute(gt_sql)
            gt_results = cursor.fetchall()  # Fetch actual results
            gt_ms = (time.time() - start_gt) * 1000
            gt_count = len(gt_results)
            gt_results = f"[{gt_count} rows]"
            
            total_ms = llm_ms + exe_ms
            
            # Results already stored as count strings above
            ai_results_str = ai_results
            gt_results_str = gt_results

            results.append({
                'query_id': qid,
                'nl_question': nl,
                'generated_sql': generated_sql,
                'ground_truth_sql': gt_sql,
                'ai_results': ai_results_str,
                'gt_results': gt_results_str,
                'llm_latency_ms': round(llm_ms, 2),
                'ai_exe_ms': round(exe_ms, 2),
                'gt_exe_ms': round(gt_ms, 2),
                'total_ai_latency_ms': round(total_ms, 2),
                'overhead_ratio': round(llm_ms / exe_ms, 2) if exe_ms > 0 else 0
            })

        except Exception as e:
            print(f"Latency Error Q{qid}: {e}")

    df = pd.DataFrame(results)
    
    # Save to CSV
    df.to_csv('latency_results.csv', index=False)
    print("\nResults saved to latency_results.csv")
    
    # Statistical analysis
    print("\nLATENCY STATISTICS (TRUE END-TO-END EXECUTION TIME)")
    print(f"Mean: {df['total_ai_latency_ms'].mean():.2f} ms")
    print(f"Median: {df['total_ai_latency_ms'].median():.2f} ms")
    print(f"P95: {df['total_ai_latency_ms'].quantile(0.95):.2f} ms")
    print(f"P99: {df['total_ai_latency_ms'].quantile(0.99):.2f} ms")
    
    print("\n=== BREAKDOWN ANALYSIS ===")
    print(f"Avg LLM Generation Time: {df['llm_latency_ms'].mean():.2f} ms")
    print(f"Avg AI SQL Execution Time: {df['ai_exe_ms'].mean():.2f} ms (includes network transfer)")
    print(f"Avg Ground Truth Execution Time: {df['gt_exe_ms'].mean():.2f} ms")
    print(f"Avg Overhead Ratio (LLM/AI-Exe): {(df['llm_latency_ms'] / df['ai_exe_ms']).mean():.2f}x")
    
    return df

if __name__ == "__main__":
    from src.core.db_utils import get_connection
    with get_connection() as conn:
        with conn.cursor() as cursor:
            run_latency_test(cursor)