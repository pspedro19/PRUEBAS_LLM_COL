"""
Filtros avanzados para Learning Paths con django-filter
"""

import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta, date

from .models import (
    LearningPath, LearningPathUnit, LearningPathLesson,
    UserPathEnrollment, UserLessonProgress, PathAchievement,
    UserPathAchievement, LearningPathReview
)


class LearningPathFilter(filters.FilterSet):
    """
    Filtros avanzados para Learning Paths
    """
    
    # Filtros básicos
    name = filters.CharFilter(lookup_expr='icontains')
    difficulty = filters.MultipleChoiceFilter(
        choices=LearningPath.DIFFICULTY_LEVELS,
        field_name='difficulty_level'
    )
    path_type = filters.MultipleChoiceFilter(
        choices=LearningPath.PATH_TYPES
    )
    status = filters.MultipleChoiceFilter(
        choices=LearningPath.PATH_STATUS
    )
    
    # Filtros por características
    is_featured = filters.BooleanFilter()
    is_premium = filters.BooleanFilter()
    has_certificate = filters.BooleanFilter()
    
    # Filtros por duración
    duration_min = filters.NumberFilter(
        field_name='estimated_duration_hours',
        lookup_expr='gte'
    )
    duration_max = filters.NumberFilter(
        field_name='estimated_duration_hours',
        lookup_expr='lte'
    )
    
    # Filtros por XP
    xp_min = filters.NumberFilter(
        field_name='total_xp_available',
        lookup_expr='gte'
    )
    xp_max = filters.NumberFilter(
        field_name='total_xp_available',
        lookup_expr='lte'
    )
    
    # Filtros por rating
    min_rating = filters.NumberFilter(
        field_name='average_rating',
        lookup_expr='gte'
    )
    
    # Filtros por fecha
    created_after = filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    
    # Filtros por nivel del usuario
    min_level_required = filters.NumberFilter(
        field_name='minimum_level',
        lookup_expr='lte'
    )
    max_level_required = filters.NumberFilter(
        field_name='minimum_level',
        lookup_expr='gte'
    )
    
    # Filtros por popularidad
    min_enrollments = filters.NumberFilter(
        field_name='total_enrollments',
        lookup_expr='gte'
    )
    
    # Filtros por tags/categorías
    tags = filters.CharFilter(method='filter_by_tags')
    category = filters.CharFilter(method='filter_by_category')
    
    # Filtros complejos
    trending = filters.BooleanFilter(method='filter_trending')
    recommended_for_user = filters.BooleanFilter(method='filter_recommended')
    user_can_enroll = filters.BooleanFilter(method='filter_user_can_enroll')
    
    # Filtros de ordenamiento
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('difficulty_level', 'difficulty'),
            ('average_rating', 'rating'),
            ('total_enrollments', 'popularity'),
            ('created_at', 'created'),
            ('updated_at', 'updated'),
            ('estimated_duration_hours', 'duration'),
        )
    )
    
    class Meta:
        model = LearningPath
        fields = {
            'name': ['icontains', 'exact'],
            'description': ['icontains'],
            'difficulty_level': ['exact', 'in'],
            'path_type': ['exact', 'in'],
            'status': ['exact', 'in'],
            'is_featured': ['exact'],
            'is_premium': ['exact'],
        }
    
    def filter_by_tags(self, queryset, name, value):
        """Filtrar por tags separados por comas"""
        if not value:
            return queryset
        
        tags = [tag.strip() for tag in value.split(',')]
        query = Q()
        for tag in tags:
            query |= Q(tags__icontains=tag)
        
        return queryset.filter(query).distinct()
    
    def filter_by_category(self, queryset, name, value):
        """Filtrar por categoría usando slug o nombre"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(category__slug__icontains=value) |
            Q(category__name__icontains=value)
        )
    
    def filter_trending(self, queryset, name, value):
        """Filtrar paths en tendencia (más inscripciones recientes)"""
        if not value:
            return queryset
        
        # Paths con más inscripciones en los últimos 7 días
        week_ago = timezone.now() - timedelta(days=7)
        trending_paths = queryset.filter(
            enrollments__created_at__gte=week_ago
        ).annotate(
            recent_enrollments=Count('enrollments', filter=Q(enrollments__created_at__gte=week_ago))
        ).filter(recent_enrollments__gte=5).order_by('-recent_enrollments')
        
        return trending_paths
    
    def filter_recommended(self, queryset, name, value):
        """Filtrar paths recomendados para el usuario actual"""
        if not value or not self.request.user.is_authenticated:
            return queryset
        
        user = self.request.user
        
        # Lógica de recomendación básica
        # 1. Paths del mismo nivel o ligeramente superior
        user_level = getattr(user, 'level', 1)
        level_range = queryset.filter(
            minimum_level__lte=user_level + 2,
            minimum_level__gte=max(1, user_level - 1)
        )
        
        # 2. Excluir paths ya completados
        completed_paths = UserPathEnrollment.objects.filter(
            user=user,
            status='COMPLETED'
        ).values_list('learning_path_id', flat=True)
        
        level_range = level_range.exclude(id__in=completed_paths)
        
        # 3. Priorizar por rating y popularidad
        return level_range.order_by('-average_rating', '-total_enrollments')
    
    def filter_user_can_enroll(self, queryset, name, value):
        """Filtrar paths en los que el usuario puede inscribirse"""
        if not value or not self.request.user.is_authenticated:
            return queryset
        
        user = self.request.user
        
        # Excluir paths ya inscritos o completados
        enrolled_paths = UserPathEnrollment.objects.filter(
            user=user
        ).values_list('learning_path_id', flat=True)
        
        available_paths = queryset.exclude(id__in=enrolled_paths)
        
        # Verificar prerequisitos de nivel
        user_level = getattr(user, 'level', 1)
        available_paths = available_paths.filter(minimum_level__lte=user_level)
        
        return available_paths


class UserPathEnrollmentFilter(filters.FilterSet):
    """
    Filtros para inscripciones de usuarios
    """
    
    status = filters.MultipleChoiceFilter(
        choices=UserPathEnrollment.ENROLLMENT_STATUS
    )
    
    # Filtros por progreso
    progress_min = filters.NumberFilter(
        field_name='overall_progress_percentage',
        lookup_expr='gte'
    )
    progress_max = filters.NumberFilter(
        field_name='overall_progress_percentage',
        lookup_expr='lte'
    )
    
    # Filtros por fecha
    enrolled_after = filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    enrolled_before = filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    
    completed_after = filters.DateFilter(
        field_name='completed_at',
        lookup_expr='gte'
    )
    completed_before = filters.DateFilter(
        field_name='completed_at',
        lookup_expr='lte'
    )
    
    # Filtros por actividad
    has_activity_today = filters.BooleanFilter(method='filter_activity_today')
    has_streak = filters.BooleanFilter(method='filter_has_streak')
    
    # Filtros por path
    path_difficulty = filters.MultipleChoiceFilter(
        field_name='learning_path__difficulty_level',
        choices=LearningPath.DIFFICULTY_LEVELS
    )
    path_type = filters.MultipleChoiceFilter(
        field_name='learning_path__path_type',
        choices=LearningPath.PATH_TYPES
    )
    
    class Meta:
        model = UserPathEnrollment
        fields = ['status', 'learning_path']
    
    def filter_activity_today(self, queryset, name, value):
        """Filtrar inscripciones con actividad hoy"""
        if not value:
            return queryset
        
        today = timezone.now().date()
        return queryset.filter(last_activity_at__date=today)
    
    def filter_has_streak(self, queryset, name, value):
        """Filtrar inscripciones con streak activo"""
        if not value:
            return queryset
        
        return queryset.filter(current_streak_days__gt=0)


class UserLessonProgressFilter(filters.FilterSet):
    """
    Filtros para progreso de lecciones
    """
    
    status = filters.MultipleChoiceFilter(
        choices=UserLessonProgress.LESSON_STATUS
    )
    
    # Filtros por scoring
    score_min = filters.NumberFilter(
        field_name='final_score',
        lookup_expr='gte'
    )
    score_max = filters.NumberFilter(
        field_name='final_score',
        lookup_expr='lte'
    )
    
    # Filtros por tiempo
    time_spent_min = filters.NumberFilter(
        field_name='time_spent_seconds',
        lookup_expr='gte'
    )
    time_spent_max = filters.NumberFilter(
        field_name='time_spent_seconds',
        lookup_expr='lte'
    )
    
    # Filtros por fecha
    completed_after = filters.DateTimeFilter(
        field_name='completed_at',
        lookup_expr='gte'
    )
    completed_before = filters.DateTimeFilter(
        field_name='completed_at',
        lookup_expr='lte'
    )
    
    # Filtros por attempts
    max_attempts = filters.NumberFilter(
        field_name='attempts_count',
        lookup_expr='lte'
    )
    
    class Meta:
        model = UserLessonProgress
        fields = ['status', 'path_lesson']


class PathAchievementFilter(filters.FilterSet):
    """
    Filtros para achievements de paths
    """
    
    achievement_type = filters.MultipleChoiceFilter(
        choices=PathAchievement.ACHIEVEMENT_TYPES
    )
    rarity_level = filters.MultipleChoiceFilter(
        choices=PathAchievement.RARITY_LEVELS
    )
    
    # Filtros por criterios
    required_score_min = filters.NumberFilter(
        field_name='required_score',
        lookup_expr='gte'
    )
    required_lessons_min = filters.NumberFilter(
        field_name='required_lessons_completed',
        lookup_expr='gte'
    )
    
    # Filtros por disponibilidad
    is_hidden = filters.BooleanFilter()
    is_active = filters.BooleanFilter()
    
    class Meta:
        model = PathAchievement
        fields = ['achievement_type', 'rarity_level', 'learning_path']


class LearningPathReviewFilter(filters.FilterSet):
    """
    Filtros para reviews de paths
    """
    
    # Filtros por rating
    rating_min = filters.NumberFilter(
        field_name='overall_rating',
        lookup_expr='gte'
    )
    rating_max = filters.NumberFilter(
        field_name='overall_rating',
        lookup_expr='lte'
    )
    
    # Filtros por aspectos específicos
    content_rating_min = filters.NumberFilter(
        field_name='content_rating',
        lookup_expr='gte'
    )
    difficulty_rating_min = filters.NumberFilter(
        field_name='difficulty_rating',
        lookup_expr='gte'
    )
    
    # Filtros por fecha
    reviewed_after = filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    reviewed_before = filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    
    # Filtros por texto
    has_comment = filters.BooleanFilter(method='filter_has_comment')
    
    class Meta:
        model = LearningPathReview
        fields = ['learning_path', 'user']
    
    def filter_has_comment(self, queryset, name, value):
        """Filtrar reviews que tienen comentarios"""
        if value:
            return queryset.exclude(Q(review_comment='') | Q(review_comment__isnull=True))
        else:
            return queryset.filter(Q(review_comment='') | Q(review_comment__isnull=True))


class DateRangeFilter(filters.Filter):
    """
    Filtro personalizado para rangos de fechas flexibles
    """
    
    def filter(self, qs, value):
        if not value:
            return qs
        
        # Interpretar valores como 'last_week', 'last_month', etc.
        now = timezone.now()
        
        if value == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif value == 'yesterday':
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif value == 'last_week':
            start_date = now - timedelta(days=7)
            end_date = now
        elif value == 'last_month':
            start_date = now - timedelta(days=30)
            end_date = now
        elif value == 'last_quarter':
            start_date = now - timedelta(days=90)
            end_date = now
        else:
            return qs
        
        return qs.filter(
            **{f'{self.field_name}__range': [start_date, end_date]}
        ) 