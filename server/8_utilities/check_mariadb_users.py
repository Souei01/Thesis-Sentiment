"""
Check MariaDB database for existing users
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

User = get_user_model()

print("=" * 80)
print("Checking All Users in MariaDB Database")
print("=" * 80)

# Get all users
users = User.objects.all()

print(f"\n📊 Total Users: {users.count()}\n")

if users.count() == 0:
    print("❌ No users found in database!")
else:
    print("Users List:")
    print("-" * 80)
    for user in users:
        print(f"\n👤 {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Student ID: {user.student_id if hasattr(user, 'student_id') else 'N/A'}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Has Password: {'Yes' if user.password else 'No'}")
        print(f"   Password Hash: {user.password[:50]}..." if user.password else "")

print("\n" + "=" * 80)

# Specifically check for the student account
print("\nSearching for: 202200001@wmsu.edu.ph")
print("-" * 80)

student = User.objects.filter(email='202200001@wmsu.edu.ph').first()
if student:
    print(f"✅ Found!")
    print(f"   Username: {student.username}")
    print(f"   Email: {student.email}")
    print(f"   Role: {student.role}")
    print(f"   Password hash: {student.password}")
else:
    print("❌ Not found!")

print("=" * 80)
