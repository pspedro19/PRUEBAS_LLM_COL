#!/usr/bin/env python3
"""
Script de prueba simple para verificar el sistema
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health():
    """Probar el health check"""
    try:
        response = requests.get(f"{BASE_URL}/auth/health/")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check OK")
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def create_test_user():
    """Crear usuario de prueba"""
    try:
        user_data = {
            "username": "test_simple",
            "email": "test_simple@test.com",
            "password": "test123",
            "full_name": "Usuario Test"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
        print(f"Register status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Usuario de prueba creado")
            return True
        elif response.status_code == 400:
            print("ℹ️ Usuario ya existe")
            return True
        else:
            print(f"❌ Error creando usuario: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        return False

def test_login():
    """Probar el login"""
    try:
        login_data = {
            "username": "test_simple",
            "password": "test123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login exitoso")
            print(f"Token: {data.get('access', 'No token')[:50]}...")
            return data.get('access')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_quiz_start(token):
    """Probar iniciar un quiz"""
    if not token:
        print("❌ No token disponible")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        quiz_data = {
            "area": "matematicas",
            "difficulty": "EASY",
            "question_count": 3
        }
        
        response = requests.post(f"{BASE_URL}/icfes/quiz/start-session", 
                               json=quiz_data, headers=headers)
        print(f"Quiz start status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Quiz iniciado exitosamente")
            print(f"Session ID: {data.get('data', {}).get('session_id', 'No session')}")
            return data.get('data', {}).get('session_id')
        else:
            print(f"❌ Quiz start failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en quiz start: {e}")
        return None

def test_submit_answer(token, session_id):
    """Probar enviar una respuesta"""
    if not token or not session_id:
        print("❌ Token o session_id no disponible")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        answer_data = {
            "question_id": 1,  # Primera pregunta
            "selected_answer": "A"  # Opción A
        }
        
        response = requests.post(f"{BASE_URL}/icfes/quiz/session/{session_id}/submit-answer", 
                               json=answer_data, headers=headers)
        print(f"Submit answer status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta enviada exitosamente")
            print(f"Estructura de respuesta: {data}")
            print(f"Correcta: {data.get('data', {}).get('is_correct', 'N/A')}")
            print(f"Session complete: {data.get('data', {}).get('session_complete', 'N/A')}")
            print(f"Progreso: {data.get('data', {}).get('progress', {}).get('current', 0)}/{data.get('data', {}).get('progress', {}).get('total', 0)}")
            return True
        else:
            print(f"❌ Submit answer failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en submit answer: {e}")
        return False

def main():
    print("🧪 PRUEBA SIMPLE DEL SISTEMA")
    print("=" * 40)
    
    # 1. Health check
    if not test_health():
        print("❌ Sistema no disponible")
        return
    
    # 2. Crear usuario de prueba
    if not create_test_user():
        print("❌ No se pudo crear usuario de prueba")
        return
    
    # 3. Login
    token = test_login()
    if not token:
        print("❌ No se pudo autenticar")
        return
    
    # 4. Quiz start
    session_id = test_quiz_start(token)
    if not session_id:
        print("❌ No se pudo iniciar quiz")
        return
    
    # 5. Submit answer
    if test_submit_answer(token, session_id):
        print("✅ Todas las pruebas básicas pasaron")
    else:
        print("❌ Error en submit answer")

if __name__ == "__main__":
    main() 