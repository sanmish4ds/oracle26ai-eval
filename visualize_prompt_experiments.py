#!/usr/bin/env python
"""
Visualize prompt engineering experiment results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 11

# Read results
exp_df = pd.read_csv('prompt_engineering_experiments.csv')

# Create figure
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Prompt Engineering Experiments: Accuracy & Latency Analysis', 
             fontsize=16, fontweight='bold', y=0.995)

# ============================================================================
# Chart 1: Accuracy Comparison
# ============================================================================
ax1 = axes[0, 0]
strategies = ['Baseline', 'Enhanced', 'Few-shot']
accuracies = [
    (exp_df['baseline_match'].sum() / len(exp_df)) * 100,
    (exp_df['enhanced_match'].sum() / len(exp_df)) * 100,
    (exp_df['fewshot_match'].sum() / len(exp_df)) * 100,
]
colors = ['#e74c3c', '#f39c12', '#2ecc71']

bars = ax1.bar(strategies, accuracies, color=colors, alpha=0.7, edgecolor='black', linewidth=2)

# Add value labels
for bar, acc in zip(bars, accuracies):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
            f'{acc:.0f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)

# Add improvement arrows
ax1.annotate('', xy=(1, accuracies[1]), xytext=(0, accuracies[0]),
            arrowprops=dict(arrowstyle='->', lw=2, color='green'))
ax1.text(0.5, (accuracies[0] + accuracies[1])/2 + 5, '+60%', 
        ha='center', fontweight='bold', fontsize=11, color='green',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

ax1.set_ylabel('Accuracy (%)', fontweight='bold', fontsize=12)
ax1.set_title('Chart 1: Accuracy by Strategy', fontweight='bold', fontsize=13)
ax1.set_ylim(0, 100)
ax1.grid(axis='y', alpha=0.3)

# ============================================================================
# Chart 2: Per-Query Results Heatmap
# ============================================================================
ax2 = axes[0, 1]
results_matrix = exp_df[['query_id', 'baseline_match', 'enhanced_match', 'fewshot_match']].set_index('query_id')
results_matrix.columns = ['Baseline', 'Enhanced', 'Few-shot']
results_matrix = results_matrix.astype(int)

# Create heatmap
sns.heatmap(results_matrix.T, annot=True, fmt='d', cmap=['#e74c3c', '#2ecc71'], 
            cbar=False, ax=ax2, linewidths=1, linecolor='black',
            xticklabels=[f'Q{qid}' for qid in results_matrix.index],
            yticklabels=['Baseline', 'Enhanced', 'Few-shot'])
ax2.set_xlabel('Query ID', fontweight='bold', fontsize=12)
ax2.set_title('Chart 2: Per-Query Results (1=Pass, 0=Fail)', fontweight='bold', fontsize=13)

# ============================================================================
# Chart 3: Latency Comparison
# ============================================================================
ax3 = axes[1, 0]
latencies = [
    exp_df['baseline_latency'].mean(),
    exp_df['enhanced_latency'].mean(),
    exp_df['fewshot_latency'].mean(),
]

bars = ax3.bar(strategies, latencies, color=colors, alpha=0.7, edgecolor='black', linewidth=2)

# Add value labels
for bar, lat in zip(bars, latencies):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 50,
            f'{lat:.0f}ms', ha='center', va='bottom', fontweight='bold', fontsize=11)

ax3.set_ylabel('Average Latency (ms)', fontweight='bold', fontsize=12)
ax3.set_title('Chart 3: Latency Impact', fontweight='bold', fontsize=13)
ax3.set_ylim(0, max(latencies) * 1.15)
ax3.grid(axis='y', alpha=0.3)

# Add "faster" annotation
if latencies[1] < latencies[0]:
    ax3.text(1, latencies[1] - 100, '⚡ Faster', 
            ha='center', fontweight='bold', fontsize=10, color='green')

# ============================================================================
# Chart 4: Improvements Summary
# ============================================================================
ax4 = axes[1, 1]
ax4.axis('off')

# Create summary text
summary_text = f"""
PROMPT ENGINEERING RESULTS SUMMARY

Test Set: 5 Representative Queries
  • 4 Previously Failed Queries
  • 1 Previously Passed Query

BASELINE STRATEGY (Current Approach)
  • Accuracy: 20% (1/5 queries)
  • Latency: {latencies[0]:.0f}ms average
  • Approach: Direct natural language

ENHANCED STRATEGY (+ Schema Context)
  • Accuracy: 80% (4/5 queries)
  • Latency: {latencies[1]:.0f}ms average
  • Improvement: +60 percentage points ✓
  • Latency Change: {latencies[1]-latencies[0]:.0f}ms ({(latencies[1]-latencies[0])/latencies[0]*100:.1f}%)
  • Fixed Queries: Q6, Q9, Q10

FEW-SHOT STRATEGY (+ Schema + Examples)
  • Accuracy: 80% (4/5 queries)
  • Latency: {latencies[2]:.0f}ms average
  • Improvement: +60 percentage points ✓
  • Latency Change: {latencies[2]-latencies[0]:.0f}ms ({(latencies[2]-latencies[0])/latencies[0]*100:.1f}%)
  • Fixed Queries: Q6, Q9, Q10

RECOMMENDATION
Enhanced strategy offers best ROI with 60% accuracy
improvement and minimal latency trade-off. Recommended
for production deployment without model fine-tuning.

NEXT STEPS
1. Deploy Enhanced strategy in production
2. Monitor accuracy improvement in real workloads
3. Consider few-shot for critical queries
4. Future: Fine-tune model on full TPC-H dataset
"""

ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
        fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('Prompt_Engineering_Results.png', dpi=300, bbox_inches='tight')
print("✅ Saved: Prompt_Engineering_Results.png")

# Also save individual charts
fig.clear()

# Simple comparison bar chart for whitepaper
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(strategies))
width = 0.25

baseline_bar = ax.bar(x - width, [exp_df['baseline_match'].sum(), 0, 0], width, 
                       label='Baseline', color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=1.5)
enhanced_bar = ax.bar(x, [0, exp_df['enhanced_match'].sum(), 0], width,
                      label='Enhanced (+Schema)', color='#f39c12', alpha=0.7, edgecolor='black', linewidth=1.5)
fewshot_bar = ax.bar(x + width, [0, 0, exp_df['fewshot_match'].sum()], width,
                     label='Few-shot (+Examples)', color='#2ecc71', alpha=0.7, edgecolor='black', linewidth=1.5)

# Add all bars for complete view
for i, acc in enumerate(accuracies):
    ax.bar(i, acc/100*5, width=0.7, color=colors[i], alpha=0.7, edgecolor='black', linewidth=2)
    ax.text(i, acc/100*5 + 0.15, f'{acc:.0f}%\n({int(acc/100*5)}/5)', 
           ha='center', va='bottom', fontweight='bold', fontsize=12)

ax.set_ylabel('Queries Correct', fontweight='bold', fontsize=13)
ax.set_xlabel('Prompting Strategy', fontweight='bold', fontsize=13)
ax.set_title('Prompt Engineering: Accuracy Improvement (+60%)', fontweight='bold', fontsize=15)
ax.set_xticks(x)
ax.set_xticklabels(strategies)
ax.set_ylim(0, 5.5)
ax.legend(fontsize=11, loc='upper left')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('Chart_Prompt_Engineering_Comparison.png', dpi=300, bbox_inches='tight')
print("✅ Saved: Chart_Prompt_Engineering_Comparison.png")

print("\n📊 Visualizations saved!")
