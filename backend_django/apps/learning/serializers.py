"""
Serializers para la app Learning
"""
from rest_framework import serializers
from .models import (
    LearningPath, LearningPathUnit, LearningPathLesson,
    UserPathEnrollment, UserLessonProgress, PathAchievement,
    UserPathAchievement, LearningPathReview
)
from apps.users.serializers import UserSerializer


class LearningPathLessonSerializer(serializers.ModelSerializer):
    """Serializer para lecciones"""
    
    class Meta:
        model = LearningPathLesson
        fields = [
            'id', 'uuid', 'title', 'lesson_type', 'order',
            'estimated_duration_minutes', 'difficulty_level',
            'max_attempts', 'passing_score', 'xp_reward',
            'perfect_score_bonus', 'hints_enabled',
            'explanations_enabled', 'skip_enabled',
            'is_active', 'is_assessment'
        ]


class LearningPathUnitSerializer(serializers.ModelSerializer):
    """Serializer para unidades"""
    lessons = LearningPathLessonSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPathUnit
        fields = [
            'id', 'uuid', 'title', 'description', 'unit_type',
            'order', 'estimated_duration_minutes', 'difficulty_modifier',
            'xp_reward', 'hearts_required', 'unlock_criteria',
            'is_bonus', 'is_optional', 'icon_emoji', 'thumbnail_url',
            'is_active', 'learning_objectives', 'lessons', 'lesson_count'
        ]
    
    def get_lesson_count(self, obj):
        return obj.lessons.count()


class LearningPathSerializer(serializers.ModelSerializer):
    """Serializer básico para rutas de aprendizaje"""
    unit_count = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'uuid', 'name', 'slug', 'description',
            'short_description', 'path_type', 'status',
            'difficulty_level', 'target_icfes_areas',
            'estimated_duration_hours', 'recommended_weekly_hours',
            'min_grade_level', 'max_grade_level',
            'total_xp_available', 'completion_xp_bonus',
            'required_hero_class', 'required_level',
            'thumbnail_url', 'cover_image_url', 'primary_color',
            'icon_emoji', 'is_premium', 'is_featured',
            'unit_count', 'enrollment_count', 'average_rating',
            'created_at', 'published_at'
        ]
    
    def get_unit_count(self, obj):
        return obj.units.count()
    
    def get_enrollment_count(self, obj):
        return obj.enrollments.filter(status='ACTIVE').count()


class LearningPathDetailSerializer(LearningPathSerializer):
    """Serializer detallado con unidades incluidas"""
    units = LearningPathUnitSerializer(many=True, read_only=True)
    prerequisite_paths = LearningPathSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta(LearningPathSerializer.Meta):
        fields = LearningPathSerializer.Meta.fields + [
            'units', 'prerequisite_paths', 'created_by',
            'learning_outcomes', 'tags', 'has_adaptive_difficulty',
            'has_peer_comparison', 'has_leaderboards',
            'has_streaks', 'has_certificates',
            'ai_recommendations_enabled', 'adaptive_sequencing_enabled',
            'personalized_feedback_enabled'
        ]


class UserPathEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer para inscripciones"""
    learning_path = LearningPathSerializer(read_only=True)
    days_enrolled = serializers.SerializerMethodField()
    estimated_completion_date = serializers.SerializerMethodField()
    
    class Meta:
        model = UserPathEnrollment
        fields = [
            'id', 'learning_path', 'status', 'current_unit_order',
            'current_lesson_order', 'progress_percentage',
            'total_xp_earned', 'total_lessons_completed',
            'total_time_minutes', 'average_score',
            'daily_goal_minutes', 'reminder_time',
            'current_streak_days', 'max_streak_days',
            'last_activity_date', 'enrolled_at', 'started_at',
            'completed_at', 'adaptive_difficulty_enabled',
            'current_difficulty_modifier', 'days_enrolled',
            'estimated_completion_date'
        ]
    
    def get_days_enrolled(self, obj):
        from django.utils import timezone
        if obj.enrolled_at:
            return (timezone.now().date() - obj.enrolled_at.date()).days
        return 0
    
    def get_estimated_completion_date(self, obj):
        return obj.estimated_completion_date


class UserLessonProgressSerializer(serializers.ModelSerializer):
    """Serializer para progreso de lecciones"""
    path_lesson = LearningPathLessonSerializer(read_only=True)
    completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = UserLessonProgress
        fields = [
            'id', 'path_lesson', 'enrollment', 'status',
            'attempts_count', 'best_score', 'last_score',
            'total_time_seconds', 'xp_earned', 'hearts_spent',
            'hints_used', 'first_attempt_at', 'last_attempt_at',
            'completed_at', 'completion_rate', 'attempt_data',
            'mistake_patterns'
        ]
    
    def get_completion_rate(self, obj):
        if obj.path_lesson.max_attempts == 0:
            return 100.0
        return (obj.attempts_count / obj.path_lesson.max_attempts) * 100


class PathAchievementSerializer(serializers.ModelSerializer):
    """Serializer para logros de ruta"""
    
    class Meta:
        model = PathAchievement
        fields = [
            'id', 'name', 'description', 'achievement_type',
            'icon_emoji', 'badge_color', 'rarity', 'criteria',
            'learning_path', 'xp_reward', 'special_rewards',
            'is_active', 'is_secret'
        ]


class UserPathAchievementSerializer(serializers.ModelSerializer):
    """Serializer para logros obtenidos"""
    achievement = PathAchievementSerializer(read_only=True)
    
    class Meta:
        model = UserPathAchievement
        fields = [
            'id', 'achievement', 'enrollment',
            'progress_when_earned', 'xp_earned',
            'achievement_data', 'earned_at'
        ] 


class LearningPathReviewSerializer(serializers.ModelSerializer):
    """Serializer para reseñas"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = LearningPathReview
        fields = [
            'id', 'user', 'learning_path', 'rating',
            'content_quality', 'difficulty_appropriateness',
            'engagement_level', 'goal_achievement',
            'review_text', 'would_recommend',
            'helpful_votes', 'created_at'
        ] 