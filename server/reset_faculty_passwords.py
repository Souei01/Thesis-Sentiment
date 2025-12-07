"""
Reset all faculty passwords to Faculty@123
Run this in Render shell: python reset_faculty_passwords.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from authentication.models import User

# Get all faculty users
faculty_users = User.objects.filter(role='faculty')

print(f"Found {faculty_users.count()} faculty users")
print("\nResetting passwords...")

reset_count = 0
for user in faculty_users:
    user.set_password('Faculty@123')
    user.save()
    print(f"✓ Reset password for: {user.email}")
    reset_count += 1

print(f"\n✅ Successfully reset {reset_count} faculty passwords")
print("All faculty can now login with password: Faculty@123")
