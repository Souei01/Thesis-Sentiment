"""
GPT-Neo based insight generator for course improvement recommendations
Uses GPT-Neo model to generate actionable insights from LDA topics and emotion analysis
"""

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import logging

logger = logging.getLogger(__name__)


class InsightGenerator:
    """Singleton class for GPT-Neo insight generation"""
    
    _instance = None
    _model = None
    _tokenizer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InsightGenerator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load GPT-Neo model and tokenizer"""
        try:
            logger.info("Loading GPT-Neo model for insight generation...")
            
            # Using GPT-2 medium as it's lighter than GPT-Neo but still effective
            # For GPT-Neo: use 'EleutherAI/gpt-neo-125M' or 'EleutherAI/gpt-neo-1.3B'
            model_name = 'gpt2-medium'  # 355M parameters, good balance
            
            self._tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            self._model = GPT2LMHeadModel.from_pretrained(model_name)
            
            # Set padding token
            self._tokenizer.pad_token = self._tokenizer.eos_token
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self._model = self._model.to('cuda')
                logger.info("✅ GPT-Neo model loaded on GPU")
            else:
                logger.info("✅ GPT-Neo model loaded on CPU")
                
        except Exception as e:
            logger.error(f"Error loading GPT-Neo model: {str(e)}")
            raise
    
    def generate_insight(self, topic_name, keywords, emotion_dist, category='general', max_length=150):
        """
        Generate a single insight using GPT-Neo
        
        Args:
            topic_name: Name of the topic (e.g., "Topic 1")
            keywords: List of topic keywords
            emotion_dist: Dictionary of emotion counts
            category: Category of insight (teaching, assessment, etc.)
            max_length: Maximum length of generated text
            
        Returns:
            Generated insight text
        """
        try:
            # Calculate emotion percentages
            total_emotions = sum(emotion_dist.values())
            if total_emotions == 0:
                return "Students provided feedback on this topic. Continue monitoring responses and implement standard teaching best practices."
            
            emotion_percentages = {
                emotion: (count / total_emotions * 100) 
                for emotion, count in emotion_dist.items()
            }
            
            # Get dominant emotion
            dominant_emotion = max(emotion_percentages.items(), key=lambda x: x[1])
            
            # Create prompt
            keyword_str = ', '.join(keywords[:5])
            emotion_str = f"{dominant_emotion[0]} ({dominant_emotion[1]:.0f}%)"
            
            # Calculate sentiment
            negative = emotion_percentages.get('boredom', 0) + emotion_percentages.get('disappointment', 0)
            positive = emotion_percentages.get('joy', 0) + emotion_percentages.get('satisfaction', 0)
            
            prompt = self._create_improved_prompt(category, keyword_str, emotion_str, negative, positive)
            
            # Generate text
            inputs = self._tokenizer(prompt, return_tensors='pt', padding=True, truncation=True, max_length=256)
            
            if torch.cuda.is_available():
                inputs = {k: v.to('cuda') for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self._model.generate(
                    inputs['input_ids'],
                    max_new_tokens=60,  # Shorter for more focused output
                    num_return_sequences=1,
                    temperature=0.7,  # Lower for more focused output
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self._tokenizer.eos_token_id,
                    no_repeat_ngram_size=2,
                    repetition_penalty=1.3,
                    bad_words_ids=self._get_bad_words()  # Filter unwanted tokens
                )
            
            generated_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part (after prompt)
            insight = generated_text[len(prompt):].strip()
            
            # Clean up the insight
            insight = self._clean_insight_improved(insight)
            
            return insight
            
        except Exception as e:
            logger.error(f"Error generating insight: {str(e)}")
            return f"Review feedback related to {keywords[0] if keywords else 'this topic'} and implement appropriate teaching improvements."
    
    def _create_improved_prompt(self, category, keywords, emotion_str, negative_pct, positive_pct):
        """Create improved, more directive prompts"""
        
        if category == 'teaching':
            if negative_pct > 40:
                return f"Students report {emotion_str} about teaching ({keywords}). Action needed: "
            else:
                return f"Teaching feedback shows {emotion_str} regarding {keywords}. Recommendation: "
        
        elif category == 'assessment':
            return f"Assessment concerns ({keywords}). Student emotion: {emotion_str}. Improve by: "
        
        elif category == 'materials':
            return f"Course materials feedback ({keywords}). Students feel {emotion_str}. Enhancement: "
        
        elif category == 'engagement':
            if negative_pct > 40:
                return f"Low engagement detected ({keywords}). Emotion: {emotion_str}. Boost engagement: "
            else:
                return f"Engagement level ({keywords}): {emotion_str}. Maintain by: "
        
        elif category == 'communication':
            return f"Communication feedback ({keywords}). Sentiment: {emotion_str}. Improve: "
        
        elif category == 'organization':
            return f"Course structure ({keywords}). Student response: {emotion_str}. Organize better: "
        
        else:
            return f"Course feedback ({keywords}). Emotion: {emotion_str}. Action: "
    
    def _get_bad_words(self):
        """Get list of bad word IDs to filter out (HTML tags, etc.)"""
        bad_words = ['<', '>', 'iframe', 'div', 'html', '<!--', '-->', '<br', '</']
        bad_ids = []
        for word in bad_words:
            try:
                ids = self._tokenizer.encode(word, add_special_tokens=False)
                bad_ids.extend(ids)
            except:
                pass
        return [[id] for id in bad_ids] if bad_ids else None
    
    def _clean_insight_improved(self, insight):
        """Improved cleaning of generated insight"""
        if not insight:
            return "Monitor student feedback and implement appropriate improvements."
        
        # Remove HTML tags and weird characters
        import re
        insight = re.sub(r'<[^>]+>', '', insight)  # Remove HTML tags
        insight = re.sub(r'<!--.*?-->', '', insight)  # Remove HTML comments
        insight = re.sub(r'\s+', ' ', insight)  # Normalize whitespace
        
        # Take first complete sentence
        sentences = insight.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 20:  # Must be substantial
                if not first_sentence.endswith('.'):
                    first_sentence += '.'
                return first_sentence
        
        # Fallback: take first 100 chars
        if len(insight) > 100:
            insight = insight[:100].rsplit(' ', 1)[0] + '...'
        
        # If still problematic, use fallback
        if len(insight) < 20 or any(char in insight for char in ['<', '>', '{', '}']):
            return "Implement teaching improvements based on student feedback and monitor results."
        
        return insight.strip()
    
    def generate_insights_batch(self, topics_data):
        """
        Generate insights for multiple topics
        
        Args:
            topics_data: List of dictionaries with topic info
            
        Returns:
            List of insights for each topic
        """
        all_insights = []
        
        for topic_info in topics_data:
            topic_name = topic_info['topic']
            keywords = topic_info['keywords']
            emotion_dist = topic_info.get('emotion_distribution', {})
            
            logger.info(f"Generating insights for {topic_name}...")
            
            # Determine categories based on keywords
            categories = self._determine_categories(keywords)
            
            topic_insights = []
            for category in categories:
                insight_text = self.generate_insight(
                    topic_name, 
                    keywords, 
                    emotion_dist, 
                    category=category
                )
                
                # Determine priority based on emotions
                priority = self._determine_priority(emotion_dist)
                
                topic_insights.append({
                    'category': category.replace('_', ' ').title(),
                    'priority': priority,
                    'suggestion': insight_text,
                    'icon': self._get_icon(category),
                    'method': 'gpt-neo'
                })
            
            all_insights.append({
                'topic': topic_name,
                'insights': topic_insights
            })
        
        return all_insights
    
    def _determine_categories(self, keywords):
        """Determine relevant categories based on keywords"""
        keyword_set = set([k.lower() for k in keywords])
        categories = []
        
        if any(word in keyword_set for word in ['teaching', 'teach', 'instructor', 'explain', 'lecture']):
            categories.append('teaching')
        
        if any(word in keyword_set for word in ['exam', 'test', 'grade', 'assessment', 'quiz']):
            categories.append('assessment')
        
        if any(word in keyword_set for word in ['material', 'book', 'slide', 'resource', 'content']):
            categories.append('materials')
        
        if any(word in keyword_set for word in ['engaging', 'boring', 'interesting', 'attention']):
            categories.append('engagement')
        
        if any(word in keyword_set for word in ['feedback', 'communicate', 'response', 'question']):
            categories.append('communication')
        
        if any(word in keyword_set for word in ['organize', 'structure', 'plan', 'syllabus']):
            categories.append('organization')
        
        # If no specific category, use general
        if not categories:
            categories.append('general')
        
        return categories[:2]  # Limit to 2 categories per topic
    
    def _determine_priority(self, emotion_dist):
        """Determine priority level based on emotion distribution"""
        total = sum(emotion_dist.values())
        if total == 0:
            return 'medium'
        
        negative = emotion_dist.get('boredom', 0) + emotion_dist.get('disappointment', 0)
        negative_pct = (negative / total) * 100
        
        if negative_pct > 50:
            return 'high'
        elif negative_pct > 25:
            return 'medium'
        else:
            return 'low'
    
    def _get_icon(self, category):
        """Get icon name for category"""
        icon_map = {
            'teaching': 'presentation',
            'assessment': 'clipboard',
            'materials': 'book',
            'engagement': 'users',
            'communication': 'message',
            'organization': 'folder',
            'general': 'info'
        }
        return icon_map.get(category, 'info')


# Singleton instance
_insight_generator = None

def get_insight_generator():
    """Get or create the insight generator singleton"""
    global _insight_generator
    if _insight_generator is None:
        _insight_generator = InsightGenerator()
    return _insight_generator
