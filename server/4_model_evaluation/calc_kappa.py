"""
Cohen's Kappa Inter-Rater Reliability Analysis
"""

import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score

def interpret_kappa(kappa):
    if kappa < 0:
        return "Poor agreement"
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

print("=" * 80)
print("COHEN'S KAPPA INTER-ANNOTATOR AGREEMENT")
print("=" * 80)

# Load data
df = pd.read_csv('data/annotations/combined_annotations_with_text.csv')
print(f"\n📂 Loaded: {len(df)} annotations")

# Calculate Cohen's Kappa for each pair
pairs = [
    ('annotator_1', 'annotator_2', 'Annotator 1 ↔ Annotator 2'),
    ('annotator_1', 'annotator_3', 'Annotator 1 ↔ Annotator 3'),
    ('annotator_2', 'annotator_3', 'Annotator 2 ↔ Annotator 3')
]

print(f"\n📊 PAIRWISE COHEN'S KAPPA")
print("-" * 80)

kappas = []
for ann1, ann2, pair_name in pairs:
    kappa = cohen_kappa_score(df[ann1], df[ann2])
    interpretation = interpret_kappa(kappa)
    agreement = (df[ann1] == df[ann2]).sum()
    agreement_pct = (agreement / len(df)) * 100
    kappas.append(kappa)
    
    print(f"\n{pair_name}")
    print(f"   Cohen's Kappa: {kappa:.4f}")
    print(f"   Interpretation: {interpretation}")
    print(f"   Raw Agreement: {agreement}/{len(df)} ({agreement_pct:.2f}%)")

# Average
avg_kappa = np.mean(kappas)
print(f"\n{'='*80}")
print(f"AVERAGE COHEN'S KAPPA: {avg_kappa:.4f}")
print(f"Interpretation: {interpret_kappa(avg_kappa)}")
print(f"{'='*80}")

# Perfect agreement
perfect = df[(df['annotator_1'] == df['annotator_2']) & 
             (df['annotator_2'] == df['annotator_3'])]
perfect_pct = (len(perfect) / len(df)) * 100

print(f"\n✅ PERFECT AGREEMENT (All 3 annotators agree)")
print(f"   {len(perfect)}/{len(df)} ({perfect_pct:.2f}%)")

print(f"\n📖 INTERPRETATION GUIDE:")
print(f"   0.81-1.00: Almost perfect agreement")
print(f"   0.61-0.80: Substantial agreement")
print(f"   0.41-0.60: Moderate agreement")
print(f"   0.21-0.40: Fair agreement")
print(f"   0.00-0.20: Slight agreement")
print("=" * 80)
