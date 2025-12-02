from django.core.management.base import BaseCommand
from authentication.models import User


class Command(BaseCommand):
    help = 'Lists all student emails'

    def handle(self, *args, **options):
        students = User.objects.filter(role='student').order_by('department', 'year_level', 'section', 'email')
        
        self.stdout.write(self.style.SUCCESS(f'\n📧 Total Students: {students.count()}\n'))
        self.stdout.write('='*80)
        
        current_dept = None
        current_year = None
        
        for student in students:
            # Print department header
            if student.department != current_dept:
                current_dept = student.department
                self.stdout.write(self.style.WARNING(f'\n{student.department} DEPARTMENT:'))
                current_year = None
            
            # Print year level header
            if student.year_level != current_year:
                current_year = student.year_level
                self.stdout.write(self.style.SUCCESS(f'\n  Year {student.year_level}:'))
            
            # Print student email
            self.stdout.write(f'    {student.email} (Section {student.section})')
        
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('\n✓ All student emails listed above'))
        self.stdout.write(self.style.WARNING('Password for all students: Student@123\n'))
