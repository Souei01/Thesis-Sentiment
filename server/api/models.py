from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Course(models.Model):
    """Course/Subject in the curriculum"""
    DEPARTMENT_CHOICES = [
        ('CS', 'Computer Science'),
        ('IT', 'Information Technology'),
        ('ICT', 'ICT'),
    ]
    
    YEAR_LEVEL_CHOICES = [
        (1, 'Year 1'),
        (2, 'Year 2'),
        (3, 'Year 3'),
        (4, 'Year 4'),
    ]
    
    SEMESTER_CHOICES = [
        ('1st', '1st Semester'),
        ('2nd', '2nd Semester'),
        ('Summer', 'Summer'),
    ]
    
    code = models.CharField(max_length=20, help_text="e.g., CS101, IT202")
    name = models.CharField(max_length=200, help_text="e.g., Data Structures")
    description = models.TextField(blank=True)
    department = models.CharField(max_length=5, choices=DEPARTMENT_CHOICES)
    year_level = models.IntegerField(choices=YEAR_LEVEL_CHOICES)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='1st')
    units = models.IntegerField(default=3, help_text="Credit units")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['department', 'year_level', 'semester', 'code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        unique_together = [['code', 'department', 'year_level', 'semester']]
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.semester})"


class CourseAssignment(models.Model):
    """Assigns an instructor to teach a course for a specific section/semester"""
    SEMESTER_CHOICES = [
        ('1st', '1st Semester'),
        ('2nd', '2nd Semester'),
        ('Summer', 'Summer'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teaching_assignments',
        limit_choices_to={'role': 'faculty'}
    )
    year_level = models.IntegerField(choices=Course.YEAR_LEVEL_CHOICES)
    section = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Leave blank to assign to all sections of this year level"
    )
    department = models.CharField(max_length=5, choices=Course.DEPARTMENT_CHOICES)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    schedule = models.CharField(max_length=100, blank=True, help_text="e.g., MWF 9:00-10:00 AM")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-academic_year', 'semester', 'course']
        verbose_name = 'Course Assignment'
        verbose_name_plural = 'Course Assignments'
        unique_together = ['course', 'instructor', 'year_level', 'section', 'semester', 'academic_year']
    
    def __str__(self):
        section_str = f"Section {self.section}" if self.section else "All Sections"
        return f"{self.course.code} - {self.instructor.get_full_name()} - {section_str} ({self.semester} {self.academic_year})"
    
    def save(self, *args, **kwargs):
        # Note: We allow course department to differ from assignment department
        # because some courses are shared across departments (e.g., IT courses for ICT students)
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Auto-enroll students after saving
        if is_new:
            self.auto_enroll_students()
    
    def auto_enroll_students(self):
        """Automatically enroll students matching year_level, section, and department"""
        from authentication.models import User
        
        # Build filter criteria
        filters = {
            'role': 'student',
            'department': self.department,
            'year_level': self.year_level,
            'is_active': True,
        }
        
        # If section is specified, filter by section; otherwise enroll all sections
        if self.section:
            filters['section'] = self.section
        
        # Find matching students
        students = User.objects.filter(**filters)
        
        # Create enrollments
        enrollments_created = 0
        for student in students:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course_assignment=self,
                defaults={'is_auto_enrolled': True, 'status': 'enrolled'}
            )
            if created:
                enrollments_created += 1
        
        return enrollments_created


class Enrollment(models.Model):
    """Links students to course assignments (auto or manual)"""
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'}
    )
    course_assignment = models.ForeignKey(
        CourseAssignment,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    is_auto_enrolled = models.BooleanField(
        default=True,
        help_text="True if enrolled automatically, False if manually added (e.g., irregular student)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-enrolled_at']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ['student', 'course_assignment']
    
    def __str__(self):
        return f"{self.student.get_full_name()} enrolled in {self.course_assignment.course.code}"
    
    def clean(self):
        # Validate student role
        if self.student.role != 'student':
            raise ValidationError("Only users with role 'student' can be enrolled")


class FeedbackSession(models.Model):
    """Defines when students can submit feedback"""
    SEMESTER_CHOICES = [
        ('1st', '1st Semester'),
        ('2nd', '2nd Semester'),
        ('Summer', 'Summer'),
    ]
    
    title = models.CharField(max_length=200, help_text="e.g., End of 1st Semester 2024-2025 Feedback")
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False, help_text="Only one session should be active at a time")
    instructions = models.TextField(
        blank=True,
        help_text="Instructions to display to students when submitting feedback"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Feedback Session'
        verbose_name_plural = 'Feedback Sessions'
    
    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"
    
    def save(self, *args, **kwargs):
        # Ensure only one active session
        if self.is_active:
            FeedbackSession.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Feedback(models.Model):
    """Student feedback for course assignments"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_feedback',
        limit_choices_to={'role': 'student'}
    )
    course_assignment = models.ForeignKey(
        CourseAssignment,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    feedback_session = models.ForeignKey(
        FeedbackSession,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    
    # Part 1: Commitment (1-5 scale)
    rating_sensitivity = models.IntegerField(
        default=3,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Demonstrates sensitivity to students' ability to attend and absorb content"
    )
    rating_integration = models.IntegerField(
        default=3,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Integrates learning objectives with students"
    )
    rating_availability = models.IntegerField(
        default=3,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Makes self available to students after class"
    )
    rating_punctuality = models.IntegerField(
        default=3,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Comes to class on time, well-prepared"
    )
    rating_record_keeping = models.IntegerField(
        default=3,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Keeps accurate records and prompt submission"
    )
    
    # Part 2: Knowledge of Subject (1-5 scale)
    rating_mastery = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_state_of_art = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_practical_integration = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_relevance = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_current_trends = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    
    # Part 3: Independent Learning (1-5 scale)
    rating_teaching_strategies = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_student_esteem = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_student_autonomy = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_independent_thinking = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_beyond_required = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    
    # Part 4: Management of Learning (1-5 scale)
    rating_student_contribution = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_facilitator_role = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_discussion_encouragement = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_instructional_methods = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_instructional_materials = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    
    # Part 5: Feedback and Assessment (1-5 scale)
    rating_clear_communication = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_timely_feedback = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_improvement_feedback = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    
    # Part 6: Other Questions (Yes/No)
    syllabus_explained = models.BooleanField(null=True, blank=True)
    delivered_as_outlined = models.BooleanField(null=True, blank=True)
    grading_criteria_explained = models.BooleanField(null=True, blank=True)
    exams_related = models.BooleanField(null=True, blank=True)
    assignments_related = models.BooleanField(null=True, blank=True)
    lms_resources_useful = models.BooleanField(null=True, blank=True)
    
    # Part 7: Overall Experience
    worthwhile_class = models.BooleanField(null=True, blank=True)
    would_recommend = models.BooleanField(null=True, blank=True)
    hours_per_week = models.IntegerField(default=0)
    overall_rating = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    
    # Part 8: Student Self-Evaluation (1-5 scale)
    rating_constructive_contribution = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    rating_achieving_outcomes = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    
    # Overall rating (computed average of all ratings)
    rating = models.FloatField(
        blank=True,
        null=True,
        help_text="Overall average rating (computed from all rating questions)"
    )
    
    # Part 9: Text feedback fields (Comments)
    suggested_changes = models.TextField(blank=True, help_text="What changes would you suggest?")
    best_teaching_aspect = models.TextField(blank=True, help_text="What did you like best about the teaching?")
    least_teaching_aspect = models.TextField(blank=True, help_text="What did you like least?")
    further_comments = models.TextField(blank=True, help_text="Any additional comments")
    
    # ML Analysis Results - Emotion Detection (XLM-RoBERTa)
    emotion_suggested_changes = models.CharField(
        max_length=20,
        blank=True,
        help_text="Predicted emotion for suggested_changes field"
    )
    emotion_best_aspect = models.CharField(
        max_length=20,
        blank=True,
        help_text="Predicted emotion for best_teaching_aspect field"
    )
    emotion_least_aspect = models.CharField(
        max_length=20,
        blank=True,
        help_text="Predicted emotion for least_teaching_aspect field"
    )
    emotion_further_comments = models.CharField(
        max_length=20,
        blank=True,
        help_text="Predicted emotion for further_comments field"
    )
    
    # Confidence scores for emotion predictions (stored as JSON)
    emotion_confidence_scores = models.JSONField(
        blank=True,
        null=True,
        help_text="Confidence scores for each emotion prediction"
    )
    
    # Legacy sentiment fields (can be deprecated later)
    sentiment_score = models.FloatField(
        blank=True,
        null=True,
        help_text="Sentiment score from ML model (-1 to 1)"
    )
    sentiment_label = models.CharField(
        max_length=20,
        blank=True,
        help_text="e.g., Positive, Negative, Neutral"
    )
    emotions = models.JSONField(
        blank=True,
        null=True,
        help_text="Detected emotions from ML model (JSON)"
    )
    
    is_anonymous = models.BooleanField(
        default=True,
        help_text="Student identity is hidden from instructor"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        unique_together = ['student', 'course_assignment', 'feedback_session']
    
    def __str__(self):
        return f"Feedback from {self.student.email} for {self.course_assignment.course.code}"
    
    def __str__(self):
        student_name = "Anonymous" if self.is_anonymous else self.enrollment.student.get_full_name()
        return f"Feedback by {student_name} for {self.enrollment.course_assignment.course.code}"
    
    def save(self, *args, **kwargs):
        # Compute average rating from all rating fields
        ratings = [
            # Commitment
            self.rating_sensitivity,
            self.rating_integration,
            self.rating_availability,
            self.rating_punctuality,
            self.rating_record_keeping,
            # Knowledge of Subject
            self.rating_mastery,
            self.rating_state_of_art,
            self.rating_practical_integration,
            self.rating_relevance,
            self.rating_current_trends,
            # Independent Learning
            self.rating_teaching_strategies,
            self.rating_student_esteem,
            self.rating_student_autonomy,
            self.rating_independent_thinking,
            self.rating_beyond_required,
            # Management of Learning
            self.rating_student_contribution,
            self.rating_facilitator_role,
            self.rating_discussion_encouragement,
            self.rating_instructional_methods,
            self.rating_instructional_materials,
            # Feedback and Assessment
            self.rating_clear_communication,
            self.rating_timely_feedback,
            self.rating_improvement_feedback,
            # Overall Experience
            self.overall_rating,
            # Student Self-Evaluation
            self.rating_constructive_contribution,
            self.rating_achieving_outcomes,
        ]
        self.rating = sum(ratings) / len(ratings)
        
        # Set submitted_at when status changes to submitted
        if self.status == 'submitted' and not self.submitted_at:
            from django.utils import timezone
            self.submitted_at = timezone.now()
        super().save(*args, **kwargs)

