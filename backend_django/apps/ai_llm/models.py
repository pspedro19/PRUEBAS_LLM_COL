import uuid
import hashlib
import json
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class AIModel(models.Model):
    """
    Gestión de modelos de IA
    """
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google'),
        ('meta', 'Meta'),
        ('custom', 'Custom'),
    ]
    
    PURPOSE_CHOICES = [
        ('explanation', 'Explanation'),
        ('hint', 'Hint'),
        ('conversation', 'Conversation'),
        ('analysis', 'Analysis'),
        ('generation', 'Generation'),
    ]
    
    name = models.CharField(max_length=200, help_text="Nombre descriptivo del modelo")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, help_text="Proveedor del modelo")
    model_identifier = models.CharField(max_length=100, help_text="Identificador único del modelo (ej: gpt-4, claude-3)")
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, help_text="Propósito principal del modelo")
    configuration = models.JSONField(default=dict, help_text="Configuración específica del modelo")
    cost_per_1k_tokens = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        help_text="Costo por 1000 tokens (input + output)"
    )
    max_tokens = models.IntegerField(
        default=4096, 
        help_text="Máximo número de tokens permitidos"
    )
    is_active = models.BooleanField(default=True, help_text="Si el modelo está disponible para uso")
    is_default = models.BooleanField(default=False, help_text="Si es el modelo por defecto para su propósito")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_models'
        unique_together = ['provider', 'model_identifier', 'purpose']
        indexes = [
            models.Index(fields=['provider', 'purpose']),
            models.Index(fields=['is_active', 'is_default']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.provider}/{self.model_identifier})"
    
    def calculate_cost(self, input_tokens, output_tokens):
        """Calcula el costo total para un número de tokens"""
        total_tokens = input_tokens + output_tokens
        return (total_tokens / 1000) * self.cost_per_1k_tokens
    
    def save(self, *args, **kwargs):
        # Si este modelo se marca como default, desmarcar otros del mismo propósito
        if self.is_default:
            AIModel.objects.filter(
                purpose=self.purpose, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class AIConversation(models.Model):
    """
    Conversaciones con contexto
    """
    CONVERSATION_TYPE_CHOICES = [
        ('explanation', 'Explanation'),
        ('hint', 'Hint'),
        ('tutoring', 'Tutoring'),
        ('analysis', 'Analysis'),
        ('general', 'General'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    conversation_type = models.CharField(max_length=20, choices=CONVERSATION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Relaciones opcionales
    area_evaluacion = models.ForeignKey(
        'icfes.AreaEvaluacion', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ai_conversations'
    )
    pregunta = models.ForeignKey(
        'icfes.PreguntaICFES', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ai_conversations'
    )
    learning_path = models.ForeignKey(
        'learning.LearningPath', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ai_conversations'
    )
    
    context_data = models.JSONField(default=dict, help_text="Datos de contexto de la conversación")
    message_count = models.IntegerField(default=0, help_text="Número total de mensajes")
    total_tokens = models.IntegerField(default=0, help_text="Total de tokens utilizados")
    total_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        default=Decimal('0.00'),
        help_text="Costo total de la conversación"
    )
    user_satisfaction = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Satisfacción del usuario (1-5)"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_conversations'
        indexes = [
            models.Index(fields=['user_id', 'status']),
            models.Index(fields=['conversation_type', 'status']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"Conversation {self.uuid} - {self.user.username} ({self.conversation_type})"
    
    def end_conversation(self):
        """Marca la conversación como terminada"""
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save()


class AIMessage(models.Model):
    """
    Mensajes individuales
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(
        AIConversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField(help_text="Contenido del mensaje")
    model_used = models.ForeignKey(
        AIModel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='messages'
    )
    tokens_input = models.IntegerField(default=0, help_text="Tokens de entrada")
    tokens_output = models.IntegerField(default=0, help_text="Tokens de salida")
    response_time_ms = models.IntegerField(default=0, help_text="Tiempo de respuesta en milisegundos")
    confidence_score = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Puntuación de confianza (0-1)"
    )
    metadata = models.JSONField(default=dict, help_text="Metadatos adicionales")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['role', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.role} message in {self.conversation.uuid}"


class AIPromptTemplate(models.Model):
    """
    Templates reutilizables
    """
    CATEGORY_CHOICES = [
        ('explanation', 'Explanation'),
        ('hint', 'Hint'),
        ('analysis', 'Analysis'),
        ('feedback', 'Feedback'),
        ('motivation', 'Motivation'),
        ('general', 'General'),
    ]
    
    ROLE_FILTER_CHOICES = [
        ('TANK', 'Tank'),
        ('DPS', 'DPS'),
        ('SUPPORT', 'Support'),
        ('ALL', 'All'),
    ]
    
    name = models.CharField(max_length=200, help_text="Nombre del template")
    code = models.CharField(max_length=50, unique=True, help_text="Código único del template")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, help_text="Descripción del template")
    system_prompt = models.TextField(help_text="Prompt del sistema")
    user_prompt_template = models.TextField(help_text="Template del prompt del usuario con {{variables}}")
    required_variables = models.JSONField(default=list, help_text="Lista de variables requeridas")
    model_config = models.JSONField(default=dict, help_text="Configuración específica del modelo")
    role_filter = models.CharField(
        max_length=10, 
        choices=ROLE_FILTER_CHOICES, 
        null=True, 
        blank=True,
        help_text="Filtro por rol de usuario"
    )
    area_filter = models.ForeignKey(
        'icfes.AreaTematica', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='prompt_templates'
    )
    effectiveness_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Puntuación de efectividad (0-1)"
    )
    usage_count = models.IntegerField(default=0, help_text="Número de veces usado")
    is_active = models.BooleanField(default=True, help_text="Si el template está activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_prompt_templates'
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['role_filter', 'is_active']),
            models.Index(fields=['effectiveness_score']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def clean(self):
        """Valida que las variables requeridas estén en el template"""
        super().clean()
        if self.user_prompt_template:
            import re
            template_vars = re.findall(r'\{\{(\w+)\}\}', self.user_prompt_template)
            missing_vars = set(self.required_variables) - set(template_vars)
            if missing_vars:
                raise ValidationError(f"Variables requeridas faltantes en el template: {missing_vars}")
    
    def render_prompt(self, **variables):
        """Renderiza el prompt con las variables proporcionadas"""
        prompt = self.user_prompt_template
        for var_name, var_value in variables.items():
            prompt = prompt.replace(f'{{{{{var_name}}}}}', str(var_value))
        return prompt


class AIResponseCache(models.Model):
    """
    Caché inteligente
    """
    cache_key = models.CharField(max_length=64, unique=True, help_text="Clave única del caché (SHA256)")
    prompt_template = models.ForeignKey(
        AIPromptTemplate, 
        on_delete=models.CASCADE, 
        related_name='cached_responses'
    )
    pregunta = models.ForeignKey(
        'icfes.PreguntaICFES', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='cached_responses'
    )
    response_content = models.TextField(help_text="Contenido de la respuesta cacheada")
    model_used = models.ForeignKey(
        AIModel, 
        on_delete=models.CASCADE, 
        related_name='cached_responses'
    )
    tokens_used = models.IntegerField(help_text="Tokens utilizados")
    user_satisfaction_avg = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="Satisfacción promedio de usuarios"
    )
    serve_count = models.IntegerField(default=0, help_text="Número de veces servido")
    last_served = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text="Fecha de expiración del caché")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_response_cache'
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['prompt_template', 'pregunta']),
        ]
    
    def __str__(self):
        return f"Cache {self.cache_key[:16]}... ({self.serve_count} serves)"
    
    def is_valid(self):
        """Verifica si el caché está vigente"""
        return timezone.now() < self.expires_at
    
    @classmethod
    def generate_cache_key(cls, prompt_template_id, variables, pregunta_id=None):
        """Genera una clave única para el caché"""
        data = {
            'template_id': prompt_template_id,
            'variables': sorted(variables.items()),
            'pregunta_id': pregunta_id
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


class AIInteractionLog(models.Model):
    """
    Logs detallados
    """
    INTERACTION_TYPE_CHOICES = [
        ('explanation_request', 'Explanation Request'),
        ('hint_request', 'Hint Request'),
        ('analysis_request', 'Analysis Request'),
        ('conversation_start', 'Conversation Start'),
        ('conversation_end', 'Conversation End'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_interactions')
    conversation = models.ForeignKey(
        AIConversation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='interaction_logs'
    )
    interaction_type = models.CharField(max_length=30, choices=INTERACTION_TYPE_CHOICES)
    input_data = models.JSONField(default=dict, help_text="Datos de entrada")
    output_data = models.JSONField(default=dict, help_text="Datos de salida")
    model_used = models.ForeignKey(
        AIModel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='interaction_logs'
    )
    total_tokens = models.IntegerField(default=0, help_text="Total de tokens utilizados")
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        default=Decimal('0.00'),
        help_text="Costo de la interacción"
    )
    processing_time_ms = models.IntegerField(default=0, help_text="Tiempo de procesamiento en ms")
    error_message = models.TextField(blank=True, help_text="Mensaje de error si aplica")
    session_id = models.CharField(max_length=100, blank=True, help_text="ID de sesión")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Dirección IP")
    user_agent = models.TextField(blank=True, help_text="User agent del cliente")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_interaction_logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['interaction_type', 'created_at']),
            models.Index(fields=['model_used', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.interaction_type} - {self.user.username} ({self.created_at})"


class AIModerationLog(models.Model):
    """
    Seguridad y moderación
    """
    FLAG_REASON_CHOICES = [
        ('inappropriate_content', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    AI_ACTION_CHOICES = [
        ('blocked', 'Blocked'),
        ('flagged', 'Flagged'),
        ('warned', 'Warned'),
        ('allowed', 'Allowed'),
    ]
    
    FINAL_DECISION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('modified', 'Modified'),
        ('pending', 'Pending'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_logs')
    conversation = models.ForeignKey(
        AIConversation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='moderation_logs'
    )
    flagged_content = models.TextField(help_text="Contenido marcado como problemático")
    flag_reason = models.CharField(max_length=30, choices=FLAG_REASON_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    ai_action_taken = models.CharField(max_length=20, choices=AI_ACTION_CHOICES)
    human_reviewed = models.BooleanField(default=False, help_text="Si fue revisado por un humano")
    reviewer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_moderation_logs'
    )
    final_decision = models.CharField(
        max_length=20, 
        choices=FINAL_DECISION_CHOICES, 
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_moderation_logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['flag_reason', 'severity']),
            models.Index(fields=['human_reviewed', 'final_decision']),
        ]
    
    def __str__(self):
        return f"Moderation {self.id} - {self.user.username} ({self.severity})"


class AILearningInsight(models.Model):
    """
    Insights pedagógicos
    """
    INSIGHT_TYPE_CHOICES = [
        ('strength_analysis', 'Strength Analysis'),
        ('weakness_identification', 'Weakness Identification'),
        ('learning_pattern', 'Learning Pattern'),
        ('recommendation', 'Recommendation'),
        ('progress_tracking', 'Progress Tracking'),
    ]
    
    CONFIDENCE_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_insights')
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPE_CHOICES)
    learning_patterns = models.JSONField(default=dict, help_text="Patrones de aprendizaje identificados")
    strengths = models.JSONField(default=dict, help_text="Fortalezas del usuario")
    weaknesses = models.JSONField(default=dict, help_text="Debilidades del usuario")
    recommendations = models.JSONField(default=dict, help_text="Recomendaciones personalizadas")
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_LEVEL_CHOICES, default='medium')
    generated_by_model = models.ForeignKey(
        AIModel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='generated_insights'
    )
    is_active = models.BooleanField(default=True, help_text="Si el insight está activo")
    valid_until = models.DateTimeField(null=True, blank=True, help_text="Fecha de validez del insight")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_learning_insights'
        indexes = [
            models.Index(fields=['user', 'insight_type']),
            models.Index(fields=['confidence_level', 'is_active']),
            models.Index(fields=['valid_until']),
        ]
    
    def __str__(self):
        return f"{self.insight_type} - {self.user.username} ({self.confidence_level})"
    
    def is_valid(self):
        """Verifica si el insight es válido"""
        if not self.is_active:
            return False
        if self.valid_until and timezone.now() > self.valid_until:
            return False
        return True


class AIUsageQuota(models.Model):
    """
    Control de uso por usuario
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_usage_quota')
    daily_limit = models.IntegerField(default=50, help_text="Límite diario de interacciones")
    monthly_limit = models.IntegerField(default=1000, help_text="Límite mensual de interacciones")
    used_today = models.IntegerField(default=0, help_text="Interacciones usadas hoy")
    used_this_month = models.IntegerField(default=0, help_text="Interacciones usadas este mes")
    last_reset_daily = models.DateTimeField(auto_now_add=True, help_text="Último reset diario")
    last_reset_monthly = models.DateTimeField(auto_now_add=True, help_text="Último reset mensual")
    is_premium = models.BooleanField(default=False, help_text="Si el usuario tiene plan premium")
    custom_limits = models.JSONField(default=dict, help_text="Límites personalizados")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_usage_quotas'
    
    def __str__(self):
        return f"Quota for {self.user.username} ({self.used_today}/{self.daily_limit} today)"
    
    def can_use_ai(self):
        """Verifica si el usuario puede usar IA"""
        self._reset_if_needed()
        return self.used_today < self.daily_limit and self.used_this_month < self.monthly_limit
    
    def increment_usage(self):
        """Incrementa el contador de uso"""
        self.used_today += 1
        self.used_this_month += 1
        self.save()
    
    def _reset_if_needed(self):
        """Resetea los contadores si es necesario"""
        now = timezone.now()
        
        # Reset diario
        if now.date() > self.last_reset_daily.date():
            self.used_today = 0
            self.last_reset_daily = now
        
        # Reset mensual
        if now.month != self.last_reset_monthly.month or now.year != self.last_reset_monthly.year:
            self.used_this_month = 0
            self.last_reset_monthly = now
        
        if self.used_today == 0 or self.used_this_month == 0:
            self.save()


class AIPerformanceMetric(models.Model):
    """
    Métricas de rendimiento
    """
    date = models.DateField(help_text="Fecha de la métrica")
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='performance_metrics')
    total_requests = models.IntegerField(default=0, help_text="Total de requests")
    avg_response_time_ms = models.FloatField(default=0.0, help_text="Tiempo promedio de respuesta en ms")
    error_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Tasa de error (0-1)"
    )
    user_satisfaction_avg = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="Satisfacción promedio de usuarios (0-5)"
    )
    total_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        default=Decimal('0.00'),
        help_text="Costo total del día"
    )
    cache_hit_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Tasa de acierto del caché (0-1)"
    )
    p95_response_time = models.FloatField(default=0.0, help_text="Percentil 95 del tiempo de respuesta")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_performance_metrics'
        unique_together = ['date', 'model']
        indexes = [
            models.Index(fields=['date', 'model']),
            models.Index(fields=['model', 'date']),
        ]
    
    def __str__(self):
        return f"{self.model.name} - {self.date} ({self.total_requests} requests)" 