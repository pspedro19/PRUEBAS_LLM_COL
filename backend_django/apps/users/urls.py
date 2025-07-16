from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, CustomTokenObtainPairView, LogoutView,
    UserProfileView, PasswordChangeView, SchoolListView,
    UniversityListView, UserStatsView, add_experience,
    health_check, CheckUsernameView, CheckEmailView,
    complete_assessment
)

app_name = 'users'

router = DefaultRouter()
# Aquí se registrarán los ViewSets cuando se implementen

urlpatterns = [
    # Autenticación
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Perfil de usuario
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('stats/', UserStatsView.as_view(), name='user_stats'),
    path('add-experience/', add_experience, name='add_experience'),
    path('complete-assessment/', complete_assessment, name='complete_assessment'),
    
    # Validaciones
    path('check-username/', CheckUsernameView.as_view(), name='check_username'),
    path('check-email/', CheckEmailView.as_view(), name='check_email'),
    
    # Datos auxiliares
    path('schools/', SchoolListView.as_view(), name='schools'),
    path('universities/', UniversityListView.as_view(), name='universities'),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Router URLs
    path('', include(router.urls)),
] 