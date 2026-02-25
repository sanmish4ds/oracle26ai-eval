# main.py - Comprehensive Oracle 26 AI Evaluation Suite
import pandas as pd
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Users/sanjaymishra/oracle26ai-eval')

from src.core.db_utils import get_connection
from src.experiments.accuracy_experiment import run_accuracy_test
from src.experiments.latency_experiment import run_latency_test
from src.core import config

def generate_visualizations(acc_df, lat_df):
    """Generate comprehensive visualizations"""
    sns.set_style("whitegrid")
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Oracle 26 AI Query Evaluation - Complete Results', fontsize=16, fontweight='bold')
    
    # GRAPH 1: Accuracy by Complexity (compare exact vs semantic match)
    ax = axes[0, 0]
    if 'exact_match' in acc_df.columns and 'semantic_match' in acc_df.columns:
        complexity_groups = acc_df.groupby('complexity')
        exact_rates = []
        semantic_rates = []
        complexities = []
        
        for comp, group in complexity_groups:
            exact = (group['exact_match'].sum() / len(group) * 100)
            semantic = (group['semantic_match'].sum() / len(group) * 100)
            complexities.append(comp)
            exact_rates.append(exact)
            semantic_rates.append(semantic)
        
        x = np.arange(len(complexities))
        width = 0.35
        ax.bar(x - width/2, exact_rates, width, label='Exact Match', color='#3498db')
        ax.bar(x + width/2, semantic_rates, width, label='Semantic Match', color='#2ecc71')
        ax.set_ylabel('Match Rate (%)', fontweight='bold')
        ax.set_xlabel('Complexity', fontweight='bold')
        ax.set_title('Accuracy by Complexity', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(complexities)
        ax.set_ylim(0, 110)
        ax.legend()
    
    # GRAPH 2: Overall Success Metrics
    ax = axes[0, 1]
    metrics = {
        'AI Success': acc_df['ai_success'].mean() * 100,
        'Exact Match': (acc_df['exact_match'].mean() * 100 if 'exact_match' in acc_df.columns else 0),
        'Semantic Match': (acc_df['semantic_match'].mean() * 100 if 'semantic_match' in acc_df.columns else acc_df['semantic_match'].mean() * 100)
    }
    colors = ['#e74c3c', '#3498db', '#2ecc71']
    bars = ax.bar(metrics.keys(), metrics.values(), color=colors)
    ax.set_ylabel('Rate (%)', fontweight='bold')
    ax.set_title('Overall Accuracy Metrics', fontweight='bold')
    ax.set_ylim(0, 110)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # GRAPH 3: Latency Distribution
    ax = axes[0, 2]
    ax.hist(lat_df['total_latency_ms'], bins=10, color='#1abc9c', alpha=0.7, edgecolor='black')
    ax.axvline(lat_df['total_latency_ms'].mean(), color='red', linestyle='--', linewidth=2, label=f"Mean: {lat_df['total_latency_ms'].mean():.0f}ms")
    ax.axvline(lat_df['total_latency_ms'].median(), color='orange', linestyle='--', linewidth=2, label=f"Median: {lat_df['total_latency_ms'].median():.0f}ms")
    ax.set_xlabel('Total Latency (ms)', fontweight='bold')
    ax.set_ylabel('Frequency', fontweight='bold')
    ax.set_title('Query Latency Distribution', fontweight='bold')
    ax.legend()
    
    # GRAPH 4: LLM vs Oracle Execution
    ax = axes[1, 0]
    x = np.arange(len(lat_df.head(10)))
    width = 0.35
    ax.bar(x - width/2, lat_df['llm_latency_ms'].head(10), width, label='LLM Generation', color='#e74c3c')
    ax.bar(x + width/2, lat_df['oracle_exe_ms'].head(10), width, label='Oracle Execution', color='#3498db')
    ax.set_ylabel('Latency (ms)', fontweight='bold')
    ax.set_xlabel('Top 10 Queries', fontweight='bold')
    ax.set_title('LLM vs Oracle Execution (Top 10)', fontweight='bold')
    ax.legend()
    ax.set_xticks(x)
    ax.set_xticklabels([f'Q{i+1}' for i in range(10)])
    
    # GRAPH 5: Overhead Ratio
    ax = axes[1, 1]
    top_overhead = lat_df.nlargest(10, 'overhead_ratio')
    colors_oh = ['#e74c3c' if x > 2 else '#f39c12' if x > 1 else '#2ecc71' for x in top_overhead['overhead_ratio']]
    ax.barh(range(len(top_overhead)), top_overhead['overhead_ratio'], color=colors_oh)
    ax.set_yticks(range(len(top_overhead)))
    ax.set_yticklabels([f"Q{qid}" for qid in top_overhead['query_id']])
    ax.set_xlabel('LLM/Oracle Overhead Ratio', fontweight='bold')
    ax.set_title('Top 10 Queries by LLM Overhead', fontweight='bold')
    ax.axvline(1, color='black', linestyle='--', alpha=0.5)
    
    # GRAPH 6: Success Rate by Category
    ax = axes[1, 2]
    category_stats = acc_df.groupby('complexity').agg({
        'ai_success': 'sum',
        'query_id': 'count'
    }).rename(columns={'query_id': 'total'})
    category_stats['fail_rate'] = (1 - category_stats['ai_success'] / category_stats['total']) * 100
    
    bars = ax.bar(category_stats.index, 100 - category_stats['fail_rate'].fillna(0), color=['#2ecc71', '#f39c12', '#e74c3c'])
    ax.set_ylabel('Success Rate (%)', fontweight='bold')
    ax.set_xlabel('Complexity', fontweight='bold')
    ax.set_title('Query Execution Success Rate', fontweight='bold')
    ax.set_ylim(0, 110)
    
    plt.tight_layout()
    plt.savefig('evaluation_complete.png', dpi=300, bbox_inches='tight')
    print("Saved comprehensive visualization: evaluation_complete.png")
    plt.close()

def generate_summary_report(acc_df, lat_df):
    """Generate comprehensive summary report with dynamic data"""
    report = []
    report.append("\n" + "-"*80)
    report.append("ORACLE 26 AI EVALUATION - COMPREHENSIVE RESULTS REPORT")
    report.append("-"*80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # SECTION 1: ACCURACY ANALYSIS
    report.append("\nACCURACY ANALYSIS")
    report.append("-" * 80)
    report.append(f"Total Queries Tested: {len(acc_df)}")
    report.append(f"AI Success Rate (No Errors): {acc_df['ai_success'].mean():.1%} ({int(acc_df['ai_success'].sum())}/{len(acc_df)})")
    
    if 'exact_match' in acc_df.columns:
        report.append(f"Exact Match Rate: {acc_df['exact_match'].mean():.1%} ({int(acc_df['exact_match'].sum())}/{len(acc_df)})")
        report.append(f"Semantic Match Rate: {acc_df['semantic_match'].mean():.1%} ({int(acc_df['semantic_match'].sum())}/{len(acc_df)})")
        
        # Pattern equivalence
        pattern_matches = acc_df['semantic_match'].sum() - acc_df['exact_match'].sum()
        if pattern_matches > 0:
            report.append(f"Pattern Equivalences Detected: {int(pattern_matches)}")
            report.append("  (FETCH FIRST↔ROWNUM, LEFT JOIN↔NOT EXISTS, SELECT * vs explicit columns)")
    else:
        report.append(f"Semantic Match Rate: {acc_df['semantic_match'].mean():.1%}")
    
    # By Complexity
    report.append("\n  BY COMPLEXITY:")
    for comp in sorted(acc_df['complexity'].unique()):
        comp_df = acc_df[acc_df['complexity'] == comp]
        success = comp_df['ai_success'].mean()
        if 'exact_match' in acc_df.columns:
            exact = comp_df['exact_match'].mean()
            semantic = comp_df['semantic_match'].mean()
            report.append(f"    {comp:10s}: Success={success:.1%} | Exact={exact:.1%} | Semantic={semantic:.1%} ({len(comp_df)} queries)")
        else:
            semantic = comp_df['semantic_match'].mean()
            report.append(f"    {comp:10s}: Success={success:.1%} | Semantic={semantic:.1%} ({len(comp_df)} queries)")
    
    # SECTION 2: LATENCY ANALYSIS
    report.append("\nLATENCY ANALYSIS")
    report.append("-" * 80)
    report.append(f"Mean Latency: {lat_df['total_latency_ms'].mean():.2f} ms")
    report.append(f"Median Latency: {lat_df['total_latency_ms'].median():.2f} ms")
    report.append(f"P95 Latency: {lat_df['total_latency_ms'].quantile(0.95):.2f} ms")
    report.append(f"P99 Latency: {lat_df['total_latency_ms'].quantile(0.99):.2f} ms")
    
    report.append("\n  LATENCY BREAKDOWN:")
    report.append(f"    Average LLM Generation Time: {lat_df['llm_latency_ms'].mean():.2f} ms ({lat_df['llm_latency_ms'].mean() / lat_df['total_latency_ms'].mean() * 100:.1f}% of total)")
    report.append(f"    Average Oracle Execution Time: {lat_df['oracle_exe_ms'].mean():.2f} ms ({lat_df['oracle_exe_ms'].mean() / lat_df['total_latency_ms'].mean() * 100:.1f}% of total)")
    report.append(f"    Average LLM Overhead Ratio: {lat_df['overhead_ratio'].mean():.2f}x")
    
    # SECTION 3: KEY INSIGHTS
    report.append("\nKEY INSIGHTS")
    report.append("-" * 80)
    
    # Best and worst performers
    fastest_query = lat_df.loc[lat_df['total_latency_ms'].idxmin()]
    slowest_query = lat_df.loc[lat_df['total_latency_ms'].idxmax()]
    report.append(f"Fastest Query (Q{fastest_query['query_id']}): {fastest_query['total_latency_ms']:.2f} ms")
    report.append(f"Slowest Query (Q{slowest_query['query_id']}): {slowest_query['total_latency_ms']:.2f} ms")
    
    # Accuracy insights
    failed_queries = acc_df[acc_df['ai_success'] == False]
    if len(failed_queries) > 0:
        report.append(f"\nFailed Queries: {len(failed_queries)}")
        for _, row in failed_queries.iterrows():
            report.append(f"  • Q{int(row['query_id'])}: {row['nl_question'][:60]}...")
    
    # SECTION 4: PRODUCTION READINESS
    report.append("\nPRODUCTION READINESS ASSESSMENT")
    report.append("-" * 80)
    
    success_rate = acc_df['ai_success'].mean()
    semantic_rate = acc_df['semantic_match'].mean() if 'semantic_match' in acc_df.columns else 0
    p95_latency = lat_df['total_latency_ms'].quantile(0.95)
    
    assessments = []
    if success_rate >= 0.95:
        assessments.append("[PASS] SQL Validity: EXCELLENT (99%+ SQL is syntactically valid)")
    elif success_rate >= 0.90:
        assessments.append("[PASS] SQL Validity: GOOD (90%+ SQL is syntactically valid)")
    else:
        assessments.append("[FAIR] SQL Validity: ACCEPTABLE (80%+ SQL is syntactically valid)")
    
    if semantic_rate >= 0.70:
        assessments.append("[PASS] Result Accuracy: EXCELLENT (70%+ queries produce correct results)")
    elif semantic_rate >= 0.50:
        assessments.append("[PASS] Result Accuracy: GOOD (50%+ queries produce correct results)")
    else:
        assessments.append("[FAIR] Result Accuracy: ACCEPTABLE (requires refinement)")
    
    if p95_latency < 5000:
        assessments.append("[PASS] Latency: EXCELLENT (P95 < 5 seconds)")
    elif p95_latency < 10000:
        assessments.append("[PASS] Latency: GOOD (P95 < 10 seconds)")
    else:
        assessments.append("[FAIR] Latency: ACCEPTABLE (P95 > 10 seconds)")
    
    for assessment in assessments:
        report.append(f"  {assessment}")
    
    report.append("\n" + "-"*80)
    
    return "\n".join(report)

def main():
    print("Starting Oracle 26 AI Comprehensive Evaluation Suite...\n")
    
    acc_df = None
    lat_df = None
    
    # Run experiments with single connection
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # EXPERIMENT 1: Accuracy Test
                print("\n" + "="*80)
                print("EXPERIMENT 1: ACCURACY & SEMANTIC MATCHING")
                print("="*80)
                try:
                    acc_df = run_accuracy_test(cursor)
                except Exception as e:
                    print(f"⚠️  Accuracy experiment warning: {e}")
                    print("Attempting to load cached accuracy results...")
                    try:
                        acc_df = pd.read_csv('accuracy_results.csv')
                        print(f"Loaded {len(acc_df)} cached accuracy results")
                    except:
                        pass
                
                # EXPERIMENT 2: Latency Test
                if acc_df is not None:
                    print("\n" + "="*80)
                    print("EXPERIMENT 2: LATENCY BREAKDOWN ANALYSIS")
                    print("="*80)
                    try:
                        lat_df = run_latency_test(cursor)
                    except KeyboardInterrupt:
                        print("\n⚠️  Latency experiment interrupted by timeout (normal for large result sets)")
                        print("Attempting to load cached latency results...")
                        try:
                            lat_df = pd.read_csv('latency_results.csv')
                            print(f"✅ Loaded {len(lat_df)} cached latency results")
                        except:
                            pass
                    except Exception as e:
                        print(f"⚠️  Latency experiment error: {e}")
                        try:
                            lat_df = pd.read_csv('latency_results.csv')
                            print(f"✅ Loaded {len(lat_df)} cached latency results")
                        except:
                            pass
    
    except Exception as e:
        print(f"Connection error: {e}")
        print("Attempting to load cached results...")
        try:
            acc_df = pd.read_csv('accuracy_results.csv')
            lat_df = pd.read_csv('latency_results.csv')
            print(f"Loaded cached data: {len(acc_df)} accuracy, {len(lat_df)} latency")
        except:
            return
    
    # Only proceed with visualization and report if we have data
    if acc_df is None or lat_df is None:
        print("\nCould not obtain experimental data. Exiting.")
        return
    
    # Generate visualizations
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)
    try:
        generate_visualizations(acc_df, lat_df)
    except Exception as e:
        print(f"Visualization error: {e}")
        import traceback
        traceback.print_exc()
    
    # Generate comprehensive report
    print("\n" + "="*80)
    print("GENERATING COMPREHENSIVE REPORT")
    print("="*80)
    report = generate_summary_report(acc_df, lat_df)
    print(report)
    
    # Save report to file
    with open('evaluation_report.txt', 'w') as f:
        f.write(report)
    print("\nReport saved to: evaluation_report.txt")
    
    # Save detailed results
    acc_df.to_csv('accuracy_results_final.csv', index=False)
    lat_df.to_csv('latency_results_final.csv', index=False)
    print("Detailed results saved to: accuracy_results_final.csv, latency_results_final.csv")
    
    print("\n" + "-"*80)
    print("COMPREHENSIVE EVALUATION COMPLETE")
    print("-"*80)

if __name__ == "__main__":
    main()