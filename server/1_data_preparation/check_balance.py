"""
Count labels per question to check balance
"""

import pandas as pd
from collections import Counter

print("=" * 80)
print("LABEL DISTRIBUTION PER QUESTION")
print("=" * 80)

# Load data
df = pd.read_csv('data/annotations/combined_annotations_with_text.csv')
print(f"\n📂 Total samples: {len(df)}")
print(f"📋 Columns: {list(df.columns)}")

# Calculate consensus label (majority vote)
def get_consensus_label(row):
    votes = [row['annotator_1'], row['annotator_2'], row['annotator_3']]
    counter = Counter(votes)
    most_common = counter.most_common(1)[0]
    return most_common[0]

print(f"\n⏳ Calculating consensus labels...")
df['label'] = df.apply(get_consensus_label, axis=1)
print(f"✅ Done")

# Overall label distribution
print(f"\n📊 Overall Label Distribution:")
overall_counts = df['label'].value_counts().sort_index()
for label, count in overall_counts.items():
    print(f"   {label:20s}: {count:4d} samples ({count/len(df)*100:.1f}%)")

# Check if 'question' column exists
if 'question' in df.columns:
    print(f"\n{'='*80}")
    print("LABEL DISTRIBUTION BY QUESTION")
    print(f"{'='*80}")
    
    # Get unique questions
    questions = df['question'].unique()
    print(f"\n📋 Found {len(questions)} unique questions")
    
    # Count labels per question
    for i, question in enumerate(questions, 1):
        print(f"\n{'─'*80}")
        print(f"Question {i}: {question}")
        print(f"{'─'*80}")
        
        question_df = df[df['question'] == question]
        label_counts = question_df['label'].value_counts().sort_index()
        
        print(f"Total responses: {len(question_df)}")
        print(f"\nLabel breakdown:")
        for label, count in label_counts.items():
            print(f"   {label:20s}: {count:4d} ({count/len(question_df)*100:.1f}%)")
        
        # Check if balanced
        if len(label_counts) == 5:
            min_count = label_counts.min()
            max_count = label_counts.max()
            variance = max_count - min_count
            if variance == 0:
                print(f"   ✅ PERFECTLY BALANCED")
            elif variance <= 5:
                print(f"   ✅ BALANCED (variance: {variance})")
            else:
                print(f"   ⚠️  IMBALANCED (variance: {variance})")
                print(f"      Target per emotion: 140")
                print(f"      Current range: {min_count} - {max_count}")
        else:
            missing = 5 - len(label_counts)
            print(f"   ⚠️  MISSING {missing} emotion(s)")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    balance_summary = []
    for question in questions:
        question_df = df[df['question'] == question]
        label_counts = question_df['label'].value_counts()
        variance = label_counts.max() - label_counts.min() if len(label_counts) > 0 else 0
        balance_summary.append({
            'question': question[:50],
            'total': len(question_df),
            'emotions': len(label_counts),
            'variance': variance,
            'min': label_counts.min(),
            'max': label_counts.max()
        })
    
    summary_df = pd.DataFrame(balance_summary)
    print(f"\n📊 Balance Statistics:")
    print(f"   Total questions: {len(questions)}")
    print(f"   Questions with all 5 emotions: {len(summary_df[summary_df['emotions'] == 5])}/{len(questions)}")
    print(f"   Average samples per question: {summary_df['total'].mean():.0f}")
    print(f"   Average variance: {summary_df['variance'].mean():.1f}")
    print(f"   Max variance: {summary_df['variance'].max():.0f}")
    print(f"   Min variance: {summary_df['variance'].min():.0f}")
    
    print(f"\n🎯 Target: 2800 total samples")
    print(f"   - 4 questions × 700 samples each")
    print(f"   - Each question: 5 emotions × 140 samples")
    
    print(f"\n📈 Current vs Target:")
    print(f"   Current total: {len(df)}")
    print(f"   Target total: 2800")
    print(f"   Difference: {2800 - len(df)} samples needed")
    
else:
    print(f"\n⚠️  No 'question' column found in the dataset")

print("\n" + "=" * 80)
