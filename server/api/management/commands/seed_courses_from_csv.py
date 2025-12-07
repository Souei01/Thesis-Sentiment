from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from authentication.models import User
from api.models import Course, CourseAssignment, FeedbackSession
import csv
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Seeds courses from CSV file with proper professor assignments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting course seeding from CSV...'))
        
        # Get CSV file path
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        csv_path = base_dir / 'data' / 'annotations' / 'Courses In Each program - Sheet1.csv'
        
        if not csv_path.exists():
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return
        
        # Clear existing courses and assignments
        self.stdout.write('Clearing existing courses and assignments...')
        CourseAssignment.objects.all().delete()
        Course.objects.filter(code__startswith=('CS', 'IT', 'CC', 'ICT')).delete()
        
        # Read CSV and create courses with semester info
        courses_created = 0
        courses_with_semester = {}  # Store courses with their semester info
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                code = row['Subject Code'].strip()
                name = row['Descriptive title'].strip()
                description = row['Description'].strip()
                year_level_str = row['Year Level'].strip()
                semester_str = row['Semester'].strip()
                program = row['Course'].strip()
                
                # Skip empty codes or electives without codes
                if not code or code == '':
                    continue
                
                # Determine department from program
                if 'COMPUTER SCIENCE' in program:
                    department = 'CS'
                elif 'INFORMATION TECHNOLOGY' in program:
                    department = 'IT'
                elif 'COMPUTER TECHNOLOGY' in program:
                    department = 'ICT'
                else:
                    continue
                
                # Parse year level
                if 'First' in year_level_str:
                    year_level = 1
                elif 'Second' in year_level_str:
                    year_level = 2
                elif 'Third' in year_level_str:
                    year_level = 3
                elif 'Fourth' in year_level_str:
                    year_level = 4
                else:
                    continue
                
                # Parse semester
                if '1st' in semester_str or 'First' in semester_str:
                    semester = '1st'
                elif '2nd' in semester_str or 'Second' in semester_str:
                    semester = '2nd'
                elif 'Summer' in semester_str:
                    semester = 'Summer'
                else:
                    semester = '1st'  # Default to 1st semester
                
                # Create course
                course, created = Course.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'description': description,
                        'department': department,
                        'year_level': year_level,
                        'units': 3
                    }
                )
                
                if created:
                    courses_created += 1
                    self.stdout.write(f'  ✓ {code}: {name} ({semester} Semester)')
                
                # Store course with semester info
                key = f'{department}_{year_level}_{semester}_{code}'
                courses_with_semester[key] = {'course': course, 'semester': semester}
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {courses_created} courses'))
        
        # Get faculty
        cs_faculty = list(User.objects.filter(role='faculty', department='CS'))
        it_faculty = list(User.objects.filter(role='faculty', department='IT'))
        ict_faculty = list(User.objects.filter(role='faculty', department='ICT'))
        
        faculty_map = {
            'CS': cs_faculty,
            'IT': it_faculty,
            'ICT': ict_faculty
        }
        
        # Create course assignments
        self.stdout.write(self.style.SUCCESS('\n📚 Creating Course Assignments...'))
        assignments_created = 0
        
        academic_year = "2024-2025"
        departments = ['CS', 'IT', 'ICT']
        sections = ['A', 'B', 'C']
        semesters = ['1st', '2nd', 'Summer']
        
        # Group courses by department, year level, and semester
        courses_by_dept_year_sem = {}
        for key, data in courses_with_semester.items():
            dept, year_str, sem, code = key.split('_', 3)
            year_level = int(year_str)
            group_key = f'{dept}_{year_level}_{sem}'
            
            if group_key not in courses_by_dept_year_sem:
                courses_by_dept_year_sem[group_key] = []
            courses_by_dept_year_sem[group_key].append(data)
        
        # Assign courses to sections
        for dept in departments:
            for year_level in [1, 2, 3, 4]:
                for semester in semesters:
                    group_key = f'{dept}_{year_level}_{semester}'
                    courses_list = courses_by_dept_year_sem.get(group_key, [])
                    
                    if not courses_list:
                        continue
                    
                    faculty_list = faculty_map.get(dept, [])
                    if not faculty_list:
                        self.stdout.write(self.style.WARNING(f'No faculty found for {dept}'))
                        continue
                    
                    for section_letter in sections:
                        section_name = f'{year_level}{section_letter}'
                        
                        # Assign one professor per section
                        section_idx = sections.index(section_letter)
                        professor = faculty_list[section_idx % len(faculty_list)]
                        
                        # Assign all courses to this section
                        for course_data in courses_list:
                            course = course_data['course']
                            assignment, created = CourseAssignment.objects.get_or_create(
                                course=course,
                                instructor=professor,
                                year_level=year_level,
                                section=section_name,
                                department=dept,
                                semester=semester,
                                academic_year=academic_year,
                                defaults={'is_active': True}
                            )
                            
                            if created:
                                assignments_created += 1
                                if assignments_created % 10 == 0:
                                    self.stdout.write(f'  ... {assignments_created} assignments created')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {assignments_created} course assignments'))
        
        # Create feedback sessions for all semesters
        self.stdout.write(self.style.SUCCESS('\n📝 Creating Feedback Sessions...'))
        for semester in semesters:
            session, created = FeedbackSession.objects.get_or_create(
                academic_year=academic_year,
                semester=semester,
                defaults={
                    'title': f'{semester} Semester {academic_year} Faculty Evaluation',
                    'start_date': timezone.now(),
                    'end_date': timezone.now() + timedelta(days=14),
                    'is_active': True if semester == '1st' else False,  # Only 1st semester active by default
                    'instructions': 'Please provide honest feedback about your courses and instructors.'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created feedback session for {semester} semester'))
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✅ COURSE SEEDING COMPLETE!'))
        self.stdout.write('='*70)
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  • Total Courses: {Course.objects.count()}')
        self.stdout.write(f'  • Total Course Assignments: {CourseAssignment.objects.count()}')
        self.stdout.write(f'  • Active Feedback Sessions: {FeedbackSession.objects.filter(is_active=True).count()}')
        self.stdout.write('\n' + '='*70)
