"""
Modelos de Learning Paths para Ciudadela del Conocimiento ICFES
Sistema de rutas de aprendizaje tipo Duolingo
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
import uuid
from datetime import timedelta

User = get_user_model()


class LearningPath(models.Model):
    """Rutas de aprendizaje - equivalente a 'courses' en Duolingo"""
    
    PATH_TYPES = [
        ('ICFES_PREP', 'Preparación ICFES'),
        ('SUBJECT_MASTERY', 'Dominio de Materia'),
        ('SKILL_DEVELOPMENT', 'Desarrollo de Habilidades'),
        ('CAREER_EXPLORATION', 'Exploración Vocacional'),
        ('CHALLENGE', 'Desafío Especial'),
        ('CUSTOM', 'Personalizado'),
    ]
    
    PATH_STATUS = [
        ('DRAFT', 'Borrador'),
        ('ACTIVE', 'Activo'),
        ('FEATURED', 'Destacado'),
        ('ARCHIVED', 'Archivado'),
        ('MAINTENANCE', 'Mantenimiento'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('BEGINNER', 'Principiante'),
        ('INTERMEDIATE', 'Intermedio'), 
        ('ADVANCED', 'Avanzado'),
        ('EXPERT', 'Experto'),
        ('ADAPTIVE', 'Adaptativo'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Información básica
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    
    # Clasificación
    path_type = models.CharField(max_length=20, choices=PATH_TYPES)
    status = models.CharField(max_length=20, choices=PATH_STATUS, default='DRAFT')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    
    # Configuración educativa
    target_icfes_areas = models.JSONField(default=list)  # ['MATHEMATICS', 'READING']
    estimated_duration_hours = models.IntegerField(default=40)
    recommended_weekly_hours = models.IntegerField(default=5)
    min_grade_level = models.IntegerField(default=9)
    max_grade_level = models.IntegerField(default=11)
    
    # Gamificación
    total_xp_available = models.IntegerField(default=0)  # Se calcula automáticamente
    completion_xp_bonus = models.IntegerField(default=100)
    mastery_xp_bonus = models.IntegerField(default=200)
    
    # Prerrequisitos
    prerequisite_paths = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='unlocks_paths'
    )
    required_hero_class = models.CharField(max_length=2, blank=True, null=True)
    required_level = models.IntegerField(default=1)
    
    # Contenido multimedia
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)
    intro_video_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Personalización visual
    primary_color = models.CharField(max_length=7, default='#3B82F6')
    secondary_color = models.CharField(max_length=7, default='#EFF6FF')
    icon_emoji = models.CharField(max_length=10, default='🎓')
    
    # Configuración de características
    has_adaptive_difficulty = models.BooleanField(default=True)
    has_peer_comparison = models.BooleanField(default=True)
    has_leaderboards = models.BooleanField(default=True)
    has_streaks = models.BooleanField(default=True)
    has_certificates = models.BooleanField(default=True)
    
    # Estado del contenido
    is_premium = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_ai_enhanced = models.BooleanField(default=False)
    
    # Métricas automáticas
    total_enrollments = models.IntegerField(default=0)
    total_completions = models.IntegerField(default=0)
    average_completion_time_hours = models.FloatField(default=0.0)
    average_rating = models.FloatField(default=0.0)
    
    # Configuración de IA
    ai_recommendations_enabled = models.BooleanField(default=True)
    adaptive_sequencing_enabled = models.BooleanField(default=True)
    personalized_feedback_enabled = models.BooleanField(default=True)
    
    # Metadatos
    learning_outcomes = models.JSONField(default=list)  # Resultados de aprendizaje esperados
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    
    # Auditoría
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'learning_paths'
        ordering = ['-is_featured', 'difficulty_level', 'name']
        indexes = [
            models.Index(fields=['path_type', 'status']),
            models.Index(fields=['difficulty_level', 'is_featured']),
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['is_premium', 'is_featured']),
        ]
        verbose_name = 'Ruta de Aprendizaje'
        verbose_name_plural = 'Rutas de Aprendizaje'
    
    def __str__(self):
        return f"{self.name} ({self.get_difficulty_level_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('learning:path_detail', kwargs={'slug': self.slug})
    
    @property
    def completion_rate(self):
        """Tasa de completitud del path"""
        if self.total_enrollments == 0:
            return 0.0
        return (self.total_completions / self.total_enrollments) * 100
    
    @property
    def estimated_weeks(self):
        """Semanas estimadas de duración"""
        if self.recommended_weekly_hours == 0:
            return 0
        return self.estimated_duration_hours / self.recommended_weekly_hours
    
    def is_accessible_for_user(self, user):
        """Verifica si el path es accesible para un usuario"""
        # Verificar nivel y clase de héroe
        if self.required_level and user.level < self.required_level:
            return False
        
        if self.required_hero_class and user.hero_class != self.required_hero_class:
            return False
        
        # Verificar prerrequisitos
        if self.prerequisite_paths.exists():
            completed_prerequisites = user.path_enrollments.filter(
                learning_path__in=self.prerequisite_paths.all(),
                is_completed=True
            ).count()
            return completed_prerequisites == self.prerequisite_paths.count()
        
        return True


class LearningPathUnit(models.Model):
    """Unidades dentro de una ruta de aprendizaje - equivalente a 'units' en Duolingo"""
    
    UNIT_TYPES = [
        ('FOUNDATION', 'Fundamentos'),
        ('CORE', 'Núcleo'),
        ('PRACTICE', 'Práctica'),
        ('ASSESSMENT', 'Evaluación'),
        ('PROJECT', 'Proyecto'),
        ('REVIEW', 'Repaso'),
        ('BONUS', 'Bonus'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Relación con path
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='units'
    )
    
    # Información básica
    title = models.CharField(max_length=200)
    description = models.TextField()
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES)
    order = models.IntegerField(default=0)
    
    # Configuración educativa
    estimated_duration_minutes = models.IntegerField(default=60)
    difficulty_modifier = models.FloatField(default=1.0)  # Multiplicador de dificultad
    
    # Gamificación
    xp_reward = models.IntegerField(default=50)
    hearts_required = models.IntegerField(default=1)
    
    # Configuración de desbloqueo
    unlock_criteria = models.JSONField(default=dict)  # Criterios para desbloquear
    is_bonus = models.BooleanField(default=False)
    is_optional = models.BooleanField(default=False)
    
    # Contenido multimedia
    icon_emoji = models.CharField(max_length=10, default='📖')
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    
    # Metadatos
    learning_objectives = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_path_units'
        ordering = ['learning_path', 'order']
        unique_together = ['learning_path', 'order']
        indexes = [
            models.Index(fields=['learning_path', 'order']),
            models.Index(fields=['unit_type', 'is_active']),
        ]
        verbose_name = 'Unidad de Ruta de Aprendizaje'
        verbose_name_plural = 'Unidades de Rutas de Aprendizaje'
    
    def __str__(self):
        return f"{self.learning_path.name} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('learning:unit_detail', kwargs={'uuid': self.uuid})


class LearningPathLesson(models.Model):
    """Lecciones dentro de unidades - equivalente a 'lessons' en Duolingo"""
    
    LESSON_TYPES = [
        ('INTRO', 'Introducción'),
        ('CONCEPT', 'Concepto'),
        ('PRACTICE', 'Práctica'),
        ('QUIZ', 'Quiz'),
        ('STORY', 'Historia'),
        ('SPEAKING', 'Expresión Oral'),
        ('LISTENING', 'Comprensión Auditiva'),
        ('CHALLENGE', 'Desafío'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Relación con unidad
    path_unit = models.ForeignKey(
        LearningPathUnit,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    
    # Información básica
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES)
    order = models.IntegerField(default=0)
    
    # Relación con contenido educativo
    content_units = models.ManyToManyField(
        'content.ContentUnit',
        blank=True,
        related_name='learning_path_lessons'
    )
    
    # Relación con preguntas ICFES
    icfes_questions = models.ManyToManyField(
        'icfes.PreguntaICFES',
        blank=True,
        related_name='learning_path_lessons'
    )
    
    # Configuración
    estimated_duration_minutes = models.IntegerField(default=15)
    difficulty_level = models.CharField(max_length=20, default='INTERMEDIATE')
    max_attempts = models.IntegerField(default=3)
    passing_score = models.FloatField(default=70.0)
    
    # Gamificación
    xp_reward = models.IntegerField(default=10)
    perfect_score_bonus = models.IntegerField(default=5)
    
    # Configuración de ayudas
    hints_enabled = models.BooleanField(default=True)
    explanations_enabled = models.BooleanField(default=True)
    skip_enabled = models.BooleanField(default=False)
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_assessment = models.BooleanField(default=False)
    
    # Metadatos
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_path_lessons'
        ordering = ['path_unit', 'order']
        unique_together = ['path_unit', 'order']
        indexes = [
            models.Index(fields=['path_unit', 'order']),
            models.Index(fields=['lesson_type', 'is_active']),
        ]
        verbose_name = 'Lección de Ruta de Aprendizaje'
        verbose_name_plural = 'Lecciones de Rutas de Aprendizaje'
    
    def __str__(self):
        return f"{self.path_unit.title} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('learning:lesson_detail', kwargs={'uuid': self.uuid})


class UserPathEnrollment(models.Model):
    """Inscripciones de usuarios en rutas de aprendizaje"""
    
    ENROLLMENT_STATUS = [
        ('ACTIVE', 'Activo'),
        ('PAUSED', 'Pausado'),
        ('COMPLETED', 'Completado'),
        ('DROPPED', 'Abandonado'),
        ('EXPIRED', 'Expirado'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='path_enrollments')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='enrollments')
    
    # Estado de la inscripción
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='ACTIVE')
    
    # Progreso
    current_unit_order = models.IntegerField(default=0)
    current_lesson_order = models.IntegerField(default=0)
    progress_percentage = models.FloatField(default=0.0)
    
    # Estadísticas de rendimiento
    total_xp_earned = models.IntegerField(default=0)
    total_lessons_completed = models.IntegerField(default=0)
    total_time_minutes = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    
    # Configuración personalizada
    daily_goal_minutes = models.IntegerField(default=30)
    reminder_time = models.TimeField(blank=True, null=True)
    
    # Racha y motivación
    current_streak_days = models.IntegerField(default=0)
    max_streak_days = models.IntegerField(default=0)
    last_activity_date = models.DateField(blank=True, null=True)
    
    # Fechas importantes
    enrolled_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    paused_at = models.DateTimeField(blank=True, null=True)
    
    # Configuración de adaptación
    adaptive_difficulty_enabled = models.BooleanField(default=True)
    current_difficulty_modifier = models.FloatField(default=1.0)
    
    # Metadatos
    enrollment_metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'user_path_enrollments'
        unique_together = ['user', 'learning_path']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['learning_path', 'status']),
            models.Index(fields=['status', 'last_activity_date']),
        ]
        verbose_name = 'Inscripción a Ruta de Aprendizaje'
        verbose_name_plural = 'Inscripciones a Rutas de Aprendizaje'
    
    def __str__(self):
        return f"{self.user.username} → {self.learning_path.name} ({self.progress_percentage:.1f}%)"
    
    @property
    def is_completed(self):
        return self.status == 'COMPLETED'
    
    @property
    def estimated_completion_date(self):
        """Fecha estimada de completitud basada en el progreso actual"""
        if self.progress_percentage == 0:
            return None
        
        remaining_percentage = 100 - self.progress_percentage
        if self.daily_goal_minutes == 0:
            return None
        
        remaining_hours = (self.learning_path.estimated_duration_hours * remaining_percentage) / 100
        remaining_days = remaining_hours * 60 / self.daily_goal_minutes
        
        return timezone.now().date() + timedelta(days=int(remaining_days))
    
    def update_streak(self):
        """Actualiza la racha de días consecutivos"""
        today = timezone.now().date()
        
        if self.last_activity_date:
            days_diff = (today - self.last_activity_date).days
            
            if days_diff == 1:
                # Continuó la racha
                self.current_streak_days += 1
                self.max_streak_days = max(self.max_streak_days, self.current_streak_days)
            elif days_diff > 1:
                # Rompió la racha
                self.current_streak_days = 1
            # Si days_diff == 0, ya estudió hoy, no cambiar
        else:
            # Primera actividad
            self.current_streak_days = 1
            self.max_streak_days = 1
        
        self.last_activity_date = today
        self.save()


class UserLessonProgress(models.Model):
    """Progreso de usuarios en lecciones específicas"""
    
    LESSON_STATUS = [
        ('NOT_STARTED', 'No Iniciado'),
        ('IN_PROGRESS', 'En Progreso'),
        ('COMPLETED', 'Completado'),
        ('PERFECT', 'Perfecto'),
        ('NEEDS_REVIEW', 'Necesita Revisión'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    path_lesson = models.ForeignKey(LearningPathLesson, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(UserPathEnrollment, on_delete=models.CASCADE)
    
    # Estado de la lección
    status = models.CharField(max_length=20, choices=LESSON_STATUS, default='NOT_STARTED')
    
    # Estadísticas de rendimiento
    attempts_count = models.IntegerField(default=0)
    best_score = models.FloatField(default=0.0)
    last_score = models.FloatField(default=0.0)
    total_time_seconds = models.IntegerField(default=0)
    
    # Gamificación
    xp_earned = models.IntegerField(default=0)
    hearts_spent = models.IntegerField(default=0)
    hints_used = models.IntegerField(default=0)
    
    # Fechas
    first_attempt_at = models.DateTimeField(blank=True, null=True)
    last_attempt_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Datos detallados
    attempt_data = models.JSONField(default=list)  # Historial de intentos
    mistake_patterns = models.JSONField(default=dict)  # Patrones de errores
    
    # Metadatos
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_lesson_progress'
        unique_together = ['user', 'path_lesson']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['enrollment', 'status']),
            models.Index(fields=['path_lesson', 'completed_at']),
        ]
        verbose_name = 'Progreso de Lección del Usuario'
        verbose_name_plural = 'Progreso de Lecciones de los Usuarios'
    
    def __str__(self):
        return f"{self.user.username} - {self.path_lesson.title} ({self.best_score:.1f}%)"
    
    @property
    def is_perfect(self):
        return self.status == 'PERFECT' or self.best_score == 100.0


class PathAchievement(models.Model):
    """Logros específicos de rutas de aprendizaje"""
    
    ACHIEVEMENT_TYPES = [
        ('COMPLETION', 'Completitud'),
        ('SPEED', 'Velocidad'),
        ('ACCURACY', 'Precisión'),
        ('STREAK', 'Racha'),
        ('PERFECT', 'Perfección'),
        ('MILESTONE', 'Hito'),
        ('SPECIAL', 'Especial'),
    ]
    
    RARITY_LEVELS = [
        ('COMMON', 'Común'),
        ('RARE', 'Raro'),
        ('EPIC', 'Épico'),
        ('LEGENDARY', 'Legendario'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    
    # Configuración visual
    icon_emoji = models.CharField(max_length=10, default='🏆')
    badge_color = models.CharField(max_length=7, default='#FFD700')
    rarity = models.CharField(max_length=20, choices=RARITY_LEVELS, default='COMMON')
    
    # Criterios de desbloqueo
    criteria = models.JSONField(default=dict)  # Criterios específicos
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='achievements',
        blank=True,
        null=True
    )
    
    # Recompensas
    xp_reward = models.IntegerField(default=50)
    special_rewards = models.JSONField(default=dict)  # Recompensas especiales
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_secret = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'path_achievements'
        indexes = [
            models.Index(fields=['achievement_type', 'is_active']),
            models.Index(fields=['learning_path', 'is_active']),
        ]
        verbose_name = 'Logro de Ruta'
        verbose_name_plural = 'Logros de Rutas'
    
    def __str__(self):
        return f"{self.name} ({self.get_achievement_type_display()})"


class UserPathAchievement(models.Model):
    """Logros obtenidos por usuarios en rutas de aprendizaje"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='path_achievements')
    achievement = models.ForeignKey(PathAchievement, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(UserPathEnrollment, on_delete=models.CASCADE, blank=True, null=True)
    
    # Detalles del logro
    progress_when_earned = models.FloatField(default=0.0)
    xp_earned = models.IntegerField(default=0)
    
    # Metadatos del logro
    achievement_data = models.JSONField(default=dict)  # Datos específicos del logro
    
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_path_achievements'
        unique_together = ['user', 'achievement']
        indexes = [
            models.Index(fields=['user', 'earned_at']),
            models.Index(fields=['achievement', 'earned_at']),
        ]
        verbose_name = 'Logro de Usuario en Ruta'
        verbose_name_plural = 'Logros de Usuarios en Rutas'
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class LearningPathReview(models.Model):
    """Reseñas de rutas de aprendizaje por usuarios"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='reviews')
    enrollment = models.ForeignKey(UserPathEnrollment, on_delete=models.CASCADE)
    
    # Calificación general
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Aspectos específicos
    content_quality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    difficulty_appropriateness = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    engagement_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    goal_achievement = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Reseña textual
    review_text = models.TextField(blank=True, null=True)
    
    # Recomendación
    would_recommend = models.BooleanField(default=True)
    
    # Utilidad
    helpful_votes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_path_reviews'
        unique_together = ['user', 'learning_path']
        indexes = [
            models.Index(fields=['learning_path', 'rating']),
            models.Index(fields=['user', 'created_at']),
        ]
        verbose_name = 'Reseña de Ruta de Aprendizaje'
        verbose_name_plural = 'Reseñas de Rutas de Aprendizaje'
    
    def __str__(self):
        return f"{self.user.username} - {self.learning_path.name}: {self.rating}/5" 