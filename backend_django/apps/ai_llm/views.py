from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import (
    AIModel, AIConversation, AIMessage, AIPromptTemplate, 
    AIResponseCache, AIInteractionLog, AIModerationLog,
    AILearningInsight, AIUsageQuota, AIPerformanceMetric
)
from .serializers import (
    AIModelSerializer, AIConversationSerializer, AIMessageSerializer,
    AIPromptTemplateSerializer, AIResponseCacheSerializer, AIInteractionLogSerializer,
    AIModerationLogSerializer, AILearningInsightSerializer, AIUsageQuotaSerializer,
    AIPerformanceMetricSerializer
)


# Vistas para AIModel
class AIModelListView(generics.ListCreateAPIView):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [IsAuthenticated]


class AIModelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [IsAuthenticated]


# Vistas para AIConversation
class AIConversationListView(generics.ListCreateAPIView):
    serializer_class = AIConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user)


class AIConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AIConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user)


# Vistas para AIMessage
class AIMessageListView(generics.ListCreateAPIView):
    serializer_class = AIMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        conversation_uuid = self.kwargs.get('uuid')
        conversation = get_object_or_404(
            AIConversation, 
            uuid=conversation_uuid, 
            user=self.request.user
        )
        return AIMessage.objects.filter(conversation=conversation)


# Vistas para AIPromptTemplate
class AIPromptTemplateListView(generics.ListCreateAPIView):
    queryset = AIPromptTemplate.objects.filter(is_active=True)
    serializer_class = AIPromptTemplateSerializer
    permission_classes = [IsAuthenticated]


class AIPromptTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AIPromptTemplate.objects.all()
    serializer_class = AIPromptTemplateSerializer
    permission_classes = [IsAuthenticated]


# Vistas para AIResponseCache
class AIResponseCacheListView(generics.ListAPIView):
    queryset = AIResponseCache.objects.all()
    serializer_class = AIResponseCacheSerializer
    permission_classes = [IsAuthenticated]


class AIResponseCacheDetailView(generics.RetrieveAPIView):
    queryset = AIResponseCache.objects.all()
    serializer_class = AIResponseCacheSerializer
    permission_classes = [IsAuthenticated]


# Vistas para AIInteractionLog
class AIInteractionLogListView(generics.ListAPIView):
    serializer_class = AIInteractionLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIInteractionLog.objects.filter(user=self.request.user)


# Vistas para AIModerationLog
class AIModerationLogListView(generics.ListAPIView):
    serializer_class = AIModerationLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIModerationLog.objects.filter(user=self.request.user)


# Vistas para AILearningInsight
class AILearningInsightListView(generics.ListCreateAPIView):
    serializer_class = AILearningInsightSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AILearningInsight.objects.filter(user=self.request.user, is_active=True)


class AILearningInsightDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AILearningInsightSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AILearningInsight.objects.filter(user=self.request.user)


# Vistas para AIUsageQuota
class AIUsageQuotaListView(generics.ListAPIView):
    serializer_class = AIUsageQuotaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIUsageQuota.objects.filter(user=self.request.user)


class AIUsageQuotaDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AIUsageQuotaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIUsageQuota.objects.filter(user=self.request.user)


# Vistas para AIPerformanceMetric
class AIPerformanceMetricListView(generics.ListAPIView):
    queryset = AIPerformanceMetric.objects.all()
    serializer_class = AIPerformanceMetricSerializer
    permission_classes = [IsAuthenticated]


class AIPerformanceMetricDetailView(generics.RetrieveAPIView):
    queryset = AIPerformanceMetric.objects.all()
    serializer_class = AIPerformanceMetricSerializer
    permission_classes = [IsAuthenticated] 