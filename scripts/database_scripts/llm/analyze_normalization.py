#!/usr/bin/env python3
"""
Script para analizar la normalización de las tablas y identificar redundancias.
Analiza la distribución de normalización y detecta tablas/columnas que podrían ser redundantes.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.apps import apps

def analyze_normalization():
    print("🔍 ANÁLISIS DE NORMALIZACIÓN Y REDUNDANCIAS")
    print("=" * 80)
    
    cursor = connection.cursor()
    
    # 1. OBTENER TODAS LAS TABLAS
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name NOT LIKE 'django_%'
        AND table_name NOT LIKE 'auth_%'
        ORDER BY table_name
    """)
    
    all_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 TOTAL DE TABLAS: {len(all_tables)}")
    print("=" * 80)
    
    # 2. ANALIZAR CADA TABLA
    normalization_issues = []
    redundant_tables = []
    unused_columns = []
    
    for table_name in all_tables:
        print(f"\n📋 TABLA: {table_name}")
        print("-" * 60)
        
        # Obtener columnas
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, [table_name])
        
        columns = cursor.fetchall()
        
        # Contar registros
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            record_count = cursor.fetchone()[0]
            print(f"📊 Registros: {record_count}")
        except Exception as e:
            print(f"📊 Registros: Error - {e}")
            record_count = 0
        
        # Analizar normalización
        primary_keys = []
        foreign_keys = []
        unique_constraints = []
        
        # Primary Keys
        cursor.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_name = %s
        """, [table_name])
        
        primary_keys = [row[0] for row in cursor.fetchall()]
        
        # Foreign Keys
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
        """, [table_name])
        
        foreign_keys = cursor.fetchall()
        
        # Unique Constraints
        cursor.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'UNIQUE'
            AND tc.table_name = %s
        """, [table_name])
        
        unique_constraints = [row[0] for row in cursor.fetchall()]
        
        # Análisis de normalización
        print(f"🆔 Primary Keys: {', '.join(primary_keys) if primary_keys else '❌ No tiene'}")
        print(f"🔗 Foreign Keys: {len(foreign_keys)}")
        print(f"🔒 Unique Constraints: {len(unique_constraints)}")
        
        # Detectar problemas de normalización
        issues = []
        
        # 1NF - Verificar atomicidad
        for col in columns:
            col_name, data_type, is_nullable, default = col
            if data_type in ['jsonb', 'json'] and col_name not in ['metadata', 'variables', 'insight_data', 'context']:
                issues.append(f"⚠️  Columna JSON en {col_name} - Verificar si necesita normalización")
        
        # 2NF - Verificar dependencias parciales
        if len(primary_keys) > 1:  # Composite primary key
            for fk in foreign_keys:
                fk_col, fk_table, fk_ref_col = fk
                if fk_col not in primary_keys:
                    issues.append(f"⚠️  Posible dependencia parcial: {fk_col} depende de parte de la PK")
        
        # 3NF - Verificar dependencias transitivas
        text_columns = [col[0] for col in columns if col[1] in ['text', 'varchar', 'char']]
        if len(text_columns) > 3 and record_count > 100:
            issues.append(f"⚠️  Muchas columnas de texto - Verificar dependencias transitivas")
        
        # Detectar redundancias
        if record_count == 0:
            redundant_tables.append((table_name, "Tabla vacía"))
        
        if record_count < 5 and len(columns) > 10:
            redundant_tables.append((table_name, "Pocos registros pero muchas columnas"))
        
        # Detectar columnas potencialmente inútiles
        for col in columns:
            col_name, data_type, is_nullable, default = col
            if col_name in ['created_at', 'updated_at', 'deleted_at'] and data_type == 'timestamp':
                continue  # Estas son útiles
            if col_name.endswith('_id') and data_type == 'integer':
                continue  # Foreign keys son útiles
            if col_name == 'id' and data_type == 'integer':
                continue  # Primary key es útil
            
            # Verificar si la columna tiene datos
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NOT NULL")
                non_null_count = cursor.fetchone()[0]
                if non_null_count == 0 and record_count > 0:
                    unused_columns.append((table_name, col_name, "Columna siempre NULL"))
            except:
                pass
        
        if issues:
            normalization_issues.append((table_name, issues))
            print("❌ PROBLEMAS DETECTADOS:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("✅ Normalización correcta")
        
        print("-" * 60)
    
    # 3. RESUMEN DE PROBLEMAS
    print(f"\n{'='*80}")
    print("📊 RESUMEN DE ANÁLISIS")
    print(f"{'='*80}")
    
    if normalization_issues:
        print(f"\n❌ TABLAS CON PROBLEMAS DE NORMALIZACIÓN ({len(normalization_issues)}):")
        for table_name, issues in normalization_issues:
            print(f"\n📋 {table_name}:")
            for issue in issues:
                print(f"  {issue}")
    else:
        print("\n✅ TODAS LAS TABLAS ESTÁN BIEN NORMALIZADAS")
    
    if redundant_tables:
        print(f"\n⚠️  TABLAS POTENCIALMENTE REDUNDANTES ({len(redundant_tables)}):")
        for table_name, reason in redundant_tables:
            print(f"  • {table_name}: {reason}")
    else:
        print("\n✅ NO SE DETECTARON TABLAS REDUNDANTES")
    
    if unused_columns:
        print(f"\n📝 COLUMNAS POTENCIALMENTE INÚTILES ({len(unused_columns)}):")
        for table_name, col_name, reason in unused_columns:
            print(f"  • {table_name}.{col_name}: {reason}")
    else:
        print("\n✅ NO SE DETECTARON COLUMNAS INÚTILES")
    
    # 4. ANÁLISIS POR APLICACIÓN
    print(f"\n{'='*80}")
    print("📱 ANÁLISIS POR APLICACIÓN")
    print(f"{'='*80}")
    
    app_tables = {}
    for table_name in all_tables:
        app_name = table_name.split('_')[0] if '_' in table_name else 'other'
        if app_name not in app_tables:
            app_tables[app_name] = []
        app_tables[app_name].append(table_name)
    
    for app_name, tables in sorted(app_tables.items()):
        print(f"\n📱 {app_name.upper()} ({len(tables)} tablas):")
        for table in sorted(tables):
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  • {table}: {count} registros")
            except:
                print(f"  • {table}: Error al contar")
    
    # 5. RECOMENDACIONES
    print(f"\n{'='*80}")
    print("💡 RECOMENDACIONES")
    print(f"{'='*80}")
    
    total_tables = len(all_tables)
    total_issues = len(normalization_issues) + len(redundant_tables) + len(unused_columns)
    
    if total_issues == 0:
        print("🎉 ¡EXCELENTE! Tu base de datos está bien normalizada y optimizada.")
        print("✅ No se detectaron problemas de normalización")
        print("✅ No se encontraron tablas redundantes")
        print("✅ No se identificaron columnas inútiles")
    else:
        print(f"⚠️  Se detectaron {total_issues} problemas potenciales:")
        print(f"  • {len(normalization_issues)} problemas de normalización")
        print(f"  • {len(redundant_tables)} tablas potencialmente redundantes")
        print(f"  • {len(unused_columns)} columnas potencialmente inútiles")
        
        if redundant_tables:
            print("\n🔧 RECOMENDACIONES PARA TABLAS REDUNDANTES:")
            for table_name, reason in redundant_tables:
                print(f"  • Considerar eliminar {table_name}: {reason}")
        
        if unused_columns:
            print("\n🔧 RECOMENDACIONES PARA COLUMNAS:")
            for table_name, col_name, reason in unused_columns:
                print(f"  • Considerar eliminar {table_name}.{col_name}: {reason}")
    
    print(f"\n📊 ESTADÍSTICAS FINALES:")
    print(f"  • Total de tablas: {total_tables}")
    print(f"  • Tablas con problemas: {len(normalization_issues)}")
    print(f"  • Tablas redundantes: {len(redundant_tables)}")
    print(f"  • Columnas inútiles: {len(unused_columns)}")
    print(f"  • Porcentaje de salud: {((total_tables - total_issues) / total_tables * 100):.1f}%")

if __name__ == "__main__":
    analyze_normalization() 