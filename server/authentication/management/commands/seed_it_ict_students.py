from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from authentication.models import User
from api.models import Course, CourseAssignment, FeedbackSession, Enrollment


class Command(BaseCommand):
    help = 'Seeds IT and ICT students (both under IT department)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting IT and ICT student seeding...\n'))
        
        # Configuration
        departments = ['IT', 'ICT']  # Both under IT department
        year_levels = [1, 2, 3, 4]
        sections_per_year = ['A', 'B', 'C']  # 3 sections per year level
        students_per_section = 10  # 10 students per section = 30 per year level
        
        # ============================================
        # CREATE IT AND ICT STUDENTS
        # ============================================
        self.stdout.write(self.style.SUCCESS('👨‍🎓 Creating IT and ICT Students...\n'))
        students_created = 0
        student_counter = {}
        
        for dept in departments:
            self.stdout.write(self.style.WARNING(f'{dept} Department:'))
            
            # Set different ID ranges for each department
            # CS uses 00001-00030 per year level
            # IT uses 10001-10030 per year level
            # ICT uses 20001-20030 per year level
            base_offset = 0
            if dept == 'IT':
                base_offset = 10000
            elif dept == 'ICT':
                base_offset = 20000
            
            for year_level in year_levels:
                for section in sections_per_year:
                    for student_num in range(1, students_per_section + 1):
                        # Generate student ID: Year code based on year level
                        year_code = 2025 - year_level
                        
                        # Generate unique counter for each department and year
                        if dept not in student_counter:
                            student_counter[dept] = {}
                        if year_level not in student_counter[dept]:
                            student_counter[dept][year_level] = 1
                        
                        counter = student_counter[dept][year_level]
                        student_counter[dept][year_level] += 1
                        
                        # Format: YYYYXXXXX with department offset
                        # CS: 202200001-202200030
                        # IT: 202210001-202210030
                        # ICT: 202220001-202220030
                        student_id_num = f'{year_code}{base_offset + counter:05d}'
                        email = f'{student_id_num}@wmsu.edu.ph'
                        username = f'student_{dept.lower()}_{student_id_num}'
                        
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
                            if students_created % 10 == 0:
                                self.stdout.write(f'  ... {students_created} students created')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {students_created} new students\n'))
        
        # ============================================
        # UPDATE COURSE ASSIGNMENTS TO TRIGGER AUTO-ENROLLMENT
        # ============================================
        self.stdout.write(self.style.SUCCESS('🎓 Triggering auto-enrollment for existing course assignments...\n'))
        
        # Re-trigger auto-enrollment for all existing IT and ICT course assignments
        it_ict_assignments = CourseAssignment.objects.filter(department__in=['IT', 'ICT'])
        enrollments_created = 0
        
        for assignment in it_ict_assignments:
            # Manually call auto_enroll_students for existing assignments
            filters = {
                'role': 'student',
                'department': assignment.department,
                'year_level': assignment.year_level
            }
            if assignment.section:
                filters['section'] = assignment.section
            
            students = User.objects.filter(**filters)
            for student in students:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course_assignment=assignment,
                    defaults={'is_auto_enrolled': True}
                )
                if created:
                    enrollments_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {enrollments_created} new enrollments\n'))
        
        # ============================================
        # SUMMARY
        # ============================================
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✅ IT AND ICT STUDENTS SEEDING COMPLETE!'))
        self.stdout.write('='*70)
        
        self.stdout.write('\n📊 Database Summary:')
        
        # Student counts
        total_students = User.objects.filter(role='student').count()
        cs_students = User.objects.filter(role='student', department='CS').count()
        it_students = User.objects.filter(role='student', department='IT').count()
        ict_students = User.objects.filter(role='student', department='ICT').count()
        
        self.stdout.write(f'\n  • Total Students: {total_students}')
        self.stdout.write(f'    - CS Students: {cs_students}')
        self.stdout.write(f'    - IT Students: {it_students}')
        self.stdout.write(f'    - ICT Students: {ict_students}')
        
        # Show breakdown by year level for IT and ICT
        for dept in ['IT', 'ICT']:
            self.stdout.write(f'\n  {dept} Department Breakdown:')
            for year in year_levels:
                year_count = User.objects.filter(role='student', department=dept, year_level=year).count()
                self.stdout.write(f'    · Year {year}: {year_count} students')
        
        self.stdout.write(f'\n  • Total Enrollments: {Enrollment.objects.count()}')
        self.stdout.write(f'  • Total Faculty: {User.objects.filter(role="faculty").count()}')
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('🔐 Login Credentials for new students:')
        self.stdout.write('='*70)
        self.stdout.write('\n  IT Students:')
        self.stdout.write('    Email: 202400001@wmsu.edu.ph (Year 1), 202300001@wmsu.edu.ph (Year 2), etc.')
        self.stdout.write('    Password: Student@123')
        self.stdout.write('\n  ICT Students:')
        self.stdout.write('    Email: 202400001@wmsu.edu.ph (Year 1), 202300001@wmsu.edu.ph (Year 2), etc.')
        self.stdout.write('    Password: Student@123')
        self.stdout.write('\n  Note: Student IDs follow the same format as CS students')
        self.stdout.write('\n' + '='*70 + '\n')
