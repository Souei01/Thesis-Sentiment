from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from authentication.models import User
from api.models import Course, CourseAssignment, FeedbackSession
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Seeds database with production-like data (students, faculty, courses with specific format)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting production data seeding...'))
        
        # Department configurations
        departments = ['CS', 'IT', 'ICT']
        year_levels = [1, 2, 3, 4]
        sections_per_year = ['A', 'B', 'C']  # 3 sections per year level
        students_per_section = 10  # 10 students per section = 30 per year level
        faculty_per_dept = 10
        
        # ============================================
        # CREATE FACULTY (10 per department)
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n📚 Creating Faculty...'))
        faculty_created = 0
        faculty_users = {}
        
        for dept in departments:
            for i in range(1, faculty_per_dept + 1):
                email = f'faculty{dept}{i}@wmsu.edu.ph'
                username = f'faculty_{dept.lower()}_{i}'
                
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': username,
                        'first_name': f'{dept} Faculty',
                        'last_name': f'{i}',
                        'role': 'faculty',
                        'department': dept,
                        'is_staff': True
                    }
                )
                if created:
                    user.set_password('Faculty@123')
                    user.save()
                    faculty_created += 1
                    self.stdout.write(f'  ✓ {email}')
                
                faculty_users[f'{dept}_{i}'] = user
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {faculty_created} faculty members'))
        
        # ============================================
        # CREATE STUDENTS (30 per year level per department)
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n👨‍🎓 Creating Students...'))
        students_created = 0
        student_counter = {}
        
        for dept in departments:
            for year_level in year_levels:
                for section in sections_per_year:
                    for student_num in range(1, students_per_section + 1):
                        # Generate student ID: 2022XXXXX format
                        # Year code based on year level (Year 1 = 2024, Year 2 = 2023, etc.)
                        year_code = 2025 - year_level
                        
                        # Generate unique 5-digit number
                        if dept not in student_counter:
                            student_counter[dept] = {}
                        if year_level not in student_counter[dept]:
                            student_counter[dept][year_level] = 1
                        
                        counter = student_counter[dept][year_level]
                        student_counter[dept][year_level] += 1
                        
                        # Format: YYYYXXXXX (e.g., 202201001)
                        student_id_num = f'{year_code}{counter:05d}'
                        email = f'{student_id_num}@wmsu.edu.ph'
                        username = f'student_{student_id_num}'
                        
                        user, created = User.objects.get_or_create(
                            email=email,
                            defaults={
                                'username': username,
                                'student_id': student_id_num,
                                'first_name': f'{dept} Student',
                                'last_name': f'{student_id_num}',
                                'role': 'student',
                                'department': dept,
                                'year_level': year_level,
                                'section': f'{year_level}{section}'
                            }
                        )
                        if created:
                            user.set_password('Student@123')
                            user.save()
                            students_created += 1
                            if students_created % 30 == 0:  # Progress update every 30 students
                                self.stdout.write(f'  ... {students_created} students created')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {students_created} students'))
        
        # ============================================
        # CREATE COURSES
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n📖 Creating Courses...'))
        courses_data = [
            # CS Third Year - First Semester
            {'code': 'CS131', 'name': 'Automata Theory and Formal Languages', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS133', 'name': 'Information Assurance and Security', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS135', 'name': 'Advanced Database Systems', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS137', 'name': 'Software Engineering 1', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS139', 'name': 'Web Programming and Development', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS140', 'name': 'CS Elective 2', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CC105', 'name': 'Applications Development and Emerging Technologies', 'department': 'CS', 'year_level': 3, 'units': 3},
            
            # CS Third Year - Second Semester
            {'code': 'CS130', 'name': 'Thesis 1', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS132', 'name': 'Software Engineering 2', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS134', 'name': 'Operating Systems', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS136', 'name': 'Modeling and Simulation', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS138', 'name': 'CS Elective 3', 'department': 'CS', 'year_level': 3, 'units': 3},
            
            # IT Third Year - First Semester (2023 Curriculum)
            {'code': 'IT311', 'name': 'Networking 2', 'department': 'IT', 'year_level': 3, 'units': 3},
            {'code': 'IT312', 'name': 'Systems Integration and Architecture 1', 'department': 'IT', 'year_level': 3, 'units': 3},
            {'code': 'IT314', 'name': 'Data Analytics', 'department': 'IT', 'year_level': 3, 'units': 3},
            {'code': 'CC105IT', 'name': 'Applications Development and Emerging Technologies', 'department': 'IT', 'year_level': 3, 'units': 3},
            
            # IT Third Year - Second Semester (2023 Curriculum)
            {'code': 'IT321', 'name': 'Internet of Things', 'department': 'IT', 'year_level': 3, 'units': 3},
            {'code': 'IT322', 'name': 'Machine Learning', 'department': 'IT', 'year_level': 3, 'units': 3},
            {'code': 'IT323', 'name': 'Information Assurance and Security', 'department': 'IT', 'year_level': 3, 'units': 3},
            
            # ICT Third Year Courses (using similar IT course names)
            {'code': 'ICT311', 'name': 'Advanced Networking', 'department': 'ICT', 'year_level': 3, 'units': 3},
            {'code': 'ICT312', 'name': 'Systems Architecture', 'department': 'ICT', 'year_level': 3, 'units': 3},
            {'code': 'ICT313', 'name': 'Data Science', 'department': 'ICT', 'year_level': 3, 'units': 3},
            {'code': 'ICT321', 'name': 'IoT Applications', 'department': 'ICT', 'year_level': 3, 'units': 3},
            {'code': 'ICT322', 'name': 'AI and Machine Learning', 'department': 'ICT', 'year_level': 3, 'units': 3},
        ]
        
        courses = {}
        courses_created = 0
        for data in courses_data:
            course, created = Course.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'department': data['department'],
                    'year_level': data['year_level'],
                    'units': data['units']
                }
            )
            if created:
                courses_created += 1
            courses[course.code] = course
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {courses_created} courses'))
        
        # ============================================
        # CREATE COURSE ASSIGNMENTS (will auto-enroll students)
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n🎓 Creating Course Assignments (this will trigger auto-enrollment)...'))
        assignments_created = 0
        total_enrollments = 0
        
        academic_year = "2024-2025"
        semester = "1st"
        
        # Map courses to departments for assignment
        cs_courses = [c['code'] for c in courses_data if c['department'] == 'CS']
        it_courses = [c['code'] for c in courses_data if c['department'] == 'IT']
        ict_courses = [c['code'] for c in courses_data if c['department'] == 'ICT']
        
        course_map = {
            'CS': cs_courses,
            'IT': it_courses,
            'ICT': ict_courses
        }
        
        for dept in departments:
            # Only assign courses to year 3 students since we only have year 3 courses
            year_level = 3
            dept_courses = course_map.get(dept, [])
            
            for section in sections_per_year:
                section_name = f'{year_level}{section}'
                
                # Assign all courses for this department to each section
                for idx, course_code in enumerate(dept_courses):
                    # Rotate faculty for variety
                    faculty_index = (idx % faculty_per_dept) + 1
                    faculty_key = f'{dept}_{faculty_index}'
                    
                    if course_code in courses and faculty_key in faculty_users:
                        course_obj = courses[course_code]
                        assignment, created = CourseAssignment.objects.get_or_create(
                            course=course_obj,
                            instructor=faculty_users[faculty_key],
                            year_level=year_level,
                            section=section_name,
                            department=course_obj.department,  # Use course's department, not dept variable
                            semester=semester,
                            academic_year=academic_year,
                            defaults={'is_active': True}
                        )
                        if created:
                            assignments_created += 1
                            enrollment_count = assignment.enrollments.count()
                            total_enrollments += enrollment_count
                            if assignments_created % 10 == 0:
                                self.stdout.write(f'  ... {assignments_created} assignments created, {total_enrollments} students enrolled')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {assignments_created} course assignments'))
        self.stdout.write(self.style.SUCCESS(f'✓ Auto-enrolled {total_enrollments} students'))
        
        # ============================================
        # CREATE FEEDBACK SESSION
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n📝 Creating Feedback Session...'))
        session, created = FeedbackSession.objects.get_or_create(
            academic_year=academic_year,
            semester=semester,
            defaults={
                'title': f'{semester} Semester {academic_year} End-of-Term Feedback',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=14),
                'is_active': True,
                'instructions': 'Please provide honest and constructive feedback about your instructors and courses. Your responses are valuable for improving our programs.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created feedback session'))
        
        # ============================================
        # SUMMARY
        # ============================================
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✅ PRODUCTION DATA SEEDING COMPLETE!'))
        self.stdout.write('='*70)
        
        # Count actual data
        from api.models import Enrollment
        
        self.stdout.write('\n📊 Database Summary:')
        self.stdout.write(f'  • Total Faculty: {User.objects.filter(role="faculty").count()}')
        self.stdout.write(f'    - CS Faculty: {User.objects.filter(role="faculty", department="CS").count()}')
        self.stdout.write(f'    - IT Faculty: {User.objects.filter(role="faculty", department="IT").count()}')
        self.stdout.write(f'    - ICT Faculty: {User.objects.filter(role="faculty", department="ICT").count()}')
        
        self.stdout.write(f'\n  • Total Students: {User.objects.filter(role="student").count()}')
        for dept in departments:
            dept_students = User.objects.filter(role="student", department=dept).count()
            self.stdout.write(f'    - {dept} Students: {dept_students}')
            for year in year_levels:
                year_students = User.objects.filter(role="student", department=dept, year_level=year).count()
                self.stdout.write(f'      · Year {year}: {year_students} students')
        
        self.stdout.write(f'\n  • Total Courses: {Course.objects.count()}')
        self.stdout.write(f'  • Total Course Assignments: {CourseAssignment.objects.count()}')
        self.stdout.write(f'  • Total Auto-Enrollments: {Enrollment.objects.filter(is_auto_enrolled=True).count()}')
        self.stdout.write(f'  • Active Feedback Sessions: {FeedbackSession.objects.filter(is_active=True).count()}')
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('🔐 Login Credentials:')
        self.stdout.write('='*70)
        self.stdout.write('\n  Faculty:')
        self.stdout.write('    Email: facultyCS1@wmsu.edu.ph (or facultyIT1@wmsu.edu.ph, facultyICT1@wmsu.edu.ph)')
        self.stdout.write('    Password: Faculty@123')
        
        self.stdout.write('\n  Students:')
        self.stdout.write('    Email: 202201001@wmsu.edu.ph (or any student ID)')
        self.stdout.write('    Password: Student@123')
        
        self.stdout.write('\n  Admin:')
        self.stdout.write('    Use the admin accounts created earlier (Dean, CS/IT Dept Heads)')
        self.stdout.write('\n' + '='*70)
