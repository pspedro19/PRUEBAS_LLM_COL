"""
URLs para la app Learning
"""
from django.urls import path
from . import views, learning_path_views

app_name = 'learning'

urlpatterns = [
    path('generate-path/', learning_path_views.generate_learning_path, name='generate_learning_path'),
    path('path/', learning_path_views.get_learning_path, name='get_learning_path'),
    path('path-test/', learning_path_views.get_learning_path_test, name='get_learning_path_test'),  # ✅ ENDPOINT TEMPORAL
    path('personalization-config/', views.get_personalization_config, name='get_personalization_config'),
] 