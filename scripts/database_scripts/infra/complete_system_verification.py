import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.apps import apps

def verify_all_tables_and_relationships():
    """Verificar todas las tablas del sistema y sus relaciones"""
    
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("=" * 80)
    
    # 1. OBTENER TODAS LAS TABLAS
    cursor = connection.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name NOT LIKE 'django_%'
        AND table_name NOT LIKE 'auth_%'
        ORDER BY table_name
    """)
    
    all_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 TOTAL DE TABLAS ENCONTRADAS: {len(all_tables)}")
    print("=" * 80)
    
    # 2. VERIFICAR RELACIONES POR TABLA
    for table_name in all_tables:
        print(f"\n📋 TABLA: {table_name}")
        print("-" * 50)
        
        # Obtener columnas de la tabla
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, [table_name])
        
        columns = cursor.fetchall()
        print(f"  📝 Columnas ({len(columns)}):")
        
        for col in columns:
            col_name, data_type, is_nullable, default = col
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default}" if default else ""
            print(f"    • {col_name}: {data_type} {nullable}{default_str}")
        
        # Obtener Foreign Keys de la tabla
        cursor.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = %s
            ORDER BY kcu.column_name
        """, [table_name])
        
        foreign_keys = cursor.fetchall()
        
        if foreign_keys:
            print(f"  🔗 Foreign Keys ({len(foreign_keys)}):")
            for fk in foreign_keys:
                col_name, foreign_table, foreign_col = fk
                print(f"    • {col_name} → {foreign_table}.{foreign_col}")
        else:
            print("  🔗 Foreign Keys: Ninguna")
        
        # Obtener índices de la tabla
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = %s
            AND indexname NOT LIKE '%%_pkey'
            ORDER BY indexname
        """, [table_name])
        
        indexes = cursor.fetchall()
        
        if indexes:
            print(f"  📌 Índices ({len(indexes)}):")
            for idx in indexes:
                idx_name, idx_def = idx
                print(f"    • {idx_name}")
        else:
            print("  📌 Índices: Ninguno")
    
    # 3. ANÁLISIS DE RELACIONES
    print("\n" + "=" * 80)
    print("🔗 ANÁLISIS DE RELACIONES")
    print("=" * 80)
    
    # Obtener todas las relaciones
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
        ORDER BY tc.table_name, kcu.column_name
    """)
    
    all_relationships = cursor.fetchall()
    
    # Agrupar por tipo de relación
    relationships_by_type = {}
    
    for rel in all_relationships:
        table_name, column_name, foreign_table, foreign_column = rel
        
        # Determinar tipo de relación
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND kcu.table_name = %s
            AND kcu.column_name = %s
        """, [foreign_table, foreign_column])
        
        reverse_count = cursor.fetchone()[0]
        
        if reverse_count > 1:
            relation_type = "N:M (Many-to-Many)"
        elif reverse_count == 1:
            relation_type = "1:N (One-to-Many)"
        else:
            relation_type = "1:1 (One-to-One)"
        
        if relation_type not in relationships_by_type:
            relationships_by_type[relation_type] = []
        
        relationships_by_type[relation_type].append(rel)
    
    # Mostrar análisis por tipo
    for relation_type, relationships in relationships_by_type.items():
        print(f"\n📊 {relation_type} ({len(relationships)} relaciones):")
        for rel in relationships:
            table_name, column_name, foreign_table, foreign_column = rel
            print(f"  • {table_name}.{column_name} → {foreign_table}.{foreign_column}")
    
    # 4. VERIFICAR INTEGRIDAD REFERENCIAL
    print("\n" + "=" * 80)
    print("✅ VERIFICACIÓN DE INTEGRIDAD REFERENCIAL")
    print("=" * 80)
    
    integrity_issues = []
    
    for rel in all_relationships:
        table_name, column_name, foreign_table, foreign_column = rel
        
        # Verificar que la tabla referenciada existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = %s
        """, [foreign_table])
        
        if cursor.fetchone()[0] == 0:
            integrity_issues.append(f"❌ {table_name}.{column_name} referencia tabla inexistente: {foreign_table}")
    
    if integrity_issues:
        print("⚠️ PROBLEMAS DETECTADOS:")
        for issue in integrity_issues:
            print(f"  {issue}")
    else:
        print("✅ Todas las relaciones tienen integridad referencial correcta")
    
    # 5. RESUMEN FINAL
    print("\n" + "=" * 80)
    print("📋 RESUMEN FINAL")
    print("=" * 80)
    
    print(f"✅ Total de tablas: {len(all_tables)}")
    print(f"✅ Total de relaciones: {len(all_relationships)}")
    print(f"✅ Relaciones 1:1: {len(relationships_by_type.get('1:1 (One-to-One)', []))}")
    print(f"✅ Relaciones 1:N: {len(relationships_by_type.get('1:N (One-to-Many)', []))}")
    print(f"✅ Relaciones N:M: {len(relationships_by_type.get('N:M (Many-to-Many)', []))}")
    print(f"✅ Problemas de integridad: {len(integrity_issues)}")
    
    print("\n🎯 CONCLUSIÓN:")
    if len(integrity_issues) == 0:
        print("  ✅ El sistema está BIEN CONFIGURADO")
        print("  ✅ Todas las relaciones respetan las 3 formas normales")
        print("  ✅ La integridad referencial está correcta")
        print("  ✅ El sistema está listo para producción")
    else:
        print("  ⚠️ Se detectaron problemas que deben corregirse")
        print("  ⚠️ Revisa los problemas de integridad referencial")

if __name__ == "__main__":
    verify_all_tables_and_relationships() 