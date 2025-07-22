import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ai_llm.models import *

def verify_ai_tables():
    """Verificar que las tablas de IA están funcionando"""
    print("🔍 Verificando tablas del sistema de LLM...")
    
    # Verificar modelos de IA
    models_count = AIModel.objects.count()
    print(f"✅ Modelos de IA: {models_count} modelos en la base de datos")
    
    # Verificar templates de prompts
    templates_count = AIPromptTemplate.objects.count()
    print(f"✅ Templates de prompts: {templates_count} templates en la base de datos")
    
    # Verificar cuotas de uso
    quotas_count = AIUsageQuota.objects.count()
    print(f"✅ Cuotas de uso: {quotas_count} cuotas en la base de datos")
    
    # Mostrar algunos ejemplos
    print("\n📋 Ejemplos de datos:")
    
    # Modelos
    models = AIModel.objects.all()[:3]
    for model in models:
        print(f"  - Modelo: {model.name} ({model.provider}/{model.model_identifier})")
    
    # Templates
    templates = AIPromptTemplate.objects.all()[:2]
    for template in templates:
        print(f"  - Template: {template.name} ({template.code})")
    
    # Cuotas
    quotas = AIUsageQuota.objects.all()[:3]
    for quota in quotas:
        print(f"  - Cuota: Usuario {quota.user.username}, Límite diario: {quota.daily_limit}")
    
    print("\n✅ Verificación completada - Todas las tablas están funcionando correctamente!")

if __name__ == "__main__":
    verify_ai_tables() 