"""
Reset password for student 202200001@wmsu.edu.ph
"""

import os
import django

# Set environment variables for MariaDB
os.environ['DB_ENGINE'] = 'mysql'
os.environ['DB_NAME'] = 'sentiment_db'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = ''
os.environ['DB_HOST'] = '127.0.0.1'
os.environ['DB_PORT'] = '3306'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

print("=" * 80)
print("Resetting Password for: 202200001@wmsu.edu.ph")
print("=" * 80)

email = "202200001@wmsu.edu.ph"
new_password = "Student@123"

try:
    user = User.objects.get(email=email)
    user.password = make_password(new_password)
    user.save()
    
    print(f"\n✅ Password reset successful!")
    print(f"\nLogin credentials:")
    print(f"   Email: {email}")
    print(f"   Password: {new_password}")
    print(f"\n   Username: {user.username}")
    print(f"   Role: {user.role}")
    print(f"   Student ID: {user.student_id}")
    
except User.DoesNotExist:
    print(f"\n❌ User not found!")

print("=" * 80)
