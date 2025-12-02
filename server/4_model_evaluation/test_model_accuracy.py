"""
Interactive Model Testing Script
Test any fine-tuned emotion classification model in the terminal
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import pandas as pd
import numpy as np
import torch
import re
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
import sys

def preprocess_text(text):
    """Enhanced preprocessing"""
    contractions = {
        "can't": "cannot", "won't": "will not", "n't": " not",
        "i'm": "i am", "you're": "you are", "it's": "it is",
        "that's": "that is", "what's": "what is", "there's": "there is"
    }
    text = str(text).lower()
    for contraction, expansion in contractions.items():
        text = text.replace(contraction, expansion)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class EmotionDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
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

def test_model(model_name):
    """Test a specific model and display results"""
    
    model_paths = {
        'roberta': 'ml_models/roberta_finetuned',
        'xlm-roberta': 'ml_models/xlm_roberta_finetuned',
        'mbert': 'ml_models/mbert_finetuned',
        'distilbert': 'ml_models/distilbert_finetuned'
    }
    
    if model_name.lower() not in model_paths:
        print(f"❌ Model '{model_name}' not found!")
        print(f"Available models: {', '.join(model_paths.keys())}")
        return
    
    model_path = model_paths[model_name.lower()]
    
    print('='*80)
    print(f'TESTING {model_name.upper()} MODEL ACCURACY')
    print('='*80)
    
    # Load test data
    print('Loading test data...')
    test_df = pd.read_csv('data/annotations/test_data.csv')
    test_texts = [preprocess_text(text) for text in test_df['feedback'].tolist()]
    test_labels = test_df['label_id'].tolist()
    print(f'✓ Loaded {len(test_texts)} test samples')
    
    # Load model
    print(f'\nLoading {model_name} model...')
    try:
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model.eval()
        print('✓ Model loaded successfully')
    except Exception as e:
        print(f'❌ Error loading model: {e}')
        return
    
    # Create dataset
    test_dataset = EmotionDataset(test_texts, test_labels, tokenizer)
    
    # Get predictions
    print('\nEvaluating model...')
    predictions_list = []
    true_labels_list = []
    
    with torch.no_grad():
        for i in range(len(test_dataset)):
            item = test_dataset[i]
            input_ids = item['input_ids'].unsqueeze(0)
            attention_mask = item['attention_mask'].unsqueeze(0)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            predictions_list.append(outputs.logits.cpu().numpy())
            true_labels_list.append(item['labels'].item())
    
    predictions_array = np.vstack(predictions_list)
    pred_labels = predictions_array.argmax(-1)
    true_labels = np.array(true_labels_list)
    
    emotion_labels = ['joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment']
    
    # Calculate metrics
    accuracy = accuracy_score(true_labels, pred_labels)
    precision, recall, f1, support = precision_recall_fscore_support(
        true_labels, pred_labels, labels=list(range(5)), zero_division=0
    )
    
    # Display results
    print('\n' + '='*80)
    print(f'RESULTS - {model_name.upper()}')
    print('='*80)
    print(f'\n📊 Overall Accuracy: {accuracy*100:.2f}%')
    print(f'📊 Overall F1 Score: {f1.mean():.4f}')
    print('\n' + '-'*80)
    print('Per-Emotion Performance:')
    print('-'*80)
    print(f'{"Emotion":<18} {"Precision":<12} {"Recall":<12} {"F1-Score":<12} {"Support":<10}')
    print('-'*80)
    
    for i, emotion in enumerate(emotion_labels):
        print(f'{emotion.capitalize():<18} {precision[i]:<12.3f} {recall[i]:<12.3f} {f1[i]:<12.3f} {support[i]:<10}')
    
    print('-'*80)
    print(f'{"Macro Avg":<18} {precision.mean():<12.3f} {recall.mean():<12.3f} {f1.mean():<12.3f} {support.sum():<10}')
    print('='*80)
    
    # Confusion Matrix
    cm = confusion_matrix(true_labels, pred_labels)
    print('\n📈 Confusion Matrix:')
    print('    ' + '  '.join([f'{e[:3]:>5}' for e in emotion_labels]))
    for i, emotion in enumerate(emotion_labels):
        print(f'{emotion[:3]:>3} ' + '  '.join([f'{cm[i][j]:>5}' for j in range(5)]))
    
    print('\n' + '='*80)

def test_single_text(model_name, text):
    """Test a single text input"""
    
    model_paths = {
        'roberta': 'ml_models/roberta_finetuned',
        'xlm-roberta': 'ml_models/xlm_roberta_finetuned',
        'mbert': 'ml_models/mbert_finetuned',
        'distilbert': 'ml_models/distilbert_finetuned'
    }
    
    if model_name.lower() not in model_paths:
        print(f"❌ Model '{model_name}' not found!")
        return
    
    model_path = model_paths[model_name.lower()]
    
    print(f'\n🔍 Testing with {model_name.upper()}...')
    
    # Load model
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model.eval()
    
    # Preprocess and tokenize
    processed_text = preprocess_text(text)
    encoding = tokenizer(
        processed_text,
        add_special_tokens=True,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )
    
    # Get prediction
    with torch.no_grad():
        outputs = model(input_ids=encoding['input_ids'], attention_mask=encoding['attention_mask'])
        probs = torch.nn.functional.softmax(outputs.logits, dim=1).squeeze()
        pred_label = outputs.logits.argmax(-1).item()
    
    emotion_labels = ['joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment']
    
    print(f'\n📝 Input: "{text}"')
    print(f'✅ Predicted Emotion: {emotion_labels[pred_label].upper()}')
    print(f'\n📊 Confidence Scores:')
    for i, emotion in enumerate(emotion_labels):
        bar = '█' * int(probs[i].item() * 50)
        print(f'   {emotion.capitalize():<18} {probs[i].item()*100:>6.2f}% {bar}')
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('='*80)
        print('MODEL ACCURACY TESTING TOOL')
        print('='*80)
        print('\nUsage:')
        print('  1. Test model accuracy on test dataset:')
        print('     python test_model_accuracy.py <model_name>')
        print('\n  2. Test single text input:')
        print('     python test_model_accuracy.py <model_name> "your feedback text here"')
        print('\nAvailable models:')
        print('  - roberta')
        print('  - xlm-roberta')
        print('  - mbert')
        print('  - distilbert')
        print('\nExamples:')
        print('  python test_model_accuracy.py roberta')
        print('  python test_model_accuracy.py roberta "This class is so boring"')
        print('='*80)
        sys.exit(1)
    
    model_name = sys.argv[1]
    
    if len(sys.argv) >= 3:
        # Single text prediction
        text = ' '.join(sys.argv[2:])
        test_single_text(model_name, text)
    else:
        # Full accuracy test
        test_model(model_name)
