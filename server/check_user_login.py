import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from authentication.models import User

def check_user_login(email, password):
    """Check if a user exists and verify their password"""
    print(f"\n=== Checking login for: {email} ===\n")
    
    try:
        # Try to find the user (case-insensitive)
        user = User.objects.get(email__iexact=email)
        print(f"✅ User found:")
        print(f"   - Email: {user.email}")
        print(f"   - Username: {user.username}")
        print(f"   - Role: {user.role}")
        print(f"   - Admin Subrole: {user.admin_subrole}")
        print(f"   - Is Active: {user.is_active}")
        print(f"   - Has usable password: {user.has_usable_password()}")
        
        # Check password
        if user.check_password(password):
            print(f"\n✅ Password is correct!")
        else:
            print(f"\n❌ Password is INCORRECT!")
            print(f"\nDebugging password:")
            print(f"   - Stored password hash: {user.password[:50]}...")
            
        return user
        
    except User.DoesNotExist:
        print(f"❌ User with email '{email}' does NOT exist in database")
        print(f"\nSearching for similar emails...")
        
        # Search for similar emails
        similar_users = User.objects.filter(email__icontains='dean')
        if similar_users.exists():
            print(f"\nFound {similar_users.count()} user(s) with 'dean' in email:")
            for u in similar_users:
                print(f"   - {u.email} (Role: {u.role}, Subrole: {u.admin_subrole})")
        else:
            print("   No users found with 'dean' in email")
            
        # Show all admin users
        admin_users = User.objects.filter(role='admin')
        if admin_users.exists():
            print(f"\nAll admin users in database:")
            for u in admin_users:
                print(f"   - {u.email} (Subrole: {u.admin_subrole})")
        
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == '__main__':
    # Check the login from the error log
    email = 'ccsdean@wmsu.edu.ph'
    password = 'Dean2024!'
    
    check_user_login(email, password)
    
    # Also list all users to see what's in the database
    print("\n" + "="*60)
    print("ALL USERS IN DATABASE:")
    print("="*60)
    all_users = User.objects.all()
    for user in all_users:
        print(f"{user.email:40} | Role: {user.role:10} | Subrole: {user.admin_subrole or 'N/A'}")
