from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from authentication.models import User
from api.models import Course, CourseAssignment, FeedbackSession, Enrollment
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Seeds the database with sample courses, students, faculty, and course assignments for testing auto-enrollment'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting database seeding...'))
        
        # Create Faculty
        faculty_data = [
            {'email': 'prof.juan.santos@wmsu.edu.ph', 'username': 'prof_juan', 'first_name': 'Juan', 'last_name': 'Santos', 'department': 'CS'},
            {'email': 'prof.maria.cruz@wmsu.edu.ph', 'username': 'prof_maria', 'first_name': 'Maria', 'last_name': 'Cruz', 'department': 'IT'},
            {'email': 'prof.pedro.reyes@wmsu.edu.ph', 'username': 'prof_pedro', 'first_name': 'Pedro', 'last_name': 'Reyes', 'department': 'CS'},
        ]
        
        faculty_users = {}
        for data in faculty_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'faculty',
                    'department': data['department'],
                    'is_staff': True
                }
            )
            if created:
                user.set_password('faculty123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created faculty: {user.email}'))
            else:
                self.stdout.write(self.style.WARNING(f'  Faculty already exists: {user.email}'))
            faculty_users[data['username']] = user
        
        # Create Students
        students_data = [
            # Regular CS Year 3 Section 3A students
            {'email': 'juan.delacruz@wmsu.edu.ph', 'username': 'juan_delacruz', 'student_id': '2021-12345', 'first_name': 'Juan', 'last_name': 'dela Cruz', 'department': 'CS', 'year_level': 3, 'section': '3A'},
            {'email': 'pedro.garcia@wmsu.edu.ph', 'username': 'pedro_garcia', 'student_id': '2021-12346', 'first_name': 'Pedro', 'last_name': 'Garcia', 'department': 'CS', 'year_level': 3, 'section': '3A'},
            {'email': 'ana.reyes@wmsu.edu.ph', 'username': 'ana_reyes', 'student_id': '2021-12347', 'first_name': 'Ana', 'last_name': 'Reyes', 'department': 'CS', 'year_level': 3, 'section': '3A'},
            
            # Regular CS Year 3 Section 3B students
            {'email': 'jose.santos@wmsu.edu.ph', 'username': 'jose_santos', 'student_id': '2021-12348', 'first_name': 'Jose', 'last_name': 'Santos', 'department': 'CS', 'year_level': 3, 'section': '3B'},
            {'email': 'rosa.lopez@wmsu.edu.ph', 'username': 'rosa_lopez', 'student_id': '2021-12349', 'first_name': 'Rosa', 'last_name': 'Lopez', 'department': 'CS', 'year_level': 3, 'section': '3B'},
            
            # Regular IT Year 2 Section 2A students
            {'email': 'maria.santos@wmsu.edu.ph', 'username': 'maria_santos', 'student_id': '2022-67890', 'first_name': 'Maria', 'last_name': 'Santos', 'department': 'IT', 'year_level': 2, 'section': '2A'},
            {'email': 'carlos.mendoza@wmsu.edu.ph', 'username': 'carlos_mendoza', 'student_id': '2022-67891', 'first_name': 'Carlos', 'last_name': 'Mendoza', 'department': 'IT', 'year_level': 2, 'section': '2A'},
            
            # Irregular student (Year 4 but might take Year 3 courses)
            {'email': 'irregular.student@wmsu.edu.ph', 'username': 'irregular_student', 'student_id': '2020-11111', 'first_name': 'Irregular', 'last_name': 'Student', 'department': 'CS', 'year_level': 4, 'section': '4A'},
        ]
        
        for data in students_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'student_id': data['student_id'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'student',
                    'department': data['department'],
                    'year_level': data['year_level'],
                    'section': data['section']
                }
            )
            if created:
                user.set_password('student123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created student: {user.email} (Year {user.year_level}, Section {user.section})'))
            else:
                self.stdout.write(self.style.WARNING(f'  Student already exists: {user.email}'))
        
        # Create Courses
        courses_data = [
            # CS Year 3 Courses
            {'code': 'CS301', 'name': 'Data Structures and Algorithms', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS302', 'name': 'Database Systems', 'department': 'CS', 'year_level': 3, 'units': 3},
            {'code': 'CS303', 'name': 'Software Engineering', 'department': 'CS', 'year_level': 3, 'units': 3},
            
            # IT Year 2 Courses
            {'code': 'IT201', 'name': 'Web Development', 'department': 'IT', 'year_level': 2, 'units': 3},
            {'code': 'IT202', 'name': 'Network Fundamentals', 'department': 'IT', 'year_level': 2, 'units': 3},
        ]
        
        courses = {}
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
                self.stdout.write(self.style.SUCCESS(f'✓ Created course: {course.code} - {course.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  Course already exists: {course.code}'))
            courses[course.code] = course
        
        # Create Course Assignments (this will trigger auto-enrollment!)
        assignments_data = [
            # CS Year 3 Section 3A
            {'course': 'CS301', 'instructor': 'prof_juan', 'year_level': 3, 'section': '3A', 'department': 'CS'},
            {'course': 'CS302', 'instructor': 'prof_pedro', 'year_level': 3, 'section': '3A', 'department': 'CS'},
            {'course': 'CS303', 'instructor': 'prof_juan', 'year_level': 3, 'section': '3A', 'department': 'CS'},
            
            # CS Year 3 Section 3B
            {'course': 'CS301', 'instructor': 'prof_juan', 'year_level': 3, 'section': '3B', 'department': 'CS'},
            {'course': 'CS302', 'instructor': 'prof_pedro', 'year_level': 3, 'section': '3B', 'department': 'CS'},
            
            # IT Year 2 Section 2A
            {'course': 'IT201', 'instructor': 'prof_maria', 'year_level': 2, 'section': '2A', 'department': 'IT'},
            {'course': 'IT202', 'instructor': 'prof_maria', 'year_level': 2, 'section': '2A', 'department': 'IT'},
        ]
        
        academic_year = "2024-2025"
        semester = "1st"
        
        for data in assignments_data:
            assignment, created = CourseAssignment.objects.get_or_create(
                course=courses[data['course']],
                instructor=faculty_users[data['instructor']],
                year_level=data['year_level'],
                section=data['section'],
                department=data['department'],
                semester=semester,
                academic_year=academic_year,
                defaults={'is_active': True}
            )
            if created:
                # Count enrollments
                enrollment_count = assignment.enrollments.count()
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Created assignment: {assignment.course.code} - {assignment.instructor.get_full_name()} - '
                    f'Section {assignment.section} → {enrollment_count} students auto-enrolled'
                ))
            else:
                self.stdout.write(self.style.WARNING(f'  Assignment already exists: {assignment}'))
        
        # Create a Feedback Session
        session, created = FeedbackSession.objects.get_or_create(
            academic_year=academic_year,
            semester=semester,
            defaults={
                'title': f'{semester} Semester {academic_year} End-of-Term Feedback',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=14),
                'is_active': True,
                'instructions': 'Please provide honest and constructive feedback about your instructors and courses.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created feedback session: {session.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'  Feedback session already exists: {session.title}'))
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✓ Database seeding complete!'))
        self.stdout.write('\n' + 'Summary:')
        self.stdout.write(f'  - Faculty: {User.objects.filter(role="faculty").count()}')
        self.stdout.write(f'  - Students: {User.objects.filter(role="student").count()}')
        self.stdout.write(f'  - Courses: {Course.objects.count()}')
        self.stdout.write(f'  - Course Assignments: {CourseAssignment.objects.count()}')
        self.stdout.write(f'  - Auto-enrollments: {Enrollment.objects.filter(is_auto_enrolled=True).count()}')
        self.stdout.write(f'  - Feedback Sessions: {FeedbackSession.objects.count()}')
        
        self.stdout.write('\n' + 'Test Credentials:')
        self.stdout.write('  Faculty: prof.juan.santos@wmsu.edu.ph / faculty123')
        self.stdout.write('  Student: juan.delacruz@wmsu.edu.ph / student123')
        self.stdout.write('  Admin: Use the accounts you created earlier')
