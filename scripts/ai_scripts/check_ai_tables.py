import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def check_ai_tables():
    """Verificar específicamente las tablas AI"""
    
    print("🔍 VERIFICACIÓN DE TABLAS AI")
    print("=" * 60)
    
    cursor = connection.cursor()
    
    # 1. VERIFICAR SI LA APP AI_LLM EXISTE
    print("\n📋 1. VERIFICANDO APP AI_LLM:")
    print("-" * 40)
    
    try:
        from apps.ai_llm.models import AIModel
        print("✅ App ai_llm SÍ existe")
        print("✅ Modelo AIModel SÍ está importable")
    except ImportError as e:
        print(f"❌ App ai_llm NO existe: {e}")
        return
    
    # 2. VERIFICAR TABLAS AI EN LA BASE DE DATOS
    print("\n📋 2. VERIFICANDO TABLAS AI EN BD:")
    print("-" * 40)
    
    ai_tables = [
        'ai_models',
        'ai_conversations',
        'ai_messages',
        'ai_prompt_templates',
        'ai_response_cache',
        'ai_interaction_logs',
        'ai_moderation_logs',
        'ai_learning_insights',
        'ai_usage_quotas',
        'ai_performance_metrics'
    ]
    
    for table_name in ai_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"✅ {table_name}: {count} registros")
        except Exception as e:
            print(f"❌ {table_name}: NO existe - {e}")
    
    # 3. VERIFICAR MIGRACIONES
    print("\n📋 3. VERIFICANDO MIGRACIONES:")
    print("-" * 40)
    
    cursor.execute("""
        SELECT app, name, applied
        FROM django_migrations
        WHERE app = 'ai_llm'
        ORDER BY applied
    """)
    
    migrations = cursor.fetchall()
    
    if migrations:
        print("✅ Migraciones de ai_llm encontradas:")
        for migration in migrations:
            app, name, applied = migration
            status = "✅ APLICADA" if applied else "❌ PENDIENTE"
            print(f"  {status}: {name}")
    else:
        print("❌ No se encontraron migraciones de ai_llm")
    
    # 4. VERIFICAR MODELOS
    print("\n📋 4. VERIFICANDO MODELOS:")
    print("-" * 40)
    
    try:
        from apps.ai_llm.models import (
            AIModel, AIConversation, AIMessage, AIPromptTemplate,
            AIResponseCache, AIInteractionLog, AIModerationLog,
            AILearningInsight, AIUsageQuota, AIPerformanceMetric
        )
        
        models = [
            ('AIModel', AIModel),
            ('AIConversation', AIConversation),
            ('AIMessage', AIMessage),
            ('AIPromptTemplate', AIPromptTemplate),
            ('AIResponseCache', AIResponseCache),
            ('AIInteractionLog', AIInteractionLog),
            ('AIModerationLog', AIModerationLog),
            ('AILearningInsight', AILearningInsight),
            ('AIUsageQuota', AIUsageQuota),
            ('AIPerformanceMetric', AIPerformanceMetric)
        ]
        
        for model_name, model in models:
            try:
                count = model.objects.count()
                print(f"✅ {model_name}: {count} registros")
            except Exception as e:
                print(f"❌ {model_name}: Error - {e}")
                
    except ImportError as e:
        print(f"❌ Error importando modelos: {e}")
    
    # 5. VERIFICAR APPS INSTALADAS
    print("\n📋 5. VERIFICANDO APPS INSTALADAS:")
    print("-" * 40)
    
    from django.apps import apps
    
    installed_apps = [app.name for app in apps.get_app_configs()]
    
    if 'apps.ai_llm' in installed_apps:
        print("✅ apps.ai_llm está en INSTALLED_APPS")
    else:
        print("❌ apps.ai_llm NO está en INSTALLED_APPS")
        print("📝 Apps instaladas:")
        for app in installed_apps:
            if 'ai' in app.lower():
                print(f"  • {app}")
    
    # 6. RESUMEN
    print("\n📋 6. RESUMEN:")
    print("-" * 40)
    
    ai_tables_exist = 0
    for table_name in ai_tables:
        try:
            cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
            ai_tables_exist += 1
        except:
            pass
    
    print(f"📊 Tablas AI existentes: {ai_tables_exist}/10")
    
    if ai_tables_exist == 10:
        print("✅ TODAS las tablas AI están creadas")
    elif ai_tables_exist > 0:
        print(f"⚠️  Solo {ai_tables_exist}/10 tablas AI están creadas")
    else:
        print("❌ NINGUNA tabla AI está creada")
    
    print("\n🎯 CONCLUSIÓN:")
    if ai_tables_exist == 10:
        print("  ✅ Las tablas AI SÍ están creadas")
        print("  ✅ El sistema está completo")
    else:
        print("  ❌ Las tablas AI NO están creadas")
        print("  ❌ Necesitas ejecutar las migraciones")

if __name__ == "__main__":
    check_ai_tables() 