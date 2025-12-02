"""
Test script for GPT-Neo insight generation
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

print('='*100)
print('TESTING GPT-NEO INSIGHT GENERATOR')
print('='*100)

# Test data
test_topics = [
    {
        'topic': 'Topic 1',
        'keywords': ['teaching', 'explain', 'clear', 'understand', 'instructor'],
        'emotion_distribution': {'joy': 5, 'satisfaction': 8, 'acceptance': 12, 'boredom': 10, 'disappointment': 2},
        'feedback_count': 37
    },
    {
        'topic': 'Topic 2',
        'keywords': ['exam', 'test', 'difficult', 'grade', 'assessment'],
        'emotion_distribution': {'joy': 2, 'satisfaction': 3, 'acceptance': 8, 'boredom': 5, 'disappointment': 15},
        'feedback_count': 33
    }
]

print('\nLoading GPT-Neo model...')
from api.ml_models.insight_generator import get_insight_generator

try:
    generator = get_insight_generator()
    print('✅ Model loaded successfully!\n')
    
    # Generate insights
    print('Generating insights...\n')
    insights = generator.generate_insights_batch(test_topics)
    
    # Display results
    for topic_insight in insights:
        print('='*100)
        print(f"TOPIC: {topic_insight['topic']}")
        print('='*100)
        
        for insight in topic_insight['insights']:
            print(f"\nCategory: {insight['category']}")
            print(f"Priority: {insight['priority'].upper()}")
            print(f"Method: {insight['method']}")
            print(f"Suggestion: {insight['suggestion']}")
            print('-'*100)
    
    print('\n✅ GPT-Neo insight generation test completed successfully!')
    
except Exception as e:
    print(f'\n❌ Error: {str(e)}')
    import traceback
    traceback.print_exc()
