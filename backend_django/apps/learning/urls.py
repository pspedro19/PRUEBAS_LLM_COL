"""
URLs para la app Learning
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LearningPathViewSet, UserLessonProgressViewSet

app_name = 'learning'

router = DefaultRouter()
router.register(r'paths', LearningPathViewSet, basename='learningpath')
router.register(r'progress', UserLessonProgressViewSet, basename='lessonprogress')

urlpatterns = [
    path('', include(router.urls)),
    
    # URLs adicionales específicas
    path('path/', LearningPathViewSet.as_view({'get': 'active_path'}), name='active-path'),
    path('generate-path/', LearningPathViewSet.as_view({'post': 'generate_from_quiz'}), name='generate-path'),
    path('templates/', LearningPathViewSet.as_view({'get': 'templates'}), name='templates'),
    path('generate-from-template/', LearningPathViewSet.as_view({'post': 'generate_from_template'}), name='generate-from-template'),
    path('metrics/', LearningPathViewSet.as_view({'get': 'metrics'}), name='metrics'),
    path('start-lesson/', UserLessonProgressViewSet.as_view({'post': 'start_lesson'}), name='start-lesson'),
    path('complete-lesson/', UserLessonProgressViewSet.as_view({'post': 'complete_lesson'}), name='complete-lesson'),
] 