"""
Generate Comprehensive Insights for All Courses
Creates a detailed report with insights, recommendations, and statistics for every course
"""

import pandas as pd
from pathlib import Path

print('='*100)
print('GENERATING COMPREHENSIVE COURSE INSIGHTS')
print('='*100)

# Load the detailed sentiment data
detailed_df = pd.read_csv('results/course_analysis/course_sentiment_detailed.csv')
scores_df = pd.read_csv('results/course_analysis/course_sentiment_scores.csv')

print(f'\nTotal courses analyzed: {len(scores_df)}')

# Create results directory
output_dir = Path('results/course_analysis')
output_dir.mkdir(parents=True, exist_ok=True)

# Generate comprehensive insights report
report_path = output_dir / 'all_courses_insights_report.txt'

with open(report_path, 'w', encoding='utf-8') as f:
    f.write('='*100 + '\n')
    f.write('COMPREHENSIVE COURSE INSIGHTS REPORT\n')
    f.write('Sentiment Analysis for All Courses\n')
    f.write('='*100 + '\n\n')
    
    f.write('EXECUTIVE SUMMARY\n')
    f.write('-'*100 + '\n')
    f.write(f'Total Courses Analyzed: {len(scores_df)}\n')
    f.write(f'Total Feedback Entries: {scores_df["Feedback_Count"].sum()}\n')
    
    # Calculate overall statistics
    positive_courses = len(scores_df[scores_df['Average_Sentiment_Score'] > 0])
    negative_courses = len(scores_df[scores_df['Average_Sentiment_Score'] < 0])
    neutral_courses = len(scores_df[scores_df['Average_Sentiment_Score'] == 0])
    
    f.write(f'Courses with Positive Sentiment: {positive_courses} ({positive_courses/len(scores_df)*100:.1f}%)\n')
    f.write(f'Courses with Negative Sentiment: {negative_courses} ({negative_courses/len(scores_df)*100:.1f}%)\n')
    f.write(f'Courses with Neutral Sentiment: {neutral_courses} ({neutral_courses/len(scores_df)*100:.1f}%)\n\n')
    
    avg_score = scores_df['Average_Sentiment_Score'].mean()
    f.write(f'Overall Average Sentiment Score: {avg_score:.3f}\n')
    f.write('(Scale: -2.0 = Very Negative, 0 = Neutral, +2.0 = Very Positive)\n\n')
    
    f.write('='*100 + '\n\n')
    
    # Individual course insights
    f.write('DETAILED COURSE-BY-COURSE INSIGHTS\n')
    f.write('='*100 + '\n\n')
    
    # Sort by sentiment score (best to worst)
    sorted_courses = scores_df.sort_values('Average_Sentiment_Score', ascending=False)
    
    for idx, row in sorted_courses.iterrows():
        course_code = row['Course_code']
        subject = row['Subject_Description']
        score = row['Average_Sentiment_Score']
        count = int(row['Feedback_Count'])
        
        f.write(f'{course_code} - {subject}\n')
        f.write('-'*100 + '\n')
        
        # Get emotion breakdown
        course_emotions = detailed_df[
            (detailed_df['Course_code'] == course_code) & 
            (detailed_df['Subject_Description'] == subject)
        ]
        
        f.write(f'Sentiment Score: {score:.3f}\n')
        f.write(f'Total Feedback: {count}\n\n')
        
        # Emotion distribution
        f.write('Emotion Breakdown:\n')
        for _, emotion_row in course_emotions.iterrows():
            emotion = emotion_row['Label']
            emotion_count = int(emotion_row['Count'])
            percentage = emotion_row['Percentage']
            f.write(f'  {emotion:<18} {emotion_count:>3} ({percentage:>5.1f}%)\n')
        
        # Generate insights and recommendations
        f.write('\nInsights:\n')
        
        # Determine overall sentiment category
        if score >= 1.5:
            sentiment_category = 'Excellent'
            f.write(f'  ✅ EXCELLENT COURSE - Students are highly satisfied with {subject}.\n')
            f.write(f'  ✅ This course demonstrates effective teaching methods and engaging content.\n')
            f.write(f'  ✅ Can serve as a model for other courses in the curriculum.\n')
        elif score >= 0.5:
            sentiment_category = 'Good'
            f.write(f'  ✔️  GOOD COURSE - Overall positive student feedback for {subject}.\n')
            f.write(f'  ✔️  Students generally enjoy this course with some room for improvement.\n')
        elif score >= -0.5:
            sentiment_category = 'Acceptable'
            f.write(f'  ⚠️  ACCEPTABLE COURSE - Mixed feedback for {subject}.\n')
            f.write(f'  ⚠️  Students have neutral feelings; course meets basic expectations.\n')
        elif score >= -1.0:
            sentiment_category = 'Needs Improvement'
            f.write(f'  ⚠️  NEEDS IMPROVEMENT - Students express concerns about {subject}.\n')
            f.write(f'  ⚠️  Moderate negative sentiment detected; requires attention.\n')
        else:
            sentiment_category = 'Critical'
            f.write(f'  ❌ CRITICAL - Significant student dissatisfaction with {subject}.\n')
            f.write(f'  ❌ High levels of boredom or disappointment; urgent intervention needed.\n')
        
        # Specific emotion-based insights
        if course_emotions.empty:
            f.write('  ℹ️  Limited feedback data available.\n')
        else:
            max_emotion = course_emotions.loc[course_emotions['Percentage'].idxmax(), 'Label']
            max_pct = course_emotions['Percentage'].max()
            
            if max_emotion == 'Joy':
                f.write(f'  😊 Joy dominates ({max_pct:.1f}%) - Students find the course enjoyable and engaging.\n')
            elif max_emotion == 'Satisfaction':
                f.write(f'  ✅ Satisfaction dominates ({max_pct:.1f}%) - Students are content with course delivery.\n')
            elif max_emotion == 'Acceptance':
                f.write(f'  🤷 Acceptance dominates ({max_pct:.1f}%) - Students tolerate the course but lack enthusiasm.\n')
            elif max_emotion == 'Boredom':
                f.write(f'  😴 Boredom dominates ({max_pct:.1f}%) - Teaching style or content fails to engage students.\n')
            elif max_emotion == 'Disappointment':
                f.write(f'  😞 Disappointment dominates ({max_pct:.1f}%) - Course fails to meet student expectations.\n')
        
        # Recommendations
        f.write('\nRecommendations:\n')
        
        if score >= 1.5:
            f.write('  💡 Maintain current teaching strategies and methods.\n')
            f.write('  💡 Document best practices for replication in other courses.\n')
            f.write('  💡 Consider having this instructor mentor others.\n')
        elif score >= 0.5:
            f.write('  💡 Continue current approach with minor refinements.\n')
            f.write('  💡 Gather more specific feedback to identify improvement areas.\n')
            f.write('  💡 Share successful strategies with similar courses.\n')
        elif score >= -0.5:
            f.write('  💡 Review course content and teaching methods.\n')
            f.write('  💡 Increase student engagement through interactive activities.\n')
            f.write('  💡 Solicit detailed feedback on pain points.\n')
        elif score >= -1.0:
            f.write('  💡 Conduct comprehensive course review with stakeholders.\n')
            f.write('  💡 Consider curriculum redesign or instructor support.\n')
            f.write('  💡 Implement immediate interventions to improve student experience.\n')
        else:
            f.write('  💡 URGENT: Schedule immediate review with department head.\n')
            f.write('  💡 Consider temporary course suspension for restructuring.\n')
            f.write('  💡 Provide intensive instructor training or reassignment.\n')
            f.write('  💡 Develop action plan with clear milestones for improvement.\n')
        
        # Sample size consideration
        if count < 5:
            f.write('  ⚠️  NOTE: Small sample size (n<5) - results may not be representative.\n')
        elif count < 10:
            f.write('  ℹ️  NOTE: Moderate sample size (n<10) - collect more feedback for better insights.\n')
        else:
            f.write(f'  ✅ Good sample size (n={count}) - results are statistically meaningful.\n')
        
        f.write('\n' + '='*100 + '\n\n')
    
    # Summary statistics
    f.write('\nSTATISTICAL SUMMARY\n')
    f.write('='*100 + '\n')
    f.write(f'Best Course: {sorted_courses.iloc[0]["Course_code"]} - {sorted_courses.iloc[0]["Subject_Description"]} (Score: {sorted_courses.iloc[0]["Average_Sentiment_Score"]:.3f})\n')
    f.write(f'Worst Course: {sorted_courses.iloc[-1]["Course_code"]} - {sorted_courses.iloc[-1]["Subject_Description"]} (Score: {sorted_courses.iloc[-1]["Average_Sentiment_Score"]:.3f})\n')
    f.write(f'Average Score: {avg_score:.3f}\n')
    f.write(f'Median Score: {scores_df["Average_Sentiment_Score"].median():.3f}\n')
    f.write(f'Standard Deviation: {scores_df["Average_Sentiment_Score"].std():.3f}\n')
    f.write('='*100 + '\n')

print(f'\n✅ Comprehensive insights report saved to: {report_path}')

# Also create a summary CSV with insights categories
summary_df = scores_df.copy()
summary_df['Sentiment_Category'] = summary_df['Average_Sentiment_Score'].apply(
    lambda x: 'Excellent' if x >= 1.5 else 
              'Good' if x >= 0.5 else 
              'Acceptable' if x >= -0.5 else 
              'Needs Improvement' if x >= -1.0 else 
              'Critical'
)

summary_df['Priority'] = summary_df['Average_Sentiment_Score'].apply(
    lambda x: 'Low' if x >= 0.5 else 
              'Medium' if x >= -0.5 else 
              'High' if x >= -1.0 else 
              'Urgent'
)

summary_csv_path = output_dir / 'course_insights_summary.csv'
summary_df.to_csv(summary_csv_path, index=False)
print(f'✅ Summary insights CSV saved to: {summary_csv_path}')

# Print quick statistics
print('\n' + '='*100)
print('QUICK STATISTICS')
print('='*100)
print(f'Excellent Courses: {len(summary_df[summary_df["Sentiment_Category"] == "Excellent"])}')
print(f'Good Courses: {len(summary_df[summary_df["Sentiment_Category"] == "Good"])}')
print(f'Acceptable Courses: {len(summary_df[summary_df["Sentiment_Category"] == "Acceptable"])}')
print(f'Needs Improvement: {len(summary_df[summary_df["Sentiment_Category"] == "Needs Improvement"])}')
print(f'Critical Courses: {len(summary_df[summary_df["Sentiment_Category"] == "Critical"])}')
print('\nPriority Levels:')
print(f'Urgent Action Required: {len(summary_df[summary_df["Priority"] == "Urgent"])}')
print(f'High Priority: {len(summary_df[summary_df["Priority"] == "High"])}')
print(f'Medium Priority: {len(summary_df[summary_df["Priority"] == "Medium"])}')
print(f'Low Priority: {len(summary_df[summary_df["Priority"] == "Low"])}')
print('='*100)
