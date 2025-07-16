"""
Modelos de Analytics para Ciudadela del Conocimiento ICFES
Sistema de métricas y análisis de rendimiento
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class UserEvent(models.Model):
    """Eventos de usuario para análisis"""
    
    EVENT_TYPES = [
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('QUESTION_ANSWERED', 'Pregunta Respondida'),
        ('QUIZ_STARTED', 'Quiz Iniciado'),
        ('QUIZ_COMPLETED', 'Quiz Completado'),
        ('BATTLE_STARTED', 'Batalla Iniciada'),
        ('BATTLE_COMPLETED', 'Batalla Completada'),
        ('ACHIEVEMENT_UNLOCKED', 'Logro Desbloqueado'),
        ('LEVEL_UP', 'Subida de Nivel'),
        ('ACADEMY_JOINED', 'Unión a Academia'),
        ('POWERUP_USED', 'Power-up Usado'),
        ('STUDY_SESSION', 'Sesión de Estudio'),
        ('PAGE_VIEW', 'Vista de Página'),
        ('FEATURE_USED', 'Función Utilizada'),
    ]
    
    EVENT_CATEGORIES = [
        ('LEARNING', 'Aprendizaje'),
        ('SOCIAL', 'Social'),
        ('GAMIFICATION', 'Gamificación'),
        ('NAVIGATION', 'Navegación'),
        ('ENGAGEMENT', 'Compromiso'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    category = models.CharField(max_length=20, choices=EVENT_CATEGORIES)
    
    # Datos del evento
    event_data = models.JSONField(default=dict)  # Datos específicos del evento
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Contexto técnico
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(max_length=500, blank=True, null=True)
    page_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Metadata
    duration_seconds = models.IntegerField(blank=True, null=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_events'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['category', 'timestamp']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_event_type_display()}"


class LearningAnalytics(models.Model):
    """Análisis de aprendizaje por usuario"""
    
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_analytics')
    
    # Métricas generales
    total_study_time_minutes = models.IntegerField(default=0)
    total_questions_answered = models.IntegerField(default=0)
    total_correct_answers = models.IntegerField(default=0)
    average_accuracy = models.FloatField(default=0.0)
    
    # Métricas por área ICFES
    mathematics_accuracy = models.FloatField(default=0.0)
    reading_accuracy = models.FloatField(default=0.0)
    natural_sciences_accuracy = models.FloatField(default=0.0)
    social_studies_accuracy = models.FloatField(default=0.0)
    english_accuracy = models.FloatField(default=0.0)
    
    # Tiempo promedio por área (segundos)
    mathematics_avg_time = models.FloatField(default=0.0)
    reading_avg_time = models.FloatField(default=0.0)
    natural_sciences_avg_time = models.FloatField(default=0.0)
    social_studies_avg_time = models.FloatField(default=0.0)
    english_avg_time = models.FloatField(default=0.0)
    
    # Patrones de estudio
    most_active_hour = models.IntegerField(default=14)  # Hora del día (0-23)
    most_active_day = models.IntegerField(default=1)    # Día de la semana (1-7)
    average_session_duration = models.FloatField(default=0.0)  # Minutos
    study_streak_days = models.IntegerField(default=0)
    
    # Progreso temporal
    weekly_improvement_rate = models.FloatField(default=0.0)  # Porcentaje
    monthly_improvement_rate = models.FloatField(default=0.0)
    skill_growth_trend = models.JSONField(default=dict)  # Tendencias por área
    
    # Predicciones de IA
    predicted_icfes_score = models.IntegerField(default=0)
    confidence_score = models.FloatField(default=0.0)
    learning_velocity = models.FloatField(default=1.0)  # Velocidad de aprendizaje
    
    # Recomendaciones
    recommended_study_areas = models.JSONField(default=list)
    optimal_study_schedule = models.JSONField(default=dict)
    personalized_difficulty = models.CharField(max_length=10, default='MEDIUM')
    
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'learning_analytics'
    
    def __str__(self):
        return f"Analytics de {self.user.username} - {self.average_accuracy:.1f}% precisión"


class SubjectAnalytics(models.Model):
    """Análisis detallado por materia"""
    
    SUBJECTS = [
        ('MATHEMATICS', 'Matemáticas'),
        ('READING', 'Lectura Crítica'),
        ('NATURAL_SCIENCES', 'Ciencias Naturales'),
        ('SOCIAL_STUDIES', 'Ciencias Sociales'),
        ('ENGLISH', 'Inglés'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_analytics')
    subject = models.CharField(max_length=20, choices=SUBJECTS)
    
    # Estadísticas básicas
    questions_answered = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    accuracy_percentage = models.FloatField(default=0.0)
    
    # Tiempo invertido
    total_time_minutes = models.IntegerField(default=0)
    average_time_per_question = models.FloatField(default=0.0)
    
    # Análisis por dificultad
    easy_accuracy = models.FloatField(default=0.0)
    medium_accuracy = models.FloatField(default=0.0)
    hard_accuracy = models.FloatField(default=0.0)
    
    # Análisis por temas (top 5 temas más frecuentes)
    topic_performance = models.JSONField(default=dict)  # {'algebra': 85.5, 'geometry': 72.3}
    weakest_topics = models.JSONField(default=list)
    strongest_topics = models.JSONField(default=list)
    
    # Progreso temporal
    progress_trend = models.JSONField(default=list)  # Histórico de precisión por semana
    improvement_rate = models.FloatField(default=0.0)
    recent_performance = models.FloatField(default=0.0)  # Últimas 2 semanas
    
    # Recomendaciones específicas
    recommended_difficulty = models.CharField(max_length=10, default='MEDIUM')
    priority_topics = models.JSONField(default=list)
    study_time_recommendation = models.IntegerField(default=60)  # Minutos semanales
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subject_analytics'
        unique_together = ['user', 'subject']
        indexes = [
            models.Index(fields=['user', 'subject']),
            models.Index(fields=['accuracy_percentage']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_subject_display()}: {self.accuracy_percentage:.1f}%"


class SessionAnalytics(models.Model):
    """Análisis de sesiones de estudio"""
    
    SESSION_TYPES = [
        ('PRACTICE', 'Práctica'),
        ('QUIZ', 'Quiz'),
        ('BATTLE', 'Batalla'),
        ('ICFES_SIMULATION', 'Simulacro ICFES'),
        ('FREE_STUDY', 'Estudio Libre'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_analytics')
    session_id = models.CharField(max_length=100, unique=True)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    
    # Métricas de la sesión
    duration_minutes = models.IntegerField(default=0)
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    accuracy_percentage = models.FloatField(default=0.0)
    
    # Distribución de tiempo
    time_per_question = models.JSONField(default=list)  # Lista de tiempos
    areas_covered = models.JSONField(default=list)      # Áreas estudiadas
    difficulty_distribution = models.JSONField(default=dict)  # Por nivel de dificultad
    
    # Engagement metrics
    focus_score = models.FloatField(default=0.0)       # Basado en patrones de interacción
    completion_rate = models.FloatField(default=0.0)   # Porcentaje completado
    interruptions_count = models.IntegerField(default=0)
    
    # Contextual data
    device_type = models.CharField(max_length=20, blank=True, null=True)  # mobile, desktop, tablet
    study_environment = models.CharField(max_length=50, blank=True, null=True)  # home, school, library
    
    # Resultados
    xp_gained = models.IntegerField(default=0)
    coins_earned = models.IntegerField(default=0)
    achievements_unlocked = models.IntegerField(default=0)
    
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'session_analytics'
        indexes = [
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['session_type', 'started_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_session_type_display()} ({self.duration_minutes}min)"


class PerformanceMetrics(models.Model):
    """Métricas de rendimiento globales del sistema"""
    
    METRIC_TYPES = [
        ('USER_ENGAGEMENT', 'Engagement de Usuario'),
        ('LEARNING_EFFECTIVENESS', 'Efectividad de Aprendizaje'),
        ('FEATURE_USAGE', 'Uso de Funcionalidades'),
        ('TECHNICAL_PERFORMANCE', 'Rendimiento Técnico'),
        ('CONTENT_QUALITY', 'Calidad de Contenido'),
    ]
    
    id = models.AutoField(primary_key=True)
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    metric_name = models.CharField(max_length=100)
    
    # Valores de la métrica
    value = models.FloatField()
    target_value = models.FloatField(blank=True, null=True)
    previous_value = models.FloatField(blank=True, null=True)
    
    # Contexto
    dimension_filters = models.JSONField(default=dict)  # Filtros aplicados
    calculation_method = models.TextField()
    data_source = models.CharField(max_length=100)
    
    # Metadata
    confidence_level = models.FloatField(default=100.0)
    sample_size = models.IntegerField(default=0)
    calculation_time = models.FloatField(default=0.0)  # Tiempo de cálculo en segundos
    
    # Timestamps
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'performance_metrics'
        indexes = [
            models.Index(fields=['metric_type', 'calculated_at']),
            models.Index(fields=['metric_name', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.value} ({self.period_start.date()})"


class A_BTest(models.Model):
    """Experimentos A/B Testing"""
    
    TEST_STATUS = [
        ('DRAFT', 'Borrador'),
        ('ACTIVE', 'Activo'),
        ('PAUSED', 'Pausado'),
        ('COMPLETED', 'Completado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    hypothesis = models.TextField()
    
    # Configuración del test
    control_variant = models.CharField(max_length=50, default='A')
    test_variant = models.CharField(max_length=50, default='B')
    traffic_split = models.FloatField(default=50.0)  # Porcentaje para variant B
    
    # Métricas a medir
    primary_metric = models.CharField(max_length=100)
    secondary_metrics = models.JSONField(default=list)
    success_criteria = models.JSONField(default=dict)
    
    # Configuración de audiencia
    target_audience = models.JSONField(default=dict)  # Filtros de usuarios
    sample_size_required = models.IntegerField(default=1000)
    confidence_level = models.FloatField(default=95.0)
    
    # Estado y fechas
    status = models.CharField(max_length=20, choices=TEST_STATUS, default='DRAFT')
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    planned_duration_days = models.IntegerField(default=14)
    
    # Resultados
    control_conversions = models.IntegerField(default=0)
    test_conversions = models.IntegerField(default=0)
    control_participants = models.IntegerField(default=0)
    test_participants = models.IntegerField(default=0)
    statistical_significance = models.FloatField(default=0.0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ab_tests'
        indexes = [
            models.Index(fields=['status', 'start_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.status})"


class UserTestParticipation(models.Model):
    """Participación de usuarios en A/B Tests"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ab_test_participations')
    ab_test = models.ForeignKey(A_BTest, on_delete=models.CASCADE, related_name='participants')
    variant = models.CharField(max_length=50)  # 'A' o 'B'
    
    # Tracking de eventos
    conversion_achieved = models.BooleanField(default=False)
    conversion_value = models.FloatField(default=0.0)
    conversion_timestamp = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    assigned_at = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_test_participations'
        unique_together = ['user', 'ab_test']
        indexes = [
            models.Index(fields=['ab_test', 'variant']),
            models.Index(fields=['conversion_achieved']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.ab_test.name} (Variant {self.variant})"


class ContentAnalytics(models.Model):
    """Análisis de contenido (preguntas, explicaciones)"""
    
    CONTENT_TYPES = [
        ('QUESTION', 'Pregunta'),
        ('EXPLANATION', 'Explicación'),
        ('TOPIC', 'Tema'),
        ('QUIZ', 'Quiz'),
    ]
    
    id = models.AutoField(primary_key=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.IntegerField()  # ID del contenido
    content_reference = models.CharField(max_length=200)  # Referencia legible
    
    # Métricas de uso
    total_views = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    total_interactions = models.IntegerField(default=0)
    
    # Métricas de calidad
    average_rating = models.FloatField(default=0.0)
    difficulty_rating = models.FloatField(default=0.0)
    clarity_rating = models.FloatField(default=0.0)
    
    # Performance metrics
    average_response_time = models.FloatField(default=0.0)
    success_rate = models.FloatField(default=0.0)
    abandonment_rate = models.FloatField(default=0.0)
    
    # Engagement metrics
    time_spent_average = models.FloatField(default=0.0)
    interaction_depth = models.FloatField(default=0.0)
    return_rate = models.FloatField(default=0.0)
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    analysis_period_days = models.IntegerField(default=30)
    
    class Meta:
        db_table = 'content_analytics'
        unique_together = ['content_type', 'content_id']
        indexes = [
            models.Index(fields=['content_type', 'success_rate']),
            models.Index(fields=['average_rating']),
        ]
    
    def __str__(self):
        return f"{self.get_content_type_display()} {self.content_reference} - Rating: {self.average_rating:.1f}" 