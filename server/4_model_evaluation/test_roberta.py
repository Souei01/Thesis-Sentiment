"""
Interactive Emotion Prediction Tool
Test RoBERTa model with your own feedback text
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

def predict_emotion(text, model, tokenizer, emotion_labels):
    """Predict emotion from text"""
    # Preprocess
    processed_text = preprocess_text(text)
    
    # Tokenize
    encoding = tokenizer(
        processed_text,
        add_special_tokens=True,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )
    
    # Predict
    with torch.no_grad():
        outputs = model(input_ids=encoding['input_ids'], attention_mask=encoding['attention_mask'])
        probs = torch.nn.functional.softmax(outputs.logits, dim=1).squeeze()
        pred_label = outputs.logits.argmax(-1).item()
    
    return pred_label, probs

def main():
    print('='*80)
    print('🎯 EMOTION PREDICTION TOOL - RoBERTa Fine-tuned Model')
    print('='*80)
    
    # Load model
    print('\nLoading RoBERTa model...')
    model_path = 'ml_models/roberta_finetuned'
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model.eval()
    print('✅ Model loaded successfully!\n')
    
    emotion_labels = ['joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment']
    emotion_emojis = ['😊', '👍', '😐', '😴', '😞']
    
    print('='*80)
    print('Emotion Labels:')
    for emoji, label in zip(emotion_emojis, emotion_labels):
        print(f'  {emoji} {label.capitalize()}')
    print('='*80)
    print('\nType your feedback below (or "quit" to exit)')
    print('='*80)
    
    while True:
        try:
            # Get user input
            feedback = input('\n💬 Your feedback: ').strip()
            
            if feedback.lower() in ['quit', 'exit', 'q']:
                print('\n👋 Goodbye!')
                break
            
            if not feedback:
                print('⚠️  Please enter some text.')
                continue
            
            # Predict
            pred_label, probs = predict_emotion(feedback, model, tokenizer, emotion_labels)
            predicted_emotion = emotion_labels[pred_label]
            predicted_emoji = emotion_emojis[pred_label]
            confidence = probs[pred_label].item() * 100
            
            # Display results
            print(f'\n{"="*80}')
            print(f'📝 Input: "{feedback}"')
            print(f'{"="*80}')
            print(f'\n✨ Predicted Emotion: {predicted_emoji} {predicted_emotion.upper()} ({confidence:.1f}% confidence)')
            print(f'\n📊 All Probabilities:')
            
            # Sort by confidence
            sorted_indices = torch.argsort(probs, descending=True)
            
            for idx in sorted_indices:
                prob = probs[idx].item()
                emotion = emotion_labels[idx]
                emoji = emotion_emojis[idx]
                bar_length = int(prob * 40)
                bar = '█' * bar_length + '░' * (40 - bar_length)
                
                # Highlight predicted emotion
                if idx == pred_label:
                    print(f'   {emoji} {emotion.capitalize():<18} {prob*100:>6.2f}%  [{bar}] ⭐')
                else:
                    print(f'   {emoji} {emotion.capitalize():<18} {prob*100:>6.2f}%  [{bar}]')
            
            print('='*80)
            
        except KeyboardInterrupt:
            print('\n\n👋 Goodbye!')
            break
        except Exception as e:
            print(f'\n❌ Error: {e}')

if __name__ == '__main__':
    main()
