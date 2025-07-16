"""
Modelos ICFES para Ciudadela del Conocimiento
Sistema de simulacros y evaluaciones ICFES
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
from datetime import timedelta

User = get_user_model()


class ICFESExam(models.Model):
    """Modelo para exámenes ICFES oficiales"""
    
    EXAM_TYPES = [
        ('SABER_11', 'Saber 11'),
        ('SABER_PRO', 'Saber Pro'),
        ('PRACTICE', 'Simulacro'),
        ('DIAGNOSTIC', 'Diagnóstico'),
    ]
    
    EXAM_PERIODS = [
        ('2024-1', '2024 Período 1'),
        ('2024-2', '2024 Período 2'),
        ('2023-1', '2023 Período 1'),
        ('2023-2', '2023 Período 2'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    period = models.CharField(max_length=10, choices=EXAM_PERIODS)
    
    # Configuración del examen
    duration_minutes = models.IntegerField(default=285)  # 4h 45min para ICFES real
    total_questions = models.IntegerField(default=158)  # Total ICFES completo
    
    # Configuración por área
    mathematics_questions = models.IntegerField(default=42)
    reading_questions = models.IntegerField(default=42)
    natural_sciences_questions = models.IntegerField(default=28)
    social_studies_questions = models.IntegerField(default=30)
    english_questions = models.IntegerField(default=16)
    
    # Puntajes
    max_score_per_area = models.IntegerField(default=100)
    global_max_score = models.IntegerField(default=500)
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_official = models.BooleanField(default=False)
    
    # Fechas
    registration_start = models.DateTimeField(blank=True, null=True)
    registration_end = models.DateTimeField(blank=True, null=True)
    exam_date = models.DateTimeField(blank=True, null=True)
    results_release_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'icfes_exams'
        ordering = ['-exam_date', 'name']
        indexes = [
            models.Index(fields=['exam_type', 'is_active']),
            models.Index(fields=['period', 'is_official']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_exam_type_display()}) - {self.period}"


class UserICFESSession(models.Model):
    """Sesiones de simulacro ICFES de usuarios"""
    
    SESSION_STATUS = [
        ('PENDING', 'Pendiente'),
        ('IN_PROGRESS', 'En Progreso'),
        ('COMPLETED', 'Completado'),
        ('ABANDONED', 'Abandonado'),
        ('EXPIRED', 'Expirado'),
    ]
    
    SESSION_TYPES = [
        ('FULL_EXAM', 'Examen Completo'),
        ('BY_AREA', 'Por Área'),
        ('ADAPTIVE', 'Adaptativo'),
        ('TIMED_PRACTICE', 'Práctica con Tiempo'),
        ('DIAGNOSTIC', 'Diagnóstico'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='icfes_sessions')
    icfes_exam = models.ForeignKey(ICFESExam, on_delete=models.CASCADE)
    
    # Configuración de la sesión
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='PENDING')
    
    # Filtros aplicados
    areas_filter = models.JSONField(default=list)  # ['MATHEMATICS', 'READING']
    difficulty_filter = models.CharField(max_length=10, blank=True, null=True)
    custom_time_limit = models.IntegerField(blank=True, null=True)  # Minutos
    
    # Progreso
    current_question_index = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    answered_questions = models.IntegerField(default=0)
    
    # Configuración de ayudas
    hints_enabled = models.BooleanField(default=True)
    immediate_feedback = models.BooleanField(default=False)
    explanation_after_answer = models.BooleanField(default=False)
    
    # Timestamps
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    
    # Tiempo total utilizado
    total_time_seconds = models.IntegerField(default=0)
    time_per_area = models.JSONField(default=dict)  # {'MATHEMATICS': 3600, 'READING': 2400}
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_icfes_sessions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['icfes_exam', 'session_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.icfes_exam.name} ({self.status})"
    
    def is_expired(self):
        """Verifica si la sesión ha expirado"""
        if self.status not in ['PENDING', 'IN_PROGRESS']:
            return False
        
        if not self.started_at:
            # Sesión no iniciada expira en 24 horas
            expire_time = self.created_at + timedelta(hours=24)
        else:
            # Sesión iniciada expira según tiempo límite
            time_limit = self.custom_time_limit or self.icfes_exam.duration_minutes
            expire_time = self.started_at + timedelta(minutes=time_limit)
        
        return timezone.now() > expire_time
    
    @property
    def completion_percentage(self):
        """Calcula el porcentaje de completitud"""
        if self.total_questions == 0:
            return 0.0
        return (self.answered_questions / self.total_questions) * 100


class ICFESResult(models.Model):
    """Resultados de evaluaciones ICFES"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='icfes_results')
    session = models.OneToOneField(UserICFESSession, on_delete=models.CASCADE, related_name='result')
    icfes_exam = models.ForeignKey(ICFESExam, on_delete=models.CASCADE)
    
    # Puntajes por área (0-100)
    mathematics_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    reading_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    natural_sciences_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    social_studies_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    english_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    
    # Puntaje global (0-500)
    global_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(500)],
        default=0
    )
    
    # Estadísticas detalladas
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    incorrect_answers = models.IntegerField(default=0)
    unanswered_questions = models.IntegerField(default=0)
    
    # Tiempo utilizado
    total_time_seconds = models.IntegerField(default=0)
    average_time_per_question = models.FloatField(default=0.0)
    
    # Ranking y percentiles
    national_percentile = models.FloatField(default=0.0)  # Percentil nacional
    regional_percentile = models.FloatField(default=0.0)  # Percentil regional
    school_percentile = models.FloatField(default=0.0)    # Percentil en su colegio
    
    # Análisis por dificultad
    easy_questions_correct = models.IntegerField(default=0)
    medium_questions_correct = models.IntegerField(default=0)
    hard_questions_correct = models.IntegerField(default=0)
    
    # Certificación oficial
    is_official = models.BooleanField(default=False)
    certificate_url = models.URLField(max_length=500, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'icfes_results'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['global_score', 'is_official']),
            models.Index(fields=['icfes_exam', 'global_score']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.icfes_exam.name}: {self.global_score}/500"
    
    @property
    def accuracy_percentage(self):
        """Calcula el porcentaje de precisión"""
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100
    
    def get_area_scores_dict(self):
        """Retorna diccionario con puntajes por área"""
        return {
            'MATHEMATICS': self.mathematics_score,
            'READING': self.reading_score,
            'NATURAL_SCIENCES': self.natural_sciences_score,
            'SOCIAL_STUDIES': self.social_studies_score,
            'ENGLISH': self.english_score,
        }
    
    def get_strongest_area(self):
        """Retorna el área con mejor puntaje"""
        scores = self.get_area_scores_dict()
        return max(scores, key=scores.get)
    
    def get_weakest_area(self):
        """Retorna el área con peor puntaje"""
        scores = self.get_area_scores_dict()
        return min(scores, key=scores.get)


class ICFESPrediction(models.Model):
    """Predicciones de puntaje ICFES basadas en IA"""
    
    PREDICTION_TYPES = [
        ('CURRENT', 'Predicción Actual'),
        ('30_DAYS', 'Predicción a 30 días'),
        ('60_DAYS', 'Predicción a 60 días'),
        ('EXAM_DATE', 'Predicción para fecha de examen'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('VERY_HIGH', 'Muy Alta'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='icfes_predictions')
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    
    # Puntajes predichos
    predicted_mathematics = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    predicted_reading = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    predicted_natural_sciences = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    predicted_social_studies = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    predicted_english = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    predicted_global = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(500)]
    )
    
    # Métricas de confianza
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_LEVELS)
    confidence_percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Factores considerados
    data_points_used = models.IntegerField(default=0)  # Número de evaluaciones consideradas
    study_hours_factor = models.FloatField(default=0.0)
    improvement_trend = models.FloatField(default=0.0)  # Tendencia de mejora (positiva/negativa)
    
    # Recomendaciones de IA
    study_plan_recommendations = models.JSONField(default=dict)
    weak_areas_focus = models.JSONField(default=list)
    estimated_study_hours_needed = models.IntegerField(default=0)
    
    # Comparación con objetivos
    target_university_score = models.IntegerField(blank=True, null=True)
    probability_reaching_target = models.FloatField(default=0.0)
    
    # Metadatos
    algorithm_version = models.CharField(max_length=10, default='1.0')
    factors_analyzed = models.JSONField(default=dict)
    
    prediction_date = models.DateTimeField(auto_now_add=True)
    target_date = models.DateTimeField(blank=True, null=True)  # Fecha objetivo para la predicción
    
    class Meta:
        db_table = 'icfes_predictions'
        indexes = [
            models.Index(fields=['user', 'prediction_date']),
            models.Index(fields=['prediction_type', 'confidence_level']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Predicción {self.predicted_global}/500 ({self.confidence_level})"


class StudyPlan(models.Model):
    """Planes de estudio personalizados para ICFES"""
    
    PLAN_TYPES = [
        ('INTENSIVE', 'Intensivo'),
        ('REGULAR', 'Regular'),
        ('LIGHT', 'Ligero'),
        ('CUSTOM', 'Personalizado'),
        ('AI_GENERATED', 'Generado por IA'),
    ]
    
    PLAN_STATUS = [
        ('ACTIVE', 'Activo'),
        ('PAUSED', 'Pausado'),
        ('COMPLETED', 'Completado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_plans')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    status = models.CharField(max_length=20, choices=PLAN_STATUS, default='ACTIVE')
    
    # Configuración del plan
    target_icfes_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(500)]
    )
    target_exam_date = models.DateField()
    weekly_study_hours = models.IntegerField(default=10)
    
    # Distribución por área (porcentajes)
    mathematics_percentage = models.FloatField(default=20.0)
    reading_percentage = models.FloatField(default=20.0)
    natural_sciences_percentage = models.FloatField(default=20.0)
    social_studies_percentage = models.FloatField(default=20.0)
    english_percentage = models.FloatField(default=20.0)
    
    # Progreso
    total_planned_hours = models.IntegerField(default=0)
    completed_hours = models.IntegerField(default=0)
    current_week = models.IntegerField(default=1)
    total_weeks = models.IntegerField(default=12)
    
    # Configuración de dificultad
    adaptive_difficulty = models.BooleanField(default=True)
    min_difficulty = models.CharField(max_length=10, default='EASY')
    max_difficulty = models.CharField(max_length=10, default='HARD')
    
    # IA y personalización
    ai_adjustments_enabled = models.BooleanField(default=True)
    learning_style_adapted = models.BooleanField(default=True)
    performance_based_adjustments = models.BooleanField(default=True)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'study_plans'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'target_exam_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.name} (Meta: {self.target_icfes_score}/500)"
    
    @property
    def completion_percentage(self):
        """Calcula el porcentaje de completitud del plan"""
        if self.total_planned_hours == 0:
            return 0.0
        return (self.completed_hours / self.total_planned_hours) * 100
    
    @property
    def remaining_days(self):
        """Días restantes hasta el examen objetivo"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.target_exam_date <= today:
            return 0
        return (self.target_exam_date - today).days


class UniversityAdmission(models.Model):
    """Información de admisiones universitarias"""
    
    id = models.AutoField(primary_key=True)
    university_name = models.CharField(max_length=200)
    program_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    
    # Requisitos ICFES
    min_global_score = models.IntegerField(default=0)
    min_mathematics_score = models.IntegerField(default=0)
    min_reading_score = models.IntegerField(default=0)
    min_natural_sciences_score = models.IntegerField(default=0)
    min_social_studies_score = models.IntegerField(default=0)
    min_english_score = models.IntegerField(default=0)
    
    # Estadísticas históricas
    average_admitted_score = models.IntegerField(default=0)
    last_admitted_score = models.IntegerField(default=0)  # Último admitido
    competition_ratio = models.FloatField(default=1.0)  # Aspirantes por cupo
    
    # Información adicional
    total_slots = models.IntegerField(default=0)
    tuition_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_semesters = models.IntegerField(default=10)
    
    # URLs de información
    program_url = models.URLField(max_length=500, blank=True, null=True)
    admission_requirements_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    admission_period = models.CharField(max_length=20, default='2024-2')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'university_admissions'
        ordering = ['university_name', 'program_name']
        indexes = [
            models.Index(fields=['min_global_score', 'is_active']),
            models.Index(fields=['university_name', 'program_name']),
        ]
    
    def __str__(self):
        return f"{self.program_name} - {self.university_name} (Min: {self.min_global_score})"


class UserUniversityGoal(models.Model):
    """Objetivos universitarios de usuarios"""
    
    GOAL_STATUS = [
        ('ACTIVE', 'Activo'),
        ('ACHIEVED', 'Alcanzado'),
        ('MODIFIED', 'Modificado'),
        ('ABANDONED', 'Abandonado'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='university_goals')
    university_admission = models.ForeignKey(UniversityAdmission, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=GOAL_STATUS, default='ACTIVE')
    
    # Prioridad del objetivo
    priority = models.IntegerField(default=1)  # 1 = más alta prioridad
    
    # Análisis de viabilidad
    current_probability = models.FloatField(default=0.0)  # Probabilidad actual de admisión
    required_score_improvement = models.IntegerField(default=0)
    estimated_study_months = models.IntegerField(default=0)
    
    # Tracking de progreso
    initial_gap = models.IntegerField(default=0)  # Brecha inicial de puntaje
    current_gap = models.IntegerField(default=0)   # Brecha actual de puntaje
    progress_percentage = models.FloatField(default=0.0)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    target_admission_date = models.DateField()
    achieved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'user_university_goals'
        unique_together = ['user', 'university_admission']
        ordering = ['priority', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.user.username} → {self.university_admission.program_name} ({self.status})" 