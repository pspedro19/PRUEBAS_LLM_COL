"""
Modelos de preguntas para Ciudadela del Conocimiento ICFES
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Subject(models.Model):
    """Áreas del conocimiento ICFES"""
    
    ICFES_AREAS = [
        ('MATHEMATICS', 'Matemáticas'),
        ('READING', 'Lectura Crítica'),
        ('NATURAL_SCIENCES', 'Ciencias Naturales'),
        ('SOCIAL_STUDIES', 'Ciencias Sociales'),
        ('ENGLISH', 'Inglés'),
    ]
    
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    area = models.CharField(max_length=20, choices=ICFES_AREAS)
    description = models.TextField(blank=True, null=True)
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    color_theme = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subjects'
        ordering = ['area', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_area_display()})"


class Topic(models.Model):
    """Temas específicos dentro de cada área"""
    
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Metadatos para IA
    keywords = models.JSONField(default=list, blank=True)  # Palabras clave para IA
    prerequisite_topics = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topics'
        ordering = ['subject', 'order', 'name']
        indexes = [
            models.Index(fields=['subject', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class ICFESCuadernillo(models.Model):
    """Cuadernillos ICFES oficiales"""
    
    CUADERNILLO_TYPES = [
        ('SABER_11', 'Saber 11'),
        ('SABER_PRO', 'Saber Pro'),
        ('SIMULACRO', 'Simulacro'),
        ('PRACTICA', 'Práctica'),
    ]
    
    PERIODS = [
        ('2024-1', '2024 Período 1'),
        ('2024-2', '2024 Período 2'), 
        ('2023-1', '2023 Período 1'),
        ('2023-2', '2023 Período 2'),
        ('2022-1', '2022 Período 1'),
        ('2022-2', '2022 Período 2'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)  # "Matemáticas 11° Cuadernillo 1"
    cuadernillo_type = models.CharField(max_length=20, choices=CUADERNILLO_TYPES)
    period = models.CharField(max_length=10, choices=PERIODS)
    code = models.CharField(max_length=50, unique=True)  # "M111", "G11.M.D"
    
    # Archivos fuente
    pdf_file_url = models.URLField(max_length=500, blank=True, null=True)
    pdf_file_path = models.CharField(max_length=500, blank=True, null=True)
    total_pages = models.IntegerField(default=0)
    
    # Información del cuadernillo
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade_level = models.IntegerField(default=11)  # 9, 10, 11
    total_questions = models.IntegerField(default=20)
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_processed = models.BooleanField(default=False)  # Si ya se extrajeron las preguntas
    processing_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'icfes_cuadernillos'
        ordering = ['-period', 'subject', 'name']
        indexes = [
            models.Index(fields=['period', 'subject']),
            models.Index(fields=['cuadernillo_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.period})"


class Question(models.Model):
    """Modelo de preguntas ICFES"""
    
    DIFFICULTY_LEVELS = [
        ('EASY', 'Fácil'),
        ('MEDIUM', 'Medio'),
        ('HARD', 'Difícil'),
        ('EXPERT', 'Experto'),
    ]
    
    QUESTION_TYPES = [
        ('MULTIPLE_CHOICE', 'Opción Múltiple'),
        ('TRUE_FALSE', 'Verdadero/Falso'),
        ('OPEN_ENDED', 'Respuesta Abierta'),
        ('MATCHING', 'Emparejamiento'),
        ('GRAPH_ANALYSIS', 'Análisis de Gráficas'),
        ('TABLE_ANALYSIS', 'Análisis de Tablas'),
    ]
    
    SOURCE_TYPES = [
        ('ICFES_OFFICIAL', 'ICFES Oficial'),
        ('CUADERNILLO', 'Cuadernillo ICFES'),
        ('PRACTICE', 'Práctica'),
        ('AI_GENERATED', 'Generada por IA'),
    ]
    
    CONTENT_TYPES = [
        ('TEXT_ONLY', 'Solo Texto'),
        ('WITH_IMAGE', 'Con Imagen'),
        ('WITH_GRAPH', 'Con Gráfica'),
        ('WITH_TABLE', 'Con Tabla'),
        ('WITH_DIAGRAM', 'Con Diagrama'),
        ('MULTIMEDIA', 'Multimedia'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Contenido de la pregunta
    question_text = models.TextField()
    question_image_url = models.URLField(max_length=500, blank=True, null=True)
    question_audio_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Multimedia adicional para ICFES
    has_diagram = models.BooleanField(default=False)
    has_graph = models.BooleanField(default=False)
    has_table = models.BooleanField(default=False)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='TEXT_ONLY')
    
    # Archivos multimedia específicos
    diagram_image_url = models.URLField(max_length=500, blank=True, null=True)
    graph_image_url = models.URLField(max_length=500, blank=True, null=True)
    table_image_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Clasificación
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='MULTIPLE_CHOICE')
    
    # Origen ICFES específico
    cuadernillo = models.ForeignKey(ICFESCuadernillo, on_delete=models.SET_NULL, null=True, blank=True)
    question_number = models.CharField(max_length=10, blank=True, null=True)  # "11", "3", etc.
    page_number = models.IntegerField(blank=True, null=True)
    
    # Metadatos ICFES
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default='PRACTICE')
    source_reference = models.CharField(max_length=200, blank=True, null=True)  # "Cuadernillo 2024-1, Pregunta 15"
    official_answer_key = models.CharField(max_length=1, blank=True, null=True)  # A, B, C, D
    
    # Análisis automático del contenido
    mathematical_notation = models.BooleanField(default=False)
    geometric_figures = models.BooleanField(default=False)
    statistical_data = models.BooleanField(default=False)
    word_problem = models.BooleanField(default=False)
    
    # Metadatos de extracción del PDF
    extraction_confidence = models.FloatField(default=0.0)  # 0.0 a 1.0
    extraction_notes = models.TextField(blank=True, null=True)
    manual_review_required = models.BooleanField(default=False)
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True, null=True)
    
    # Estadísticas
    times_asked = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    average_time_seconds = models.FloatField(default=0.0)
    
    # Configuración para IA
    ai_explanation_prompt = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)  # Tags para búsqueda y clasificación
    detected_topics = models.JSONField(default=list, blank=True)  # Temas detectados automáticamente
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        indexes = [
            models.Index(fields=['subject', 'difficulty']),
            models.Index(fields=['topic', 'is_active']),
            models.Index(fields=['source_type', 'is_verified']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Q{self.id} - {self.subject.name} ({self.difficulty})"
    
    @property
    def success_rate(self):
        """Calcula la tasa de éxito de la pregunta"""
        if self.times_asked == 0:
            return 0.0
        return (self.times_correct / self.times_asked) * 100
    
    def update_stats(self, is_correct, response_time_seconds):
        """Actualiza las estadísticas de la pregunta"""
        self.times_asked += 1
        if is_correct:
            self.times_correct += 1
        
        # Actualizar tiempo promedio
        if self.average_time_seconds == 0:
            self.average_time_seconds = response_time_seconds
        else:
            self.average_time_seconds = (
                (self.average_time_seconds * (self.times_asked - 1) + response_time_seconds) 
                / self.times_asked
            )
        
        self.save()


class QuestionOption(models.Model):
    """Opciones de respuesta para preguntas de opción múltiple"""
    
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_letter = models.CharField(max_length=1)  # A, B, C, D, E
    option_text = models.TextField()
    option_image_url = models.URLField(max_length=500, blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    
    # Explicación para cada opción
    explanation = models.TextField(blank=True, null=True)
    
    # Metadatos adicionales para ICFES
    has_mathematical_notation = models.BooleanField(default=False)
    has_image = models.BooleanField(default=False)
    extraction_confidence = models.FloatField(default=0.0)
    
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'question_options'
        ordering = ['order', 'option_letter']
        unique_together = ['question', 'option_letter']
    
    def __str__(self):
        return f"{self.question.id} - Opción {self.option_letter}"


class QuestionExplanation(models.Model):
    """Explicaciones detalladas para preguntas"""
    
    EXPLANATION_TYPES = [
        ('SOLUTION', 'Solución'),
        ('HINT', 'Pista'),
        ('THEORY', 'Teoría'),
        ('AI_GENERATED', 'Generada por IA'),
        ('ROLE_BASED', 'Personalizada por Rol'),
    ]
    
    ROLE_TARGET = [
        ('ALL', 'Todos'),
        ('TANK', 'Tanque'),
        ('DPS', 'Daño'),
        ('SUPPORT', 'Soporte'),
        ('SPECIALIST', 'Especialista'),
    ]
    
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='explanations')
    explanation_type = models.CharField(max_length=20, choices=EXPLANATION_TYPES)
    target_role = models.CharField(max_length=20, choices=ROLE_TARGET, default='ALL')
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Multimedia
    image_url = models.URLField(max_length=500, blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Metadatos
    difficulty_level = models.CharField(max_length=10, choices=Question.DIFFICULTY_LEVELS, default='MEDIUM')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'question_explanations'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.question.id} - {self.title}"


class UserQuestionResponse(models.Model):
    """Respuestas de usuarios a preguntas"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # Respuesta
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, null=True, blank=True)
    open_answer = models.TextField(blank=True, null=True)  # Para preguntas abiertas
    is_correct = models.BooleanField()
    
    # Metadatos de la respuesta
    response_time_seconds = models.FloatField()
    confidence_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3
    )
    
    # Contexto de la sesión
    session_id = models.CharField(max_length=100, blank=True, null=True)
    quiz_type = models.CharField(max_length=50, blank=True, null=True)  # practice, exam, battle, etc.
    
    # IA y análisis
    ai_explanation_requested = models.BooleanField(default=False)
    ai_explanation_provided = models.TextField(blank=True, null=True)
    difficulty_perceived = models.CharField(max_length=10, choices=Question.DIFFICULTY_LEVELS, blank=True, null=True)
    
    # Gamificación específica por rol
    xp_gained = models.IntegerField(default=0)
    role_bonus_applied = models.BooleanField(default=False)
    strategy_hint_used = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_question_responses'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['question', 'is_correct']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Q{self.question.id} ({'✓' if self.is_correct else '✗'})"


class QuestionSet(models.Model):
    """Conjuntos de preguntas para exámenes o prácticas específicas"""
    
    SET_TYPES = [
        ('PRACTICE', 'Práctica'),
        ('EXAM', 'Examen'),
        ('BATTLE', 'Batalla'),
        ('ASSESSMENT', 'Evaluación'),
        ('CUADERNILLO', 'Cuadernillo'),
        ('ICFES_SIMULATION', 'Simulacro ICFES'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    set_type = models.CharField(max_length=20, choices=SET_TYPES)
    
    # Configuración
    questions = models.ManyToManyField(Question, through='QuestionSetItem')
    time_limit_minutes = models.IntegerField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Filtros para generación automática
    subject_filter = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty_filter = models.CharField(max_length=10, choices=Question.DIFFICULTY_LEVELS, blank=True, null=True)
    topic_filters = models.ManyToManyField(Topic, blank=True)
    
    # Configuración específica ICFES
    cuadernillo_source = models.ForeignKey(ICFESCuadernillo, on_delete=models.SET_NULL, null=True, blank=True)
    role_specific = models.CharField(max_length=20, blank=True, null=True)  # TANK, DPS, etc.
    adaptive_difficulty = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'question_sets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.set_type})"


class QuestionSetItem(models.Model):
    """Relación entre conjuntos de preguntas y preguntas individuales"""
    
    question_set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=1)
    
    # Configuración específica por rol
    tank_difficulty_modifier = models.FloatField(default=1.0)
    dps_difficulty_modifier = models.FloatField(default=1.0)
    support_difficulty_modifier = models.FloatField(default=1.0)
    specialist_difficulty_modifier = models.FloatField(default=1.0)
    
    class Meta:
        db_table = 'question_set_items'
        unique_together = ['question_set', 'question']
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question_set.name} - Q{self.question.id}"


class QuestionMultimedia(models.Model):
    """Archivos multimedia asociados a preguntas"""
    
    MEDIA_TYPES = [
        ('IMAGE', 'Imagen'),
        ('DIAGRAM', 'Diagrama'),
        ('GRAPH', 'Gráfica'),
        ('TABLE', 'Tabla'),
        ('CHART', 'Gráfico'),
        ('SCREENSHOT', 'Captura'),
        ('DRAWING', 'Dibujo'),
    ]
    
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='multimedia')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    file_url = models.URLField(max_length=500)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Metadatos del archivo
    file_size_kb = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    alt_text = models.CharField(max_length=500, blank=True, null=True)
    
    # Orden y estado
    order = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'question_multimedia'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Q{self.question.id} - {self.get_media_type_display()}" 