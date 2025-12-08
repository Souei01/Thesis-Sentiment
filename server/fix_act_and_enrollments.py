"""
Fix ACT department and check enrollment issues
Run in Render shell: python fix_act_and_enrollments.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import CourseAssignment, Enrollment
from authentication.models import User

print("=== Checking Department Issues ===\n")

# 1. Check ICT vs ACT
ict_assignments = CourseAssignment.objects.filter(department='ICT').count()
act_assignments = CourseAssignment.objects.filter(department='ACT').count()

print(f"ICT assignments: {ict_assignments}")
print(f"ACT assignments: {act_assignments}\n")

if ict_assignments > 0:
    print(f"Renaming {ict_assignments} ICT assignments to ACT...")
    CourseAssignment.objects.filter(department='ICT').update(department='ACT')
    print("✓ Done\n")

# 2. Check ICT users
ict_users = User.objects.filter(department='ICT').count()
act_users = User.objects.filter(department='ACT').count()

print(f"ICT users: {ict_users}")
print(f"ACT users: {act_users}\n")

if ict_users > 0:
    print(f"Renaming {ict_users} ICT users to ACT...")
    User.objects.filter(department='ICT').update(department='ACT')
    print("✓ Done\n")

# 3. Check enrollments per department
print("=== Enrollment Counts by Department ===\n")
from django.db.models import Count

enrollment_counts = Enrollment.objects.values(
    'course_assignment__department'
).annotate(count=Count('id'))

for item in enrollment_counts:
    dept = item['course_assignment__department']
    count = item['count']
    print(f"{dept}: {count} enrollments")

# 4. Check active ACT assignments with students
print("\n=== Active ACT Assignments with Enrollments ===\n")
act_assignments_active = CourseAssignment.objects.filter(
    department='ACT',
    is_active=True
)

print(f"Active ACT assignments: {act_assignments_active.count()}")

for assignment in act_assignments_active[:5]:
    enrollment_count = Enrollment.objects.filter(course_assignment=assignment).count()
    print(f"  {assignment.course.code} Section {assignment.section}: {enrollment_count} students")

print("\n=== Complete ===")
