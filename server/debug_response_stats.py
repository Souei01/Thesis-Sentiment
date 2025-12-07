"""
Debug script for response stats endpoint
Run this in Render shell: python debug_response_stats.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import Enrollment, Feedback, User
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta

print("=== Response Stats Debug ===\n")

# Get a faculty user for testing
faculty = User.objects.filter(role='faculty').first()
if not faculty:
    print("ERROR: No faculty users found")
    exit(1)

print(f"Testing as faculty: {faculty.email}\n")

# Get their course assignments
from api.models import CourseAssignment
assignments = CourseAssignment.objects.filter(instructor=faculty)
print(f"Faculty has {assignments.count()} course assignments")

if assignments.count() == 0:
    print("ERROR: Faculty has no course assignments")
    exit(1)

# Get enrollments for their courses
enrollments_qs = Enrollment.objects.filter(
    course_assignment__in=assignments,
    status='enrolled'
).select_related('student', 'course_assignment__course')

print(f"Total enrollments: {enrollments_qs.count()}\n")

if enrollments_qs.count() == 0:
    print("ERROR: No enrollments found")
    exit(1)

# Test the respondents query
print("=== Testing Respondents Query ===")
respondents = []
respondent_ids = set()

for enrollment in enrollments_qs[:5]:  # Test first 5
    print(f"Checking enrollment: student={enrollment.student.email}, course={enrollment.course_assignment.course.name}")
    
    try:
        feedback = Feedback.objects.filter(
            student=enrollment.student,
            course_assignment=enrollment.course_assignment,
            status='submitted'
        ).first()
        
        if feedback:
            print(f"  ✓ Found feedback, created: {feedback.created_at}")
            respondent_ids.add(enrollment.student.id)
        else:
            print(f"  ✗ No feedback found")
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\nTotal respondents found: {len(respondent_ids)}")

# Test the submissions over time query
print("\n=== Testing Submissions Over Time Query ===")
thirty_days_ago = datetime.now() - timedelta(days=30)

student_ids = enrollments_qs.values_list('student_id', flat=True)
assignment_ids = enrollments_qs.values_list('course_assignment_id', flat=True)

print(f"Student IDs count: {len(list(student_ids))}")
print(f"Assignment IDs count: {len(list(assignment_ids))}")

try:
    submissions_by_date = Feedback.objects.filter(
        status='submitted',
        created_at__gte=thirty_days_ago,
        student__in=student_ids,
        course_assignment__in=assignment_ids
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    print(f"Submissions found: {submissions_by_date.count()}")
    for item in submissions_by_date[:10]:
        print(f"  Date: {item['date']}, Count: {item['count']}")
        
except Exception as e:
    print(f"ERROR in submissions query: {e}")

# Check feedback model structure
print("\n=== Feedback Model Fields ===")
feedback_sample = Feedback.objects.first()
if feedback_sample:
    print(f"Feedback fields: {[f.name for f in Feedback._meta.get_fields()]}")
    print(f"Student: {feedback_sample.student}")
    print(f"Course Assignment: {feedback_sample.course_assignment}")
else:
    print("No feedback records found")

# Check enrollment model structure
print("\n=== Enrollment Model Fields ===")
enrollment_sample = Enrollment.objects.first()
if enrollment_sample:
    print(f"Enrollment fields: {[f.name for f in Enrollment._meta.get_fields()]}")
    print(f"Student: {enrollment_sample.student}")
    print(f"Course Assignment: {enrollment_sample.course_assignment}")
else:
    print("No enrollment records found")

print("\n=== Debug Complete ===")
