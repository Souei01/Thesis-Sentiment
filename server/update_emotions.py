import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import Feedback
from api.ml_models.emotion_predictor import predict_emotions_batch

print("="*80)
print("UPDATING EXISTING FEEDBACK WITH EMOTION PREDICTIONS")
print("="*80)

# Get all submitted feedback without emotions
feedbacks = Feedback.objects.filter(status='submitted')

print(f"\nTotal submitted feedback: {feedbacks.count()}")

# Update each feedback with emotion predictions
updated_count = 0

for fb in feedbacks:
    # Collect text fields
    texts = [
        fb.suggested_changes or '',
        fb.best_teaching_aspect or '',
        fb.least_teaching_aspect or '',
        fb.further_comments or ''
    ]
    
    print(f"\nProcessing Feedback ID {fb.id}...")
    
    # Predict emotions
    try:
        emotion_predictions = predict_emotions_batch(texts, return_all_scores=True)
        
        # Update the feedback
        fb.emotion_suggested_changes = emotion_predictions[0]['emotion']
        fb.emotion_best_aspect = emotion_predictions[1]['emotion']
        fb.emotion_least_aspect = emotion_predictions[2]['emotion']
        fb.emotion_further_comments = emotion_predictions[3]['emotion']
        
        fb.emotion_confidence_scores = {
            'suggested_changes': {
                'emotion': emotion_predictions[0]['emotion'],
                'confidence': emotion_predictions[0]['confidence'],
                'all_scores': emotion_predictions[0].get('all_scores', {})
            },
            'best_aspect': {
                'emotion': emotion_predictions[1]['emotion'],
                'confidence': emotion_predictions[1]['confidence'],
                'all_scores': emotion_predictions[1].get('all_scores', {})
            },
            'least_aspect': {
                'emotion': emotion_predictions[2]['emotion'],
                'confidence': emotion_predictions[2]['confidence'],
                'all_scores': emotion_predictions[2].get('all_scores', {})
            },
            'further_comments': {
                'emotion': emotion_predictions[3]['emotion'],
                'confidence': emotion_predictions[3]['confidence'],
                'all_scores': emotion_predictions[3].get('all_scores', {})
            }
        }
        
        fb.save()
        updated_count += 1
        
        print(f"  ✓ Updated with emotions:")
        print(f"    - Suggested Changes: {emotion_predictions[0]['emotion']} ({emotion_predictions[0]['confidence']:.2f})")
        print(f"    - Best Aspect: {emotion_predictions[1]['emotion']} ({emotion_predictions[1]['confidence']:.2f})")
        print(f"    - Least Aspect: {emotion_predictions[2]['emotion']} ({emotion_predictions[2]['confidence']:.2f})")
        print(f"    - Further Comments: {emotion_predictions[3]['emotion']} ({emotion_predictions[3]['confidence']:.2f})")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")

print("\n" + "="*80)
print(f"Successfully updated {updated_count} / {feedbacks.count()} feedback entries")
print("="*80)
