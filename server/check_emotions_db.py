import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import Feedback

# Check if there are any feedback entries with emotions
feedbacks = Feedback.objects.filter(status='submitted')

print(f"Total submitted feedback: {feedbacks.count()}")
print("\n" + "="*80)

if feedbacks.exists():
    print("\nChecking emotion fields in feedback:")
    print("="*80)
    
    for fb in feedbacks[:5]:  # Check first 5
        print(f"\nFeedback ID: {fb.id}")
        print(f"  Suggested Changes: '{fb.suggested_changes[:50] if fb.suggested_changes else 'Empty'}...'")
        print(f"    -> Emotion: {fb.emotion_suggested_changes or 'NONE'}")
        
        print(f"  Best Aspect: '{fb.best_teaching_aspect[:50] if fb.best_teaching_aspect else 'Empty'}...'")
        print(f"    -> Emotion: {fb.emotion_best_aspect or 'NONE'}")
        
        print(f"  Least Aspect: '{fb.least_teaching_aspect[:50] if fb.least_teaching_aspect else 'Empty'}...'")
        print(f"    -> Emotion: {fb.emotion_least_aspect or 'NONE'}")
        
        print(f"  Further Comments: '{fb.further_comments[:50] if fb.further_comments else 'Empty'}...'")
        print(f"    -> Emotion: {fb.emotion_further_comments or 'NONE'}")
        
        print(f"  Confidence Scores: {fb.emotion_confidence_scores or 'NONE'}")
    
    # Count how many have emotions
    with_emotions = feedbacks.exclude(
        emotion_suggested_changes='',
        emotion_best_aspect='',
        emotion_least_aspect='',
        emotion_further_comments=''
    ).count()
    
    print("\n" + "="*80)
    print(f"\nFeedback with emotions predicted: {with_emotions} / {feedbacks.count()}")
    
    # Count by emotion type
    from django.db.models import Count
    
    print("\n" + "="*80)
    print("Emotion Distribution:")
    print("="*80)
    
    fields = [
        'emotion_suggested_changes',
        'emotion_best_aspect', 
        'emotion_least_aspect',
        'emotion_further_comments'
    ]
    
    emotion_counts = {}
    for field in fields:
        field_data = feedbacks.values(field).annotate(count=Count(field))
        for item in field_data:
            emotion = item[field]
            if emotion:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + item['count']
    
    print(f"\nTotal emotion predictions: {sum(emotion_counts.values())}")
    for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {emotion}: {count}")
    
else:
    print("No submitted feedback found in database!")
