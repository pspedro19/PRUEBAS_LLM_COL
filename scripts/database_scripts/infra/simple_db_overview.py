import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def get_db_overview():
    """Obtener resumen de todas las tablas"""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = [table[0] for table in cursor.fetchall()]
    
    print("=" * 80)
    print("🗄️  RESUMEN COMPLETO DE LA BASE DE DATOS - PROYECTO ICFES-LLM")
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
    
    # Mostrar tablas por app
    for app_name, app_table_list in app_tables.items():
        print(f"📦 {app_name.upper()}")
        print("=" * 60)
        for table in sorted(app_table_list):
            print(f"  📋 {table}")
        print()
    
    # Estadísticas
    print("=" * 80)
    print("📊 ESTADÍSTICAS")
    print("=" * 80)
    
    total_tables = len(tables)
    print(f"📈 Total de tablas: {total_tables}")
    print()
    
    for app_name, app_table_list in app_tables.items():
        print(f"  • {app_name}: {len(app_table_list)} tablas")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    get_db_overview() 