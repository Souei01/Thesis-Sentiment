"""
Improved Course Ranking with Statistical Confidence
Uses Wilson Score Interval and Bayesian Average to handle small sample sizes
Based on research: Wilson, E.B. (1927) and Bayesian estimation for ratings
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

print('='*100)
print('IMPROVED COURSE RANKING WITH STATISTICAL CONFIDENCE')
print('='*100)

# Load data
detailed_df = pd.read_csv('results/course_analysis/course_sentiment_detailed.csv')
scores_df = pd.read_csv('results/course_analysis/course_sentiment_scores.csv')

# Constants for statistical adjustments
MINIMUM_FEEDBACK_THRESHOLD = 10  # Courses with < 10 feedback get confidence penalty
GLOBAL_MEAN = scores_df['Average_Sentiment_Score'].mean()
GLOBAL_FEEDBACK_MEAN = scores_df['Feedback_Count'].mean()

print(f'\nGlobal average sentiment: {GLOBAL_MEAN:.3f}')
print(f'Global average feedback count: {GLOBAL_FEEDBACK_MEAN:.1f}')

def calculate_wilson_score(positive, total, confidence=0.95):
    """
    Wilson Score Interval - Used by Reddit, Yelp, etc.
    Provides lower bound of confidence interval for true score
    """
    if total == 0:
        return 0
    
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    phat = positive / total
    
    denominator = 1 + z**2 / total
    numerator = phat + z**2 / (2 * total) - z * np.sqrt((phat * (1 - phat) + z**2 / (4 * total)) / total)
    
    return numerator / denominator

def calculate_bayesian_average(score, count, global_mean, min_count):
    """
    Bayesian Average - Used by IMDB, Metacritic
    Shrinks scores toward global mean based on sample size
    Formula: (C * m + Σx) / (C + n)
    Where: C = confidence constant, m = global mean, n = sample size, Σx = sum of ratings
    """
    C = min_count  # Confidence constant (minimum votes for full weight)
    return (C * global_mean + count * score) / (C + count)

def calculate_confidence_score(score, count, global_mean, global_count):
    """
    Confidence-weighted score combining multiple methods
    """
    # 1. Bayesian average (shrinks toward mean for small samples)
    bayesian = calculate_bayesian_average(score, count, global_mean, MINIMUM_FEEDBACK_THRESHOLD)
    
    # 2. Sample size weight (0 to 1, based on sqrt to avoid over-penalizing)
    size_weight = min(1.0, np.sqrt(count / MINIMUM_FEEDBACK_THRESHOLD))
    
    # 3. Confidence interval adjustment
    # Convert score from -2 to +2 scale to 0 to 1 scale for Wilson score
    normalized_score = (score + 2) / 4  # Now 0 to 1
    positive_prop = (normalized_score + 1) / 2  # Treat as positive proportion
    wilson = calculate_wilson_score(positive_prop * count, count, confidence=0.95)
    
    # Combine methods
    confidence_adjusted = (bayesian * 0.5) + (score * size_weight * 0.5)
    
    return confidence_adjusted, bayesian, size_weight, wilson

# Calculate adjusted scores
adjusted_scores = []

for idx, row in scores_df.iterrows():
    course = row['Course_code']
    subject = row['Subject_Description']
    raw_score = row['Average_Sentiment_Score']
    count = row['Feedback_Count']
    
    confidence_score, bayesian, size_weight, wilson = calculate_confidence_score(
        raw_score, count, GLOBAL_MEAN, GLOBAL_FEEDBACK_MEAN
    )
    
    adjusted_scores.append({
        'Course_code': course,
        'Subject_Description': subject,
        'Raw_Score': raw_score,
        'Feedback_Count': count,
        'Bayesian_Score': bayesian,
        'Size_Weight': size_weight,
        'Confidence_Adjusted_Score': confidence_score,
        'Reliability_Rating': 'High' if count >= MINIMUM_FEEDBACK_THRESHOLD else 
                             'Medium' if count >= 5 else 'Low'
    })

adjusted_df = pd.DataFrame(adjusted_scores)

# Sort by confidence-adjusted score
adjusted_df_sorted = adjusted_df.sort_values('Confidence_Adjusted_Score', ascending=False)

# Save results
output_dir = Path('results/course_analysis')
adjusted_df_sorted.to_csv(output_dir / 'course_rankings_statistically_adjusted.csv', index=False)

print('\n' + '='*100)
print('TOP 15 COURSES (STATISTICALLY ADJUSTED RANKING)')
print('='*100)
print(f'{"Rank":<6} {"Course":<12} {"Subject":<45} {"Raw":<7} {"Adj":<7} {"n":<5} {"Reliability"}')
print('-'*100)

for i, row in adjusted_df_sorted.head(15).iterrows():
    rank = adjusted_df_sorted.index.get_loc(i) + 1
    print(f'{rank:<6} {row["Course_code"]:<12} {row["Subject_Description"][:45]:<45} '
          f'{row["Raw_Score"]:>6.2f}  {row["Confidence_Adjusted_Score"]:>6.2f}  '
          f'{int(row["Feedback_Count"]):<5} {row["Reliability_Rating"]}')

print('\n' + '='*100)
print('BOTTOM 15 COURSES (NEED IMMEDIATE ATTENTION)')
print('='*100)
print(f'{"Rank":<6} {"Course":<12} {"Subject":<45} {"Raw":<7} {"Adj":<7} {"n":<5} {"Reliability"}')
print('-'*100)

bottom_15 = adjusted_df_sorted.tail(15).sort_values('Confidence_Adjusted_Score')
for i, row in bottom_15.iterrows():
    rank = len(adjusted_df_sorted) - adjusted_df_sorted.index.get_loc(i)
    print(f'{rank:<6} {row["Course_code"]:<12} {row["Subject_Description"][:45]:<45} '
          f'{row["Raw_Score"]:>6.2f}  {row["Confidence_Adjusted_Score"]:>6.2f}  '
          f'{int(row["Feedback_Count"]):<5} {row["Reliability_Rating"]}')

# Visualization 1: Comparison of Raw vs Adjusted Scores for Top Courses
print('\nGenerating visualizations...')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# Top courses comparison
top_20 = adjusted_df_sorted.head(20)
x = np.arange(len(top_20))
width = 0.35

ax1.barh(x - width/2, top_20['Raw_Score'], width, label='Raw Score', alpha=0.8, color='lightblue')
ax1.barh(x + width/2, top_20['Confidence_Adjusted_Score'], width, label='Adjusted Score', alpha=0.8, color='darkblue')
ax1.set_yticks(x)
ax1.set_yticklabels([f"{c} (n={int(n)})" for c, n in zip(top_20['Course_code'], top_20['Feedback_Count'])], fontsize=8)
ax1.set_xlabel('Sentiment Score', fontweight='bold')
ax1.set_title('Top 20 Courses: Raw vs Confidence-Adjusted Scores', fontweight='bold')
ax1.legend()
ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
ax1.invert_yaxis()

# Bottom courses comparison
bottom_20 = adjusted_df_sorted.tail(20).sort_values('Confidence_Adjusted_Score')
x = np.arange(len(bottom_20))

ax2.barh(x - width/2, bottom_20['Raw_Score'], width, label='Raw Score', alpha=0.8, color='lightcoral')
ax2.barh(x + width/2, bottom_20['Confidence_Adjusted_Score'], width, label='Adjusted Score', alpha=0.8, color='darkred')
ax2.set_yticks(x)
ax2.set_yticklabels([f"{c} (n={int(n)})" for c, n in zip(bottom_20['Course_code'], bottom_20['Feedback_Count'])], fontsize=8)
ax2.set_xlabel('Sentiment Score', fontweight='bold')
ax2.set_title('Bottom 20 Courses: Raw vs Confidence-Adjusted Scores', fontweight='bold')
ax2.legend()
ax2.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
ax2.invert_yaxis()

plt.tight_layout()
plt.savefig(output_dir / '5_adjusted_vs_raw_scores.png', dpi=300, bbox_inches='tight')
print('✅ Saved: 5_adjusted_vs_raw_scores.png')
plt.close()

# Visualization 2: Reliability vs Score Scatter Plot
fig, ax = plt.subplots(figsize=(12, 8))

colors = {'High': 'green', 'Medium': 'orange', 'Low': 'red'}
for reliability in ['Low', 'Medium', 'High']:
    subset = adjusted_df[adjusted_df['Reliability_Rating'] == reliability]
    ax.scatter(subset['Feedback_Count'], subset['Confidence_Adjusted_Score'], 
              label=f'{reliability} Reliability', alpha=0.6, s=100, c=colors[reliability])

ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Neutral Sentiment')
ax.axvline(x=MINIMUM_FEEDBACK_THRESHOLD, color='blue', linestyle='--', alpha=0.5, 
          label=f'Minimum Sample Size ({MINIMUM_FEEDBACK_THRESHOLD})')
ax.set_xlabel('Feedback Count (Sample Size)', fontweight='bold', fontsize=12)
ax.set_ylabel('Confidence-Adjusted Score', fontweight='bold', fontsize=12)
ax.set_title('Course Reliability: Sample Size vs Sentiment Score', fontweight='bold', fontsize=14)
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / '6_reliability_scatter.png', dpi=300, bbox_inches='tight')
print('✅ Saved: 6_reliability_scatter.png')
plt.close()

# Generate comprehensive report
report_path = output_dir / 'statistically_adjusted_rankings_report.txt'

with open(report_path, 'w', encoding='utf-8') as f:
    f.write('='*100 + '\n')
    f.write('STATISTICALLY ADJUSTED COURSE RANKINGS\n')
    f.write('Addressing Sample Size Bias in Sentiment Analysis\n')
    f.write('='*100 + '\n\n')
    
    f.write('METHODOLOGY\n')
    f.write('-'*100 + '\n')
    f.write('To address the imbalance in feedback counts and prevent courses with 1-2 responses\n')
    f.write('from dominating rankings, we implemented three statistical adjustments:\n\n')
    f.write('1. BAYESIAN AVERAGE (IMDB Method)\n')
    f.write('   - Shrinks scores toward the global mean for courses with few responses\n')
    f.write(f'   - Formula: (C × m + n × x) / (C + n)\n')
    f.write(f'   - Where: C = {MINIMUM_FEEDBACK_THRESHOLD} (confidence constant), m = {GLOBAL_MEAN:.3f} (global mean), n = sample size\n')
    f.write('   - Effect: A course with 1 feedback at +2.0 gets pulled toward global mean\n\n')
    f.write('2. SAMPLE SIZE WEIGHTING\n')
    f.write('   - Weight = sqrt(n / minimum_threshold)\n')
    f.write('   - Courses with < 10 responses receive reduced confidence\n')
    f.write('   - Uses square root to avoid over-penalizing moderate samples\n\n')
    f.write('3. RELIABILITY CLASSIFICATION\n')
    f.write('   - High: ≥ 10 feedback (statistically meaningful)\n')
    f.write('   - Medium: 5-9 feedback (moderate confidence)\n')
    f.write('   - Low: < 5 feedback (insufficient for strong conclusions)\n\n')
    f.write('REFERENCE: Wilson, E.B. (1927). Probable inference, the law of succession,\n')
    f.write('and statistical inference. Journal of the American Statistical Association.\n')
    f.write('='*100 + '\n\n')
    
    f.write('TOP 20 COURSES (HIGH CONFIDENCE)\n')
    f.write('='*100 + '\n')
    f.write(f'{"Rank":<6} {"Course":<12} {"Subject":<50} {"Raw":<7} {"Adj":<7} {"n":<5} {"Reliability"}\n')
    f.write('-'*100 + '\n')
    
    for i, row in adjusted_df_sorted.head(20).iterrows():
        rank = adjusted_df_sorted.index.get_loc(i) + 1
        f.write(f'{rank:<6} {row["Course_code"]:<12} {row["Subject_Description"]:<50} '
                f'{row["Raw_Score"]:>6.2f}  {row["Confidence_Adjusted_Score"]:>6.2f}  '
                f'{int(row["Feedback_Count"]):<5} {row["Reliability_Rating"]}\n')
    
    f.write('\n' + '='*100 + '\n')
    f.write('COURSES NEEDING IMMEDIATE INTERVENTION (HIGH CONFIDENCE)\n')
    f.write('='*100 + '\n')
    f.write(f'{"Rank":<6} {"Course":<12} {"Subject":<50} {"Raw":<7} {"Adj":<7} {"n":<5} {"Reliability"}\n')
    f.write('-'*100 + '\n')
    
    # Focus on high-reliability negative courses
    negative_reliable = adjusted_df_sorted[
        (adjusted_df_sorted['Confidence_Adjusted_Score'] < 0) & 
        (adjusted_df_sorted['Reliability_Rating'] == 'High')
    ].head(15)
    
    for i, row in negative_reliable.iterrows():
        rank = len(adjusted_df_sorted) - adjusted_df_sorted.index.get_loc(i)
        f.write(f'{rank:<6} {row["Course_code"]:<12} {row["Subject_Description"]:<50} '
                f'{row["Raw_Score"]:>6.2f}  {row["Confidence_Adjusted_Score"]:>6.2f}  '
                f'{int(row["Feedback_Count"]):<5} {row["Reliability_Rating"]}\n')
    
    f.write('\n' + '='*100 + '\n')
    f.write('KEY INSIGHTS\n')
    f.write('='*100 + '\n')
    
    high_reliability = adjusted_df[adjusted_df['Reliability_Rating'] == 'High']
    f.write(f'\nCourses with High Reliability (n≥10): {len(high_reliability)}\n')
    f.write(f'Average adjusted score for high-reliability courses: {high_reliability["Confidence_Adjusted_Score"].mean():.3f}\n\n')
    
    top_reliable = adjusted_df_sorted[adjusted_df_sorted['Reliability_Rating'] == 'High'].head(5)
    f.write('Top 5 High-Reliability Courses:\n')
    for _, row in top_reliable.iterrows():
        f.write(f'  - {row["Course_code"]}: {row["Subject_Description"]} '
                f'(Score: {row["Confidence_Adjusted_Score"]:.3f}, n={int(row["Feedback_Count"])})\n')
    
    f.write('\nCourses Requiring Urgent Attention (High Reliability + Negative):\n')
    for _, row in negative_reliable.head(5).iterrows():
        f.write(f'  - {row["Course_code"]}: {row["Subject_Description"]} '
                f'(Score: {row["Confidence_Adjusted_Score"]:.3f}, n={int(row["Feedback_Count"])})\n')

print(f'\n✅ Statistical report saved to: {report_path}')

print('\n' + '='*100)
print('SUMMARY STATISTICS')
print('='*100)
print(f'Total courses: {len(adjusted_df)}')
print(f'High reliability courses (n≥10): {len(adjusted_df[adjusted_df["Reliability_Rating"] == "High"])}')
print(f'Medium reliability courses (5≤n<10): {len(adjusted_df[adjusted_df["Reliability_Rating"] == "Medium"])}')
print(f'Low reliability courses (n<5): {len(adjusted_df[adjusted_df["Reliability_Rating"] == "Low"])}')
print(f'\nBiggest ranking changes:')
changes = adjusted_df.copy()
changes['Raw_Rank'] = changes['Raw_Score'].rank(ascending=False, method='min')
changes['Adjusted_Rank'] = changes['Confidence_Adjusted_Score'].rank(ascending=False, method='min')
changes['Rank_Change'] = changes['Raw_Rank'] - changes['Adjusted_Rank']
biggest_changes = changes.nlargest(5, 'Rank_Change', keep='all')
for _, row in biggest_changes.iterrows():
    print(f"  {row['Course_code']}: Moved {int(row['Rank_Change'])} positions DOWN "
          f"(n={int(row['Feedback_Count'])}, {row['Reliability_Rating']} reliability)")
print('='*100)
