# main.py
import pandas as pd
from db_utils import get_connection
from experiments.accuracy_experiment import run_accuracy_test
from experiments.latency_experiment import run_latency_test
import config

def main():
    print("🚀 Starting TPC-H Comprehensive Evaluation Suite...")
    
    # 1. Execute Experiments inside a single connection block for efficiency
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # EXPERIMENT 1: Accuracy & Semantic Match
            print("\n" + "-"*40)
            print("RUNNING EXPERIMENT 1: ACCURACY EVALUATION")
            print("-"*40)
            acc_df = run_accuracy_test(cursor)
            
            # EXPERIMENT 2: Latency Breakdown
            print("\n" + "-"*40)
            print("RUNNING EXPERIMENT 2: LATENCY BREAKDOWN")
            print("-"*40)
            lat_df = run_latency_test(cursor)

    # 2. Final Results Presentation
    print("\n" + "═"*45)
    print("       FINAL TPC-H EVALUATION SUMMARY")
    print("═"*45)
    
    # Accuracy Metrics
    overall_succ = acc_df['ai_success'].mean()
    semantic_match = acc_df['semantic_match'].mean()
    
    # Latency Metrics
    avg_llm_ms = lat_df['llm_latency_ms'].mean()
    avg_exe_ms = lat_df['oracle_exe_ms'].mean()
    p95_total = lat_df['total_latency_ms'].quantile(0.95)

    print(f"{'Overall Success Rate:':<25} {overall_succ:.2%}")
    print(f"{'Semantic Match Rate:':<25} {semantic_match:.2%}")
    print("-" * 45)
    print(f"{'Avg LLM Thinking Time:':<25} {avg_llm_ms:>8.2f} ms")
    print(f"{'Avg Oracle Doing Time:':<25} {avg_exe_ms:>8.2f} ms")
    print(f"{'P95 End-to-End Latency:':<25} {p95_total:>8.2f} ms")
    print(f"{'AI Overhead Ratio:':<25} {(avg_llm_ms / avg_exe_ms):>7.1f}x")
    print("═"*45)

    # 3. Save Final Artifacts
    acc_df.to_csv('TPCH_Accuracy_Final.csv', index=False)
    lat_df.to_csv('TPCH_Latency_Final.csv', index=False)
    print("\n✅ All results saved to CSV. Evaluation complete!")

if __name__ == "__main__":
    main()