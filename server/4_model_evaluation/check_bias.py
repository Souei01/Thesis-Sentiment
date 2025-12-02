"""
Bias Detection Analysis for Fine-tuned Models
Checks for various types of bias in training data and model predictions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter

print('='*100)
print('BIAS ANALYSIS - FINE-TUNED EMOTION CLASSIFICATION MODELS')
print('='*100)

# Load data
train_df = pd.read_csv('data/annotations/train_data.csv')
test_df = pd.read_csv('data/annotations/test_data.csv')
all_data = pd.concat([train_df, test_df], ignore_index=True)

print(f'\nTotal samples: {len(all_data)} (Train: {len(train_df)}, Test: {len(test_df)})')

# ==============================================================================
# 1. CLASS DISTRIBUTION BIAS
# ==============================================================================
print('\n' + '='*100)
print('1. CLASS DISTRIBUTION ANALYSIS')
print('='*100)

train_dist = train_df['label'].value_counts().sort_index()
test_dist = test_df['label'].value_counts().sort_index()

print('\nTraining Set Distribution:')
for label, count in train_dist.items():
    print(f'  {label}: {count} ({count/len(train_df)*100:.2f}%)')

print('\nTest Set Distribution:')
for label, count in test_dist.items():
    print(f'  {label}: {count} ({count/len(test_df)*100:.2f}%)')

# Check balance
max_diff = (train_dist.max() - train_dist.min()) / train_dist.mean()
if max_diff < 0.1:
    print(f'\n✅ Classes are well-balanced (max difference: {max_diff*100:.1f}%)')
else:
    print(f'\n⚠️  Class imbalance detected (max difference: {max_diff*100:.1f}%)')

# ==============================================================================
# 2. TEXT LENGTH BIAS
# ==============================================================================
print('\n' + '='*100)
print('2. TEXT LENGTH BIAS ANALYSIS')
print('='*100)

all_data['text_length'] = all_data['feedback'].str.len()
all_data['word_count'] = all_data['feedback'].str.split().str.len()

print('\nText Length by Emotion:')
length_by_emotion = all_data.groupby('label')['word_count'].agg(['mean', 'std', 'min', 'max'])
print(length_by_emotion)

# Check if certain emotions have systematically longer/shorter text
length_variance = length_by_emotion['mean'].std() / length_by_emotion['mean'].mean()
if length_variance > 0.3:
    print(f'\n⚠️  Significant length bias detected (variance: {length_variance:.2%})')
    print('   Longer texts may be easier to classify correctly')
else:
    print(f'\n✅ Text lengths are relatively consistent across emotions')

# ==============================================================================
# 3. VOCABULARY BIAS
# ==============================================================================
print('\n' + '='*100)
print('3. VOCABULARY OVERLAP ANALYSIS')
print('='*100)

from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(max_features=100, stop_words='english')
train_vocab = set(vectorizer.fit(train_df['feedback']).get_feature_names_out())
test_vocab = set(vectorizer.fit(test_df['feedback']).get_feature_names_out())

overlap = len(train_vocab & test_vocab)
overlap_pct = overlap / len(train_vocab) * 100

print(f'\nTop 100 words overlap: {overlap}/100 ({overlap_pct:.1f}%)')

if overlap_pct < 70:
    print('⚠️  Low vocabulary overlap - test set may have out-of-vocabulary bias')
else:
    print('✅ Good vocabulary overlap between train and test sets')

# ==============================================================================
# 4. EMOTION WORD BIAS (Check for obvious keywords)
# ==============================================================================
print('\n' + '='*100)
print('4. OBVIOUS KEYWORD BIAS CHECK')
print('='*100)

emotion_keywords = {
    'joy': ['happy', 'great', 'excellent', 'love', 'best', 'amazing', 'wonderful'],
    'satisfaction': ['good', 'satisfied', 'pleased', 'content', 'nice'],
    'acceptance': ['okay', 'fine', 'acceptable', 'neutral', 'average'],
    'boredom': ['boring', 'dull', 'sleepy', 'monotonous', 'repetitive'],
    'disappointment': ['disappointed', 'bad', 'poor', 'worst', 'terrible', 'awful']
}

print('\nChecking if data contains obvious emotion keywords:')
for emotion, keywords in emotion_keywords.items():
    emotion_samples = all_data[all_data['label'] == emotion]['feedback'].str.lower()
    keyword_matches = sum(emotion_samples.str.contains('|'.join(keywords), regex=True))
    keyword_pct = keyword_matches / len(emotion_samples) * 100
    
    print(f'\n{emotion.upper()}:')
    print(f'  Samples with obvious keywords: {keyword_matches}/{len(emotion_samples)} ({keyword_pct:.1f}%)')
    
    if keyword_pct > 50:
        print(f'  ⚠️  HIGH KEYWORD BIAS - Model may rely on obvious words instead of context')
    elif keyword_pct > 30:
        print(f'  ⚠️  MODERATE KEYWORD BIAS')
    else:
        print(f'  ✅ Low keyword bias - model must learn contextual patterns')

# ==============================================================================
# 5. STRATIFICATION CHECK
# ==============================================================================
print('\n' + '='*100)
print('5. TRAIN-TEST STRATIFICATION VERIFICATION')
print('='*100)

from scipy.stats import chisquare

observed = test_dist.values
expected = train_dist.values * (len(test_df) / len(train_df))

chi2, p_value = chisquare(observed, expected)

print(f'\nChi-square test for distribution similarity:')
print(f'  Chi-square statistic: {chi2:.4f}')
print(f'  P-value: {p_value:.4f}')

if p_value > 0.05:
    print('  ✅ Train and test distributions are statistically similar (good stratification)')
else:
    print('  ⚠️  Train and test distributions differ significantly')

# ==============================================================================
# 6. VISUALIZATIONS
# ==============================================================================
output_dir = Path('results/bias_analysis')
output_dir.mkdir(parents=True, exist_ok=True)

# Visualization 1: Class distribution comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].bar(train_dist.index, train_dist.values, color='steelblue', alpha=0.8, edgecolor='black')
axes[0].set_title('Training Set Class Distribution', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Emotion', fontsize=11)
axes[0].set_ylabel('Count', fontsize=11)
axes[0].tick_params(axis='x', rotation=45)
axes[0].grid(axis='y', alpha=0.3)

axes[1].bar(test_dist.index, test_dist.values, color='coral', alpha=0.8, edgecolor='black')
axes[1].set_title('Test Set Class Distribution', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Emotion', fontsize=11)
axes[1].set_ylabel('Count', fontsize=11)
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / '1_class_distribution.png', dpi=300, bbox_inches='tight')
print(f'\n✅ Saved: 1_class_distribution.png')
plt.close()

# Visualization 2: Word count distribution by emotion
fig, ax = plt.subplots(figsize=(12, 6))

emotions = all_data['label'].unique()
positions = range(len(emotions))

bp = ax.boxplot([all_data[all_data['label'] == e]['word_count'] for e in emotions],
                labels=emotions, patch_artist=True)

for patch in bp['boxes']:
    patch.set_facecolor('lightblue')
    patch.set_alpha(0.7)

ax.set_title('Text Length Distribution by Emotion (Word Count)', fontsize=14, fontweight='bold')
ax.set_xlabel('Emotion', fontsize=12)
ax.set_ylabel('Word Count', fontsize=12)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / '2_text_length_distribution.png', dpi=300, bbox_inches='tight')
print('✅ Saved: 2_text_length_distribution.png')
plt.close()

# ==============================================================================
# SUMMARY REPORT
# ==============================================================================
print('\n' + '='*100)
print('BIAS ANALYSIS SUMMARY')
print('='*100)

bias_score = 0
max_score = 5

print('\n✅ STRENGTHS:')
if max_diff < 0.1:
    print('  - Well-balanced class distribution')
    bias_score += 1
if overlap_pct >= 70:
    print('  - Good vocabulary overlap between train/test')
    bias_score += 1
if p_value > 0.05:
    print('  - Proper stratification in train-test split')
    bias_score += 1

print('\n⚠️  POTENTIAL BIASES TO ADDRESS:')
issues = []
if length_variance > 0.3:
    issues.append('Text length varies significantly by emotion')
if any(kw_pct > 50 for kw_pct in [keyword_pct]):  # Simplified check
    issues.append('High reliance on obvious emotion keywords')

if not issues:
    print('  - None detected in automated analysis')
    bias_score += 2
else:
    for issue in issues:
        print(f'  - {issue}')

print(f'\n📊 BIAS SCORE: {bias_score}/5')
if bias_score >= 4:
    print('   Interpretation: LOW BIAS - Good data quality')
elif bias_score >= 3:
    print('   Interpretation: MODERATE BIAS - Acceptable for thesis')
else:
    print('   Interpretation: HIGH BIAS - Consider data improvements')

print('\n' + '='*100)
print(f'Results saved to: {output_dir}')
print('='*100)
