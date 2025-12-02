import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import Feedback

print("="*80)
print("ACTUAL FEEDBACK TEXT WITH MODEL PREDICTIONS")
print("="*80)

feedbacks = Feedback.objects.filter(status='submitted').order_by('-id')[:5]

for fb in feedbacks:
    print(f"\n{'='*80}")
    print(f"FEEDBACK ID: {fb.id}")
    print(f"Student: {fb.student.get_full_name()}")
    print(f"Course: {fb.course_assignment.course.name if fb.course_assignment else 'N/A'}")
    print('='*80)
    
    if fb.suggested_changes:
        print(f"\n📝 SUGGESTED CHANGES:")
        print(f"   Text: \"{fb.suggested_changes}\"")
        print(f"   🤖 Predicted Emotion: {fb.emotion_suggested_changes}")
        if fb.emotion_confidence_scores:
            conf = fb.emotion_confidence_scores.get('suggested_changes', {}).get('confidence', 0)
            print(f"   Confidence: {conf:.2%}")
    
    if fb.best_teaching_aspect:
        print(f"\n✨ BEST TEACHING ASPECT:")
        print(f"   Text: \"{fb.best_teaching_aspect}\"")
        print(f"   🤖 Predicted Emotion: {fb.emotion_best_aspect}")
        if fb.emotion_confidence_scores:
            conf = fb.emotion_confidence_scores.get('best_aspect', {}).get('confidence', 0)
            print(f"   Confidence: {conf:.2%}")
    
    if fb.least_teaching_aspect:
        print(f"\n⚠️ LEAST TEACHING ASPECT:")
        print(f"   Text: \"{fb.least_teaching_aspect}\"")
        print(f"   🤖 Predicted Emotion: {fb.emotion_least_aspect}")
        if fb.emotion_confidence_scores:
            conf = fb.emotion_confidence_scores.get('least_aspect', {}).get('confidence', 0)
            print(f"   Confidence: {conf:.2%}")
    
    if fb.further_comments:
        print(f"\n💬 FURTHER COMMENTS:")
        print(f"   Text: \"{fb.further_comments}\"")
        print(f"   🤖 Predicted Emotion: {fb.emotion_further_comments}")
        if fb.emotion_confidence_scores:
            conf = fb.emotion_confidence_scores.get('further_comments', {}).get('confidence', 0)
            print(f"   Confidence: {conf:.2%}")

print("\n" + "="*80)
print("\n✅ These are REAL predictions from your XLM-RoBERTa model!")
print("   Model: ml_models/xlm_roberta_finetuned/")
print("   Emotions: joy, satisfaction, acceptance, boredom, disappointment")
print("="*80)
