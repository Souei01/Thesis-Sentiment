"""
Prepare Balanced Training Data for Model Training

This script creates a balanced dataset with equal samples per emotion category.
Only includes annotations where all 3 annotators agree (perfect agreement).
"""

import pandas as pd
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def prepare_balanced_training_data():
    """
    Create a balanced training dataset with equal samples per emotion.
    Only uses annotations with perfect agreement (all 3 annotators agree).
    """
    try:
        base_path = 'data/annotations'
        
        print("=" * 100)
        print("PREPARING BALANCED TRAINING DATA")
        print("=" * 100)
        print()
        
        # Load the combined annotations with text
        input_file = f'{base_path}/combined_annotations_with_text.csv'
        print(f"📂 Loading data from: {input_file}")
        df = pd.read_csv(input_file)
        print(f"✅ Loaded {len(df)} annotations")
        print()
        
        # Filter for perfect agreement only (all 3 annotators agree)
        print("🔍 Filtering for perfect agreement (all 3 annotators agree)...")
        df_perfect = df[
            (df['annotator_1'] == df['annotator_2']) & 
            (df['annotator_2'] == df['annotator_3'])
        ].copy()
        
        print(f"✅ Found {len(df_perfect)} annotations with perfect agreement ({len(df_perfect)/len(df)*100:.2f}%)")
        print()
        
        # Use the agreed label (since all 3 are the same)
        df_perfect['emotion'] = df_perfect['annotator_1']
        
        # Remove 'irrelevant' category (too few samples)
        df_perfect = df_perfect[df_perfect['emotion'] != 'irrelevant']
        
        # Show emotion distribution before balancing
        print("📊 Emotion Distribution (Before Balancing):")
        print("=" * 100)
        emotion_counts = df_perfect['emotion'].value_counts()
        for emotion, count in emotion_counts.items():
            percentage = (count / len(df_perfect)) * 100
            print(f"  {emotion.capitalize():15s}: {count:4d} ({percentage:5.2f}%)")
        print()
        
        # Find minimum count to balance all emotions equally
        min_count = emotion_counts.min()
        print(f"🎯 Target samples per emotion: {min_count} (based on minimum class)")
        print()
        
        # Sample equal number from each emotion category
        print("⚖️  Balancing dataset...")
        balanced_dfs = []
        
        for emotion in emotion_counts.index:
            emotion_df = df_perfect[df_perfect['emotion'] == emotion]
            # Randomly sample min_count items from this emotion
            sampled_df = emotion_df.sample(n=min_count, random_state=42)
            balanced_dfs.append(sampled_df)
            print(f"  ✅ {emotion.capitalize():15s}: Sampled {min_count} from {len(emotion_df)}")
        
        # Combine all balanced samples
        df_balanced = pd.concat(balanced_dfs, ignore_index=True)
        
        # Shuffle the dataset
        df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
        
        print()
        print("=" * 100)
        print("📊 Emotion Distribution (After Balancing):")
        print("=" * 100)
        balanced_counts = df_balanced['emotion'].value_counts()
        for emotion, count in balanced_counts.items():
            percentage = (count / len(df_balanced)) * 100
            print(f"  {emotion.capitalize():15s}: {count:4d} ({percentage:5.2f}%)")
        
        print()
        print(f"✅ Total balanced samples: {len(df_balanced)}")
        print()
        
        # Prepare final training data with relevant columns
        df_train = df_balanced[['feedback_text', 'question', 'question_num', 'emotion']].copy()
        
        # Save the balanced training dataset
        output_file = f'{base_path}/training_data_balanced.csv'
        df_train.to_csv(output_file, index=False)
        print(f"💾 Saved balanced training data to: {output_file}")
        print()
        
        # Show sample of the data
        print("=" * 100)
        print("📋 Sample of Balanced Training Data:")
        print("=" * 100)
        for idx, row in df_train.head(10).iterrows():
            feedback_text = row['feedback_text'][:80] + "..." if len(row['feedback_text']) > 80 else row['feedback_text']
            print(f"\n{idx + 1}. [{row['emotion'].upper()}] ({row['question_num']})")
            print(f"   Text: {feedback_text}")
        print()
        
        # Statistics by question
        print("=" * 100)
        print("📊 Distribution by Question:")
        print("=" * 100)
        question_dist = df_train.groupby(['question_num', 'emotion']).size().unstack(fill_value=0)
        print(question_dist)
        print()
        
        # Save summary statistics
        print("=" * 100)
        print("📈 Dataset Statistics:")
        print("=" * 100)
        print(f"  Total samples: {len(df_train)}")
        print(f"  Number of emotions: {df_train['emotion'].nunique()}")
        print(f"  Samples per emotion: {min_count}")
        print(f"  Balance ratio: {df_train['emotion'].value_counts().min() / df_train['emotion'].value_counts().max() * 100:.1f}%")
        print(f"  Perfect agreement: 100% (only using agreed annotations)")
        print()
        
        # Split information
        print("=" * 100)
        print("💡 Recommended Train/Validation/Test Split:")
        print("=" * 100)
        total = len(df_train)
        train_size = int(total * 0.70)
        val_size = int(total * 0.15)
        test_size = total - train_size - val_size
        
        print(f"  Training Set (70%):   {train_size} samples ({train_size/5} per emotion)")
        print(f"  Validation Set (15%): {val_size} samples ({val_size/5} per emotion)")
        print(f"  Test Set (15%):       {test_size} samples ({test_size/5} per emotion)")
        print()
        
        print("=" * 100)
        print("✅ Balanced training data preparation complete!")
        print("=" * 100)
        print()
        print("📋 Next steps:")
        print("   1. Review the training_data_balanced.csv file")
        print("   2. Split into train/val/test sets for model training")
        print("   3. Train your sentiment classification model")
        print()
        
        return df_train
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    prepare_balanced_training_data()
