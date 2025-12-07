"""
Complete setup script for production
Run in Render shell: python complete_setup.py

This script:
1. Creates all faculty accounts
2. Seeds courses from CSV
3. Creates students (optional)
4. Enrolls students in courses
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.core.management import call_command
from authentication.models import User
from api.models import Course, CourseAssignment, Enrollment, FeedbackSession
from django.db import transaction

print("=" * 70)
print("COMPLETE PRODUCTION SETUP")
print("=" * 70)

# Step 1: Create Faculty
print("\n📚 STEP 1: Creating Faculty Accounts...")
print("-" * 70)

departments = ['CS', 'IT', 'ACT']
faculty_per_dept = 10
faculty_created = 0
faculty_updated = 0

for dept in departments:
    for i in range(1, faculty_per_dept + 1):
        email = f'faculty{dept}{i}@wmsu.edu.ph'
        username = f'faculty_{dept.lower()}_{i}'
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': f'{dept} Faculty',
                'last_name': f'{i}',
                'role': 'faculty',
                'department': dept,
                'is_staff': False,
                'is_superuser': False
            }
        )
        
        user.set_password('Faculty@123')
        user.save()
        
        if created:
            faculty_created += 1
        else:
            faculty_updated += 1

print(f"✅ Faculty: {faculty_created} created, {faculty_updated} updated")

# Step 2: Seed Courses
print("\n📖 STEP 2: Seeding Courses from CSV...")
print("-" * 70)

try:
    call_command('seed_courses_from_csv')
    print("✅ Courses seeded successfully")
except Exception as e:
    print(f"❌ Error seeding courses: {e}")

# Step 3: Check enrollment
print("\n📊 STEP 3: Checking Enrollments...")
print("-" * 70)

# Auto-enrollment happens in CourseAssignment post_save signal
total_enrollments = Enrollment.objects.count()
print(f"✅ Total enrollments: {total_enrollments}")

if total_enrollments == 0:
    print("⚠️  No enrollments found. Students may not be created yet.")
    print("   Run 'python manage.py seed_production_data' to create students.")

# Summary
print("\n" + "=" * 70)
print("✅ SETUP COMPLETE!")
print("=" * 70)
print(f"\n📊 Database State:")
print(f"  • Faculty: {User.objects.filter(role='faculty').count()}")
print(f"  • Students: {User.objects.filter(role='student').count()}")
print(f"  • Courses: {Course.objects.count()}")
print(f"  • Course Assignments: {CourseAssignment.objects.count()}")
print(f"  • Enrollments: {Enrollment.objects.count()}")
print(f"  • Feedback Sessions: {FeedbackSession.objects.filter(is_active=True).count()}")

print("\n🔐 Faculty Login:")
print("  Email: facultyCS1@wmsu.edu.ph (or any faculty)")
print("  Password: Faculty@123")

print("\n" + "=" * 70)
