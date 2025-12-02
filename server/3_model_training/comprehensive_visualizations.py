"""
Comprehensive Visualization Suite for Model Evaluation
Includes all visualizations required for thesis/academic papers
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, classification_report, 
    roc_curve, auc, precision_recall_curve,
    average_precision_score
)
from sklearn.preprocessing import label_binarize
from pathlib import Path
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

class ComprehensiveVisualizer:
    def __init__(self, model_name, results_dir, emotion_labels):
        self.model_name = model_name
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.emotion_labels = emotion_labels
        self.n_classes = len(emotion_labels)
    
    def plot_confusion_matrix(self, y_true, y_pred):
        """1. Confusion Matrix (Mandatory)"""
        cm = confusion_matrix(y_true, y_pred)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=self.emotion_labels,
                   yticklabels=self.emotion_labels,
                   cbar_kws={'label': 'Count'},
                   ax=ax)
        
        ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
        ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
        ax.set_title(f'Confusion Matrix - {self.model_name}', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Add accuracy on diagonal
        for i in range(len(self.emotion_labels)):
            total = cm[i].sum()
            if total > 0:
                acc = cm[i, i] / total * 100
                ax.text(i + 0.5, i - 0.3, f'{acc:.1f}%', 
                       ha='center', va='center', 
                       fontsize=9, fontweight='bold', color='red')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '1_confusion_matrix.png', bbox_inches='tight')
        plt.close()
        print(f"✅ Saved: 1_confusion_matrix.png")
        
        return cm
    
    def plot_classification_metrics(self, y_true, y_pred):
        """2. Per-Class Metrics Bar Chart"""
        from sklearn.metrics import precision_recall_fscore_support
        
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, labels=list(range(self.n_classes)), zero_division=0
        )
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(self.emotion_labels))
        width = 0.25
        
        bars1 = ax.bar(x - width, precision, width, label='Precision', 
                      color='steelblue', alpha=0.8)
        bars2 = ax.bar(x, recall, width, label='Recall', 
                      color='coral', alpha=0.8)
        bars3 = ax.bar(x + width, f1, width, label='F1-Score', 
                      color='lightgreen', alpha=0.8)
        
        ax.set_xlabel('Emotion Class', fontsize=12, fontweight='bold')
        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title(f'Classification Metrics per Emotion - {self.model_name}',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([e.capitalize() for e in self.emotion_labels], 
                          rotation=45, ha='right')
        ax.legend(loc='upper right', framealpha=0.9)
        ax.set_ylim(0, 1.0)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                       f'{height:.2f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '2_classification_metrics.png', bbox_inches='tight')
        plt.close()
        print(f"✅ Saved: 2_classification_metrics.png")
        
        return precision, recall, f1, support
    
    def plot_roc_curves(self, y_true, y_pred_proba):
        """3. ROC Curve + AUC Score (Multi-class)"""
        # Binarize labels
        y_true_bin = label_binarize(y_true, classes=list(range(self.n_classes)))
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        
        for i, (emotion, color) in enumerate(zip(self.emotion_labels, colors)):
            fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_pred_proba[:, i])
            roc_auc = auc(fpr, tpr)
            
            ax.plot(fpr, tpr, color=color, lw=2, 
                   label=f'{emotion.capitalize()} (AUC = {roc_auc:.3f})')
        
        ax.plot([0, 1], [0, 1], 'k--', lw=2, label='Random Classifier')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate', fontsize=12, fontweight='bold')
        ax.set_ylabel('True Positive Rate', fontsize=12, fontweight='bold')
        ax.set_title(f'ROC Curves - {self.model_name}', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc="lower right", framealpha=0.9)
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '3_roc_curves.png', bbox_inches='tight')
        plt.close()
        print(f"✅ Saved: 3_roc_curves.png")
    
    def plot_precision_recall_curves(self, y_true, y_pred_proba):
        """4. Precision-Recall Curves"""
        y_true_bin = label_binarize(y_true, classes=list(range(self.n_classes)))
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        
        for i, (emotion, color) in enumerate(zip(self.emotion_labels, colors)):
            precision, recall, _ = precision_recall_curve(
                y_true_bin[:, i], y_pred_proba[:, i]
            )
            avg_precision = average_precision_score(
                y_true_bin[:, i], y_pred_proba[:, i]
            )
            
            ax.plot(recall, precision, color=color, lw=2,
                   label=f'{emotion.capitalize()} (AP = {avg_precision:.3f})')
        
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('Recall', fontsize=12, fontweight='bold')
        ax.set_ylabel('Precision', fontsize=12, fontweight='bold')
        ax.set_title(f'Precision-Recall Curves - {self.model_name}',
                    fontsize=14, fontweight='bold')
        ax.legend(loc="lower left", framealpha=0.9)
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '4_precision_recall_curves.png', bbox_inches='tight')
        plt.close()
        print(f"✅ Saved: 4_precision_recall_curves.png")
    
    def plot_training_history(self, log_history):
        """5. Training History (Loss and Metrics over Epochs)"""
        if log_history is None:
            print('⚠️  Skipped: 5_training_history.png (no training history available)')
            return
            
        train_loss = []
        eval_loss = []
        eval_acc = []
        eval_f1 = []
        train_steps = []
        eval_epochs = []
        
        for entry in log_history:
            if 'loss' in entry and 'epoch' in entry:
                train_loss.append(entry['loss'])
                train_steps.append(entry['step'])
            if 'eval_loss' in entry:
                eval_loss.append(entry['eval_loss'])
                eval_acc.append(entry.get('eval_accuracy', 0))
                eval_f1.append(entry.get('eval_f1', 0))
                eval_epochs.append(entry['epoch'])
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Training Loss
        if train_loss:
            ax1.plot(train_loss, color='#e74c3c', linewidth=2, marker='o', 
                    markersize=4, alpha=0.7)
            ax1.set_xlabel('Training Step', fontweight='bold')
            ax1.set_ylabel('Loss', fontweight='bold')
            ax1.set_title('Training Loss', fontsize=12, fontweight='bold')
            ax1.grid(alpha=0.3)
        
        # Validation Loss
        if eval_loss:
            ax2.plot(eval_epochs, eval_loss, color='#3498db', linewidth=2, 
                    marker='s', markersize=8, alpha=0.7)
            ax2.set_xlabel('Epoch', fontweight='bold')
            ax2.set_ylabel('Loss', fontweight='bold')
            ax2.set_title('Validation Loss', fontsize=12, fontweight='bold')
            ax2.grid(alpha=0.3)
            for x, y in zip(eval_epochs, eval_loss):
                ax2.text(x, y + 0.02, f'{y:.3f}', ha='center', fontsize=9)
        
        # Validation Accuracy
        if eval_acc:
            ax3.plot(eval_epochs, eval_acc, color='#2ecc71', linewidth=2,
                    marker='d', markersize=8, alpha=0.7)
            ax3.set_xlabel('Epoch', fontweight='bold')
            ax3.set_ylabel('Accuracy', fontweight='bold')
            ax3.set_title('Validation Accuracy', fontsize=12, fontweight='bold')
            ax3.set_ylim([0, 1])
            ax3.grid(alpha=0.3)
            for x, y in zip(eval_epochs, eval_acc):
                ax3.text(x, y + 0.02, f'{y:.3f}', ha='center', fontsize=9)
        
        # Validation F1
        if eval_f1:
            ax4.plot(eval_epochs, eval_f1, color='#f39c12', linewidth=2,
                    marker='*', markersize=10, alpha=0.7)
            ax4.set_xlabel('Epoch', fontweight='bold')
            ax4.set_ylabel('F1 Score', fontweight='bold')
            ax4.set_title('Validation F1 Score', fontsize=12, fontweight='bold')
            ax4.set_ylim([0, 1])
            ax4.grid(alpha=0.3)
            for x, y in zip(eval_epochs, eval_f1):
                ax4.text(x, y + 0.02, f'{y:.3f}', ha='center', fontsize=9)
        
        plt.suptitle(f'Training History - {self.model_name}', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.results_dir / '5_training_history.png', bbox_inches='tight')
        plt.close()
        print(f"✅ Saved: 5_training_history.png")
    
    def plot_confidence_histogram(self, y_pred_proba, y_pred):
        """6. Probability Confidence Histogram (Calibration Plot)"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        max_probs = np.max(y_pred_proba, axis=1)
        
        # Overall confidence
        axes[0].hist(max_probs, bins=30, color='steelblue', alpha=0.7, edgecolor='black')
        axes[0].set_xlabel('Prediction Confidence', fontweight='bold')
        axes[0].set_ylabel('Frequency', fontweight='bold')
        axes[0].set_title('Overall Confidence Distribution', fontweight='bold')
        axes[0].axvline(max_probs.mean(), color='red', linestyle='--', 
                       linewidth=2, label=f'Mean: {max_probs.mean():.3f}')
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        
        # Per-class confidence
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        for i, (emotion, color) in enumerate(zip(self.emotion_labels, colors)):
            if i < 5:
                class_probs = y_pred_proba[y_pred == i, i]
                if len(class_probs) > 0:
                    axes[i+1].hist(class_probs, bins=20, color=color, 
                                  alpha=0.7, edgecolor='black')
                    axes[i+1].set_xlabel('Confidence', fontweight='bold')
                    axes[i+1].set_ylabel('Frequency', fontweight='bold')
                    axes[i+1].set_title(f'{emotion.capitalize()}', fontweight='bold')
                    axes[i+1].axvline(class_probs.mean(), color='darkred', 
                                     linestyle='--', linewidth=2,
                                     label=f'Mean: {class_probs.mean():.3f}')
                    axes[i+1].legend()
                    axes[i+1].grid(alpha=0.3)
        
        plt.suptitle(f'Prediction Confidence Distribution - {self.model_name}',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.results_dir / '6_confidence_histogram.png', bbox_inches='tight')
        plt.close()
        print(f"✅ Saved: 6_confidence_histogram.png")
    
    def plot_error_analysis(self, texts, y_true, y_pred):
        """7. Error Analysis Visualization"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 7a. Error distribution by class
        errors_by_class = []
        for i in range(self.n_classes):
            mask = y_true == i
            if mask.sum() > 0:
                error_rate = (y_pred[mask] != y_true[mask]).sum() / mask.sum()
                errors_by_class.append(error_rate * 100)
            else:
                errors_by_class.append(0)
        
        ax1.bar(range(self.n_classes), errors_by_class, 
               color=['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'],
               alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Emotion Class', fontweight='bold')
        ax1.set_ylabel('Error Rate (%)', fontweight='bold')
        ax1.set_title('Error Rate by Class', fontweight='bold')
        ax1.set_xticks(range(self.n_classes))
        ax1.set_xticklabels([e.capitalize() for e in self.emotion_labels], 
                           rotation=45, ha='right')
        ax1.grid(axis='y', alpha=0.3)
        for i, v in enumerate(errors_by_class):
            ax1.text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
        
        # 7b. Error by text length
        text_lengths = [len(str(t).split()) for t in texts]
        correct = y_pred == y_true
        
        length_bins = [0, 5, 10, 15, 20, 100]
        bin_labels = ['1-5', '6-10', '11-15', '16-20', '20+']
        error_by_length = []
        
        for i in range(len(length_bins)-1):
            mask = (np.array(text_lengths) >= length_bins[i]) & \
                   (np.array(text_lengths) < length_bins[i+1])
            if mask.sum() > 0:
                error_rate = (~correct[mask]).sum() / mask.sum() * 100
                error_by_length.append(error_rate)
            else:
                error_by_length.append(0)
        
        ax2.bar(bin_labels, error_by_length, color='coral', 
               alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Text Length (words)', fontweight='bold')
        ax2.set_ylabel('Error Rate (%)', fontweight='bold')
        ax2.set_title('Error Rate by Text Length', fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        for i, v in enumerate(error_by_length):
            ax2.text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
        
        # 7c. Most confused pairs
        cm = confusion_matrix(y_true, y_pred)
        np.fill_diagonal(cm, 0)
        
        confused_pairs = []
        for i in range(self.n_classes):
            for j in range(self.n_classes):
                if i != j and cm[i, j] > 0:
                    confused_pairs.append({
                        'true': self.emotion_labels[i],
                        'pred': self.emotion_labels[j],
                        'count': cm[i, j]
                    })
        
        confused_pairs = sorted(confused_pairs, key=lambda x: x['count'], reverse=True)[:10]
        
        if confused_pairs:
            pair_labels = [f"{p['true'][:3]}→{p['pred'][:3]}" for p in confused_pairs]
            pair_counts = [p['count'] for p in confused_pairs]
            
            ax3.barh(pair_labels, pair_counts, color='lightcoral', 
                    alpha=0.7, edgecolor='black')
            ax3.set_xlabel('Error Count', fontweight='bold')
            ax3.set_ylabel('True → Predicted', fontweight='bold')
            ax3.set_title('Top 10 Confused Class Pairs', fontweight='bold')
            ax3.grid(axis='x', alpha=0.3)
            for i, v in enumerate(pair_counts):
                ax3.text(v + 0.5, i, str(v), va='center', fontweight='bold')
        
        # 7d. Correct vs Incorrect distribution
        correct_count = correct.sum()
        incorrect_count = (~correct).sum()
        
        ax4.pie([correct_count, incorrect_count], 
               labels=['Correct', 'Incorrect'],
               colors=['#2ecc71', '#e74c3c'],
               autopct='%1.1f%%',
               startangle=90,
               textprops={'fontweight': 'bold', 'fontsize': 12})
        ax4.set_title(f'Overall Accuracy: {correct_count/(correct_count+incorrect_count)*100:.2f}%',
                     fontweight='bold')
        
        plt.suptitle(f'Error Analysis - {self.model_name}',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.results_dir / '7_error_analysis.png', bbox_inches='tight')
        plt.close()
        print(f"✅ Saved: 7_error_analysis.png")
    
    def plot_sample_predictions(self, texts, y_true, y_pred, num_samples=15):
        """8. Sample Predictions Table"""
        fig, ax = plt.subplots(figsize=(16, 10))
        ax.axis('tight')
        ax.axis('off')
        
        # Select diverse samples (some correct, some wrong)
        correct_idx = np.where(y_true == y_pred)[0]
        wrong_idx = np.where(y_true != y_pred)[0]
        
        n_correct = min(8, len(correct_idx))
        n_wrong = min(7, len(wrong_idx))
        
        selected = []
        if len(correct_idx) > 0:
            selected.extend(np.random.choice(correct_idx, n_correct, replace=False))
        if len(wrong_idx) > 0:
            selected.extend(np.random.choice(wrong_idx, n_wrong, replace=False))
        
        table_data = []
        for i, idx in enumerate(selected[:num_samples]):
            text = str(texts[idx])
            text = (text[:70] + '...') if len(text) > 70 else text
            true_label = self.emotion_labels[y_true[idx]].capitalize()
            pred_label = self.emotion_labels[y_pred[idx]].capitalize()
            match = '✓' if y_true[idx] == y_pred[idx] else '✗'
            table_data.append([i+1, text, true_label, pred_label, match])
        
        table = ax.table(cellText=table_data,
                        colLabels=['#', 'Feedback Text', 'True Emotion', 'Predicted', 'Result'],
                        cellLoc='left',
                        loc='center',
                        colWidths=[0.05, 0.55, 0.15, 0.15, 0.08])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.5)
        
        # Style header
        for i in range(5):
            table[(0, i)].set_facecolor('#34495e')
            table[(0, i)].set_text_props(weight='bold', color='white', fontsize=10)
        
        # Color result column
        for i in range(1, len(table_data) + 1):
            if table_data[i-1][4] == '✓':
                table[(i, 4)].set_facecolor('#2ecc71')
                table[(i, 4)].set_text_props(weight='bold', fontsize=11)
            else:
                table[(i, 4)].set_facecolor('#e74c3c')
                table[(i, 4)].set_text_props(weight='bold', color='white', fontsize=11)
        
        plt.title(f'Sample Predictions - {self.model_name}',
                 fontsize=14, fontweight='bold', pad=20)
        plt.savefig(self.results_dir / '8_sample_predictions.png', bbox_inches='tight')
        plt.close()
        print(f"✅ Saved: 8_sample_predictions.png")
    
    def generate_all_visualizations(self, y_true, y_pred, y_pred_proba, 
                                   texts, log_history):
        """Generate all visualizations in one call"""
        print(f"\n{'='*80}")
        print(f"GENERATING COMPREHENSIVE VISUALIZATIONS - {self.model_name}")
        print(f"{'='*80}\n")
        
        # 1. Confusion Matrix
        self.plot_confusion_matrix(y_true, y_pred)
        
        # 2. Classification Metrics
        self.plot_classification_metrics(y_true, y_pred)
        
        # 3. ROC Curves
        self.plot_roc_curves(y_true, y_pred_proba)
        
        # 4. Precision-Recall Curves
        self.plot_precision_recall_curves(y_true, y_pred_proba)
        
        # 5. Training History
        self.plot_training_history(log_history)
        
        # 6. Confidence Histogram
        self.plot_confidence_histogram(y_pred_proba, y_pred)
        
        # 7. Error Analysis
        self.plot_error_analysis(texts, y_true, y_pred)
        
        # 8. Sample Predictions
        self.plot_sample_predictions(texts, y_true, y_pred)
        
        print(f"\n✅ All visualizations saved to: {self.results_dir}")
        print(f"{'='*80}\n")
