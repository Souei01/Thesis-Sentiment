from django.core.management.base import BaseCommand
from authentication.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Seeds the database with admin users: CS Dept Head, IT Dept Head, and Dean'

    def handle(self, *args, **options):
        admin_users = [
            {
                'email': 'cs.head@wmsu.edu.ph',
                'username': 'cs_dept_head',
                'role': 'admin',
                'admin_subrole': 'dept_head_cs',
                'department': 'Computer Science',
                'password': 'CSHead2024!',
            },
            {
                'email': 'it.head@wmsu.edu.ph',
                'username': 'it_dept_head',
                'role': 'admin',
                'admin_subrole': 'dept_head_it',
                'department': 'Information Technology',
                'password': 'ITHead2024!',
            },
            {
                'email': 'dean@wmsu.edu.ph',
                'username': 'college_dean',
                'role': 'admin',
                'admin_subrole': 'dean',
                'department': 'College of Computing Studies',
                'password': 'Dean2024!',
            },
        ]

        created_count = 0
        skipped_count = 0

        for user_data in admin_users:
            password = user_data.pop('password')
            email = user_data['email']
            
            try:
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User {email} already exists - skipping')
                    )
                    skipped_count += 1
                    continue
                
                # Create the user
                user = User.objects.create(**user_data)
                user.set_password(password)
                user.is_staff = True  # Allow access to Django admin
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created {user.get_admin_subrole_display()}: {email}')
                )
                created_count += 1
                
            except IntegrityError as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creating {email}: {str(e)}')
                )
                skipped_count += 1

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Summary: {created_count} created, {skipped_count} skipped'))
        
        if created_count > 0:
            self.stdout.write('\nDefault passwords:')
            self.stdout.write('  CS Dept Head: CSHead2024!')
            self.stdout.write('  IT Dept Head: ITHead2024!')
            self.stdout.write('  Dean: Dean2024!')
            self.stdout.write(self.style.WARNING('\n⚠ Remember to change these passwords in production!'))
