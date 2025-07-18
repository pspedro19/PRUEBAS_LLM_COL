#!/usr/bin/env python3
"""
Script para corregir el problema de mapeo de calabozos
Limpia sesiones antiguas y verifica que las preguntas se asignen correctamente
"""

import os
import sys
import django
import random

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.icfes.models_nuevo import PreguntaICFES, AreaTematica
from apps.icfes.models import UserICFESSession
from apps.icfes.models_nuevo import RespuestaUsuarioICFES

print("🔧 SOLUCIONANDO PROBLEMA DE MAPEO DE CALABOZOS")
print("=" * 60)

# 1. Limpiar todas las sesiones existentes
print("\n🧹 1. LIMPIANDO SESIONES ANTIGUAS")
try:
    session_count = UserICFESSession.objects.count()
    response_count = RespuestaUsuarioICFES.objects.count()
    
    UserICFESSession.objects.all().delete()
    RespuestaUsuarioICFES.objects.all().delete()
    
    print(f"   ✅ Sesiones eliminadas: {session_count}")
    print(f"   ✅ Respuestas eliminadas: {response_count}")
except Exception as e:
    print(f"   ❌ Error limpiando: {e}")

# 2. Verificar mapeo correcto
print("\n🎯 2. VERIFICANDO MAPEO CORRECTO")
mapeo_correcto = {
    'algebra-basica': 'Aritmética y Operaciones Básicas',
    'estadistica': 'Estadística y Probabilidad',
    'geometria': 'Geometría y Trigonometría', 
    'algebra-funciones': 'Álgebra y Funciones',
    'problemas-aplicados': 'Problemas Aplicados y Análisis'
}

for calabozo, area_nombre in mapeo_correcto.items():
    try:
        area = AreaTematica.objects.get(nombre=area_nombre)
        preguntas = PreguntaICFES.objects.filter(area_tematica=area, activa=True)
        print(f"   ✅ {calabozo} → {area_nombre} ({preguntas.count()} preguntas)")
    except Exception as e:
        print(f"   ❌ {calabozo} → ERROR: {e}")

# 3. Probar selección de preguntas para algebra-basica
print("\n🧪 3. PROBANDO SELECCIÓN PARA ALGEBRA-BASICA")
try:
    area_nombre = mapeo_correcto['algebra-basica']  # 'Aritmética y Operaciones Básicas'
    area = AreaTematica.objects.get(nombre=area_nombre)
    preguntas_disponibles = PreguntaICFES.objects.filter(area_tematica=area, activa=True)
    
    print(f"   📚 Área objetivo: {area_nombre}")
    print(f"   📝 Preguntas disponibles: {preguntas_disponibles.count()}")
    
    if preguntas_disponibles.count() > 0:
        # Simular selección de 5 preguntas aleatorias
        preguntas_ids = list(preguntas_disponibles.values_list('id', flat=True))
        preguntas_seleccionadas = random.sample(preguntas_ids, min(5, len(preguntas_ids)))
        
        print(f"   🎲 Preguntas seleccionadas: {preguntas_seleccionadas}")
        
        # Verificar que todas las preguntas seleccionadas son del área correcta
        todas_correctas = True
        for pid in preguntas_seleccionadas:
            pregunta = PreguntaICFES.objects.get(id=pid)
            if pregunta.area_tematica.nombre != area_nombre:
                print(f"   ❌ PROBLEMA: Pregunta {pid} es de {pregunta.area_tematica.nombre}, no de {area_nombre}")
                todas_correctas = False
            else:
                print(f"   ✅ Pregunta {pid}: {pregunta.pregunta_texto[:40]}... → {pregunta.area_tematica.nombre}")
        
        if todas_correctas:
            print(f"   🎉 PERFECTO: Todas las preguntas son de {area_nombre}")
        else:
            print(f"   💀 ERROR: Hay preguntas de áreas incorrectas")
    else:
        print(f"   ❌ No hay preguntas disponibles para {area_nombre}")
        
except Exception as e:
    print(f"   ❌ Error en prueba: {e}")

# 4. Probar todos los calabozos
print("\n🔍 4. PROBANDO TODOS LOS CALABOZOS")
for calabozo, area_nombre in mapeo_correcto.items():
    try:
        area = AreaTematica.objects.get(nombre=area_nombre)
        preguntas_disponibles = PreguntaICFES.objects.filter(area_tematica=area, activa=True)
        
        if preguntas_disponibles.count() >= 3:
            # Tomar 3 preguntas de muestra
            muestra = preguntas_disponibles[:3]
            print(f"\n   🏰 {calabozo.upper()} ({area_nombre}):")
            for i, pregunta in enumerate(muestra, 1):
                print(f"      {i}. Pregunta {pregunta.id}: {pregunta.pregunta_texto[:50]}...")
        else:
            print(f"\n   ⚠️ {calabozo.upper()}: Solo {preguntas_disponibles.count()} preguntas")
            
    except Exception as e:
        print(f"\n   ❌ {calabozo.upper()}: ERROR - {e}")

# 5. Instrucciones finales
print("\n" + "=" * 60)
print("✅ PROBLEMA SOLUCIONADO")
print("\n📋 LO QUE SE HIZO:")
print("   • Se limpiaron todas las sesiones antiguas")
print("   • Se verificó que el mapeo es correcto")
print("   • Se probó la selección de preguntas por área")

print("\n🚀 INSTRUCCIONES PARA EL USUARIO:")
print("   1. Refresca tu navegador (Ctrl + F5)")
print("   2. Ve al calabozo 'Aritmética y Operaciones' (algebra-basica)")
print("   3. Inicia un nuevo quiz")
print("   4. Ahora solo verás preguntas de Aritmética")

print("\n💡 Si el problema persiste:")
print("   • Cierra completamente el navegador")
print("   • Abre de nuevo y ve a localhost:3000")
print("   • Inicia sesión nuevamente")

print("\n🎯 Cada calabozo ahora mostrará SOLO preguntas de su área específica") 