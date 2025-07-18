"""
URLs para la app de Learning Paths
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'learning'

# Router para ViewSets de DRF
router = DefaultRouter()
router.register(r'paths', views.LearningPathViewSet, basename='path')
router.register(r'units', views.LearningPathUnitViewSet, basename='unit')
router.register(r'lessons', views.LearningPathLessonViewSet, basename='lesson')
router.register(r'enrollments', views.UserPathEnrollmentViewSet, basename='enrollment')
router.register(r'achievements', views.PathAchievementViewSet, basename='achievement')

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
    
    # URLs de rutas de aprendizaje
    path('api/paths/<slug:slug>/', views.LearningPathDetailView.as_view(), name='path-detail'),
    path('api/paths/<slug:slug>/enroll/', views.EnrollInPathView.as_view(), name='path-enroll'),
    path('api/paths/<slug:slug>/unenroll/', views.UnenrollFromPathView.as_view(), name='path-unenroll'),
    path('api/paths/<slug:slug>/progress/', views.PathProgressView.as_view(), name='path-progress'),
    
    # URLs de unidades y lecciones
    # path('api/units/<uuid:uuid>/', views.LearningPathUnitDetailView.as_view(), name='unit-detail'),
    # path('api/lessons/<uuid:uuid>/', views.LearningPathLessonDetailView.as_view(), name='lesson-detail'),
    path('api/lessons/<uuid:uuid>/start/', views.StartLessonView.as_view(), name='lesson-start'),
    path('api/lessons/<uuid:uuid>/complete/', views.CompleteLessonView.as_view(), name='lesson-complete'),
    # path('api/lessons/<uuid:uuid>/submit-answer/', views.SubmitLessonAnswerView.as_view(), name='lesson-submit'),
    
    # URLs de inscripciones
    # path('api/enrollments/<int:enrollment_id>/pause/', views.PauseEnrollmentView.as_view(), name='enrollment-pause'),
    # path('api/enrollments/<int:enrollment_id>/resume/', views.ResumeEnrollmentView.as_view(), name='enrollment-resume'),
    # path('api/enrollments/<int:enrollment_id>/stats/', views.EnrollmentStatsView.as_view(), name='enrollment-stats'),
    
    # URLs de usuario
    path('api/my-paths/', views.MyLearningPathsView.as_view(), name='my-paths'),
    path('api/my-achievements/', views.MyAchievementsView.as_view(), name='my-achievements'),
    path('api/my-streaks/', views.MyStreaksView.as_view(), name='my-streaks'),
    path('api/leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    
    # URLs de recomendaciones
    path('api/recommended-paths/', views.RecommendedPathsView.as_view(), name='recommended-paths'),
    path('api/next-lesson/', views.NextLessonView.as_view(), name='next-lesson'),
    
    # URLs de reseñas y rating
    path('api/paths/<slug:slug>/review/', views.ReviewPathView.as_view(), name='path-review'),
    path('api/reviews/<int:review_id>/helpful/', views.MarkReviewHelpfulView.as_view(), name='review-helpful'),
] 