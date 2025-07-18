# apps/learning/models.py
"""
Modelos para Learning Paths estilo Duolingo y Simulacros ICFES
Autor: Ciudadela del Conocimiento
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class LearningPath(models.Model):
    """
    Rutas de aprendizaje estilo Duolingo
    Cada path es una unidad temática (ej: "Razonamiento Cuantitativo Básico")
    """
    name = models.CharField(max_length=255, verbose_name="Nombre del Path")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(verbose_name="Descripción")
    icon_url = models.URLField(max_length=500, blank=True)
    color_theme = models.CharField(max_length=7, default="#6B46C1")  # Hex color
    
    # Orden y estructura
    order_index = models.IntegerField(default=0, verbose_name="Orden de visualización")
    area_evaluacion = models.ForeignKey(
        'icfes.AreaEvaluacion', 
        on_delete=models.CASCADE,
        related_name='learning_paths'
    )
    
    # Características del path
    estimated_hours = models.IntegerField(default=10, verbose_name="Horas estimadas")
    total_nodes = models.IntegerField(default=0, verbose_name="Total de nodos")
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Principiante'),
            ('intermediate', 'Intermedio'),
            ('advanced', 'Avanzado'),
            ('expert', 'Experto')
        ],
        default='beginner'
    )
    
    # Premium y desbloqueo
    is_premium = models.BooleanField(default=False)
    unlock_requirements = models.JSONField(default=dict, blank=True)
    # Ejemplo: {"min_level": 5, "completed_paths": ["slug1", "slug2"]}
    
    # Recompensas
    completion_xp = models.IntegerField(default=1000)
    completion_rewards = models.JSONField(default=dict, blank=True)
    # Ejemplo: {"coins": 500, "items": ["power_up_1"], "title": "Maestro Cuantitativo"}
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_paths'
        ordering = ['order_index', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['area_evaluacion', 'order_index']),
        ]
        verbose_name = "Learning Path"
        verbose_name_plural = "Learning Paths"
    
    def __str__(self):
        return f"{self.name} ({self.get_difficulty_level_display()})"


class LearningPathNode(models.Model):
    """
    Nodos individuales en un Learning Path
    Pueden ser lecciones, checkpoints, o boss battles
    """
    NODE_TYPES = [
        ('lesson', 'Lección Normal'),
        ('checkpoint', 'Checkpoint'),
        ('boss_battle', 'Boss Battle'),
        ('review', 'Repaso'),
        ('bonus', 'Bonus'),
    ]
    
    # Relaciones
    path = models.ForeignKey(
        LearningPath, 
        on_delete=models.CASCADE,
        related_name='nodes'
    )
    parent_node = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='children'
    )
    
    # Información básica
    node_type = models.CharField(max_length=50, choices=NODE_TYPES, default='lesson')
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    icon_emoji = models.CharField(max_length=10, default="📚")
    
    # Posicionamiento visual (para UI tipo árbol)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    order_index = models.IntegerField(default=0)
    
    # Desbloqueo y requisitos
    is_locked = models.BooleanField(default=True)
    unlock_requirements = models.JSONField(default=dict)
    # Ejemplo: {
    #   "min_score": 80,
    #   "prerequisite_nodes": [1, 2, 3],
    #   "min_streak": 3,
    #   "special_condition": "perfect_previous_node"
    # }
    
    # Contenido del nodo
    content = models.JSONField(default=dict)
    # Ejemplo: {
    #   "question_ids": ["uuid1", "uuid2", ...],
    #   "theory_content": "markdown content",
    #   "video_url": "https://...",
    #   "tips": ["tip1", "tip2"],
    #   "time_limit_minutes": 10
    # }
    
    # Configuración de práctica
    questions_count = models.IntegerField(default=10)
    passing_score = models.IntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    allow_hints = models.BooleanField(default=True)
    lives_count = models.IntegerField(default=3)  # Vidas por intento
    
    # Recompensas
    base_xp_reward = models.IntegerField(default=100)
    perfect_bonus_xp = models.IntegerField(default=50)
    speed_bonus_xp = models.IntegerField(default=30)
    coin_reward = models.IntegerField(default=20)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_path_nodes'
        ordering = ['path', 'order_index']
        indexes = [
            models.Index(fields=['path', 'order_index']),
            models.Index(fields=['node_type']),
        ]
        unique_together = [['path', 'position_x', 'position_y']]
    
    def __str__(self):
        return f"{self.path.name} - {self.title} ({self.node_type})"


class UserPathProgress(models.Model):
    """
    Progreso del usuario en cada Learning Path
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='path_progress'
    )
    path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    # Estado actual
    current_node = models.ForeignKey(
        LearningPathNode,
        on_delete=models.SET_NULL,
        null=True,
        related_name='current_users'
    )
    nodes_completed = ArrayField(
        models.IntegerField(),
        default=list,
        blank=True
    )
    nodes_unlocked = ArrayField(
        models.IntegerField(),
        default=list,
        blank=True
    )
    
    # Progreso
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    total_xp_earned = models.IntegerField(default=0)
    total_coins_earned = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    
    # Estadísticas
    total_time_spent_minutes = models.IntegerField(default=0)
    average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    perfect_nodes_count = models.IntegerField(default=0)
    total_attempts = models.IntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_path_progress'
        unique_together = [['user', 'path']]
        indexes = [
            models.Index(fields=['user', 'completion_percentage']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.path.name} ({self.completion_percentage}%)"


class NodeAttempt(models.Model):
    """
    Intentos del usuario en cada nodo
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='node_attempts'
    )
    node = models.ForeignKey(
        LearningPathNode,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    # Resultado del intento
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    passed = models.BooleanField(default=False)
    is_perfect = models.BooleanField(default=False)
    lives_remaining = models.IntegerField(default=0)
    
    # Detalles
    questions_answered = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    hints_used = models.IntegerField(default=0)
    time_spent_seconds = models.IntegerField(default=0)
    
    # Recompensas obtenidas
    xp_earned = models.IntegerField(default=0)
    coins_earned = models.IntegerField(default=0)
    bonuses_earned = models.JSONField(default=list)
    
    # Metadata
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'node_attempts'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'node', '-started_at']),
        ]


# ==================== SIMULACROS ICFES ====================

class Simulacro(models.Model):
    """
    Simulacros completos tipo examen ICFES real
    """
    DIFFICULTY_LEVELS = [
        ('easy', 'Fácil'),
        ('medium', 'Intermedio'),
        ('hard', 'Difícil'),
        ('realistic', 'Realista ICFES'),
    ]
    
    # Información básica
    name = models.CharField(max_length=255)
    description = models.TextField()
    code = models.CharField(max_length=50, unique=True)
    
    # Configuración
    duration_minutes = models.IntegerField(default=270)  # 4.5 horas como el real
    total_questions = models.IntegerField(default=0)
    question_distribution = models.JSONField(default=dict)
    # Ejemplo: {
    #   "lectura_critica": 41,
    #   "matematicas": 25,
    #   "sociales_ciudadanas": 25,
    #   "ciencias_naturales": 25,
    #   "ingles": 25
    # }
    
    # Características
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_LEVELS,
        default='medium'
    )
    is_official = models.BooleanField(default=False)
    is_diagnostic = models.BooleanField(default=False)
    allows_pause = models.BooleanField(default=True)
    shows_timer = models.BooleanField(default=True)
    
    # Requisitos
    min_level_required = models.IntegerField(default=1)
    is_premium = models.BooleanField(default=False)
    unlock_requirements = models.JSONField(default=dict, blank=True)
    
    # Metadata
    times_taken = models.IntegerField(default=0)
    average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'simulacros'
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['difficulty_level', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_difficulty_level_display()})"


class SimulacroSession(models.Model):
    """
    Sesión de simulacro de un usuario
    """
    STATUS_CHOICES = [
        ('not_started', 'No iniciado'),
        ('in_progress', 'En progreso'),
        ('paused', 'Pausado'),
        ('completed', 'Completado'),
        ('abandoned', 'Abandonado'),
    ]
    
    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='simulacro_sessions'
    )
    simulacro = models.ForeignKey(
        Simulacro,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    # Estado
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='not_started'
    )
    session_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Progreso
    current_section = models.CharField(max_length=50, blank=True)
    current_question_index = models.IntegerField(default=0)
    questions_answered = models.IntegerField(default=0)
    sections_completed = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )
    
    # Tiempo
    time_spent_seconds = models.IntegerField(default=0)
    time_remaining_seconds = models.IntegerField(null=True, blank=True)
    pause_count = models.IntegerField(default=0)
    total_pause_time_seconds = models.IntegerField(default=0)
    
    # Resultados
    score_total = models.IntegerField(null=True, blank=True)
    percentil_nacional = models.IntegerField(null=True, blank=True)
    areas_scores = models.JSONField(default=dict, blank=True)
    # Ejemplo: {
    #   "lectura_critica": {"score": 85, "percentil": 92},
    #   "matematicas": {"score": 72, "percentil": 78},
    #   ...
    # }
    
    # Análisis
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    
    # Metadata
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'simulacro_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['session_uuid']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.simulacro.name} ({self.status})"


class SimulacroAnswer(models.Model):
    """
    Respuestas individuales en un simulacro
    """
    session = models.ForeignKey(
        SimulacroSession,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    pregunta = models.ForeignKey(
        'icfes.PreguntaICFES',
        on_delete=models.CASCADE,
        related_name='simulacro_answers'
    )
    
    # Respuesta
    section = models.CharField(max_length=50)
    question_number = models.IntegerField()
    selected_option = models.CharField(max_length=1, blank=True)
    is_correct = models.BooleanField(default=False)
    
    # Comportamiento
    time_spent_seconds = models.IntegerField(default=0)
    changed_answer = models.BooleanField(default=False)
    marked_for_review = models.BooleanField(default=False)
    confidence_level = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Metadata
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'simulacro_answers'
        unique_together = [['session', 'pregunta']]
        indexes = [
            models.Index(fields=['session', 'section']),
            models.Index(fields=['is_correct']),
        ]
