"""
Management command para poblar la base de datos con modelos AI
predefinidos según las configuraciones del orchestrator
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from apps.ai_llm.models import AIModel

class Command(BaseCommand):
    help = 'Pobla la base de datos con modelos AI predefinidos para ICFES Quest'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Iniciando poblado de modelos AI...'))
        
        with transaction.atomic():
            # Limpiar modelos existentes si se especifica
            if options.get('reset', False):
                AIModel.objects.all().delete()
                self.stdout.write(self.style.WARNING('🗑️  Modelos existentes eliminados'))
            
            # Crear modelos según configuración del orchestrator
            self._create_math_models()
            self._create_reading_models()
            self._create_science_models()
            self._create_social_models()
            self._create_english_models()
            self._create_general_models()
            
        total_models = AIModel.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✅ Modelos AI creados exitosamente!'))
        self.stdout.write(f'📊 Total de modelos: {total_models}')
        
        # Mostrar resumen por proveedor
        self._show_summary()
    
    def _create_math_models(self):
        """Modelos específicos para matemáticas"""
        
        # GPT-4 para matemáticas (modelo principal)
        AIModel.objects.get_or_create(
            model_identifier='gpt-4',
            purpose='explanation',
            defaults={
                'name': 'GPT-4 Matemáticas',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.1,
                    'max_tokens': 1500,
                    'top_p': 0.9,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0,
                    'tools': ['code_interpreter', 'mathematical_reasoning']
                },
                'cost_per_1k_tokens': Decimal('0.030'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': False
            }
        )
        
        # GPT-3.5-turbo para matemáticas (modelo de fallback)
        AIModel.objects.get_or_create(
            model_identifier='gpt-3.5-turbo',
            purpose='explanation',
            defaults={
                'name': 'GPT-3.5-turbo Matemáticas',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.2,
                    'max_tokens': 1000,
                    'top_p': 0.9,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0
                },
                'cost_per_1k_tokens': Decimal('0.002'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': True  # Default para matemáticas
            }
        )
        
        # Modelo específico para hints matemáticos
        AIModel.objects.get_or_create(
            model_identifier='gpt-3.5-turbo',
            purpose='hint',
            defaults={
                'name': 'GPT-3.5-turbo Hints Matemáticos',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.3,
                    'max_tokens': 300,
                    'top_p': 0.8
                },
                'cost_per_1k_tokens': Decimal('0.002'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': False
            }
        )
        
        self.stdout.write('📐 Modelos de matemáticas creados')
    
    def _create_reading_models(self):
        """Modelos específicos para lectura crítica"""
        
        # Claude-3-Opus para lectura crítica (modelo principal)
        AIModel.objects.get_or_create(
            model_identifier='claude-3-opus',
            purpose='explanation',
            defaults={
                'name': 'Claude-3-Opus Lectura Crítica',
                'provider': 'anthropic',
                'configuration': {
                    'temperature': 0.3,
                    'max_tokens': 1200,
                    'top_p': 0.9,
                    'features': ['text_analysis', 'reading_comprehension']
                },
                'cost_per_1k_tokens': Decimal('0.015'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': False
            }
        )
        
        # GPT-4 como fallback para lectura crítica
        AIModel.objects.get_or_create(
            model_identifier='gpt-4',
            purpose='explanation',
            defaults={
                'name': 'GPT-4 Lectura Crítica',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.3,
                    'max_tokens': 1200,
                    'top_p': 0.9
                },
                'cost_per_1k_tokens': Decimal('0.030'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': True  # Default para lectura crítica
            }
        )
        
        self.stdout.write('📚 Modelos de lectura crítica creados')
    
    def _create_science_models(self):
        """Modelos específicos para ciencias naturales"""
        
        # GPT-4 para ciencias (modelo principal)
        AIModel.objects.get_or_create(
            model_identifier='gpt-4',
            purpose='explanation',
            defaults={
                'name': 'GPT-4 Ciencias Naturales',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.2,
                    'max_tokens': 1000,
                    'top_p': 0.9,
                    'features': ['scientific_reasoning', 'experimental_analysis']
                },
                'cost_per_1k_tokens': Decimal('0.030'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': False
            }
        )
        
        # GPT-3.5-turbo como fallback para ciencias
        AIModel.objects.get_or_create(
            model_identifier='gpt-3.5-turbo',
            purpose='explanation',
            defaults={
                'name': 'GPT-3.5-turbo Ciencias',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.3,
                    'max_tokens': 800,
                    'top_p': 0.9
                },
                'cost_per_1k_tokens': Decimal('0.002'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': True  # Default para ciencias
            }
        )
        
        self.stdout.write('🔬 Modelos de ciencias naturales creados')
    
    def _create_social_models(self):
        """Modelos específicos para ciencias sociales"""
        
        # Claude-3-Sonnet para ciencias sociales (modelo principal)
        AIModel.objects.get_or_create(
            model_identifier='claude-3-sonnet',
            purpose='explanation',
            defaults={
                'name': 'Claude-3-Sonnet Ciencias Sociales',
                'provider': 'anthropic',
                'configuration': {
                    'temperature': 0.4,
                    'max_tokens': 1000,
                    'top_p': 0.9,
                    'features': ['social_analysis', 'cultural_context']
                },
                'cost_per_1k_tokens': Decimal('0.003'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': False
            }
        )
        
        # GPT-4 como fallback para ciencias sociales
        AIModel.objects.get_or_create(
            model_identifier='gpt-4',
            purpose='explanation',
            defaults={
                'name': 'GPT-4 Ciencias Sociales',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.4,
                    'max_tokens': 1000,
                    'top_p': 0.9,
                    'context_injection': 'constitucion_colombia.json'
                },
                'cost_per_1k_tokens': Decimal('0.030'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': True  # Default para ciencias sociales
            }
        )
        
        self.stdout.write('🏛️ Modelos de ciencias sociales creados')
    
    def _create_english_models(self):
        """Modelos específicos para inglés"""
        
        # GPT-3.5-turbo fine-tuned para inglés (modelo principal)
        AIModel.objects.get_or_create(
            model_identifier='gpt-3.5-turbo-fine-tuned',
            purpose='explanation',
            defaults={
                'name': 'GPT-3.5-turbo Inglés Fine-tuned',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.2,
                    'max_tokens': 800,
                    'top_p': 0.9,
                    'fine_tuned_model': 'ft:gpt-3.5-turbo:icfes-english:7n8m9p0q',
                    'features': ['language_learning', 'grammar_analysis']
                },
                'cost_per_1k_tokens': Decimal('0.008'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': False
            }
        )
        
        # GPT-3.5-turbo estándar como fallback para inglés
        AIModel.objects.get_or_create(
            model_identifier='gpt-3.5-turbo',
            purpose='explanation',
            defaults={
                'name': 'GPT-3.5-turbo Inglés',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.2,
                    'max_tokens': 800,
                    'top_p': 0.9
                },
                'cost_per_1k_tokens': Decimal('0.002'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': True  # Default para inglés
            }
        )
        
        self.stdout.write('🇺🇸 Modelos de inglés creados')
    
    def _create_general_models(self):
        """Modelos generales para múltiples propósitos"""
        
        # Modelo para análisis general
        AIModel.objects.get_or_create(
            model_identifier='gpt-4',
            purpose='analysis',
            defaults={
                'name': 'GPT-4 Análisis General',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.3,
                    'max_tokens': 1500,
                    'top_p': 0.9
                },
                'cost_per_1k_tokens': Decimal('0.030'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': True  # Default para análisis
            }
        )
        
        # Modelo para conversaciones generales
        AIModel.objects.get_or_create(
            model_identifier='gpt-3.5-turbo',
            purpose='conversation',
            defaults={
                'name': 'GPT-3.5-turbo Conversación',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.7,
                    'max_tokens': 800,
                    'top_p': 0.9
                },
                'cost_per_1k_tokens': Decimal('0.002'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': True  # Default para conversación
            }
        )
        
        # Modelo para generación de contenido
        AIModel.objects.get_or_create(
            model_identifier='gpt-3.5-turbo',
            purpose='generation',
            defaults={
                'name': 'GPT-3.5-turbo Generación',
                'provider': 'openai',
                'configuration': {
                    'temperature': 0.8,
                    'max_tokens': 1000,
                    'top_p': 0.9
                },
                'cost_per_1k_tokens': Decimal('0.002'),
                'max_tokens': 4096,
                'is_active': True,
                'is_default': True  # Default para generación
            }
        )
        
        self.stdout.write('⚙️ Modelos generales creados')
    
    def _show_summary(self):
        """Muestra resumen de modelos creados"""
        
        self.stdout.write(self.style.SUCCESS('\n📊 RESUMEN DE MODELOS AI:'))
        
        # Resumen por proveedor
        providers = AIModel.objects.values_list('provider', flat=True).distinct()
        for provider in providers:
            count = AIModel.objects.filter(provider=provider).count()
            self.stdout.write(f'  {provider.upper()}: {count} modelos')
        
        # Resumen por propósito
        self.stdout.write('\n🎯 RESUMEN POR PROPÓSITO:')
        purposes = AIModel.objects.values_list('purpose', flat=True).distinct()
        for purpose in purposes:
            count = AIModel.objects.filter(purpose=purpose).count()
            defaults_count = AIModel.objects.filter(purpose=purpose, is_default=True).count()
            self.stdout.write(f'  {purpose.upper()}: {count} modelos ({defaults_count} defaults)')
        
        # Modelos activos vs inactivos
        active_count = AIModel.objects.filter(is_active=True).count()
        inactive_count = AIModel.objects.filter(is_active=False).count()
        self.stdout.write(f'\n✅ ACTIVOS: {active_count}')
        self.stdout.write(f'❌ INACTIVOS: {inactive_count}')
        
        # Costo promedio por proveedor
        self.stdout.write('\n💰 COSTO PROMEDIO POR 1K TOKENS:')
        for provider in providers:
            models = AIModel.objects.filter(provider=provider)
            if models.exists():
                avg_cost = sum(m.cost_per_1k_tokens for m in models) / len(models)
                self.stdout.write(f'  {provider.upper()}: ${avg_cost:.4f}')
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todos los modelos existentes antes de crear nuevos',
        )