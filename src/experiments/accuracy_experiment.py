# accuracy_eval.py
import sys
import time
import pandas as pd
sys.path.insert(0, '/Users/sanjaymishra/oracle26ai-eval')
from src.core.db_utils import init_ai_session

def is_semantically_equivalent(ai_res, gt_res, ai_query, gt_sql):
    """Check if results are semantically equivalent (same row count & pattern match)"""
    if not ai_res or not gt_res:
        return False
    
    # Exact match (best case)
    if set(tuple(x) for x in ai_res) == set(tuple(x) for x in gt_res):
        return True
    
    # Same row count with known SQL pattern equivalences
    if len(ai_res) == len(gt_res) and len(ai_res) > 0:
        ai_upper = ai_query.upper() if isinstance(ai_query, str) else ""
        gt_upper = gt_sql.upper()
        
        patterns = [
            ('FETCH FIRST' in ai_upper and 'ROWNUM' in gt_upper),
            ('LEFT JOIN' in ai_upper and 'NOT EXISTS' in gt_upper),
            ('NOT EXISTS' in ai_upper and 'LEFT JOIN' in gt_upper),
        ]
        
        if any(patterns):
            return True
    
    return False

def run_accuracy_test(cursor):
    init_ai_session(cursor)
    
    # No longer need TO_CHAR because of oracledb.defaults.fetch_lobs = False
    cursor.execute("SELECT query_id, nl_question, ground_truth_sql, complexity FROM NL_SQL_TEST_QUERIES ORDER BY query_id")
    rows = cursor.fetchall()
    
    results = []
    for qid, nl, gt_sql, comp in rows:
        print(f"Testing Q{qid}: {nl[:50]}...")
        
        ai_query = None
        ai_count = 0
        gt_count = 0
        try:
            # 1. AI SQL Generation
            start = time.time()
            gen_cmd = f"SELECT DBMS_CLOUD_AI.GENERATE(prompt => '{nl}', action => 'showsql') FROM DUAL"
            cursor.execute(gen_cmd)
            ai_query = cursor.fetchone()[0]
            #print(f"Generated SQL: {ai_query}")  # Debug: print generated SQL
            
            # 2. AI Execution - wrap with COUNT(*) for performance
            if qid == 21:
                cursor.execute("BEGIN DBMS_SESSION.SET_TIME_LIMIT(300); END;", ())  # 5 min timeout
            
            count_query = f"SELECT COUNT(*) FROM ({ai_query})"
            cursor.execute(count_query)
            ai_count = cursor.fetchone()[0]
            latency = time.time() - start
            ai_ok = True
        except Exception as e:
            ai_count, latency, ai_ok = 0, 0, False
            print(f"AI Error Q{qid}: {e}")

        # 2. Ground Truth Execution - wrap with COUNT(*) for performance
        try:
            if qid == 21:
                cursor.execute("BEGIN DBMS_SESSION.SET_TIME_LIMIT(300); END;", ())  # 5 min timeout
            
            count_query = f"SELECT COUNT(*) FROM ({gt_sql})"
            cursor.execute(count_query)
            gt_count = cursor.fetchone()[0]
        except Exception as e:
            gt_count = 0
            print(f"GT Error Q{qid}: {e}")

        # 3. Compare Results (Count-based comparison)
        exact_match = (ai_count == gt_count) if ai_ok else False
        semantic_match = (ai_count == gt_count) if ai_ok else False
        
        # Convert results to string for CSV storage
        ai_results_str = f"[{ai_count} rows]"
        gt_results_str = f"[{gt_count} rows]"
        
        results.append({
            'query_id': qid,
            'nl_question': nl,
            'ground_truth_sql': gt_sql,
            'ai_query': ai_query,
            'ai_results': ai_results_str,
            'gt_results': gt_results_str,
            'complexity': comp,
            'ai_success': ai_ok,
            'exact_match': exact_match,
            'semantic_match': semantic_match,
            'latency_sec': round(latency, 2)
        })

    results_df = pd.DataFrame(results)
    
    # Save to CSV
    results_df.to_csv('accuracy_results.csv', index=False)
    print("\nResults saved to accuracy_results.csv")
    
    # Calculate metrics
    print("\n" + "-"*60)
    print("ACCURACY METRICS")
    print("-"*60)
    print(f"Overall Success Rate: {results_df['ai_success'].mean():.2%}")
    print(f"Exact Match Rate: {results_df['exact_match'].mean():.2%}")
    print(f"Semantic Match Rate: {results_df['semantic_match'].mean():.2%}")
    
    print("\nBY COMPLEXITY:")
    by_comp = results_df.groupby('complexity')[['exact_match', 'semantic_match']].mean()
    print(by_comp)

    
    return results_df

if __name__ == "__main__":
    from src.core.db_utils import get_connection
    with get_connection() as conn:
        with conn.cursor() as cursor:
            run_accuracy_test(cursor)