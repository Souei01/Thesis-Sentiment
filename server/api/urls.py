from django.urls import path
from .views import (
    load_training_data,
    get_student_enrollments,
    submit_feedback,
    get_faculty_courses,
    get_feedback_analytics,
    get_emotion_analytics,
    get_topic_modeling_data,
    trigger_topic_modeling,
    get_available_years,
    export_feedback_pdf,
    get_courses_list,
)

urlpatterns = [
    path('preview-data/', load_training_data, name='preview_data'),
    path('enrollments/', get_student_enrollments, name='student_enrollments'),
    path('feedback/', submit_feedback, name='submit_feedback'),
    path('faculty/courses/', get_faculty_courses, name='faculty_courses'),
    path('feedback/analytics/', get_feedback_analytics, name='feedback_analytics'),
    path('feedback/available-years/', get_available_years, name='available_years'),
    path('feedback/courses/', get_courses_list, name='courses_list'),
    path('feedback/export-pdf/', export_feedback_pdf, name='export_feedback_pdf'),
    path('emotions/analytics/', get_emotion_analytics, name='emotion_analytics'),
    path('topics/', get_topic_modeling_data, name='topic_modeling'),
    path('topics/trigger/', trigger_topic_modeling, name='trigger_topic_modeling'),
]
