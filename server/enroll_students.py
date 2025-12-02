"""
Auto-enroll students in courses based on course assignments
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import CourseAssignment

print("="*80)
print("AUTO-ENROLLING STUDENTS")
print("="*80)

assignments = CourseAssignment.objects.all()
print(f"\nFound {assignments.count()} course assignments")

count = 0
for assignment in assignments:
    print(f"\nProcessing: {assignment.course.code} Section {assignment.section}")
    assignment.auto_enroll_students()
    count += 1
    if count % 20 == 0:
        print(f"  ... processed {count}/{assignments.count()}")

print("\n" + "="*80)
print(f"✅ COMPLETED: Processed {count} course assignments")
print("="*80)

# Show summary
from api.models import Enrollment
total_enrollments = Enrollment.objects.count()
print(f"\nTotal enrollments created: {total_enrollments}")
