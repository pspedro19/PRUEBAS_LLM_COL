# ================== apps/learning/serializers.py ==================

from rest_framework import serializers
from .models import (
    LearningPath, LearningPathNode, UserPathProgress,
    NodeAttempt, Simulacro, SimulacroSession
)
from apps.users.serializers import UserBasicSerializer

class LearningPathNodeSerializer(serializers.ModelSerializer):
    """Serializer para nodos del learning path"""
    is_unlocked = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    user_best_score = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPathNode
        fields = [
            'id', 'node_type', 'title', 'subtitle', 'icon_emoji',
            'position_x', 'position_y', 'order_index',
            'is_locked', 'is_unlocked', 'is_completed',
            'unlock_requirements', 'questions_count',
            'passing_score', 'base_xp_reward', 'coin_reward',
            'user_best_score'
        ]
    
    def get_is_unlocked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # Lógica para verificar si está desbloqueado
        return not obj.is_locked
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # Verificar si el usuario completó este nodo
        return NodeAttempt.objects.filter(
            user=request.user,
            node=obj,
            passed=True
        ).exists()
    
    def get_user_best_score(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        best_attempt = NodeAttempt.objects.filter(
            user=request.user,
            node=obj
        ).order_by('-score').first()
        return best_attempt.score if best_attempt else None


class LearningPathSerializer(serializers.ModelSerializer):
    """Serializer para Learning Paths"""
    nodes = LearningPathNodeSerializer(many=True, read_only=True)
    user_progress = serializers.SerializerMethodField()
    total_nodes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'name', 'slug', 'description', 'icon_url',
            'color_theme', 'order_index', 'area_evaluacion',
            'estimated_hours', 'total_nodes', 'difficulty_level',
            'is_premium', 'unlock_requirements', 'completion_xp',
            'completion_rewards', 'is_active', 'nodes', 'user_progress'
        ]
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        progress = UserPathProgress.objects.filter(
            user=request.user,
            path=obj
        ).first()
        
        if progress:
            return {
                'completion_percentage': float(progress.completion_percentage),
                'current_node_id': progress.current_node_id,
                'nodes_completed': progress.nodes_completed,
                'total_xp_earned': progress.total_xp_earned,
                'last_activity': progress.last_activity
            }
        return None


class UserPathProgressSerializer(serializers.ModelSerializer):
    """Serializer para el progreso del usuario"""
    path = LearningPathSerializer(read_only=True)
    current_node = LearningPathNodeSerializer(read_only=True)
    
    class Meta:
        model = UserPathProgress
        fields = [
            'id', 'path', 'current_node', 'nodes_completed',
            'nodes_unlocked', 'completion_percentage',
            'total_xp_earned', 'total_coins_earned',
            'best_streak', 'total_time_spent_minutes',
            'average_score', 'perfect_nodes_count',
            'started_at', 'last_activity', 'completed_at'
        ]


class SimulacroSerializer(serializers.ModelSerializer):
    """Serializer para Simulacros"""
    can_access = serializers.SerializerMethodField()
    user_sessions = serializers.SerializerMethodField()
    
    class Meta:
        model = Simulacro
        fields = [
            'id', 'name', 'description', 'code', 'duration_minutes',
            'total_questions', 'question_distribution',
            'difficulty_level', 'is_official', 'is_diagnostic',
            'allows_pause', 'min_level_required', 'is_premium',
            'times_taken', 'average_score', 'can_access',
            'user_sessions'
        ]
    
    def get_can_access(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # Verificar nivel y otros requisitos
        return request.user.level >= obj.min_level_required
    
    def get_user_sessions(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []
        
        sessions = SimulacroSession.objects.filter(
            user=request.user,
            simulacro=obj
        ).order_by('-created_at')[:5]
        
        return [{
            'id': s.id,
            'status': s.status,
            'score_total': s.score_total,
            'percentil_nacional': s.percentil_nacional,
            'completed_at': s.completed_at
        } for s in sessions]


# ================== apps/learning/views.py ==================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import *
from .serializers import *

class LearningPathViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Learning Paths
    Incluye endpoints para listar, detalle y progreso
    """
    serializer_class = LearningPathSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = LearningPath.objects.filter(is_active=True)
        
        # Filtros
        area = self.request.query_params.get('area')
        if area:
            queryset = queryset.filter(area_evaluacion__codigo=area)
        
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Ordenamiento
        queryset = queryset.prefetch_related('nodes').order_by('order_index')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """Obtener el progreso del usuario en todos los paths"""
        progress = UserPathProgress.objects.filter(
            user=request.user
        ).select_related('path', 'current_node')
        
        serializer = UserPathProgressSerializer(progress, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, slug=None):
        """Iniciar un learning path"""
        path = self.get_object()
        
        # Crear o obtener progreso
        progress, created = UserPathProgress.objects.get_or_create(
            user=request.user,
            path=path,
            defaults={
                'current_node': path.nodes.filter(order_index=0).first()
            }
        )
        
        if created:
            # Desbloquear primer nodo
            first_node = path.nodes.filter(parent_node__isnull=True).first()
            if first_node:
                progress.nodes_unlocked = [first_node.id]
                progress.save()
        
        serializer = UserPathProgressSerializer(progress)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, slug=None):
        """Obtener el leaderboard del path"""
        path = self.get_object()
        
        top_users = UserPathProgress.objects.filter(
            path=path
        ).select_related('user').order_by(
            '-completion_percentage',
            '-total_xp_earned'
        )[:20]
        
        leaderboard = [{
            'rank': idx + 1,
            'user': {
                'id': p.user.id,
                'username': p.user.username,
                'avatar_config': p.user.avatar_config
            },
            'completion_percentage': float(p.completion_percentage),
            'total_xp_earned': p.total_xp_earned,
            'perfect_nodes': p.perfect_nodes_count
        } for idx, p in enumerate(top_users)]
        
        return Response(leaderboard)


class LearningPathNodeViewSet(viewsets.ModelViewSet):
    """ViewSet para nodos individuales"""
    serializer_class = LearningPathNodeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LearningPathNode.objects.select_related('path')
    
    @action(detail=True, methods=['post'])
    def start_practice(self, request, pk=None):
        """Iniciar práctica en un nodo"""
        node = self.get_object()
        
        # Verificar que el nodo esté desbloqueado
        progress = UserPathProgress.objects.filter(
            user=request.user,
            path=node.path
        ).first()
        
        if not progress or node.id not in progress.nodes_unlocked:
            return Response(
                {'error': 'Nodo bloqueado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Crear intento
        attempt = NodeAttempt.objects.create(
            user=request.user,
            node=node,
            lives_remaining=node.lives_count
        )
        
        # Obtener preguntas del nodo
        question_ids = node.content.get('question_ids', [])
        # Aquí obtendrías las preguntas reales
        
        return Response({
            'attempt_id': attempt.id,
            'questions': question_ids,
            'lives': node.lives_count,
            'passing_score': node.passing_score,
            'allows_hints': node.allow_hints
        })
    
    @action(detail=True, methods=['post'])
    def complete_practice(self, request, pk=None):
        """Completar práctica de un nodo"""
        node = self.get_object()
        attempt_id = request.data.get('attempt_id')
        score = request.data.get('score', 0)
        
        try:
            attempt = NodeAttempt.objects.get(
                id=attempt_id,
                user=request.user,
                node=node
            )
        except NodeAttempt.DoesNotExist:
            return Response(
                {'error': 'Intento no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Actualizar intento
        attempt.score = score
        attempt.passed = score >= node.passing_score
        attempt.is_perfect = score == 100
        attempt.completed_at = timezone.now()
        
        # Calcular XP y monedas
        xp_earned = node.base_xp_reward
        if attempt.is_perfect:
            xp_earned += node.perfect_bonus_xp
        
        attempt.xp_earned = xp_earned
        attempt.coins_earned = node.coin_reward
        attempt.save()
        
        # Actualizar progreso del usuario
        progress = UserPathProgress.objects.get(
            user=request.user,
            path=node.path
        )
        
        if attempt.passed and node.id not in progress.nodes_completed:
            progress.nodes_completed.append(node.id)
            progress.total_xp_earned += xp_earned
            progress.total_coins_earned += node.coin_reward
            
            # Desbloquear siguientes nodos
            next_nodes = LearningPathNode.objects.filter(
                parent_node=node
            )
            for next_node in next_nodes:
                if next_node.id not in progress.nodes_unlocked:
                    progress.nodes_unlocked.append(next_node.id)
            
            # Actualizar porcentaje de completitud
            total_nodes = node.path.nodes.count()
            progress.completion_percentage = (
                len(progress.nodes_completed) / total_nodes * 100
            )
            
            progress.save()
            
            # Actualizar stats del usuario principal
            request.user.experience_points += xp_earned
            request.user.save()
        
        return Response({
            'passed': attempt.passed,
            'score': score,
            'xp_earned': xp_earned,
            'coins_earned': attempt.coins_earned,
            'is_perfect': attempt.is_perfect,
            'next_nodes_unlocked': len(next_nodes) if attempt.passed else 0
        })


# ================== apps/learning/urls.py ==================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LearningPathViewSet, LearningPathNodeViewSet

router = DefaultRouter()
router.register(r'paths', LearningPathViewSet, basename='learningpath')
router.register(r'nodes', LearningPathNodeViewSet, basename='learningnode')

app_name = 'learning'

urlpatterns = [
    path('', include(router.urls)),
]


# ================== apps/content/serializers.py ==================

from rest_framework import serializers
from .models import (
    EducationalContent, QuestionExplanation,
    UserContentInteraction, ContentRecommendation
)

class EducationalContentSerializer(serializers.ModelSerializer):
    """Serializer para contenido educativo"""
    user_interaction = serializers.SerializerMethodField()
    is_new = serializers.SerializerMethodField()
    
    class Meta:
        model = EducationalContent
        fields = [
            'id', 'uuid', 'title', 'subtitle', 'slug',
            'content_type', 'description', 'summary',
            'url', 'thumbnail_url', 'duration_seconds',
            'difficulty_level', 'tags', 'view_count',
            'average_rating', 'is_premium', 'is_featured',
            'user_interaction', 'is_new', 'published_at'
        ]
    
    def get_user_interaction(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        interaction = UserContentInteraction.objects.filter(
            user=request.user,
            content=obj
        ).first()
        
        if interaction:
            return {
                'has_viewed': interaction.interaction_type == 'view',
                'has_liked': interaction.interaction_type == 'like',
                'is_saved': interaction.interaction_type == 'save',
                'watch_percentage': interaction.watch_percentage,
                'rating': interaction.rating
            }
        return None
    
    def get_is_new(self, obj):
        # Contenido de los últimos 7 días
        from datetime import timedelta
        from django.utils import timezone
        return obj.published_at and obj.published_at > timezone.now() - timedelta(days=7)


class QuestionExplanationSerializer(serializers.ModelSerializer):
    """Serializer para explicaciones de preguntas"""
    related_content = EducationalContentSerializer(many=True, read_only=True)
    helpfulness_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = QuestionExplanation
        fields = [
            'id', 'explanation_type', 'title', 'content',
            'summary', 'steps', 'visual_aids', 'common_mistakes',
            'pro_tips', 'memory_tricks', 'key_concepts',
            'prerequisites', 'related_content', 'is_official',
            'helpful_count', 'not_helpful_count',
            'helpfulness_percentage'
        ]
    
    def get_helpfulness_percentage(self, obj):
        total = obj.helpful_count + obj.not_helpful_count
        if total == 0:
            return None
        return round((obj.helpful_count / total) * 100, 1)


# ================== apps/content/views.py ==================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F
from django.utils import timezone
from .models import *
from .serializers import *

class EducationalContentViewSet(viewsets.ModelViewSet):
    """ViewSet para contenido educativo"""
    serializer_class = EducationalContentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = EducationalContent.objects.filter(
            is_active=True
        ).select_related('area_evaluacion')
        
        # Filtros
        content_type = self.request.query_params.get('type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        area = self.request.query_params.get('area')
        if area:
            queryset = queryset.filter(area_evaluacion__codigo=area)
        
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__contains=[search])
            )
        
        # Ordenamiento
        order = self.request.query_params.get('order', '-published_at')
        if order == 'popular':
            queryset = queryset.order_by('-view_count')
        elif order == 'rating':
            queryset = queryset.order_by('-average_rating')
        else:
            queryset = queryset.order_by(order)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def view(self, request, slug=None):
        """Registrar vista de contenido"""
        content = self.get_object()
        
        # Incrementar contador
        content.view_count = F('view_count') + 1
        content.save()
        
        # Registrar interacción
        interaction, created = UserContentInteraction.objects.update_or_create(
            user=request.user,
            content=content,
            interaction_type='view',
            defaults={
                'time_spent_seconds': 0
            }
        )
        
        return Response({'status': 'viewed'})
    
    @action(detail=True, methods=['post'])
    def rate(self, request, slug=None):
        """Calificar contenido"""
        content = self.get_object()
        rating = request.data.get('rating')
        
        if not rating or not (1 <= rating <= 5):
            return Response(
                {'error': 'Rating debe estar entre 1 y 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar o crear interacción
        interaction, created = UserContentInteraction.objects.update_or_create(
            user=request.user,
            content=content,
            interaction_type='rating',
            defaults={'rating': rating}
        )
        
        # Recalcular rating promedio
        ratings = UserContentInteraction.objects.filter(
            content=content,
            interaction_type='rating',
            rating__isnull=False
        )
        
        content.rating_count = ratings.count()
        content.average_rating = ratings.aggregate(
            avg=Avg('rating')
        )['avg'] or 0
        content.save()
        
        return Response({
            'rating': rating,
            'average_rating': float(content.average_rating),
            'total_ratings': content.rating_count
        })
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Obtener recomendaciones personalizadas"""
        recommendations = ContentRecommendation.objects.filter(
            user=request.user,
            is_dismissed=False
        ).select_related('content').order_by('-priority', '-created_at')[:10]
        
        data = []
        for rec in recommendations:
            content_data = EducationalContentSerializer(
                rec.content,
                context={'request': request}
            ).data
            
            data.append({
                'id': rec.id,
                'content': content_data,
                'reason': rec.get_reason_display(),
                'reason_detail': rec.reason_detail,
                'priority': rec.priority
            })
        
        # Marcar como vistas
        recommendations.update(is_seen=True, seen_at=timezone.now())
        
        return Response(data)


# ================== Agregar a urls.py principal ==================
# En backend_django/urls.py agregar:

# from django.urls import path, include

# urlpatterns = [
#     # ... otras urls ...
#     path('api/learning/', include('apps.learning.urls')),
#     path('api/content/', include('apps.content.urls')),
# ]
