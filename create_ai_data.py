import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ai_llm.models import *
from apps.users.models import User
from decimal import Decimal

def create_sample_data():
    """Crear datos de ejemplo para el sistema de LLM"""
    print("🚀 Creando datos de ejemplo para el sistema de LLM...")
    
    # Crear modelos de IA
    models_data = [
        {
            'name': 'GPT-4 para Explicaciones',
            'provider': 'openai',
            'model_identifier': 'gpt-4',
            'purpose': 'explanation',
            'configuration': {'temperature': 0.7, 'max_tokens': 1000},
            'cost_per_1k_tokens': Decimal('0.03'),
            'max_tokens': 4096,
            'is_active': True,
            'is_default': True
        },
        {
            'name': 'Claude-3 para Pistas',
            'provider': 'anthropic',
            'model_identifier': 'claude-3-sonnet',
            'purpose': 'hint',
            'configuration': {'temperature': 0.5, 'max_tokens': 500},
            'cost_per_1k_tokens': Decimal('0.015'),
            'max_tokens': 4096,
            'is_active': True,
            'is_default': False
        },
        {
            'name': 'GPT-3.5 para Conversación',
            'provider': 'openai',
            'model_identifier': 'gpt-3.5-turbo',
            'purpose': 'conversation',
            'configuration': {'temperature': 0.8, 'max_tokens': 2000},
            'cost_per_1k_tokens': Decimal('0.002'),
            'max_tokens': 4096,
            'is_active': True,
            'is_default': True
        }
    ]
    
    for model_data in models_data:
        model, created = AIModel.objects.get_or_create(
            provider=model_data['provider'],
            model_identifier=model_data['model_identifier'],
            purpose=model_data['purpose'],
            defaults=model_data
        )
        if created:
            print(f"✅ Modelo creado: {model.name}")
        else:
            print(f"ℹ️  Modelo ya existe: {model.name}")
    
    # Crear templates de prompts
    templates_data = [
        {
            'name': 'Explicación de Pregunta ICFES',
            'code': 'icfes_explanation',
            'category': 'explanation',
            'description': 'Template para explicar preguntas del ICFES',
            'system_prompt': 'Eres un tutor experto en matemáticas que explica conceptos de manera clara y didáctica.',
            'user_prompt_template': 'Explica la siguiente pregunta del ICFES de manera clara y paso a paso: {{pregunta_texto}}. La respuesta correcta es {{respuesta_correcta}}.',
            'required_variables': ['pregunta_texto', 'respuesta_correcta'],
            'model_config': {'temperature': 0.7},
            'role_filter': 'ALL',
            'effectiveness_score': 0.85,
            'is_active': True
        },
        {
            'name': 'Pista para Pregunta ICFES',
            'code': 'icfes_hint',
            'category': 'hint',
            'description': 'Template para dar pistas sobre preguntas del ICFES',
            'system_prompt': 'Eres un tutor que da pistas útiles sin revelar la respuesta completa.',
            'user_prompt_template': 'Dame una pista útil para resolver esta pregunta: {{pregunta_texto}}. No reveles la respuesta completa.',
            'required_variables': ['pregunta_texto'],
            'model_config': {'temperature': 0.6},
            'role_filter': 'ALL',
            'effectiveness_score': 0.78,
            'is_active': True
        }
    ]
    
    for template_data in templates_data:
        template, created = AIPromptTemplate.objects.get_or_create(
            code=template_data['code'],
            defaults=template_data
        )
        if created:
            print(f"✅ Template creado: {template.name}")
        else:
            print(f"ℹ️  Template ya existe: {template.name}")
    
    # Crear cuotas de uso para usuarios existentes
    users = User.objects.all()[:5]  # Primeros 5 usuarios
    for user in users:
        quota, created = AIUsageQuota.objects.get_or_create(
            user=user,
            defaults={
                'daily_limit': 50,
                'monthly_limit': 1000,
                'is_premium': False
            }
        )
        if created:
            print(f"✅ Cuota creada para: {user.username}")
        else:
            print(f"ℹ️  Cuota ya existe para: {user.username}")
    
    print("✅ Datos de ejemplo creados exitosamente!")

if __name__ == "__main__":
    create_sample_data() 