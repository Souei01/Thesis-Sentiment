"""
Interactive Emotion Prediction Tool
Input feedback text and get emotion predictions from RoBERTa model
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import torch
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification

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

print('='*80)
print('EMOTION PREDICTION - RoBERTa Model')
print('='*80)

# Load model
print('\nLoading RoBERTa model...')
model = AutoModelForSequenceClassification.from_pretrained('ml_models/roberta_finetuned')
tokenizer = AutoTokenizer.from_pretrained('ml_models/roberta_finetuned')
model.eval()
print('✅ Model loaded successfully\n')

emotion_labels = ['Joy', 'Satisfaction', 'Acceptance', 'Boredom', 'Disappointment']

print('Enter your feedback (or type "exit" to quit):')
print('-'*80)

while True:
    # Get user input
    text = input('\n📝 Feedback: ').strip()
    
    if text.lower() in ['exit', 'quit', 'q']:
        print('\nGoodbye! 👋')
        break
    
    if not text:
        print('⚠️  Please enter some feedback text')
        continue
    
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
        confidence = probs[pred_label].item()
    
    # Display result
    print(f'\n🎯 Predicted Emotion: {emotion_labels[pred_label].upper()} ({confidence*100:.1f}% confidence)')
    print(f'\n📊 All Scores:')
    
    # Sort by probability
    sorted_emotions = sorted(zip(emotion_labels, probs.tolist()), key=lambda x: x[1], reverse=True)
    
    for emotion, prob in sorted_emotions:
        bar = '█' * int(prob * 40)
        print(f'   {emotion:<15} {prob*100:>6.2f}% {bar}')
    
    print('-'*80)
