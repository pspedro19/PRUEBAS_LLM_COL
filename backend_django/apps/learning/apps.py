"""
Configuración de la app de Learning Paths
"""

from django.apps import AppConfig


class LearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.learning'
    verbose_name = 'Learning Paths'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import apps.learning.signals 