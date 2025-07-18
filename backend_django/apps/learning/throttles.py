"""
Sistema de throttling personalizado para Learning Paths
"""

from rest_framework.throttling import BaseThrottle, UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import hashlib


class LearningPathThrottle(UserRateThrottle):
    """
    Throttling específico para learning paths
    Más permisivo para usuarios regulares
    """
    scope = 'learning_path'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class BattleActionThrottle(BaseThrottle):
    """
    Throttling específico para acciones de batalla
    Limita batallas a una cada 6 horas por path
    """
    
    def allow_request(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Obtener path desde la URL
        path_slug = view.kwargs.get('slug') or view.kwargs.get('pk')
        if not path_slug:
            return True
        
        cache_key = f"battle_throttle_{request.user.id}_{path_slug}"
        
        # Verificar si ya hay una entrada reciente
        last_battle = cache.get(cache_key)
        if last_battle:
            return False
        
        # Registrar la acción por 6 horas
        cache.set(cache_key, timezone.now().isoformat(), 6 * 3600)
        return True
    
    def wait(self):
        return 6 * 3600  # 6 horas


class DailyChallengeThrottle(BaseThrottle):
    """
    Limita challenge diario a uno por día por usuario
    """
    
    def allow_request(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        today = timezone.now().date()
        cache_key = f"daily_challenge_{request.user.id}_{today}"
        
        if cache.get(cache_key):
            return False
        
        # Marcar como usado por 24 horas
        cache.set(cache_key, True, 24 * 3600)
        return True
    
    def wait(self):
        # Tiempo hasta medianoche
        now = timezone.now()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return int((tomorrow - now).total_seconds())


class RewardClaimThrottle(BaseThrottle):
    """
    Throttling para reclamar recompensas
    Previene spam de claims
    """
    
    def allow_request(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        cache_key = f"reward_claim_{request.user.id}"
        
        # Permitir claim cada 5 minutos
        if cache.get(cache_key):
            return False
        
        cache.set(cache_key, True, 5 * 60)  # 5 minutos
        return True
    
    def wait(self):
        return 5 * 60


class AIRecommendationThrottle(BaseThrottle):
    """
    Throttling para recomendaciones de IA
    Costoso computacionalmente, limitar uso
    """
    
    def allow_request(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        cache_key = f"ai_recommendation_{request.user.id}"
        
        # Permitir 3 requests por hora
        attempts = cache.get(cache_key, 0)
        if attempts >= 3:
            return False
        
        cache.set(cache_key, attempts + 1, 3600)  # 1 hora
        return True
    
    def wait(self):
        return 3600  # 1 hora


class ProgressUpdateThrottle(BaseThrottle):
    """
    Throttling para updates de progreso
    Prevenir actualizaciones demasiado frecuentes
    """
    
    def allow_request(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Solo aplicar throttling a POST/PUT/PATCH
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return True
        
        cache_key = f"progress_update_{request.user.id}"
        
        # Permitir update cada 30 segundos
        if cache.get(cache_key):
            return False
        
        cache.set(cache_key, True, 30)
        return True
    
    def wait(self):
        return 30


class LeaderboardThrottle(BaseThrottle):
    """
    Throttling para consultas de leaderboard
    Costoso de calcular, limitar frecuencia
    """
    
    def allow_request(self, request, view):
        cache_key = f"leaderboard_request_{self.get_ident(request)}"
        
        # Permitir 10 requests por minuto
        attempts = cache.get(cache_key, 0)
        if attempts >= 10:
            return False
        
        cache.set(cache_key, attempts + 1, 60)
        return True
    
    def get_ident(self, request):
        """Identificar usuario por IP o user_id"""
        if request.user.is_authenticated:
            return f"user_{request.user.id}"
        
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        remote_addr = request.META.get('REMOTE_ADDR')
        num_proxies = getattr(request, 'num_proxies', 0)
        
        if num_proxies is not None:
            if num_proxies == 0 or xff is None:
                return remote_addr
            
            addrs = xff.split(',')
            client_addr = addrs[-min(num_proxies, len(addrs))]
            return client_addr.strip()
        
        return ''.join(xff.split()) if xff else remote_addr
    
    def wait(self):
        return 60


class HeavyComputationThrottle(BaseThrottle):
    """
    Throttling para operaciones pesadas como reportes PDF
    """
    
    def allow_request(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        cache_key = f"heavy_computation_{request.user.id}"
        
        # Solo 2 operaciones pesadas por hora
        attempts = cache.get(cache_key, 0)
        if attempts >= 2:
            return False
        
        cache.set(cache_key, attempts + 1, 3600)
        return True
    
    def wait(self):
        return 3600


class AdminActionThrottle(BaseThrottle):
    """
    Throttling más permisivo para admins
    """
    
    def allow_request(self, request, view):
        # Sin límites para superusers
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        
        # Límites normales para staff
        if request.user.is_authenticated and request.user.is_staff:
            cache_key = f"admin_action_{request.user.id}"
            attempts = cache.get(cache_key, 0)
            
            if attempts >= 100:  # 100 acciones por hora
                return False
            
            cache.set(cache_key, attempts + 1, 3600)
            return True
        
        # No admin access
        return False
    
    def wait(self):
        return 3600


class PremiumUserThrottle(UserRateThrottle):
    """
    Throttling más generoso para usuarios premium
    """
    scope = 'premium_user'
    
    def allow_request(self, request, view):
        # Verificar si el usuario es premium
        if (request.user.is_authenticated and 
            hasattr(request.user, 'is_premium') and 
            request.user.is_premium):
            
            # Rates más altos para premium
            self.rate = '1000/hour'
        else:
            # Rate normal
            self.rate = '100/hour'
        
        return super().allow_request(request, view)


class SmartThrottle(BaseThrottle):
    """
    Throttling inteligente que ajusta límites según el comportamiento
    """
    
    def allow_request(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_id = request.user.id
        
        # Obtener historial de comportamiento
        behavior_key = f"user_behavior_{user_id}"
        behavior = cache.get(behavior_key, {
            'good_requests': 0,
            'bad_requests': 0,
            'last_reset': timezone.now().isoformat()
        })
        
        # Calcular trust score (0-1)
        total_requests = behavior['good_requests'] + behavior['bad_requests']
        if total_requests > 0:
            trust_score = behavior['good_requests'] / total_requests
        else:
            trust_score = 0.5  # Neutral para nuevos usuarios
        
        # Ajustar límites según trust score
        if trust_score > 0.8:
            max_requests = 200  # Usuario confiable
        elif trust_score > 0.6:
            max_requests = 100  # Usuario normal
        else:
            max_requests = 50   # Usuario sospechoso
        
        # Verificar límite actual
        current_key = f"smart_throttle_{user_id}"
        current_count = cache.get(current_key, 0)
        
        if current_count >= max_requests:
            return False
        
        # Incrementar contador
        cache.set(current_key, current_count + 1, 3600)
        return True
    
    def wait(self):
        return 3600 