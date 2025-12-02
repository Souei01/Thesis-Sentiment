"""
Process annotations and split into train/test (70/30) without removing data
Applies data preprocessing while keeping all samples
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from collections import Counter
import re
import unicodedata
from pathlib import Path

print("=" * 80)
print("DATA PROCESSING AND TRAIN/TEST SPLIT")
print("=" * 80)

# Load data
input_file = 'data/annotations/combined_annotations_with_text.csv'
print(f"\n📂 Loading: {input_file}")
df = pd.read_csv(input_file)
print(f"✅ Loaded {len(df)} samples")

# ============================================================================
# STEP 1: CALCULATE CONSENSUS LABELS
# ============================================================================
print(f"\n{'='*80}")
print("STEP 1: CALCULATING CONSENSUS LABELS")
print(f"{'='*80}")

def get_consensus_label(row):
    """Get majority vote from 3 annotators"""
    votes = [row['annotator_1'], row['annotator_2'], row['annotator_3']]
    counter = Counter(votes)
    most_common = counter.most_common(1)[0]
    return most_common[0]

df['label'] = df.apply(get_consensus_label, axis=1)
print(f"✅ Consensus labels calculated")

print(f"\n📊 Label Distribution:")
for label, count in df['label'].value_counts().sort_index().items():
    print(f"   {label:20s}: {count:4d} ({count/len(df)*100:.1f}%)")

# ============================================================================
# STEP 2: DATA PREPROCESSING (NO REMOVAL)
# ============================================================================
print(f"\n{'='*80}")
print("STEP 2: TEXT PREPROCESSING")
print(f"{'='*80}")

def preprocess_text(text):
    """
    Preprocess text with normalization techniques
    Does NOT remove any samples, only cleans the text
    """
    if pd.isna(text) or text == '':
        return text
    
    text = str(text)
    
    # 1. Unicode normalization
    text = unicodedata.normalize('NFKD', text)
    
    # 2. Lowercase
    text = text.lower()
    
    # 3. Fix contractions
    contractions = {
        "won't": "will not", "can't": "cannot", "n't": " not",
        "'re": " are", "'s": " is", "'d": " would",
        "'ll": " will", "'ve": " have", "'m": " am"
    }
    for contraction, expansion in contractions.items():
        text = text.replace(contraction, expansion)
    
    # 4. Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # 5. Strip
    text = text.strip()
    
    return text

print("\nApplying preprocessing...")
print("   - Unicode normalization")
print("   - Lowercase conversion")
print("   - Contraction expansion")
print("   - Whitespace cleaning")

df['feedback'] = df['feedback_text'].apply(preprocess_text)
df['question'] = df['question'].apply(preprocess_text)

print(f"✅ Preprocessing complete")
print(f"   All {len(df)} samples retained")

# ============================================================================
# STEP 3: CREATE LABEL IDs
# ============================================================================
print(f"\n{'='*80}")
print("STEP 3: ENCODING LABELS")
print(f"{'='*80}")

label_dict = {
    'joy': 0,
    'satisfaction': 1,
    'acceptance': 2,
    'boredom': 3,
    'disappointment': 4
}

df['label_id'] = df['label'].map(label_dict)
print(f"✅ Label encoding complete")

# ============================================================================
# STEP 4: SPLIT INTO TRAIN (70%) AND TEST (30%)
# ============================================================================
print(f"\n{'='*80}")
print("STEP 4: TRAIN/TEST SPLIT (70% / 30%)")
print(f"{'='*80}")

# Split with stratification
train_df, test_df = train_test_split(
    df,
    test_size=0.30,
    random_state=42,
    stratify=df['label_id']
)

print(f"\n✅ Split complete:")
print(f"   Training set: {len(train_df)} samples (70%)")
print(f"   Test set:     {len(test_df)} samples (30%)")

# Show distribution
print(f"\n📊 Training Set Distribution:")
for label, count in train_df['label'].value_counts().sort_index().items():
    print(f"   {label:20s}: {count:4d} ({count/len(train_df)*100:.1f}%)")

print(f"\n📊 Test Set Distribution:")
for label, count in test_df['label'].value_counts().sort_index().items():
    print(f"   {label:20s}: {count:4d} ({count/len(test_df)*100:.1f}%)")

# ============================================================================
# STEP 5: PREPARE FINAL FORMAT
# ============================================================================
print(f"\n{'='*80}")
print("STEP 5: PREPARING FINAL FORMAT")
print(f"{'='*80}")

# Select columns for training/testing
columns_to_keep = ['feedback', 'question', 'label', 'label_id']

train_final = train_df[columns_to_keep].copy()
test_final = test_df[columns_to_keep].copy()

# Reset index
train_final = train_final.reset_index(drop=True)
test_final = test_final.reset_index(drop=True)

print(f"✅ Final format prepared")
print(f"   Columns: {list(train_final.columns)}")

# ============================================================================
# STEP 6: SAVE FILES
# ============================================================================
print(f"\n{'='*80}")
print("STEP 6: SAVING FILES")
print(f"{'='*80}")

output_dir = Path('data/annotations')

# Save training data
train_output = output_dir / 'train_data.csv'
train_final.to_csv(train_output, index=False)
print(f"\n✅ Training data saved: {train_output}")
print(f"   Samples: {len(train_final)}")

# Save test data
test_output = output_dir / 'test_data.csv'
test_final.to_csv(test_output, index=False)
print(f"✅ Test data saved: {test_output}")
print(f"   Samples: {len(test_final)}")

# Save full processed data (with all original columns)
full_output = output_dir / 'processed_full.csv'
df[['feedback_id', 'feedback', 'question', 'label', 'label_id', 
    'annotator_1', 'annotator_2', 'annotator_3']].to_csv(full_output, index=False)
print(f"✅ Full processed data saved: {full_output}")
print(f"   Samples: {len(df)}")

# ============================================================================
# STEP 7: STATISTICS
# ============================================================================
print(f"\n{'='*80}")
print("STEP 7: FINAL STATISTICS")
print(f"{'='*80}")

print(f"\n📊 Dataset Summary:")
print(f"   Total samples:     {len(df)}")
print(f"   Training samples:  {len(train_final)} (70%)")
print(f"   Test samples:      {len(test_final)} (30%)")
print(f"   Samples removed:   0 (100% retention)")

print(f"\n📏 Text Length Statistics (Training):")
lengths = train_final['feedback'].str.len()
print(f"   Mean:   {lengths.mean():.1f} characters")
print(f"   Median: {lengths.median():.1f} characters")
print(f"   Min:    {lengths.min()} characters")
print(f"   Max:    {lengths.max()} characters")

print(f"\n📝 Word Count Statistics (Training):")
word_counts = train_final['feedback'].str.split().str.len()
print(f"   Mean:   {word_counts.mean():.1f} words")
print(f"   Median: {word_counts.median():.1f} words")
print(f"   Min:    {word_counts.min()} words")
print(f"   Max:    {word_counts.max()} words")

print(f"\n📋 Sample Data (Training):")
print("-" * 80)
for idx, row in train_final.head(3).iterrows():
    print(f"\n{idx + 1}. Label: {row['label']}")
    print(f"   Question: {row['question'][:60]}...")
    print(f"   Feedback: {row['feedback'][:80]}...")

print("\n" + "=" * 80)
print("✅ PROCESSING COMPLETE!")
print("=" * 80)
print(f"\n💡 Summary:")
print(f"   ✓ All {len(df)} samples retained (no data removed)")
print(f"   ✓ Text preprocessing applied")
print(f"   ✓ Consensus labels calculated from 3 annotators")
print(f"   ✓ Stratified 70/30 train/test split")
print(f"   ✓ Files saved:")
print(f"     - train_data.csv ({len(train_final)} samples)")
print(f"     - test_data.csv ({len(test_final)} samples)")
print(f"     - processed_full.csv ({len(df)} samples with metadata)")
print(f"\n💡 Next step: Use train_data.csv for training and test_data.csv for evaluation")
print("=" * 80)
