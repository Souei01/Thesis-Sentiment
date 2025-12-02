"""
Topic Modeling using LDA (Latent Dirichlet Allocation)
Discovers hidden topics in student feedback
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print('='*100)
print('TOPIC MODELING - STUDENT FEEDBACK ANALYSIS')
print('='*100)

# Load data
print('\nLoading feedback data...')
train_df = pd.read_csv('data/annotations/train_data.csv')
test_df = pd.read_csv('data/annotations/test_data.csv')
all_feedback = pd.concat([train_df, test_df], ignore_index=True)

print(f'Total feedback entries: {len(all_feedback)}')

# Preprocess text for topic modeling
def preprocess_for_topics(text):
    """Clean text for topic modeling"""
    text = str(text).lower()
    # Remove very short words and numbers
    words = [w for w in text.split() if len(w) > 3 and not w.isdigit()]
    return ' '.join(words)

all_feedback['cleaned_text'] = all_feedback['feedback'].apply(preprocess_for_topics)

# Create document-term matrix
print('\nCreating document-term matrix...')
vectorizer = CountVectorizer(
    max_features=1000,  # Top 1000 words
    max_df=0.8,         # Ignore words in >80% of documents
    min_df=5,           # Ignore words in <5 documents
    stop_words='english'
)

doc_term_matrix = vectorizer.fit_transform(all_feedback['cleaned_text'])
feature_names = vectorizer.get_feature_names_out()

print(f'Vocabulary size: {len(feature_names)}')
print(f'Document-term matrix shape: {doc_term_matrix.shape}')

# Train LDA model
print('\nTraining LDA model...')
n_topics = 8  # Number of topics to discover

lda_model = LatentDirichletAllocation(
    n_components=n_topics,
    max_iter=50,
    learning_method='online',
    random_state=42,
    n_jobs=-1
)

lda_output = lda_model.fit_transform(doc_term_matrix)

print(f'✅ LDA model trained with {n_topics} topics')

# Display top words for each topic
print('\n' + '='*100)
print('DISCOVERED TOPICS')
print('='*100)

def display_topics(model, feature_names, n_top_words=10):
    """Display top words for each topic"""
    topics = {}
    for topic_idx, topic in enumerate(model.components_):
        top_indices = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        topics[f'Topic {topic_idx + 1}'] = top_words
        
        print(f'\nTopic {topic_idx + 1}:')
        print(', '.join(top_words))
    
    return topics

topics_dict = display_topics(lda_model, feature_names, n_top_words=15)

# Assign dominant topic to each feedback
all_feedback['dominant_topic'] = lda_output.argmax(axis=1)
all_feedback['topic_probability'] = lda_output.max(axis=1)

# Analyze topics by emotion
print('\n' + '='*100)
print('TOPIC DISTRIBUTION BY EMOTION')
print('='*100)

emotion_topic_dist = pd.crosstab(
    all_feedback['label'], 
    all_feedback['dominant_topic'],
    normalize='index'
) * 100

print('\nPercentage of each topic per emotion:')
print(emotion_topic_dist.round(2))

# Create visualizations
output_dir = Path('results/topic_modeling')
output_dir.mkdir(parents=True, exist_ok=True)

# Visualization 1: Topic-Emotion Heatmap
print('\n1. Creating topic-emotion heatmap...')
fig, ax = plt.subplots(figsize=(12, 8))

sns.heatmap(emotion_topic_dist.T, annot=True, fmt='.1f', cmap='YlOrRd', 
           cbar_kws={'label': 'Percentage (%)'}, ax=ax)

ax.set_xlabel('Emotion', fontsize=12, fontweight='bold')
ax.set_ylabel('Topic', fontsize=12, fontweight='bold')
ax.set_title('Topic Distribution Across Emotions', fontsize=14, fontweight='bold')
ax.set_yticklabels([f'Topic {i+1}' for i in range(n_topics)], rotation=0)

plt.tight_layout()
plt.savefig(output_dir / '1_topic_emotion_heatmap.png', dpi=300, bbox_inches='tight')
print('✅ Saved: 1_topic_emotion_heatmap.png')
plt.close()

# Visualization 2: Topic Distribution Bar Chart
print('2. Creating topic distribution chart...')
topic_counts = all_feedback['dominant_topic'].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(range(n_topics), topic_counts.values, color='steelblue', alpha=0.8, edgecolor='black')

for bar, count in zip(bars, topic_counts.values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{int(count)}\n({count/len(all_feedback)*100:.1f}%)',
           ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xlabel('Topic', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Feedback Entries', fontsize=12, fontweight='bold')
ax.set_title('Distribution of Topics in Student Feedback', fontsize=14, fontweight='bold')
ax.set_xticks(range(n_topics))
ax.set_xticklabels([f'Topic {i+1}' for i in range(n_topics)])
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / '2_topic_distribution.png', dpi=300, bbox_inches='tight')
print('✅ Saved: 2_topic_distribution.png')
plt.close()

# Visualization 3: Word Cloud for Each Topic (showing top words)
print('3. Creating topic word importance chart...')

fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for topic_idx in range(n_topics):
    ax = axes[topic_idx]
    
    # Get top 10 words for this topic
    topic = lda_model.components_[topic_idx]
    top_indices = topic.argsort()[-10:][::-1]
    top_words = [feature_names[i] for i in top_indices]
    top_weights = topic[top_indices]
    
    # Normalize weights
    top_weights = top_weights / top_weights.sum() * 100
    
    # Create horizontal bar chart
    y_pos = np.arange(len(top_words))
    ax.barh(y_pos, top_weights, color='teal', alpha=0.7, edgecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_words, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Importance (%)', fontsize=9)
    ax.set_title(f'Topic {topic_idx + 1}', fontsize=11, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / '3_topic_word_importance.png', dpi=300, bbox_inches='tight')
print('✅ Saved: 3_topic_word_importance.png')
plt.close()

# Save results to CSV
print('\n4. Saving detailed results...')

# Topic keywords
topics_df = pd.DataFrame([
    {'Topic': f'Topic {i+1}', 'Keywords': ', '.join(words)}
    for i, words in enumerate(topics_dict.values())
])
topics_df.to_csv(output_dir / 'topics_keywords.csv', index=False)

# Feedback with topics
feedback_with_topics = all_feedback[['feedback', 'label', 'dominant_topic', 'topic_probability']].copy()
feedback_with_topics['topic_name'] = feedback_with_topics['dominant_topic'].apply(lambda x: f'Topic {x+1}')
feedback_with_topics.to_csv(output_dir / 'feedback_with_topics.csv', index=False)

print('✅ Saved: topics_keywords.csv')
print('✅ Saved: feedback_with_topics.csv')

# Sample feedback per topic
print('\n' + '='*100)
print('SAMPLE FEEDBACK PER TOPIC')
print('='*100)

for topic_idx in range(n_topics):
    print(f'\nTopic {topic_idx + 1} - Top Keywords: {", ".join(topics_dict[f"Topic {topic_idx + 1}"][:5])}')
    print('-' * 100)
    
    topic_samples = all_feedback[all_feedback['dominant_topic'] == topic_idx].nlargest(3, 'topic_probability')
    
    for idx, row in topic_samples.iterrows():
        print(f'  [{row["label"]}] {row["feedback"][:100]}...')

print('\n' + '='*100)
print(f'All results saved to: {output_dir}')
print('='*100)

# Generate LDA-based insights
print('\n' + '='*100)
print('GENERATING LDA-BASED INSIGHTS')
print('='*100)

def generate_lda_insights(topic_idx, keywords, emotion_dist, topic_feedback_samples):
    """Generate insights based on LDA topic analysis and emotion distribution"""
    insights = []
    
    # Analyze emotion distribution for this topic
    total_emotions = sum(emotion_dist.values())
    if total_emotions == 0:
        return insights
    
    emotion_percentages = {emotion: (count / total_emotions * 100) for emotion, count in emotion_dist.items()}
    
    # Dominant emotion
    dominant_emotion = max(emotion_percentages.items(), key=lambda x: x[1])
    
    # Analyze keywords using LDA topic coherence
    keyword_set = set([k.lower() for k in keywords[:10]])
    
    # Priority determination based on LDA topic-emotion distribution
    negative_emotions = emotion_percentages.get('boredom', 0) + emotion_percentages.get('disappointment', 0)
    positive_emotions = emotion_percentages.get('joy', 0) + emotion_percentages.get('satisfaction', 0)
    
    if negative_emotions > 50:
        base_priority = 'high'
    elif negative_emotions > 25:
        base_priority = 'medium'
    else:
        base_priority = 'low'
    
    # Teaching quality insights (based on LDA topic keywords)
    if any(word in keyword_set for word in ['teaching', 'teach', 'instructor', 'professor', 'explain', 'instruction', 'lecture']):
        if negative_emotions > positive_emotions:
            insights.append({
                'category': 'Teaching Methods',
                'priority': 'high',
                'suggestion': f'Teaching methods need improvement. {dominant_emotion[0].capitalize()} is the dominant emotion ({dominant_emotion[1]:.1f}%). Consider: more interactive sessions, clearer explanations, and varied teaching approaches.',
                'icon': 'presentation',
                'confidence': min(dominant_emotion[1] / 100, 0.95)
            })
        elif positive_emotions > 50:
            insights.append({
                'category': 'Teaching Methods',
                'priority': 'low',
                'suggestion': f'Teaching approach is effective! Students express {dominant_emotion[0]} ({dominant_emotion[1]:.1f}%). Continue current methods and share best practices.',
                'icon': 'presentation',
                'confidence': min(dominant_emotion[1] / 100, 0.95)
            })
    
    # Course content and materials
    if any(word in keyword_set for word in ['material', 'content', 'book', 'slide', 'resource', 'handout', 'note', 'reading']):
        if emotion_percentages.get('boredom', 0) > 30:
            insights.append({
                'category': 'Learning Materials',
                'priority': 'high',
                'suggestion': f'Course materials may be causing disengagement (boredom: {emotion_percentages.get("boredom", 0):.1f}%). Update content with multimedia, real-world examples, and interactive resources.',
                'icon': 'book',
                'confidence': min(emotion_percentages.get('boredom', 0) / 100, 0.9)
            })
        else:
            insights.append({
                'category': 'Learning Materials',
                'priority': base_priority,
                'suggestion': 'Review and refresh course materials regularly. Consider adding diverse learning resources to support different learning styles.',
                'icon': 'book',
                'confidence': 0.7
            })
    
    # Assessment and grading
    if any(word in keyword_set for word in ['exam', 'test', 'grade', 'grading', 'assessment', 'quiz', 'assignment', 'homework']):
        if emotion_percentages.get('disappointment', 0) > 20:
            insights.append({
                'category': 'Assessment',
                'priority': 'high',
                'suggestion': f'Assessments causing frustration (disappointment: {emotion_percentages.get("disappointment", 0):.1f}%). Review grading criteria, provide clearer rubrics, practice problems, and more timely feedback.',
                'icon': 'clipboard',
                'confidence': min(emotion_percentages.get('disappointment', 0) / 100, 0.9)
            })
        elif emotion_percentages.get('acceptance', 0) > 40:
            insights.append({
                'category': 'Assessment',
                'priority': 'medium',
                'suggestion': f'Assessment practices are acceptable ({emotion_percentages.get("acceptance", 0):.1f}% acceptance). Consider enhancements: provide sample exams, more practice opportunities, and detailed feedback.',
                'icon': 'clipboard',
                'confidence': 0.75
            })
    
    # Time management and pacing
    if any(word in keyword_set for word in ['time', 'deadline', 'schedule', 'pace', 'pacing', 'rushed', 'fast', 'slow']):
        if negative_emotions > 40:
            insights.append({
                'category': 'Time Management',
                'priority': 'high',
                'suggestion': f'Course pacing is problematic (negative emotions: {negative_emotions:.1f}%). Adjust deadlines, break large projects into milestones, and allow flexible scheduling.',
                'icon': 'clock',
                'confidence': min(negative_emotions / 100, 0.95)
            })
        else:
            insights.append({
                'category': 'Time Management',
                'priority': 'medium',
                'suggestion': 'Monitor course pacing. Ensure adequate time for complex topics and provide extension options when needed.',
                'icon': 'clock',
                'confidence': 0.7
            })
    
    # Student engagement
    if any(word in keyword_set for word in ['engaging', 'engage', 'interesting', 'interest', 'boring', 'bore', 'motivate', 'attention']):
        if emotion_percentages.get('boredom', 0) > 35:
            insights.append({
                'category': 'Student Engagement',
                'priority': 'high',
                'suggestion': f'Low student engagement detected (boredom: {emotion_percentages.get("boredom", 0):.1f}%). Implement: group discussions, hands-on activities, real-world case studies, and gamification.',
                'icon': 'users',
                'confidence': min(emotion_percentages.get('boredom', 0) / 100, 0.95)
            })
        elif emotion_percentages.get('joy', 0) > 40:
            insights.append({
                'category': 'Student Engagement',
                'priority': 'low',
                'suggestion': f'Excellent student engagement (joy: {emotion_percentages.get("joy", 0):.1f}%)! Maintain current strategies and document successful techniques for other courses.',
                'icon': 'users',
                'confidence': min(emotion_percentages.get('joy', 0) / 100, 0.95)
            })
    
    # Communication and feedback
    if any(word in keyword_set for word in ['feedback', 'communicate', 'communication', 'response', 'respond', 'question', 'help', 'support']):
        if negative_emotions > 30:
            insights.append({
                'category': 'Communication',
                'priority': 'high',
                'suggestion': f'Communication gaps identified (negative emotions: {negative_emotions:.1f}%). Improve: response time, office hour availability, clear email communication, and feedback quality.',
                'icon': 'message',
                'confidence': min(negative_emotions / 100, 0.9)
            })
        else:
            insights.append({
                'category': 'Communication',
                'priority': 'medium',
                'suggestion': 'Maintain open communication channels. Provide timely feedback and be accessible during designated office hours.',
                'icon': 'message',
                'confidence': 0.75
            })
    
    # Course organization and structure
    if any(word in keyword_set for word in ['organize', 'organization', 'structure', 'structured', 'plan', 'planning', 'syllabus', 'clear', 'clarity']):
        if emotion_percentages.get('acceptance', 0) < 30 and negative_emotions > 25:
            insights.append({
                'category': 'Course Organization',
                'priority': 'high',
                'suggestion': f'Course structure needs improvement (negative emotions: {negative_emotions:.1f}%). Provide: detailed syllabus, clear learning objectives, organized content modules, and consistent schedule.',
                'icon': 'folder',
                'confidence': min(negative_emotions / 100, 0.9)
            })
        else:
            insights.append({
                'category': 'Course Organization',
                'priority': 'medium',
                'suggestion': 'Review course organization. Ensure syllabus is comprehensive, objectives are clear, and content flow is logical.',
                'icon': 'folder',
                'confidence': 0.7
            })
    
    # General insight based on overall emotion distribution
    if not insights:
        if positive_emotions > 60:
            insights.append({
                'category': 'Overall Course Quality',
                'priority': 'low',
                'suggestion': f'Course is performing well with {positive_emotions:.1f}% positive emotions. Continue monitoring feedback and maintain current standards.',
                'icon': 'info',
                'confidence': min(positive_emotions / 100, 0.9)
            })
        elif negative_emotions > 50:
            insights.append({
                'category': 'Overall Course Quality',
                'priority': 'high',
                'suggestion': f'Course needs significant improvement ({negative_emotions:.1f}% negative emotions). Conduct student surveys, review all aspects, and implement changes systematically.',
                'icon': 'info',
                'confidence': min(negative_emotions / 100, 0.95)
            })
        else:
            insights.append({
                'category': 'Overall Course Quality',
                'priority': 'medium',
                'suggestion': 'Course performance is moderate. Focus on areas mentioned in student feedback and implement incremental improvements.',
                'icon': 'info',
                'confidence': 0.75
            })
    
    return insights

# Generate insights for each topic using GPT-Neo
print('\n' + '='*100)
print('GENERATING GPT-NEO BASED INSIGHTS')
print('='*100)

# Prepare data for GPT-Neo
topics_for_gpt = []
for topic_idx in range(n_topics):
    topic_name = f'Topic {topic_idx + 1}'
    keywords = topics_dict[topic_name]
    
    # Get emotion distribution for this topic
    topic_data = all_feedback[all_feedback['dominant_topic'] == topic_idx]
    emotion_dist = topic_data['label'].value_counts().to_dict()
    
    topics_for_gpt.append({
        'topic': topic_name,
        'keywords': keywords[:10],
        'emotion_distribution': emotion_dist,
        'feedback_count': len(topic_data)
    })

# Option 1: Use GPT-Neo (requires model loading)
use_gpt_neo = True  # Set to False to use LDA-based insights

if use_gpt_neo:
    try:
        print('\nLoading GPT-Neo model for insight generation...')
        import sys
        sys.path.append('..')
        from api.ml_models.insight_generator import get_insight_generator
        
        generator = get_insight_generator()
        lda_insights = generator.generate_insights_batch(topics_for_gpt)
        
        print('✅ GPT-Neo insights generated successfully!')
        
        # Print insights
        for topic_insight in lda_insights:
            topic_name = topic_insight['topic']
            idx = int(topic_name.split()[1]) - 1
            keywords = topics_dict[topic_name]
            topic_data = all_feedback[all_feedback['dominant_topic'] == idx]
            emotion_dist = topic_data['label'].value_counts().to_dict()
            
            print(f'\n{topic_name}: {", ".join(keywords[:5])}')
            print(f'Feedback count: {len(topic_data)}')
            print(f'Emotions: {emotion_dist}')
            print('GPT-Neo Generated Insights:')
            for insight in topic_insight['insights']:
                print(f'  [{insight["priority"].upper()}] {insight["category"]}: {insight["suggestion"][:100]}...')
        
    except Exception as e:
        print(f'⚠️ GPT-Neo generation failed: {str(e)}')
        print('Falling back to LDA-based insights...')
        use_gpt_neo = False

# Option 2: Fallback to LDA-based insights
if not use_gpt_neo:
    lda_insights = []
    
    for topic_idx in range(n_topics):
        topic_name = f'Topic {topic_idx + 1}'
        keywords = topics_dict[topic_name]
        
        # Get emotion distribution for this topic
        topic_data = all_feedback[all_feedback['dominant_topic'] == topic_idx]
        emotion_dist = topic_data['label'].value_counts().to_dict()
        
        # Get sample feedback
        topic_samples = topic_data.nlargest(3, 'topic_probability')
        
        # Generate insights
        insights = generate_lda_insights(topic_idx, keywords, emotion_dist, topic_samples)
        
        lda_insights.append({
            'topic': topic_name,
            'keywords': keywords[:10],
            'emotion_distribution': emotion_dist,
            'insights': insights,
            'feedback_count': len(topic_data)
        })
        
        # Print insights
        print(f'\n{topic_name}: {", ".join(keywords[:5])}')
        print(f'Feedback count: {len(topic_data)}')
        print(f'Emotions: {emotion_dist}')
        print('LDA-Based Insights:')
        for insight in insights:
            print(f'  [{insight["priority"].upper()}] {insight["category"]}: {insight["suggestion"][:80]}... (confidence: {insight["confidence"]:.2f})')

# Save insights to JSON
import json

insights_output = {
    'topics': lda_insights,
    'total_topics': n_topics,
    'total_feedback': len(all_feedback),
    'generation_method': 'GPT-Neo' if use_gpt_neo else 'LDA-based topic-emotion analysis'
}

with open(output_dir / 'lda_insights.json', 'w') as f:
    json.dump(insights_output, f, indent=2)

print('\n✅ Saved: lda_insights.json')
print('\n' + '='*100)
print(f'LDA ANALYSIS COMPLETE WITH {"GPT-NEO" if use_gpt_neo else "LDA-BASED"} INSIGHTS')
print('='*100)
