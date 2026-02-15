# accuracy_eval.py
import time
import pandas as pd
from db_utils import init_ai_session

def run_accuracy_test(cursor):
    init_ai_session(cursor)
    
    # No longer need TO_CHAR because of oracledb.defaults.fetch_lobs = False
    cursor.execute("SELECT query_id, nl_question, ground_truth_sql, complexity FROM NL_SQL_TEST_QUERIES")
    rows = cursor.fetchall()
    
    results = []
    for qid, nl, gt_sql, comp in rows:
        print(f"🔬 Testing Q{qid}: {nl[:50]}...")
        
        try:
            # 1. AI Execution
            start = time.time()
            cursor.execute(f"SELECT AI {nl}")
            ai_res = cursor.fetchall()
            latency = time.time() - start
            ai_ok = True
        except Exception as e:
            ai_res, latency, ai_ok = None, 0, False
            print(f"❌ AI Error Q{qid}: {e}")

        # 2. Ground Truth Execution
        try:
            cursor.execute(gt_sql)
            gt_res = cursor.fetchall()
        except Exception as e:
            gt_res = []
            print(f"❌ GT Error Q{qid}: {e}")

        # 3. Semantic Comparison (Order Independent)
        match = (set(tuple(x) for x in ai_res) == set(tuple(x) for x in gt_res)) if ai_ok else False
        
        results.append({
            'query_id': qid, 'complexity': comp, 'ai_success': ai_ok,
            'semantic_match': match, 'latency_sec': round(latency, 2)
        })

    results_df = pd.DataFrame(results)
    
    # Calculate metrics
    print("\n=== ACCURACY METRICS ===")
    print(f"Overall Success Rate: {results_df['ai_success'].mean():.2%}")
    print(f"Semantic Match Rate: {results_df['semantic_match'].mean():.2%}")
    
    print("\n=== BY COMPLEXITY ===")
    print(results_df.groupby('complexity')['semantic_match'].mean())
    
    return results_df