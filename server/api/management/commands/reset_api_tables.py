from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Drops and recreates API tables'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Dropping API tables...'))
        
        with connection.cursor() as cursor:
            tables = [
                'api_feedback',
                'api_feedbacksession',
                'api_enrollment',
                'api_courseassignment',
                'api_course',
            ]
            
            # Disable foreign key checks
            cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
            
            for table in tables:
                try:
                    cursor.execute(f'DROP TABLE IF EXISTS {table}')
                    self.stdout.write(f'  ✓ Dropped {table}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  ! Could not drop {table}: {e}'))
            
            # Re-enable foreign key checks
            cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Tables dropped successfully!'))
        self.stdout.write(self.style.WARNING('\nNow run:'))
        self.stdout.write('  python server\\manage.py makemigrations api')
        self.stdout.write('  python server\\manage.py migrate')
        self.stdout.write('  python server\\manage.py seed_course_assignments')
