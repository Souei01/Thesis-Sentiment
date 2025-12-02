"""
XLM-RoBERTa Emotion Predictor
Loads the fine-tuned model and provides emotion prediction for student feedback
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Emotion labels (based on your training data)
EMOTION_LABELS = [
    'joy',
    'satisfaction',
    'acceptance',
    'boredom',
    'disappointment'
]


class EmotionPredictor:
    """
    Singleton class for XLM-RoBERTa emotion prediction
    """
    _instance = None
    _model = None
    _tokenizer = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmotionPredictor, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Load the model and tokenizer"""
        try:
            # Path to the fine-tuned model
            model_path = Path(__file__).parent.parent.parent / 'ml_models' / 'xlm_roberta_finetuned'
            
            logger.info(f"Loading XLM-RoBERTa model from {model_path}")
            
            # Check if CUDA is available
            self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"Using device: {self._device}")
            
            # Load tokenizer and model
            self._tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            self._model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
            self._model.to(self._device)
            self._model.eval()
            
            logger.info("✅ XLM-RoBERTa model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading XLM-RoBERTa model: {str(e)}")
            raise
    
    def predict(self, text, return_all_scores=False):
        """
        Predict emotion for given text
        
        Args:
            text (str): Input text to analyze
            return_all_scores (bool): If True, return confidence scores for all emotions
        
        Returns:
            dict: {
                'emotion': str (predicted emotion label),
                'confidence': float (confidence score 0-1),
                'all_scores': dict (optional, all emotion scores)
            }
        """
        if not text or not isinstance(text, str) or text.strip() == '':
            return {
                'emotion': 'acceptance',
                'confidence': 1.0,
                'all_scores': {label: 0.0 for label in EMOTION_LABELS} if return_all_scores else None
            }
        
        try:
            # Tokenize input
            inputs = self._tokenizer(
                text,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # Move inputs to device
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
                
            # Apply softmax to get probabilities
            probs = torch.softmax(logits, dim=-1)
            probs = probs.cpu().numpy()[0]
            
            # Get predicted emotion
            predicted_idx = np.argmax(probs)
            predicted_emotion = EMOTION_LABELS[predicted_idx]
            confidence = float(probs[predicted_idx])
            
            result = {
                'emotion': predicted_emotion,
                'confidence': confidence
            }
            
            # Add all scores if requested
            if return_all_scores:
                result['all_scores'] = {
                    label: float(probs[i]) for i, label in enumerate(EMOTION_LABELS)
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting emotion: {str(e)}")
            return {
                'emotion': 'acceptance',
                'confidence': 0.0,
                'all_scores': {label: 0.0 for label in EMOTION_LABELS} if return_all_scores else None
            }
    
    def predict_batch(self, texts, return_all_scores=False):
        """
        Predict emotions for multiple texts at once (more efficient)
        
        Args:
            texts (list): List of text strings
            return_all_scores (bool): If True, return confidence scores for all emotions
        
        Returns:
            list: List of prediction dictionaries
        """
        results = []
        
        # Handle empty texts
        processed_texts = []
        for text in texts:
            if not text or not isinstance(text, str) or text.strip() == '':
                processed_texts.append('[EMPTY]')
            else:
                processed_texts.append(text)
        
        try:
            # Tokenize all inputs at once
            inputs = self._tokenizer(
                processed_texts,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # Move inputs to device
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
            
            # Apply softmax to get probabilities
            probs = torch.softmax(logits, dim=-1)
            probs = probs.cpu().numpy()
            
            # Process each prediction
            for i, text in enumerate(texts):
                if not text or not isinstance(text, str) or text.strip() == '':
                    results.append({
                        'emotion': 'acceptance',
                        'confidence': 1.0,
                        'all_scores': {label: 0.0 for label in EMOTION_LABELS} if return_all_scores else None
                    })
                else:
                    predicted_idx = np.argmax(probs[i])
                    predicted_emotion = EMOTION_LABELS[predicted_idx]
                    confidence = float(probs[i][predicted_idx])
                    
                    result = {
                        'emotion': predicted_emotion,
                        'confidence': confidence
                    }
                    
                    if return_all_scores:
                        result['all_scores'] = {
                            label: float(probs[i][j]) for j, label in enumerate(EMOTION_LABELS)
                        }
                    
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch prediction: {str(e)}")
            # Return acceptance for all on error
            return [{
                'emotion': 'acceptance',
                'confidence': 0.0,
                'all_scores': {label: 0.0 for label in EMOTION_LABELS} if return_all_scores else None
            } for _ in texts]


# Singleton instance
_predictor = None

def get_emotion_predictor():
    """Get or create the emotion predictor singleton"""
    global _predictor
    if _predictor is None:
        _predictor = EmotionPredictor()
    return _predictor


def predict_emotion(text, return_all_scores=False):
    """
    Convenience function to predict emotion for a single text
    
    Args:
        text (str): Input text
        return_all_scores (bool): Return all emotion scores
    
    Returns:
        dict: Prediction result
    """
    predictor = get_emotion_predictor()
    return predictor.predict(text, return_all_scores)


def predict_emotions_batch(texts, return_all_scores=False):
    """
    Convenience function to predict emotions for multiple texts
    
    Args:
        texts (list): List of input texts
        return_all_scores (bool): Return all emotion scores
    
    Returns:
        list: List of prediction results
    """
    predictor = get_emotion_predictor()
    return predictor.predict_batch(texts, return_all_scores)
