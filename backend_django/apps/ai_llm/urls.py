from django.urls import path
from . import views

app_name = 'ai_llm'

urlpatterns = [
    # APIs del Asistente IA
    path('analyze-user/', views.UserAnalysisView.as_view(), name='analyze_user'),
    path('quiz-recommendations/', views.QuizRecommendationsView.as_view(), name='quiz_recommendations'),
    path('post-quiz-analysis/', views.PostQuizAnalysisView.as_view(), name='post_quiz_analysis'),
] 