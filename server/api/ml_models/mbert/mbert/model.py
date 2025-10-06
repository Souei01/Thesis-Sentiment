from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import torch.nn.functional as F
import json
import os

class FineTunedmBERTEmotionAnalyzer:
    def __init__(self, model_path='./mbert-emotion-finetuned'):
        """
        Initialize fine-tuned mBERT model for emotion analysis
        """
        try:
            # Load the fine-tuned model and tokenizer
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model.eval()
            
            # Load label mapping
            with open(os.path.join(model_path, 'label_mapping.json'), 'r') as f:
                self.label_mapping = json.load(f)
            
            self.id_to_label = self.label_mapping['id_to_label']
            self.label_to_id = self.label_mapping['label_to_id']
            
            print("Fine-tuned mBERT model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading fine-tuned model: {e}")
            print("Falling back to zero-shot classification...")
            # Fallback to zero-shot classification if fine-tuned model not available
            self.use_zero_shot = True
            self.setup_zero_shot()
    
    def setup_zero_shot(self):
        """Setup zero-shot classification as fallback"""
        from transformers import pipeline
        self.model_name = "bert-base-multilingual-cased"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.classifier = pipeline(
            "zero-shot-classification",
            model=self.model_name,
            tokenizer=self.tokenizer
        )
        self.custom_labels = ["acceptance", "joy", "disappointment", "satisfaction", "boredom"]
        self.use_zero_shot = True
    
    def predict_emotion(self, text):
        """
        Predict emotion for given text
        Args:
            text (str): Input text for emotion analysis
        Returns:
            dict: Contains emotion label and confidence score
        """
        try:
            if hasattr(self, 'use_zero_shot') and self.use_zero_shot:
                return self.predict_zero_shot(text)
            else:
                return self.predict_fine_tuned(text)
                
        except Exception as e:
            return {"error": str(e)}
    
    def predict_fine_tuned(self, text):
        """Predict using fine-tuned model"""
        # Tokenize input text
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )
        
        # Make prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = F.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = torch.max(predictions).item()
        
        # Get emotion label
        emotion = self.id_to_label[str(predicted_class)]
        
        # Create scores for all emotions
        all_scores = {}
        for i, score in enumerate(predictions[0]):
            label = self.id_to_label[str(i)]
            all_scores[label] = score.item()
        
        return {
            "emotion": emotion,
            "confidence": round(confidence, 4),
            "all_scores": {k: round(v, 4) for k, v in all_scores.items()},
            "model": "Fine-tuned mBERT"
        }
    
    def predict_zero_shot(self, text):
        """Predict using zero-shot classification (fallback)"""
        result = self.classifier(text, self.custom_labels)
        
        top_emotion = result['labels'][0]
        top_confidence = result['scores'][0]
        
        all_scores = {
            label: score for label, score in zip(result['labels'], result['scores'])
        }
        
        return {
            "emotion": top_emotion,
            "confidence": round(top_confidence, 4),
            "all_scores": {k: round(v, 4) for k, v in all_scores.items()},
            "model": "mBERT Zero-shot"
        }
    
    def predict_batch(self, texts):
        """
        Predict emotion for multiple texts
        Args:
            texts (list): List of text strings
        Returns:
            list: List of prediction results
        """
        results = []
        for text in texts:
            result = self.predict_emotion(text)
            results.append(result)
        return results

# Initialize the emotion analyzer
emotion_analyzer = FineTunedmBERTEmotionAnalyzer()

# Test the model
if __name__ == "__main__":
    test_texts = [
        "I love this course! It's amazing!",
        "I'm so disappointed with this result.",
        "This class is okay, nothing special.",
        "The teacher explains everything perfectly!",
        "This lecture is so boring and repetitive.",
    ]
    
    print("Testing Fine-tuned mBERT Emotion Detection Model")
    print("=" * 80)
    
    for text in test_texts:
        result = emotion_analyzer.predict_emotion(text)
        print(f"Text: {text}")
        print(f"Predicted Emotion: {result.get('emotion', 'Error')}")
        print(f"Confidence: {result.get('confidence', 'N/A')}")
        print(f"All scores: {result.get('all_scores', {})}")
        print(f"Model: {result.get('model', 'Unknown')}")
        print("-" * 80)