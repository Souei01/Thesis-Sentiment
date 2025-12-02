import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import Course


class Command(BaseCommand):
    help = 'Loads courses from CSV file into the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Loading courses from CSV...\n'))
        
        # Path to CSV file
        csv_path = os.path.join(settings.BASE_DIR, 'data', 'annotations', 'Courses In Each program - Sheet1.csv')
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found at: {csv_path}'))
            return
        
        # Clear existing courses
        Course.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing courses\n'))
        
        courses_created = 0
        courses_skipped = 0
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                program = row['Course'].strip()
                year_level_str = row['Year Level'].strip()
                semester = row['Semester'].strip()
                subject_code = row['Subject Code'].strip()
                descriptive_title = row['Descriptive title'].strip()
                description = row['Description'].strip()
                
                # Skip rows without subject code (electives without codes)
                if not subject_code:
                    courses_skipped += 1
                    continue
                
                # Map program to department
                department = None
                if 'COMPUTER SCIENCE' in program:
                    department = 'CS'
                elif 'INFORMATION TECHNOLOGY' in program:
                    department = 'IT'
                elif 'ASSOCIATE IN COMPUTER TECHNOLOGY' in program:
                    department = 'ICT'
                else:
                    self.stdout.write(self.style.WARNING(f'Unknown program: {program}'))
                    courses_skipped += 1
                    continue
                
                # Parse year level
                year_level = None
                if 'First Year' in year_level_str:
                    year_level = 1
                elif 'Second Year' in year_level_str:
                    year_level = 2
                elif 'Third Year' in year_level_str:
                    year_level = 3
                elif 'Fourth Year' in year_level_str:
                    year_level = 4
                else:
                    self.stdout.write(self.style.WARNING(f'Unknown year level: {year_level_str}'))
                    courses_skipped += 1
                    continue
                
                # Map semester
                semester_mapped = None
                if 'First Semester' in semester:
                    semester_mapped = '1st'
                elif 'Second Semester' in semester:
                    semester_mapped = '2nd'
                elif 'Summer' in semester:
                    semester_mapped = 'Summer'
                else:
                    self.stdout.write(self.style.WARNING(f'Unknown semester: {semester}'))
                    courses_skipped += 1
                    continue
                
                # Create or update course
                course, created = Course.objects.get_or_create(
                    code=subject_code,
                    department=department,
                    year_level=year_level,
                    semester=semester_mapped,
                    defaults={
                        'name': descriptive_title,
                        'description': description,
                        'units': 3,  # Default units
                        'is_active': True
                    }
                )
                
                if created:
                    courses_created += 1
                    if courses_created % 10 == 0:
                        self.stdout.write(f'  ... {courses_created} courses created')
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✅ COURSES LOADED FROM CSV!'))
        self.stdout.write('='*70)
        
        # Summary
        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'  • Courses created: {courses_created}')
        self.stdout.write(f'  • Courses skipped (no code): {courses_skipped}')
        
        # Count by department
        cs_courses = Course.objects.filter(department='CS').count()
        it_courses = Course.objects.filter(department='IT').count()
        ict_courses = Course.objects.filter(department='ICT').count()
        
        self.stdout.write(f'\n  • CS Courses: {cs_courses}')
        self.stdout.write(f'  • IT Courses: {it_courses}')
        self.stdout.write(f'  • ICT Courses: {ict_courses}')
        
        # Count by year level
        self.stdout.write('\n  Courses by Year Level:')
        for year in range(1, 5):
            year_count = Course.objects.filter(year_level=year).count()
            self.stdout.write(f'    · Year {year}: {year_count} courses')
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.WARNING('\n⚠️  NOTE: You need to recreate course assignments for these new courses.'))
        self.stdout.write('Run: python manage.py seed_course_assignments\n')
