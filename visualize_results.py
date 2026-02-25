import sys
sys.path.insert(0, '/Users/sanjaymishra/oracle26ai-eval')

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)

# Load data
try:
    accuracy_df = pd.read_csv('accuracy_results.csv')
    print(f"✅ Loaded accuracy results: {len(accuracy_df)} queries")
except:
    print("⚠️ accuracy_results.csv not found")
    accuracy_df = None

try:
    latency_df = pd.read_csv('latency_results.csv')
    print(f"✅ Loaded latency results: {len(latency_df)} queries")
except:
    print("⚠️ latency_results.csv not found")
    latency_df = None

# Create figure with subplots
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Oracle 26 AI Query Evaluation Results', fontsize=16, fontweight='bold')

# GRAPH 1: Accuracy by Complexity (Accuracy)
if accuracy_df is not None:
    ax = axes[0, 0]
    complexity_acc = accuracy_df.groupby('complexity').agg({
        'semantic_match': ['sum', 'count']
    }).reset_index()
    complexity_acc.columns = ['complexity', 'matches', 'total']
    complexity_acc['rate'] = (complexity_acc['matches'] / complexity_acc['total'] * 100).round(1)
    
    bars = ax.bar(complexity_acc['complexity'], complexity_acc['rate'], color=['#2ecc71', '#f39c12', '#e74c3c'])
    ax.set_ylabel('Match Rate (%)', fontweight='bold')
    ax.set_xlabel('Complexity', fontweight='bold')
    ax.set_title('Semantic Match Rate by Complexity', fontweight='bold')
    ax.set_ylim(0, 110)
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{complexity_acc.iloc[i]["rate"]:.1f}%\n({int(complexity_acc.iloc[i]["matches"])}/{int(complexity_acc.iloc[i]["total"])})',
                ha='center', va='bottom', fontweight='bold')

# GRAPH 2: Success Rate Metrics (Accuracy)
if accuracy_df is not None:
    ax = axes[0, 1]
    metrics = {
        'AI Success': accuracy_df['ai_success'].mean() * 100,
        'Semantic Match': accuracy_df['semantic_match'].mean() * 100
    }
    bars = ax.bar(metrics.keys(), metrics.values(), color=['#3498db', '#9b59b6'])
    ax.set_ylabel('Rate (%)', fontweight='bold')
    ax.set_title('Overall Accuracy Metrics', fontweight='bold')
    ax.set_ylim(0, 110)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')

# GRAPH 3: Latency Distribution (Latency)
if latency_df is not None:
    ax = axes[0, 2]
    ax.hist(latency_df['total_latency_ms'], bins=10, color='#1abc9c', alpha=0.7, edgecolor='black')
    ax.axvline(latency_df['total_latency_ms'].mean(), color='red', linestyle='--', linewidth=2, label=f"Mean: {latency_df['total_latency_ms'].mean():.0f}ms")
    ax.axvline(latency_df['total_latency_ms'].median(), color='orange', linestyle='--', linewidth=2, label=f"Median: {latency_df['total_latency_ms'].median():.0f}ms")
    ax.set_xlabel('Total Latency (ms)', fontweight='bold')
    ax.set_ylabel('Frequency', fontweight='bold')
    ax.set_title('Query Latency Distribution', fontweight='bold')
    ax.legend()

# GRAPH 4: LLM vs Oracle Execution Breakdown (Latency)
if latency_df is not None:
    ax = axes[1, 0]
    x = np.arange(len(latency_df.head(10)))
    width = 0.35
    ax.bar(x - width/2, latency_df['llm_latency_ms'].head(10), width, label='LLM Generation', color='#e74c3c')
    ax.bar(x + width/2, latency_df['oracle_exe_ms'].head(10), width, label='Oracle Execution', color='#3498db')
    ax.set_ylabel('Latency (ms)', fontweight='bold')
    ax.set_xlabel('Top 10 Queries', fontweight='bold')
    ax.set_title('LLM vs Oracle Execution Latency (Top 10)', fontweight='bold')
    ax.legend()
    ax.set_xticks(x)
    ax.set_xticklabels([f'Q{i+1}' for i in range(10)])

# GRAPH 5: Overhead Ratio by Query (Latency)
if latency_df is not None:
    ax = axes[1, 1]
    top_overhead = latency_df.nlargest(10, 'overhead_ratio')
    colors = ['#e74c3c' if x > 2 else '#f39c12' if x > 1 else '#2ecc71' for x in top_overhead['overhead_ratio']]
    ax.barh(range(len(top_overhead)), top_overhead['overhead_ratio'], color=colors)
    ax.set_yticks(range(len(top_overhead)))
    ax.set_yticklabels([f"Q{qid}" for qid in top_overhead['query_id']])
    ax.set_xlabel('LLM/Oracle Overhead Ratio', fontweight='bold')
    ax.set_title('Top 10 Queries by LLM Overhead', fontweight='bold')
    ax.axvline(1, color='black', linestyle='--', alpha=0.5)

# GRAPH 6: Query Success vs Latency (Combined Analysis)
if accuracy_df is not None and latency_df is not None:
    ax = axes[1, 2]
    # Merge results
    merged = pd.merge(accuracy_df, latency_df, on='query_id')
    scatter = ax.scatter(merged['total_latency_ms'], merged['semantic_match'].astype(int) * 100,
                        s=200, alpha=0.6, c=merged['complexity'].astype('category').cat.codes,
                        cmap='viridis', edgecolors='black', linewidth=1.5)
    ax.set_xlabel('Total Latency (ms)', fontweight='bold')
    ax.set_ylabel('Semantic Match (%)', fontweight='bold')
    ax.set_title('Match Success vs Query Latency', fontweight='bold')
    ax.set_ylim(-5, 105)
    
    # Add colorbar for complexity
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Complexity Level', fontweight='bold')

plt.tight_layout()
plt.savefig('evaluation_results.png', dpi=300, bbox_inches='tight')
print("\n✅ Saved visualization: evaluation_results.png")

# Print Summary Statistics
print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)

if accuracy_df is not None:
    print("\n📊 ACCURACY METRICS:")
    print(f"  • Overall Success Rate: {accuracy_df['ai_success'].mean():.1%}")
    print(f"  • Semantic Match Rate: {accuracy_df['semantic_match'].mean():.1%}")
    by_complexity = accuracy_df.groupby('complexity')['semantic_match'].mean()
    for comp, rate in by_complexity.items():
        print(f"    - {comp}: {rate:.1%}")

if latency_df is not None:
    print("\n⏱️  LATENCY METRICS:")
    print(f"  • Mean Latency: {latency_df['total_latency_ms'].mean():.2f} ms")
    print(f"  • Median Latency: {latency_df['total_latency_ms'].median():.2f} ms")
    print(f"  • P95 Latency: {latency_df['total_latency_ms'].quantile(0.95):.2f} ms")
    print(f"  • P99 Latency: {latency_df['total_latency_ms'].quantile(0.99):.2f} ms")
    print(f"  • Avg LLM Generation: {latency_df['llm_latency_ms'].mean():.2f} ms")
    print(f"  • Avg Oracle Execution: {latency_df['oracle_exe_ms'].mean():.2f} ms")
    print(f"  • Avg Overhead Ratio: {latency_df['overhead_ratio'].mean():.2f}x")

plt.show()
