from django.urls import path
from .views import load_training_data

urlpatterns = [
    path('preview-data/', load_training_data, name='preview_data'),
]
