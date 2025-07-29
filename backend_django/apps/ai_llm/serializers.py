"""
Serializers para el sistema AI/LLM
Incluye serializers para todas las funcionalidades de IA
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import (
    AIModel, AIConversation, AIMessage, AIPromptTemplate,
    AIResponseCache, AIInteractionLog, AIModerationLog,
    AILearningInsight, AIUsageQuota, AIPerformanceMetric
)

User = get_user_model()


class AIModelSerializer(serializers.ModelSerializer):
    """Serializer para modelos de IA"""
    
    class Meta:
        model = AIModel
        fields = [
            'id', 'name', 'provider', 'model_identifier', 'purpose',
            'configuration', 'cost_per_1k_tokens', 'max_tokens',
            'is_active', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_configuration(self, value):
        """Valida que la configuración tenga los campos requeridos"""
        required_fields = ['temperature', 'max_tokens']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Campo requerido '{field}' faltante en configuración")
        return value


class AIConversationSerializer(serializers.ModelSerializer):
    """Serializer para conversaciones AI"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    message_count = serializers.IntegerField(read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=6, read_only=True)
    
    class Meta:
        model = AIConversation
        fields = [
            'id', 'uuid', 'user', 'user_email', 'conversation_type', 'status',
            'area_evaluacion', 'pregunta', 'learning_path', 'context_data',
            'message_count', 'total_tokens', 'total_cost', 'user_satisfaction',
            'started_at', 'ended_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'uuid', 'message_count', 'total_tokens', 'total_cost',
            'started_at', 'ended_at', 'created_at', 'updated_at'
        ]
    
    def validate_context_data(self, value):
        """Valida que context_data sea un diccionario válido"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("context_data debe ser un objeto JSON válido")
        return value


class AIMessageSerializer(serializers.ModelSerializer):
    """Serializer para mensajes AI"""
    
    model_name = serializers.CharField(source='model_used.name', read_only=True)
    conversation_uuid = serializers.UUIDField(source='conversation.uuid', read_only=True)
    
    class Meta:
        model = AIMessage
        fields = [
            'id', 'conversation', 'conversation_uuid', 'role', 'content',
            'model_used', 'model_name', 'tokens_input', 'tokens_output',
            'response_time_ms', 'confidence_score', 'metadata', 'created_at'
        ]
        read_only_fields = [
            'id', 'conversation_uuid', 'model_name', 'tokens_input',
            'tokens_output', 'response_time_ms', 'confidence_score', 'created_at'
        ]
    
    def validate_role(self, value):
        """Valida que el rol sea válido"""
        valid_roles = ['user', 'assistant', 'system']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Rol debe ser uno de: {valid_roles}")
        return value


class AIPromptTemplateSerializer(serializers.ModelSerializer):
    """Serializer para templates de prompts"""
    
    usage_count = serializers.IntegerField(read_only=True)
    effectiveness_score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = AIPromptTemplate
        fields = [
            'id', 'name', 'code', 'category', 'description',
            'system_prompt', 'user_prompt_template', 'required_variables',
            'model_config', 'role_filter', 'area_filter',
            'effectiveness_score', 'usage_count', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'usage_count', 'effectiveness_score', 'created_at', 'updated_at'
        ]
    
    def validate_required_variables(self, value):
        """Valida que required_variables sea una lista válida"""
        if not isinstance(value, list):
            raise serializers.ValidationError("required_variables debe ser una lista")
        return value
    
    def validate_code(self, value):
        """Valida que el código sea único"""
        if self.instance:
            # Actualización - excluir la instancia actual
            if AIPromptTemplate.objects.filter(code=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ya existe un template con este código")
        else:
            # Creación - verificar que no exista
            if AIPromptTemplate.objects.filter(code=value).exists():
                raise serializers.ValidationError("Ya existe un template con este código")
        return value


class AIUsageQuotaSerializer(serializers.ModelSerializer):
    """Serializer para cuotas de uso de IA"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    daily_remaining = serializers.SerializerMethodField()
    monthly_remaining = serializers.SerializerMethodField()
    can_use = serializers.SerializerMethodField()
    
    class Meta:
        model = AIUsageQuota
        fields = [
            'id', 'user', 'user_email', 'daily_limit', 'monthly_limit',
            'used_today', 'used_this_month', 'daily_remaining', 'monthly_remaining',
            'can_use', 'last_reset_daily', 'last_reset_monthly',
            'is_premium', 'custom_limits', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'used_today', 'used_this_month',
            'daily_remaining', 'monthly_remaining', 'can_use',
            'last_reset_daily', 'last_reset_monthly', 'created_at', 'updated_at'
        ]
    
    def get_daily_remaining(self, obj):
        """Calcula uso diario restante"""
        return max(0, obj.daily_limit - obj.used_today)
    
    def get_monthly_remaining(self, obj):
        """Calcula uso mensual restante"""
        return max(0, obj.monthly_limit - obj.used_this_month)
    
    def get_can_use(self, obj):
        """Verifica si el usuario puede usar IA"""
        return obj.can_use_ai()


class AILearningInsightSerializer(serializers.ModelSerializer):
    """Serializer para insights de aprendizaje"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    model_name = serializers.CharField(source='generated_by_model.name', read_only=True)
    is_valid_now = serializers.SerializerMethodField()
    
    class Meta:
        model = AILearningInsight
        fields = [
            'id', 'user', 'user_email', 'insight_type', 'learning_patterns',
            'strengths', 'weaknesses', 'recommendations', 'confidence_level',
            'generated_by_model', 'model_name', 'is_active', 'is_valid_now',
            'valid_until', 'created_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'model_name', 'is_valid_now', 'created_at'
        ]
    
    def get_is_valid_now(self, obj):
        """Verifica si el insight es válido actualmente"""
        return obj.is_valid()
    
    def validate_confidence_level(self, value):
        """Valida el nivel de confianza"""
        valid_levels = ['low', 'medium', 'high', 'very_high']
        if value not in valid_levels:
            raise serializers.ValidationError(f"Nivel de confianza debe ser uno de: {valid_levels}")
        return value


class AIInteractionLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de interacciones"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    model_name = serializers.CharField(source='model_used.name', read_only=True)
    conversation_uuid = serializers.UUIDField(source='conversation.uuid', read_only=True)
    
    class Meta:
        model = AIInteractionLog
        fields = [
            'id', 'user', 'user_email', 'conversation', 'conversation_uuid',
            'interaction_type', 'input_data', 'output_data', 'model_used',
            'model_name', 'total_tokens', 'cost', 'processing_time_ms',
            'error_message', 'session_id', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'conversation_uuid', 'model_name', 'created_at'
        ]


class AIModerationLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de moderación"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    reviewer_email = serializers.EmailField(source='reviewer.email', read_only=True)
    conversation_uuid = serializers.UUIDField(source='conversation.uuid', read_only=True)
    
    class Meta:
        model = AIModerationLog
        fields = [
            'id', 'user', 'user_email', 'conversation', 'conversation_uuid',
            'flagged_content', 'flag_reason', 'severity', 'ai_action_taken',
            'human_reviewed', 'reviewer', 'reviewer_email', 'final_decision',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'reviewer_email', 'conversation_uuid',
            'created_at', 'updated_at'
        ]


class AIPerformanceMetricSerializer(serializers.ModelSerializer):
    """Serializer para métricas de performance"""
    
    model_name = serializers.CharField(source='model.name', read_only=True)
    
    class Meta:
        model = AIPerformanceMetric
        fields = [
            'id', 'date', 'model', 'model_name', 'total_requests',
            'avg_response_time_ms', 'error_rate', 'user_satisfaction_avg',
            'total_cost', 'cache_hit_rate', 'p95_response_time', 'created_at'
        ]
        read_only_fields = ['id', 'model_name', 'created_at']
    
    def validate_error_rate(self, value):
        """Valida que error_rate esté entre 0 y 1"""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Error rate debe estar entre 0 y 1")
        return value
    
    def validate_cache_hit_rate(self, value):
        """Valida que cache_hit_rate esté entre 0 y 1"""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Cache hit rate debe estar entre 0 y 1")
        return value


# Serializers específicos para funcionalidades

class ExplanationRequestSerializer(serializers.Serializer):
    """Serializer para solicitudes de explicación"""
    
    question_id = serializers.IntegerField()
    question_text = serializers.CharField()
    selected_option = serializers.CharField(max_length=10)
    correct_option = serializers.CharField(max_length=10)
    area = serializers.CharField(max_length=50)
    explanation_type = serializers.ChoiceField(
        choices=['explanation', 'hint', 'analysis', 'feedback'],
        default='explanation'
    )
    user_context = serializers.DictField(required=False, default=dict)
    
    def validate_area(self, value):
        """Valida que el área sea válida"""
        valid_areas = [
            'matematicas', 'lectura_critica', 'ciencias_naturales', 
            'sociales_ciudadanas', 'ingles'
        ]
        if value not in valid_areas:
            raise serializers.ValidationError(f"Área debe ser una de: {valid_areas}")
        return value
    
    def validate_user_context(self, value):
        """Valida que user_context tenga la estructura esperada"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("user_context debe ser un diccionario")
        return value


class ExplanationResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de explicación"""
    
    success = serializers.BooleanField()
    content = serializers.CharField()
    explanation_type = serializers.CharField()
    model_used = serializers.CharField()
    personalized = serializers.BooleanField()
    confidence_score = serializers.FloatField(required=False)
    processing_time_ms = serializers.IntegerField()
    cached = serializers.BooleanField(default=False)
    tokens_used = serializers.IntegerField(required=False)
    recommendations = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    related_concepts = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class ConversationCreateSerializer(serializers.Serializer):
    """Serializer para crear conversaciones"""
    
    conversation_type = serializers.ChoiceField(
        choices=['explanation', 'hint', 'tutoring', 'analysis', 'general']
    )
    area = serializers.CharField(max_length=50, required=False)
    question_id = serializers.IntegerField(required=False)
    learning_path_id = serializers.IntegerField(required=False)
    initial_message = serializers.CharField(max_length=2000)
    context_data = serializers.DictField(default=dict)
    
    def validate(self, data):
        """Valida que la conversación tenga contexto apropiado"""
        conversation_type = data.get('conversation_type')
        
        if conversation_type in ['explanation', 'hint'] and not data.get('question_id'):
            raise serializers.ValidationError(
                "question_id es requerido para conversaciones de explicación o hint"
            )
        
        if conversation_type == 'tutoring' and not data.get('learning_path_id'):
            raise serializers.ValidationError(
                "learning_path_id es requerido para conversaciones de tutoría"
            )
        
        return data


class MessageCreateSerializer(serializers.Serializer):
    """Serializer para crear mensajes en conversaciones"""
    
    conversation_id = serializers.UUIDField()
    content = serializers.CharField(max_length=5000)
    context_data = serializers.DictField(default=dict)
    
    def validate_conversation_id(self, value):
        """Valida que la conversación exista y esté activa"""
        try:
            conversation = AIConversation.objects.get(uuid=value)
            if conversation.status != 'active':
                raise serializers.ValidationError("La conversación no está activa")
        except AIConversation.DoesNotExist:
            raise serializers.ValidationError("Conversación no encontrada")
        return value


class UserAnalysisRequestSerializer(serializers.Serializer):
    """Serializer para solicitudes de análisis de usuario"""
    
    analysis_type = serializers.ChoiceField(
        choices=['complete', 'performance', 'learning_patterns', 'recommendations'],
        default='complete'
    )
    include_predictions = serializers.BooleanField(default=True)
    include_insights = serializers.BooleanField(default=True)
    time_range_days = serializers.IntegerField(default=30, min_value=7, max_value=365)


class UserAnalysisResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de análisis de usuario"""
    
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField()
    
    def to_representation(self, instance):
        """Personaliza la representación de los datos de análisis"""
        data = super().to_representation(instance)
        
        # Estructurar datos de análisis si están presentes
        if 'data' in data and isinstance(data['data'], dict):
            analysis_data = data['data']
            
            # Formatear estadísticas del usuario
            if 'user_stats' in analysis_data:
                user_stats = analysis_data['user_stats']
                user_stats['accuracy'] = round(user_stats.get('accuracy', 0), 1)
                user_stats['improvement_rate'] = round(user_stats.get('improvement_rate', 0), 2)
            
            # Formatear recomendaciones
            if 'recommendations' in analysis_data:
                for rec in analysis_data['recommendations']:
                    if 'estimated_improvement' in rec:
                        rec['estimated_improvement'] = round(rec['estimated_improvement'], 1)
            
            # Formatear predicciones
            if 'predictions' in analysis_data:
                predictions = analysis_data['predictions']
                if 'confidence_level' in predictions:
                    predictions['confidence_level'] = round(predictions['confidence_level'], 2)
        
        return data


class QuotaStatusSerializer(serializers.Serializer):
    """Serializer para estado de cuotas de usuario"""
    
    daily_used = serializers.IntegerField()
    daily_limit = serializers.IntegerField()
    daily_remaining = serializers.IntegerField()
    monthly_used = serializers.IntegerField()
    monthly_limit = serializers.IntegerField()
    monthly_remaining = serializers.IntegerField()
    can_use_ai = serializers.BooleanField()
    is_premium = serializers.BooleanField()
    reset_times = serializers.DictField()


class BatchExplanationRequestSerializer(serializers.Serializer):
    """Serializer para solicitudes batch de explicaciones"""
    
    questions = serializers.ListField(
        child=ExplanationRequestSerializer(),
        min_length=1,
        max_length=10  # Límite de procesamiento batch
    )
    parallel_processing = serializers.BooleanField(default=True)
    
    def validate_questions(self, value):
        """Valida que no haya preguntas duplicadas en el batch"""
        question_ids = [q['question_id'] for q in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError("No se permiten preguntas duplicadas en el batch")
        return value 