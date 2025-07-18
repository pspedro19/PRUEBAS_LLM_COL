"""
Permisos personalizados para Learning Paths
"""

from rest_framework import permissions
from django.utils import timezone
from datetime import timedelta


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permite solo al propietario editar su progreso/data
    """
    
    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permisos de escritura solo para el propietario
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsEnrolledInPath(permissions.BasePermission):
    """
    Permite acceso solo si el usuario está inscrito en el path
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Para objetos que tienen learning_path
        if hasattr(obj, 'learning_path'):
            from .models import UserPathEnrollment
            return UserPathEnrollment.objects.filter(
                user=request.user,
                learning_path=obj.learning_path,
                status='ACTIVE'
            ).exists()
        
        # Para LearningPath directamente
        if hasattr(obj, 'enrollments'):
            from .models import UserPathEnrollment
            return UserPathEnrollment.objects.filter(
                user=request.user,
                learning_path=obj,
                status='ACTIVE'
            ).exists()
            
        return False


class CanStartBattle(permissions.BasePermission):
    """
    Permite iniciar batallas solo si se cumplen condiciones
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Verificar si está inscrito
        from .models import UserPathEnrollment
        enrollment = UserPathEnrollment.objects.filter(
            user=request.user,
            learning_path=obj,
            status='ACTIVE'
        ).first()
        
        if not enrollment:
            return False
            
        # Verificar que no tenga una batalla activa
        if hasattr(enrollment, 'active_battle_session'):
            return False
            
        # Verificar cooldown de batallas (6 horas)
        if enrollment.last_battle_at:
            cooldown = timezone.now() - enrollment.last_battle_at
            if cooldown < timedelta(hours=6):
                return False
                
        return True


class CanClaimRewards(permissions.BasePermission):
    """
    Permite reclamar recompensas solo si hay recompensas pendientes
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        from .models import UserPathEnrollment
        enrollment = UserPathEnrollment.objects.filter(
            user=request.user,
            learning_path=obj,
            status='ACTIVE'
        ).first()
        
        if not enrollment:
            return False
            
        # Verificar que tenga recompensas pendientes
        return enrollment.unclaimed_rewards > 0


class RateLimitByUserAndPath(permissions.BasePermission):
    """
    Limita acciones por usuario y path para evitar abuse
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Implementar rate limiting básico en cache
        # (Redis cache se configurará después)
        return True


class DailyActionLimit(permissions.BasePermission):
    """
    Limita ciertas acciones a una vez por día
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Verificar límite diario para acciones específicas
        from django.core.cache import cache
        
        cache_key = f"daily_action_{request.user.id}_{view.action}_{timezone.now().date()}"
        
        if cache.get(cache_key):
            return False
            
        return True


class AdminOrSuperUserOnly(permissions.BasePermission):
    """
    Permite acceso solo a admins o superusers
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser
        )


class HasMinimumLevel(permissions.BasePermission):
    """
    Requiere nivel mínimo del usuario
    """
    
    def __init__(self, min_level=1):
        self.min_level = min_level
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Verificar nivel del usuario
        return request.user.level >= self.min_level


class InActiveHours(permissions.BasePermission):
    """
    Permite acceso solo en horas activas (para endpoints pesados)
    """
    
    def has_permission(self, request, view):
        current_hour = timezone.now().hour
        # Permitir entre 6 AM y 11 PM
        return 6 <= current_hour <= 23 