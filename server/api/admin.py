from django.contrib import admin
from .models import Course, CourseAssignment, Enrollment, FeedbackSession, Feedback


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'year_level', 'units', 'is_active']
    list_filter = ['department', 'year_level', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['department', 'year_level', 'code']


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ['course', 'instructor', 'year_level', 'section', 'department', 'semester', 'academic_year', 'is_active']
    list_filter = ['department', 'year_level', 'semester', 'academic_year', 'is_active']
    search_fields = ['course__code', 'course__name', 'instructor__username', 'instructor__email']
    ordering = ['-academic_year', 'semester', 'course']
    raw_id_fields = ['instructor']
    
    def save_model(self, request, obj, form, change):
        """Override to show enrollment count after save"""
        super().save_model(request, obj, form, change)
        if not change:  # Only for new assignments
            count = obj.auto_enroll_students()
            self.message_user(request, f"Course assignment created. {count} students auto-enrolled.")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'get_course_code', 'get_instructor', 'get_section', 'is_auto_enrolled', 'status', 'enrolled_at']
    list_filter = ['is_auto_enrolled', 'status', 'course_assignment__semester', 'course_assignment__academic_year']
    search_fields = ['student__username', 'student__email', 'student__student_id', 'course_assignment__course__code']
    ordering = ['-enrolled_at']
    raw_id_fields = ['student', 'course_assignment']
    
    def get_course_code(self, obj):
        return obj.course_assignment.course.code
    get_course_code.short_description = 'Course'
    
    def get_instructor(self, obj):
        return obj.course_assignment.instructor.get_full_name()
    get_instructor.short_description = 'Instructor'
    
    def get_section(self, obj):
        return obj.course_assignment.section or 'All Sections'
    get_section.short_description = 'Section'


@admin.register(FeedbackSession)
class FeedbackSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'academic_year', 'semester', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'semester', 'academic_year']
    search_fields = ['title', 'academic_year']
    ordering = ['-start_date']
    
    def save_model(self, request, obj, form, change):
        """Override to warn about making session active"""
        if obj.is_active:
            self.message_user(request, "This session is now active. All other sessions have been deactivated.", level='warning')
        super().save_model(request, obj, form, change)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['get_student', 'get_course', 'get_instructor', 'rating', 'sentiment_label', 'status', 'is_anonymous', 'submitted_at']
    list_filter = ['status', 'is_anonymous', 'sentiment_label', 'feedback_session__semester', 'feedback_session__academic_year']
    search_fields = ['student__username', 'student__email', 'course_assignment__course__code', 'suggested_changes', 'further_comments']
    ordering = ['-submitted_at']
    readonly_fields = ['sentiment_score', 'sentiment_label', 'emotions', 'submitted_at', 'created_at', 'updated_at']
    raw_id_fields = ['student', 'course_assignment', 'feedback_session']
    
    fieldsets = (
        ('Assignment Info', {
            'fields': ('student', 'course_assignment', 'feedback_session')
        }),
        ('Feedback Content', {
            'fields': ('rating', 'suggested_changes', 'best_teaching_aspect', 'least_teaching_aspect', 'further_comments', 'is_anonymous', 'status')
        }),
        ('ML Analysis Results', {
            'fields': ('sentiment_score', 'sentiment_label', 'emotions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_student(self, obj):
        if obj.is_anonymous:
            return "Anonymous"
        return obj.student.get_full_name()
    get_student.short_description = 'Student'
    
    def get_course(self, obj):
        return obj.course_assignment.course.code
    get_course.short_description = 'Course'
    
    def get_instructor(self, obj):
        return obj.course_assignment.instructor.get_full_name()
    get_instructor.short_description = 'Instructor'

