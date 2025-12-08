"""
Run LDA Topic Modeling on Database Feedback with GPT-Neo Insights
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import Feedback
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
import json
warnings.filterwarnings('ignore')

print('='*100)
print('TOPIC MODELING - DATABASE FEEDBACK ANALYSIS')
print('='*100)

# Load feedback from database
print('\nLoading feedback from database...')
feedbacks = Feedback.objects.filter(status='submitted')

if feedbacks.count() < 10:  # Lowered threshold for testing
    print(f'\n❌ Need at least 10 feedbacks for topic modeling. Currently have {feedbacks.count()}.')
    sys.exit(1)

# Combine all text feedback fields
feedback_data = []
for fb in feedbacks:
    combined_text = ' '.join(filter(None, [
        fb.suggested_changes or '',
        fb.best_teaching_aspect or '',
        fb.least_teaching_aspect or '',
        fb.further_comments or ''
    ]))
    
    if combined_text.strip():
        # Get emotion from any field (use dominant emotion if available)
        emotions = []
        if fb.emotion_suggested_changes:
            emotions.append(fb.emotion_suggested_changes)
        if fb.emotion_best_aspect:
            emotions.append(fb.emotion_best_aspect)
        if fb.emotion_least_aspect:
            emotions.append(fb.emotion_least_aspect)
        if fb.emotion_further_comments:
            emotions.append(fb.emotion_further_comments)
        
        # Use most common emotion or default
        from collections import Counter
        emotion = Counter(emotions).most_common(1)[0][0] if emotions else 'acceptance'
        
        feedback_data.append({
            'feedback': combined_text,
            'label': emotion
        })

all_feedback = pd.DataFrame(feedback_data)
print(f'Total feedback entries: {len(all_feedback)}')

# Preprocess text for topic modeling
def preprocess_for_topics(text):
    """Clean text for topic modeling"""
    text = str(text).lower()
    words = [w for w in text.split() if len(w) > 3 and not w.isdigit()]
    return ' '.join(words)

all_feedback['cleaned_text'] = all_feedback['feedback'].apply(preprocess_for_topics)

# Create document-term matrix
print('\nCreating document-term matrix...')
vectorizer = CountVectorizer(
    max_features=1000,
    max_df=0.8,
    min_df=2,  # Lower threshold for smaller datasets
    stop_words='english'
)

doc_term_matrix = vectorizer.fit_transform(all_feedback['cleaned_text'])
feature_names = vectorizer.get_feature_names_out()

print(f'Vocabulary size: {len(feature_names)}')
print(f'Document-term matrix shape: {doc_term_matrix.shape}')

# Train LDA model
print('\nTraining LDA model...')
n_topics = min(5, len(all_feedback) // 2)  # Adjust topics based on data size

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

def generate_topic_name(keywords):
    """Generate a meaningful topic name based on keywords"""
    keyword_list = [k.lower() for k in keywords[:10]]
    
    # Define topic categories based on keyword patterns
    topic_patterns = {
        'Teaching Quality': ['teaching', 'instructor', 'professor', 'explain', 'explains', 'clear', 'understanding', 'lectures', 'lecture'],
        'Course Content': ['content', 'material', 'materials', 'topics', 'subject', 'curriculum', 'knowledge', 'learning'],
        'Assignments & Workload': ['assignments', 'homework', 'workload', 'tasks', 'work', 'projects', 'assignment', 'deadline'],
        'Class Engagement': ['class', 'interactive', 'activities', 'discussions', 'participate', 'engaging', 'interesting', 'attention'],
        'Assessment & Grading': ['exam', 'exams', 'test', 'tests', 'grade', 'grading', 'feedback', 'assessment', 'evaluation'],
        'Time Management': ['time', 'schedule', 'pace', 'pacing', 'deadlines', 'timing', 'duration', 'hours'],
        'Learning Support': ['help', 'support', 'guidance', 'office', 'hours', 'questions', 'clarification', 'assistance'],
        'Course Organization': ['organized', 'structure', 'organized', 'syllabus', 'schedule', 'plan', 'organization'],
        'Student Experience': ['experience', 'enjoy', 'enjoyed', 'appreciate', 'liked', 'love', 'positive', 'good'],
        'Communication': ['communication', 'responds', 'response', 'email', 'available', 'accessible', 'communicates']
    }
    
    # Score each category based on keyword matches
    category_scores = {}
    for category, patterns in topic_patterns.items():
        score = sum(1 for kw in keyword_list if any(pattern in kw for pattern in patterns))
        if score > 0:
            category_scores[category] = score
    
    # Return best matching category or generic name
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        return best_category
    
    # Fallback: use top 2 keywords
    return ' & '.join([k.title() for k in keywords[:2]])

def display_topics(model, feature_names, n_top_words=10):
    """Display top words for each topic with meaningful names"""
    topics = {}
    for topic_idx, topic in enumerate(model.components_):
        top_indices = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        
        # Generate meaningful topic name
        topic_name = generate_topic_name(top_words)
        topics[topic_name] = top_words
        
        print(f'\n{topic_name}:')
        print(', '.join(top_words))
    
    return topics

topics_dict = display_topics(lda_model, feature_names, n_top_words=15)

# Assign dominant topic to each feedback
all_feedback['dominant_topic'] = lda_output.argmax(axis=1)
all_feedback['topic_probability'] = lda_output.max(axis=1)

# Create mapping of topic index to topic name
topic_names_list = list(topics_dict.keys())
topic_index_to_name = {i: name for i, name in enumerate(topic_names_list)}

# Save results
output_dir = Path('results/topic_modeling')
output_dir.mkdir(parents=True, exist_ok=True)

# Save topic keywords with meaningful names
topics_df = pd.DataFrame([
    {'Topic': topic_name, 'Keywords': ', '.join(words)}
    for topic_name, words in topics_dict.items()
])
topics_df.to_csv(output_dir / 'topics_keywords.csv', index=False)
print(f'\n✅ Saved: topics_keywords.csv')

# Save feedback with topics using meaningful names
feedback_with_topics = all_feedback[['feedback', 'label', 'dominant_topic', 'topic_probability']].copy()
feedback_with_topics['topic_name'] = feedback_with_topics['dominant_topic'].map(topic_index_to_name)
feedback_with_topics.to_csv(output_dir / 'feedback_with_topics.csv', index=False)
print('✅ Saved: feedback_with_topics.csv')

# Generate Insights
print('='*100)
print('GENERATING INSIGHTS')
print('='*100)

# Prepare topic data
topics_data = []
for topic_idx in range(n_topics):
    topic_name = topic_index_to_name[topic_idx]
    keywords = topics_dict[topic_name]
    
    topic_data = all_feedback[all_feedback['dominant_topic'] == topic_idx]
    emotion_dist = topic_data['label'].value_counts().to_dict()
    
    topics_data.append({
        'topic': topic_name,
        'keywords': keywords[:10],
        'emotion_distribution': emotion_dist,
        'feedback_count': len(topic_data)
    })

# Try GPT-Neo
use_gpt_neo = False  # Disabled - use LDA-based insights for better quality

if use_gpt_neo:
    try:
        print('\nLoading GPT-Neo model...')
        sys.path.append('..')
        from api.ml_models.insight_generator import get_insight_generator
        
        generator = get_insight_generator()
        lda_insights = generator.generate_insights_batch(topics_for_gpt)
        
        print('✅ GPT-Neo insights generated!')
        
        # Print insights
        for topic_insight in lda_insights:
            print(f'\n{topic_insight["topic"]}:')
            for insight in topic_insight['insights']:
                print(f'  [{insight["priority"].upper()}] {insight["category"]}: {insight["suggestion"][:80]}...')
        
    except Exception as e:
        print(f'⚠️ GPT-Neo failed: {str(e)}')
        import traceback
        traceback.print_exc()
        use_gpt_neo = False

if not use_gpt_neo:
    print('\nGenerating LDA-based quality insights...')
    
    def generate_quality_insights(topic_idx, keywords, emotion_dist):
        """Generate comprehensive insights based on LDA topic and emotions"""
        insights = []
        total = sum(emotion_dist.values())
        if total == 0:
            return [{
                'category': 'General',
                'priority': 'medium',
                'suggestion': 'Continue monitoring student feedback for this topic area.',
                'icon': 'info',
                'method': 'lda-based'
            }]
        
        # Calculate emotion percentages and detailed breakdown
        emotions = {e: (c/total*100) for e, c in emotion_dist.items()}
        negative = emotions.get('boredom', 0) + emotions.get('disappointment', 0)
        positive = emotions.get('joy', 0) + emotions.get('satisfaction', 0)
        neutral = emotions.get('acceptance', 0)
        
        # Get top keywords for better context
        keyword_set = set([k.lower() for k in keywords[:15]])
        top_keywords = ', '.join(keywords[:5])
        
        # Sentiment summary for context
        sentiment_context = ""
        if negative > 50:
            sentiment_context = f"High concern detected ({negative:.0f}% negative sentiment)"
        elif negative > 30:
            sentiment_context = f"Moderate concerns identified ({negative:.0f}% negative sentiment)"
        elif positive > 60:
            sentiment_context = f"Strong positive feedback ({positive:.0f}% positive sentiment)"
        elif positive > 40:
            sentiment_context = f"Generally positive feedback ({positive:.0f}% positive sentiment)"
        else:
            sentiment_context = f"Mixed feedback ({neutral:.0f}% neutral, {positive:.0f}% positive, {negative:.0f}% negative)"
        
        # Teaching-related comprehensive analysis
        if any(w in keyword_set for w in ['teaching', 'instructor', 'explain', 'learning', 'understand', 'method']):
            if negative > 40:
                insights.append({
                    'category': 'Teaching Effectiveness',
                    'priority': 'high',
                    'suggestion': f'{sentiment_context}. Students highlight concerns about teaching methods related to: {top_keywords}. **Immediate Actions**: (1) Schedule one-on-one consultations with struggling students to understand specific challenges and learning barriers, (2) Record all lectures and make them available within 24 hours for review and self-paced learning, (3) Implement proven interactive teaching strategies: think-pair-share discussions (5-10 min per class), case study analysis in small groups, real-world problem-solving sessions, and peer teaching opportunities, (4) Provide multi-modal explanations using visual aids (diagrams, flowcharts, concept maps), video demonstrations, step-by-step written guides, and concrete examples before abstract concepts, (5) Create a continuous feedback loop through weekly check-ins, anonymous pulse surveys, and mid-semester formal evaluation to adjust teaching approaches in real-time, (6) Utilize backward design: start with learning outcomes and design assessments first, then align teaching methods to ensure constructive alignment, (7) Differentiate instruction by offering multiple pathways to master content (readings, videos, hands-on labs, group projects) to accommodate diverse learning styles and paces.',
                    'icon': 'presentation',
                    'method': 'lda-based'
                })
                # Add specific sub-recommendations
                if emotions.get('boredom', 0) > 25:
                    insights.append({
                        'category': 'Teaching Engagement',
                        'priority': 'high',
                        'suggestion': f'Significant boredom detected ({emotions.get("boredom", 0):.0f}%). **Comprehensive Engagement Strategies**: (1) Introduce gamification: point systems for participation, achievement badges for milestones, class leaderboards (individual or team-based), and challenge-based learning with rewards, (2) Use interactive technology: live polls and quizzes with Mentimeter/Kahoot every 15 minutes, collaborative virtual whiteboards (Miro, Jamboard), real-time Q&A platforms (Slido), and interactive simulations, (3) Implement active learning structures: think-pair-share (individual thinking → pair discussion → class sharing), jigsaw method (expert groups teaching each other), fishbowl discussions, and Socratic seminars, (4) Incorporate multimedia: relevant video clips (3-5 min), podcast segments, infographics, animations, and interactive demonstrations, (5) Connect to real-world: bring in industry guest speakers, analyze current news events, solve authentic problems from local businesses, virtual field trips, and student-led case presentations, (6) Vary instructional methods every 15-20 minutes following brain science: mini-lecture → active practice → discussion → reflection cycle, (7) Give students autonomy: choice in project topics, multiple assessment formats, self-paced modules, and opportunities to teach peers.',
                        'icon': 'zap',
                        'method': 'lda-based'
                    })
                if emotions.get('disappointment', 0) > 25:
                    insights.append({
                        'category': 'Teaching Quality',
                        'priority': 'high',
                        'suggestion': f'Student disappointment is evident ({emotions.get("disappointment", 0):.0f}%). **Comprehensive Quality Improvements**: (1) Conduct thorough content audit: review all materials for accuracy, currency, clarity, and alignment with current standards and industry practices, (2) Establish crystal-clear learning objectives: use measurable, action-oriented language (Bloom\'s taxonomy), share objectives at start of each class, and map how activities connect to objectives, (3) Provide scaffolded learning: start with foundational concepts, build complexity gradually, offer worked examples before independent practice, and use "I do, we do, you do" instructional model, (4) Increase practice opportunities: provide guided practice problems with immediate feedback, create low-stakes formative quizzes, offer practice exams, and establish study problem sets with detailed solutions, (5) Expand support infrastructure: double office hours, create supplemental instruction sessions with trained peer leaders, offer online help through discussion forums or chat hours, and provide one-on-one tutoring referrals, (6) Ensure constructive alignment: verify assessments directly test what you taught, use same terminology in tests as in lectures, provide practice questions similar to exam format, and eliminate "gotcha" questions that test trivia, (7) Demonstrate competence and preparation: arrive early to set up, have backup plans for technical issues, respond knowledgeably to questions, and show enthusiasm for the subject matter.',
                        'icon': 'alert-triangle',
                        'method': 'lda-based'
                    })
            elif positive > 50:
                insights.append({
                    'category': 'Teaching Effectiveness',
                    'priority': 'low',
                    'suggestion': f'{sentiment_context}. Students appreciate teaching methods related to: {top_keywords}. **Sustain and Scale Excellence**: (1) Document your success: create a detailed teaching portfolio with lesson plans, assessment examples, student feedback quotes, and reflection on what makes methods effective, (2) Share with colleagues: lead departmental teaching workshops, present at teaching and learning conferences, write articles for pedagogical journals (e.g., Journal of College Teaching & Learning), and create video demonstrations of your techniques, (3) Mentor others: formally mentor new faculty or graduate teaching assistants, conduct peer observations with feedback, and serve on teaching excellence committees, (4) Innovate strategically: maintain 80% of proven methods while experimenting with 20% new approaches, stay current with pedagogical research, attend teaching conferences, and pilot emerging technologies thoughtfully, (5) Seek external recognition: apply for teaching awards, request letters of support from students for promotion portfolios, and contribute to teaching excellence programs, (6) Create reusable resources: develop open educational resources (OER) that others can adapt, build a repository of successful activities and assignments, and share on platforms like MERLOT or OER Commons, (7) Research your practice: conduct scholarship of teaching and learning (SoTL) studies on what makes your methods effective, present findings at conferences, and publish to advance the field.',
                    'icon': 'presentation',
                    'method': 'lda-based'
                })
            else:
                insights.append({
                    'category': 'Teaching Effectiveness',
                    'priority': 'medium',
                    'suggestion': f'{sentiment_context} regarding teaching methods focused on: {top_keywords}. **Improvement Path**: Conduct a detailed mid-semester survey to identify specific areas for improvement, experiment with different pedagogical approaches (flipped classroom, peer instruction, active learning), seek peer observation and feedback from experienced colleagues, attend professional development workshops on innovative teaching methods, and implement formative assessments to gauge student understanding regularly.',
                    'icon': 'presentation',
                    'method': 'lda-based'
                })
        
        # Materials-related comprehensive analysis
        if any(w in keyword_set for w in ['materials', 'assignments', 'course', 'provide', 'resources', 'content']):
            if negative > 30:
                insights.append({
                    'category': 'Course Materials',
                    'priority': 'high',
                    'suggestion': f'Course materials need significant improvement - key areas: {top_keywords}. **Comprehensive Materials Overhaul**: (1) Conduct full content audit: evaluate all materials for accuracy, currency (published within 5 years), clarity (appropriate reading level), cultural relevance, and direct alignment with learning objectives, (2) Develop multi-modal content library: create 5-10 minute micro-lecture videos with closed captions, design visual infographics summarizing key concepts, develop interactive simulations or virtual labs, record podcast-style explanations for mobile learning, and provide traditional text readings with guided reading questions, (3) Ensure universal accessibility: use proper heading structure for screen readers, provide alt-text for all images, caption all videos (auto-generated plus manual review), use sufficient color contrast, offer materials in multiple formats (PDF, Word, HTML), and test with accessibility checkers (WAVE, aXe), (4) Create comprehensive support materials: write detailed study guides with key terms and concept maps, develop practice problem sets with step-by-step solutions, create FAQ documents addressing common misconceptions, design self-assessment quizzes with immediate feedback, and provide exam study resources (practice tests, concept reviews), (5) Organize systematically in LMS: use consistent module structure, create clear navigation with descriptive labels, sequence materials logically (pre-class → in-class → post-class), use folders and subfolders strategically, and provide a course roadmap showing how materials connect, (6) Gather and implement feedback: survey students on which materials are most/least helpful, track which resources students actually use (LMS analytics), conduct focus groups to understand material preferences, and iterate based on data, (7) Update continuously: review and refresh materials each semester, incorporate current events and recent research, replace outdated examples, and archive old versions.',
                    'icon': 'book',
                    'method': 'lda-based'
                })
                # Assignment-specific insights
                if 'assignments' in keyword_set or 'homework' in keyword_set:
                    insights.append({
                        'category': 'Assignment Design',
                        'priority': 'high',
                        'suggestion': f'Assignments require comprehensive redesign ({negative:.0f}% negative feedback). **Strategic Assignment Improvements**: (1) Develop transparent rubrics: create detailed scoring criteria for each assignment component (content, organization, analysis, mechanics), use 4-5 performance levels (exemplary, proficient, developing, beginning), include concrete descriptors for each level, share rubrics when assigning (not just when grading), and consider letting students help design rubrics to increase buy-in, (2) Provide exemplars and models: show 2-3 sample assignments from previous semesters (with permission) representing different quality levels, explain what makes each strong or weak using rubric language, create annotated examples highlighting key features, and offer templates or starter files for complex assignments, (3) Scaffold large projects: break major assignments into meaningful milestones (proposal → outline → draft → final), set interim deadlines with feedback opportunities, require progress check-ins (office hours or online submissions), and build skills progressively across assignments, (4) Write crystal-clear instructions: use numbered steps for multi-part assignments, define all technical terms, provide specific formatting requirements (citation style, length, file format), include FAQ sections addressing common questions, and offer checklists students can use before submitting, (5) Ensure constructive alignment: verify each assignment directly assesses stated learning objectives, use assignments to practice skills needed for exams, connect assignments to real-world applications in the field, and eliminate busywork that doesn\'t advance learning, (6) Offer strategic choice: provide 2-3 topic options for projects, allow selection of format (paper, presentation, video, portfolio), let students propose alternatives with approval, and differentiate complexity for challenge levels, (7) Design for authentic learning: base assignments on real-world problems or scenarios, invite students to address issues in their communities or interests, consider partnerships with local organizations, and create opportunities to share work publicly (class presentations, websites, community events).',
                        'icon': 'clipboard',
                        'method': 'lda-based'
                    })
            elif positive > 45:
                insights.append({
                    'category': 'Course Materials',
                    'priority': 'low',
                    'suggestion': f'Course materials are well-received ({positive:.0f}% positive sentiment) in areas like: {top_keywords}. **Maintain Quality**: Continue updating materials with current research and industry trends, gather feedback on specific resources to identify the most valuable ones, consider publishing or sharing your high-quality materials with the broader academic community, create a resource library that can be reused and refined for future course iterations.',
                    'icon': 'book',
                    'method': 'lda-based'
                })
            else:
                insights.append({
                    'category': 'Course Materials',
                    'priority': 'medium',
                    'suggestion': f'Course materials show room for enhancement in: {top_keywords}. **Strategic Updates**: Refresh materials regularly with current examples and case studies, add multimedia elements to increase engagement (videos, interactive diagrams), provide both digital and printable versions, include prerequisite review materials for students who need foundational support, curate external resources (articles, videos, websites) that complement core materials, and solicit student input on which resources are most helpful.',
                    'icon': 'book',
                    'method': 'lda-based'
                })
        
        # Time management and workload
        if any(w in keyword_set for w in ['time', 'deadlines', 'schedule', 'mindful', 'workload', 'pace']):
            priority = 'high' if negative > 35 else 'medium'
            insights.append({
                'category': 'Time Management & Workload',
                'priority': priority,
                'suggestion': f'Students express concerns about time and workload related to: {top_keywords}. **Comprehensive Workload Optimization**: (1) Create semester workload map: chart all assignments, exams, and major deliverables on a calendar, identify clustering periods (e.g., weeks with multiple deadlines), redistribute work to create breathing room, avoid scheduling major assessments during peak times (before holidays, exam weeks), and share workload calendar with students on day one so they can plan, (2) Provide detailed master schedule: create comprehensive course calendar with all class topics, reading assignments, due dates, exam dates, and no-class days, distribute in multiple formats (PDF, Google Calendar, LMS calendar), update and announce any changes prominently, and send weekly reminder emails of upcoming deadlines, (3) Implement milestone-based project structure: for projects spanning 4+ weeks, create 3-4 mandatory checkpoints (proposal, outline, draft, final), assign points to milestones to incentivize steady progress, provide substantive feedback at each stage, build in time for revision between stages, and penalize procrastination less while rewarding consistent effort, (4) Prioritize quality over quantity: audit current assignments and eliminate those that don\'t directly advance learning objectives, combine similar assignments into one deeper task, replace multiple small quizzes with fewer meaningful assessments, focus on assignments that develop critical skills rather than test recall, and aim for students to spend 2-3 hours outside class per credit hour, (5) Build in flexibility mechanisms: offer "grace day" policy (e.g., 3 penalty-free 24-hour extensions per semester, no questions asked), accept late work with clear policies (e.g., 10% reduction per day), allow revision opportunities on major assignments, and drop lowest quiz/homework grade, (6) Coordinate across courses: communicate with colleagues teaching in same program, consult department exam schedule before setting your dates, be aware of major events affecting students (conferences, practicum requirements), and participate in program-level workload discussions, (7) Assess and adjust workload: conduct mid-semester survey asking students about time spent per week, compare student-reported time to course credit expectations (3 hours per credit), identify specific bottlenecks or overwhelming assignments, make adjustments for future semesters, and share workload data transparently with students.',
                'icon': 'clock',
                'method': 'lda-based'
            })
            # Specific deadline concerns
            if 'deadlines' in keyword_set:
                insights.append({
                    'category': 'Deadline Management',
                    'priority': priority,
                    'suggestion': 'Deadline concerns identified. **Better Deadline Practices**: Announce all deadlines at least 2-3 weeks in advance, send reminder notifications 1 week and 1 day before due dates, allow students to submit draft work for early feedback, implement a "late day" policy where students have limited penalty-free extensions, coordinate with other instructors to avoid deadline conflicts, and be transparent about why certain deadlines exist to help students prioritize.',
                    'icon': 'calendar',
                    'method': 'lda-based'
                })
        
        # Engagement and interaction
        if any(w in keyword_set for w in ['interactive', 'activities', 'discussions', 'experience', 'participate', 'engage']):
            if emotions.get('boredom', 0) > 30:
                insights.append({
                    'category': 'Student Engagement',
                    'priority': 'high',
                    'suggestion': f'Low engagement detected ({emotions.get("boredom", 0):.0f}% boredom) in areas: {top_keywords}. **Engagement Transformation**: (1) Implement active learning: think-pair-share, jigsaw activities, peer teaching, problem-based learning, (2) Use technology: interactive polls (Mentimeter, Kahoot), collaborative tools (Padlet, Miro), discussion forums, (3) Incorporate real-world applications and current events to show relevance, (4) Design group projects that require meaningful collaboration and interdependence, (5) Invite guest speakers or organize field trips to connect theory with practice, (6) Create opportunities for student choice in topics, presentation formats, or project directions, (7) Gamify learning with points, badges, leaderboards for motivation.',
                    'icon': 'users',
                    'method': 'lda-based'
                })
            elif positive > 45:
                insights.append({
                    'category': 'Student Engagement',
                    'priority': 'low',
                    'suggestion': f'Strong engagement success ({positive:.0f}% positive sentiment) with: {top_keywords}. **Scale Your Success**: Document what makes your engagement strategies effective, create a best practices guide for your department, consider presenting your methods at teaching conferences, mentor colleagues who want to increase engagement, and continuously innovate by trying new engagement techniques while keeping proven methods.',
                    'icon': 'users',
                    'method': 'lda-based'
                })
            else:
                insights.append({
                    'category': 'Student Engagement',
                    'priority': 'medium',
                    'suggestion': f'Engagement shows mixed results in: {top_keywords}. **Boost Interaction**: Experiment with new interactive formats (debates, simulations, role-playing), ensure all students participate (not just vocal ones) through structured turn-taking or random selection, create safe spaces for questions and discussion without judgment, use small group work before large group discussions to build confidence, and regularly assess what engagement strategies resonate most with your students.',
                    'icon': 'users',
                    'method': 'lda-based'
                })
        
        # Assessment and evaluation
        if any(w in keyword_set for w in ['assessment', 'exam', 'test', 'grading', 'evaluation', 'feedback', 'grades']):
            if negative > 35:
                insights.append({
                    'category': 'Assessment & Evaluation',
                    'priority': 'high',
                    'suggestion': f'Assessment practices need review ({negative:.0f}% negative feedback) regarding: {top_keywords}. **Assessment Reform**: (1) Ensure assessments align with learning objectives and class content (constructive alignment), (2) Provide detailed rubrics before assignments so students know expectations, (3) Offer formative assessments (low-stakes quizzes, practice problems) before high-stakes exams, (4) Give timely, constructive feedback that helps students improve (within 1-2 weeks), (5) Consider alternative assessment formats beyond traditional exams (portfolios, presentations, projects), (6) Implement self and peer assessment to develop metacognitive skills, (7) Be transparent about grading criteria and address student concerns promptly.',
                    'icon': 'file-text',
                    'method': 'lda-based'
                })
            elif positive > 45:
                insights.append({
                    'category': 'Assessment & Evaluation',
                    'priority': 'low',
                    'suggestion': f'Assessment practices are well-regarded ({positive:.0f}% positive sentiment). **Maintain Standards**: Continue providing clear expectations and timely feedback, share your assessment strategies with colleagues, document your rubrics and grading practices for consistency, and explore new assessment methods that could further enhance student learning and demonstrate mastery.',
                    'icon': 'file-text',
                    'method': 'lda-based'
                })
        
        # Course structure and organization
        if any(w in keyword_set for w in ['course', 'subject', 'overall', 'better', 'need', 'structure', 'organized']):
            if negative > 35:
                insights.append({
                    'category': 'Course Structure',
                    'priority': 'high',
                    'suggestion': f'Course organization needs significant improvement in: {top_keywords}. **Structural Overhaul**: (1) Create a comprehensive, detailed syllabus with clear learning objectives, topics, schedule, policies, and contact information, (2) Organize course content into logical, coherent modules with clear progression, (3) Establish consistent patterns (e.g., lectures on Monday, labs on Wednesday) so students know what to expect, (4) Provide a visual course roadmap showing how topics connect and build on each other, (5) Communicate changes to the schedule promptly and clearly, (6) Hold a mid-semester feedback session to address organizational concerns, (7) Use a well-organized LMS with intuitive navigation and consistent structure across modules.',
                    'icon': 'folder',
                    'method': 'lda-based'
                })
            elif positive > 50:
                insights.append({
                    'category': 'Course Structure',
                    'priority': 'low',
                    'suggestion': f'Excellent course organization ({positive:.0f}% positive sentiment) in: {top_keywords}. **Best Practice Sharing**: Your organizational approach is working well. Document your course design process, share your syllabus and course structure as a model for others, contribute to curriculum development committees, and consider writing about your course design in teaching publications.',
                    'icon': 'folder',
                    'method': 'lda-based'
                })
            else:
                insights.append({
                    'category': 'Course Structure',
                    'priority': 'medium',
                    'suggestion': f'Course organization can be refined in areas like: {top_keywords}. **Incremental Improvements**: Review syllabus for clarity and completeness, ensure consistent structure across all modules, provide clear learning objectives for each class session, create transition statements that connect topics, maintain updated course materials and schedules, and gather student input on organizational aspects that could be clearer.',
                    'icon': 'folder',
                    'method': 'lda-based'
                })
        
        # Communication and support
        if any(w in keyword_set for w in ['communication', 'questions', 'help', 'support', 'available', 'office', 'hours']):
            if negative > 30:
                insights.append({
                    'category': 'Communication & Support',
                    'priority': 'high',
                    'suggestion': f'Students need better communication and support regarding: {top_keywords}. **Enhanced Support System**: (1) Increase office hours or offer virtual meeting options for accessibility, (2) Respond to emails within 24-48 hours and set clear communication expectations, (3) Create multiple channels for help (email, discussion forum, messaging app, office hours), (4) Establish peer tutoring or study groups for additional support, (5) Proactively reach out to struggling students early in the semester, (6) Provide clear, detailed responses to questions and follow up to ensure understanding, (7) Create an FAQ document addressing common questions and concerns.',
                    'icon': 'message-circle',
                    'method': 'lda-based'
                })
            else:
                insights.append({
                    'category': 'Communication & Support',
                    'priority': 'medium',
                    'suggestion': 'Maintain open, responsive communication channels. Continue being available and supportive to students, respond promptly to inquiries, and consider implementing additional support mechanisms like peer mentoring or supplementary instruction sessions for challenging topics.',
                    'icon': 'message-circle',
                    'method': 'lda-based'
                })
        
        # General overall feedback if no specific insights generated
        if not insights:
            if positive > 50:
                insights.append({
                    'category': 'Overall Performance',
                    'priority': 'low',
                    'suggestion': f'Course is performing excellently ({positive:.0f}% positive sentiment) in areas: {top_keywords}. **Continuous Excellence**: Continue current effective practices, document your successful strategies, share your approach with colleagues, stay current with pedagogical innovations, regularly seek student feedback to maintain high quality, and consider taking on leadership roles in teaching and learning initiatives in your department or institution.',
                    'icon': 'award',
                    'method': 'lda-based'
                })
            elif negative > 45:
                insights.append({
                    'category': 'Overall Performance',
                    'priority': 'high',
                    'suggestion': f'Significant improvement needed ({negative:.0f}% negative sentiment) regarding: {top_keywords}. **Comprehensive Action Plan**: (1) Conduct student focus groups to identify root causes of dissatisfaction, (2) Prioritize top 3-5 issues based on student feedback frequency and severity, (3) Create a concrete action plan with timeline and measurable goals, (4) Seek mentorship from excellent teachers in your department, (5) Attend teaching workshops and professional development programs, (6) Implement changes incrementally and gather ongoing feedback, (7) Consider course redesign consultation with your institution\'s teaching and learning center, (8) Communicate changes to students transparently to show you value their input.',
                    'icon': 'alert-circle',
                    'method': 'lda-based'
                })
            else:
                insights.append({
                    'category': 'Overall Performance',
                    'priority': 'medium',
                    'suggestion': f'Course shows moderate performance with mixed feedback on: {top_keywords}. **Strategic Improvement**: Focus on identified areas from student feedback, implement targeted improvements systematically, measure impact of changes through ongoing feedback collection, celebrate and sustain what is working well, address problem areas with evidence-based teaching practices, and maintain open dialogue with students about course evolution.',
                    'icon': 'bar-chart',
                    'method': 'lda-based'
                })
        
        # Post-process: create concise one-line summary and keep full details
        processed_insights = []
        for ins in insights:
            full = ins.get('suggestion', '')
            # Build a short summary: first sentence or truncated text
            summary = ''
            if full:
                # Use first sentence if it's short enough
                if '.' in full:
                    first = full.split('.')[:1][0].strip()
                    if len(first) > 140:
                        summary = first[:137].rsplit(' ', 1)[0] + '...'
                    else:
                        summary = first
                else:
                    summary = full if len(full) <= 140 else full[:137].rsplit(' ', 1)[0] + '...'
            else:
                summary = ''

            ins_short = ins.copy()
            ins_short['summary'] = summary
            ins_short['details'] = full
            # Replace suggestion with concise summary for display
            ins_short['suggestion'] = summary if summary else full
            processed_insights.append(ins_short)

        return processed_insights
    
    # Generate insights for each topic
    lda_insights = []
    for topic_info in topics_data:
        insights = generate_quality_insights(
            int(topic_info['topic'].split()[1]) - 1,
            topic_info['keywords'],
            topic_info['emotion_distribution']
        )
        lda_insights.append({
            'topic': topic_info['topic'],
            'keywords': topic_info['keywords'],
            'emotion_distribution': topic_info['emotion_distribution'],
            'insights': insights,
            'feedback_count': topic_info['feedback_count']
        })
        
        # Print
        print(f'\n{topic_info["topic"]}:')
        for insight in insights:
            print(f'  [{insight["priority"].upper()}] {insight["category"]}: {insight["suggestion"][:80]}...')

# Save insights
insights_output = {
    'topics': lda_insights,
    'total_topics': n_topics,
    'total_feedback': len(all_feedback),
    'generation_method': 'rule-based'
}

with open(output_dir / 'lda_insights.json', 'w') as f:
    json.dump(insights_output, f, indent=2)

print(f'\n✅ Saved: lda_insights.json')
print('\n' + '='*100)
print('TOPIC MODELING COMPLETE WITH RULE-BASED INSIGHTS')
print('='*100)
