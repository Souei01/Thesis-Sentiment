from rest_framework import serializers
from .models import Feedback, Course, CourseAssignment, FeedbackSession
from authentication.models import User


class FeedbackSummarySerializer(serializers.Serializer):
    """Serializer for aggregated feedback data"""
    total_feedback = serializers.IntegerField()
    average_rating = serializers.FloatField()
    
    # Commitment ratings
    avg_sensitivity = serializers.FloatField()
    avg_integration = serializers.FloatField()
    avg_availability = serializers.FloatField()
    avg_punctuality = serializers.FloatField()
    avg_record_keeping = serializers.FloatField()
    
    # Knowledge of Subject
    avg_mastery = serializers.FloatField()
    avg_state_of_art = serializers.FloatField()
    avg_practical_integration = serializers.FloatField()
    avg_relevance = serializers.FloatField()
    avg_current_trends = serializers.FloatField()
    
    # Independent Learning
    avg_teaching_strategies = serializers.FloatField()
    avg_student_esteem = serializers.FloatField()
    avg_student_autonomy = serializers.FloatField()
    avg_independent_thinking = serializers.FloatField()
    avg_beyond_required = serializers.FloatField()
    
    # Management of Learning
    avg_student_contribution = serializers.FloatField()
    avg_facilitator_role = serializers.FloatField()
    avg_discussion_encouragement = serializers.FloatField()
    avg_instructional_methods = serializers.FloatField()
    avg_instructional_materials = serializers.FloatField()
    
    # Feedback and Assessment
    avg_clear_communication = serializers.FloatField()
    avg_timely_feedback = serializers.FloatField()
    avg_improvement_feedback = serializers.FloatField()
    
    # Overall Experience
    avg_overall_rating = serializers.FloatField()
    
    # Student Self-Evaluation
    avg_constructive_contribution = serializers.FloatField()
    avg_achieving_outcomes = serializers.FloatField()
    
    # Yes/No percentages
    pct_syllabus_explained = serializers.FloatField()
    pct_delivered_as_outlined = serializers.FloatField()
    pct_grading_criteria_explained = serializers.FloatField()
    pct_exams_related = serializers.FloatField()
    pct_assignments_related = serializers.FloatField()
    pct_lms_resources_useful = serializers.FloatField()
    pct_worthwhile_class = serializers.FloatField()
    pct_would_recommend = serializers.FloatField()
    
    # Text feedback
    text_feedback = serializers.ListField(child=serializers.DictField())


class FeedbackDetailSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_code = serializers.CharField(source='course_assignment.course.code')
    course_name = serializers.CharField(source='course_assignment.course.name')
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'student_name', 'course_code', 'course_name',
            'rating', 'overall_rating', 'submitted_at',
            'suggested_changes', 'best_teaching_aspect',
            'least_teaching_aspect', 'further_comments',
            'sentiment_score', 'sentiment_label', 'emotions'
        ]
    
    def get_student_name(self, obj):
        if obj.is_anonymous:
            return 'Anonymous'
        return obj.student.get_full_name()
