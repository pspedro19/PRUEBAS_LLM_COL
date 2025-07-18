#!/usr/bin/env python
"""
Script para probar directamente submit_answer
"""

import os
import sys
import django

# Configurar Django
sys.path.append('backend_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.icfes.models import UserICFESSession
from apps.icfes.models_nuevo import RespuestaUsuarioICFES
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import json

def test_submit_answer():
    """Probar submit_answer directamente"""
    
    print("🧪 TESTING SUBMIT_ANSWER ENDPOINT")
    print("=" * 50)
    
    # Buscar una sesión activa
    sessions = UserICFESSession.objects.all()
    if not sessions:
        print("❌ No hay sesiones para probar")
        return
    
    session = sessions.first()
    print(f"📋 Session encontrada: {session.uuid}")
    print(f"👤 Usuario: {session.user.username}")
    print(f"📊 Status: {session.status}")
    print(f"🎯 Areas filter: {session.areas_filter}")
    
    # Obtener datos de la sesión
    areas_data = session.areas_filter or {}
    preguntas_ids = areas_data.get('preguntas_ids', [])
    
    if not preguntas_ids:
        print("❌ No hay preguntas en la sesión")
        return
    
    print(f"🔢 Preguntas en sesión: {preguntas_ids}")
    
    # Probar submit_answer simulando datos del frontend
    question_id = preguntas_ids[0]  # Primera pregunta
    
    print(f"\n🎯 PROBANDO SUBMIT_ANSWER:")
    print(f"Question ID: {question_id}")
    
    # Verificar que la pregunta existe
    from apps.icfes.models_nuevo import PreguntaICFES
    try:
        pregunta = PreguntaICFES.objects.get(id=question_id)
        print(f"✅ Pregunta encontrada: {pregunta.pregunta_texto[:50]}...")
        print(f"🎯 Respuesta correcta: {pregunta.respuesta_correcta}")
    except PreguntaICFES.DoesNotExist:
        print(f"❌ Pregunta {question_id} NO EXISTE en la base de datos")
        return
    
    # Simular data del frontend
    test_data = {
        'question_id': str(question_id),
        'selected_answer': 'A'  # Respuesta de prueba
    }
    
    print(f"📤 Enviando data: {test_data}")
    
    # Llamar directamente a process_submit_answer
    from apps.icfes.views import process_submit_answer
    from rest_framework.request import Request
    from rest_framework.test import APIRequestFactory

    factory = APIRequestFactory()
    drf_request = factory.post(
        f'/api/icfes/quiz/session/{session.uuid}/submit-answer',
        test_data,
        format='json'
    )
    drf_request.user = session.user
    
    response = process_submit_answer(drf_request, str(session.uuid))
    
    print(f"\n📥 RESPONSE:")
    print(f"Status: {response.status_code}")
    print(f"Content: {response.data}")
    
    if response.status_code == 200:
        try:
            print(f"JSON Response: {json.dumps(response.data, indent=2)}")
        except:
            print("❌ No se pudo parsear JSON")
    
    # Verificar si se guardó la respuesta
    respuestas_guardadas = RespuestaUsuarioICFES.objects.filter(
        session_id=str(session.uuid)
    )
    print(f"\n💾 Respuestas guardadas para esta sesión: {respuestas_guardadas.count()}")
    
    if respuestas_guardadas.exists():
        for resp in respuestas_guardadas:
            print(f"   - Pregunta {resp.pregunta.id}: {resp.opcion_seleccionada} (Correcta: {resp.es_correcta})")

if __name__ == "__main__":
    test_submit_answer() 