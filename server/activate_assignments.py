"""
Activate all course assignments
Run in Render shell: python activate_assignments.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import CourseAssignment

print("=== Activating Course Assignments ===\n")

# Get all assignments
total = CourseAssignment.objects.count()
inactive = CourseAssignment.objects.filter(is_active=False).count()
active = CourseAssignment.objects.filter(is_active=True).count()

print(f"Total assignments: {total}")
print(f"Active: {active}")
print(f"Inactive: {inactive}\n")

if inactive > 0:
    print(f"Activating {inactive} assignments...")
    updated = CourseAssignment.objects.filter(is_active=False).update(is_active=True)
    print(f"✓ Activated {updated} assignments\n")
else:
    print("All assignments are already active\n")

# Show breakdown by department
from django.db.models import Count
by_dept = CourseAssignment.objects.values('department').annotate(count=Count('id'))

print("Assignments by department:")
for dept in by_dept:
    print(f"  {dept['department']}: {dept['count']}")

print("\n=== Complete ===")
