import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def check_foreign_keys():
    """Verificar Foreign Keys en tablas AI"""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name, 
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' 
        AND tc.table_name LIKE 'ai_%'
        ORDER BY tc.table_name, kcu.column_name
    """)
    
    fks = cursor.fetchall()
    
    print("🔗 Foreign Keys en tablas AI:")
    print("=" * 60)
    
    for fk in fks:
        table_name, column_name, foreign_table, foreign_column = fk
        print(f"  ✅ {table_name}.{column_name} → {foreign_table}.{foreign_column}")
    
    print(f"\n📊 Total de Foreign Keys en tablas AI: {len(fks)}")
    
    # Verificar que las relaciones principales estén presentes
    expected_fks = [
        ('ai_conversations', 'user_id', 'users', 'id'),
        ('ai_conversations', 'area_evaluacion_id', 'areas_evaluacion', 'id'),
        ('ai_conversations', 'pregunta_id', 'preguntas_icfes', 'id'),
        ('ai_conversations', 'learning_path_id', 'learning_paths', 'id'),
        ('ai_messages', 'conversation_id', 'ai_conversations', 'id'),
        ('ai_messages', 'model_used_id', 'ai_models', 'id'),
        ('ai_prompt_templates', 'area_filter_id', 'areas_tematicas', 'id'),
        ('ai_response_cache', 'prompt_template_id', 'ai_prompt_templates', 'id'),
        ('ai_response_cache', 'pregunta_id', 'preguntas_icfes', 'id'),
        ('ai_response_cache', 'model_used_id', 'ai_models', 'id'),
        ('ai_interaction_logs', 'user_id', 'users', 'id'),
        ('ai_interaction_logs', 'conversation_id', 'ai_conversations', 'id'),
        ('ai_interaction_logs', 'model_used_id', 'ai_models', 'id'),
        ('ai_moderation_logs', 'user_id', 'users', 'id'),
        ('ai_moderation_logs', 'conversation_id', 'ai_conversations', 'id'),
        ('ai_moderation_logs', 'reviewer_id', 'users', 'id'),
        ('ai_learning_insights', 'user_id', 'users', 'id'),
        ('ai_learning_insights', 'generated_by_model_id', 'ai_models', 'id'),
        ('ai_usage_quotas', 'user_id', 'users', 'id'),
        ('ai_performance_metrics', 'model_id', 'ai_models', 'id'),
    ]
    
    print("\n🔍 Verificando relaciones esperadas:")
    print("=" * 60)
    
    found_fks = [(fk[0], fk[1], fk[2], fk[3]) for fk in fks]
    
    for expected in expected_fks:
        if expected in found_fks:
            print(f"  ✅ {expected[0]}.{expected[1]} → {expected[2]}.{expected[3]}")
        else:
            print(f"  ❌ FALTA: {expected[0]}.{expected[1]} → {expected[2]}.{expected[3]}")
    
    print("\n✅ Verificación completada")

if __name__ == "__main__":
    check_foreign_keys() 