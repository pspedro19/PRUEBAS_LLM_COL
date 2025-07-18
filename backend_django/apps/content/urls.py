"""
URLs para la app de contenido educativo
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'content'

# Router para ViewSets de DRF
router = DefaultRouter()
router.register(r'categories', views.ContentCategoryViewSet, basename='category')
router.register(r'units', views.ContentUnitViewSet, basename='unit')
router.register(r'lessons', views.ContentLessonViewSet, basename='lesson')
router.register(r'progress', views.UserContentProgressViewSet, basename='progress')

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
    
    # URLs adicionales para funcionalidad específica
    path('api/categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('api/units/<uuid:uuid>/', views.ContentUnitDetailView.as_view(), name='unit-detail'),
    path('api/units/<uuid:uuid>/start/', views.StartContentUnitView.as_view(), name='unit-start'),
    path('api/units/<uuid:uuid>/complete/', views.CompleteContentUnitView.as_view(), name='unit-complete'),
    path('api/lessons/<uuid:uuid>/', views.ContentLessonDetailView.as_view(), name='lesson-detail'),
    path('api/lessons/<uuid:uuid>/complete/', views.CompleteLessonView.as_view(), name='lesson-complete'),
    
    # Endpoints de usuario
    path('api/my-progress/', views.MyContentProgressView.as_view(), name='my-progress'),
    path('api/my-bookmarks/', views.MyBookmarksView.as_view(), name='my-bookmarks'),
    path('api/recommend/', views.RecommendedContentView.as_view(), name='recommend'),
    
    # Endpoints de rating y reseñas
    path('api/units/<uuid:uuid>/rate/', views.RateContentUnitView.as_view(), name='rate-unit'),
    path('api/units/<uuid:uuid>/bookmark/', views.BookmarkContentUnitView.as_view(), name='bookmark-unit'),
] 