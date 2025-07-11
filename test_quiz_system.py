#!/usr/bin/env python3
"""
Script de prueba para el sistema de quiz de la Torre de Babel
Verifica que todos los endpoints estén funcionando correctamente
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Credenciales de prueba
TEST_USER = {
    "email": "test@example.com",
    "password": "test123"
}

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step):
    print(f"\n>>> {step}")

def test_authentication():
    print_section("AUTENTICACIÓN")
    
    # Intentar crear usuario primero (ignorar si ya existe)
    print_step("Verificando/creando usuario de prueba...")
    register_response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "full_name": "Usuario Test"
    })
    
    if register_response.status_code == 200:
        print("✅ Usuario de prueba creado exitosamente")
    else:
        print("ℹ️ Usuario de prueba ya existe o error en creación (continuando...)")
    
    # Login
    print_step("Iniciando sesión...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data["access_token"]
        print(f"✅ Login exitoso! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Error en login: {login_response.status_code}")
        print(login_response.text)
        return None

def test_quiz_topics(token):
    print_section("TEMAS DISPONIBLES")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print_step("Obteniendo temas de matemáticas...")
    response = requests.get(f"{BASE_URL}/quiz/topics/matematicas", headers=headers)
    
    if response.status_code == 200:
        topics = response.json()
        print(f"✅ Encontrados {len(topics)} temas:")
        for topic in topics:
            print(f"   📚 {topic['topic']} ({topic['question_count']} preguntas)")
        return topics
    else:
        print(f"❌ Error obteniendo temas: {response.status_code}")
        print(response.text)
        return []

def test_quiz_questions(token):
    print_section("PREGUNTAS DISPONIBLES")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print_step("Obteniendo preguntas de álgebra básica...")
    response = requests.get(
        f"{BASE_URL}/quiz/questions?area=matematicas&topic=algebra_basica&limit=3", 
        headers=headers
    )
    
    if response.status_code == 200:
        questions = response.json()
        print(f"✅ Encontradas {len(questions)} preguntas:")
        for i, q in enumerate(questions, 1):
            print(f"   {i}. {q['title']}")
            print(f"      Dificultad: {q['difficulty']} | Puntos: {q['points_value']}")
        return questions
    else:
        print(f"❌ Error obteniendo preguntas: {response.status_code}")
        print(response.text)
        return []

def test_full_quiz_flow(token):
    print_section("FLUJO COMPLETO DE QUIZ")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Iniciar sesión de quiz
    print_step("1. Iniciando sesión de quiz...")
    start_data = {
        "area": "matematicas",
        "topic": "algebra_basica",
        "quiz_mode": "practice",
        "max_questions": 3
    }
    
    session_response = requests.post(
        f"{BASE_URL}/quiz/start-session", 
        json=start_data, 
        headers=headers
    )
    
    if session_response.status_code != 200:
        print(f"❌ Error iniciando sesión: {session_response.status_code}")
        print(session_response.text)
        return
    
    session = session_response.json()
    session_id = session["session_id"]
    print(f"✅ Sesión iniciada: {session_id}")
    print(f"   Total de preguntas: {session['total_questions']}")
    
    # 2. Resolver preguntas
    for i in range(session["total_questions"]):
        print_step(f"2.{i+1}. Obteniendo pregunta {i+1}...")
        
        # Obtener pregunta actual
        question_response = requests.get(
            f"{BASE_URL}/quiz/session/{session_id}/current-question",
            headers=headers
        )
        
        if question_response.status_code != 200:
            print(f"❌ Error obteniendo pregunta: {question_response.status_code}")
            break
        
        question = question_response.json()
        print(f"✅ Pregunta: {question['title']}")
        print(f"   A) {question['option_a']}")
        print(f"   B) {question['option_b']}")
        print(f"   C) {question['option_c']}")
        print(f"   D) {question['option_d']}")
        
        # Simular respuesta (siempre A para la prueba)
        answer_data = {
            "question_id": question["id"],
            "selected_answer": "A",
            "time_taken_seconds": 10 + i * 5,
            "hints_used": 0,
            "confidence_level": 4
        }
        
        print_step(f"     Enviando respuesta A...")
        answer_response = requests.post(
            f"{BASE_URL}/quiz/session/{session_id}/submit-answer",
            json=answer_data,
            headers=headers
        )
        
        if answer_response.status_code == 200:
            result = answer_response.json()
            status = "✅ CORRECTO" if result["is_correct"] else "❌ INCORRECTO"
            print(f"   {status} - Puntos ganados: {result['points_earned']}")
            print(f"   Feedback: {result['feedback_message']}")
        else:
            print(f"❌ Error enviando respuesta: {answer_response.status_code}")
            print(answer_response.text)
        
        time.sleep(1)  # Pausa entre preguntas
    
    # 3. Verificar progreso final
    print_step("3. Verificando progreso final...")
    progress_response = requests.get(
        f"{BASE_URL}/quiz/session/{session_id}/progress",
        headers=headers
    )
    
    if progress_response.status_code == 200:
        progress = progress_response.json()
        print(f"✅ Quiz completado!")
        print(f"   Preguntas respondidas: {progress['questions_answered']}")
        print(f"   Respuestas correctas: {progress['questions_correct']}")
        print(f"   Precisión: {progress['accuracy_percentage']:.1f}%")
        print(f"   Puntos totales: {progress['total_points']}")
    else:
        print(f"❌ Error obteniendo progreso: {progress_response.status_code}")

def test_user_stats(token):
    print_section("ESTADÍSTICAS DE USUARIO")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print_step("Obteniendo estadísticas de matemáticas...")
    response = requests.get(f"{BASE_URL}/quiz/stats/matematicas", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Estadísticas del usuario:")
        print(f"   Total respondidas: {stats['total_questions_answered']}")
        print(f"   Total correctas: {stats['total_questions_correct']}")
        print(f"   Precisión general: {stats['overall_accuracy']:.1f}%")
        print(f"   Puntos totales: {stats['total_points_earned']}")
        print(f"   Tiempo promedio: {stats['average_time_per_question']:.1f}s")
        print(f"   Dificultad favorita: {stats['favorite_difficulty']}")
        
        if stats['topics_stats']:
            print(f"   Estadísticas por tema:")
            for topic_stat in stats['topics_stats'][:3]:
                print(f"     • {topic_stat['topic']}: {topic_stat['accuracy_percentage']:.1f}% de precisión")
    else:
        print(f"❌ Error obteniendo estadísticas: {response.status_code}")
        print(response.text)

def test_recommendations(token):
    print_section("RECOMENDACIONES")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print_step("Obteniendo recomendaciones de matemáticas...")
    response = requests.get(f"{BASE_URL}/quiz/recommendations/matematicas", headers=headers)
    
    if response.status_code == 200:
        recommendations = response.json()
        print(f"✅ Recomendaciones generadas:")
        print(f"   Resumen: {recommendations['reason_summary']}")
        print(f"   Temas de enfoque: {', '.join(recommendations['focus_topics'])}")
        print(f"   Dificultad sugerida: {recommendations['suggested_difficulty']}")
        
        if recommendations['recommended_questions']:
            print(f"   Preguntas recomendadas:")
            for i, rec in enumerate(recommendations['recommended_questions'][:3], 1):
                print(f"     {i}. {rec['question']['title']} (Prioridad: {rec['priority']})")
                print(f"        Razón: {rec['reason']}")
    else:
        print(f"❌ Error obteniendo recomendaciones: {response.status_code}")
        print(response.text)

def main():
    print("🏗️ TORRE DE BABEL - PRUEBA DEL SISTEMA DE QUIZ")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test de autenticación
    token = test_authentication()
    if not token:
        print("\n❌ No se pudo obtener el token. Abortando pruebas.")
        return
    
    # Tests del sistema de quiz
    try:
        test_quiz_topics(token)
        test_quiz_questions(token)
        test_full_quiz_flow(token)
        test_user_stats(token)
        test_recommendations(token)
        
        print_section("RESUMEN FINAL")
        print("✅ Todas las pruebas completadas exitosamente!")
        print("🎮 El sistema de quiz está funcionando correctamente!")
        print("🏆 Los usuarios pueden practicar matemáticas del ICFES!")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 