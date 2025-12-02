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
