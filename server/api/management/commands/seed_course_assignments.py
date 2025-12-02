from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from authentication.models import User
from api.models import Course, CourseAssignment, FeedbackSession, Enrollment


class Command(BaseCommand):
    help = 'Creates course assignments from loaded courses and triggers auto-enrollment'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating course assignments...\n'))
        
        # Clear existing assignments and enrollments
        CourseAssignment.objects.all().delete()
        Enrollment.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing course assignments and enrollments\n'))
        
        academic_year = "2024-2025"
        sections = ['A', 'B', 'C']
        assignments_created = 0
        
        # Get all courses grouped by department and year level
        departments = ['CS', 'IT', 'ICT']
        
        for dept in departments:
            self.stdout.write(self.style.SUCCESS(f'\n{dept} Department:'))
            
            # Get faculty for this department
            faculty_list = list(User.objects.filter(role='faculty', department=dept))
            if not faculty_list:
                self.stdout.write(self.style.WARNING(f'  No faculty found for {dept} department'))
                continue
            
            faculty_index = 0
            
            # Get courses for this department
            for year_level in range(1, 5):
                # Get courses for this year level and semester
                semester = '1st'
                courses = Course.objects.filter(
                    department=dept,
                    year_level=year_level,
                    semester=semester,
                    is_active=True
                )
                
                if not courses.exists():
                    continue
                
                # Assign each course to each section
                for course in courses:
                    for section in sections:
                        section_name = f'{year_level}{section}'
                        
                        # Rotate through faculty
                        instructor = faculty_list[faculty_index % len(faculty_list)]
                        faculty_index += 1
                        
                        # Create assignment
                        assignment, created = CourseAssignment.objects.get_or_create(
                            course=course,
                            instructor=instructor,
                            year_level=year_level,
                            section=section_name,
                            department=dept,
                            semester=semester,
                            academic_year=academic_year,
                            defaults={
                                'is_active': True,
                                'schedule': ''
                            }
                        )
                        
                        if created:
                            assignments_created += 1
                            if assignments_created % 50 == 0:
                                self.stdout.write(f'  ... {assignments_created} assignments created')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {assignments_created} course assignments'))
        
        # Count total enrollments
        total_enrollments = Enrollment.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✓ Auto-enrolled {total_enrollments} students\n'))
        
        # Create or update feedback session
        self.stdout.write(self.style.SUCCESS('📝 Creating Feedback Session...'))
        session, created = FeedbackSession.objects.get_or_create(
            academic_year=academic_year,
            semester='1st',
            defaults={
                'title': f'1st Semester {academic_year} End-of-Term Feedback',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=14),
                'is_active': True,
                'instructions': 'Please provide honest and constructive feedback about your instructors and courses. Your responses are valuable for improving our programs.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created feedback session\n'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Feedback session already exists\n'))
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✅ COURSE ASSIGNMENTS COMPLETE!'))
        self.stdout.write('='*70)
        
        self.stdout.write('\n📊 Database Summary:')
        self.stdout.write(f'  • Total Students: {User.objects.filter(role="student").count()}')
        self.stdout.write(f'  • Total Faculty: {User.objects.filter(role="faculty").count()}')
        self.stdout.write(f'  • Total Courses: {Course.objects.count()}')
        self.stdout.write(f'  • Total Course Assignments: {CourseAssignment.objects.count()}')
        self.stdout.write(f'  • Total Auto-Enrollments: {Enrollment.objects.filter(is_auto_enrolled=True).count()}')
        
        # Breakdown by department
        for dept in departments:
            dept_assignments = CourseAssignment.objects.filter(department=dept).count()
            dept_enrollments = Enrollment.objects.filter(course_assignment__department=dept).count()
            self.stdout.write(f'\n  {dept} Department:')
            self.stdout.write(f'    · Course Assignments: {dept_assignments}')
            self.stdout.write(f'    · Student Enrollments: {dept_enrollments}')
        
        self.stdout.write('\n' + '='*70 + '\n')
