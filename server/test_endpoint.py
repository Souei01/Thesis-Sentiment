"""
Test the response stats endpoint directly
Run in Render shell: python test_endpoint.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import Enrollment, Feedback, CourseAssignment
from authentication.models import User
import traceback

print("=== Testing Response Stats Logic ===\n")

# Get a faculty user
faculty = User.objects.filter(role='faculty').first()
if not faculty:
    print("ERROR: No faculty found")
    exit(1)

print(f"Testing as: {faculty.email} ({faculty.role})\n")

try:
    # Get faculty's assignments
    assignments = CourseAssignment.objects.filter(instructor=faculty, is_active=True)
    print(f"Faculty has {assignments.count()} active assignments")
    
    if assignments.count() == 0:
        print("No active assignments - this is why response stats is empty")
        exit(0)
    
    # Get enrollments
    enrollments_qs = Enrollment.objects.select_related(
        'student', 'course_assignment', 'course_assignment__course', 'course_assignment__instructor'
    ).filter(course_assignment__in=assignments)
    
    print(f"Total enrollments: {enrollments_qs.count()}")
    
    if enrollments_qs.count() == 0:
        print("No enrollments found")
        exit(0)
    
    # Get enrollment pairs
    enrollment_list = list(enrollments_qs.values_list('student_id', 'course_assignment_id'))
    print(f"Enrollment pairs: {len(enrollment_list)}\n")
    
    # Test the feedback query
    print("Testing feedback query...")
    from django.db import models as django_models
    
    feedback_queries = [
        django_models.Q(student_id=student_id, course_assignment_id=assignment_id)
        for student_id, assignment_id in enrollment_list
    ]
    
    if feedback_queries:
        feedback_qs = Feedback.objects.filter(
            django_models.Q(*feedback_queries, _connector=django_models.Q.OR),
            status='submitted'
        ).select_related('student', 'course_assignment__course')
        
        print(f"✓ Feedback query successful: {feedback_qs.count()} responses found\n")
        
        # Build lookup dict
        feedbacks = {}
        for feedback in feedback_qs:
            key = (feedback.student_id, feedback.course_assignment_id)
            feedbacks[key] = feedback
        
        # Count respondents and non-respondents
        respondents = []
        non_respondents = []
        
        for enrollment in enrollments_qs[:10]:  # Test first 10
            key = (enrollment.student.id, enrollment.course_assignment.id)
            feedback = feedbacks.get(key)
            
            if feedback:
                respondents.append(enrollment.student.student_id)
            else:
                non_respondents.append(enrollment.student.student_id)
        
        print(f"Sample results (first 10 enrollments):")
        print(f"  Respondents: {len(respondents)} - {respondents}")
        print(f"  Non-respondents: {len(non_respondents)} - {non_respondents}")
        
    print("\n✓ All queries work correctly!")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    traceback.print_exc()

print("\n=== Test Complete ===")

