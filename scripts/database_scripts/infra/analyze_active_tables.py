#!/usr/bin/env python3
"""
Script para analizar las tablas activas del proyecto, sus columnas y cardinalidad.
"""

import os
import sys
import django
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
from django.db import connection
from django.db.models import Count

def get_all_models():
    """Obtener todos los modelos de Django"""
    models = []
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('apps.'):
            for model in app_config.get_models():
                models.append(model)
    return models

def get_table_cardinality(model):
    """Obtener la cardinalidad de una tabla"""
    try:
        count = model.objects.count()
        return count
    except Exception as e:
        return f"Error: {str(e)}"

def get_field_type_info(field):
    """Obtener información detallada del tipo de campo"""
    field_type = field.get_internal_type()
    
    # Información adicional según el tipo
    additional_info = []
    
    if field_type == 'CharField':
        if hasattr(field, 'max_length'):
            additional_info.append(f"max_length={field.max_length}")
    elif field_type == 'DecimalField':
        if hasattr(field, 'max_digits') and hasattr(field, 'decimal_places'):
            additional_info.append(f"max_digits={field.max_digits}, decimal_places={field.decimal_places}")
    elif field_type == 'ForeignKey':
        additional_info.append(f"→ {field.related_model._meta.model_name}")
    elif field_type == 'ManyToManyField':
        additional_info.append(f"↔ {field.related_model._meta.model_name}")
    
    if field.null:
        additional_info.append("nullable")
    if hasattr(field, 'unique') and field.unique:
        additional_info.append("unique")
    if hasattr(field, 'blank') and field.blank:
        additional_info.append("blank")
    
    return f"{field_type}({', '.join(additional_info)})" if additional_info else field_type

def analyze_active_tables():
    """Analizar las tablas activas del proyecto"""
    
    print("# 📊 ANÁLISIS DE TABLAS ACTIVAS DEL PROYECTO")
    print()
    print("## 📋 **ESTADÍSTICAS GENERALES:**")
    
    models = get_all_models()
    
    # Agrupar por app
    apps_models = {}
    for model in models:
        app_name = model._meta.app_label
        if app_name not in apps_models:
            apps_models[app_name] = []
        apps_models[app_name].append(model)
    
    total_tables = len(models)
    total_records = 0
    active_tables = 0
    
    print(f"- **Total de tablas:** {total_tables}")
    print(f"- **Total de apps:** {len(apps_models)}")
    print()
    
    # Analizar cada app
    for app_name, app_models in sorted(apps_models.items()):
        print(f"## 📱 **APP: {app_name.upper()}**")
        print()
        
        app_total_records = 0
        app_active_tables = 0
        
        for model in sorted(app_models, key=lambda x: x._meta.model_name):
            model_name = model._meta.model_name
            table_name = model._meta.db_table
            verbose_name = model._meta.verbose_name if hasattr(model._meta, 'verbose_name') else model_name
            
            # Obtener cardinalidad
            cardinality = get_table_cardinality(model)
            
            # Contar campos
            fields = model._meta.get_fields()
            field_count = len(fields)
            
            # Contar tipos de campos
            field_types = {}
            for field in fields:
                field_type = field.get_internal_type()
                if field_type not in field_types:
                    field_types[field_type] = 0
                field_types[field_type] += 1
            
            print(f"### 📋 **TABLA: {table_name}**")
            print()
            print(f"**Modelo:** `{model_name}`")
            print(f"**Nombre descriptivo:** {verbose_name}")
            print(f"**Cardinalidad:** {cardinality} registros")
            print(f"**Total campos:** {field_count}")
            print()
            
            # Mostrar campos
            print("#### 📝 **COLUMNAS:**")
            print()
            
            for field in fields:
                field_name = field.name
                field_type_info = get_field_type_info(field)
                
                print(f"**{field_name}:** {field_type_info}")
            
            print()
            
            # Resumen de tipos de campos
            print("#### 📊 **RESUMEN DE TIPOS DE CAMPOS:**")
            print()
            for field_type, count in sorted(field_types.items()):
                print(f"- **{field_type}:** {count}")
            
            print()
            
            # Actualizar estadísticas
            if isinstance(cardinality, int):
                app_total_records += cardinality
                total_records += cardinality
                if cardinality > 0:
                    app_active_tables += 1
                    active_tables += 1
            
            print("---")
            print()
        
        # Estadísticas de la app
        print(f"**📊 Estadísticas de {app_name.upper()}:**")
        print(f"- Tablas activas: {app_active_tables}/{len(app_models)}")
        print(f"- Total registros: {app_total_records}")
        print()
    
    # Estadísticas generales
    print("## 📊 **ESTADÍSTICAS GENERALES:**")
    print()
    print(f"**Total de tablas:** {total_tables}")
    print(f"**Tablas activas:** {active_tables}")
    print(f"**Tablas vacías:** {total_tables - active_tables}")
    print(f"**Total de registros:** {total_records}")
    print(f"**Promedio de registros por tabla activa:** {total_records // active_tables if active_tables > 0 else 0}")
    print()
    
    # Top 10 tablas con más registros
    print("## 🏆 **TOP 10 TABLAS CON MÁS REGISTROS:**")
    print()
    
    table_counts = []
    for model in models:
        try:
            count = model.objects.count()
            table_counts.append({
                'table': model._meta.db_table,
                'model': model._meta.model_name,
                'app': model._meta.app_label,
                'count': count
            })
        except:
            continue
    
    # Ordenar por cantidad de registros
    table_counts.sort(key=lambda x: x['count'], reverse=True)
    
    for i, table_info in enumerate(table_counts[:10], 1):
        print(f"{i}. **{table_info['table']}** ({table_info['app']})")
        print(f"   - Modelo: `{table_info['model']}`")
        print(f"   - Registros: {table_info['count']}")
        print()
    
    # Análisis de apps más activas
    print("## 📱 **APPS MÁS ACTIVAS:**")
    print()
    
    app_stats = {}
    for app_name, app_models in apps_models.items():
        total_records_app = 0
        active_tables_app = 0
        
        for model in app_models:
            try:
                count = model.objects.count()
                total_records_app += count
                if count > 0:
                    active_tables_app += 1
            except:
                continue
        
        app_stats[app_name] = {
            'total_tables': len(app_models),
            'active_tables': active_tables_app,
            'total_records': total_records_app
        }
    
    # Ordenar apps por total de registros
    sorted_apps = sorted(app_stats.items(), key=lambda x: x[1]['total_records'], reverse=True)
    
    for app_name, stats in sorted_apps:
        print(f"**{app_name.upper()}:**")
        print(f"  - Tablas activas: {stats['active_tables']}/{stats['total_tables']}")
        print(f"  - Total registros: {stats['total_records']}")
        print()

if __name__ == "__main__":
    analyze_active_tables() 