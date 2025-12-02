"""
Split training_data_balanced.csv into separate train (70%) and test (30%) files
with data cleaning
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import re
from pathlib import Path

print("=" * 80)
print("TRAIN/TEST DATA SPLITTING WITH DATA CLEANING")
print("=" * 80)

# Load the balanced training data
input_file = 'data/annotations/training_data_balanced.csv'
print(f"\n📂 Loading: {input_file}")
df = pd.read_csv(input_file)
print(f"✅ Loaded {len(df)} samples")
print(f"   Columns: {list(df.columns)}")

# Show label distribution
print(f"\n📊 Original Label Distribution:")
label_counts = df['label'].value_counts()
for label, count in label_counts.items():
    print(f"   {label:20s}: {count:4d} samples ({count/len(df)*100:.1f}%)")

# ============================================================================
# DATA CLEANING
# ============================================================================
print(f"\n🧹 APPLYING DATA CLEANING...")
print("-" * 80)

original_count = len(df)

# 1. Remove duplicates
print("1. Removing duplicate feedback entries...")
before_dups = len(df)
df = df.drop_duplicates(subset=['feedback'], keep='first')
after_dups = len(df)
print(f"   Removed {before_dups - after_dups} duplicates")

# 2. Remove rows with missing or empty feedback
print("2. Removing empty/missing feedback...")
before_empty = len(df)
df = df.dropna(subset=['feedback'])
df = df[df['feedback'].str.strip() != '']
after_empty = len(df)
print(f"   Removed {before_empty - after_empty} empty entries")

# 3. Remove very short feedback (less than 10 characters)
print("3. Removing very short feedback (< 10 characters)...")
before_short = len(df)
df = df[df['feedback'].str.len() >= 10]
after_short = len(df)
print(f"   Removed {before_short - after_short} short entries")

# 4. Remove feedback that is just "none", "n/a", "na", etc.
print("4. Removing non-informative responses...")
before_noise = len(df)
noise_patterns = ['none', 'n/a', 'na', 'nil', 'nothing', 'no comment', 'no response']
pattern = '|'.join([f'^{p}$' for p in noise_patterns])
df = df[~df['feedback'].str.lower().str.strip().str.match(pattern)]
after_noise = len(df)
print(f"   Removed {before_noise - after_noise} non-informative entries")

# 5. Clean text - remove extra whitespace
print("5. Cleaning text formatting...")
df['feedback'] = df['feedback'].str.strip()
df['feedback'] = df['feedback'].str.replace(r'\s+', ' ', regex=True)
if 'question' in df.columns:
    df['question'] = df['question'].str.strip()
    df['question'] = df['question'].str.replace(r'\s+', ' ', regex=True)

# 6. Reset index
df = df.reset_index(drop=True)

print(f"\n✅ Cleaning complete!")
print(f"   Original: {original_count} samples")
print(f"   After cleaning: {len(df)} samples")
print(f"   Removed: {original_count - len(df)} samples ({(original_count - len(df))/original_count*100:.1f}%)")

# Show cleaned label distribution
print(f"\n📊 Cleaned Label Distribution:")
label_counts = df['label'].value_counts()
for label, count in label_counts.items():
    print(f"   {label:20s}: {count:4d} samples ({count/len(df)*100:.1f}%)")

# ============================================================================
# SPLIT INTO TRAIN (70%) AND TEST (30%)
# ============================================================================
print(f"\n✂️  SPLITTING DATA...")
print("-" * 80)

# Create label IDs for stratification
label_dict = {'joy': 0, 'satisfaction': 1, 'acceptance': 2, 'boredom': 3, 'disappointment': 4}
df['label_id'] = df['label'].map(label_dict)

# Split with stratification to maintain class distribution
train_df, test_df = train_test_split(
    df, 
    test_size=0.30,           # 30% for testing
    random_state=42,           # Fixed seed for reproducibility
    stratify=df['label_id']    # Maintain label distribution
)

print(f"✅ Split complete!")
print(f"   Training set: {len(train_df)} samples (70%)")
print(f"   Test set:     {len(test_df)} samples (30%)")

# Show distribution in each set
print(f"\n📊 Training Set Distribution:")
train_counts = train_df['label'].value_counts()
for label, count in train_counts.items():
    print(f"   {label:20s}: {count:4d} samples ({count/len(train_df)*100:.1f}%)")

print(f"\n📊 Test Set Distribution:")
test_counts = test_df['label'].value_counts()
for label, count in test_counts.items():
    print(f"   {label:20s}: {count:4d} samples ({count/len(test_df)*100:.1f}%)")

# ============================================================================
# SAVE TO FILES
# ============================================================================
print(f"\n💾 SAVING FILES...")
print("-" * 80)

# Create output directory if needed
output_dir = Path('data/annotations')
output_dir.mkdir(parents=True, exist_ok=True)

# Save training set
train_output = output_dir / 'training_data_70.csv'
train_df.to_csv(train_output, index=False)
print(f"✅ Saved: {train_output}")
print(f"   {len(train_df)} samples")

# Save test set
test_output = output_dir / 'testing_data_30.csv'
test_df.to_csv(test_output, index=False)
print(f"✅ Saved: {test_output}")
print(f"   {len(test_df)} samples")

# Also save a backup of original cleaned data
cleaned_output = output_dir / 'training_data_balanced_cleaned.csv'
df.to_csv(cleaned_output, index=False)
print(f"✅ Saved: {cleaned_output} (backup of cleaned data)")
print(f"   {len(df)} samples")

print("\n" + "=" * 80)
print("✅ COMPLETE!")
print("=" * 80)
print(f"\n📝 Summary:")
print(f"   - Original data: {original_count} samples")
print(f"   - After cleaning: {len(df)} samples")
print(f"   - Training set (70%): {len(train_df)} samples → training_data_70.csv")
print(f"   - Testing set (30%): {len(test_df)} samples → testing_data_30.csv")
print(f"\n💡 Next steps:")
print(f"   1. Update training scripts to use 'training_data_70.csv'")
print(f"   2. Update testing scripts to use 'testing_data_30.csv'")
print(f"   3. This ensures consistent train/test split across all models")
print("=" * 80)
