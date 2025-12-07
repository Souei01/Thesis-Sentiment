from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Avg, Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import os
import json
from datetime import datetime
from .models import Course, CourseAssignment, Enrollment, FeedbackSession, Feedback
from authentication.models import User
from .ml_models.emotion_predictor import predict_emotions_batch
import logging

logger = logging.getLogger(__name__)

def load_training_data(request):
    # Path to your training data file
    data_path = os.path.join('server', 'data', 'Data Sample Training.xlsx - Annotator 1.csv')
    try:
        df = pd.read_csv(data_path)
        
        # Create separate rows for each feedback type with its corresponding label
        rows = []
        
        for index, row in df.iterrows():
            # Add suggested_changes row (include even if empty)
            feedback_text = row['suggested_changes'] if pd.notna(row['suggested_changes']) else 'No response'
            rows.append({
                'question': 'suggested_changes',
                'feedback': feedback_text,
                'label': row['suggested_changes_label'],
            })
            
            # Add best_teaching_aspect row (include even if empty)
            feedback_text = row['best_teaching_aspect'] if pd.notna(row['best_teaching_aspect']) else 'No response'
            rows.append({
                'question': 'best_teaching_aspect',
                'feedback': feedback_text,
                'label': row['best_teaching_aspect_label'],
            })
            
            # Add least_teaching_aspect row (include even if empty)
            feedback_text = row['least_teaching_aspect'] if pd.notna(row['least_teaching_aspect']) else 'No response'
            rows.append({
                'question': 'least_teaching_aspect',
                'feedback': feedback_text,
                'label': row['least_teaching_aspect_label'],
            })
            
            # Add further_comments row (include even if empty)
            feedback_text = row['further_comments'] if pd.notna(row['further_comments']) else 'No response'
            rows.append({
                'question': 'further_comments',
                'feedback': feedback_text,
                'label': row['further_comments_label'],
            })
        
        # Create new DataFrame with separate rows
        training_df = pd.DataFrame(rows)
        
        print(training_df.head())  # Show first 5 rows in terminal
        print(training_df.info())    # Show column info and data types
        
        # Convert ALL DataFrame rows to HTML table for browser viewing
        html_table = training_df.to_html(classes='table table-striped', table_id='data-preview')
        
        html_content = f"""
        <html>
        <head>
            <title>Data Preview</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .info {{ background-color: #f0f0f0; padding: 10px; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="info">
                <p><strong>Shape:</strong> {training_df.shape[0]} rows, {training_df.shape[1]} columns</p>
                <p><strong>Columns:</strong> {', '.join(training_df.columns)}</p>
            </div>
            {html_table}
        </body>
        </html>
        """
        
        return HttpResponse(html_content)
    except Exception as e:
        return JsonResponse({'error': str(e)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_enrollments(request):
    """Get all enrolled courses for the authenticated student"""
    try:
        print(f"Request received from user: {request.user.email}, role: {request.user.role}")
        user = request.user
        
        if user.role != 'student':
            return Response(
                {'error': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get active feedback session
        active_session = FeedbackSession.objects.filter(is_active=True).first()
        print(f"Active session: {active_session}")
        
        # Get student's enrollments
        enrollments = Enrollment.objects.filter(
            student=user,
            course_assignment__is_active=True
        ).select_related(
            'course_assignment__course',
            'course_assignment__instructor'
        )
        
        print(f"Found {enrollments.count()} enrollments for student")
        
        courses_data = []
        for enrollment in enrollments:
            assignment = enrollment.course_assignment
            course = assignment.course
            
            # Check if student has submitted feedback for this assignment
            has_feedback = False
            if active_session:
                has_feedback = Feedback.objects.filter(
                    student=user,
                    course_assignment=assignment,
                    feedback_session=active_session
                ).exists()
            
            # Map semester to display format
            if assignment.semester == 'Summer':
                semester_display = 'Summer'
            else:
                semester_display = f"{assignment.semester} Semester"
            
            # Assign color based on course code prefix
            color = 'blue'
            if course.code.startswith('CC'):
                color = 'pink'
            elif course.code.startswith('IT'):
                color = 'blue'
            elif course.code.startswith('CS'):
                color = 'green'
            elif course.code.startswith('ACT'):
                color = 'yellow'
            
            courses_data.append({
                'id': str(assignment.id),
                'code': course.code,
                'name': course.name,
                'description': course.description,
                'semester': semester_display,
                'instructor': assignment.instructor.get_display_name(),
                'instructor_id': assignment.instructor.id,
                'section': assignment.section,
                'schedule': assignment.schedule,
                'hasSubmittedFeedback': has_feedback,
                'progress': 100 if has_feedback else 0,
                'color': color,
                'dueDate': active_session.end_date.strftime('%d %B %Y') if active_session else 'No active session',
            })
        
        print(f"Returning {len(courses_data)} courses")
        
        return Response({
            'courses': courses_data,
            'active_session': {
                'title': active_session.title,
                'start_date': active_session.start_date,
                'end_date': active_session.end_date,
                'instructions': active_session.instructions,
            } if active_session else None
        })
    except Exception as e:
        print(f"ERROR in get_student_enrollments: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    """Submit feedback for a course assignment"""
    user = request.user
    
    if user.role != 'student':
        return Response(
            {'error': 'Only students can submit feedback'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get active feedback session
    active_session = FeedbackSession.objects.filter(is_active=True).first()
    if not active_session:
        return Response(
            {'error': 'No active feedback session'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get data from request
    assignment_id = request.data.get('courseId')
    feedback_data = request.data.get('feedback', {})
    
    try:
        assignment = CourseAssignment.objects.get(id=assignment_id)
    except CourseAssignment.DoesNotExist:
        return Response(
            {'error': 'Course assignment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if student is enrolled
    enrollment = Enrollment.objects.filter(
        student=user,
        course_assignment=assignment
    ).first()
    
    if not enrollment:
        return Response(
            {'error': 'You are not enrolled in this course'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if feedback already submitted
    existing_feedback = Feedback.objects.filter(
        student=user,
        course_assignment=assignment,
        feedback_session=active_session
    ).first()
    
    if existing_feedback:
        return Response(
            {'error': 'Feedback already submitted for this course'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Helper function to sanitize and validate text input
    def sanitize_text_input(text, max_length=2000):
        """Sanitize text input to prevent injection attacks and enforce length limits"""
        if not text:
            return ''
        
        # Strip whitespace
        text = text.strip()
        
        # Enforce maximum length
        if len(text) > max_length:
            text = text[:max_length]
        
        # HTML escape to prevent XSS
        from html import escape
        text = escape(text)
        
        return text
    
    # Extract and sanitize text feedback for emotion analysis
    text_feedback = {
        'suggested_changes': sanitize_text_input(
            feedback_data.get('comments', {}).get('recommendedChanges', ''), 
            max_length=1000
        ),
        'best_teaching_aspect': sanitize_text_input(
            feedback_data.get('comments', {}).get('likeBest', ''), 
            max_length=1000
        ),
        'least_teaching_aspect': sanitize_text_input(
            feedback_data.get('comments', {}).get('likeLeast', ''), 
            max_length=1000
        ),
        'further_comments': sanitize_text_input(
            feedback_data.get('comments', {}).get('additionalComments', ''), 
            max_length=2000
        ),
    }
    
    # Validate rating values to ensure they're within acceptable range (1-5)
    def validate_rating(value, default=3):
        """Validate rating is an integer between 1-5"""
        try:
            rating = int(value)
            if 1 <= rating <= 5:
                return rating
        except (TypeError, ValueError):
            pass
        return default
    
    # Predict emotions for all text fields (batch prediction for efficiency)
    logger.info("Predicting emotions for feedback text...")
    try:
        texts_to_predict = [
            text_feedback['suggested_changes'],
            text_feedback['best_teaching_aspect'],
            text_feedback['least_teaching_aspect'],
            text_feedback['further_comments']
        ]
        
        emotion_predictions = predict_emotions_batch(texts_to_predict, return_all_scores=True)
        
        logger.info(f"Emotion predictions: {emotion_predictions}")
    except Exception as e:
        logger.error(f"Error predicting emotions: {str(e)}")
        # Use default values if prediction fails
        emotion_predictions = [
            {'emotion': 'acceptance', 'confidence': 0.0, 'all_scores': {}},
            {'emotion': 'acceptance', 'confidence': 0.0, 'all_scores': {}},
            {'emotion': 'acceptance', 'confidence': 0.0, 'all_scores': {}},
            {'emotion': 'acceptance', 'confidence': 0.0, 'all_scores': {}}
        ]
    
    # Create feedback
    feedback = Feedback.objects.create(
        student=user,
        course_assignment=assignment,
        feedback_session=active_session,
        # Part 1: Commitment
        rating_sensitivity=validate_rating(feedback_data.get('commitment', {}).get('sensitivity', 3)),
        rating_integration=validate_rating(feedback_data.get('commitment', {}).get('integration', 3)),
        rating_availability=validate_rating(feedback_data.get('commitment', {}).get('availability', 3)),
        rating_punctuality=validate_rating(feedback_data.get('commitment', {}).get('punctuality', 3)),
        rating_record_keeping=validate_rating(feedback_data.get('commitment', {}).get('recordKeeping', 3)),
        # Part 2: Knowledge of Subject
        rating_mastery=validate_rating(feedback_data.get('knowledgeOfSubject', {}).get('mastery', 3)),
        rating_state_of_art=validate_rating(feedback_data.get('knowledgeOfSubject', {}).get('stateOfArt', 3)),
        rating_practical_integration=validate_rating(feedback_data.get('knowledgeOfSubject', {}).get('practicalIntegration', 3)),
        rating_relevance=validate_rating(feedback_data.get('knowledgeOfSubject', {}).get('relevance', 3)),
        rating_current_trends=validate_rating(feedback_data.get('knowledgeOfSubject', {}).get('currentTrends', 3)),
        # Part 3: Independent Learning
        rating_teaching_strategies=validate_rating(feedback_data.get('independentLearning', {}).get('teachingStrategies', 3)),
        rating_student_esteem=validate_rating(feedback_data.get('independentLearning', {}).get('studentEsteem', 3)),
        rating_student_autonomy=validate_rating(feedback_data.get('independentLearning', {}).get('studentAutonomy', 3)),
        rating_independent_thinking=validate_rating(feedback_data.get('independentLearning', {}).get('independentThinking', 3)),
        rating_beyond_required=validate_rating(feedback_data.get('independentLearning', {}).get('beyondRequired', 3)),
        # Part 4: Management of Learning
        rating_student_contribution=validate_rating(feedback_data.get('managementOfLearning', {}).get('studentContribution', 3)),
        rating_facilitator_role=validate_rating(feedback_data.get('managementOfLearning', {}).get('facilitatorRole', 3)),
        rating_discussion_encouragement=validate_rating(feedback_data.get('managementOfLearning', {}).get('discussionEncouragement', 3)),
        rating_instructional_methods=validate_rating(feedback_data.get('managementOfLearning', {}).get('instructionalMethods', 3)),
        rating_instructional_materials=validate_rating(feedback_data.get('managementOfLearning', {}).get('instructionalMaterials', 3)),
        # Part 5: Feedback and Assessment
        rating_clear_communication=validate_rating(feedback_data.get('feedbackAssessment', {}).get('clearCommunication', 3)),
        rating_timely_feedback=validate_rating(feedback_data.get('feedbackAssessment', {}).get('timelyFeedback', 3)),
        rating_improvement_feedback=validate_rating(feedback_data.get('feedbackAssessment', {}).get('improvementFeedback', 3)),
        # Part 6: Other Questions
        syllabus_explained=feedback_data.get('otherQuestions', {}).get('syllabusExplained'),
        delivered_as_outlined=feedback_data.get('otherQuestions', {}).get('deliveredAsOutlined'),
        grading_criteria_explained=feedback_data.get('otherQuestions', {}).get('gradingCriteriaExplained'),
        exams_related=feedback_data.get('otherQuestions', {}).get('examsRelated'),
        assignments_related=feedback_data.get('otherQuestions', {}).get('assignmentsRelated'),
        lms_resources_useful=feedback_data.get('otherQuestions', {}).get('lmsResourcesUseful'),
        # Part 7: Overall Experience
        worthwhile_class=feedback_data.get('overallExperience', {}).get('worthwhileClass'),
        would_recommend=feedback_data.get('overallExperience', {}).get('wouldRecommend'),
        hours_per_week=validate_rating(feedback_data.get('overallExperience', {}).get('hoursPerWeek', 0)),
        overall_rating=validate_rating(feedback_data.get('overallExperience', {}).get('overallRating', 3)),
        # Part 8: Student Self-Evaluation
        rating_constructive_contribution=validate_rating(feedback_data.get('studentEvaluation', {}).get('constructiveContribution', 3)),
        rating_achieving_outcomes=validate_rating(feedback_data.get('studentEvaluation', {}).get('achievingOutcomes', 3)),
        # Part 9: Comments (Text feedback)
        suggested_changes=text_feedback['suggested_changes'],
        best_teaching_aspect=text_feedback['best_teaching_aspect'],
        least_teaching_aspect=text_feedback['least_teaching_aspect'],
        further_comments=text_feedback['further_comments'],
        # Emotion predictions (XLM-RoBERTa)
        emotion_suggested_changes=emotion_predictions[0]['emotion'],
        emotion_best_aspect=emotion_predictions[1]['emotion'],
        emotion_least_aspect=emotion_predictions[2]['emotion'],
        emotion_further_comments=emotion_predictions[3]['emotion'],
        emotion_confidence_scores={
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
    )
    
    # Trigger topic modeling after every 5 new feedbacks
    try:
        total_feedbacks = Feedback.objects.filter(status='submitted').count()
        
        # Check if we should run topic modeling
        # Run if: at 10 feedbacks OR multiple of 5 feedbacks after 10
        should_run = (total_feedbacks == 10) or (total_feedbacks > 10 and total_feedbacks % 5 == 0)
        
        if should_run:
            logger.info(f"Triggering topic modeling task ({total_feedbacks} feedbacks)...")
            
            # Run asynchronously in background
            from threading import Thread
            from pathlib import Path
            import subprocess
            import sys
            
            def run_topic_modeling_background():
                try:
                    python_exe = sys.executable
                    script_path = Path(__file__).parent.parent / 'run_topic_modeling_task.py'
                    subprocess.Popen(
                        [python_exe, str(script_path)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        cwd=Path(__file__).parent.parent
                    )
                    logger.info("✅ Topic modeling task started in background")
                except Exception as e:
                    logger.error(f"Failed to start topic modeling: {str(e)}")
            
            # Start in separate thread to not block response
            Thread(target=run_topic_modeling_background, daemon=True).start()
    
    except Exception as e:
        # Don't fail feedback submission if topic modeling fails
        logger.error(f"Error triggering topic modeling: {str(e)}")
    
    return Response({
        'success': True,
        'message': 'Feedback submitted successfully',
        'feedback_id': feedback.id,
        'average_rating': feedback.rating
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_faculty_courses(request):
    """Get all courses assigned to the authenticated faculty member"""
    user = request.user
    
    if user.role != 'faculty':
        return Response(
            {'error': 'Only faculty can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get faculty's course assignments
    assignments = CourseAssignment.objects.filter(
        instructor=user,
        is_active=True
    ).select_related('course')
    
    courses_data = []
    for assignment in assignments:
        course = assignment.course
        
        # Count enrolled students
        enrollment_count = assignment.enrollments.count()
        
        # Count feedback received
        feedback_count = Feedback.objects.filter(
            course_assignment=assignment
        ).count()
        
        courses_data.append({
            'id': str(assignment.id),
            'code': course.code,
            'name': course.name,
            'description': course.description,
            'semester': assignment.semester,
            'section': assignment.section,
            'schedule': assignment.schedule,
            'academic_year': assignment.academic_year,
            'enrolled_students': enrollment_count,
            'feedback_received': feedback_count,
        })
    
    return Response({
        'courses': courses_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feedback_analytics(request):
    """Get aggregated feedback analytics with filters"""
    user = request.user
    
    if user.role not in ['faculty', 'admin']:
        return Response(
            {'error': 'Only faculty and admin can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get filter parameters
    semester = request.GET.get('semester')  # e.g., '1st', '2nd'
    academic_year = request.GET.get('academic_year')  # e.g., '2024-2025'
    instructor_id = request.GET.get('instructor_id')  # faculty ID
    course_id = request.GET.get('course_id')  # specific course
    department = request.GET.get('department')  # e.g., 'CS', 'IT', 'ICT'
    
    # Base queryset
    feedback_qs = Feedback.objects.filter(status='submitted')
    
    # Apply department filter for dean (overrides RBAC)
    if department and user.role == 'admin' and user.admin_subrole == 'dean':
        if department == 'CS':
            feedback_qs = feedback_qs.filter(course_assignment__course__code__startswith='CS')
        elif department == 'IT':
            feedback_qs = feedback_qs.filter(
                Q(course_assignment__course__code__startswith='IT') |
                Q(course_assignment__course__code__startswith='ICT') |
                Q(course_assignment__course__code__startswith='ACT')
            )
    # RBAC: Department head restrictions (only if no department filter)
    elif user.role == 'admin' and user.admin_subrole:
        if user.admin_subrole == 'dept_head_cs':
            # CS Department Head: only CS courses
            feedback_qs = feedback_qs.filter(course_assignment__course__code__startswith='CS')
        elif user.admin_subrole == 'dept_head_it':
            # IT Department Head: IT and ICT/ACT courses
            feedback_qs = feedback_qs.filter(
                Q(course_assignment__course__code__startswith='IT') |
                Q(course_assignment__course__code__startswith='ICT') |
                Q(course_assignment__course__code__startswith='ACT')
            )
        # dean has no restrictions (sees all)
    
    # Apply filters
    if semester:
        feedback_qs = feedback_qs.filter(feedback_session__semester=semester)
    
    if academic_year:
        feedback_qs = feedback_qs.filter(feedback_session__academic_year=academic_year)
    
    if instructor_id:
        feedback_qs = feedback_qs.filter(course_assignment__instructor_id=instructor_id)
    elif user.role == 'faculty':
        # Faculty can only see their own feedback
        feedback_qs = feedback_qs.filter(course_assignment__instructor=user)
    
    if course_id:
        feedback_qs = feedback_qs.filter(course_assignment_id=course_id)
    
    # Get count
    total_feedback = feedback_qs.count()
    
    if total_feedback == 0:
        return Response({
            'total_feedback': 0,
            'message': 'No feedback data available for the selected filters'
        })
    
    # Aggregate ratings
    aggregates = feedback_qs.aggregate(
        average_rating=Avg('rating'),
        # Commitment
        avg_sensitivity=Avg('rating_sensitivity'),
        avg_integration=Avg('rating_integration'),
        avg_availability=Avg('rating_availability'),
        avg_punctuality=Avg('rating_punctuality'),
        avg_record_keeping=Avg('rating_record_keeping'),
        # Knowledge of Subject
        avg_mastery=Avg('rating_mastery'),
        avg_state_of_art=Avg('rating_state_of_art'),
        avg_practical_integration=Avg('rating_practical_integration'),
        avg_relevance=Avg('rating_relevance'),
        avg_current_trends=Avg('rating_current_trends'),
        # Independent Learning
        avg_teaching_strategies=Avg('rating_teaching_strategies'),
        avg_student_esteem=Avg('rating_student_esteem'),
        avg_student_autonomy=Avg('rating_student_autonomy'),
        avg_independent_thinking=Avg('rating_independent_thinking'),
        avg_beyond_required=Avg('rating_beyond_required'),
        # Management of Learning
        avg_student_contribution=Avg('rating_student_contribution'),
        avg_facilitator_role=Avg('rating_facilitator_role'),
        avg_discussion_encouragement=Avg('rating_discussion_encouragement'),
        avg_instructional_methods=Avg('rating_instructional_methods'),
        avg_instructional_materials=Avg('rating_instructional_materials'),
        # Feedback and Assessment
        avg_clear_communication=Avg('rating_clear_communication'),
        avg_timely_feedback=Avg('rating_timely_feedback'),
        avg_improvement_feedback=Avg('rating_improvement_feedback'),
        # Overall
        avg_overall_rating=Avg('overall_rating'),
        avg_hours_per_week=Avg('hours_per_week'),
        # Student Self-Evaluation
        avg_constructive_contribution=Avg('rating_constructive_contribution'),
        avg_achieving_outcomes=Avg('rating_achieving_outcomes'),
        # Yes/No percentages
        total_responses=Count('id'),
        syllabus_yes=Count('id', filter=Q(syllabus_explained=True)),
        delivered_yes=Count('id', filter=Q(delivered_as_outlined=True)),
        grading_yes=Count('id', filter=Q(grading_criteria_explained=True)),
        exams_yes=Count('id', filter=Q(exams_related=True)),
        assignments_yes=Count('id', filter=Q(assignments_related=True)),
        lms_yes=Count('id', filter=Q(lms_resources_useful=True)),
        worthwhile_yes=Count('id', filter=Q(worthwhile_class=True)),
        recommend_yes=Count('id', filter=Q(would_recommend=True)),
    )
    
    # Calculate percentages for Yes/No questions
    total = aggregates['total_responses']
    
    # Get text feedback samples with related student and course info
    text_feedback = []
    for fb in feedback_qs.select_related('student', 'course_assignment__course')[:100]:
        text_feedback.append({
            'id': fb.id,
            'suggested_changes': fb.suggested_changes or '',
            'best_teaching_aspect': fb.best_teaching_aspect or '',
            'least_teaching_aspect': fb.least_teaching_aspect or '',
            'further_comments': fb.further_comments or '',
            'sentiment_score': fb.sentiment_score if fb.sentiment_score is not None else 0,
            'sentiment_label': fb.sentiment_label or 'neutral',
            'student_name': fb.student.get_full_name() if fb.student else 'Anonymous',
            'course_name': fb.course_assignment.course.name if fb.course_assignment and fb.course_assignment.course else 'Unknown',
            'submitted_at': fb.submitted_at.isoformat() if fb.submitted_at else None,
        })
    
    # Prepare response
    response_data = {
        'total_feedback': total_feedback,
        'average_rating': round(aggregates['average_rating'], 2) if aggregates['average_rating'] else 0,
        
        # Commitment (Part A)
        'commitment': {
            'sensitivity': round(aggregates['avg_sensitivity'], 2) if aggregates['avg_sensitivity'] else 0,
            'integration': round(aggregates['avg_integration'], 2) if aggregates['avg_integration'] else 0,
            'availability': round(aggregates['avg_availability'], 2) if aggregates['avg_availability'] else 0,
            'punctuality': round(aggregates['avg_punctuality'], 2) if aggregates['avg_punctuality'] else 0,
            'record_keeping': round(aggregates['avg_record_keeping'], 2) if aggregates['avg_record_keeping'] else 0,
        },
        
        # Knowledge of Subject (Part B)
        'knowledge': {
            'mastery': round(aggregates['avg_mastery'], 2) if aggregates['avg_mastery'] else 0,
            'state_of_art': round(aggregates['avg_state_of_art'], 2) if aggregates['avg_state_of_art'] else 0,
            'practical_integration': round(aggregates['avg_practical_integration'], 2) if aggregates['avg_practical_integration'] else 0,
            'relevance': round(aggregates['avg_relevance'], 2) if aggregates['avg_relevance'] else 0,
            'current_trends': round(aggregates['avg_current_trends'], 2) if aggregates['avg_current_trends'] else 0,
        },
        
        # Independent Learning (Part C)
        'independent_learning': {
            'teaching_strategies': round(aggregates['avg_teaching_strategies'], 2) if aggregates['avg_teaching_strategies'] else 0,
            'student_esteem': round(aggregates['avg_student_esteem'], 2) if aggregates['avg_student_esteem'] else 0,
            'student_autonomy': round(aggregates['avg_student_autonomy'], 2) if aggregates['avg_student_autonomy'] else 0,
            'independent_thinking': round(aggregates['avg_independent_thinking'], 2) if aggregates['avg_independent_thinking'] else 0,
            'beyond_required': round(aggregates['avg_beyond_required'], 2) if aggregates['avg_beyond_required'] else 0,
        },
        
        # Management of Learning (Part D)
        'management': {
            'student_contribution': round(aggregates['avg_student_contribution'], 2) if aggregates['avg_student_contribution'] else 0,
            'facilitator_role': round(aggregates['avg_facilitator_role'], 2) if aggregates['avg_facilitator_role'] else 0,
            'discussion_encouragement': round(aggregates['avg_discussion_encouragement'], 2) if aggregates['avg_discussion_encouragement'] else 0,
            'instructional_methods': round(aggregates['avg_instructional_methods'], 2) if aggregates['avg_instructional_methods'] else 0,
            'instructional_materials': round(aggregates['avg_instructional_materials'], 2) if aggregates['avg_instructional_materials'] else 0,
        },
        
        # Feedback and Assessment (Part E)
        'feedback_assessment': {
            'clear_communication': round(aggregates['avg_clear_communication'], 2) if aggregates['avg_clear_communication'] else 0,
            'timely_feedback': round(aggregates['avg_timely_feedback'], 2) if aggregates['avg_timely_feedback'] else 0,
            'improvement_feedback': round(aggregates['avg_improvement_feedback'], 2) if aggregates['avg_improvement_feedback'] else 0,
        },
        
        # Overall Experience (Part G)
        'overall': {
            'rating': round(aggregates['avg_overall_rating'], 2) if aggregates['avg_overall_rating'] else 0,
            'hours_per_week': round(aggregates['avg_hours_per_week'], 2) if aggregates['avg_hours_per_week'] else 0,
        },
        
        # Student Self-Evaluation (Part H)
        'student_evaluation': {
            'constructive_contribution': round(aggregates['avg_constructive_contribution'], 2) if aggregates['avg_constructive_contribution'] else 0,
            'achieving_outcomes': round(aggregates['avg_achieving_outcomes'], 2) if aggregates['avg_achieving_outcomes'] else 0,
        },
        
        # Yes/No Questions (Part F - percentages)
        'course_info': {
            'syllabus_explained': round((aggregates['syllabus_yes'] / total * 100), 1) if total > 0 else 0,
            'delivered_as_outlined': round((aggregates['delivered_yes'] / total * 100), 1) if total > 0 else 0,
            'grading_criteria_explained': round((aggregates['grading_yes'] / total * 100), 1) if total > 0 else 0,
            'exams_related': round((aggregates['exams_yes'] / total * 100), 1) if total > 0 else 0,
            'assignments_related': round((aggregates['assignments_yes'] / total * 100), 1) if total > 0 else 0,
            'lms_resources_useful': round((aggregates['lms_yes'] / total * 100), 1) if total > 0 else 0,
            'worthwhile_class': round((aggregates['worthwhile_yes'] / total * 100), 1) if total > 0 else 0,
            'would_recommend': round((aggregates['recommend_yes'] / total * 100), 1) if total > 0 else 0,
        },
        
        # Text feedback
        'text_feedback': text_feedback,
        
        # Filter info
        'filters': {
            'semester': semester,
            'academic_year': academic_year,
            'instructor_id': instructor_id,
            'course_id': course_id,
        }
    }
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_emotion_analytics(request):
    """Get emotion distribution analytics from feedback"""
    user = request.user
    
    if user.role not in ['faculty', 'admin']:
        return Response(
            {'error': 'Only faculty and admin can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get filter parameters
    semester = request.GET.get('semester')
    academic_year = request.GET.get('academic_year')
    instructor_id = request.GET.get('instructor_id')
    course_id = request.GET.get('course_id')
    department = request.GET.get('department')
    
    # Base queryset
    feedback_qs = Feedback.objects.filter(status='submitted')
    
    # Apply department filter for dean (overrides RBAC)
    if department and user.role == 'admin' and user.admin_subrole == 'dean':
        if department == 'CS':
            feedback_qs = feedback_qs.filter(course_assignment__course__code__startswith='CS')
        elif department == 'IT':
            feedback_qs = feedback_qs.filter(
                Q(course_assignment__course__code__startswith='IT') |
                Q(course_assignment__course__code__startswith='ICT') |
                Q(course_assignment__course__code__startswith='ACT')
            )
    # RBAC: Department head restrictions (only if no department filter)
    elif user.role == 'admin' and user.admin_subrole:
        if user.admin_subrole == 'dept_head_cs':
            # CS Department Head: only CS courses
            feedback_qs = feedback_qs.filter(course_assignment__course__code__startswith='CS')
        elif user.admin_subrole == 'dept_head_it':
            # IT Department Head: IT and ICT/ACT courses
            feedback_qs = feedback_qs.filter(
                Q(course_assignment__course__code__startswith='IT') |
                Q(course_assignment__course__code__startswith='ICT') |
                Q(course_assignment__course__code__startswith='ACT')
            )
        # dean has no restrictions (sees all)
    
    # Apply filters
    if semester:
        feedback_qs = feedback_qs.filter(feedback_session__semester=semester)
    if academic_year:
        feedback_qs = feedback_qs.filter(feedback_session__academic_year=academic_year)
    if instructor_id:
        feedback_qs = feedback_qs.filter(course_assignment__instructor_id=instructor_id)
    elif user.role == 'faculty':
        feedback_qs = feedback_qs.filter(course_assignment__instructor=user)
    if course_id:
        feedback_qs = feedback_qs.filter(course_assignment_id=course_id)
    
    # Count emotions for each field
    emotion_fields = [
        'emotion_suggested_changes',
        'emotion_best_aspect',
        'emotion_least_aspect',
        'emotion_further_comments'
    ]
    
    emotion_counts = {
        'joy': 0,
        'satisfaction': 0,
        'acceptance': 0,
        'boredom': 0,
        'disappointment': 0
    }
    
    # Aggregate emotions from all fields
    for field in emotion_fields:
        field_counts = feedback_qs.values(field).annotate(count=Count(field))
        for item in field_counts:
            emotion = item[field]
            if emotion and emotion in emotion_counts:
                emotion_counts[emotion] += item['count']
    
    # Get emotion distribution by feedback field
    field_emotions = {}
    field_names = {
        'emotion_suggested_changes': 'Suggested Changes',
        'emotion_best_aspect': 'Best Aspect',
        'emotion_least_aspect': 'Least Aspect',
        'emotion_further_comments': 'Additional Comments'
    }
    
    for field in emotion_fields:
        field_name = field_names.get(field, field)
        field_dist = {'joy': 0, 'satisfaction': 0, 'acceptance': 0, 'boredom': 0, 'disappointment': 0}
        field_counts = feedback_qs.values(field).annotate(count=Count(field))
        for item in field_counts:
            emotion = item[field]
            if emotion and emotion in field_dist:
                field_dist[emotion] = item['count']
        field_emotions[field_name] = field_dist
    
    total_emotions = sum(emotion_counts.values())
    
    return Response({
        'total_feedback': feedback_qs.count(),
        'total_emotions_analyzed': total_emotions,
        'emotion_distribution': emotion_counts,
        'emotion_by_field': field_emotions,
        'emotion_percentages': {
            emotion: round((count / total_emotions * 100), 2) if total_emotions > 0 else 0
            for emotion, count in emotion_counts.items()
        }
    })


def generate_topic_insights(keywords, emotion_dist=None):
    """Generate actionable insights based on topic keywords and emotions"""
    insights = []
    
    # Keyword-based insights
    keyword_set = set([k.lower() for k in keywords])
    
    # Teaching quality related
    if any(word in keyword_set for word in ['teaching', 'explain', 'instruction', 'clear', 'understanding']):
        if emotion_dist and (emotion_dist.get('boredom', 0) > emotion_dist.get('joy', 0)):
            insights.append({
                'category': 'Teaching Methods',
                'priority': 'high',
                'suggestion': 'Consider varying teaching methods and pace. Students may benefit from more interactive activities.',
                'icon': 'presentation'
            })
        else:
            insights.append({
                'category': 'Teaching Methods',
                'priority': 'medium',
                'suggestion': 'Continue current teaching approach while exploring new pedagogical techniques.',
                'icon': 'presentation'
            })
    
    # Materials and resources
    if any(word in keyword_set for word in ['material', 'resource', 'book', 'slide', 'handout', 'notes']):
        insights.append({
            'category': 'Learning Materials',
            'priority': 'medium',
            'suggestion': 'Review and update course materials. Consider adding more diverse resources like videos or interactive content.',
            'icon': 'book'
        })
    
    # Assessment and grading
    if any(word in keyword_set for word in ['exam', 'test', 'grade', 'assessment', 'quiz', 'assignment']):
        if emotion_dist and emotion_dist.get('disappointment', 0) > 0:
            insights.append({
                'category': 'Assessment',
                'priority': 'high',
                'suggestion': 'Review assessment criteria and grading rubrics. Provide clearer expectations and more timely feedback.',
                'icon': 'clipboard'
            })
        else:
            insights.append({
                'category': 'Assessment',
                'priority': 'low',
                'suggestion': 'Maintain current assessment practices. Consider providing practice problems or sample exams.',
                'icon': 'clipboard'
            })
    
    # Time management
    if any(word in keyword_set for word in ['time', 'deadline', 'schedule', 'pace', 'rushed']):
        insights.append({
            'category': 'Time Management',
            'priority': 'high',
            'suggestion': 'Adjust pacing and deadlines. Consider extending assignment due dates or breaking large projects into milestones.',
            'icon': 'clock'
        })
    
    # Student engagement
    if any(word in keyword_set for word in ['engaging', 'interesting', 'boring', 'motivate', 'attention']):
        if emotion_dist and (emotion_dist.get('boredom', 0) > 2):
            insights.append({
                'category': 'Student Engagement',
                'priority': 'high',
                'suggestion': 'Increase student engagement through discussions, group work, or real-world applications.',
                'icon': 'users'
            })
        elif emotion_dist and emotion_dist.get('joy', 0) > 3:
            insights.append({
                'category': 'Student Engagement',
                'priority': 'low',
                'suggestion': 'Students are engaged! Continue current engagement strategies and share best practices.',
                'icon': 'users'
            })
    
    # Feedback and communication
    if any(word in keyword_set for word in ['feedback', 'communicate', 'response', 'question', 'help']):
        insights.append({
            'category': 'Communication',
            'priority': 'medium',
            'suggestion': 'Enhance communication channels. Provide more timely feedback and be more accessible during office hours.',
            'icon': 'message'
        })
    
    # Course organization
    if any(word in keyword_set for word in ['organize', 'structure', 'plan', 'syllabus', 'clear']):
        insights.append({
            'category': 'Course Organization',
            'priority': 'medium',
            'suggestion': 'Improve course structure and organization. Provide detailed syllabus and clear learning objectives.',
            'icon': 'folder'
        })
    
    # If no specific insights, provide general one
    if not insights:
        insights.append({
            'category': 'General',
            'priority': 'low',
            'suggestion': 'Continue monitoring student feedback and maintain current teaching practices.',
            'icon': 'info'
        })
    
    return insights


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_topic_modeling_data(request):
    """Get topic modeling data from CSV results with LDA-generated insights"""
    import pandas as pd
    import json
    from pathlib import Path
    
    user = request.user
    
    if user.role not in ['faculty', 'admin']:
        return Response(
            {'error': 'Only faculty and admin can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Load topic modeling results
        base_path = Path(__file__).parent.parent / 'results' / 'topic_modeling'
        topics_file = base_path / 'topics_keywords.csv'
        feedback_file = base_path / 'feedback_with_topics.csv'
        insights_file = base_path / 'lda_insights.json'
        
        if not topics_file.exists():
            return Response({
                'error': 'Topic modeling data not found. Please run topic modeling first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Load topics and keywords
        topics_df = pd.read_csv(topics_file)
        topics_data = []
        for _, row in topics_df.iterrows():
            keywords = row['Keywords'].split(', ')[:10]  # Top 10 keywords
            topics_data.append({
                'topic': row['Topic'],
                'keywords': keywords
            })
        
        # Load feedback with topics if available
        topic_distribution = {}
        topic_emotion_dist = {}
        topic_insights = []
        
        if feedback_file.exists():
            feedback_df = pd.read_csv(feedback_file)
            
            # Topic distribution
            topic_counts = feedback_df['dominant_topic'].value_counts().to_dict()
            topic_distribution = {f'Topic {k+1}': v for k, v in topic_counts.items()}
            
            # Topic-emotion distribution (if emotion labels exist)
            if 'label' in feedback_df.columns:
                topic_emotion = feedback_df.groupby(['dominant_topic', 'label']).size().unstack(fill_value=0)
                topic_emotion_dist = topic_emotion.to_dict('index')
                topic_emotion_dist = {f'Topic {k+1}': v for k, v in topic_emotion_dist.items()}
        
        # Load LDA-generated insights if available
        if insights_file.exists():
            with open(insights_file, 'r') as f:
                lda_insights_data = json.load(f)
                topic_insights = lda_insights_data.get('topics', [])
        else:
            # Fallback: Generate basic insights using rule-based system
            logger.warning("LDA insights not found, using fallback rule-based generation")
            for idx, topic_data in enumerate(topics_data):
                emotion_dist = topic_emotion_dist.get(f'Topic {idx+1}', {})
                insights = generate_topic_insights(topic_data['keywords'], emotion_dist)
                topic_insights.append({
                    'topic': topic_data['topic'],
                    'insights': insights
                })
        
        return Response({
            'topics': topics_data,
            'topic_distribution': topic_distribution,
            'topic_emotion_distribution': topic_emotion_dist,
            'topic_insights': topic_insights,
            'total_topics': len(topics_data),
            'insights_method': 'LDA-based' if insights_file.exists() else 'rule-based'
        })
        
    except Exception as e:
        logger.error(f"Error loading topic modeling data: {str(e)}")
        return Response({
            'error': f'Failed to load topic modeling data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_topic_modeling(request):
    """
    Manually trigger topic modeling and insight generation
    Only accessible by admin users
    """
    user = request.user
    
    if user.role != 'admin':
        return Response(
            {'error': 'Only admin can trigger topic modeling'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from pathlib import Path
        import subprocess
        import sys
        from threading import Thread
        
        # Check feedback count
        feedback_count = Feedback.objects.filter(status='submitted').count()
        
        if feedback_count < 10:
            return Response({
                'error': f'Need at least 10 feedbacks for topic modeling. Currently have {feedback_count}.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        def run_topic_modeling_background():
            try:
                python_exe = sys.executable
                script_path = Path(__file__).parent.parent / 'run_topic_modeling_task.py'
                result = subprocess.run(
                    [python_exe, str(script_path)],
                    cwd=Path(__file__).parent.parent,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode == 0:
                    logger.info("✅ Topic modeling completed successfully")
                else:
                    logger.error(f"Topic modeling failed: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error running topic modeling: {str(e)}")
        
        # Start in background thread
        Thread(target=run_topic_modeling_background, daemon=True).start()
        
        return Response({
            'success': True,
            'message': f'Topic modeling started in background for {feedback_count} feedbacks',
            'feedback_count': feedback_count,
            'status': 'processing'
        })
        
    except Exception as e:
        logger.error(f"Error triggering topic modeling: {str(e)}")
        return Response({
            'error': f'Failed to trigger topic modeling: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_years(request):
    """
    Get list of academic years from submitted feedback
    Returns current year and upcoming year, plus any years with existing feedback
    """
    user = request.user
    
    if user.role not in ['faculty', 'admin']:
        return Response(
            {'error': 'Only faculty and admin can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Get distinct academic years from course assignments with feedback
        from django.db.models import Q
        
        feedback_years = Feedback.objects.filter(
            status='submitted'
        ).values_list(
            'course_assignment__academic_year', flat=True
        ).distinct().order_by('-course_assignment__academic_year')
        
        # Get unique years
        years_set = set(filter(None, feedback_years))
        
        # Add current and next academic year
        from datetime import datetime
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Determine current academic year (July-June cycle)
        if current_month >= 7:  # July onwards = start of new academic year
            current_academic_year = f"{current_year}-{current_year + 1}"
            next_academic_year = f"{current_year + 1}-{current_year + 2}"
        else:  # January-June = end of academic year
            current_academic_year = f"{current_year - 1}-{current_year}"
            next_academic_year = f"{current_year}-{current_year + 1}"
        
        years_set.add(current_academic_year)
        years_set.add(next_academic_year)
        
        # Sort years in descending order
        sorted_years = sorted(list(years_set), reverse=True)
        
        return Response({
            'years': sorted_years,
            'current_year': current_academic_year
        })
        
    except Exception as e:
        logger.error(f"Error fetching available years: {str(e)}")
        # Fallback to current and next year
        current_year = datetime.now().year
        return Response({
            'years': [f"{current_year}-{current_year + 1}", f"{current_year + 1}-{current_year + 2}"],
            'current_year': f"{current_year}-{current_year + 1}"
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_feedback_pdf(request):
    """Export feedback report as PDF"""
    from .reports.pdf_generator import generate_feedback_report_pdf
    
    user = request.user
    
    if user.role not in ['faculty', 'admin']:
        return Response(
            {'error': 'Only faculty and admin can export reports'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get filter parameters
    semester = request.GET.get('semester')
    academic_year = request.GET.get('academic_year')
    instructor_id = request.GET.get('instructor_id')
    course_id = request.GET.get('course_id')
    department = request.GET.get('department')
    
    # Base queryset
    feedback_qs = Feedback.objects.filter(status='submitted')
    
    # Apply department filter for dean (overrides RBAC)
    if department and user.role == 'admin' and user.admin_subrole == 'dean':
        if department == 'CS':
            feedback_qs = feedback_qs.filter(course_assignment__course__code__startswith='CS')
        elif department == 'IT':
            feedback_qs = feedback_qs.filter(
                Q(course_assignment__course__code__startswith='IT') |
                Q(course_assignment__course__code__startswith='ICT') |
                Q(course_assignment__course__code__startswith='ACT')
            )
    # RBAC: Department head restrictions (only if no department filter)
    elif user.role == 'admin' and user.admin_subrole:
        if user.admin_subrole == 'dept_head_cs':
            feedback_qs = feedback_qs.filter(course_assignment__course__code__startswith='CS')
        elif user.admin_subrole == 'dept_head_it':
            feedback_qs = feedback_qs.filter(
                Q(course_assignment__course__code__startswith='IT') |
                Q(course_assignment__course__code__startswith='ICT') |
                Q(course_assignment__course__code__startswith='ACT')
            )
    
    # Apply filters
    if semester:
        feedback_qs = feedback_qs.filter(feedback_session__semester=semester)
    if academic_year:
        feedback_qs = feedback_qs.filter(feedback_session__academic_year=academic_year)
    if instructor_id:
        feedback_qs = feedback_qs.filter(course_assignment__instructor_id=instructor_id)
    elif user.role == 'faculty':
        feedback_qs = feedback_qs.filter(course_assignment__instructor=user)
    if course_id:
        feedback_qs = feedback_qs.filter(course_assignment_id=course_id)
    
    # Prepare filter info for report
    filters = {
        'semester': semester,
        'academic_year': academic_year,
    }
    
    if instructor_id:
        try:
            instructor = User.objects.get(id=instructor_id)
            filters['instructor_name'] = instructor.get_display_name()
        except User.DoesNotExist:
            filters['instructor_name'] = 'Unknown'
    
    # Generate PDF
    try:
        pdf_buffer = generate_feedback_report_pdf(feedback_qs, filters, user)
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        
        # Generate filename with professor name if filtered
        if filters.get('instructor_name'):
            # Replace spaces with underscores and remove special characters
            prof_name = filters['instructor_name'].replace(' ', '_').replace(',', '')
            filename = f"feedback-report-{prof_name}-{datetime.now().strftime('%Y%m%d')}.pdf"
        else:
            filename = f"feedback-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Failed to generate PDF report: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_courses_list(request):
    """Get list of courses filtered by department and/or instructor (for cascading dropdowns)"""
    user = request.user
    
    if user.role not in ['faculty', 'admin']:
        return Response(
            {'error': 'Only faculty and admin can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get filter parameters
    department = request.GET.get('department')
    instructor_id = request.GET.get('instructor_id')
    
    # Base queryset - get courses that have assignments
    courses_qs = Course.objects.filter(
        assignments__is_active=True
    ).distinct()
    
    # RBAC: Department head restrictions
    if user.role == 'admin' and user.admin_subrole:
        if user.admin_subrole == 'dept_head_cs':
            courses_qs = courses_qs.filter(department='CS')
        elif user.admin_subrole == 'dept_head_it':
            courses_qs = courses_qs.filter(department__in=['IT', 'ACT'])
        # dean has no restrictions
    
    # Apply filters
    if department and department != 'all':
        courses_qs = courses_qs.filter(department=department)
    
    if instructor_id and instructor_id != 'all':
        courses_qs = courses_qs.filter(assignments__instructor_id=instructor_id)
    elif user.role == 'faculty':
        # Faculty can only see their own courses
        courses_qs = courses_qs.filter(assignments__instructor=user)
    
    # Order by department, year level, and code
    courses_qs = courses_qs.order_by('department', 'year_level', 'code')
    
    # Serialize courses
    courses_data = []
    for course in courses_qs:
        courses_data.append({
            'id': course.id,
            'code': course.code,
            'name': course.name,
            'department': course.department,
            'year_level': course.year_level,
        })
    
    return Response({
        'success': True,
        'courses': courses_data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_response_stats(request):
    """
    Get feedback response statistics including respondents and non-respondents
    """
    from django.db.models import Count, Q
    from collections import defaultdict
    
    user = request.user
    semester = request.GET.get('semester')
    academic_year = request.GET.get('academic_year')
    instructor_id = request.GET.get('instructor_id')
    course_id = request.GET.get('course_id')
    department = request.GET.get('department')
    
    # Base queryset for enrollments
    enrollments_qs = Enrollment.objects.select_related(
        'student', 'assignment', 'assignment__course', 'assignment__instructor'
    ).filter(assignment__is_active=True)
    
    # Apply filters
    if semester and semester != 'all':
        enrollments_qs = enrollments_qs.filter(assignment__semester=semester)
    if academic_year and academic_year != 'all':
        enrollments_qs = enrollments_qs.filter(assignment__academic_year=academic_year)
    if instructor_id and instructor_id != 'all':
        enrollments_qs = enrollments_qs.filter(assignment__instructor_id=instructor_id)
    if course_id and course_id != 'all':
        enrollments_qs = enrollments_qs.filter(assignment__course_id=course_id)
    if department and department != 'all':
        enrollments_qs = enrollments_qs.filter(assignment__department=department)
    
    # RBAC: Apply role-based restrictions
    if user.role == 'faculty':
        enrollments_qs = enrollments_qs.filter(assignment__instructor=user)
    elif user.role == 'admin' and user.admin_subrole:
        if user.admin_subrole == 'dept_head_cs':
            enrollments_qs = enrollments_qs.filter(assignment__department='CS')
        elif user.admin_subrole == 'dept_head_it':
            enrollments_qs = enrollments_qs.filter(assignment__department__in=['IT', 'ACT'])
    
    # Get total students (enrolled)
    total_students = enrollments_qs.count()
    
    # Get respondents - students who submitted feedback
    respondents = []
    respondent_ids = set()
    
    for enrollment in enrollments_qs:
        # Check if there's feedback for this enrollment's course assignment and student
        feedback = Feedback.objects.filter(
            student=enrollment.student,
            course_assignment=enrollment.course_assignment,
            status='submitted'
        ).first()
        
        if feedback:
            respondent_ids.add(enrollment.student.id)
            respondents.append({
                'id': enrollment.student.id,
                'name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
                'email': enrollment.student.email,
                'student_id': enrollment.student.student_id,
                'course': f"{enrollment.course_assignment.course.code} - {enrollment.course_assignment.course.name}",
                'section': enrollment.course_assignment.section,
                'submitted_at': feedback.submitted_at.isoformat() if feedback.submitted_at else feedback.created_at.isoformat()
            })
    
    # Get non-respondents
    non_respondents = []
    for enrollment in enrollments_qs:
        if enrollment.student.id not in respondent_ids:
            non_respondents.append({
                'id': enrollment.student.id,
                'name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
                'email': enrollment.student.email,
                'student_id': enrollment.student.student_id,
                'course': f"{enrollment.course_assignment.course.code} - {enrollment.course_assignment.course.name}",
                'section': enrollment.course_assignment.section
            })
    
    # Calculate response rate
    total_responses = len(respondents)
    response_rate = (total_responses / total_students * 100) if total_students > 0 else 0
    
    # Get submissions over time (last 30 days)
    from datetime import datetime, timedelta
    from django.db.models.functions import TruncDate
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Get student and course_assignment IDs from enrollments
    student_ids = enrollments_qs.values_list('student_id', flat=True)
    assignment_ids = enrollments_qs.values_list('course_assignment_id', flat=True)
    
    # Filter feedback by students and course assignments in scope
    submissions_by_date = Feedback.objects.filter(
        status='submitted',
        created_at__gte=thirty_days_ago,
        student__in=student_ids,
        course_assignment__in=assignment_ids
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    submissions_over_time = [
        {
            'date': item['date'].isoformat() if item['date'] else str(item['date']),
            'count': item['count']
        }
        for item in submissions_by_date
    ]
    
    return Response({
        'total_students': total_students,
        'total_responses': total_responses,
        'response_rate': response_rate,
        'respondents': respondents,
        'non_respondents': non_respondents,
        'submissions_over_time': submissions_over_time
    }, status=status.HTTP_200_OK)
