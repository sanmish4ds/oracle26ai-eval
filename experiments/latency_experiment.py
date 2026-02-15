import time
import pandas as pd
from db_utils import init_ai_session

def run_latency_test(cursor):
    """
    Measures the breakdown of latency into:
    1. LLM Generation (Thinking)
    2. Oracle Execution (Doing)
    """
    init_ai_session(cursor)
    
    # Fetch test queries from your Ground Truth table
    cursor.execute("SELECT query_id, nl_question FROM NL_SQL_TEST_QUERIES")
    rows = cursor.fetchall()
    
    results = []

    for row in rows:
        qid, nl = row
        print(f"⏱️ Timing Q{qid}: {nl[:50]}...")
        
        try:
            # STAGE 1: Measure LLM Generation (The 'Thinking' phase)
            # action => 'showsql' stops Oracle from running the query, giving us pure LLM time.
            start_llm = time.time()
            gen_cmd = f"SELECT DBMS_CLOUD_AI.GENERATE(prompt => '{nl}', action => 'showsql') FROM DUAL"
            cursor.execute(gen_cmd)
            generated_sql = cursor.fetchone()[0]
            llm_ms = (time.time() - start_llm) * 1000

            # STAGE 2: Measure Oracle Execution (The 'Doing' phase)
            # We execute the SQL string returned by the AI directly.
            start_exe = time.time()
            cursor.execute(generated_sql)
            cursor.fetchall()
            exe_ms = (time.time() - start_exe) * 1000
            
            total_ms = llm_ms + exe_ms

            results.append({
                'query_id': qid,
                'llm_latency_ms': round(llm_ms, 2),
                'oracle_exe_ms': round(exe_ms, 2),
                'total_latency_ms': round(total_ms, 2),
                'overhead_ratio': round(llm_ms / exe_ms, 2) if exe_ms > 0 else 0
            })

        except Exception as e:
            print(f"❌ Latency Error Q{qid}: {e}")

    return pd.DataFrame(results)