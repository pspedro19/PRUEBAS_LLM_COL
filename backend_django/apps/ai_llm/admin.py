from django.contrib import admin
from .models import (
    AIModel, AIConversation, AIMessage, AIPromptTemplate, 
    AIResponseCache, AIInteractionLog, AIModerationLog,
    AILearningInsight, AIUsageQuota, AIPerformanceMetric
)


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'model_identifier', 'purpose', 'is_active', 'is_default', 'cost_per_1k_tokens']
    list_filter = ['provider', 'purpose', 'is_active', 'is_default']
    search_fields = ['name', 'model_identifier']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'user', 'conversation_type', 'status', 'message_count', 'total_tokens', 'total_cost', 'started_at']
    list_filter = ['conversation_type', 'status', 'started_at']
    search_fields = ['uuid', 'user__username']
    readonly_fields = ['uuid', 'created_at', 'updated_at']


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'model_used', 'tokens_input', 'tokens_output', 'response_time_ms', 'created_at']
    list_filter = ['role', 'model_used', 'created_at']
    search_fields = ['content']
    readonly_fields = ['created_at']


@admin.register(AIPromptTemplate)
class AIPromptTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'role_filter', 'effectiveness_score', 'usage_count', 'is_active']
    list_filter = ['category', 'role_filter', 'is_active']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AIResponseCache)
class AIResponseCacheAdmin(admin.ModelAdmin):
    list_display = ['cache_key', 'prompt_template', 'model_used', 'tokens_used', 'serve_count', 'last_served', 'expires_at']
    list_filter = ['model_used', 'last_served', 'expires_at']
    search_fields = ['cache_key']
    readonly_fields = ['cache_key', 'created_at']


@admin.register(AIInteractionLog)
class AIInteractionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'interaction_type', 'model_used', 'total_tokens', 'cost', 'processing_time_ms', 'created_at']
    list_filter = ['interaction_type', 'model_used', 'created_at']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['created_at']


@admin.register(AIModerationLog)
class AIModerationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'flag_reason', 'severity', 'ai_action_taken', 'human_reviewed', 'final_decision', 'created_at']
    list_filter = ['flag_reason', 'severity', 'ai_action_taken', 'human_reviewed', 'final_decision']
    search_fields = ['user__username', 'flagged_content']
    readonly_fields = ['created_at']


@admin.register(AILearningInsight)
class AILearningInsightAdmin(admin.ModelAdmin):
    list_display = ['user', 'insight_type', 'confidence_level', 'generated_by_model', 'is_active', 'valid_until']
    list_filter = ['insight_type', 'confidence_level', 'is_active', 'valid_until']
    search_fields = ['user__username']
    readonly_fields = ['created_at']


@admin.register(AIUsageQuota)
class AIUsageQuotaAdmin(admin.ModelAdmin):
    list_display = ['user', 'daily_limit', 'monthly_limit', 'used_today', 'used_this_month', 'is_premium']
    list_filter = ['is_premium', 'last_reset_daily', 'last_reset_monthly']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AIPerformanceMetric)
class AIPerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['date', 'model', 'total_requests', 'avg_response_time_ms', 'error_rate', 'user_satisfaction_avg', 'total_cost']
    list_filter = ['date', 'model']
    readonly_fields = ['created_at'] 