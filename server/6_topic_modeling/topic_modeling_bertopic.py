"""
Advanced Topic Modeling using BERTopic
Uses transformer embeddings for better topic discovery
Installation required: pip install bertopic
"""

import pandas as pd
import numpy as np
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print('='*100)
print('ADVANCED TOPIC MODELING WITH BERTopic')
print('='*100)

# Load data
print('\nLoading feedback data...')
train_df = pd.read_csv('data/annotations/train_data.csv')
test_df = pd.read_csv('data/annotations/test_data.csv')
all_feedback = pd.concat([train_df, test_df], ignore_index=True)

feedback_texts = all_feedback['feedback'].tolist()
print(f'Total feedback: {len(feedback_texts)}')

# Configure BERTopic
print('\nInitializing BERTopic model...')
vectorizer_model = CountVectorizer(stop_words='english', min_df=5)

topic_model = BERTopic(
    language='english',
    calculate_probabilities=True,
    vectorizer_model=vectorizer_model,
    nr_topics=8,  # Number of topics
    verbose=True
)

# Fit model
print('\nTraining BERTopic model (this may take a few minutes)...')
topics, probs = topic_model.fit_transform(feedback_texts)

print(f'✅ Model trained! Discovered {len(set(topics))} topics')

# Get topic information
topic_info = topic_model.get_topic_info()
print('\nTopic Information:')
print(topic_info)

# Add topics to dataframe
all_feedback['topic'] = topics
all_feedback['topic_probability'] = probs.max(axis=1) if len(probs.shape) > 1 else probs

# Create output directory
output_dir = Path('results/topic_modeling_bertopic')
output_dir.mkdir(parents=True, exist_ok=True)

# Visualization 1: Topic word scores
print('\nGenerating visualizations...')
fig = topic_model.visualize_barchart(top_n_topics=8, n_words=10, height=400)
fig.write_html(str(output_dir / '1_topic_words.html'))
print('✅ Saved: 1_topic_words.html')

# Visualization 2: Topic similarity
fig = topic_model.visualize_heatmap()
fig.write_html(str(output_dir / '2_topic_similarity.html'))
print('✅ Saved: 2_topic_similarity.html')

# Visualization 3: Intertopic distance map
fig = topic_model.visualize_topics()
fig.write_html(str(output_dir / '3_intertopic_distance.html'))
print('✅ Saved: 3_intertopic_distance.html')

# Analyze topics by emotion
print('\nAnalyzing topic-emotion relationships...')
emotion_topic_dist = pd.crosstab(
    all_feedback['label'],
    all_feedback['topic'],
    normalize='index'
) * 100

# Create static heatmap
fig, ax = plt.subplots(figsize=(14, 8))
sns.heatmap(emotion_topic_dist, annot=True, fmt='.1f', cmap='YlGnBu',
           cbar_kws={'label': 'Percentage (%)'}, ax=ax)
ax.set_xlabel('Topic', fontsize=12, fontweight='bold')
ax.set_ylabel('Emotion', fontsize=12, fontweight='bold')
ax.set_title('Topic Distribution Across Emotions (BERTopic)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(output_dir / '4_topic_emotion_heatmap.png', dpi=300, bbox_inches='tight')
print('✅ Saved: 4_topic_emotion_heatmap.png')
plt.close()

# Save results
all_feedback.to_csv(output_dir / 'feedback_with_bertopics.csv', index=False)
topic_info.to_csv(output_dir / 'topic_info.csv', index=False)

print('\n' + '='*100)
print('SAMPLE FEEDBACK PER TOPIC')
print('='*100)

for topic_id in sorted(set(topics)):
    if topic_id == -1:  # Skip outlier topic
        continue
    
    topic_samples = all_feedback[all_feedback['topic'] == topic_id].head(3)
    topic_words = topic_model.get_topic(topic_id)
    
    print(f'\nTopic {topic_id}: {", ".join([word for word, _ in topic_words[:5]])}')
    print('-' * 100)
    
    for _, row in topic_samples.iterrows():
        print(f'  [{row["label"]}] {row["feedback"][:100]}...')

print('\n' + '='*100)
print(f'All results saved to: {output_dir}')
print('='*100)
