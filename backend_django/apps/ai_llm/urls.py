"""
URLs para el sistema AI/LLM
Incluye todas las funcionalidades de IA organizadas por categoría
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Vistas principales de explicaciones e IA
    ExplanationView, ConversationView, MessageView, UserAnalysisView,
    QuotaStatusView, BatchExplanationView,
    
    # Vistas de compatibilidad (existentes)
    QuizRecommendationsView, PostQuizAnalysisView,
    
    # Vistas auxiliares
    ai_models_list, prompt_templates_list
)

app_name = 'ai_llm'

# Router para posibles ViewSets futuros
router = DefaultRouter()

urlpatterns = [
    # ===== EXPLICACIONES E IA =====
    
    # Explicaciones inteligentes
    path('explanation/', ExplanationView.as_view(), name='explanation'),
    path('explanation/batch/', BatchExplanationView.as_view(), name='explanation_batch'),
    
    # Conversaciones con IA
    path('conversation/', ConversationView.as_view(), name='conversation'),
    path('conversation/message/', MessageView.as_view(), name='conversation_message'),
    
    # Análisis de usuario con IA
    path('analysis/user/', UserAnalysisView.as_view(), name='user_analysis'),
    
    # ===== GESTIÓN DE CUOTAS Y LÍMITES =====
    
    # Estado de cuotas del usuario
    path('quota/status/', QuotaStatusView.as_view(), name='quota_status'),
    
    # ===== UTILIDADES Y CONFIGURACIÓN =====
    
    # Listado de modelos disponibles
    path('models/', ai_models_list, name='models_list'),
    
    # Listado de templates de prompts
    path('templates/', prompt_templates_list, name='templates_list'),
    
    # ===== VISTAS DE COMPATIBILIDAD (EXISTENTES) =====
    
    # Análisis de usuario (versión original para compatibilidad)
    path('analyze-user/', UserAnalysisView.as_view(), name='analyze_user_legacy'),
    
    # Recomendaciones de quiz
    path('quiz-recommendations/', QuizRecommendationsView.as_view(), name='quiz_recommendations'),
    
    # Análisis post-quiz
    path('post-quiz-analysis/', PostQuizAnalysisView.as_view(), name='post_quiz_analysis'),
    
    # ===== RUTAS DEL ROUTER =====
    path('', include(router.urls)),
]

# URLs adicionales organizadas por funcionalidad
conversation_patterns = [
    path('conversations/', ConversationView.as_view(), name='conversation_list'),
    path('conversations/create/', ConversationView.as_view(), name='conversation_create'),
    path('conversations/<uuid:conversation_id>/messages/', MessageView.as_view(), name='conversation_messages'),
]

explanation_patterns = [
    path('explanations/request/', ExplanationView.as_view(), name='explanation_request'),
    path('explanations/batch/', BatchExplanationView.as_view(), name='explanation_batch'),
]

analysis_patterns = [
    path('analysis/user/complete/', UserAnalysisView.as_view(), name='user_analysis_complete'),
    path('analysis/user/performance/', UserAnalysisView.as_view(), name='user_analysis_performance'),
    path('analysis/user/patterns/', UserAnalysisView.as_view(), name='user_analysis_patterns'),
]

# Patrones de URL versioned (para futuras versiones API)
v1_patterns = [
    path('v1/ai/', include([
        path('explain/', ExplanationView.as_view(), name='v1_explain'),
        path('analyze/', UserAnalysisView.as_view(), name='v1_analyze'),
        path('chat/', ConversationView.as_view(), name='v1_chat'),
        path('quota/', QuotaStatusView.as_view(), name='v1_quota'),
    ])),
]

# URLs para administración y debugging (solo en desarrollo)
admin_patterns = [
    # Estas URLs solo estarían disponibles para staff/superusers
    path('admin/models/', ai_models_list, name='admin_models'),
    path('admin/templates/', prompt_templates_list, name='admin_templates'),
]

# Agregar patrones opcionales a urlpatterns principal si se necesitan
# urlpatterns += conversation_patterns
# urlpatterns += explanation_patterns  
# urlpatterns += analysis_patterns
# urlpatterns += v1_patterns

# En desarrollo, agregar patrones de admin
# if settings.DEBUG:
#     urlpatterns += admin_patterns 