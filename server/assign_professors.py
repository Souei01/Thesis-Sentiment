"""
Assign professors to courses/subjects with sections
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from authentication.models import User
from api.models import Course, CourseAssignment
from django.db import transaction

# Faculty mapping
FACULTY_DATA = {
    'CS': [
        {'email': 'facultyCS1@wmsu.edu.ph', 'name': 'Professor CS 1', 'first': 'Professor', 'last': 'CS1'},
        {'email': 'facultyCS2@wmsu.edu.ph', 'name': 'Professor CS 2', 'first': 'Professor', 'last': 'CS2'},
        {'email': 'facultyCS3@wmsu.edu.ph', 'name': 'Professor CS 3', 'first': 'Professor', 'last': 'CS3'},
        {'email': 'facultyCS4@wmsu.edu.ph', 'name': 'Professor CS 4', 'first': 'Professor', 'last': 'CS4'},
        {'email': 'facultyCS5@wmsu.edu.ph', 'name': 'Professor CS 5', 'first': 'Professor', 'last': 'CS5'},
        {'email': 'facultyCS6@wmsu.edu.ph', 'name': 'Professor CS 6', 'first': 'Professor', 'last': 'CS6'},
        {'email': 'facultyCS7@wmsu.edu.ph', 'name': 'Professor CS 7', 'first': 'Professor', 'last': 'CS7'},
        {'email': 'facultyCS8@wmsu.edu.ph', 'name': 'Professor CS 8', 'first': 'Professor', 'last': 'CS8'},
        {'email': 'facultyCS9@wmsu.edu.ph', 'name': 'Professor CS 9', 'first': 'Professor', 'last': 'CS9'},
        {'email': 'facultyCS10@wmsu.edu.ph', 'name': 'Professor CS 10', 'first': 'Professor', 'last': 'CS10'},
    ],
    'IT': [
        {'email': 'facultyIT1@wmsu.edu.ph', 'name': 'Professor IT 1', 'first': 'Professor', 'last': 'IT1'},
        {'email': 'facultyIT2@wmsu.edu.ph', 'name': 'Professor IT 2', 'first': 'Professor', 'last': 'IT2'},
        {'email': 'facultyIT3@wmsu.edu.ph', 'name': 'Professor IT 3', 'first': 'Professor', 'last': 'IT3'},
        {'email': 'facultyIT4@wmsu.edu.ph', 'name': 'Professor IT 4', 'first': 'Professor', 'last': 'IT4'},
        {'email': 'facultyIT5@wmsu.edu.ph', 'name': 'Professor IT 5', 'first': 'Professor', 'last': 'IT5'},
        {'email': 'facultyIT6@wmsu.edu.ph', 'name': 'Professor IT 6', 'first': 'Professor', 'last': 'IT6'},
        {'email': 'facultyIT7@wmsu.edu.ph', 'name': 'Professor IT 7', 'first': 'Professor', 'last': 'IT7'},
        {'email': 'facultyIT8@wmsu.edu.ph', 'name': 'Professor IT 8', 'first': 'Professor', 'last': 'IT8'},
        {'email': 'facultyIT9@wmsu.edu.ph', 'name': 'Professor IT 9', 'first': 'Professor', 'last': 'IT9'},
        {'email': 'facultyIT10@wmsu.edu.ph', 'name': 'Professor IT 10', 'first': 'Professor', 'last': 'IT10'},
    ],
    'ICT': [
        {'email': 'facultyICT1@wmsu.edu.ph', 'name': 'Professor ICT 1', 'first': 'Professor', 'last': 'ICT1'},
        {'email': 'facultyICT2@wmsu.edu.ph', 'name': 'Professor ICT 2', 'first': 'Professor', 'last': 'ICT2'},
        {'email': 'facultyICT3@wmsu.edu.ph', 'name': 'Professor ICT 3', 'first': 'Professor', 'last': 'ICT3'},
        {'email': 'facultyICT4@wmsu.edu.ph', 'name': 'Professor ICT 4', 'first': 'Professor', 'last': 'ICT4'},
        {'email': 'facultyICT5@wmsu.edu.ph', 'name': 'Professor ICT 5', 'first': 'Professor', 'last': 'ICT5'},
        {'email': 'facultyICT6@wmsu.edu.ph', 'name': 'Professor ICT 6', 'first': 'Professor', 'last': 'ICT6'},
        {'email': 'facultyICT7@wmsu.edu.ph', 'name': 'Professor ICT 7', 'first': 'Professor', 'last': 'ICT7'},
        {'email': 'facultyICT8@wmsu.edu.ph', 'name': 'Professor ICT 8', 'first': 'Professor', 'last': 'ICT8'},
        {'email': 'facultyICT9@wmsu.edu.ph', 'name': 'Professor ICT 9', 'first': 'Professor', 'last': 'ICT9'},
        {'email': 'facultyICT10@wmsu.edu.ph', 'name': 'Professor ICT 10', 'first': 'Professor', 'last': 'ICT10'},
    ]
}

# Sections for each department/year
SECTIONS = {
    'CS': {
        1: ['A', 'B'],           # Year 1: sections A, B
        2: ['A', 'B', 'C'],      # Year 2: sections A, B, C
        3: ['A', 'B'],           # Year 3: sections A, B
        4: ['A'],                # Year 4: section A
    },
    'IT': {
        1: ['A', 'B'],
        2: ['A', 'B'],
        3: ['A'],
        4: ['A'],
    },
    'ICT': {
        1: ['A'],
        2: ['A'],
        3: ['A'],
        4: ['A'],
    }
}

def update_faculty_names():
    """Update faculty names to Professor CS1, etc."""
    print("Updating faculty names...")
    for dept, faculty_list in FACULTY_DATA.items():
        for fac_data in faculty_list:
            try:
                user = User.objects.get(email=fac_data['email'])
                user.first_name = fac_data['first']
                user.last_name = fac_data['last']
                user.save()
                print(f"✅ Updated: {fac_data['email']} → {fac_data['first']} {fac_data['last']}")
            except User.DoesNotExist:
                print(f"⚠️  User not found: {fac_data['email']}")

def assign_professors_to_courses():
    """Assign professors to courses with different sections"""
    print("\n" + "="*80)
    print("ASSIGNING PROFESSORS TO COURSES")
    print("="*80)
    
    current_year = "2024-2025"
    assignments_created = 0
    
    with transaction.atomic():
        # Clear existing assignments
        deleted_count = CourseAssignment.objects.all().delete()[0]
        print(f"\nCleared {deleted_count} existing assignments")
        
        # Get all courses
        courses = Course.objects.filter(is_active=True).order_by('department', 'year_level', 'semester')
        
        faculty_index = {}  # Track which faculty to assign next per department
        
        for course in courses:
            dept = course.department
            year = course.year_level
            semester = course.semester
            
            # Get sections for this department/year
            sections = SECTIONS.get(dept, {}).get(year, ['A'])
            
            # Get faculty for this department
            dept_faculty = FACULTY_DATA.get(dept, [])
            if not dept_faculty:
                print(f"⚠️  No faculty found for department {dept}")
                continue
            
            # Initialize faculty index for this department
            if dept not in faculty_index:
                faculty_index[dept] = 0
            
            print(f"\n📚 {course.code} - {course.name} ({dept} Y{year} {semester})")
            
            # Assign different professors to different sections
            for section in sections:
                # Get next faculty member (round-robin)
                faculty_data = dept_faculty[faculty_index[dept] % len(dept_faculty)]
                faculty_index[dept] += 1
                
                try:
                    instructor = User.objects.get(email=faculty_data['email'])
                    
                    # Create assignment
                    assignment = CourseAssignment.objects.create(
                        course=course,
                        instructor=instructor,
                        year_level=year,
                        section=section,
                        department=dept,
                        semester=semester,
                        academic_year=current_year,
                        schedule=f"MWF 9:00-10:00 AM",  # Default schedule
                        is_active=True
                    )
                    
                    assignments_created += 1
                    print(f"  ✅ Section {section}: {instructor.get_full_name()} ({instructor.email})")
                    
                except User.DoesNotExist:
                    print(f"  ❌ Section {section}: Faculty not found - {faculty_data['email']}")
                except Exception as e:
                    print(f"  ❌ Section {section}: Error - {str(e)}")
    
    print("\n" + "="*80)
    print(f"✅ COMPLETED: {assignments_created} course assignments created!")
    print("="*80)

def show_summary():
    """Show summary of assignments"""
    print("\n" + "="*80)
    print("ASSIGNMENT SUMMARY")
    print("="*80)
    
    for dept in ['CS', 'IT', 'ICT']:
        assignments = CourseAssignment.objects.filter(department=dept).select_related('course', 'instructor')
        print(f"\n{dept} Department: {assignments.count()} assignments")
        
        # Group by course
        courses_assigned = {}
        for assignment in assignments:
            course_key = f"{assignment.course.code} - {assignment.course.name}"
            if course_key not in courses_assigned:
                courses_assigned[course_key] = []
            courses_assigned[course_key].append({
                'section': assignment.section,
                'professor': assignment.instructor.get_full_name()
            })
        
        # Show first 3 courses as example
        for idx, (course_name, sections) in enumerate(list(courses_assigned.items())[:3]):
            print(f"\n  {course_name}:")
            for sec in sections:
                print(f"    Section {sec['section']}: {sec['professor']}")

if __name__ == '__main__':
    print("="*80)
    print("PROFESSOR ASSIGNMENT SETUP")
    print("="*80)
    
    # Step 1: Update faculty names
    update_faculty_names()
    
    # Step 2: Assign professors to courses
    assign_professors_to_courses()
    
    # Step 3: Show summary
    show_summary()
    
    print("\n✅ All done!")
