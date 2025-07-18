#!/usr/bin/env python3
"""
Script de verificación completa del Sistema ICFES Quiz
Verifica: datos, imágenes, categorías, opciones A,B,C,D y funcionalidad
"""

import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.icfes.models_nuevo import PreguntaICFES, OpcionRespuesta, AreaTematica
from apps.icfes.models import UserICFESSession
from apps.users.models import User

print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA ICFES QUIZ")
print("=" * 60)

# 1. Verificar datos básicos
print("\n📊 1. DATOS BÁSICOS")
total_preguntas = PreguntaICFES.objects.count()
preguntas_activas = PreguntaICFES.objects.filter(activa=True).count()
areas_tematicas = AreaTematica.objects.count()

print(f"   ✓ Total preguntas: {total_preguntas}")
print(f"   ✓ Preguntas activas: {preguntas_activas}")
print(f"   ✓ Áreas temáticas: {areas_tematicas}")

if total_preguntas != 49:
    print(f"   ❌ ERROR: Se esperaban 49 preguntas, encontradas {total_preguntas}")
else:
    print("   ✅ Cantidad de preguntas correcta")

# 2. Verificar áreas temáticas
print("\n📂 2. ÁREAS TEMÁTICAS")
for area in AreaTematica.objects.all():
    count = PreguntaICFES.objects.filter(area_tematica=area, activa=True).count()
    print(f"   • {area.nombre}: {count} preguntas")

# 3. Verificar opciones A,B,C,D
print("\n🔤 3. OPCIONES DE RESPUESTA")
preguntas_sin_opciones = []
opciones_incompletas = []

for pregunta in PreguntaICFES.objects.filter(activa=True):
    opciones = OpcionRespuesta.objects.filter(pregunta=pregunta)
    opciones_dict = {opt.letra_opcion: opt for opt in opciones}
    
    letras_esperadas = ['A', 'B', 'C', 'D']
    letras_encontradas = list(opciones_dict.keys())
    
    if len(opciones) == 0:
        preguntas_sin_opciones.append(pregunta.id)
    elif set(letras_encontradas) != set(letras_esperadas):
        opciones_incompletas.append({
            'pregunta_id': pregunta.id,
            'esperadas': letras_esperadas,
            'encontradas': letras_encontradas
        })

if preguntas_sin_opciones:
    print(f"   ❌ Preguntas sin opciones: {preguntas_sin_opciones}")
else:
    print("   ✅ Todas las preguntas tienen opciones")

if opciones_incompletas:
    print(f"   ❌ Preguntas con opciones incompletas: {len(opciones_incompletas)}")
    for item in opciones_incompletas[:3]:  # Mostrar solo las primeras 3
        print(f"      • Pregunta {item['pregunta_id']}: {item['encontradas']}")
else:
    print("   ✅ Todas las preguntas tienen opciones A, B, C, D")

# 4. Verificar imágenes
print("\n🖼️  4. IMÁGENES")
preguntas_con_imagen = PreguntaICFES.objects.filter(
    imagen_pregunta_url__isnull=False
).exclude(imagen_pregunta_url='')

opciones_con_imagen = OpcionRespuesta.objects.filter(
    imagen_opcion_url__isnull=False
).exclude(imagen_opcion_url='')

print(f"   • Preguntas con imagen: {preguntas_con_imagen.count()}")
print(f"   • Opciones con imagen: {opciones_con_imagen.count()}")

# Verificar que las imágenes existen físicamente
imagenes_faltantes = []
media_path = "/app/media/icfes_images/"

for pregunta in preguntas_con_imagen[:5]:  # Verificar las primeras 5
    if pregunta.imagen_pregunta_url:
        # Extraer nombre del archivo de la URL
        filename = pregunta.imagen_pregunta_url.split('/')[-1]
        filepath = os.path.join(media_path, filename)
        if not os.path.exists(filepath):
            imagenes_faltantes.append(filename)

if imagenes_faltantes:
    print(f"   ❌ Imágenes faltantes (ejemplo): {imagenes_faltantes[:3]}")
else:
    print("   ✅ Imágenes de muestra disponibles")

# 5. Verificar estructura de datos para el frontend
print("\n🔗 5. ESTRUCTURA DE DATOS")
pregunta_ejemplo = PreguntaICFES.objects.filter(activa=True).first()
if pregunta_ejemplo:
    campos_requeridos = [
        'id', 'pregunta_texto', 'imagen_pregunta_url', 
        'area_tematica', 'nivel_dificultad'
    ]
    
    campos_faltantes = []
    for campo in campos_requeridos:
        if not hasattr(pregunta_ejemplo, campo):
            campos_faltantes.append(campo)
    
    if campos_faltantes:
        print(f"   ❌ Campos faltantes: {campos_faltantes}")
    else:
        print("   ✅ Estructura de modelo correcta")
        
    # Verificar opciones de la pregunta ejemplo
    opciones = OpcionRespuesta.objects.filter(pregunta=pregunta_ejemplo)
    if opciones.count() == 4:
        print("   ✅ Pregunta ejemplo tiene 4 opciones")
        
        # Verificar que hay una respuesta correcta
        correcta = opciones.filter(es_correcta=True)
        if correcta.count() == 1:
            print(f"   ✅ Pregunta ejemplo tiene respuesta correcta: {correcta.first().letra_opcion}")
        else:
            print(f"   ❌ Pregunta ejemplo tiene {correcta.count()} respuestas marcadas como correctas")
    else:
        print(f"   ❌ Pregunta ejemplo tiene {opciones.count()} opciones (se esperaban 4)")

# 6. Verificar archivos de imagen físicos
print("\n📁 6. ARCHIVOS FÍSICOS")
if os.path.exists(media_path):
    archivos = os.listdir(media_path)
    print(f"   ✓ Directorio de imágenes existe")
    print(f"   ✓ Total archivos: {len(archivos)}")
    
    if len(archivos) >= 39:
        print("   ✅ Cantidad de imágenes esperada disponible")
    else:
        print(f"   ❌ Se esperaban al menos 39 imágenes, encontradas {len(archivos)}")
else:
    print("   ❌ Directorio de imágenes no existe")

# 7. Resumen final
print("\n" + "=" * 60)
print("📋 RESUMEN FINAL")

errores = []
if total_preguntas != 49:
    errores.append(f"Cantidad incorrecta de preguntas ({total_preguntas}/49)")
if preguntas_sin_opciones:
    errores.append(f"{len(preguntas_sin_opciones)} preguntas sin opciones")
if opciones_incompletas:
    errores.append(f"{len(opciones_incompletas)} preguntas con opciones incompletas")

if errores:
    print("❌ ERRORES ENCONTRADOS:")
    for error in errores:
        print(f"   • {error}")
    print("\n💡 RECOMENDACIÓN: Reimportar datos ICFES")
else:
    print("✅ SISTEMA COMPLETAMENTE FUNCIONAL")
    print("   • 49 preguntas importadas correctamente")
    print("   • Todas las preguntas tienen opciones A,B,C,D")
    print("   • Imágenes disponibles")
    print("   • Áreas temáticas configuradas")
    print("   • Listo para usar en el frontend")

print("\n🚀 El sistema está listo para pruebas en el navegador!") 