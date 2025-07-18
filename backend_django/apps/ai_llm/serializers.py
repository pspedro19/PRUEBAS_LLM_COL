from rest_framework import serializers
from .models import (
    AIModel, AIConversation, AIMessage, AIPromptTemplate, 
    AIResponseCache, AIInteractionLog, AIModerationLog,
    AILearningInsight, AIUsageQuota, AIPerformanceMetric
)


class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AIConversationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    uuid = serializers.ReadOnlyField()
    
    class Meta:
        model = AIConversation
        fields = '__all__'
        read_only_fields = ['uuid', 'message_count', 'total_tokens', 'total_cost', 'started_at', 'ended_at', 'created_at', 'updated_at']


class AIMessageSerializer(serializers.ModelSerializer):
    conversation_uuid = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = AIMessage
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def create(self, validated_data):
        conversation_uuid = validated_data.pop('conversation_uuid')
        conversation = AIConversation.objects.get(uuid=conversation_uuid)
        validated_data['conversation'] = conversation
        return super().create(validated_data)


class AIPromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPromptTemplate
        fields = '__all__'
        read_only_fields = ['usage_count', 'created_at', 'updated_at']


class AIResponseCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIResponseCache
        fields = '__all__'
        read_only_fields = ['cache_key', 'serve_count', 'last_served', 'created_at']


class AIInteractionLogSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = AIInteractionLog
        fields = '__all__'
        read_only_fields = ['created_at']


class AIModerationLogSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    reviewer = serializers.ReadOnlyField(source='reviewer.username')
    
    class Meta:
        model = AIModerationLog
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AILearningInsightSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = AILearningInsight
        fields = '__all__'
        read_only_fields = ['created_at']


class AIUsageQuotaSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = AIUsageQuota
        fields = '__all__'
        read_only_fields = ['used_today', 'used_this_month', 'last_reset_daily', 'last_reset_monthly', 'created_at', 'updated_at']


class AIPerformanceMetricSerializer(serializers.ModelSerializer):
    model_name = serializers.ReadOnlyField(source='model.name')
    
    class Meta:
        model = AIPerformanceMetric
        fields = '__all__'
        read_only_fields = ['created_at'] 