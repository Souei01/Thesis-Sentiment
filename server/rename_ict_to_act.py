"""
Rename ICT department to ACT in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from authentication.models import User
from api.models import Course, CourseAssignment

print("="*80)
print("RENAMING ICT DEPARTMENT TO ACT")
print("="*80)

# Update users
users_updated = User.objects.filter(department='ICT').update(department='ACT')
print(f"\n✓ Updated {users_updated} users from ICT to ACT")

# Update courses
courses_updated = Course.objects.filter(department='ICT').update(department='ACT')
print(f"✓ Updated {courses_updated} courses from ICT to ACT")

# Update course assignments
assignments_updated = CourseAssignment.objects.filter(department='ICT').update(department='ACT')
print(f"✓ Updated {assignments_updated} course assignments from ICT to ACT")

print("\n" + "="*80)
print("✅ RENAMING COMPLETE!")
print("="*80)

# Show summary
print(f"\n📊 Final counts:")
print(f"  - CS users: {User.objects.filter(department='CS').count()}")
print(f"  - IT users: {User.objects.filter(department='IT').count()}")
print(f"  - ACT users: {User.objects.filter(department='ACT').count()}")
print(f"  - ICT users (should be 0): {User.objects.filter(department='ICT').count()}")
