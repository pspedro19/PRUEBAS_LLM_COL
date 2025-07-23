"""
Comando Django para cargar y verificar templates de Learning Paths
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.learning.recommendation_engine import LearningRecommendationEngine
from apps.icfes.models import ICFESResult
import yaml
from pathlib import Path

class Command(BaseCommand):
    help = 'Cargar y verificar templates de Learning Paths desde YAML'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Probar generación de learning paths con templates',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username para probar generación de path',
            default='admin_icfes'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 CARGANDO TEMPLATES DE LEARNING PATHS'))
        self.stdout.write('=' * 60)
        
        # Inicializar motor de recomendaciones
        engine = LearningRecommendationEngine()
        
        # Verificar templates cargados
        self.stdout.write('\n📋 TEMPLATES DISPONIBLES:')
        available_templates = engine.get_available_templates()
        
        for template in available_templates:
            self.stdout.write(f"  ✅ {template['display_name']}")
            self.stdout.write(f"     - Dificultad: {template['difficulty']}")
            self.stdout.write(f"     - Duración: {template['estimated_hours']} horas")
            self.stdout.write(f"     - Rango puntaje: {template['target_score_range']}")
            self.stdout.write('')
        
        # Mostrar configuración UI
        self.stdout.write('\n🎨 CONFIGURACIÓN UI:')
        for template_name in ['basic_mathematics_path', 'intermediate_mathematics_path', 'advanced_mathematics_path']:
            ui_config = engine.get_ui_configuration(template_name)
            if ui_config:
                self.stdout.write(f"  {template_name}:")
                self.stdout.write(f"    - Background: {ui_config.get('background', 'N/A')}")
                self.stdout.write(f"    - Button Style: {ui_config.get('button_style', 'N/A')}")
        
        if options['test']:
            self.stdout.write('\n🧪 PROBANDO GENERACIÓN DE LEARNING PATHS')
            self._test_path_generation(engine, options['user'])
        
        self.stdout.write(self.style.SUCCESS('\n✅ Proceso completado'))

    def _test_path_generation(self, engine, username):
        """Probar generación de paths con diferentes puntajes"""
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"\n👤 Probando con usuario: {username}")
            
            # Probar con diferentes puntajes simulados
            test_scores = [30, 55, 85]  # Básico, Intermedio, Avanzado
            
            for score in test_scores:
                self.stdout.write(f"\n📊 Simulando puntaje: {score}")
                
                # Crear análisis simulado
                analysis = {
                    'global_score': score,
                    'selected_template': engine._select_template_by_score(score),
                    'area_analysis': {
                        'Álgebra': {'score': score + 5, 'status': 'regular'},
                        'Geometría': {'score': score - 5, 'status': 'necesita_refuerzo'}
                    },
                    'weak_areas': ['Álgebra'] if score < 60 else [],
                    'recommendations': []
                }
                
                template_name = analysis['selected_template']
                template = engine.get_template_by_name(template_name)
                
                self.stdout.write(f"  📋 Template seleccionado: {template_name}")
                if template and 'metadata' in template:
                    self.stdout.write(f"  📚 Plan: {template['metadata']['name']}")
                    self.stdout.write(f"  ⏱️ Duración: {template['metadata']['estimated_hours']} horas")
                    self.stdout.write(f"  📈 Unidades: {len(template.get('units', []))}")
                
                # Verificar reglas de asignación
                ui_config = engine.get_ui_configuration(template_name)
                if ui_config:
                    self.stdout.write(f"  🎨 Theme: {ui_config.get('background', 'N/A')}")
        
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Usuario '{username}' no encontrado")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error en prueba: {str(e)}")
            ) 