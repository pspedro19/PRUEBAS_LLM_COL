from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    start_quiz_session, get_current_question, 
    submit_icfes_answer, get_quiz_feedback,
    get_user_areas_stats, get_dungeon_stats
)

app_name = 'icfes'

router = DefaultRouter()
# Aquí se registrarán los ViewSets cuando se implementen

urlpatterns = [
    # Incluir las rutas del router
    path('', include(router.urls)),
    
    # Rutas específicas del quiz
    path('quiz/start-session/', start_quiz_session, name='start_quiz_session'),
    path('quiz/session/<uuid:session_id>/current-question/', get_current_question, name='get_current_question'),
    path('quiz/session/<uuid:session_id>/submit-answer/', submit_icfes_answer, name='submit_icfes_answer'),
    path('quiz/session/<uuid:session_id>/feedback/', get_quiz_feedback, name='get_quiz_feedback'),
    
    # Estadísticas
    path('areas-stats/', get_user_areas_stats, name='get_user_areas_stats'),
    path('dungeon-stats/', get_dungeon_stats, name='get_dungeon_stats'),
] 