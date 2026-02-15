#!/usr/bin/env python
"""
Generate visualizations for the TPC-H evaluation results
Creates publication-quality charts for the whitepaper
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style for publication
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 12)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# Read data
acc_df = pd.read_csv('accuracy_results.csv')
lat_df = pd.read_csv('latency_results.csv')

# Merge to get complexity in latency dataframe
lat_df = lat_df.merge(acc_df[['query_id', 'complexity']], on='query_id', how='left')

# Create figure with subplots
fig = plt.figure(figsize=(16, 12))

# ============================================================================
# CHART 1: Accuracy by Complexity (Bar Chart)
# ============================================================================
ax1 = plt.subplot(2, 3, 1)
complexity_order = ['simple', 'medium', 'complex']
accuracy_by_complexity = []
success_counts = []
total_counts = []

for complexity in complexity_order:
    subset = acc_df[acc_df['complexity'] == complexity]
    acc_rate = subset['semantic_match'].mean()
    accuracy_by_complexity.append(acc_rate * 100)
    success_counts.append(subset['semantic_match'].sum())
    total_counts.append(len(subset))

colors = ['#2ecc71', '#f39c12', '#e74c3c']  # Green, Orange, Red
bars = ax1.bar(complexity_order, accuracy_by_complexity, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

# Add value labels on bars
for i, (bar, count, total) in enumerate(zip(bars, success_counts, total_counts)):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{count}/{total}\n({height:.1f}%)',
             ha='center', va='bottom', fontweight='bold', fontsize=10)

ax1.set_ylabel('Semantic Match Rate (%)', fontweight='bold')
ax1.set_xlabel('Query Complexity', fontweight='bold')
ax1.set_title('Chart 1: Accuracy by Complexity Level', fontweight='bold', fontsize=13)
ax1.set_ylim(0, 110)
ax1.grid(axis='y', alpha=0.3)

# ============================================================================
# CHART 2: Latency Distribution (Box Plot + Violin)
# ============================================================================
ax2 = plt.subplot(2, 3, 2)
lat_by_complexity = [lat_df[lat_df['complexity'] == c]['total_latency_ms'].values 
                      for c in complexity_order]

bp = ax2.boxplot(lat_by_complexity, labels=complexity_order, patch_artist=True,
                  medianprops=dict(color='red', linewidth=2),
                  whiskerprops=dict(linewidth=1.5),
                  capprops=dict(linewidth=1.5))

for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax2.set_ylabel('Total Latency (ms)', fontweight='bold')
ax2.set_xlabel('Query Complexity', fontweight='bold')
ax2.set_title('Chart 2: Latency Distribution by Complexity', fontweight='bold', fontsize=13)
ax2.grid(axis='y', alpha=0.3)

# Add statistics annotation
mean_lat = lat_df['total_latency_ms'].mean()
p95_lat = lat_df['total_latency_ms'].quantile(0.95)
ax2.axhline(mean_lat, color='blue', linestyle='--', alpha=0.5, label=f'Mean: {mean_lat:.0f}ms')
ax2.axhline(p95_lat, color='purple', linestyle='--', alpha=0.5, label=f'P95: {p95_lat:.0f}ms')
ax2.legend(loc='upper right', fontsize=9)

# ============================================================================
# CHART 3: Latency Breakdown Pie Chart
# ============================================================================
ax3 = plt.subplot(2, 3, 3)
avg_llm = lat_df['llm_latency_ms'].mean()
avg_oracle = lat_df['oracle_exe_ms'].mean()
total = avg_llm + avg_oracle

sizes = [avg_llm, avg_oracle]
labels = [f'LLM Generation\n{avg_llm:.0f}ms\n({avg_llm/total*100:.1f}%)',
          f'Oracle Execution\n{avg_oracle:.0f}ms\n({avg_oracle/total*100:.1f}%)']
colors_pie = ['#3498db', '#e74c3c']
explode = (0.05, 0.05)

ax3.pie(sizes, labels=labels, colors=colors_pie, autopct='', explode=explode,
        shadow=True, startangle=90, textprops={'fontweight': 'bold', 'fontsize': 10})
ax3.set_title('Chart 3: Latency Breakdown\n(Average per Query)', fontweight='bold', fontsize=13)

# ============================================================================
# CHART 4: Accuracy vs Latency Scatter
# ============================================================================
ax4 = plt.subplot(2, 3, 4)
colors_scatter = {'simple': '#2ecc71', 'medium': '#f39c12', 'complex': '#e74c3c'}
for complexity in complexity_order:
    subset = acc_df.merge(lat_df[['nl_question', 'total_latency_ms']], 
                          on='nl_question', how='inner')
    subset = subset[subset['complexity'] == complexity]
    ax4.scatter(subset['total_latency_ms'], subset['semantic_match'].astype(int) * 100,
               label=complexity, s=150, alpha=0.6, color=colors_scatter[complexity],
               edgecolors='black', linewidth=1)

ax4.set_xlabel('Total Latency (ms)', fontweight='bold')
ax4.set_ylabel('Semantic Match (True/False)', fontweight='bold')
ax4.set_title('Chart 4: Accuracy vs Latency', fontweight='bold', fontsize=13)
ax4.set_yticks([0, 100])
ax4.set_yticklabels(['Failed (0)', 'Passed (1)'])
ax4.legend(loc='best', fontsize=10)
ax4.grid(True, alpha=0.3)

# ============================================================================
# CHART 5: Success Rate Summary
# ============================================================================
ax5 = plt.subplot(2, 3, 5)
metrics = ['Overall\nSuccess', 'Semantic\nMatch', 'Simple\nAccuracy', 
           'Medium\nAccuracy', 'Complex\nAccuracy']
values = [
    acc_df['ai_success'].mean() * 100,
    acc_df['semantic_match'].mean() * 100,
    acc_df[acc_df['complexity'] == 'simple']['semantic_match'].mean() * 100,
    acc_df[acc_df['complexity'] == 'medium']['semantic_match'].mean() * 100,
    acc_df[acc_df['complexity'] == 'complex']['semantic_match'].mean() * 100
]
metric_colors = ['#95a5a6', '#9b59b6', '#2ecc71', '#f39c12', '#e74c3c']

bars = ax5.barh(metrics, values, color=metric_colors, alpha=0.7, edgecolor='black', linewidth=1.5)
for i, (bar, value) in enumerate(zip(bars, values)):
    ax5.text(value + 1, bar.get_y() + bar.get_height()/2,
            f'{value:.1f}%', va='center', fontweight='bold', fontsize=10)

ax5.set_xlabel('Accuracy (%)', fontweight='bold')
ax5.set_title('Chart 5: Performance Summary', fontweight='bold', fontsize=13)
ax5.set_xlim(0, 120)
ax5.grid(axis='x', alpha=0.3)

# ============================================================================
# CHART 6: Query Count by Complexity
# ============================================================================
ax6 = plt.subplot(2, 3, 6)
complexity_counts = acc_df['complexity'].value_counts().reindex(complexity_order)
passed = []
failed = []
for complexity in complexity_order:
    subset = acc_df[acc_df['complexity'] == complexity]
    passed.append((subset['semantic_match'] == True).sum())
    failed.append((subset['semantic_match'] == False).sum())

x_pos = np.arange(len(complexity_order))
width = 0.35

bars1 = ax6.bar(x_pos - width/2, passed, width, label='Passed', 
               color='#2ecc71', alpha=0.7, edgecolor='black', linewidth=1.5)
bars2 = ax6.bar(x_pos + width/2, failed, width, label='Failed',
               color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=1.5)

ax6.set_ylabel('Number of Queries', fontweight='bold')
ax6.set_xlabel('Complexity Level', fontweight='bold')
ax6.set_title('Chart 6: Query Results Distribution', fontweight='bold', fontsize=13)
ax6.set_xticks(x_pos)
ax6.set_xticklabels(complexity_order)
ax6.legend(loc='upper right', fontsize=10)
ax6.grid(axis='y', alpha=0.3)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=9)

# ============================================================================
# Overall Title and Layout
# ============================================================================
fig.suptitle('Oracle AI SQL Generation: TPC-H Benchmark Evaluation (22 Queries)', 
             fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout(rect=[0, 0, 1, 0.99])

# Save figures
plt.savefig('TPCH_Evaluation_Charts.png', dpi=300, bbox_inches='tight')
print("✅ Saved: TPCH_Evaluation_Charts.png")

# Also save individual charts
fig.clear()

# Chart 1 only
fig1, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(complexity_order, accuracy_by_complexity, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
for i, (bar, count, total) in enumerate(zip(bars, success_counts, total_counts)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{count}/{total}\n({height:.1f}%)',
            ha='center', va='bottom', fontweight='bold', fontsize=11)
ax.set_ylabel('Semantic Match Rate (%)', fontweight='bold', fontsize=12)
ax.set_xlabel('Query Complexity', fontweight='bold', fontsize=12)
ax.set_title('Accuracy by Complexity Level', fontweight='bold', fontsize=14)
ax.set_ylim(0, 110)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('Chart_1_Accuracy_by_Complexity.png', dpi=300, bbox_inches='tight')
print("✅ Saved: Chart_1_Accuracy_by_Complexity.png")

# Chart 3 only 
fig3, ax = plt.subplots(figsize=(8, 6))
sizes = [avg_llm, avg_oracle]
labels = [f'LLM Generation\n{avg_llm:.0f}ms\n({avg_llm/total*100:.1f}%)',
          f'Oracle Execution\n{avg_oracle:.0f}ms\n({avg_oracle/total*100:.1f}%)']
colors_pie = ['#3498db', '#e74c3c']
ax.pie(sizes, labels=labels, colors=colors_pie, autopct='', explode=(0.05, 0.05),
       shadow=True, startangle=90, textprops={'fontweight': 'bold', 'fontsize': 12})
ax.set_title('Latency Breakdown (Average per Query)', fontweight='bold', fontsize=14)
plt.tight_layout()
plt.savefig('Chart_3_Latency_Breakdown.png', dpi=300, bbox_inches='tight')
print("✅ Saved: Chart_3_Latency_Breakdown.png")

print("\n" + "="*60)
print("📊 VISUALIZATION GENERATION COMPLETE")
print("="*60)
print(f"✅ Generated 5 high-resolution charts (300 DPI)")
print(f"\nFiles created:")
print(f"  1. TPCH_Evaluation_Charts.png (6-panel comprehensive)")
print(f"  2. Chart_1_Accuracy_by_Complexity.png")
print(f"  3. Chart_3_Latency_Breakdown.png")
print(f"\nReady for publication! 🎉")
