"""
Fix student sections to match course assignment format (A, B, C instead of 1A, 2B, etc.)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from authentication.models import User

print("="*80)
print("FIXING STUDENT SECTIONS")
print("="*80)

students = User.objects.filter(role='student')
print(f"\nFound {students.count()} students")

updated = 0
for student in students:
    if student.section and len(student.section) > 1 and student.section[0].isdigit():
        old_section = student.section
        # Remove year prefix (e.g., '1A' -> 'A', '2B' -> 'B')
        new_section = student.section[1:]
        student.section = new_section
        student.save()
        updated += 1
        if updated <= 5:  # Show first 5 examples
            print(f"  {student.email}: {old_section} → {new_section}")

print(f"\n✅ Updated {updated} student sections")
print("="*80)
