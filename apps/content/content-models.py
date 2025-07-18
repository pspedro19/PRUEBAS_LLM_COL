# apps/content/models.py
"""
Modelos para contenido educativo: videos, explicaciones, recursos
Autor: Ciudadela del Conocimiento
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class EducationalContent(models.Model):
    """
    Contenido educativo: videos, artículos, infografías, podcasts
    """
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('article', 'Artículo'),
        ('infographic', 'Infografía'),
        ('podcast', 'Podcast'),
        ('interactive', 'Interactivo'),
        ('pdf', 'PDF'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('basic', 'Básico'),
        ('intermediate', 'Intermedio'),
        ('advanced', 'Avanzado'),
    ]
    
    # Identificación
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    
    # Tipo y categorización
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES)
    description = models.TextField()
    summary = models.TextField(max_length=500, help_text="Resumen corto para preview")
    
    # URLs y archivos
    url = models.URLField(max_length=500, blank=True)
    embed_url = models.URLField(max_length=500, blank=True, help_text="URL para iframe")
    thumbnail_url = models.URLField(max_length=500)
    preview_url = models.URLField(max_length=500, blank=True, help_text="Preview de 30 segundos")
    
    # Relaciones con ICFES
    area_evaluacion = models.ForeignKey(
        'icfes.AreaEvaluacion',
        on_delete=models.SET_NULL,
        null=True,
        related_name='educational_content'
    )
    competencias = models.ManyToManyField(
        'icfes.CompetenciaICFES',
        related_name='educational_content',
        blank=True
    )
    componentes = models.ManyToManyField(
        'icfes.ComponenteConocimiento',
        related_name='educational_content',
        blank=True
    )
    
    # Metadata del contenido
    duration_seconds = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Duración en segundos (videos/podcasts)"
    )
    reading_time_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Tiempo de lectura estimado"
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_LEVELS,
        default='intermediate'
    )
    
    # Tags y búsqueda
    tags = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )
    keywords = models.TextField(blank=True, help_text="Palabras clave para búsqueda")
    
    # Información del autor/fuente
    author_name = models.CharField(max_length=255, blank=True)
    author_bio = models.TextField(blank=True)
    source_name = models.CharField(max_length=255, blank=True)
    source_url = models.URLField(max_length=500, blank=True)
    
    # Estadísticas
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    rating_count = models.IntegerField(default=0)
    
    # Control
    is_premium = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'educational_content'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['content_type', 'is_active']),
            models.Index(fields=['area_evaluacion', 'difficulty_level']),
            models.Index(fields=['-view_count']),
            models.Index(fields=['slug']),
            models.Index(fields=['uuid']),
        ]
        verbose_name = "Contenido Educativo"
        verbose_name_plural = "Contenidos Educativos"
    
    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"


class QuestionExplanation(models.Model):
    """
    Explicaciones detalladas para cada pregunta ICFES
    """
    EXPLANATION_TYPES = [
        ('text', 'Texto'),
        ('video', 'Video'),
        ('step_by_step', 'Paso a Paso'),
        ('visual', 'Visual/Diagrama'),
        ('ai_generated', 'Generada por IA'),
    ]
    
    # Relación con pregunta
    pregunta = models.ForeignKey(
        'icfes.PreguntaICFES',
        on_delete=models.CASCADE,
        related_name='explanations'
    )
    
    # Tipo de explicación
    explanation_type = models.CharField(
        max_length=50,
        choices=EXPLANATION_TYPES,
        default='text'
    )
    
    # Contenido principal
    title = models.CharField(max_length=255, default="Explicación")
    content = models.TextField(help_text="Contenido principal de la explicación")
    summary = models.TextField(
        max_length=500,
        help_text="Resumen rápido de la explicación"
    )
    
    # Contenido estructurado
    steps = models.JSONField(default=list, blank=True)
    # Ejemplo: [
    #   {"step": 1, "title": "Identificar datos", "content": "..."},
    #   {"step": 2, "title": "Aplicar fórmula", "content": "..."}
    # ]
    
    visual_aids = models.JSONField(default=dict, blank=True)
    # Ejemplo: {
    #   "diagrams": ["url1", "url2"],
    #   "formulas": ["F = ma", "E = mc²"],
    #   "graphs": [{"type": "bar", "data": {...}}]
    # }
    
    # Errores comunes y tips
    common_mistakes = ArrayField(
        models.TextField(),
        default=list,
        blank=True,
        help_text="Errores comunes que cometen los estudiantes"
    )
    pro_tips = ArrayField(
        models.TextField(),
        default=list,
        blank=True,
        help_text="Tips profesionales para resolver"
    )
    memory_tricks = models.TextField(
        blank=True,
        help_text="Trucos mnemotécnicos o reglas para recordar"
    )
    
    # Conceptos relacionados
    key_concepts = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    prerequisites = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Conceptos que debe saber antes"
    )
    
    # Contenido relacionado
    related_content = models.ManyToManyField(
        EducationalContent,
        related_name='question_explanations',
        blank=True
    )
    related_questions = models.ManyToManyField(
        'icfes.PreguntaICFES',
        related_name='related_explanations',
        blank=True
    )
    
    # Metadata
    difficulty_addressed = models.CharField(
        max_length=20,
        choices=[
            ('conceptual', 'Error Conceptual'),
            ('procedural', 'Error de Procedimiento'),
            ('calculation', 'Error de Cálculo'),
            ('interpretation', 'Error de Interpretación'),
            ('careless', 'Error por Descuido'),
        ],
        blank=True
    )
    
    # Control
    is_official = models.BooleanField(
        default=False,
        help_text="Si es la explicación oficial del ICFES"
    )
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Estadísticas
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    # Timestamps
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_explanations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'question_explanations'
        ordering = ['-helpful_count', '-created_at']
        indexes = [
            models.Index(fields=['pregunta', 'explanation_type']),
            models.Index(fields=['is_official', 'is_active']),
        ]
    
    def __str__(self):
        return f"Explicación para {self.pregunta.id} ({self.explanation_type})"


class UserContentInteraction(models.Model):
    """
    Interacciones del usuario con el contenido educativo
    """
    INTERACTION_TYPES = [
        ('view', 'Vista'),
        ('like', 'Me gusta'),
        ('dislike', 'No me gusta'),
        ('save', 'Guardar'),
        ('share', 'Compartir'),
        ('complete', 'Completado'),
        ('rating', 'Calificación'),
    ]
    
    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='content_interactions'
    )
    content = models.ForeignKey(
        EducationalContent,
        on_delete=models.CASCADE,
        related_name='user_interactions'
    )
    
    # Tipo de interacción
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    
    # Detalles
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    watch_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje visto (para videos)"
    )
    time_spent_seconds = models.IntegerField(default=0)
    
    # Notas y comentarios
    notes = models.TextField(blank=True, help_text="Notas privadas del usuario")
    is_favorite = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_content_interactions'
        unique_together = [['user', 'content', 'interaction_type']]
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['content', 'interaction_type']),
            models.Index(fields=['-created_at']),
        ]


class ExplanationFeedback(models.Model):
    """
    Feedback de usuarios sobre las explicaciones
    """
    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='explanation_feedback'
    )
    explanation = models.ForeignKey(
        QuestionExplanation,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    
    # Feedback
    is_helpful = models.BooleanField()
    feedback_text = models.TextField(blank=True)
    
    # Categorización del problema
    issue_type = models.CharField(
        max_length=50,
        choices=[
            ('too_complex', 'Muy compleja'),
            ('too_simple', 'Muy simple'),
            ('incorrect', 'Incorrecta'),
            ('confusing', 'Confusa'),
            ('missing_info', 'Falta información'),
            ('other', 'Otro'),
        ],
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'explanation_feedback'
        unique_together = [['user', 'explanation']]
        indexes = [
            models.Index(fields=['explanation', 'is_helpful']),
            models.Index(fields=['-created_at']),
        ]


class ContentRecommendation(models.Model):
    """
    Recomendaciones de contenido personalizadas
    """
    RECOMMENDATION_REASONS = [
        ('weak_area', 'Área débil detectada'),
        ('similar_users', 'Usuarios similares lo vieron'),
        ('trending', 'Tendencia actual'),
        ('new_content', 'Contenido nuevo'),
        ('follow_up', 'Continuación de tema'),
        ('ai_suggested', 'Sugerido por IA'),
    ]
    
    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='content_recommendations'
    )
    content = models.ForeignKey(
        EducationalContent,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    # Razón de la recomendación
    reason = models.CharField(max_length=50, choices=RECOMMENDATION_REASONS)
    reason_detail = models.TextField(blank=True)
    
    # Prioridad y contexto
    priority = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    context_data = models.JSONField(default=dict, blank=True)
    # Ejemplo: {
    #   "weak_competency": "inferencia_textual",
    #   "recent_errors": 3,
    #   "improvement_potential": 0.85
    # }
    
    # Estado
    is_seen = models.BooleanField(default=False)
    is_clicked = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    # Feedback
    was_helpful = models.BooleanField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    seen_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'content_recommendations'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_seen', '-priority']),
            models.Index(fields=['reason', '-created_at']),
        ]
