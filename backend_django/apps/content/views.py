"""
Vistas para la app de contenido educativo
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from django.utils import timezone

from .models import (
    ContentCategory, ContentUnit, ContentLesson,
    UserContentProgress, ContentRating, ContentBookmark
)
from .serializers import (
    ContentCategorySerializer, ContentUnitSerializer, ContentLessonSerializer,
    UserContentProgressSerializer, ContentRatingSerializer, ContentBookmarkSerializer
)


class ContentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para categorías de contenido"""
    serializer_class = ContentCategorySerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        return ContentCategory.objects.filter(is_active=True)


class ContentUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para unidades de contenido"""
    serializer_class = ContentUnitSerializer
    lookup_field = 'uuid'
    
    def get_queryset(self):
        queryset = ContentUnit.objects.filter(is_active=True)
        
        # Filtros opcionales
        category = self.request.query_params.get('category', None)
        difficulty = self.request.query_params.get('difficulty', None)
        unit_type = self.request.query_params.get('type', None)
        
        if category:
            queryset = queryset.filter(category__slug=category)
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        if unit_type:
            queryset = queryset.filter(unit_type=unit_type)
            
        return queryset


class ContentLessonViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para lecciones de contenido"""
    serializer_class = ContentLessonSerializer
    lookup_field = 'uuid'
    
    def get_queryset(self):
        return ContentLesson.objects.filter(is_active=True)


class UserContentProgressViewSet(viewsets.ModelViewSet):
    """ViewSet para progreso de contenido del usuario"""
    serializer_class = UserContentProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserContentProgress.objects.filter(user=self.request.user)


class CategoryDetailView(generics.RetrieveAPIView):
    """Vista detallada de una categoría"""
    queryset = ContentCategory.objects.filter(is_active=True)
    serializer_class = ContentCategorySerializer
    lookup_field = 'slug'


class ContentUnitDetailView(generics.RetrieveAPIView):
    """Vista detallada de una unidad de contenido"""
    queryset = ContentUnit.objects.filter(is_active=True)
    serializer_class = ContentUnitSerializer
    lookup_field = 'uuid'


class ContentLessonDetailView(generics.RetrieveAPIView):
    """Vista detallada de una lección"""
    queryset = ContentLesson.objects.filter(is_active=True)
    serializer_class = ContentLessonSerializer
    lookup_field = 'uuid'


class StartContentUnitView(generics.CreateAPIView):
    """Vista para iniciar una unidad de contenido"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        content_unit = get_object_or_404(ContentUnit, uuid=uuid, is_active=True)
        
        # Verificar si ya existe progreso
        progress, created = UserContentProgress.objects.get_or_create(
            user=request.user,
            content_unit=content_unit,
            defaults={
                'status': 'IN_PROGRESS',
                'first_attempt_at': timezone.now()
            }
        )
        
        if not created and progress.status == 'NOT_STARTED':
            progress.status = 'IN_PROGRESS'
            progress.first_attempt_at = timezone.now()
            progress.save()
        
        serializer = UserContentProgressSerializer(progress)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompleteContentUnitView(generics.UpdateAPIView):
    """Vista para completar una unidad de contenido"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, uuid):
        content_unit = get_object_or_404(ContentUnit, uuid=uuid, is_active=True)
        progress = get_object_or_404(
            UserContentProgress, 
            user=request.user, 
            content_unit=content_unit
        )
        
        progress.update_progress()
        
        serializer = UserContentProgressSerializer(progress)
        return Response(serializer.data)


class CompleteLessonView(generics.UpdateAPIView):
    """Vista para completar una lección"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, uuid):
        lesson = get_object_or_404(ContentLesson, uuid=uuid, is_active=True)
        
        # Obtener o crear progreso de la unidad
        progress, created = UserContentProgress.objects.get_or_create(
            user=request.user,
            content_unit=lesson.content_unit,
            defaults={'status': 'IN_PROGRESS'}
        )
        
        # Actualizar progreso de la lección
        lesson_data = request.data
        lesson_id = str(lesson.id)
        
        if lesson_id not in progress.lesson_progress:
            progress.lesson_progress[lesson_id] = {}
        
        progress.lesson_progress[lesson_id].update({
            'completed': True,
            'completed_at': timezone.now().isoformat(),
            'score': lesson_data.get('score', 100),
            'time_seconds': lesson_data.get('time_seconds', 0)
        })
        
        progress.update_progress()
        
        serializer = UserContentProgressSerializer(progress)
        return Response(serializer.data)


class MyContentProgressView(generics.ListAPIView):
    """Vista del progreso personal del usuario"""
    serializer_class = UserContentProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserContentProgress.objects.filter(user=self.request.user)


class MyBookmarksView(generics.ListAPIView):
    """Vista de marcadores del usuario"""
    serializer_class = ContentBookmarkSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ContentBookmark.objects.filter(user=self.request.user)


class RecommendedContentView(generics.ListAPIView):
    """Vista de contenido recomendado"""
    serializer_class = ContentUnitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Lógica simple de recomendación
        # TODO: Implementar IA para recomendaciones más sofisticadas
        completed_units = UserContentProgress.objects.filter(
            user=user, 
            is_completed=True
        ).values_list('content_unit_id', flat=True)
        
        return ContentUnit.objects.filter(
            is_active=True
        ).exclude(
            id__in=completed_units
        ).order_by('?')[:10]  # 10 recomendaciones aleatorias


class RateContentUnitView(generics.CreateAPIView):
    """Vista para calificar una unidad de contenido"""
    serializer_class = ContentRatingSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        content_unit = get_object_or_404(ContentUnit, uuid=uuid, is_active=True)
        
        rating, created = ContentRating.objects.update_or_create(
            user=request.user,
            content_unit=content_unit,
            defaults=request.data
        )
        
        serializer = ContentRatingSerializer(rating)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookmarkContentUnitView(generics.CreateAPIView):
    """Vista para marcar/desmarcar contenido como favorito"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        content_unit = get_object_or_404(ContentUnit, uuid=uuid, is_active=True)
        
        bookmark, created = ContentBookmark.objects.get_or_create(
            user=request.user,
            content_unit=content_unit,
            defaults={'notes': request.data.get('notes', '')}
        )
        
        if not created:
            # Si ya existe, actualizar notas
            bookmark.notes = request.data.get('notes', bookmark.notes)
            bookmark.save()
        
        serializer = ContentBookmarkSerializer(bookmark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, uuid):
        content_unit = get_object_or_404(ContentUnit, uuid=uuid, is_active=True)
        
        try:
            bookmark = ContentBookmark.objects.get(
                user=request.user,
                content_unit=content_unit
            )
            bookmark.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ContentBookmark.DoesNotExist:
            return Response(
                {'error': 'Bookmark not found'}, 
                status=status.HTTP_404_NOT_FOUND
            ) 