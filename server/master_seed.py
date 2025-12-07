"""
Master seeder - runs all seeders in correct order without conflicts
Run in Render shell: python master_seed.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.core.management import call_command
from authentication.models import User
from api.models import Course, CourseAssignment, FeedbackSession
from django.db import transaction

print("=" * 70)
print("MASTER SEEDER - Complete Database Setup")
print("=" * 70)

# Step 1: Create Faculty Accounts
print("\n📚 STEP 1: Creating Faculty Accounts...")
print("-" * 70)

departments = ['CS', 'IT', 'ICT']
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

print(f"✅ Faculty Ready: {faculty_created} created, {faculty_updated} updated")

# Step 2: Seed Courses from CSV
print("\n📖 STEP 2: Seeding Courses from CSV...")
print("-" * 70)

try:
    # Clear old courses/assignments first
    CourseAssignment.objects.all().delete()
    Course.objects.filter(code__startswith=('CS', 'IT', 'CC', 'ICT')).delete()
    print("✓ Cleared old courses and assignments")
    
    # Run CSV seeder
    call_command('seed_courses_from_csv')
    print("✅ Courses seeded successfully")
    
except Exception as e:
    print(f"❌ Error seeding courses: {e}")

# Step 3: Summary
print("\n" + "=" * 70)
print("✅ MASTER SEEDING COMPLETE!")
print("=" * 70)
print(f"\n📊 Final Database State:")
print(f"  • Total Users: {User.objects.count()}")
print(f"  • Faculty: {User.objects.filter(role='faculty').count()}")
print(f"  • Students: {User.objects.filter(role='student').count()}")
print(f"  • Courses: {Course.objects.count()}")
print(f"  • Course Assignments: {CourseAssignment.objects.count()}")
print(f"  • Active Feedback Sessions: {FeedbackSession.objects.filter(is_active=True).count()}")

print("\n🔐 Login Credentials:")
print("  Faculty: facultyCS1@wmsu.edu.ph (or any faculty email)")
print("  Password: Faculty@123")

print("\n" + "=" * 70)
