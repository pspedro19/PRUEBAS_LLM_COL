#!/usr/bin/env python3
"""
Script para generar un diagrama ASCII completo de todas las tablas y sus relaciones.
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

def get_all_models():
    """Obtener todos los modelos de Django"""
    models = []
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('apps.'):
            for model in app_config.get_models():
                models.append(model)
    return models

def get_foreign_keys(model):
    """Obtener las claves foráneas de un modelo"""
    foreign_keys = []
    for field in model._meta.get_fields():
        if hasattr(field, 'related_model') and field.related_model:
            foreign_keys.append({
                'field': field.name,
                'related_model': field.related_model._meta.model_name,
                'related_app': field.related_model._meta.app_label,
                'on_delete': field.remote_field.on_delete.__name__ if hasattr(field, 'remote_field') else 'CASCADE'
            })
    return foreign_keys

def get_many_to_many(model):
    """Obtener las relaciones many-to-many de un modelo"""
    many_to_many = []
    for field in model._meta.get_fields():
        if field.many_to_many:
            many_to_many.append({
                'field': field.name,
                'related_model': field.related_model._meta.model_name,
                'related_app': field.related_model._meta.app_label
            })
    return many_to_many

def get_on_delete(field):
    """Obtener el on_delete de un campo de relación"""
    try:
        if hasattr(field, 'remote_field') and field.remote_field:
            return field.remote_field.on_delete.__name__
        elif hasattr(field, 'on_delete'):
            return field.on_delete.__name__
        else:
            return 'CASCADE'
    except:
        return 'CASCADE'

def generate_ascii_diagram():
    """Generar el diagrama ASCII completo"""
    
    print("🎯 DIAGRAMA COMPLETO DE TABLAS Y RELACIONES")
    print("=" * 80)
    print()
    
    models = get_all_models()
    
    # Agrupar por app
    apps_models = {}
    for model in models:
        app_name = model._meta.app_label
        if app_name not in apps_models:
            apps_models[app_name] = []
        apps_models[app_name].append(model)
    
    # Generar diagrama por app
    for app_name, app_models in sorted(apps_models.items()):
        print(f"📱 APP: {app_name.upper()}")
        print("=" * 50)
        print()
        
        for model in sorted(app_models, key=lambda x: x._meta.model_name):
            model_name = model._meta.model_name
            table_name = model._meta.db_table
            
            print(f"📋 TABLA: {table_name}")
            print(f"   Modelo: {model_name}")
            print(f"   App: {app_name}")
            print()
            
            # Mostrar campos
            print("   📝 CAMPOS:")
            for field in model._meta.get_fields():
                if field.is_relation:
                    if field.many_to_many:
                        print(f"     🔗 {field.name} -> ManyToMany -> {field.related_model._meta.model_name}")
                    else:
                        on_delete = get_on_delete(field)
                        print(f"     🔗 {field.name} -> ForeignKey -> {field.related_model._meta.model_name} (on_delete={on_delete})")
                else:
                    field_type = field.get_internal_type()
                    null_info = " (NULL)" if field.null else ""
                    print(f"     📄 {field.name}: {field_type}{null_info}")
            
            print()
            
            # Mostrar relaciones inversas
            reverse_relations = []
            for field in model._meta.get_fields():
                if hasattr(field, 'related_name') and field.related_name:
                    reverse_relations.append(f"     ⬅️  {field.related_name} <- {field.model._meta.model_name}")
            
            if reverse_relations:
                print("   ⬅️  RELACIONES INVERSAS:")
                for rel in reverse_relations:
                    print(rel)
                print()
            
            print("-" * 50)
            print()
    
    # Generar resumen de relaciones
    print("🔗 RESUMEN DE RELACIONES ENTRE APPS")
    print("=" * 80)
    print()
    
    app_relations = {}
    for model in models:
        app_name = model._meta.app_label
        if app_name not in app_relations:
            app_relations[app_name] = set()
        
        for field in model._meta.get_fields():
            if hasattr(field, 'related_model') and field.related_model:
                related_app = field.related_model._meta.app_label
                if related_app != app_name:
                    app_relations[app_name].add(related_app)
    
    for app_name, related_apps in sorted(app_relations.items()):
        if related_apps:
            print(f"📱 {app_name.upper()} -> {', '.join(sorted(related_apps))}")
    
    print()
    print("📊 ESTADÍSTICAS:")
    print(f"   Total de modelos: {len(models)}")
    print(f"   Total de apps: {len(apps_models)}")
    
    # Contar relaciones
    total_fk = 0
    total_m2m = 0
    for model in models:
        for field in model._meta.get_fields():
            if field.is_relation:
                if field.many_to_many:
                    total_m2m += 1
                else:
                    total_fk += 1
    
    print(f"   Total ForeignKeys: {total_fk}")
    print(f"   Total ManyToMany: {total_m2m}")
    print(f"   Total relaciones: {total_fk + total_m2m}")

if __name__ == "__main__":
    generate_ascii_diagram() 