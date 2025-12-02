"""
Cohen's Kappa Inter-Rater Reliability Analysis

This script calculates Cohen's Kappa coefficient for pairwise annotator agreement.
Cohen's Kappa measures agreement between two annotators.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score, confusion_matrix
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def interpret_kappa(kappa):
    """Interpret Cohen's Kappa value"""
    if kappa < 0:
        return "Poor agreement (worse than chance)"
    elif kappa < 0.20:
        return "Slight agreement"
    elif kappa < 0.40:
        return "Fair agreement"
    elif kappa < 0.60:
        return "Moderate agreement"
    elif kappa < 0.80:
        return "Substantial agreement"
    else:
        return "Almost perfect agreement"

def calculate_cohens_kappa(csv_file):
    """
    Calculate Cohen's Kappa for all annotator pairs
    """
    print("=" * 100)
    print("COHEN'S KAPPA INTER-RATER RELIABILITY ANALYSIS")
    print("Student Feedback Emotion Classification")
    print("=" * 100)
    print()
    
    # Load data
    print(f"📂 Loading data from: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"✅ Loaded {len(df)} annotations")
    print()
    
    # Get annotators
    annotators = ['annotator_1', 'annotator_2', 'annotator_3']
    
    # Get emotion categories
    emotions = sorted(set(df['annotator_1'].unique()) | 
                     set(df['annotator_2'].unique()) | 
                     set(df['annotator_3'].unique()))
    
    print(f"📊 Dataset Information:")
    print(f"   • Total annotations: {len(df)}")
    print(f"   • Number of annotators: 3")
    print(f"   • Emotion categories: {', '.join(emotions)}")
    print()
    
    # Calculate Cohen's Kappa for each pair
    pairs = [
        ('annotator_1', 'annotator_2', 'Annotator 1 ↔ Annotator 2'),
        ('annotator_1', 'annotator_3', 'Annotator 1 ↔ Annotator 3'),
        ('annotator_2', 'annotator_3', 'Annotator 2 ↔ Annotator 3')
    ]
    
    results = []
    
    print("=" * 100)
    print("🎯 COHEN'S KAPPA RESULTS (Pairwise Agreement)")
    print("=" * 100)
    print()
    
    for ann1, ann2, pair_name in pairs:
        kappa = cohen_kappa_score(df[ann1], df[ann2])
        interpretation = interpret_kappa(kappa)
        
        # Calculate raw agreement
        agreement = (df[ann1] == df[ann2]).sum()
        agreement_pct = (agreement / len(df)) * 100
        
        results.append({
            'pair': pair_name,
            'kappa': kappa,
            'interpretation': interpretation,
            'agreement': agreement,
            'agreement_pct': agreement_pct
        })
        
        print(f"📊 {pair_name}")
        print(f"   Cohen's Kappa: {kappa:.4f}")
        print(f"   Interpretation: {interpretation}")
        print(f"   Raw Agreement: {agreement}/{len(df)} ({agreement_pct:.2f}%)")
        print()
    
    # Calculate average Cohen's Kappa
    avg_kappa = np.mean([r['kappa'] for r in results])
    avg_agreement = np.mean([r['agreement_pct'] for r in results])
    
    print("=" * 100)
    print("📈 OVERALL SUMMARY")
    print("=" * 100)
    print(f"   Average Cohen's Kappa: {avg_kappa:.4f}")
    print(f"   Average Agreement: {avg_agreement:.2f}%")
    print(f"   Interpretation: {interpret_kappa(avg_kappa)}")
    print()
    
    # Show confusion matrix for each pair
    print("=" * 100)
    print("📊 CONFUSION MATRICES")
    print("=" * 100)
    print()
    
    for ann1, ann2, pair_name in pairs:
        print(f"🔍 {pair_name}")
        print()
        cm = confusion_matrix(df[ann1], df[ann2], labels=emotions)
        
        # Create DataFrame for better display
        cm_df = pd.DataFrame(cm, index=emotions, columns=emotions)
        cm_df.index.name = f'{ann1}'
        cm_df.columns.name = f'{ann2}'
        
        print(cm_df.to_string())
        print()
    
    # Emotion distribution
    print("=" * 100)
    print("📊 EMOTION DISTRIBUTION BY ANNOTATOR")   
    print("=" * 100)
    print()
    
    for annotator in annotators:
        print(f"📋 {annotator.replace('_', ' ').title()}")
        emotion_counts = df[annotator].value_counts().sort_index()
        for emotion, count in emotion_counts.items():
            percentage = (count / len(df)) * 100
            print(f"   {emotion.capitalize():15s}: {count:4d} ({percentage:5.2f}%)")
        print()
    
    # Perfect agreement (all 3 agree)
    perfect_agreement = df[
        (df['annotator_1'] == df['annotator_2']) & 
        (df['annotator_2'] == df['annotator_3'])
    ]
    perfect_pct = (len(perfect_agreement) / len(df)) * 100
    
    print("=" * 100)
    print("✅ PERFECT AGREEMENT (All 3 Annotators)")
    print("=" * 100)
    print(f"   Total: {len(perfect_agreement)}/{len(df)} ({perfect_pct:.2f}%)")
    print()
    
    # Disagreements
    disagreements = df[
        (df['annotator_1'] != df['annotator_2']) | 
        (df['annotator_2'] != df['annotator_3']) | 
        (df['annotator_1'] != df['annotator_3'])
    ]
    
    if len(disagreements) > 0:
        print("=" * 100)
        print(f"⚠️  DISAGREEMENTS ({len(disagreements)} cases)")
        print("=" * 100)
        print()
        print("Sample disagreements:")
        for idx, row in disagreements.head(10).iterrows():
            if 'feedback_text' in df.columns:
                text = row['feedback_text'][:60] + "..." if len(row['feedback_text']) > 60 else row['feedback_text']
                print(f"  {row['feedback_id']}: {text}")
            else:
                print(f"  {row['feedback_id']}")
            print(f"    Annotator 1: {row['annotator_1']:15} | Annotator 2: {row['annotator_2']:15} | Annotator 3: {row['annotator_3']}")
            print()
    
    print("=" * 100)
    print("📖 KAPPA INTERPRETATION GUIDE")
    print("=" * 100)
    print("   < 0.00  : Poor agreement (worse than chance)")
    print("   0.00-0.20: Slight agreement")
    print("   0.21-0.40: Fair agreement")
    print("   0.41-0.60: Moderate agreement")
    print("   0.61-0.80: Substantial agreement")
    print("   0.81-1.00: Almost perfect agreement")
    print()
    
    print("=" * 100)
    print("✅ Analysis Complete!")
    print("=" * 100)
    print()
    
    return results, avg_kappa

if __name__ == "__main__":
    # Check if file argument is provided
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = 'data/annotations/combined_annotations_correct.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: File not found: {csv_file}")
        sys.exit(1)
    
    calculate_cohens_kappa(csv_file)
