"""
Vistas optimizadas para Learning Paths con funcionalidad avanzada
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, Sum, Prefetch, F
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import random
from datetime import timedelta, date
import uuid as uuid_lib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

from .models import (
    LearningPath, LearningPathUnit, LearningPathLesson,
    UserPathEnrollment, UserLessonProgress, PathAchievement,
    UserPathAchievement, LearningPathReview
)
from .serializers import (
    OptimizedLearningPathSerializer, OptimizedLearningPathUnitSerializer, 
    OptimizedLearningPathLessonSerializer, UserPathEnrollmentDetailSerializer,
    LearningPathListSerializer, PathAchievementSerializer, UserPathAchievementSerializer,
    LearningPathReviewSerializer
)
from .permissions import (
    IsOwnerOrReadOnly, IsEnrolledInPath, CanStartBattle, CanClaimRewards,
    DailyActionLimit, HasMinimumLevel
)
from .throttles import (
    LearningPathThrottle, BattleActionThrottle, DailyChallengeThrottle,
    RewardClaimThrottle, AIRecommendationThrottle, HeavyComputationThrottle
)
from .filters import (
    LearningPathFilter, UserPathEnrollmentFilter, UserLessonProgressFilter
)
from .pagination import (
    LearningPathPagination, StandardResultsSetPagination, 
    ProgressPagination, LargeResultsSetPagination
)
from .cache import LearningCacheManager, cached_response, CacheTimeouts


@extend_schema_view(
    list=extend_schema(
        summary="Lista de Learning Paths",
        description="Obtiene la lista de rutas de aprendizaje con filtros avanzados",
        parameters=[
            OpenApiParameter("difficulty", OpenApiTypes.STR, description="Filtrar por dificultad"),
            OpenApiParameter("path_type", OpenApiTypes.STR, description="Filtrar por tipo de path"),
            OpenApiParameter("trending", OpenApiTypes.BOOL, description="Solo paths en tendencia"),
            OpenApiParameter("recommended_for_user", OpenApiTypes.BOOL, description="Paths recomendados"),
        ]
    ),
    retrieve=extend_schema(
        summary="Detalle de Learning Path",
        description="Obtiene información detallada de una ruta de aprendizaje"
    )
)
class LearningPathViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet optimizado para rutas de aprendizaje con endpoints especiales
    """
    
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]
    throttle_classes = [LearningPathThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LearningPathFilter
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['name', 'difficulty_level', 'average_rating', 'total_enrollments', 'created_at']
    ordering = ['-is_featured', '-average_rating']
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'list':
            return LearningPathListSerializer
        return OptimizedLearningPathSerializer
    
    def get_pagination_class(self):
        """Paginación específica para learning paths"""
        return LearningPathPagination
    
    def get_queryset(self):
        """
        Queryset optimizado con select_related y prefetch_related
        """
        queryset = LearningPath.objects.select_related(
            'category'
        ).prefetch_related(
            'prerequisite_paths',
            Prefetch(
                'units',
                queryset=LearningPathUnit.objects.select_related().prefetch_related('lessons')
            )
        ).filter(status='ACTIVE')
        
        # Optimización adicional para vistas detalladas
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'reviews__user',
                'achievements'
            )
        
        return queryset.annotate(
            completion_rate=Count('enrollments', filter=Q(enrollments__status='COMPLETED')) * 100.0 / Count('enrollments')
        )
    
    @cached_response(timeout=CacheTimeouts.LEARNING_PATH_LIST)
    def list(self, request, *args, **kwargs):
        """Lista optimizada con caché"""
        return super().list(request, *args, **kwargs)
    
    @cached_response(timeout=CacheTimeouts.LEARNING_PATH_DETAIL)
    def retrieve(self, request, *args, **kwargs):
        """Detalle optimizado con caché"""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Iniciar Boss Battle",
        description="Inicia una batalla de jefe en el learning path",
        responses={200: "Batalla iniciada exitosamente", 400: "No se puede iniciar batalla"}
    )
    @action(
        detail=True, 
        methods=['post'],
        permission_classes=[IsAuthenticated, IsEnrolledInPath, CanStartBattle],
        throttle_classes=[BattleActionThrottle]
    )
    def start_battle(self, request, slug=None):
        """
        Endpoint especial: Iniciar un boss battle
        """
        learning_path = self.get_object()
        user = request.user
        
        # Verificar cooldown de batalla
        if LearningCacheManager.get_battle_cooldown(user.id, learning_path.id):
            return Response(
                {"error": "Debes esperar antes de iniciar otra batalla"},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Obtener inscripción del usuario
        enrollment = get_object_or_404(
            UserPathEnrollment,
            user=user,
            learning_path=learning_path,
            status='ACTIVE'
        )
        
        # Verificar que tenga progreso suficiente (al menos 70%)
        if enrollment.overall_progress_percentage < 70:
            return Response(
                {"error": "Necesitas al menos 70% de progreso para enfrentar al jefe"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generar batalla (seleccionar preguntas más difíciles)
        difficult_lessons = LearningPathLesson.objects.filter(
            path_unit__learning_path=learning_path
        ).select_related('icfes_question').filter(
            icfes_question__nivel_dificultad__gte=4
        )[:10]
        
        battle_data = {
            'battle_id': str(uuid_lib.uuid4()),
            'learning_path_slug': learning_path.slug,
            'questions': [
                {
                    'lesson_uuid': str(lesson.uuid),
                    'question_text': lesson.icfes_question.pregunta_texto if lesson.icfes_question else lesson.title,
                    'difficulty': lesson.icfes_question.nivel_dificultad if lesson.icfes_question else 4,
                    'xp_reward': lesson.xp_reward * 2  # Doble XP en batallas
                }
                for lesson in difficult_lessons
            ],
            'total_xp_possible': sum(lesson.xp_reward * 2 for lesson in difficult_lessons),
            'time_limit_minutes': 45,
            'started_at': timezone.now().isoformat()
        }
        
        # Guardar sesión de batalla en caché
        cache_key = f"battle_session_{battle_data['battle_id']}"
        cache.set(cache_key, battle_data, CacheTimeouts.BATTLE_SESSION)
        
        # Establecer cooldown
        LearningCacheManager.set_battle_cooldown(user.id, learning_path.id)
        
        # Actualizar último intento de batalla
        enrollment.last_battle_at = timezone.now()
        enrollment.save(update_fields=['last_battle_at'])
        
        return Response({
            "message": "¡Batalla iniciada! ¡Prepárate para enfrentar al jefe!",
            "battle_data": battle_data,
            "tips": [
                "Las batallas otorgan doble XP",
                "Tienes 45 minutos para completarla",
                "Solo puedes hacer una batalla cada 6 horas"
            ]
        })
    
    @extend_schema(
        summary="Reclamar Recompensas",
        description="Reclama recompensas pendientes del learning path",
        responses={200: "Recompensas reclamadas", 400: "No hay recompensas disponibles"}
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, IsEnrolledInPath, CanClaimRewards],
        throttle_classes=[RewardClaimThrottle]
    )
    def claim_rewards(self, request, slug=None):
        """
        Endpoint especial: Reclamar recompensas
        """
        learning_path = self.get_object()
        user = request.user
        
        enrollment = get_object_or_404(
            UserPathEnrollment,
            user=user,
            learning_path=learning_path
        )
        
        if enrollment.unclaimed_rewards <= 0:
            return Response(
                {"error": "No tienes recompensas pendientes"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calcular recompensas basadas en progreso
        rewards = {
            'xp_gained': 0,
            'achievements_unlocked': [],
            'items_received': [],
            'vitality_restored': 0
        }
        
        # XP por milestones completados
        progress_milestones = [25, 50, 75, 100]
        current_progress = enrollment.overall_progress_percentage
        
        for milestone in progress_milestones:
            if current_progress >= milestone:
                milestone_xp = learning_path.total_xp_available * milestone // 400  # 25% del total por milestone
                rewards['xp_gained'] += milestone_xp
        
        # Verificar achievements nuevos
        path_achievements = PathAchievement.objects.filter(
            learning_path=learning_path,
            is_active=True
        ).exclude(
            id__in=UserPathAchievement.objects.filter(
                user=user,
                achievement__learning_path=learning_path
            ).values_list('achievement_id', flat=True)
        )
        
        for achievement in path_achievements:
            # Lógica simplificada para otorgar achievements
            if self._check_achievement_criteria(achievement, enrollment):
                UserPathAchievement.objects.create(
                    user=user,
                    achievement=achievement,
                    earned_at=timezone.now(),
                    progress_when_earned=current_progress
                )
                rewards['achievements_unlocked'].append({
                    'name': achievement.name,
                    'description': achievement.description,
                    'rarity': achievement.rarity_level,
                    'icon': achievement.icon_emoji
                })
        
        # Restaurar vitalidad basada en progreso
        if current_progress >= 50:
            rewards['vitality_restored'] = min(5, enrollment.unclaimed_rewards)
        
        # Items especiales por completar unidades
        completed_units = UserLessonProgress.objects.filter(
            user=user,
            path_lesson__path_unit__learning_path=learning_path,
            status='COMPLETED'
        ).values('path_lesson__path_unit').distinct().count()
        
        if completed_units >= 3:
            rewards['items_received'].append({
                'name': 'Pergamino de Sabiduría',
                'description': 'Reduce tiempo de cooldown de batallas en 1 hora',
                'type': 'consumable'
            })
        
        # Actualizar usuario
        user.experience_points = F('experience_points') + rewards['xp_gained']
        user.save(update_fields=['experience_points'])
        
        # Limpiar recompensas reclamadas
        enrollment.unclaimed_rewards = 0
        enrollment.save(update_fields=['unclaimed_rewards'])
        
        # Invalidar caché del usuario
        LearningCacheManager.invalidate_user_progress(user.id, learning_path.id)
        
        return Response({
            "message": "¡Recompensas reclamadas exitosamente!",
            "rewards": rewards,
            "user_level": user.level,
            "user_xp": user.experience_points
        })
    
    def _check_achievement_criteria(self, achievement, enrollment):
        """Helper para verificar criterios de achievements"""
        if achievement.achievement_type == 'COMPLETION':
            return enrollment.overall_progress_percentage >= achievement.required_progress_percentage
        elif achievement.achievement_type == 'STREAK':
            return enrollment.current_streak_days >= achievement.required_streak_days
        elif achievement.achievement_type == 'SCORE':
            avg_score = UserLessonProgress.objects.filter(
                user=enrollment.user,
                path_lesson__path_unit__learning_path=enrollment.learning_path,
                status='COMPLETED'
            ).aggregate(avg_score=Avg('final_score'))['avg_score'] or 0
            return avg_score >= achievement.required_score
        return False
    
    @extend_schema(
        summary="Paths Recomendados por IA",
        description="Obtiene paths recomendados personalizados usando IA",
        responses={200: "Lista de paths recomendados"}
    )
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        throttle_classes=[AIRecommendationThrottle],
        pagination_class=StandardResultsSetPagination
    )
    def recommended(self, request):
        """
        Endpoint especial: Paths recomendados por IA
        """
        user = request.user
        
        # Intentar obtener recomendaciones del caché
        recommendations = LearningCacheManager.get_ai_recommendations(user.id)
        
        if recommendations is None:
            # Generar recomendaciones usando algoritmo básico de IA
            recommendations = self._generate_ai_recommendations(user)
            LearningCacheManager.set_ai_recommendations(user.id, recommendations)
        
        # Obtener los paths recomendados
        recommended_paths = LearningPath.objects.filter(
            id__in=[r['path_id'] for r in recommendations]
        ).select_related('category')
        
        # Ordenar según el score de recomendación
        path_scores = {r['path_id']: r['score'] for r in recommendations}
        recommended_paths = sorted(
            recommended_paths, 
            key=lambda p: path_scores.get(p.id, 0), 
            reverse=True
        )
        
        serializer = LearningPathListSerializer(
            recommended_paths,
            many=True,
            context={'request': request}
        )
        
        return Response({
            "message": "Recomendaciones personalizadas generadas",
            "algorithm_version": "1.2",
            "recommendations": [
                {
                    **path_data,
                    "recommendation_score": path_scores.get(path_data['uuid'], 0),
                    "reason": next(
                        (r['reason'] for r in recommendations if r['path_id'] == path_data['uuid']), 
                        "Basado en tu perfil de aprendizaje"
                    )
                }
                for path_data in serializer.data
            ]
        })
    
    def _generate_ai_recommendations(self, user):
        """
        Algoritmo básico de recomendación por IA
        En producción sería más sofisticado con ML
        """
        user_level = getattr(user, 'level', 1)
        user_hero_class = getattr(user, 'hero_class', 'F')
        
        # Obtener historial del usuario
        completed_paths = UserPathEnrollment.objects.filter(
            user=user,
            status='COMPLETED'
        ).values_list('learning_path_id', flat=True)
        
        enrolled_paths = UserPathEnrollment.objects.filter(
            user=user
        ).values_list('learning_path_id', flat=True)
        
        # Paths candidatos
        candidate_paths = LearningPath.objects.filter(
            status='ACTIVE',
            minimum_level__lte=user_level + 2
        ).exclude(
            id__in=enrolled_paths
        ).annotate(
            avg_rating=Avg('reviews__overall_rating'),
            popularity_score=Count('enrollments')
        )
        
        recommendations = []
        
        for path in candidate_paths[:20]:  # Limitar para performance
            score = 0
            reason = ""
            
            # Factor 1: Nivel apropiado (40% del score)
            level_diff = abs(path.minimum_level - user_level)
            if level_diff <= 1:
                score += 40
                reason = "Perfecto para tu nivel actual"
            elif level_diff <= 2:
                score += 30
                reason = "Ligeramente desafiante para tu nivel"
            else:
                score += 10
                reason = "Desafío avanzado"
            
            # Factor 2: Rating del path (30% del score)
            if path.avg_rating:
                score += (path.avg_rating / 5.0) * 30
            
            # Factor 3: Popularidad (20% del score)
            if path.popularity_score > 0:
                popularity_factor = min(path.popularity_score / 100.0, 1.0)
                score += popularity_factor * 20
            
            # Factor 4: Tipo de path según hero class (10% del score)
            if user_hero_class in ['A', 'S', 'S+'] and path.difficulty_level >= 4:
                score += 10
                reason += " (recomendado para heroes avanzados)"
            elif user_hero_class in ['F', 'E', 'D'] and path.difficulty_level <= 2:
                score += 10
                reason += " (ideal para principiantes)"
            
            recommendations.append({
                'path_id': path.id,
                'score': round(score, 2),
                'reason': reason
            })
        
        # Ordenar por score y tomar top 10
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:10]
    
    @extend_schema(
        summary="Reto Diario",
        description="Obtiene el reto diario personalizado",
        responses={200: "Reto diario generado"}
    )
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, DailyActionLimit],
        throttle_classes=[DailyChallengeThrottle]
    )
    def daily_challenge(self, request):
        """
        Endpoint especial: Reto diario
        """
        user = request.user
        today = timezone.now().date()
        
        # Intentar obtener challenge del caché
        challenge_data = LearningCacheManager.get_daily_challenge(today.isoformat())
        
        if challenge_data is None:
            # Generar nuevo challenge diario
            challenge_data = self._generate_daily_challenge(user, today)
            LearningCacheManager.set_daily_challenge(challenge_data, today.isoformat())
        
        # Verificar si el usuario ya completó el challenge
        cache_key = f"daily_challenge_completed_{user.id}_{today}"
        already_completed = cache.get(cache_key, False)
        
        challenge_data['user_completed'] = already_completed
        challenge_data['rewards_available'] = not already_completed
        
        return Response({
            "message": "Reto diario disponible",
            "challenge": challenge_data
        })
    
    def _generate_daily_challenge(self, user, date):
        """Genera un reto diario personalizado"""
        user_level = getattr(user, 'level', 1)
        
        # Tipos de challenges rotativos por día de la semana
        challenge_types = [
            'speed_run',      # Lunes
            'perfect_score',  # Martes
            'endurance',      # Miércoles
            'exploration',    # Jueves
            'streak_master',  # Viernes
            'boss_battle',    # Sábado
            'community'       # Domingo
        ]
        
        challenge_type = challenge_types[date.weekday()]
        
        # Configuración base del challenge
        base_xp = user_level * 10
        base_vitality = 2
        
        if challenge_type == 'speed_run':
            return {
                'type': 'speed_run',
                'title': '🏃‍♂️ Velocidad Extrema',
                'description': 'Completa 5 lecciones en menos de 15 minutos',
                'requirements': {
                    'lessons_to_complete': 5,
                    'time_limit_minutes': 15,
                    'min_score_per_lesson': 70
                },
                'rewards': {
                    'xp': base_xp * 2,
                    'vitality': base_vitality,
                    'badge': 'Rayo Velocidad'
                },
                'expires_at': (timezone.now() + timedelta(days=1)).isoformat()
            }
        
        elif challenge_type == 'perfect_score':
            return {
                'type': 'perfect_score',
                'title': '🎯 Precisión Perfecta',
                'description': 'Obtén puntuación perfecta (100%) en 3 lecciones',
                'requirements': {
                    'lessons_to_complete': 3,
                    'required_score': 100,
                    'max_attempts_per_lesson': 1
                },
                'rewards': {
                    'xp': base_xp * 3,
                    'vitality': base_vitality + 1,
                    'badge': 'Maestro Perfecto'
                },
                'expires_at': (timezone.now() + timedelta(days=1)).isoformat()
            }
        
        # Más tipos de challenges...
        else:
            return {
                'type': 'exploration',
                'title': '🗺️ Explorador del Conocimiento',
                'description': 'Explora 3 paths diferentes y completa al menos 1 lección en cada uno',
                'requirements': {
                    'different_paths': 3,
                    'lessons_per_path': 1,
                    'min_score': 60
                },
                'rewards': {
                    'xp': base_xp * 1.5,
                    'vitality': base_vitality,
                    'badge': 'Explorador'
                },
                'expires_at': (timezone.now() + timedelta(days=1)).isoformat()
            }


class LearningPathUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para unidades de rutas de aprendizaje"""
    serializer_class = OptimizedLearningPathUnitSerializer
    lookup_field = 'uuid'
    
    def get_queryset(self):
        return LearningPathUnit.objects.filter(is_active=True)


class LearningPathLessonViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para lecciones de rutas de aprendizaje"""
    serializer_class = OptimizedLearningPathLessonSerializer
    lookup_field = 'uuid'
    
    def get_queryset(self):
        return LearningPathLesson.objects.filter(is_active=True)


class UserPathEnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet para inscripciones de usuarios"""
    serializer_class = UserPathEnrollmentDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserPathEnrollment.objects.filter(user=self.request.user)


class PathAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para logros de rutas"""
    serializer_class = PathAchievementSerializer
    
    def get_queryset(self):
        return PathAchievement.objects.filter(is_active=True, is_secret=False)


class LearningPathDetailView(generics.RetrieveAPIView):
    """Vista detallada de una ruta de aprendizaje"""
    queryset = LearningPath.objects.filter(status='ACTIVE')
    serializer_class = OptimizedLearningPathSerializer
    lookup_field = 'slug'


class EnrollInPathView(generics.CreateAPIView):
    """Vista para inscribirse en una ruta de aprendizaje"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, slug):
        learning_path = get_object_or_404(LearningPath, slug=slug, status='ACTIVE')
        
        # Verificar si el usuario puede acceder a esta ruta
        if not learning_path.is_accessible_for_user(request.user):
            return Response(
                {'error': 'No cumples los requisitos para esta ruta'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar si ya está inscrito
        enrollment, created = UserPathEnrollment.objects.get_or_create(
            user=request.user,
            learning_path=learning_path,
            defaults={
                'status': 'ACTIVE',
                'daily_goal_minutes': request.data.get('daily_goal_minutes', 30)
            }
        )
        
        if not created and enrollment.status in ['DROPPED', 'EXPIRED']:
            enrollment.status = 'ACTIVE'
            enrollment.save()
        
        serializer = UserPathEnrollmentDetailSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnenrollFromPathView(generics.UpdateAPIView):
    """Vista para desincribirse de una ruta de aprendizaje"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, slug):
        learning_path = get_object_or_404(LearningPath, slug=slug)
        enrollment = get_object_or_404(
            UserPathEnrollment, 
            user=request.user, 
            learning_path=learning_path
        )
        
        enrollment.status = 'DROPPED'
        enrollment.save()
        
        serializer = UserPathEnrollmentDetailSerializer(enrollment)
        return Response(serializer.data)


class PathProgressView(generics.RetrieveAPIView):
    """Vista del progreso en una ruta específica"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, slug):
        learning_path = get_object_or_404(LearningPath, slug=slug)
        
        try:
            enrollment = UserPathEnrollment.objects.get(
                user=request.user,
                learning_path=learning_path
            )
            serializer = UserPathEnrollmentDetailSerializer(enrollment)
            return Response(serializer.data)
        except UserPathEnrollment.DoesNotExist:
            return Response(
                {'error': 'No estás inscrito en esta ruta'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class StartLessonView(generics.CreateAPIView):
    """Vista para iniciar una lección"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        lesson = get_object_or_404(LearningPathLesson, uuid=uuid, is_active=True)
        
        # Verificar inscripción en la ruta
        try:
            enrollment = UserPathEnrollment.objects.get(
                user=request.user,
                learning_path=lesson.path_unit.learning_path,
                status='ACTIVE'
            )
        except UserPathEnrollment.DoesNotExist:
            return Response(
                {'error': 'No estás inscrito en esta ruta'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Crear o actualizar progreso de la lección
        lesson_progress, created = UserLessonProgress.objects.get_or_create(
            user=request.user,
            path_lesson=lesson,
            enrollment=enrollment,
            defaults={
                'status': 'IN_PROGRESS',
                'first_attempt_at': timezone.now()
            }
        )
        
        if not created and lesson_progress.status == 'NOT_STARTED':
            lesson_progress.status = 'IN_PROGRESS'
            lesson_progress.first_attempt_at = timezone.now()
            lesson_progress.save()
        
        serializer = UserLessonProgressSerializer(lesson_progress)
        return Response(serializer.data)


class CompleteLessonView(generics.UpdateAPIView):
    """Vista para completar una lección"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, uuid):
        lesson = get_object_or_404(LearningPathLesson, uuid=uuid, is_active=True)
        
        lesson_progress = get_object_or_404(
            UserLessonProgress,
            user=request.user,
            path_lesson=lesson
        )
        
        # Actualizar progreso con datos del request
        score = request.data.get('score', 0)
        time_seconds = request.data.get('time_seconds', 0)
        
        lesson_progress.last_score = score
        lesson_progress.best_score = max(lesson_progress.best_score, score)
        lesson_progress.total_time_seconds += time_seconds
        lesson_progress.attempts_count += 1
        lesson_progress.last_attempt_at = timezone.now()
        
        # Determinar estado basado en puntuación
        if score >= lesson.passing_score:
            if score == 100:
                lesson_progress.status = 'PERFECT'
            else:
                lesson_progress.status = 'COMPLETED'
            
            if not lesson_progress.completed_at:
                lesson_progress.completed_at = timezone.now()
        else:
            lesson_progress.status = 'NEEDS_REVIEW'
        
        lesson_progress.save()
        
        # Actualizar racha del usuario
        lesson_progress.enrollment.update_streak()
        
        serializer = UserLessonProgressSerializer(lesson_progress)
        return Response(serializer.data)


class MyLearningPathsView(generics.ListAPIView):
    """Vista de las rutas del usuario"""
    serializer_class = UserPathEnrollmentDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserPathEnrollment.objects.filter(
            user=self.request.user
        ).exclude(status='DROPPED')


class MyAchievementsView(generics.ListAPIView):
    """Vista de los logros del usuario"""
    serializer_class = UserPathAchievementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserPathAchievement.objects.filter(user=self.request.user)


class MyStreaksView(generics.RetrieveAPIView):
    """Vista de las rachas del usuario"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        enrollments = UserPathEnrollment.objects.filter(
            user=request.user,
            status='ACTIVE'
        )
        
        streaks_data = []
        for enrollment in enrollments:
            streaks_data.append({
                'learning_path': enrollment.learning_path.name,
                'current_streak': enrollment.current_streak_days,
                'max_streak': enrollment.max_streak_days,
                'last_activity': enrollment.last_activity_date
            })
        
        return Response({'streaks': streaks_data})


class LeaderboardView(generics.ListAPIView):
    """Vista del tablero de líderes"""
    
    def get(self, request):
        # Top usuarios por XP total en rutas
        top_users = UserPathEnrollment.objects.values(
            'user__username'
        ).annotate(
            total_xp=Count('total_xp_earned')
        ).order_by('-total_xp')[:10]
        
        return Response({'leaderboard': top_users})


class RecommendedPathsView(generics.ListAPIView):
    """Vista de rutas recomendadas"""
    serializer_class = LearningPathListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Rutas no inscritas que el usuario puede acceder
        enrolled_paths = UserPathEnrollment.objects.filter(
            user=user
        ).values_list('learning_path_id', flat=True)
        
        return LearningPath.objects.filter(
            status='ACTIVE'
        ).exclude(
            id__in=enrolled_paths
        ).filter(
            required_level__lte=user.level
        ).order_by('?')[:5]  # 5 recomendaciones aleatorias


class NextLessonView(generics.RetrieveAPIView):
    """Vista para obtener la siguiente lección recomendada"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Buscar la siguiente lección no completada
        active_enrollments = UserPathEnrollment.objects.filter(
            user=request.user,
            status='ACTIVE'
        )
        
        for enrollment in active_enrollments:
            # Buscar lecciones incompletas
            incomplete_lessons = UserLessonProgress.objects.filter(
                enrollment=enrollment,
                status__in=['NOT_STARTED', 'IN_PROGRESS', 'NEEDS_REVIEW']
            ).order_by('path_lesson__path_unit__order', 'path_lesson__order')
            
            if incomplete_lessons.exists():
                next_lesson = incomplete_lessons.first().path_lesson
                serializer = LearningPathLessonSerializer(next_lesson)
                return Response({
                    'next_lesson': serializer.data,
                    'enrollment': UserPathEnrollmentDetailSerializer(enrollment).data
                })
        
        return Response({'message': 'No hay lecciones pendientes'})


class ReviewPathView(generics.CreateAPIView):
    """Vista para reseñar una ruta de aprendizaje"""
    serializer_class = LearningPathReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, slug):
        learning_path = get_object_or_404(LearningPath, slug=slug)
        
        # Verificar que el usuario esté inscrito
        enrollment = get_object_or_404(
            UserPathEnrollment,
            user=request.user,
            learning_path=learning_path
        )
        
        review, created = LearningPathReview.objects.update_or_create(
            user=request.user,
            learning_path=learning_path,
            enrollment=enrollment,
            defaults=request.data
        )
        
        serializer = LearningPathReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarkReviewHelpfulView(generics.UpdateAPIView):
    """Vista para marcar una reseña como útil"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, review_id):
        review = get_object_or_404(LearningPathReview, id=review_id)
        review.helpful_votes += 1
        review.save()
        
        serializer = LearningPathReviewSerializer(review)
        return Response(serializer.data) 


class SimulacroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para simulacros ICFES con endpoints especiales
    """
    
    queryset = UserPathEnrollment.objects.select_related(
        'learning_path', 'user'
    ).filter(learning_path__path_type='SIMULACRO')
    
    serializer_class = UserPathEnrollmentDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserPathEnrollmentFilter
    pagination_class = ProgressPagination
    
    @extend_schema(
        summary="Generar Preguntas Aleatorias",
        description="Genera un set aleatorio de preguntas para simulacro",
        responses={200: "Preguntas generadas exitosamente"}
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, IsOwnerOrReadOnly]
    )
    def generate_questions(self, request, uuid=None):
        """
        Endpoint especial: Generar preguntas aleatorias para simulacro
        """
        simulacro = self.get_object()
        
        # Parámetros de generación
        num_questions = request.data.get('num_questions', 45)  # Simulacro ICFES típico
        difficulty_distribution = request.data.get('difficulty_distribution', {
            'easy': 30,    # 30% fáciles
            'medium': 50,  # 50% medias
            'hard': 20     # 20% difíciles
        })
        
        areas_distribution = request.data.get('areas_distribution', {
            'matematicas': 42,
            'lectura_critica': 35,
            'ciencias_naturales': 30,
            'ciencias_sociales': 30,
            'ingles': 25
        })
        
        # Generar preguntas basadas en distribución
        generated_questions = []
        
        # Obtener pool de preguntas disponibles
        from apps.icfes.models import PreguntaICFES
        available_questions = PreguntaICFES.objects.filter(
            activa=True,
            verificada=True
        ).select_related('area_evaluacion', 'competencia')
        
        # Generar por dificultad
        for difficulty, percentage in difficulty_distribution.items():
            count_needed = int(num_questions * percentage / 100)
            
            if difficulty == 'easy':
                questions = available_questions.filter(nivel_dificultad__lte=2)
            elif difficulty == 'medium':
                questions = available_questions.filter(nivel_dificultad__in=[3, 4])
            else:  # hard
                questions = available_questions.filter(nivel_dificultad__gte=4)
            
            # Selección aleatoria
            selected = questions.order_by('?')[:count_needed]
            
            for question in selected:
                generated_questions.append({
                    'question_id': question.id,
                    'question_text': question.pregunta_texto[:200] + '...',
                    'area': question.area_evaluacion.nombre if question.area_evaluacion else 'General',
                    'difficulty': question.nivel_dificultad,
                    'estimated_time': question.tiempo_estimado_segundos,
                    'xp_reward': question.puntos_xp,
                    'competencia': question.competencia.nombre if question.competencia else 'General'
                })
        
        # Guardar configuración del simulacro en caché
        simulacro_config = {
            'simulacro_uuid': str(simulacro.uuid),
            'questions': generated_questions,
            'total_questions': len(generated_questions),
            'estimated_duration_minutes': sum(q['estimated_time'] for q in generated_questions) // 60,
            'total_xp_possible': sum(q['xp_reward'] for q in generated_questions),
            'generated_at': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(hours=6)).isoformat()
        }
        
        cache_key = f"simulacro_questions_{simulacro.uuid}"
        cache.set(cache_key, simulacro_config, 6 * 3600)  # 6 horas
        
        return Response({
            "message": "Preguntas generadas exitosamente",
            "simulacro_config": simulacro_config,
            "difficulty_distribution": difficulty_distribution,
            "instructions": [
                "Tienes 6 horas para completar el simulacro",
                "Las preguntas están balanceadas por dificultad",
                "Puedes pausar y reanudar cuando quieras"
            ]
        })
    
    @extend_schema(
        summary="Reporte Detallado PDF",
        description="Genera un reporte detallado en PDF del simulacro",
        responses={200: "PDF generado exitosamente"}
    )
    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAuthenticated, IsOwnerOrReadOnly],
        throttle_classes=[HeavyComputationThrottle]
    )
    def detailed_report(self, request, uuid=None):
        """
        Endpoint especial: Generar reporte detallado en PDF
        """
        simulacro = self.get_object()
        
        if simulacro.status != 'COMPLETED':
            return Response(
                {"error": "El simulacro debe estar completado para generar reporte"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear PDF en memoria
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Título del reporte
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 100, f"Reporte de Simulacro ICFES")
        p.drawString(100, height - 120, f"Usuario: {simulacro.user.get_full_name() or simulacro.user.username}")
        p.drawString(100, height - 140, f"Path: {simulacro.learning_path.name}")
        
        # Estadísticas generales
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, height - 180, "Estadísticas Generales")
        
        p.setFont("Helvetica", 12)
        y_position = height - 200
        
        stats = [
            f"Progreso: {simulacro.overall_progress_percentage}%",
            f"XP Ganado: {simulacro.total_xp_earned}",
            f"Tiempo Total: {simulacro.total_time_spent_hours:.1f} horas",
            f"Racha Actual: {simulacro.current_streak_days} días",
            f"Iniciado: {simulacro.created_at.strftime('%d/%m/%Y')}",
        ]
        
        if simulacro.completed_at:
            stats.append(f"Completado: {simulacro.completed_at.strftime('%d/%m/%Y')}")
        
        for stat in stats:
            p.drawString(120, y_position, stat)
            y_position -= 20
        
        # Progreso por unidades
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y_position - 20, "Progreso por Unidades")
        y_position -= 50
        
        # Obtener progreso detallado
        serializer = self.get_serializer(simulacro)
        detailed_progress = serializer.get_detailed_progress(simulacro)
        
        p.setFont("Helvetica", 10)
        for unit_data in detailed_progress['units'][:5]:  # Limitar por espacio
            unit_text = f"• {unit_data['unit_title']}: {unit_data['progress_percentage']:.1f}%"
            p.drawString(120, y_position, unit_text)
            y_position -= 15
            
            if y_position < 100:  # Nueva página si es necesario
                p.showPage()
                y_position = height - 100
        
        # Finalizar PDF
        p.showPage()
        p.save()
        
        # Preparar respuesta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_simulacro_{simulacro.uuid}.pdf"'
        
        return response
    
    @extend_schema(
        summary="Comparar Resultados",
        description="Compara resultados con otros usuarios",
        responses={200: "Comparación generada exitosamente"}
    )
    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAuthenticated, IsOwnerOrReadOnly]
    )
    def compare_results(self, request, uuid=None):
        """
        Endpoint especial: Comparar resultados con otros usuarios
        """
        user_simulacro = self.get_object()
        
        if user_simulacro.status != 'COMPLETED':
            return Response(
                {"error": "El simulacro debe estar completado para comparar"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener simulacros similares para comparación
        similar_simulacros = UserPathEnrollment.objects.filter(
            learning_path=user_simulacro.learning_path,
            status='COMPLETED'
        ).exclude(
            user=user_simulacro.user
        ).select_related('user')
        
        # Estadísticas de comparación
        total_users = similar_simulacros.count()
        
        if total_users == 0:
            return Response({
                "message": "No hay otros usuarios para comparar aún",
                "comparison": None
            })
        
        # Calcular percentiles
        better_progress = similar_simulacros.filter(
            overall_progress_percentage__lt=user_simulacro.overall_progress_percentage
        ).count()
        
        better_xp = similar_simulacros.filter(
            total_xp_earned__lt=user_simulacro.total_xp_earned
        ).count()
        
        better_time = similar_simulacros.filter(
            total_time_spent_hours__gt=user_simulacro.total_time_spent_hours
        ).count()
        
        # Promedios generales
        averages = similar_simulacros.aggregate(
            avg_progress=Avg('overall_progress_percentage'),
            avg_xp=Avg('total_xp_earned'),
            avg_time=Avg('total_time_spent_hours'),
            avg_streak=Avg('current_streak_days')
        )
        
        # Top performers
        top_performers = similar_simulacros.order_by(
            '-overall_progress_percentage',
            '-total_xp_earned'
        )[:5]
        
        comparison_data = {
            'user_stats': {
                'progress': user_simulacro.overall_progress_percentage,
                'xp_earned': user_simulacro.total_xp_earned,
                'time_spent': user_simulacro.total_time_spent_hours,
                'streak': user_simulacro.current_streak_days
            },
            'percentiles': {
                'progress': round((better_progress / total_users) * 100, 1),
                'xp': round((better_xp / total_users) * 100, 1),
                'time_efficiency': round((better_time / total_users) * 100, 1)
            },
            'averages': {
                'progress': round(averages['avg_progress'] or 0, 1),
                'xp': round(averages['avg_xp'] or 0, 1),
                'time': round(averages['avg_time'] or 0, 1),
                'streak': round(averages['avg_streak'] or 0, 1)
            },
            'ranking': {
                'total_users': total_users,
                'your_position': better_progress + 1,
                'top_10_percent': total_users <= 10 or better_progress >= (total_users * 0.9)
            },
            'top_performers': [
                {
                    'username': perf.user.username[:3] + '***',  # Privacidad
                    'progress': perf.overall_progress_percentage,
                    'xp': perf.total_xp_earned,
                    'streak': perf.current_streak_days
                }
                for perf in top_performers
            ]
        }
        
        # Mensajes motivacionales
        messages = []
        if comparison_data['percentiles']['progress'] >= 80:
            messages.append("¡Excelente! Estás en el top 20% de usuarios")
        elif comparison_data['percentiles']['progress'] >= 50:
            messages.append("¡Buen trabajo! Estás por encima del promedio")
        else:
            messages.append("¡Sigue así! Tienes potencial para mejorar")
        
        if comparison_data['percentiles']['time_efficiency'] >= 70:
            messages.append("Tu eficiencia de tiempo es muy buena")
        
        return Response({
            "message": "Comparación generada exitosamente",
            "comparison": comparison_data,
            "motivational_messages": messages,
            "suggestions": [
                "Mantén tu racha diaria para mejorar tu posición",
                "Completa más lecciones para ganar más XP",
                "Revisa las lecciones más difíciles para mejorar tu score"
            ]
        }) 