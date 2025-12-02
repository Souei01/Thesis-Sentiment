from django.core.management.base import BaseCommand
from authentication.models import User
from api.models import Enrollment, CourseAssignment, FeedbackSession, Feedback


class Command(BaseCommand):
    help = 'Removes old test data (named email students and old faculty)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🧹 Cleaning up old test data...\n'))
        
        # List of old test student emails to remove
        old_test_students = [
            'juan.delacruz@wmsu.edu.ph',
            'maria.santos@wmsu.edu.ph',
            'pedro.garcia@wmsu.edu.ph',
            'ana.reyes@wmsu.edu.ph',
            'jose.santos@wmsu.edu.ph',
            'carlos.mendoza@wmsu.edu.ph',
            'rosa.lopez@wmsu.edu.ph',
            'irregular.student@wmsu.edu.ph',
        ]
        
        # List of old test faculty emails to remove
        old_test_faculty = [
            'prof.juan.santos@wmsu.edu.ph',
            'prof.maria.reyes@wmsu.edu.ph',
            'prof.pedro.cruz@wmsu.edu.ph',
        ]
        
        # Remove old test students
        students_deleted = 0
        for email in old_test_students:
            try:
                user = User.objects.get(email=email)
                user.delete()
                students_deleted += 1
                self.stdout.write(f'  ✓ Removed student: {email}')
            except User.DoesNotExist:
                pass
        
        # Remove old test faculty
        faculty_deleted = 0
        for email in old_test_faculty:
            try:
                user = User.objects.get(email=email)
                user.delete()
                faculty_deleted += 1
                self.stdout.write(f'  ✓ Removed faculty: {email}')
            except User.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Cleanup complete!'))
        self.stdout.write(f'  • Removed {students_deleted} old test students')
        self.stdout.write(f'  • Removed {faculty_deleted} old test faculty')
        
        # Show current counts
        self.stdout.write('\n📊 Current Database:')
        self.stdout.write(f'  • Total Students: {User.objects.filter(role="student").count()}')
        self.stdout.write(f'  • Total Faculty: {User.objects.filter(role="faculty").count()}')
        self.stdout.write(f'  • Total Enrollments: {Enrollment.objects.count()}')
