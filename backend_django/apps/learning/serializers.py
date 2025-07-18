"""
Serializers optimizados para Learning Paths con performance y funcionalidad avanzada
"""

from rest_framework import serializers
from django.db.models import Avg, Count, Sum, Prefetch
from django.utils import timezone
from django.core.cache import cache
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from .models import (
    LearningPath, LearningPathUnit, LearningPathLesson,
    UserPathEnrollment, UserLessonProgress, PathAchievement,
    UserPathAchievement, LearningPathReview
)
from .cache import LearningCacheManager


class OptimizedLearningPathUnitSerializer(serializers.ModelSerializer):
    """
    Serializer optimizado para unidades de rutas de aprendizaje
    """
    
    # Campos calculados con caché
    lessons_count = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    # Campos relacionados optimizados
    next_unit = serializers.SerializerMethodField()
    previous_unit = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPathUnit
        fields = [
            'uuid', 'learning_path', 'title', 'description', 'order_index',
            'xp_reward', 'is_bonus', 'is_optional', 'unlock_criteria',
            'lessons_count', 'completion_rate', 'user_progress',
            'next_unit', 'previous_unit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_lessons_count(self, obj):
        """Obtiene el número de lecciones (con caché)"""
        cache_key = f"unit_lessons_count_{obj.id}"
        count = cache.get(cache_key)
        
        if count is None:
            count = obj.lessons.count()
            cache.set(cache_key, count, 3600)  # 1 hora
        
        return count
    
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_completion_rate(self, obj):
        """Tasa de completado de la unidad"""
        # Solo calcular si hay contexto de request
        if not self.context.get('request'):
            return 0.0
        
        cache_key = f"unit_completion_rate_{obj.id}"
        rate = cache.get(cache_key)
        
        if rate is None:
            total_enrollments = obj.learning_path.total_enrollments
            if total_enrollments == 0:
                rate = 0.0
            else:
                completed_count = UserLessonProgress.objects.filter(
                    path_lesson__path_unit=obj,
                    status='COMPLETED'
                ).values('user').distinct().count()
                rate = (completed_count / total_enrollments) * 100
            
            cache.set(cache_key, rate, 1800)  # 30 minutos
        
        return round(rate, 2)
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_user_progress(self, obj):
        """Progreso del usuario autenticado en esta unidad"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        # Usar caché para progreso del usuario
        progress_data = LearningCacheManager.get_user_progress(
            request.user.id, obj.learning_path.id
        )
        
        if progress_data and str(obj.id) in progress_data.get('units', {}):
            return progress_data['units'][str(obj.id)]
        
        # Calcular si no está en caché
        user_lessons = UserLessonProgress.objects.filter(
            user=request.user,
            path_lesson__path_unit=obj
        )
        
        total_lessons = obj.lessons.count()
        completed_lessons = user_lessons.filter(status='COMPLETED').count()
        
        progress = {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
            'is_unlocked': True,  # Lógica de unlock más compleja si es necesario
            'current_lesson': None
        }
        
        # Encontrar lección actual
        current_lesson = user_lessons.filter(
            status__in=['IN_PROGRESS', 'NOT_STARTED']
        ).order_by('path_lesson__order_index').first()
        
        if current_lesson:
            progress['current_lesson'] = {
                'uuid': current_lesson.path_lesson.uuid,
                'title': current_lesson.path_lesson.title,
                'order_index': current_lesson.path_lesson.order_index
            }
        
        return progress
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_next_unit(self, obj):
        """Unidad siguiente en la secuencia"""
        next_unit = LearningPathUnit.objects.filter(
            learning_path=obj.learning_path,
            order_index__gt=obj.order_index
        ).order_by('order_index').first()
        
        if next_unit:
            return {
                'uuid': next_unit.uuid,
                'title': next_unit.title,
                'order_index': next_unit.order_index
            }
        return None
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_previous_unit(self, obj):
        """Unidad anterior en la secuencia"""
        prev_unit = LearningPathUnit.objects.filter(
            learning_path=obj.learning_path,
            order_index__lt=obj.order_index
        ).order_by('-order_index').first()
        
        if prev_unit:
            return {
                'uuid': prev_unit.uuid,
                'title': prev_unit.title,
                'order_index': prev_unit.order_index
            }
        return None


class OptimizedLearningPathLessonSerializer(serializers.ModelSerializer):
    """
    Serializer optimizado para lecciones de rutas de aprendizaje
    """
    
    path_unit_title = serializers.CharField(source='path_unit.title', read_only=True)
    content_unit_title = serializers.CharField(source='content_unit.title', read_only=True)
    icfes_question_text = serializers.CharField(source='icfes_question.pregunta_texto', read_only=True)
    
    # Campos calculados
    user_progress = serializers.SerializerMethodField()
    estimated_time_minutes = serializers.SerializerMethodField()
    difficulty_level = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPathLesson
        fields = [
            'uuid', 'path_unit', 'content_unit', 'icfes_question',
            'title', 'description', 'order_index', 'is_mandatory',
            'xp_reward', 'time_limit_minutes', 'retry_limit',
            'path_unit_title', 'content_unit_title', 'icfes_question_text',
            'user_progress', 'estimated_time_minutes', 'difficulty_level',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_user_progress(self, obj):
        """Progreso específico del usuario en esta lección"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            progress = UserLessonProgress.objects.get(
                user=request.user,
                path_lesson=obj
            )
            return {
                'status': progress.status,
                'attempts_count': progress.attempts_count,
                'final_score': progress.final_score,
                'time_spent_seconds': progress.time_spent_seconds,
                'completed_at': progress.completed_at,
                'can_retry': progress.attempts_count < obj.retry_limit if obj.retry_limit else True
            }
        except UserLessonProgress.DoesNotExist:
            return {
                'status': 'NOT_STARTED',
                'attempts_count': 0,
                'final_score': None,
                'time_spent_seconds': 0,
                'completed_at': None,
                'can_retry': True
            }
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_estimated_time_minutes(self, obj):
        """Tiempo estimado basado en datos reales de usuarios"""
        cache_key = f"lesson_avg_time_{obj.id}"
        avg_time = cache.get(cache_key)
        
        if avg_time is None:
            avg_seconds = UserLessonProgress.objects.filter(
                path_lesson=obj,
                status='COMPLETED'
            ).aggregate(avg_time=Avg('time_spent_seconds'))['avg_time']
            
            if avg_seconds:
                avg_time = int(avg_seconds / 60)  # Convertir a minutos
            else:
                # Tiempo por defecto si no hay datos
                if obj.icfes_question:
                    avg_time = obj.icfes_question.tiempo_estimado_segundos // 60
                elif obj.content_unit:
                    avg_time = 15  # Default para content unit
                else:
                    avg_time = 10  # Default general
            
            cache.set(cache_key, avg_time, 7200)  # 2 horas
        
        return avg_time
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_difficulty_level(self, obj):
        """Nivel de dificultad basado en el contenido"""
        if obj.icfes_question:
            return obj.icfes_question.nivel_dificultad
        elif obj.content_unit:
            return getattr(obj.content_unit, 'difficulty_level', 3)
        else:
            return 3  # Neutral


class OptimizedLearningPathSerializer(serializers.ModelSerializer):
    """
    Serializer principal optimizado para rutas de aprendizaje
    """
    
    # Relaciones optimizadas
    units = OptimizedLearningPathUnitSerializer(many=True, read_only=True)
    
    # Campos calculados con caché
    completion_rate = serializers.SerializerMethodField()
    estimated_weeks = serializers.SerializerMethodField()
    user_enrollment = serializers.SerializerMethodField()
    user_can_enroll = serializers.SerializerMethodField()
    
    # Estadísticas agregadas
    stats = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    
    # Tags como lista
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = [
            'uuid', 'name', 'slug', 'description', 'difficulty_level',
            'path_type', 'status', 'category', 'image_url', 'icon_url',
            'is_featured', 'is_premium', 'has_certificate',
            'estimated_duration_hours', 'minimum_level', 'prerequisite_paths',
            'total_enrollments', 'total_completions', 'average_completion_time_hours',
            'average_rating', 'total_xp_available', 'vitality_cost',
            'tags', 'tags_list', 'units', 'completion_rate', 'estimated_weeks',
            'user_enrollment', 'user_can_enroll', 'stats', 'recent_reviews',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'uuid', 'total_enrollments', 'total_completions',
            'average_completion_time_hours', 'average_rating',
            'total_xp_available', 'created_at', 'updated_at', 'published_at'
        ]
    
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_completion_rate(self, obj):
        """Tasa de completado general del path"""
        cache_key = f"path_completion_rate_{obj.id}"
        rate = cache.get(cache_key)
        
        if rate is None:
            if obj.total_enrollments == 0:
                rate = 0.0
            else:
                rate = (obj.total_completions / obj.total_enrollments) * 100
            cache.set(cache_key, rate, 3600)  # 1 hora
        
        return round(rate, 2)
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_estimated_weeks(self, obj):
        """Estimación en semanas basada en horas y actividad promedio"""
        if obj.estimated_duration_hours <= 5:
            return 1
        elif obj.estimated_duration_hours <= 15:
            return 2
        elif obj.estimated_duration_hours <= 30:
            return 4
        else:
            return max(8, obj.estimated_duration_hours // 5)
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_user_enrollment(self, obj):
        """Información de inscripción del usuario actual"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            enrollment = UserPathEnrollment.objects.select_related().get(
                user=request.user,
                learning_path=obj
            )
            return {
                'status': enrollment.status,
                'enrolled_at': enrollment.created_at,
                'overall_progress_percentage': enrollment.overall_progress_percentage,
                'current_streak_days': enrollment.current_streak_days,
                'total_xp_earned': enrollment.total_xp_earned,
                'completed_at': enrollment.completed_at,
                'last_activity_at': enrollment.last_activity_at
            }
        except UserPathEnrollment.DoesNotExist:
            return None
    
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_user_can_enroll(self, obj):
        """Si el usuario puede inscribirse en este path"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        user = request.user
        
        # Verificar si ya está inscrito
        if UserPathEnrollment.objects.filter(user=user, learning_path=obj).exists():
            return False
        
        # Verificar nivel mínimo
        if obj.minimum_level > getattr(user, 'level', 1):
            return False
        
        # Verificar prerequisitos
        if obj.prerequisite_paths.exists():
            completed_prerequisites = UserPathEnrollment.objects.filter(
                user=user,
                learning_path__in=obj.prerequisite_paths.all(),
                status='COMPLETED'
            ).count()
            
            if completed_prerequisites < obj.prerequisite_paths.count():
                return False
        
        return True
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_stats(self, obj):
        """Estadísticas agregadas del path"""
        cache_key = f"path_stats_{obj.id}"
        stats = cache.get(cache_key)
        
        if stats is None:
            stats = {
                'total_lessons': obj.units.aggregate(
                    total=Sum('lessons__count', default=0)
                )['total'] or 0,
                'avg_user_score': UserLessonProgress.objects.filter(
                    path_lesson__path_unit__learning_path=obj,
                    status='COMPLETED'
                ).aggregate(avg_score=Avg('final_score'))['avg_score'] or 0,
                'completion_trend': 'stable',  # Simplificado, se puede hacer más complejo
                'difficulty_distribution': {
                    'easy': 30,
                    'medium': 50,
                    'hard': 20
                }  # Simplificado
            }
            cache.set(cache_key, stats, 7200)  # 2 horas
        
        return stats
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_recent_reviews(self, obj):
        """Reviews recientes del path"""
        recent_reviews = LearningPathReview.objects.filter(
            learning_path=obj
        ).select_related('user').order_by('-created_at')[:3]
        
        return [
            {
                'user_name': review.user.first_name or review.user.username,
                'overall_rating': review.overall_rating,
                'review_comment': review.review_comment[:100] + '...' if len(review.review_comment) > 100 else review.review_comment,
                'created_at': review.created_at
            }
            for review in recent_reviews
        ]
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_tags_list(self, obj):
        """Tags como lista procesada"""
        if not obj.tags:
            return []
        return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar que la duración estimada sea razonable
        if 'estimated_duration_hours' in data:
            if data['estimated_duration_hours'] < 1:
                raise serializers.ValidationError({
                    'estimated_duration_hours': 'La duración debe ser al menos 1 hora'
                })
            if data['estimated_duration_hours'] > 500:
                raise serializers.ValidationError({
                    'estimated_duration_hours': 'La duración no puede exceder 500 horas'
                })
        
        # Validar nivel mínimo
        if 'minimum_level' in data:
            if data['minimum_level'] < 1 or data['minimum_level'] > 100:
                raise serializers.ValidationError({
                    'minimum_level': 'El nivel mínimo debe estar entre 1 y 100'
                })
        
        return data


class UserPathEnrollmentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para inscripciones con progreso completo
    """
    
    learning_path = OptimizedLearningPathSerializer(read_only=True)
    detailed_progress = serializers.SerializerMethodField()
    achievements_earned = serializers.SerializerMethodField()
    time_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = UserPathEnrollment
        fields = [
            'uuid', 'learning_path', 'status', 'overall_progress_percentage',
            'current_streak_days', 'longest_streak_days', 'total_time_spent_hours',
            'total_xp_earned', 'average_session_duration_minutes',
            'daily_goal_minutes', 'weekly_goal_completed', 'last_activity_at',
            'detailed_progress', 'achievements_earned', 'time_stats',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'uuid', 'total_time_spent_hours', 'average_session_duration_minutes',
            'created_at'
        ]
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_detailed_progress(self, obj):
        """Progreso detallado por unidad y lección"""
        # Usar caché para progreso detallado
        cache_key = f"detailed_progress_{obj.user.id}_{obj.learning_path.id}"
        progress = cache.get(cache_key)
        
        if progress is None:
            units_progress = []
            
            for unit in obj.learning_path.units.prefetch_related('lessons').all():
                lessons_progress = []
                
                for lesson in unit.lessons.all():
                    try:
                        lesson_progress = UserLessonProgress.objects.get(
                            user=obj.user,
                            path_lesson=lesson
                        )
                        lessons_progress.append({
                            'lesson_uuid': lesson.uuid,
                            'lesson_title': lesson.title,
                            'status': lesson_progress.status,
                            'score': lesson_progress.final_score,
                            'attempts': lesson_progress.attempts_count,
                            'time_spent': lesson_progress.time_spent_seconds,
                            'completed_at': lesson_progress.completed_at
                        })
                    except UserLessonProgress.DoesNotExist:
                        lessons_progress.append({
                            'lesson_uuid': lesson.uuid,
                            'lesson_title': lesson.title,
                            'status': 'NOT_STARTED',
                            'score': None,
                            'attempts': 0,
                            'time_spent': 0,
                            'completed_at': None
                        })
                
                # Calcular progreso de la unidad
                completed_lessons = sum(1 for l in lessons_progress if l['status'] == 'COMPLETED')
                total_lessons = len(lessons_progress)
                unit_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
                
                units_progress.append({
                    'unit_uuid': unit.uuid,
                    'unit_title': unit.title,
                    'progress_percentage': unit_progress,
                    'lessons': lessons_progress
                })
            
            progress = {
                'units': units_progress,
                'last_updated': timezone.now().isoformat()
            }
            
            cache.set(cache_key, progress, 600)  # 10 minutos
        
        return progress
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_achievements_earned(self, obj):
        """Logros obtenidos en este path"""
        user_achievements = UserPathAchievement.objects.filter(
            user=obj.user,
            achievement__learning_path=obj.learning_path
        ).select_related('achievement')
        
        return [
            {
                'achievement_uuid': ua.achievement.uuid,
                'achievement_name': ua.achievement.name,
                'achievement_type': ua.achievement.achievement_type,
                'rarity_level': ua.achievement.rarity_level,
                'earned_at': ua.earned_at,
                'progress_when_earned': ua.progress_when_earned
            }
            for ua in user_achievements
        ]
    
    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_time_stats(self, obj):
        """Estadísticas de tiempo detalladas"""
        cache_key = f"time_stats_{obj.user.id}_{obj.learning_path.id}"
        stats = cache.get(cache_key)
        
        if stats is None:
            # Calcular estadísticas de tiempo
            lesson_progresses = UserLessonProgress.objects.filter(
                user=obj.user,
                path_lesson__path_unit__learning_path=obj.learning_path
            )
            
            total_time = lesson_progresses.aggregate(
                total=Sum('time_spent_seconds')
            )['total'] or 0
            
            avg_session = lesson_progresses.filter(
                time_spent_seconds__gt=0
            ).aggregate(
                avg=Avg('time_spent_seconds')
            )['avg'] or 0
            
            stats = {
                'total_minutes': total_time // 60,
                'average_session_minutes': avg_session // 60,
                'sessions_completed': lesson_progresses.filter(status='COMPLETED').count(),
                'estimated_remaining_minutes': max(0, 
                    (obj.learning_path.estimated_duration_hours * 60) - (total_time // 60)
                )
            }
            
            cache.set(cache_key, stats, 1800)  # 30 minutos
        
        return stats


# Serializers simplificados para listas
class LearningPathListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listas de paths"""
    
    completion_rate = serializers.ReadOnlyField()
    user_can_enroll = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = [
            'uuid', 'name', 'slug', 'description', 'difficulty_level',
            'path_type', 'image_url', 'is_featured', 'is_premium',
            'estimated_duration_hours', 'average_rating', 'total_enrollments',
            'completion_rate', 'user_can_enroll'
        ]
    
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_user_can_enroll(self, obj):
        """Versión simplificada para listas"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Cache simple check
        cache_key = f"can_enroll_{request.user.id}_{obj.id}"
        can_enroll = cache.get(cache_key)
        
        if can_enroll is None:
            can_enroll = not UserPathEnrollment.objects.filter(
                user=request.user,
                learning_path=obj
            ).exists()
            cache.set(cache_key, can_enroll, 300)  # 5 minutos
        
        return can_enroll 


class PathAchievementSerializer(serializers.ModelSerializer):
    """
    Serializer para PathAchievement con información básica
    """
    
    class Meta:
        model = PathAchievement
        fields = [
            'id', 'name', 'description', 'achievement_type', 'icon_emoji',
            'badge_color', 'rarity', 'xp_reward', 'is_secret'
        ]


class UserPathAchievementSerializer(serializers.ModelSerializer):
    """
    Serializer para UserPathAchievement con información de progreso
    """
    achievement = PathAchievementSerializer(read_only=True)
    
    class Meta:
        model = UserPathAchievement
        fields = [
            'id', 'achievement', 'progress_percentage', 'is_completed',
            'completed_at', 'xp_earned'
        ] 


class LearningPathReviewSerializer(serializers.ModelSerializer):
    """
    Serializer para LearningPathReview - reseñas de rutas de aprendizaje
    """
    
    class Meta:
        model = LearningPathReview
        fields = [
            'id', 'rating', 'review_text', 'is_recommended', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at'] 