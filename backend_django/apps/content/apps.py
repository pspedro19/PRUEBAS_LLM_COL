"""
Configuración de la app de contenido educativo
"""

from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.content'
    verbose_name = 'Contenido Educativo'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import apps.content.signals 