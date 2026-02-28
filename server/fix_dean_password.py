import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from authentication.models import User

# Fix the dean password
dean = User.objects.get(email='ccsdean@wmsu.edu.ph')
dean.set_password('Dean2024!')
dean.admin_subrole = 'dean'  # Also set the subrole
dean.save()

print(f"✅ Dean password updated successfully!")
print(f"   Email: {dean.email}")
print(f"   Role: {dean.role}")
print(f"   Subrole: {dean.admin_subrole}")
print(f"   Password: Dean2024!")
print(f"\nYou can now login with:")
print(f"   Email: ccsdean@wmsu.edu.ph")
print(f"   Password: Dean2024!")
