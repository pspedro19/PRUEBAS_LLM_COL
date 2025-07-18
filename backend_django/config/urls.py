"""
URL Configuration para Ciudadela del Conocimiento ICFES
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API endpoints (compatible with frontend)
    path('api/auth/', include('apps.users.urls')),
    path('api/questions/', include('apps.questions.urls')),
    path('api/icfes/', include('apps.icfes.urls')),
    path('api/gamification/', include('apps.gamification.urls')),
    path('api/jarvis/', include('apps.jarvis.urls')),
    path('api/assessments/', include('apps.assessments.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/schools/', include('apps.schools.urls')),
    path('api/content/', include('apps.content.urls')),
    # path('api/learning/', include('apps.learning.urls')),
    
    # Health check
    path('health/', include('apps.users.urls', namespace='health')),  # Reutilizamos el health check de users
]

# Configuración para servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalización del admin
admin.site.site_header = 'Ciudadela del Conocimiento ICFES'
admin.site.site_title = 'ICFES Admin'
admin.site.index_title = 'Panel de Administración' 