#!/usr/bin/env python3
"""
Script de utilidad para ejecutar otros scripts del proyecto.
Facilita la ejecución de scripts sin necesidad de copiarlos manualmente al contenedor.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def get_script_path(script_name):
    """Obtener la ruta del script basado en su nombre"""
    script_dirs = {
        'database': 'database_scripts',
        'test': 'test_scripts', 
        'ai': 'ai_scripts'
    }
    
    # Buscar en todas las carpetas
    for category, dir_name in script_dirs.items():
        script_path = Path(__file__).parent / dir_name / f"{script_name}.py"
        if script_path.exists():
            return script_path
    
    return None

def copy_to_container(script_path):
    """Copiar script al contenedor Docker"""
    try:
        cmd = f'docker cp "{script_path}" mathquest-backend:/app/'
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Script copiado al contenedor: {script_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error copiando script: {e}")
        return False

def run_in_container(script_name):
    """Ejecutar script en el contenedor"""
    try:
        cmd = f'docker-compose exec backend python {script_name}.py'
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando script: {e}")
        return False

def list_available_scripts():
    """Listar todos los scripts disponibles"""
    script_dirs = {
        '📊 Database Scripts': 'database_scripts',
        '🧪 Test Scripts': 'test_scripts',
        '🤖 AI Scripts': 'ai_scripts'
    }
    
    print("📁 SCRIPTS DISPONIBLES:")
    print("=" * 50)
    
    for category, dir_name in script_dirs.items():
        dir_path = Path(__file__).parent / dir_name
        if dir_path.exists():
            scripts = list(dir_path.glob("*.py"))
            if scripts:
                print(f"\n{category}:")
                for script in sorted(scripts):
                    print(f"  • {script.stem}")
    
    print("\n🚀 USO:")
    print("  python run_script.py <nombre_script>")
    print("  python run_script.py --list")

def main():
    parser = argparse.ArgumentParser(description='Ejecutar scripts del proyecto ICFES-LLM')
    parser.add_argument('script_name', nargs='?', help='Nombre del script a ejecutar')
    parser.add_argument('--list', '-l', action='store_true', help='Listar scripts disponibles')
    
    args = parser.parse_args()
    
    if args.list or not args.script_name:
        list_available_scripts()
        return
    
    script_name = args.script_name
    script_path = get_script_path(script_name)
    
    if not script_path:
        print(f"❌ Script no encontrado: {script_name}")
        print("\n📁 Scripts disponibles:")
        list_available_scripts()
        return
    
    print(f"🔍 Ejecutando: {script_name}")
    print(f"📁 Ubicación: {script_path}")
    print("-" * 50)
    
    # Copiar al contenedor
    if not copy_to_container(script_path):
        return
    
    # Ejecutar en el contenedor
    if not run_in_container(script_name):
        return
    
    print("\n✅ Script ejecutado exitosamente!")

if __name__ == "__main__":
    main() 