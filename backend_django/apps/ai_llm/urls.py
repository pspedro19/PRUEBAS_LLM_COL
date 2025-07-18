from django.urls import path
from . import views

app_name = 'ai_llm'

urlpatterns = [
    # Modelos de IA
    path('models/', views.AIModelListView.as_view(), name='model-list'),
    path('models/<int:pk>/', views.AIModelDetailView.as_view(), name='model-detail'),
    
    # Conversaciones
    path('conversations/', views.AIConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:uuid>/', views.AIConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<uuid:uuid>/messages/', views.AIMessageListView.as_view(), name='message-list'),
    
    # Templates de prompts
    path('prompt-templates/', views.AIPromptTemplateListView.as_view(), name='prompt-template-list'),
    path('prompt-templates/<int:pk>/', views.AIPromptTemplateDetailView.as_view(), name='prompt-template-detail'),
    
    # Caché
    path('cache/', views.AIResponseCacheListView.as_view(), name='cache-list'),
    path('cache/<str:cache_key>/', views.AIResponseCacheDetailView.as_view(), name='cache-detail'),
    
    # Logs
    path('logs/interactions/', views.AIInteractionLogListView.as_view(), name='interaction-log-list'),
    path('logs/moderation/', views.AIModerationLogListView.as_view(), name='moderation-log-list'),
    
    # Insights
    path('insights/', views.AILearningInsightListView.as_view(), name='insight-list'),
    path('insights/<int:pk>/', views.AILearningInsightDetailView.as_view(), name='insight-detail'),
    
    # Cuotas de uso
    path('quotas/', views.AIUsageQuotaListView.as_view(), name='quota-list'),
    path('quotas/<int:pk>/', views.AIUsageQuotaDetailView.as_view(), name='quota-detail'),
    
    # Métricas de rendimiento
    path('metrics/', views.AIPerformanceMetricListView.as_view(), name='metric-list'),
    path('metrics/<int:pk>/', views.AIPerformanceMetricDetailView.as_view(), name='metric-detail'),
] 