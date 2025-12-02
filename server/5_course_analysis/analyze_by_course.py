"""
Course-Specific Sentiment Analysis
Analyzes sentiment distribution for each course/subject
Addresses thesis requirement: "Include course-specific analysis to identify which subjects 
receive the most positive or negative feedback"
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Load the insights CSV
print('='*100)
print('COURSE-SPECIFIC SENTIMENT ANALYSIS')
print('='*100)

df = pd.read_csv('data/annotations/insights_cleaned.csv')
print(f'\nTotal rows: {len(df)}')

# Get actual column names
all_cols = list(df.columns)
print(f'Total columns: {len(all_cols)}')

# Find feedback and label columns dynamically
feedback_cols = [col for col in all_cols if 'what' in col.lower() or 'comment' in col.lower()]
label_cols = [col for col in all_cols if col.startswith('Label')]
course_cols = [col for col in all_cols if col.startswith('Course_code')]
subject_cols = [col for col in all_cols if col.startswith('Subject_Description')]

print(f'\nFound {len(feedback_cols)} feedback columns')
print(f'Found {len(label_cols)} label columns')
print(f'Found {len(course_cols)} course code columns')

# Combine all feedback from all question types
feedback_data = []

for i in range(len(feedback_cols)):
    fb_col = feedback_cols[i]
    lbl_col = label_cols[i] if i < len(label_cols) else None
    crs_col = course_cols[i] if i < len(course_cols) else course_cols[0]
    sbj_col = subject_cols[i] if i < len(subject_cols) else subject_cols[0]
    
    if lbl_col is None:
        continue
    
    print(f'\nProcessing: {fb_col[:50]}...')
    
    temp_df = df[[crs_col, sbj_col, fb_col, lbl_col]].copy()
    temp_df.columns = ['Course_code', 'Subject_Description', 'Feedback', 'Label']
    temp_df = temp_df.dropna(subset=['Course_code', 'Feedback', 'Label'])
    
    print(f'  Valid entries: {len(temp_df)}')
    feedback_data.append(temp_df)

# Combine all feedback
all_feedback = pd.concat(feedback_data, ignore_index=True)
all_feedback = all_feedback.dropna(subset=['Course_code', 'Label'])

print(f'\nTotal feedback entries: {len(all_feedback)}')
print(f'Unique courses: {all_feedback["Course_code"].nunique()}')

# Create results directory
results_dir = Path('results/course_analysis')
results_dir.mkdir(parents=True, exist_ok=True)

# ============================================================================
# 1. OVERALL SENTIMENT BY COURSE
# ============================================================================
course_sentiment = all_feedback.groupby(['Course_code', 'Subject_Description', 'Label']).size().reset_index(name='Count')
course_totals = all_feedback.groupby(['Course_code', 'Subject_Description']).size().reset_index(name='Total')

# Calculate percentages
course_sentiment = course_sentiment.merge(course_totals, on=['Course_code', 'Subject_Description'])
course_sentiment['Percentage'] = (course_sentiment['Count'] / course_sentiment['Total'] * 100).round(2)

# Save detailed course sentiment
course_sentiment.to_csv(results_dir / 'course_sentiment_detailed.csv', index=False)
print(f'\n✅ Saved: {results_dir}/course_sentiment_detailed.csv')

# ============================================================================
# 2. SENTIMENT SCORE BY COURSE (Weighted)
# ============================================================================
# Assign sentiment weights: Joy=2, Satisfaction=1, Acceptance=0, Boredom=-1, Disappointment=-2
sentiment_weights = {
    'Joy': 2,
    'Satisfaction': 1,
    'Acceptance': 0,
    'Boredom': -1,
    'Disappointment': -2
}

all_feedback['Sentiment_Weight'] = all_feedback['Label'].map(sentiment_weights)
course_scores = all_feedback.groupby(['Course_code', 'Subject_Description']).agg({
    'Sentiment_Weight': 'mean',
    'Label': 'count'
}).reset_index()
course_scores.columns = ['Course_code', 'Subject_Description', 'Average_Sentiment_Score', 'Feedback_Count']
course_scores = course_scores.sort_values('Average_Sentiment_Score', ascending=False)
course_scores.to_csv(results_dir / 'course_sentiment_scores.csv', index=False)

print(f'✅ Saved: {results_dir}/course_sentiment_scores.csv')

# ============================================================================
# 3. TOP 10 MOST POSITIVE COURSES
# ============================================================================
top_positive = course_scores.head(10)
print('\n' + '='*100)
print('TOP 10 MOST POSITIVE COURSES')
print('='*100)
for idx, row in top_positive.iterrows():
    print(f"{row['Course_code']:10} - {row['Subject_Description'][:50]:50} | Score: {row['Average_Sentiment_Score']:+.3f} | n={int(row['Feedback_Count'])}")

# ============================================================================
# 4. TOP 10 MOST NEGATIVE COURSES
# ============================================================================
top_negative = course_scores.tail(10).sort_values('Average_Sentiment_Score')
print('\n' + '='*100)
print('TOP 10 MOST NEGATIVE COURSES (Need Improvement)')
print('='*100)
for idx, row in top_negative.iterrows():
    print(f"{row['Course_code']:10} - {row['Subject_Description'][:50]:50} | Score: {row['Average_Sentiment_Score']:+.3f} | n={int(row['Feedback_Count'])}")

# ============================================================================
# 5. VISUALIZATIONS
# ============================================================================

# Visualization 1: Top 15 Courses by Sentiment Score
fig, ax = plt.subplots(figsize=(14, 8))
top_courses = course_scores.head(15)
colors = top_courses['Average_Sentiment_Score'].apply(
    lambda x: '#2ecc71' if x > 0.5 else '#3498db' if x > 0 else '#e74c3c'
)
bars = ax.barh(range(len(top_courses)), top_courses['Average_Sentiment_Score'], color=colors)
ax.set_yticks(range(len(top_courses)))
ax.set_yticklabels([f"{row['Course_code']} - {row['Subject_Description'][:35]}" 
                     for _, row in top_courses.iterrows()], fontsize=9)
ax.set_xlabel('Average Sentiment Score', fontweight='bold', fontsize=11)
ax.set_title('Top 15 Courses by Average Sentiment Score', fontweight='bold', fontsize=14, pad=20)
ax.axvline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(results_dir / '1_top_courses_sentiment.png', dpi=300, bbox_inches='tight')
print(f'\n✅ Saved: {results_dir}/1_top_courses_sentiment.png')
plt.close()

# Visualization 2: Bottom 15 Courses (Need Improvement)
fig, ax = plt.subplots(figsize=(14, 8))
bottom_courses = course_scores.tail(15).sort_values('Average_Sentiment_Score', ascending=True)
colors = bottom_courses['Average_Sentiment_Score'].apply(
    lambda x: '#e74c3c' if x < -0.5 else '#e67e22' if x < 0 else '#f39c12'
)
bars = ax.barh(range(len(bottom_courses)), bottom_courses['Average_Sentiment_Score'], color=colors)
ax.set_yticks(range(len(bottom_courses)))
ax.set_yticklabels([f"{row['Course_code']} - {row['Subject_Description'][:35]}" 
                     for _, row in bottom_courses.iterrows()], fontsize=9)
ax.set_xlabel('Average Sentiment Score', fontweight='bold', fontsize=11)
ax.set_title('Bottom 15 Courses by Sentiment (Requiring Attention)', fontweight='bold', fontsize=14, pad=20)
ax.axvline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(results_dir / '2_bottom_courses_sentiment.png', dpi=300, bbox_inches='tight')
print(f'✅ Saved: {results_dir}/2_bottom_courses_sentiment.png')
plt.close()

# Visualization 3: Sentiment Distribution for Specific Courses (CC 100, CC 103, CC 104)
specific_courses = ['CC 100', 'CC 103', 'CC 104', 'CC 105', 'IT 131', 'IT 135']
specific_data = all_feedback[all_feedback['Course_code'].isin(specific_courses)]

fig, ax = plt.subplots(figsize=(14, 8))
sentiment_by_course = specific_data.groupby(['Course_code', 'Label']).size().unstack(fill_value=0)
sentiment_by_course_pct = sentiment_by_course.div(sentiment_by_course.sum(axis=1), axis=0) * 100

sentiment_by_course_pct.plot(kind='bar', stacked=True, ax=ax, 
                              color=['#2ecc71', '#3498db', '#f39c12', '#e67e22', '#e74c3c'])
ax.set_xlabel('Course Code', fontweight='bold', fontsize=11)
ax.set_ylabel('Percentage (%)', fontweight='bold', fontsize=11)
ax.set_title('Sentiment Distribution for Key Courses', fontweight='bold', fontsize=14, pad=20)
ax.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
plt.tight_layout()
plt.savefig(results_dir / '3_key_courses_sentiment_distribution.png', dpi=300, bbox_inches='tight')
print(f'✅ Saved: {results_dir}/3_key_courses_sentiment_distribution.png')
plt.close()

# Visualization 4: Heatmap of Sentiment by Course
pivot_data = all_feedback.groupby(['Course_code', 'Label']).size().unstack(fill_value=0)
pivot_data_pct = pivot_data.div(pivot_data.sum(axis=1), axis=0) * 100

# Select top 20 courses by feedback count
top_20_courses = course_totals.nlargest(20, 'Total')['Course_code']
pivot_subset = pivot_data_pct.loc[pivot_data_pct.index.isin(top_20_courses)]

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(pivot_subset, annot=True, fmt='.1f', cmap='RdYlGn', cbar_kws={'label': 'Percentage (%)'}, ax=ax)
ax.set_xlabel('Sentiment', fontweight='bold', fontsize=11)
ax.set_ylabel('Course Code', fontweight='bold', fontsize=11)
ax.set_title('Sentiment Heatmap for Top 20 Courses by Feedback Count', fontweight='bold', fontsize=14, pad=20)
plt.tight_layout()
plt.savefig(results_dir / '4_sentiment_heatmap.png', dpi=300, bbox_inches='tight')
print(f'✅ Saved: {results_dir}/4_sentiment_heatmap.png')
plt.close()

print('\n' + '='*100)
print('✅ COURSE-SPECIFIC ANALYSIS COMPLETE')
print('='*100)
print(f'\nAll results saved to: {results_dir}/')
print('\nGenerated files:')
print('  1. course_sentiment_detailed.csv - Full breakdown by course and sentiment')
print('  2. course_sentiment_scores.csv - Weighted sentiment scores for all courses')
print('  3. 1_top_courses_sentiment.png - Top 15 performing courses')
print('  4. 2_bottom_courses_sentiment.png - Bottom 15 courses needing attention')
print('  5. 3_key_courses_sentiment_distribution.png - Sentiment breakdown for key courses')
print('  6. 4_sentiment_heatmap.png - Heatmap for top 20 courses')
print('\n' + '='*100)
