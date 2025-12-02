"""
View CSV Data in Excel-like Format
Display all training data rows and columns
"""

import pandas as pd

# Set pandas to display all rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

print('='*150)
print('TRAINING DATA - ALL 1990 ROWS')
print('='*150)

# Load training data
train_df = pd.read_csv('data/annotations/train_data.csv')
print(f'\nTotal samples: {len(train_df)}')
print(f'Columns: {list(train_df.columns)}\n')

# Display ALL rows using pandas to_string for better formatting
print(train_df.to_string(index=True))

print('\n' + '='*150)
print('EMOTION DISTRIBUTION')
print('='*150)
emotion_dist = train_df['label'].value_counts()
print(emotion_dist)

print('\n' + '='*150)
print(f'Displayed all {len(train_df)} training samples with all columns')
print('='*150)
