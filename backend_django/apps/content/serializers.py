"""
Serializers para la app de contenido educativo
"""

from rest_framework import serializers
from .models import (
    ContentCategory, ContentUnit, ContentLesson,
    UserContentProgress, ContentRating, ContentBookmark
)


class ContentCategorySerializer(serializers.ModelSerializer):
    """Serializer para categorías de contenido"""
    
    class Meta:
        model = ContentCategory
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ContentLessonSerializer(serializers.ModelSerializer):
    """Serializer para lecciones de contenido"""
    
    class Meta:
        model = ContentLesson
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class ContentUnitSerializer(serializers.ModelSerializer):
    """Serializer para unidades de contenido"""
    lessons = ContentLessonSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ContentUnit
        fields = '__all__'
        read_only_fields = [
            'uuid', 'total_attempts', 'total_completions',
            'average_completion_time', 'average_rating',
            'created_at', 'updated_at'
        ]


class UserContentProgressSerializer(serializers.ModelSerializer):
    """Serializer para progreso de contenido del usuario"""
    content_unit_title = serializers.CharField(source='content_unit.title', read_only=True)
    
    class Meta:
        model = UserContentProgress
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ContentRatingSerializer(serializers.ModelSerializer):
    """Serializer para calificaciones de contenido"""
    
    class Meta:
        model = ContentRating
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ContentBookmarkSerializer(serializers.ModelSerializer):
    """Serializer para marcadores de contenido"""
    content_unit_title = serializers.CharField(source='content_unit.title', read_only=True)
    
    class Meta:
        model = ContentBookmark
        fields = '__all__'
        read_only_fields = ['created_at'] 