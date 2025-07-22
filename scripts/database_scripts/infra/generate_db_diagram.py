import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.apps import apps

def get_all_tables():
    """Obtener todas las tablas de la base de datos"""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    return [table[0] for table in cursor.fetchall()]

def get_table_columns(table_name):
    """Obtener columnas de una tabla"""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position
    """, [table_name])
    return cursor.fetchall()

def get_foreign_keys(table_name):
    """Obtener claves foráneas de una tabla"""
    cursor = connection.cursor()
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
    return cursor.fetchall()

def generate_ascii_diagram():
    """Generar diagrama ASCII completo de la base de datos"""
    tables = get_all_tables()
    
    print("=" * 80)
    print("🗄️  DIAGRAMA COMPLETO DE LA BASE DE DATOS - PROYECTO ICFES-LLM")
    print("=" * 80)
    print()
    
    # Agrupar tablas por app
    app_tables = {}
    for table in tables:
        if table.startswith('auth_') or table.startswith('django_'):
            app = 'Django Core'
        elif table.startswith('ai_'):
            app = 'AI LLM System'
        elif table.startswith('icfes_'):
            app = 'ICFES System'
        elif table.startswith('users_'):
            app = 'Users System'
        elif table.startswith('questions_'):
            app = 'Questions System'
        elif table.startswith('gamification_'):
            app = 'Gamification System'
        elif table.startswith('content_'):
            app = 'Content System'
        elif table.startswith('learning_'):
            app = 'Learning System'
        elif table.startswith('analytics_'):
            app = 'Analytics System'
        elif table.startswith('notifications_'):
            app = 'Notifications System'
        elif table.startswith('schools_'):
            app = 'Schools System'
        else:
            app = 'Other'
        
        if app not in app_tables:
            app_tables[app] = []
        app_tables[app].append(table)
    
    # Generar diagrama por app
    for app_name, app_table_list in app_tables.items():
        print(f"📦 {app_name.upper()}")
        print("=" * 60)
        
        for table in sorted(app_table_list):
            print(f"\n📋 Tabla: {table}")
            print("-" * 40)
            
            # Obtener columnas
            columns = get_table_columns(table)
            fks = get_foreign_keys(table)
            
            # Mostrar columnas
            print("  Columnas:")
            for col_name, data_type, is_nullable, default in columns:
                nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"    • {col_name:<20} {data_type:<15} {nullable}{default_str}")
            
            # Mostrar claves foráneas
            if fks:
                print("  Claves Foráneas:")
                for fk_col, fk_table, fk_col_ref in fks:
                    print(f"    • {fk_col} → {fk_table}.{fk_col_ref}")
            
            print()
    
    # Resumen estadístico
    print("=" * 80)
    print("📊 RESUMEN ESTADÍSTICO")
    print("=" * 80)
    
    total_tables = len(tables)
    total_columns = sum(len(get_table_columns(table)) for table in tables)
    total_fks = sum(len(get_foreign_keys(table)) for table in tables)
    
    print(f"📈 Total de tablas: {total_tables}")
    print(f"📈 Total de columnas: {total_columns}")
    print(f"📈 Total de claves foráneas: {total_fks}")
    print()
    
    for app_name, app_table_list in app_tables.items():
        print(f"  • {app_name}: {len(app_table_list)} tablas")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    generate_ascii_diagram() 