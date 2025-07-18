"""
Paginación optimizada para Learning Paths
"""

from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginación estándar con metadatos optimizados
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class LargeResultsSetPagination(PageNumberPagination):
    """
    Paginación para resultados grandes (reportes, logs)
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
    """
    Paginación para conjuntos pequeños (dashboards)
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 25


class OptimizedCursorPagination(CursorPagination):
    """
    Paginación con cursor para performance en listas grandes
    Ideal para feeds de actividad, notificaciones, etc.
    """
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-created_at'  # Campo requerido para cursor
    cursor_query_param = 'cursor'
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class LearningPathPagination(PageNumberPagination):
    """
    Paginación específica para Learning Paths con metadatos extra
    """
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    def get_paginated_response(self, data):
        # Calcular estadísticas adicionales si es necesario
        response_data = OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])
        
        # Agregar metadatos de filtros aplicados si existen
        if hasattr(self, 'request') and self.request.query_params:
            filters_applied = {}
            for key, value in self.request.query_params.items():
                if key not in ['page', 'page_size', 'cursor']:
                    filters_applied[key] = value
            
            if filters_applied:
                response_data['filters_applied'] = filters_applied
                
        return Response(response_data)


class ProgressPagination(PageNumberPagination):
    """
    Paginación para progreso del usuario con estadísticas
    """
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        from django.db.models import Avg, Count, Sum
        
        # Calcular estadísticas del progreso si es necesario
        stats = {}
        if hasattr(self, '_queryset'):
            stats = {
                'total_xp': self._queryset.aggregate(Sum('xp_gained'))['xp_gained__sum'] or 0,
                'avg_completion': self._queryset.aggregate(Avg('completion_percentage'))['completion_percentage__avg'] or 0,
                'completed_count': self._queryset.filter(completion_percentage=100).count()
            }
        
        response_data = OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('stats', stats),
            ('results', data)
        ])
        
        return Response(response_data)


class TimelinePagination(OptimizedCursorPagination):
    """
    Paginación para timeline/feed con timestamps
    """
    page_size = 20
    ordering = '-created_at'
    
    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        
        # Agregar timestamp de la respuesta para sincronización
        from django.utils import timezone
        response.data['timestamp'] = timezone.now().isoformat()
        
        return response 