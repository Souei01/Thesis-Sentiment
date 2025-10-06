import json
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)
from sklearn.metrics import accuracy_score, classification_report
import os

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
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    accuracy = accuracy_score(labels, predictions)
    return {'accuracy': accuracy}

def fine_tune_mbert():
    # Load prepared data
    try:
        with open('train_data.json', 'r') as f:
            train_data = json.load(f)
        
        with open('val_data.json', 'r') as f:
            val_data = json.load(f)
            
        with open('label_mapping.json', 'r') as f:
            label_mapping = json.load(f)
            
    except FileNotFoundError:
        print("Training data files not found. Run prepare_training_data.py first.")
        return
    
    # Initialize tokenizer and model
    model_name = "bert-base-multilingual-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    num_labels = len(label_mapping['id_to_label'])
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels
    )
    
    # Create datasets
    train_dataset = EmotionDataset(
        train_data['texts'],
        train_data['labels'],
        tokenizer
    )
    
    val_dataset = EmotionDataset(
        val_data['texts'],
        val_data['labels'],
        tokenizer
    )
    
    # Training arguments - CORRECTED VERSION
    training_args = TrainingArguments(
        output_dir='./mbert-emotion-finetuned',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        eval_strategy="steps",  # Changed from evaluation_strategy
        eval_steps=100,
        save_strategy="steps",
        save_steps=100,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
        save_total_limit=2,
        seed=42,
        dataloader_num_workers=0,  # Set to 0 for Windows
        use_cpu=True,  # Force CPU usage for compatibility
        report_to=None,  # Disable wandb/tensorboard logging
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_bdataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )
    
    # Fine-tune the model
    print("Starting fine-tuning...")
    trainer.train()
    
    # Evaluate the model
    print("Evaluating model...")
    eval_results = trainer.evaluate()
    print(f"Evaluation results: {eval_results}")
    
    # Save the fine-tuned model
    model.save_pretrained('./mbert-emotion-finetuned')
    tokenizer.save_pretrained('./mbert-emotion-finetuned')
    
    # Save label mapping with the model
    with open('./mbert-emotion-finetuned/label_mapping.json', 'w') as f:
        json.dump(label_mapping, f, indent=2)
    
    print("Fine-tuning completed!")
    print("Model saved to: ./mbert-emotion-finetuned")
    
    # Test predictions
    test_predictions(model, tokenizer, label_mapping)

def test_predictions(model, tokenizer, label_mapping):
    print("\nTesting fine-tuned model...")
    
    test_texts = [
        "I love this course! It's amazing!",
        "I'm so disappointed with this result.",
        "This class is okay, nothing special.",
        "The teacher explains everything perfectly!",
        "This lecture is so boring and repetitive."
    ]
    
    model.eval()
    for text in test_texts:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )
        
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = torch.max(predictions).item()
        
        predicted_emotion = label_mapping['id_to_label'][str(predicted_class)]
        
        print(f"Text: {text}")
        print(f"Predicted Emotion: {predicted_emotion}")
        print(f"Confidence: {confidence:.4f}")
        print("-" * 50)

if __name__ == "__main__":
    fine_tune_mbert()