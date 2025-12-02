"""
Unified Training Script for All Models
Uses identical training algorithm and generates comprehensive visualizations for thesis
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable CUDA

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    TrainingArguments, 
    Trainer, 
    EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, 
    precision_recall_fscore_support, 
    confusion_matrix,
    roc_curve,
    auc,
    precision_recall_curve,
    classification_report
)
import time
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

MODELS_CONFIG = {
    'xlm_roberta': {
        'name': 'XLM-RoBERTa',
        'path': 'ml_models/xlm_roberta',
        'output_dir': 'ml_models/xlm_roberta_finetuned',
        'results_dir': 'results/xlm_roberta_finetuned'
    },
    'mbert': {
        'name': 'mBERT',
        'path': 'ml_models/mbert',
        'output_dir': 'ml_models/mbert_finetuned',
        'results_dir': 'results/mbert_finetuned'
    },
    'roberta': {
        'name': 'RoBERTa',
        'path': 'ml_models/roberta',
        'output_dir': 'ml_models/roberta_finetuned',
        'results_dir': 'results/roberta_finetuned'
    },
    'distilbert': {
        'name': 'DistilBERT',
        'path': 'ml_models/distilbert',
        'output_dir': 'ml_models/distilbert_finetuned',
        'results_dir': 'results/distilbert_finetuned'
    }
}

EMOTION_LABELS = ['joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment']
LABEL_DICT = {'joy': 0, 'satisfaction': 1, 'acceptance': 2, 'boredom': 3, 'disappointment': 4}
ID2LABEL = {v: k for k, v in LABEL_DICT.items()}

# Training hyperparameters (IDENTICAL for all models)
TRAIN_CONFIG = {
    'num_train_epochs': 5,
    'per_device_train_batch_size': 16,
    'per_device_eval_batch_size': 32,
    'warmup_steps': 100,
    'weight_decay': 0.01,
    'learning_rate': 2e-5,
    'logging_steps': 50,
    'eval_strategy': 'epoch',
    'save_strategy': 'epoch',
    'load_best_model_at_end': True,
    'metric_for_best_model': 'f1',
    'early_stopping_patience': 3,
    'max_length': 128
}

# ============================================================================
# DATASET CLASS
# ============================================================================

class EmotionDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average='weighted', zero_division=0
    )
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_confusion_matrix(cm, labels, model_name, save_path):
    """1. Confusion Matrix"""
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels, yticklabels=labels,
                cbar_kws={'label': 'Count'})
    plt.title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold', pad=20)
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved: {save_path}')

def plot_classification_metrics(precision, recall, f1, labels, model_name, save_path):
    """2. Classification Performance (Per-Class Bar Chart)"""
    x = np.arange(len(labels))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width, precision, width, label='Precision', color='steelblue')
    ax.bar(x, recall, width, label='Recall', color='coral')
    ax.bar(x + width, f1, width, label='F1-Score', color='lightgreen')
    
    ax.set_xlabel('Emotion', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title(f'Classification Metrics - {model_name}', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()
    ax.set_ylim(0, 1.0)
    ax.grid(axis='y', alpha=0.3)
    
    for i in range(len(labels)):
        ax.text(i - width, precision[i] + 0.02, f'{precision[i]:.2f}', 
               ha='center', va='bottom', fontsize=9)
        ax.text(i, recall[i] + 0.02, f'{recall[i]:.2f}', 
               ha='center', va='bottom', fontsize=9)
        ax.text(i + width, f1[i] + 0.02, f'{f1[i]:.2f}', 
               ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved: {save_path}')

def plot_roc_curves(y_true, y_probs, labels, model_name, save_path):
    """3. ROC Curve + AUC (One-vs-Rest for multiclass)"""
    from sklearn.preprocessing import label_binarize
    
    y_true_bin = label_binarize(y_true, classes=list(range(len(labels))))
    
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (label, color) in enumerate(zip(labels, colors)):
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_probs[:, i])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=color, lw=2, 
               label=f'{label} (AUC = {roc_auc:.3f})')
    
    ax.plot([0, 1], [0, 1], 'k--', lw=2, label='Random Classifier')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title(f'ROC Curves - {model_name}', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved: {save_path}')

def plot_precision_recall_curves(y_true, y_probs, labels, model_name, save_path):
    """4. Precision-Recall Curve"""
    from sklearn.preprocessing import label_binarize
    
    y_true_bin = label_binarize(y_true, classes=list(range(len(labels))))
    
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (label, color) in enumerate(zip(labels, colors)):
        precision_curve, recall_curve, _ = precision_recall_curve(
            y_true_bin[:, i], y_probs[:, i]
        )
        ax.plot(recall_curve, precision_curve, color=color, lw=2, label=label)
    
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('Recall', fontsize=12)
    ax.set_ylabel('Precision', fontsize=12)
    ax.set_title(f'Precision-Recall Curves - {model_name}', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved: {save_path}')

def plot_training_history(trainer, model_name, save_path):
    """5. Training vs Validation Loss/Accuracy Curves"""
    log_history = trainer.state.log_history
    
    train_loss = []
    eval_loss = []
    eval_acc = []
    eval_f1 = []
    epochs = []
    
    for entry in log_history:
        if 'loss' in entry and 'epoch' in entry:
            train_loss.append(entry['loss'])
        if 'eval_loss' in entry:
            eval_loss.append(entry['eval_loss'])
            eval_acc.append(entry['eval_accuracy'])
            eval_f1.append(entry['eval_f1'])
            epochs.append(entry['epoch'])
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Training Loss
    if train_loss:
        axes[0, 0].plot(train_loss, marker='o', color='#e74c3c', linewidth=2)
        axes[0, 0].set_title('Training Loss', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Step', fontsize=10)
        axes[0, 0].set_ylabel('Loss', fontsize=10)
        axes[0, 0].grid(True, alpha=0.3)
    
    # Validation Loss
    if eval_loss:
        axes[0, 1].plot(epochs, eval_loss, marker='s', color='#3498db', linewidth=2)
        axes[0, 1].set_title('Validation Loss', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Epoch', fontsize=10)
        axes[0, 1].set_ylabel('Loss', fontsize=10)
        axes[0, 1].grid(True, alpha=0.3)
    
    # Validation Accuracy
    if eval_acc:
        axes[1, 0].plot(epochs, eval_acc, marker='d', color='#2ecc71', linewidth=2)
        axes[1, 0].set_title('Validation Accuracy', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Epoch', fontsize=10)
        axes[1, 0].set_ylabel('Accuracy', fontsize=10)
        axes[1, 0].set_ylim([0, 1])
        axes[1, 0].grid(True, alpha=0.3)
        for x, y in zip(epochs, eval_acc):
            axes[1, 0].text(x, y + 0.02, f'{y:.3f}', ha='center', fontsize=9)
    
    # Validation F1
    if eval_f1:
        axes[1, 1].plot(epochs, eval_f1, marker='*', color='#f39c12', linewidth=2, markersize=10)
        axes[1, 1].set_title('Validation F1 Score', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Epoch', fontsize=10)
        axes[1, 1].set_ylabel('F1 Score', fontsize=10)
        axes[1, 1].set_ylim([0, 1])
        axes[1, 1].grid(True, alpha=0.3)
        for x, y in zip(epochs, eval_f1):
            axes[1, 1].text(x, y + 0.02, f'{y:.3f}', ha='center', fontsize=9)
    
    plt.suptitle(f'Training History - {model_name}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved: {save_path}')

def plot_confidence_histogram(y_probs, y_pred, labels, model_name, save_path):
    """6. Probability Confidence Histogram"""
    max_probs = np.max(y_probs, axis=1)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Overall confidence distribution
    axes[0].hist(max_probs, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
    axes[0].set_xlabel('Confidence Score', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title('Prediction Confidence Distribution', fontsize=12, fontweight='bold')
    axes[0].axvline(np.mean(max_probs), color='red', linestyle='--', 
                    label=f'Mean: {np.mean(max_probs):.3f}')
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    # Confidence by predicted class
    for i, label in enumerate(labels):
        mask = y_pred == i
        if mask.sum() > 0:
            axes[1].hist(max_probs[mask], bins=15, alpha=0.5, label=label)
    
    axes[1].set_xlabel('Confidence Score', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title('Confidence by Predicted Class', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    
    plt.suptitle(f'Model Confidence - {model_name}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved: {save_path}')

def plot_error_analysis(texts, y_true, y_pred, labels, model_name, save_path):
    """7. Error Analysis - Length vs Error Rate"""
    # Calculate text lengths
    text_lengths = [len(text.split()) for text in texts]
    errors = (y_true != y_pred).astype(int)
    
    # Bin by length
    length_bins = [0, 5, 10, 15, 20, 100]
    bin_labels = ['1-5', '6-10', '11-15', '16-20', '20+']
    length_categories = pd.cut(text_lengths, bins=length_bins, labels=bin_labels)
    
    # Calculate error rate per bin
    df_error = pd.DataFrame({
        'length_cat': length_categories,
        'error': errors
    })
    error_rates = df_error.groupby('length_cat')['error'].mean()
    counts = df_error.groupby('length_cat').size()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Error rate by text length
    axes[0].bar(range(len(error_rates)), error_rates.values, color='coral', alpha=0.7)
    axes[0].set_xticks(range(len(error_rates)))
    axes[0].set_xticklabels(error_rates.index)
    axes[0].set_xlabel('Text Length (words)', fontsize=12)
    axes[0].set_ylabel('Error Rate', fontsize=12)
    axes[0].set_title('Error Rate by Text Length', fontsize=12, fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(error_rates.values):
        axes[0].text(i, v + 0.01, f'{v:.2%}\n(n={counts.iloc[i]})', 
                    ha='center', va='bottom', fontsize=9)
    
    # Per-class error breakdown
    error_per_class = []
    for i, label in enumerate(labels):
        mask = y_true == i
        if mask.sum() > 0:
            error_rate = (y_pred[mask] != y_true[mask]).mean()
            error_per_class.append(error_rate)
        else:
            error_per_class.append(0)
    
    axes[1].bar(range(len(labels)), error_per_class, color='steelblue', alpha=0.7)
    axes[1].set_xticks(range(len(labels)))
    axes[1].set_xticklabels(labels, rotation=45, ha='right')
    axes[1].set_xlabel('Emotion Class', fontsize=12)
    axes[1].set_ylabel('Error Rate', fontsize=12)
    axes[1].set_title('Error Rate by Class', fontsize=12, fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(error_per_class):
        axes[1].text(i, v + 0.01, f'{v:.2%}', ha='center', va='bottom', fontsize=9)
    
    plt.suptitle(f'Error Analysis - {model_name}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved: {save_path}')

def plot_sample_predictions(texts, y_true, y_pred, labels, model_name, save_path, num_samples=10):
    """8. Sample Predictions Table"""
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis('tight')
    ax.axis('off')
    
    table_data = []
    for i in range(min(num_samples, len(texts))):
        text = texts[i][:70] + '...' if len(texts[i]) > 70 else texts[i]
        true_label = labels[y_true[i]].capitalize()
        pred_label = labels[y_pred[i]].capitalize()
        match = '✓' if y_true[i] == y_pred[i] else '✗'
        table_data.append([i+1, text, true_label, pred_label, match])
    
    table = ax.table(cellText=table_data,
                     colLabels=['#', 'Feedback Text', 'True Label', 'Predicted', 'Match'],
                     cellLoc='left',
                     loc='center',
                     colWidths=[0.05, 0.55, 0.15, 0.15, 0.08])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    for i in range(5):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    for i in range(1, len(table_data) + 1):
        if table_data[i-1][4] == '✓':
            table[(i, 4)].set_facecolor('#2ecc71')
            table[(i, 4)].set_text_props(weight='bold')
        else:
            table[(i, 4)].set_facecolor('#e74c3c')
            table[(i, 4)].set_text_props(weight='bold', color='white')
    
    plt.title(f'Sample Predictions - {model_name}', fontsize=14, fontweight='bold', pad=20)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved: {save_path}')

# ============================================================================
# MAIN TRAINING FUNCTION
# ============================================================================

def train_model(model_key):
    """Train a single model with comprehensive evaluation"""
    
    config = MODELS_CONFIG[model_key]
    model_name = config['name']
    
    print('\n' + '='*80)
    print(f'FINE-TUNING {model_name.upper()} FOR EMOTION CLASSIFICATION')
    print('='*80)
    
    # Setup
    device = torch.device('cpu')
    print(f'Device: {device} (GPU sm_120 not yet supported)')
    print(f'Estimated training time: ~30-40 minutes on CPU\n')
    
    # Load data
    print('📂 Loading data...')
    df = pd.read_csv('data/annotations/train_data.csv')
    print(f'✅ Loaded {len(df)} samples')
    print(f'📊 Distribution: {dict(df["label"].value_counts())}\n')
    
    # Use feedback only (best format based on previous experiments)
    df['text'] = df['feedback']
    df['label_id'] = df['label'].map(LABEL_DICT)
    
    # Split into train/val (70/30)
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['text'].tolist(),
        df['label_id'].tolist(),
        test_size=0.30,
        random_state=42,
        stratify=df['label_id']
    )
    print(f'Training: {len(train_texts)} | Validation: {len(val_texts)}\n')
    
    # Load model and tokenizer
    print(f'🔄 Loading {model_name}...')
    tokenizer = AutoTokenizer.from_pretrained(config['path'])
    model = AutoModelForSequenceClassification.from_pretrained(
        config['path'],
        num_labels=5,
        id2label=ID2LABEL,
        label2id=LABEL_DICT
    )
    model.to(device)
    print('✅ Model loaded\n')
    
    # Create datasets
    train_dataset = EmotionDataset(train_texts, train_labels, tokenizer, 
                                   TRAIN_CONFIG['max_length'])
    val_dataset = EmotionDataset(val_texts, val_labels, tokenizer, 
                                 TRAIN_CONFIG['max_length'])
    
    # Setup output directories
    output_dir = config['output_dir']
    results_dir = config['results_dir']
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=TRAIN_CONFIG['num_train_epochs'],
        per_device_train_batch_size=TRAIN_CONFIG['per_device_train_batch_size'],
        per_device_eval_batch_size=TRAIN_CONFIG['per_device_eval_batch_size'],
        warmup_steps=TRAIN_CONFIG['warmup_steps'],
        weight_decay=TRAIN_CONFIG['weight_decay'],
        learning_rate=TRAIN_CONFIG['learning_rate'],
        logging_steps=TRAIN_CONFIG['logging_steps'],
        eval_strategy=TRAIN_CONFIG['eval_strategy'],
        save_strategy=TRAIN_CONFIG['save_strategy'],
        load_best_model_at_end=TRAIN_CONFIG['load_best_model_at_end'],
        metric_for_best_model=TRAIN_CONFIG['metric_for_best_model'],
        report_to='none',
        fp16=False
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(
            early_stopping_patience=TRAIN_CONFIG['early_stopping_patience']
        )]
    )
    
    # Train
    print('='*80)
    print('🚀 STARTING TRAINING')
    print('='*80)
    start_time = time.time()
    trainer.train()
    training_time = (time.time() - start_time) / 60
    print(f'\n✅ Training complete: {training_time:.2f} minutes\n')
    
    # Save model
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f'💾 Model saved to: {output_dir}\n')
    
    # Evaluation
    print('='*80)
    print('📊 EVALUATION')
    print('='*80)
    
    eval_results = trainer.evaluate()
    print(f"Accuracy:  {eval_results['eval_accuracy']*100:.2f}%")
    print(f"Precision: {eval_results['eval_precision']:.4f}")
    print(f"Recall:    {eval_results['eval_recall']:.4f}")
    print(f"F1 Score:  {eval_results['eval_f1']:.4f}\n")
    
    # Get predictions
    predictions = trainer.predict(val_dataset)
    y_pred = predictions.predictions.argmax(-1)
    y_true = predictions.label_ids
    y_probs = torch.softmax(torch.tensor(predictions.predictions), dim=1).numpy()
    
    # Per-class metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=list(range(5)), zero_division=0
    )
    
    print('📋 Per-Emotion Performance:')
    for i, emotion in enumerate(EMOTION_LABELS):
        print(f'{emotion:15} P:{precision[i]:.3f} R:{recall[i]:.3f} F1:{f1[i]:.3f} Support:{support[i]}')
    print()
    
    # Generate all visualizations
    print('='*80)
    print('📈 GENERATING VISUALIZATIONS')
    print('='*80)
    
    cm = confusion_matrix(y_true, y_pred, labels=list(range(5)))
    
    # 1. Confusion Matrix
    plot_confusion_matrix(cm, EMOTION_LABELS, model_name, 
                         f'{results_dir}/1_confusion_matrix.png')
    
    # 2. Classification Metrics
    plot_classification_metrics(precision, recall, f1, EMOTION_LABELS, 
                                model_name, f'{results_dir}/2_classification_metrics.png')
    
    # 3. ROC Curves
    plot_roc_curves(y_true, y_probs, EMOTION_LABELS, model_name, 
                   f'{results_dir}/3_roc_curves.png')
    
    # 4. Precision-Recall Curves
    plot_precision_recall_curves(y_true, y_probs, EMOTION_LABELS, model_name, 
                                f'{results_dir}/4_precision_recall_curves.png')
    
    # 5. Training History
    plot_training_history(trainer, model_name, f'{results_dir}/5_training_history.png')
    
    # 6. Confidence Histogram
    plot_confidence_histogram(y_probs, y_pred, EMOTION_LABELS, model_name, 
                             f'{results_dir}/6_confidence_histogram.png')
    
    # 7. Error Analysis
    plot_error_analysis(val_texts, y_true, y_pred, EMOTION_LABELS, model_name, 
                       f'{results_dir}/7_error_analysis.png')
    
    # 8. Sample Predictions
    plot_sample_predictions(val_texts, y_true, y_pred, EMOTION_LABELS, 
                           model_name, f'{results_dir}/8_sample_predictions.png', 
                           num_samples=15)
    
    # Save metrics to CSV
    results_df = pd.DataFrame({
        'emotion': EMOTION_LABELS,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'support': support
    })
    results_df.to_csv(f'{results_dir}/metrics.csv', index=False)
    print(f'✅ Saved: {results_dir}/metrics.csv')
    
    print()
    print('='*80)
    print(f'✅ {model_name.upper()} TRAINING COMPLETE!')
    print('='*80)
    print(f'📁 Model: {output_dir}')
    print(f'📁 Results: {results_dir}')
    print(f'⏱️  Time: {training_time:.2f} minutes')
    print(f'🎯 Accuracy: {eval_results["eval_accuracy"]*100:.2f}%')
    print(f'📊 F1 Score: {eval_results["eval_f1"]:.4f}')
    print('='*80)
    print()
    
    return {
        'model_name': model_name,
        'accuracy': eval_results['eval_accuracy'],
        'f1': eval_results['eval_f1'],
        'precision': eval_results['eval_precision'],
        'recall': eval_results['eval_recall'],
        'training_time': training_time
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import sys
    
    print('\n' + '='*80)
    print('UNIFIED MODEL TRAINING PIPELINE')
    print('Training all models with identical algorithm and hyperparameters')
    print('='*80)
    print(f'\n📋 Training Configuration:')
    for key, value in TRAIN_CONFIG.items():
        print(f'   {key}: {value}')
    print()
    
    # Determine which models to train
    if len(sys.argv) > 1:
        # Train specific model
        model_key = sys.argv[1].lower()
        if model_key not in MODELS_CONFIG:
            print(f'❌ Error: Unknown model "{model_key}"')
            print(f'Available models: {", ".join(MODELS_CONFIG.keys())}')
            sys.exit(1)
        models_to_train = [model_key]
    else:
        # Train all models
        models_to_train = list(MODELS_CONFIG.keys())
    
    print(f'🎯 Models to train: {", ".join([MODELS_CONFIG[k]["name"] for k in models_to_train])}\n')
    
    # Train each model
    all_results = []
    for model_key in models_to_train:
        result = train_model(model_key)
        all_results.append(result)
    
    # Summary
    print('\n' + '='*80)
    print('🎉 ALL TRAINING COMPLETE!')
    print('='*80)
    print(f'\n{"Model":<20} {"Accuracy":<12} {"F1 Score":<12} {"Time (min)":<12}')
    print('-'*80)
    for result in all_results:
        print(f"{result['model_name']:<20} {result['accuracy']*100:>10.2f}%  {result['f1']:>10.4f}  {result['training_time']:>10.2f}")
    print('='*80)
    print()
