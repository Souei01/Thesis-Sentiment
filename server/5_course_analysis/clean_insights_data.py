"""
Clean insights CSV - Remove entries without course codes
"""

import pandas as pd
import numpy as np

print('='*100)
print('CLEANING INSIGHTS DATA')
print('='*100)

# Load the insights CSV
df = pd.read_csv('data/annotations/Student Feedback Sentiment Annotation Form - insights.csv')
print(f'\nOriginal total rows: {len(df)}')

# Check all Course_code columns
course_code_cols = ['Course_code', 'Course_code.1', 'Course_code.2', 'Course_code.3']

# Count rows with at least one valid course code
valid_rows = df[course_code_cols].notna().any(axis=1)
print(f'Rows with at least one course code: {valid_rows.sum()}')
print(f'Rows without any course code: {(~valid_rows).sum()}')

# Show some examples of missing course codes
print('\nSample rows WITHOUT course codes:')
missing_df = df[~valid_rows].head(10)
for idx, row in missing_df.iterrows():
    print(f'  Row {idx}: {row["What changes would you recommend to improve this course?"]}')

# Remove rows where ALL course code columns are NaN
df_cleaned = df[valid_rows].copy()

print(f'\n✅ Cleaned data: {len(df_cleaned)} rows')
print(f'❌ Removed: {len(df) - len(df_cleaned)} rows without course codes')

# Save cleaned version
output_path = 'data/annotations/insights_cleaned.csv'
df_cleaned.to_csv(output_path, index=False, encoding='utf-8')
print(f'\n✅ Saved cleaned data to: {output_path}')

# Show course code statistics
print('\n' + '='*100)
print('COURSE CODE STATISTICS')
print('='*100)

for col in course_code_cols:
    unique_codes = df_cleaned[col].dropna().unique()
    print(f'\n{col}: {len(unique_codes)} unique courses')
    if len(unique_codes) > 0:
        print(f'  Examples: {sorted(unique_codes)[:10]}')

print('\n' + '='*100)
