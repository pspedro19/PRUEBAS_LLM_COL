"""
URLs para la app de Learning Paths
"""

from django.urls import path
from .learning_path_views import get_learning_path, generate_learning_path

app_name = 'learning'

urlpatterns = [
    # URLs para Learning Path IA
    path('path/', get_learning_path, name='get_learning_path'),
    path('generate-path/', generate_learning_path, name='generate_learning_path'),
] 