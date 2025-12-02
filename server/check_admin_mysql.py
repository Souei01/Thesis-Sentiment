import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin user exists
user = User.objects.filter(email='ccsdean@wmsu.edu.ph').first()

if user:
    print(f"✓ User found: {user.email}")
    print(f"  - Username: {user.username}")
    print(f"  - Is staff: {user.is_staff}")
    print(f"  - Is active: {user.is_active}")
    print(f"  - Password check (admin123): {user.check_password('admin123')}")
else:
    print("✗ User NOT found in database!")
    print("\nCreating admin user...")
    user = User.objects.create_user(
        username='ccsdean',
        email='ccsdean@wmsu.edu.ph',
        password='admin123',
        first_name='Dean',
        last_name='CCS',
        is_staff=True,
        is_superuser=True
    )
    print(f"✓ Admin user created: {user.email}")
