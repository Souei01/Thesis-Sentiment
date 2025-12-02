# Fine-tune XLM-RoBERTa for Emotion Classification
# Using FEEDBACK ONLY format (proven best - 78.5% accuracy with RoBERTa)

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable CUDA completely

import pandas as pd
import numpy as np
import torch
import re
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer, EarlyStoppingCallback
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, roc_curve, auc
import time
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from comprehensive_visualizations import ComprehensiveVisualizer

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
        encoding = self.tokenizer(text, add_special_tokens=True, max_length=self.max_length, padding='max_length', truncation=True, return_tensors='pt')
        return {'input_ids': encoding['input_ids'].flatten(), 'attention_mask': encoding['attention_mask'].flatten(), 'labels': torch.tensor(label, dtype=torch.long)}

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    acc = accuracy_score(labels, preds)
    return {'accuracy': acc, 'f1': f1, 'precision': precision, 'recall': recall}

def preprocess_text(text):
    """Enhanced text preprocessing for better accuracy"""
    text = str(text)
    
    # Expand common contractions
    contractions = {
        "don't": "do not", "doesn't": "does not", "didn't": "did not",
        "can't": "cannot", "couldn't": "could not", "won't": "will not",
        "wouldn't": "would not", "shouldn't": "should not",
        "isn't": "is not", "aren't": "are not", "wasn't": "was not",
        "weren't": "were not", "haven't": "have not", "hasn't": "has not",
        "hadn't": "had not", "i'm": "i am", "you're": "you are",
        "he's": "he is", "she's": "she is", "it's": "it is",
        "we're": "we are", "they're": "they are"
    }
    
    for contraction, expansion in contractions.items():
        text = text.replace(contraction, expansion)
        text = text.replace(contraction.capitalize(), expansion.capitalize())
    
    # Normalize multiple punctuation but keep emotional indicators
    text = re.sub(r'!!+', '!', text)
    text = re.sub(r'\?\?+', '?', text)
    text = re.sub(r'\.\.\.+', '...', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def main():
    print('='*80)
    print('FINE-TUNING XLM-RoBERTa FOR EMOTION CLASSIFICATION')
    print('Using FEEDBACK ONLY format (proven best: 78.5% with RoBERTa)')
    print('='*80)
    
    # Force CPU - GPU too new (RTX 5060 sm_120 not supported by PyTorch yet)
    device = torch.device('cpu')
    print(f'Device: {device} (GPU sm_120 not yet supported - waiting for PyTorch update)')
    print('Training will take ~40-50 minutes on CPU (5 epochs, optimized hyperparameters)')
    print()
    
    print('Loading data...')
    train_df = pd.read_csv('data/annotations/train_data.csv')
    test_df = pd.read_csv('data/annotations/test_data.csv')
    print(f'Training samples: {len(train_df)}')
    print(f'Test samples: {len(test_df)}\n')
    
    # Use FEEDBACK ONLY (proven best format) with enhanced preprocessing
    train_df['text'] = train_df['feedback'].apply(preprocess_text)
    test_df['text'] = test_df['feedback'].apply(preprocess_text)
    print('📊 Input Format: FEEDBACK ONLY (enhanced preprocessing)')
    print('   Dataset: Pre-split train_data.csv and test_data.csv')
    print()
    
    label_dict = {'joy': 0, 'satisfaction': 1, 'acceptance': 2, 'boredom': 3, 'disappointment': 4}
    
    train_texts = train_df['text'].tolist()
    train_labels = train_df['label_id'].tolist()
    val_texts = test_df['text'].tolist()
    val_labels = test_df['label_id'].tolist()
    
    print('Loading XLM-RoBERTa...')
    tokenizer = AutoTokenizer.from_pretrained('ml_models/xlm_roberta')
    model = AutoModelForSequenceClassification.from_pretrained('ml_models/xlm_roberta', num_labels=5, id2label={v:k for k,v in label_dict.items()}, label2id=label_dict)
    model.to(device)
    print('Model loaded\\n')
    
    train_dataset = EmotionDataset(train_texts, train_labels, tokenizer)
    val_dataset = EmotionDataset(val_texts, val_labels, tokenizer)
    
    output_dir = 'ml_models/xlm_roberta_finetuned'
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        learning_rate=2e-5,
        warmup_ratio=0.1,
        weight_decay=0.01,
        logging_steps=50,
        eval_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='f1',
        report_to='none',
        fp16=False
    )
    
    trainer = Trainer(model=model, args=training_args, train_dataset=train_dataset, eval_dataset=val_dataset, compute_metrics=compute_metrics, callbacks=[EarlyStoppingCallback(early_stopping_patience=2)])
    
    print('='*80)
    print('STARTING TRAINING')
    print('='*80)
    
    start_time = time.time()
    trainer.train()
    print(f'\\nTraining time: {(time.time()-start_time)/60:.2f} minutes\\n')
    
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print('='*80)
    print('EVALUATION')
    print('='*80)
    eval_results = trainer.evaluate()
    print(f'Accuracy: {eval_results["eval_accuracy"]*100:.2f}%')
    print(f'F1 Score: {eval_results["eval_f1"]:.4f}\\n')
    
    predictions = trainer.predict(val_dataset)
    pred_labels = predictions.predictions.argmax(-1)
    pred_probs = torch.nn.functional.softmax(torch.tensor(predictions.predictions), dim=1).numpy()
    true_labels = predictions.label_ids
    emotion_labels = ['joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment']
    
    precision, recall, f1, support = precision_recall_fscore_support(true_labels, pred_labels, labels=list(range(5)), zero_division=0)
    
    print('Per-Emotion:')
    for i, emotion in enumerate(emotion_labels):
        print(f'{emotion:15} P:{precision[i]:.3f} R:{recall[i]:.3f} F1:{f1[i]:.3f}')
    print()
    
    # Generate Comprehensive Visualizations
    results_dir = 'results/xlm_roberta_finetuned'
    visualizer = ComprehensiveVisualizer('XLM-RoBERTa Fine-tuned', results_dir, emotion_labels)
    visualizer.generate_all_visualizations(
        y_true=true_labels,
        y_pred=pred_labels,
        y_pred_proba=pred_probs,
        texts=val_texts,
        log_history=trainer.state.log_history
    )
    
    print()
    print('='*80)
    print('COMPARISON WITH OTHER MODELS')
    print('='*80)
    print(f"{'Model':<20} {'Accuracy':<12} {'F1 Score':<12} {'Input Format':<20}")
    print('-'*80)
    print(f"{'RoBERTa':<20} {'78.50%':<12} {'0.7859':<12} {'Feedback Only':<20}")
    print(f"{'DistilBERT':<20} {'77.00%':<12} {'0.7706':<12} {'Feedback Only':<20}")
    print(f"{'mBERT':<20} {'76.50%':<12} {'0.7656':<12} {'Feedback Only':<20}")
    print(f"{'XLM-RoBERTa':<20} {f'{eval_results["eval_accuracy"]*100:.2f}%':<12} {f'{eval_results["eval_f1"]:.4f}':<12} {'Feedback Only':<20}")
    print('-'*80)
    
    print()
    print('COMPLETE! Model saved to:', output_dir)
    print(f'Visualizations saved to: {results_dir}')
    print('='*80)

if __name__ == '__main__':
    main()
