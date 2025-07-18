"""
Modelos de contenido educativo para Ciudadela del Conocimiento ICFES
Sistema de contenido tipo Duolingo/Khan Academy
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
import uuid

User = get_user_model()


class ContentCategory(models.Model):
    """Categorías principales de contenido educativo"""
    
    CATEGORY_TYPES = [
        ('ACADEMIC', 'Académico'),
        ('SKILL', 'Habilidad'),
        ('TOPIC', 'Temático'),
        ('EXAM_PREP', 'Preparación Examen'),
        ('CAREER', 'Orientación Vocacional'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True, null=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    
    # Visualización
    icon = models.CharField(max_length=100, default='📚')  # Emoji o clase CSS
    color_theme = models.CharField(max_length=7, default='#3B82F6')  # Color hex
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Jerarquía
    parent_category = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='subcategories'
    )
    order = models.IntegerField(default=0)
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Configuración educativa
    min_grade_level = models.IntegerField(
        validators=[MinValueValidator(6), MaxValueValidator(11)], 
        default=9
    )
    max_grade_level = models.IntegerField(
        validators=[MinValueValidator(6), MaxValueValidator(11)], 
        default=11
    )
    
    # Metadatos
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['category_type', 'is_active']),
            models.Index(fields=['parent_category', 'order']),
            models.Index(fields=['is_featured', 'is_active']),
        ]
        verbose_name = 'Categoría de Contenido'
        verbose_name_plural = 'Categorías de Contenido'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('content:category_detail', kwargs={'slug': self.slug})
    
    @property
    def full_path(self):
        """Ruta completa de la categoría incluyendo padres"""
        if self.parent_category:
            return f"{self.parent_category.full_path} > {self.name}"
        return self.name


class ContentUnit(models.Model):
    """Unidades de contenido - equivalente a 'skills' en Duolingo"""
    
    UNIT_TYPES = [
        ('LESSON', 'Lección'),
        ('PRACTICE', 'Práctica'),
        ('QUIZ', 'Quiz'),
        ('PROJECT', 'Proyecto'),
        ('ASSESSMENT', 'Evaluación'),
        ('STORY', 'Historia Interactiva'),
        ('GAME', 'Juego Educativo'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('BEGINNER', 'Principiante'),
        ('BASIC', 'Básico'),
        ('INTERMEDIATE', 'Intermedio'),
        ('ADVANCED', 'Avanzado'),
        ('EXPERT', 'Experto'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Información básica
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220)
    description = models.TextField()
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES)
    
    # Relaciones
    category = models.ForeignKey(
        ContentCategory, 
        on_delete=models.CASCADE,
        related_name='content_units'
    )
    
    # Configuración educativa
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    estimated_duration_minutes = models.IntegerField(default=15)
    recommended_age_min = models.IntegerField(default=14)
    recommended_age_max = models.IntegerField(default=18)
    
    # Prerrequisitos
    prerequisite_units = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='unlocks_units'
    )
    
    # Gamificación
    xp_reward = models.IntegerField(default=10)
    hearts_required = models.IntegerField(default=1)  # Vitalidad necesaria
    completion_criteria = models.JSONField(default=dict)  # Criterios de completitud
    
    # Contenido multimedia
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    video_intro_url = models.URLField(max_length=500, blank=True, null=True)
    audio_intro_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Configuración de contenido
    has_theory = models.BooleanField(default=True)
    has_examples = models.BooleanField(default=True)
    has_practice = models.BooleanField(default=True)
    has_assessment = models.BooleanField(default=True)
    
    # Orden y navegación
    order = models.IntegerField(default=0)
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Métricas automáticas
    total_attempts = models.IntegerField(default=0)
    total_completions = models.IntegerField(default=0)
    average_completion_time = models.FloatField(default=0.0)
    average_rating = models.FloatField(default=0.0)
    
    # Metadatos
    learning_objectives = models.JSONField(default=list)  # Objetivos de aprendizaje
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_units'
        ordering = ['category', 'order', 'title']
        unique_together = ['category', 'slug']
        indexes = [
            models.Index(fields=['category', 'order']),
            models.Index(fields=['difficulty_level', 'is_active']),
            models.Index(fields=['unit_type', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
        ]
        verbose_name = 'Unidad de Contenido'
        verbose_name_plural = 'Unidades de Contenido'
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_level_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('content:unit_detail', kwargs={'uuid': self.uuid})
    
    @property
    def completion_rate(self):
        """Tasa de completitud de la unidad"""
        if self.total_attempts == 0:
            return 0.0
        return (self.total_completions / self.total_attempts) * 100
    
    @property
    def is_unlocked_for_user(self, user):
        """Verifica si la unidad está desbloqueada para un usuario"""
        if not self.prerequisite_units.exists():
            return True
        
        # Verificar que todas las unidades prerrequisito estén completadas
        completed_prerequisites = user.content_progress.filter(
            content_unit__in=self.prerequisite_units.all(),
            is_completed=True
        ).count()
        
        return completed_prerequisites == self.prerequisite_units.count()


class ContentLesson(models.Model):
    """Lecciones dentro de las unidades de contenido"""
    
    LESSON_TYPES = [
        ('THEORY', 'Teoría'),
        ('EXAMPLE', 'Ejemplo'),
        ('PRACTICE', 'Práctica'),
        ('QUIZ', 'Quiz'),
        ('INTERACTIVE', 'Interactivo'),
        ('VIDEO', 'Video'),
        ('READING', 'Lectura'),
    ]
    
    CONTENT_FORMATS = [
        ('TEXT', 'Texto'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('INTERACTIVE', 'Interactivo'),
        ('MIXED', 'Mixto'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Relación con unidad
    content_unit = models.ForeignKey(
        ContentUnit,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    
    # Información básica
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES)
    content_format = models.CharField(max_length=20, choices=CONTENT_FORMATS)
    order = models.IntegerField(default=0)
    
    # Contenido
    content_text = models.TextField(blank=True, null=True)
    content_html = models.TextField(blank=True, null=True)
    
    # Multimedia
    video_url = models.URLField(max_length=500, blank=True, null=True)
    audio_url = models.URLField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    interactive_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Configuración
    estimated_duration_seconds = models.IntegerField(default=300)  # 5 minutos
    is_mandatory = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Gamificación
    xp_reward = models.IntegerField(default=5)
    
    # Metadatos
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_lessons'
        ordering = ['content_unit', 'order']
        unique_together = ['content_unit', 'order']
        indexes = [
            models.Index(fields=['content_unit', 'order']),
            models.Index(fields=['lesson_type', 'is_active']),
        ]
        verbose_name = 'Lección de Contenido'
        verbose_name_plural = 'Lecciones de Contenido'
    
    def __str__(self):
        return f"{self.content_unit.title} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('content:lesson_detail', kwargs={'uuid': self.uuid})


class UserContentProgress(models.Model):
    """Progreso de usuarios en unidades de contenido"""
    
    PROGRESS_STATUS = [
        ('NOT_STARTED', 'No Iniciado'),
        ('IN_PROGRESS', 'En Progreso'),
        ('COMPLETED', 'Completado'),
        ('MASTERED', 'Dominado'),
        ('NEEDS_REVIEW', 'Necesita Revisión'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_progress')
    content_unit = models.ForeignKey(ContentUnit, on_delete=models.CASCADE)
    
    # Estado del progreso
    status = models.CharField(max_length=20, choices=PROGRESS_STATUS, default='NOT_STARTED')
    progress_percentage = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    is_mastered = models.BooleanField(default=False)
    
    # Estadísticas de rendimiento
    attempts_count = models.IntegerField(default=0)
    best_score = models.FloatField(default=0.0)
    total_time_seconds = models.IntegerField(default=0)
    completion_time_seconds = models.IntegerField(default=0)
    
    # Fechas importantes
    first_attempt_at = models.DateTimeField(blank=True, null=True)
    last_attempt_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    mastered_at = models.DateTimeField(blank=True, null=True)
    
    # Gamificación
    xp_earned = models.IntegerField(default=0)
    hearts_spent = models.IntegerField(default=0)
    
    # Datos detallados de progreso
    lesson_progress = models.JSONField(default=dict)  # {lesson_id: completion_data}
    mistakes_data = models.JSONField(default=list)    # Errores cometidos para aprendizaje
    
    # Metadatos
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_content_progress'
        unique_together = ['user', 'content_unit']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['content_unit', 'is_completed']),
            models.Index(fields=['user', 'updated_at']),
        ]
        verbose_name = 'Progreso de Contenido del Usuario'
        verbose_name_plural = 'Progreso de Contenido de los Usuarios'
    
    def __str__(self):
        return f"{self.user.username} - {self.content_unit.title} ({self.progress_percentage:.1f}%)"
    
    def calculate_progress(self):
        """Calcula el progreso basado en las lecciones completadas"""
        total_lessons = self.content_unit.lessons.filter(is_mandatory=True).count()
        if total_lessons == 0:
            return 0.0
        
        completed_lessons = sum(
            1 for lesson_id, data in self.lesson_progress.items()
            if data.get('completed', False)
        )
        
        return (completed_lessons / total_lessons) * 100
    
    def update_progress(self):
        """Actualiza el progreso automáticamente"""
        self.progress_percentage = self.calculate_progress()
        self.is_completed = self.progress_percentage >= 100.0
        
        if self.is_completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        
        self.save()


class ContentRating(models.Model):
    """Calificaciones y reseñas de contenido por usuarios"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_unit = models.ForeignKey(ContentUnit, on_delete=models.CASCADE, related_name='ratings')
    
    # Calificación
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Reseña
    review_text = models.TextField(blank=True, null=True)
    
    # Aspectos específicos (1-5)
    content_quality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    difficulty_appropriateness = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    engagement_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    
    # Utilidad
    is_helpful = models.BooleanField(default=True)
    would_recommend = models.BooleanField(default=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_ratings'
        unique_together = ['user', 'content_unit']
        indexes = [
            models.Index(fields=['content_unit', 'rating']),
            models.Index(fields=['user', 'created_at']),
        ]
        verbose_name = 'Calificación de Contenido'
        verbose_name_plural = 'Calificaciones de Contenido'
    
    def __str__(self):
        return f"{self.user.username} - {self.content_unit.title}: {self.rating}/5"


class ContentBookmark(models.Model):
    """Marcadores de contenido favorito de usuarios"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_bookmarks')
    content_unit = models.ForeignKey(ContentUnit, on_delete=models.CASCADE, related_name='bookmarks')
    
    # Organización
    notes = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'content_bookmarks'
        unique_together = ['user', 'content_unit']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
        verbose_name = 'Marcador de Contenido'
        verbose_name_plural = 'Marcadores de Contenido'
    
    def __str__(self):
        return f"{self.user.username} ♥ {self.content_unit.title}" 