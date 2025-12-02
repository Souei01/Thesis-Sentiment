"""
Check if student account exists and reset password if needed
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

print("=" * 80)
print("Checking Student Account: 202200001@wmsu.edu.ph")
print("=" * 80)

email = "202200001@wmsu.edu.ph"

try:
    user = User.objects.get(email=email)
    print(f"\n✅ User found!")
    print(f"   Email: {user.email}")
    print(f"   Username: {user.username}")
    print(f"   Role: {user.role}")
    print(f"   Is Active: {user.is_active}")
    print(f"   Is Staff: {user.is_staff}")
    
    # Reset password
    new_password = "Student@123"
    user.password = make_password(new_password)
    user.save()
    
    print(f"\n✅ Password reset to: {new_password}")
    print(f"\nYou can now login with:")
    print(f"   Email: {email}")
    print(f"   Password: {new_password}")
    
except User.DoesNotExist:
    print(f"\n❌ User not found!")
    print(f"\nCreating student account...")
    
    # Create the student user
    user = User.objects.create(
        email=email,
        username="202200001",
        first_name="John",
        last_name="Student",
        role="student",
        student_id="202200001",
        password=make_password("Student@123")
    )
    
    print(f"✅ Student account created!")
    print(f"   Email: {user.email}")
    print(f"   Password: Student@123")

print("=" * 80)
