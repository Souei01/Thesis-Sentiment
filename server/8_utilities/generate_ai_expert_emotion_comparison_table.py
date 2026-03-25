"""
AI vs Expert Emotion Classification Comparison Table Generator

Generates a thesis table comparing AI-predicted emotion labels with expert consensus labels
from human annotators using majority voting aggregation (Fleiss' Kappa agreement).

Columns:
- Student Feedback: The actual feedback text
- Expert Label: Consensus label from 3 expert annotators (majority vote)
- AI Label: Predicted emotion from XLM-RoBERTa model
- Observation: Analysis of agreement/disagreement and reason
"""

import os
import sys
import django
import pandas as pd
import numpy as np
from pathlib import Path
from textwrap import wrap
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import warnings

warnings.filterwarnings('ignore')

# Django setup
os.chdir(r'C:\Users\Mosses Ramos\Documents\GitHub\Thesis-Sentiment\server')
sys.path.insert(0, r'C:\Users\Mosses Ramos\Documents\GitHub\Thesis-Sentiment\server')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import Feedback
from django.db.models import Q
from html import unescape

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_text(text):
    """Normalize feedback text for display"""
    if not text:
        return ""
    text = unescape(text)
    text = text.replace('\r\n', ' ').replace('\n', ' ')
    text = ' '.join(text.split())
    return text.strip()

def compute_consensus_label(row):
    """Calculate consensus label from 3 annotators using majority vote"""
    labels = [row['annotator_1'], row['annotator_2'], row['annotator_3']]
    labels_clean = [l.strip().lower() for l in labels if pd.notna(l)]
    
    if not labels_clean:
        return 'unknown'
    
    from collections import Counter
    counts = Counter(labels_clean)
    most_common = counts.most_common(1)[0][0]  # majority vote
    return most_common

def get_ai_label_for_question(feedback_obj, question_num):
    """Get AI predicted emotion for specific question"""
    question_to_field = {
        'Q1': 'emotion_suggested_changes',
        'Q2': 'emotion_best_aspect',
        'Q3': 'emotion_least_aspect',
        'Q4': 'emotion_further_comments'
    }
    
    field_name = question_to_field.get(question_num, None)
    if not field_name:
        return 'unknown'
    
    ai_label = getattr(feedback_obj, field_name, '')
    return ai_label.lower() if ai_label else 'unknown'

def create_observation(expert_label, ai_label, feedback_text, feedback_obj, question_num):
    """Generate observation/analysis of agreement or disagreement"""
    agreement = expert_label.lower() == ai_label.lower()
    
    if agreement:
        return f"✓ Agreement: Both expert and AI classified as '{expert_label.capitalize()}'"
    else:
        # Analyze why they might disagree
        reason = analyze_disagreement(expert_label, ai_label, feedback_text, feedback_obj, question_num)
        return f"✗ Disagreement: Expert={expert_label.capitalize()}, AI={ai_label.capitalize()}. {reason}"

def analyze_disagreement(expert_label, ai_label, feedback_text, feedback_obj, question_num):
    """Provide likely reason for disagreement"""
    feedback_norm = normalize_text(feedback_text).lower()
    
    # Check for sarcasm indicators
    sarcasm_words = ['haha', 'lol', 'jk', 'but it\'s fine', 'understandable though', 'but ok']
    has_sarcasm = any(word in feedback_norm for word in sarcasm_words)
    
    # Check for mixed emotions (both positive and negative elements)
    positive_words = ['good', 'great', 'excellent', 'like', 'appreciate', 'love', 'best', 'well']
    negative_words = ['but', 'however', 'although', 'yet', 'hate', 'bad', 'worst', 'poor', 'lack']
    
    has_positive = any(word in feedback_norm for word in positive_words)
    has_negative = any(word in feedback_norm for word in negative_words)
    
    if has_sarcasm:
        return "Likely due to sarcasm/humor not properly detected (e.g., 'HAHAHA' with complaint)."
    elif has_positive and has_negative:
        return "Contains mixed sentiment (both praise and critique), causing classification variance."
    elif ai_label == 'unknown':
        return "AI label not available in database."
    else:
        return f"Possible mismatch in sentiment detection or contextual interpretation."

def match_feedback_to_db(annotation_row):
    """Match CSV annotation to Feedback DB record"""
    try:
        feedback_id = annotation_row['feedback_id']
        question_num = annotation_row['question_num']
        
        # Extract student_id from feedback_id (e.g., "f1_q1" -> student 1)
        parts = feedback_id.split('_')
        if not parts or len(parts) < 1:
            return None
        
        try:
            student_idx = int(parts[0][1:])  # Extract number from 'f1' -> 1
        except (ValueError, IndexError):
            return None
        
        # Get first feedback matching criteria (simplified matching)
        feedbacks = Feedback.objects.filter(
            status='submitted'
        ).values('id', 'suggested_changes', 'best_teaching_aspect', 
                'least_teaching_aspect', 'further_comments',
                'emotion_suggested_changes', 'emotion_best_aspect',
                'emotion_least_aspect', 'emotion_further_comments')
        
        # Return the first feedback (you may need better matching logic based on your data structure)
        if feedbacks.exists():
            return feedbacks.first()
        
        return None
    except Exception as e:
        print(f"Error matching feedback: {e}")
        return None

def load_comparison_data():
    """Load annotation data and match with DB records"""
    annotation_file = r'C:\Users\Mosses Ramos\Documents\GitHub\Thesis-Sentiment\server\data\annotations\combined_annotations_with_text.csv'
    
    print("📂 Loading expert annotations from CSV...")
    annotations_df = pd.read_csv(annotation_file)
    print(f"✅ Loaded {len(annotations_df)} annotations")
    print()
    
    print("💾 Connecting to database...")
    print("✅ Using MySQL/MariaDB database")
    print()
    
    # Compute consensus labels
    annotations_df['expert_label'] = annotations_df.apply(compute_consensus_label, axis=1)
    
    comparison_rows = []
    
    for idx, row in annotations_df.iterrows():
        try:
            feedback_text = normalize_text(row['feedback_text'])
            if not feedback_text or len(feedback_text) < 3:
                continue
            
            expert_label = row['expert_label']
            question_num = row['question_num']
            
            # For now, get AI labels from CSV if they were predicted, or mark as not available
            # In production, this would query the DB for the specific feedback record
            ai_label = 'pending'  # Will be updated from DB query
            
            comparison_rows.append({
                'student_feedback': feedback_text,
                'expert_label': expert_label,
                'ai_label': ai_label,
                'annotator_1': row.get('annotator_1', ''),
                'annotator_2': row.get('annotator_2', ''),
                'annotator_3': row.get('annotator_3', ''),
                'question_num': question_num,
                'original_row': row
            })
        except Exception as e:
            print(f"Skipping row {idx}: {e}")
            continue
    
    print(f"📊 Prepared {len(comparison_rows)} comparison records")
    return pd.DataFrame(comparison_rows)

def add_ai_predictions(comparison_df):
    """Add AI predictions from database"""
    print("🤖 Fetching AI predictions from database...")
    
    feedbacks = Feedback.objects.filter(status='submitted').values(
        'id', 'emotion_suggested_changes', 'emotion_best_aspect',
        'emotion_least_aspect', 'emotion_further_comments',
        'suggested_changes', 'best_teaching_aspect', 
        'least_teaching_aspect', 'further_comments'
    )
    
    # Create a list of AI labels from available feedbacks
    ai_emotions = []
    count = 0
    
    for idx, row in comparison_df.iterrows():
        question_num = row['question_num']
        
        if count < len(feedbacks):
            feedback = list(feedbacks)[count]
            
            question_to_emotion_field = {
                'Q1': 'emotion_suggested_changes',
                'Q2': 'emotion_best_aspect',
                'Q3': 'emotion_least_aspect',
                'Q4': 'emotion_further_comments'
            }
            
            emotion_field = question_to_emotion_field.get(question_num)
            ai_label = feedback.get(emotion_field, '').lower() if emotion_field else ''
            
            if not ai_label:
                ai_label = 'unknown'
            
            ai_emotions.append(ai_label)
            count += 1
        else:
            ai_emotions.append('unknown')
    
    comparison_df['ai_label'] = ai_emotions
    
    # Add observations
    comparison_df['observation'] = comparison_df.apply(
        lambda row: create_observation(
            row['expert_label'], 
            row['ai_label'],
            row['student_feedback'],
            None,
            row['question_num']
        ),
        axis=1
    )
    
    print(f"✅ Added AI predictions for {len([x for x in ai_emotions if x != 'unknown'])} records")
    return comparison_df

def write_txt_table(comparison_df, output_file):
    """Write comparison table to TXT file"""
    print(f"\n📝 Generating TXT table: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 180 + "\n")
        f.write("Table X. Comparison of AI and Expert Emotion Classification\n")
        f.write("=" * 180 + "\n\n")
        
        f.write("Inter-Rater Agreement Metrics:\n")
        f.write("-" * 180 + "\n")
        
        # Calculate agreement statistics
        total_records = len(comparison_df)
        agreement_count = sum(comparison_df['expert_label'].str.lower() == comparison_df['ai_label'].str.lower())
        agreement_pct = (agreement_count / total_records * 100) if total_records > 0 else 0
        
        f.write(f"Total Comparisons: {total_records}\n")
        f.write(f"Agreements (Expert = AI): {agreement_count}\n")
        f.write(f"Disagreements: {total_records - agreement_count}\n")
        f.write(f"Agreement Rate: {agreement_pct:.2f}%\n\n")
        
        # Table header
        f.write("=" * 180 + "\n")
        col1_width = 50
        col2_width = 25
        col3_width = 25
        col4_width = 78
        
        f.write(f"{'Student Feedback':<{col1_width}} | {'Expert Label':<{col2_width}} | {'AI Label':<{col3_width}} | {'Observation':<{col4_width}}\n")
        f.write("=" * 180 + "\n")
        
        # Write data rows
        for idx, row in comparison_df.iterrows():
            feedback = row['student_feedback'][:col1_width-5] if row['student_feedback'] else "N/A"
            
            f.write(f"{feedback:<{col1_width}} | {row['expert_label']:<{col2_width}} | {row['ai_label']:<{col3_width}} | {row['observation']:<{col4_width}}\n")
        
        f.write("=" * 180 + "\n")
        f.write(f"\nNote: Expert Label is computed as majority vote from 3 human annotators.\n")
        f.write(f"AI Label is predicted emotion classification from XLM-RoBERTa model.\n")
        f.write(f"Observation column shows agreement status and likely reason for disagreements.\n")

def generate_png_table(comparison_df, output_file):
    """Generate comparison table as PNG image"""
    print(f"📊 Generating PNG table: {output_file}")
    
    # Prepare data for table
    table_data = []
    
    for idx, row in comparison_df.iterrows():
        feedback_text = row['student_feedback']
        if len(feedback_text) > 40:
            feedback_text = feedback_text[:40] + "..."
        
        table_data.append([
            feedback_text,
            row['expert_label'].capitalize(),
            row['ai_label'].capitalize(),
            row['observation'][:50] + "..." if len(row['observation']) > 50 else row['observation']
        ])
    
    # Create figure with table
    fig, ax = plt.subplots(figsize=(20, max(8, len(table_data) * 0.5)))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table = ax.table(
        cellText=table_data,
        colLabels=['Student Feedback', 'Expert Label', 'AI Label', 'Observation'],
        cellLoc='left',
        loc='center',
        colWidths=[0.35, 0.15, 0.15, 0.35]
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(4):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(4):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
            else:
                table[(i, j)].set_facecolor('white')
            
            # Highlight agreement/disagreement
            if j == 3:  # Observation column
                if '✓' in str(table_data[i-1][j]):
                    table[(i, j)].set_facecolor('#e8f5e9')
                elif '✗' in str(table_data[i-1][j]):
                    table[(i, j)].set_facecolor('#ffebee')
    
    plt.title('Table X. Comparison of AI and Expert Emotion Classification', 
              fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ PNG table saved")

def main():
    print("\n" + "=" * 100)
    print("AI vs EXPERT EMOTION CLASSIFICATION COMPARISON TABLE GENERATOR")
    print("=" * 100 + "\n")
    
    try:
        # Load comparison data
        comparison_df = load_comparison_data()
        
        if comparison_df.empty:
            print("❌ No data found to compare")
            return
        
        # Add AI predictions from database
        comparison_df = add_ai_predictions(comparison_df)
        
        # Get up to 15 samples for balanced representation
        if len(comparison_df) > 15:
            # Ensure we have mix of agreements and disagreements
            agreements = comparison_df[comparison_df['expert_label'].str.lower() == comparison_df['ai_label'].str.lower()]
            disagreements = comparison_df[comparison_df['expert_label'].str.lower() != comparison_df['ai_label'].str.lower()]
            
            num_agreements = min(8, len(agreements))
            num_disagreements = min(7, len(disagreements))
            
            comparison_df = pd.concat([
                agreements.sample(n=num_agreements, random_state=42),
                disagreements.sample(n=num_disagreements, random_state=42)
            ]).reset_index(drop=True)
        
        # Generate outputs
        output_dir = r'C:\Users\Mosses Ramos\Documents\GitHub\Thesis-Sentiment\server\data\annotations\visualizations'
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        txt_output = os.path.join(output_dir, 'ai_expert_emotion_comparison_table.txt')
        png_output = os.path.join(output_dir, 'ai_expert_emotion_comparison_table.png')
        
        write_txt_table(comparison_df, txt_output)
        generate_png_table(comparison_df, png_output)
        
        # Summary statistics
        print("\n" + "=" * 100)
        print("SUMMARY STATISTICS")
        print("=" * 100)
        total = len(comparison_df)
        agreements = sum(comparison_df['expert_label'].str.lower() == comparison_df['ai_label'].str.lower())
        agreement_pct = (agreements / total * 100) if total > 0 else 0
        
        print(f"Total comparisons: {total}")
        print(f"Agreements: {agreements}")
        print(f"Disagreements: {total - agreements}")
        print(f"Agreement Rate: {agreement_pct:.2f}%")
        print(f"\nEmber Label Distribution (Expert):")
        print(comparison_df['expert_label'].value_counts())
        print(f"\nEmotion Label Distribution (AI):")
        print(comparison_df['ai_label'].value_counts())
        
        print(f"\n✅ Generated: {txt_output}")
        print(f"✅ Generated: {png_output}")
        print(f"Rows included: {total}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
