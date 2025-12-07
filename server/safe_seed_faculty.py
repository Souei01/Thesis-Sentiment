"""
Safely seed faculty accounts without conflicts
Run in Render shell: python safe_seed_faculty.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from authentication.models import User

# Department configurations
departments = ['CS', 'IT', 'ICT']
faculty_per_dept = 10

print("Creating/Updating Faculty Accounts...")
print("=" * 50)

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
        
        # Always set/reset password
        user.set_password('Faculty@123')
        user.save()
        
        if created:
            faculty_created += 1
            print(f'✓ Created: {email}')
        else:
            faculty_updated += 1
            print(f'↻ Updated: {email}')

print("\n" + "=" * 50)
print(f"✅ Created: {faculty_created} new faculty")
print(f"↻ Updated: {faculty_updated} existing faculty")
print(f"📊 Total: {faculty_created + faculty_updated} faculty accounts ready")
print("\nAll faculty can login with password: Faculty@123")
