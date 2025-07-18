"""
Utilidades de caché Redis para Learning Paths
"""

from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from functools import wraps
import hashlib
import json
import pickle
from typing import Any, Optional, Callable


class CacheKeys:
    """Constantes para keys de caché organizadas"""
    
    # Learning Paths
    LEARNING_PATH_DETAIL = "learning_path_detail_{slug}"
    LEARNING_PATH_LIST = "learning_path_list_{filters_hash}"
    LEARNING_PATH_UNITS = "learning_path_units_{path_id}"
    
    # User Progress
    USER_PROGRESS = "user_progress_{user_id}_{path_id}"
    USER_ENROLLMENTS = "user_enrollments_{user_id}"
    USER_ACHIEVEMENTS = "user_achievements_{user_id}"
    USER_STATS = "user_stats_{user_id}"
    
    # Recommendations
    AI_RECOMMENDATIONS = "ai_recommendations_{user_id}_{date}"
    DAILY_CHALLENGE = "daily_challenge_{date}"
    TRENDING_PATHS = "trending_paths_{date}"
    
    # Performance
    LEADERBOARD = "leaderboard_{type}_{period}"
    POPULAR_PATHS = "popular_paths_{timeframe}"
    
    # Battle System
    BATTLE_SESSION = "battle_session_{session_id}"
    BATTLE_COOLDOWN = "battle_cooldown_{user_id}_{path_id}"


class CacheTimeouts:
    """Timeouts de caché en segundos"""
    
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    
    # Específicos por tipo de data
    LEARNING_PATH_DETAIL = DAY  # Paths no cambian frecuentemente
    LEARNING_PATH_LIST = HOUR   # Lista puede cambiar con nuevos paths
    USER_PROGRESS = MINUTE * 5  # Progreso cambia frecuentemente
    USER_STATS = HOUR           # Stats se actualizan menos
    AI_RECOMMENDATIONS = DAY    # Recomendaciones de IA una vez al día
    LEADERBOARD = HOUR          # Actualizar ranking cada hora
    BATTLE_SESSION = HOUR * 6   # Sesiones de batalla duran hasta 6h


def cache_key_from_request(request, prefix: str, extra_keys: list = None) -> str:
    """
    Genera cache key único basado en request parameters
    """
    key_parts = [prefix]
    
    if hasattr(request, 'user') and request.user.is_authenticated:
        key_parts.append(f"user_{request.user.id}")
    
    # Agregar query parameters relevantes
    if hasattr(request, 'query_params'):
        query_params = dict(request.query_params)
        # Remover parámetros que no afectan cache
        query_params.pop('page', None)
        query_params.pop('page_size', None)
        
        if query_params:
            params_str = json.dumps(query_params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            key_parts.append(f"params_{params_hash}")
    
    if extra_keys:
        key_parts.extend(extra_keys)
    
    return "_".join(key_parts)


def cached_response(timeout: int = CacheTimeouts.HOUR, 
                   key_func: Optional[Callable] = None):
    """
    Decorator para cachear respuestas de view methods
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Generar cache key
            if key_func:
                cache_key = key_func(request, *args, **kwargs)
            else:
                cache_key = cache_key_from_request(
                    request, 
                    f"{func.__name__}", 
                    [str(arg) for arg in args]
                )
            
            # Intentar obtener del cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(self, request, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def cached_queryset(timeout: int = CacheTimeouts.HOUR):
    """
    Decorator para cachear querysets
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generar cache key único para queryset
            cache_key = f"queryset_{func.__name__}_{self.__class__.__name__}"
            
            if hasattr(self, 'request') and self.request.query_params:
                params_hash = hashlib.md5(
                    str(sorted(self.request.query_params.items())).encode()
                ).hexdigest()[:8]
                cache_key += f"_{params_hash}"
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(self, *args, **kwargs)
            
            # Solo cachear si el queryset no está vacío
            if hasattr(result, 'exists') and result.exists():
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


class LearningCacheManager:
    """
    Manager centralizado para operaciones de caché específicas
    """
    
    @staticmethod
    def get_user_progress(user_id: int, path_id: int) -> Optional[dict]:
        """Obtiene progreso del usuario desde caché"""
        cache_key = CacheKeys.USER_PROGRESS.format(user_id=user_id, path_id=path_id)
        return cache.get(cache_key)
    
    @staticmethod
    def set_user_progress(user_id: int, path_id: int, progress_data: dict):
        """Guarda progreso del usuario en caché"""
        cache_key = CacheKeys.USER_PROGRESS.format(user_id=user_id, path_id=path_id)
        cache.set(cache_key, progress_data, CacheTimeouts.USER_PROGRESS)
    
    @staticmethod
    def invalidate_user_progress(user_id: int, path_id: int = None):
        """Invalida caché de progreso del usuario"""
        if path_id:
            cache_key = CacheKeys.USER_PROGRESS.format(user_id=user_id, path_id=path_id)
            cache.delete(cache_key)
        else:
            # Invalidar todo el progreso del usuario (costoso, usar con cuidado)
            pattern = CacheKeys.USER_PROGRESS.format(user_id=user_id, path_id="*")
            # En producción usar Redis SCAN para patterns
            pass
    
    @staticmethod
    def get_daily_challenge(date_str: str = None) -> Optional[dict]:
        """Obtiene reto diario desde caché"""
        if not date_str:
            date_str = timezone.now().date().isoformat()
        
        cache_key = CacheKeys.DAILY_CHALLENGE.format(date=date_str)
        return cache.get(cache_key)
    
    @staticmethod
    def set_daily_challenge(challenge_data: dict, date_str: str = None):
        """Guarda reto diario en caché"""
        if not date_str:
            date_str = timezone.now().date().isoformat()
        
        cache_key = CacheKeys.DAILY_CHALLENGE.format(date=date_str)
        cache.set(cache_key, challenge_data, CacheTimeouts.DAY)
    
    @staticmethod
    def get_ai_recommendations(user_id: int) -> Optional[list]:
        """Obtiene recomendaciones de IA desde caché"""
        date_str = timezone.now().date().isoformat()
        cache_key = CacheKeys.AI_RECOMMENDATIONS.format(user_id=user_id, date=date_str)
        return cache.get(cache_key)
    
    @staticmethod
    def set_ai_recommendations(user_id: int, recommendations: list):
        """Guarda recomendaciones de IA en caché"""
        date_str = timezone.now().date().isoformat()
        cache_key = CacheKeys.AI_RECOMMENDATIONS.format(user_id=user_id, date=date_str)
        cache.set(cache_key, recommendations, CacheTimeouts.AI_RECOMMENDATIONS)
    
    @staticmethod
    def get_battle_cooldown(user_id: int, path_id: int) -> Optional[bool]:
        """Verifica si el usuario está en cooldown de batalla"""
        cache_key = CacheKeys.BATTLE_COOLDOWN.format(user_id=user_id, path_id=path_id)
        return cache.get(cache_key)
    
    @staticmethod
    def set_battle_cooldown(user_id: int, path_id: int, cooldown_seconds: int = 21600):
        """Establece cooldown de batalla (6 horas por defecto)"""
        cache_key = CacheKeys.BATTLE_COOLDOWN.format(user_id=user_id, path_id=path_id)
        cache.set(cache_key, True, cooldown_seconds)
    
    @staticmethod
    def get_leaderboard(leaderboard_type: str, period: str = 'weekly') -> Optional[list]:
        """Obtiene leaderboard desde caché"""
        cache_key = CacheKeys.LEADERBOARD.format(type=leaderboard_type, period=period)
        return cache.get(cache_key)
    
    @staticmethod
    def set_leaderboard(leaderboard_type: str, data: list, period: str = 'weekly'):
        """Guarda leaderboard en caché"""
        cache_key = CacheKeys.LEADERBOARD.format(type=leaderboard_type, period=period)
        cache.set(cache_key, data, CacheTimeouts.LEADERBOARD)


class CacheWarmer:
    """
    Utilidades para pre-calentar caché con datos importantes
    """
    
    @staticmethod
    def warm_popular_paths():
        """Pre-cachea los paths más populares"""
        from .models import LearningPath
        from .serializers import LearningPathListSerializer
        
        popular_paths = LearningPath.objects.filter(
            status='ACTIVE'
        ).order_by('-total_enrollments')[:20]
        
        serializer = LearningPathListSerializer(popular_paths, many=True)
        cache.set(
            CacheKeys.POPULAR_PATHS.format(timeframe='current'),
            serializer.data,
            CacheTimeouts.DAY
        )
    
    @staticmethod
    def warm_trending_paths():
        """Pre-cachea paths en tendencia"""
        from .models import LearningPath
        from django.utils import timezone
        from datetime import timedelta
        
        # Paths con más inscripciones en los últimos 7 días
        week_ago = timezone.now() - timedelta(days=7)
        trending_paths = LearningPath.objects.filter(
            status='ACTIVE',
            enrollments__created_at__gte=week_ago
        ).distinct().order_by('-total_enrollments')[:10]
        
        date_str = timezone.now().date().isoformat()
        cache.set(
            CacheKeys.TRENDING_PATHS.format(date=date_str),
            list(trending_paths.values('uuid', 'name', 'slug')),
            CacheTimeouts.DAY
        ) 