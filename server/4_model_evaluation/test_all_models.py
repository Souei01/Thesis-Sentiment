"""
Comprehensive Test of All Fine-Tuned Models
Tests all 4 models on the same 30% test set and generates detailed comparisons
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support, 
                             confusion_matrix, classification_report, cohen_kappa_score)
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import time

def load_model(model_path, model_name):
    """Load a fine-tuned model"""
    print(f"\n⏳ Loading {model_name}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        model.eval()
        print(f"✅ {model_name} loaded")
        return tokenizer, model
    except Exception as e:
        print(f"❌ Error loading {model_name}: {e}")
        return None, None

def predict_batch(model, tokenizer, texts, batch_size=32):
    """Make predictions on a batch of texts"""
    all_predictions = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors='pt'
        )
        
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=1).numpy()
            all_predictions.extend(predictions)
    
    return np.array(all_predictions)

def evaluate_model(model, tokenizer, texts, true_labels, model_name):
    """Evaluate a model and return detailed metrics"""
    print(f"\n{'='*80}")
    print(f"EVALUATING {model_name.upper()}")
    print(f"{'='*80}")
    
    start_time = time.time()
    predictions = predict_batch(model, tokenizer, texts)
    inference_time = time.time() - start_time
    
    # Calculate metrics
    accuracy = accuracy_score(true_labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        true_labels, predictions, average='weighted', zero_division=0
    )
    kappa = cohen_kappa_score(true_labels, predictions)
    
    # Per-class metrics
    precision_per_class, recall_per_class, f1_per_class, support = \
        precision_recall_fscore_support(
            true_labels, predictions, labels=list(range(5)), zero_division=0
        )
    
    # Confusion matrix
    cm = confusion_matrix(true_labels, predictions, labels=list(range(5)))
    
    print(f"\nOverall Metrics:")
    print(f"  Accuracy:       {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision:      {precision:.4f}")
    print(f"  Recall:         {recall:.4f}")
    print(f"  F1 Score:       {f1:.4f}")
    print(f"  Cohen's Kappa:  {kappa:.4f}")
    print(f"  Inference Time: {inference_time:.2f}s ({len(texts)/inference_time:.1f} samples/sec)")
    
    emotion_labels = ['joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment']
    print(f"\nPer-Emotion Performance:")
    print("-" * 80)
    print(f"{'Emotion':<15} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'Support':<10}")
    print("-" * 80)
    for i, emotion in enumerate(emotion_labels):
        print(f"{emotion.capitalize():<15} "
              f"{precision_per_class[i]:<12.4f} "
              f"{recall_per_class[i]:<12.4f} "
              f"{f1_per_class[i]:<12.4f} "
              f"{support[i]:<10.0f}")
    print("-" * 80)
    
    return {
        'model': model_name,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'kappa': kappa,
        'inference_time': inference_time,
        'samples_per_sec': len(texts)/inference_time,
        'predictions': predictions,
        'confusion_matrix': cm,
        'precision_per_class': precision_per_class,
        'recall_per_class': recall_per_class,
        'f1_per_class': f1_per_class,
        'support': support
    }

def plot_model_comparison(results, save_dir):
    """Create comprehensive comparison visualizations"""
    
    print(f"\n{'='*80}")
    print("GENERATING COMPARISON VISUALIZATIONS")
    print(f"{'='*80}")
    
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    
    models = [r['model'] for r in results]
    emotion_labels = ['Joy', 'Satisfaction', 'Acceptance', 'Boredom', 'Disappointment']
    
    # 1. Overall Metrics Comparison
    print("\n1. Overall metrics comparison...")
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    metrics = ['accuracy', 'precision', 'recall', 'f1', 'kappa', 'samples_per_sec']
    metric_names = ['Accuracy', 'Precision', 'Recall', 'F1 Score', "Cohen's Kappa", 'Speed (samples/sec)']
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    
    for idx, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
        ax = axes[idx // 3, idx % 3]
        values = [r[metric] for r in results]
        
        bars = ax.bar(range(len(models)), values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.set_ylabel(metric_name, fontsize=11, fontweight='bold')
        ax.set_title(f'{metric_name} Comparison', fontsize=12, fontweight='bold')
        ax.set_xticks(range(len(models)))
        ax.set_xticklabels(models, rotation=15, ha='right')
        
        if metric != 'samples_per_sec':
            ax.set_ylim([0, 1])
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, values)):
            if metric == 'samples_per_sec':
                label = f'{val:.1f}'
            else:
                label = f'{val:.3f}'
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01 if metric != 'samples_per_sec' else bar.get_height(),
                   label, ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.suptitle('Model Performance Comparison - All Metrics', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_dir / 'overall_comparison.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: {save_dir / 'overall_comparison.png'}")
    plt.close()
    
    # 2. Confusion Matrices Side-by-Side
    print("2. Confusion matrices comparison...")
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    
    for idx, result in enumerate(results):
        ax = axes[idx // 2, idx % 2]
        cm = result['confusion_matrix']
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                   xticklabels=emotion_labels,
                   yticklabels=emotion_labels,
                   cbar_kws={'label': 'Count'})
        
        ax.set_title(f"{result['model']}\nAccuracy: {result['accuracy']:.2%}", 
                    fontsize=12, fontweight='bold')
        ax.set_ylabel('True Label', fontsize=10)
        ax.set_xlabel('Predicted Label', fontsize=10)
    
    plt.suptitle('Confusion Matrices - All Models', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_dir / 'confusion_matrices.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: {save_dir / 'confusion_matrices.png'}")
    plt.close()
    
    # 3. Per-Emotion F1 Scores Comparison
    print("3. Per-emotion F1 scores...")
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = np.arange(len(emotion_labels))
    width = 0.2
    
    for i, result in enumerate(results):
        offset = (i - len(results)/2 + 0.5) * width
        bars = ax.bar(x + offset, result['f1_per_class'], width, 
                     label=result['model'], color=colors[i], alpha=0.8)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=8)
    
    ax.set_ylabel('F1 Score', fontsize=12, fontweight='bold')
    ax.set_xlabel('Emotion', fontsize=12, fontweight='bold')
    ax.set_title('Per-Emotion F1 Score Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(emotion_labels, rotation=15, ha='right')
    ax.legend(loc='upper right', fontsize=10)
    ax.set_ylim([0, 1])
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(save_dir / 'per_emotion_f1.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: {save_dir / 'per_emotion_f1.png'}")
    plt.close()
    
    # 4. Ranking Summary
    print("4. Model ranking summary...")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ranking_data = []
    for result in results:
        ranking_data.append([
            result['model'],
            f"{result['accuracy']:.4f}",
            f"{result['f1']:.4f}",
            f"{result['kappa']:.4f}",
            f"{result['samples_per_sec']:.1f}"
        ])
    
    # Sort by accuracy
    ranking_data.sort(key=lambda x: float(x[1]), reverse=True)
    
    table = ax.table(cellText=ranking_data,
                     colLabels=['Model', 'Accuracy', 'F1 Score', "Cohen's κ", 'Speed (s/s)'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.25, 0.15, 0.15, 0.15, 0.15])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Color header
    for i in range(5):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Color first place
    for i in range(5):
        table[(1, i)].set_facecolor('#f1c40f')
        table[(1, i)].set_text_props(weight='bold')
    
    ax.axis('off')
    plt.title('Model Performance Ranking (Sorted by Accuracy)', 
             fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(save_dir / 'ranking_summary.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: {save_dir / 'ranking_summary.png'}")
    plt.close()
    
    # 5. Agreement Analysis
    print("5. Model agreement analysis...")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Calculate pairwise agreement
    agreement_matrix = np.zeros((len(results), len(results)))
    
    for i in range(len(results)):
        for j in range(len(results)):
            if i == j:
                agreement_matrix[i, j] = 1.0
            else:
                agreement = np.mean(results[i]['predictions'] == results[j]['predictions'])
                agreement_matrix[i, j] = agreement
    
    sns.heatmap(agreement_matrix, annot=True, fmt='.3f', cmap='YlGnBu',
               xticklabels=models, yticklabels=models,
               vmin=0, vmax=1, ax=ax, cbar_kws={'label': 'Agreement Rate'})
    
    ax.set_title('Inter-Model Agreement Matrix', fontsize=14, fontweight='bold')
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Model', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(save_dir / 'agreement_matrix.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: {save_dir / 'agreement_matrix.png'}")
    plt.close()

def main():
    print("="*80)
    print("COMPREHENSIVE MODEL COMPARISON TEST")
    print("Testing all 4 fine-tuned models on the same test set")
    print("="*80)
    
    # Load data
    print("\n📂 Loading dataset...")
    df = pd.read_csv('data/annotations/training_data_balanced.csv')
    print(f"✅ Loaded {len(df)} samples")
    
    # Use FEEDBACK ONLY format (proven best)
    df['text'] = df['feedback']
    
    # Map labels
    label_dict = {'joy': 0, 'satisfaction': 1, 'acceptance': 2, 'boredom': 3, 'disappointment': 4}
    df['label_id'] = df['label'].map(label_dict)
    
    # Split data (same split as training)
    _, test_df = train_test_split(df, test_size=0.30, random_state=42, stratify=df['label_id'])
    
    test_texts = test_df['text'].tolist()
    test_labels = test_df['label_id'].values
    
    print(f"✅ Test set: {len(test_texts)} samples (30% of data)")
    print(f"   Format: Feedback Only")
    print()
    
    # Models to test
    models_config = [
        {'name': 'RoBERTa', 'path': 'ml_models/roberta_finetuned'},
        {'name': 'mBERT', 'path': 'ml_models/mbert_finetuned'},
        {'name': 'DistilBERT', 'path': 'ml_models/distilbert_finetuned'},
        {'name': 'XLM-RoBERTa', 'path': 'ml_models/xlm_roberta_finetuned'}
    ]
    
    # Evaluate each model
    results = []
    
    for config in models_config:
        if Path(config['path']).exists():
            tokenizer, model = load_model(config['path'], config['name'])
            if model is not None:
                result = evaluate_model(model, tokenizer, test_texts, test_labels, config['name'])
                results.append(result)
        else:
            print(f"\n⚠️  {config['name']} not found at {config['path']}")
    
    # Generate comparison visualizations
    if results:
        plot_model_comparison(results, 'results/model_comparison')
        
        # Print final summary
        print(f"\n{'='*80}")
        print("FINAL SUMMARY")
        print(f"{'='*80}")
        
        print(f"\n{'Model':<15} {'Accuracy':<12} {'F1 Score':<12} {'Kappa':<12} {'Speed (s/s)':<15}")
        print("-"*80)
        
        # Sort by accuracy
        sorted_results = sorted(results, key=lambda x: x['accuracy'], reverse=True)
        
        for i, result in enumerate(sorted_results):
            rank_symbol = '🏆' if i == 0 else '  '
            print(f"{rank_symbol} {result['model']:<13} "
                  f"{result['accuracy']:<12.4f} "
                  f"{result['f1']:<12.4f} "
                  f"{result['kappa']:<12.4f} "
                  f"{result['samples_per_sec']:<15.1f}")
        
        print("-"*80)
        
        # Best model per metric
        print(f"\n🏆 Best Performance by Metric:")
        print(f"   Highest Accuracy:  {max(results, key=lambda x: x['accuracy'])['model']} ({max(r['accuracy'] for r in results):.4f})")
        print(f"   Highest F1 Score:  {max(results, key=lambda x: x['f1'])['model']} ({max(r['f1'] for r in results):.4f})")
        print(f"   Highest Kappa:     {max(results, key=lambda x: x['kappa'])['model']} ({max(r['kappa'] for r in results):.4f})")
        print(f"   Fastest:           {max(results, key=lambda x: x['samples_per_sec'])['model']} ({max(r['samples_per_sec'] for r in results):.1f} samples/sec)")
        
        print(f"\n📁 All visualizations saved to: results/model_comparison/")
        print(f"{'='*80}")
    else:
        print("\n❌ No models available for comparison")

if __name__ == "__main__":
    main()
