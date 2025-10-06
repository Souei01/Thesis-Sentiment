from django.core.management.base import BaseCommand
from authentication.models import User

class Command(BaseCommand):
    help = 'Seeds the database with initial users'

    def handle(self, *args, **kwargs):
        users_data = [
            {
                'email': 'admin@wmsu.edu.ph',
                'username': 'admin',
                'password': 'Admin@123',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'email': 'faculty@wmsu.edu.ph',
                'username': 'faculty_user',
                'password': 'Faculty@123',
                'role': 'faculty',
                'department': 'Computer Science',
            },
            {
                'email': 'eh202201090@wmsu.edu.ph',
                'username': 'student_user',
                'password': 'Student@123',
                'role': 'student',
                'student_id': 'EH-2022-01090',
                'department': 'Computer Science',
            },
        ]

        for user_data in users_data:
            email = user_data['email']
            
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f'User {email} already exists'))
                continue
            
            password = user_data.pop('password')
            user = User.objects.create(**user_data)
            user.set_password(password)
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created user: {email}'))

        self.stdout.write(self.style.SUCCESS('User seeding completed!'))
