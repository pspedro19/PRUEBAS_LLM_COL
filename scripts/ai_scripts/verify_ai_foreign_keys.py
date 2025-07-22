import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def verify_ai_foreign_keys():
    """Verificar específicamente los campos de las tablas AI"""
    
    print("🔍 VERIFICACIÓN ESPECÍFICA DE CAMPOS AI")
    print("=" * 80)
    
    cursor = connection.cursor()
    
    # 1. VERIFICAR ESTRUCTURA DE TABLAS AI
    print("\n📋 1. ESTRUCTURA DE TABLAS AI")
    print("-" * 50)
    
    ai_tables = [
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
    
    for table in ai_tables:
        print(f"\n📦 TABLA: {table}")
        print("-" * 30)
        
        # Obtener columnas de la tabla
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, [table])
        
        columns = cursor.fetchall()
        
        for col in columns:
            col_name, data_type, is_nullable, default = col
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default}" if default else ""
            
            # Marcar campos que deberían ser FK
            if col_name.endswith('_id') and col_name != 'id':
                print(f"  🔗 {col_name}: {data_type} {nullable}{default_str} (POSIBLE FK)")
            else:
                print(f"  📝 {col_name}: {data_type} {nullable}{default_str}")
    
    # 2. VERIFICAR FOREIGN KEYS REALES
    print("\n🔗 2. FOREIGN KEYS REALES EN TABLAS AI")
    print("-" * 50)
    
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
    
    foreign_keys = cursor.fetchall()
    
    if foreign_keys:
        print("✅ Foreign Keys encontradas:")
        for fk in foreign_keys:
            table_name, column_name, foreign_table, foreign_column = fk
            print(f"  • {table_name}.{column_name} → {foreign_table}.{foreign_column}")
    else:
        print("❌ No se encontraron Foreign Keys en tablas AI")
    
    # 3. VERIFICAR CAMPOS QUE DEBERÍAN SER FK PERO NO LO SON
    print("\n⚠️ 3. CAMPOS QUE DEBERÍAN SER FK PERO NO LO SON")
    print("-" * 50)
    
    # Lista de campos que deberían ser FK según el modelo
    expected_fks = [
        ('ai_conversations', 'area_evaluacion_id', 'areas_evaluacion', 'id'),
        ('ai_conversations', 'pregunta_id', 'preguntas_icfes', 'id'),
        ('ai_conversations', 'learning_path_id', 'learning_paths', 'id'),
        ('ai_conversations', 'user_id', 'users', 'id'),
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
    
    found_fks = [(fk[0], fk[1], fk[2], fk[3]) for fk in foreign_keys]
    missing_fks = []
    
    for expected in expected_fks:
        if expected in found_fks:
            print(f"  ✅ {expected[0]}.{expected[1]} → {expected[2]}.{expected[3]}")
        else:
            print(f"  ❌ FALTA: {expected[0]}.{expected[1]} → {expected[2]}.{expected[3]}")
            missing_fks.append(expected)
    
    # 4. VERIFICAR TIPOS DE DATOS
    print("\n📊 4. VERIFICACIÓN DE TIPOS DE DATOS")
    print("-" * 50)
    
    # Verificar si los campos _id son integer o bigint
    for table in ai_tables:
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = %s
            AND column_name LIKE '%_id'
            AND column_name != 'id'
        """, [table])
        
        id_columns = cursor.fetchall()
        
        if id_columns:
            print(f"\n📦 {table}:")
            for col_name, data_type in id_columns:
                if data_type in ['integer', 'bigint']:
                    print(f"  ✅ {col_name}: {data_type} (Correcto para FK)")
                else:
                    print(f"  ❌ {col_name}: {data_type} (Incorrecto para FK)")
    
    # 5. RESUMEN FINAL
    print("\n" + "=" * 80)
    print("📋 RESUMEN FINAL")
    print("=" * 80)
    
    print(f"✅ Foreign Keys encontradas: {len(foreign_keys)}")
    print(f"❌ Foreign Keys faltantes: {len(missing_fks)}")
    
    if missing_fks:
        print("\n⚠️ PROBLEMAS DETECTADOS:")
        print("  • Hay campos que deberían ser ForeignKey pero no lo son")
        print("  • Esto puede causar problemas de integridad referencial")
        print("  • Se recomienda revisar las migraciones")
    else:
        print("\n✅ NO SE DETECTARON PROBLEMAS:")
        print("  • Todas las Foreign Keys están correctamente definidas")
        print("  • La integridad referencial está correcta")
        print("  • Los tipos de datos son apropiados")
    
    print("\n🎯 CONCLUSIÓN:")
    if missing_fks:
        print("  ❌ HAY PROBLEMAS DE INTEGRIDAD REFERENCIAL")
        print("  ❌ Se deben corregir las Foreign Keys faltantes")
    else:
        print("  ✅ LA INTEGRIDAD REFERENCIAL ESTÁ CORRECTA")
        print("  ✅ No hay problemas detectados")

if __name__ == "__main__":
    verify_ai_foreign_keys() 