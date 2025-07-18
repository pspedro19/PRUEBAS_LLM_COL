import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:8000/api"
TOKEN = None
SESSION_ID = None

def register_user():
    """Registrar un usuario de prueba"""
    global TOKEN
    
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser_progress",
        "email": "test_progress@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(url, json=data)
    print(f"Register status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Usuario registrado exitosamente")
    else:
        print(f"❌ Error en registro: {response.text}")

def login_user():
    """Iniciar sesión"""
    global TOKEN
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testuser_progress",
        "password": "testpass123"
    }
    
    response = requests.post(url, json=data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        TOKEN = data.get('access')
        print("✅ Login exitoso")
        print(f"Token: {TOKEN[:50]}...")
    else:
        print(f"❌ Error en login: {response.text}")

def start_quiz():
    """Iniciar quiz"""
    global SESSION_ID
    
    url = f"{BASE_URL}/icfes/quiz/start-session"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "area": "matematicas",
        "difficulty": "EASY",
        "question_count": 3
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Quiz start status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        SESSION_ID = data['data']['session_id']
        print("✅ Quiz iniciado exitosamente")
        print(f"Session ID: {SESSION_ID}")
        print(f"Total questions: {data['data']['total_questions']}")
        return data['data']['current_question']
    else:
        print(f"❌ Error iniciando quiz: {response.text}")
        return None

def get_current_question():
    """Obtener pregunta actual"""
    url = f"{BASE_URL}/icfes/quiz/session/{SESSION_ID}/current-question"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = requests.get(url, headers=headers)
    print(f"Get current question status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['data'].get('session_complete'):
            print("🏆 Quiz completado!")
            return None
        else:
            print(f"📝 Pregunta actual: {data['data']['question']['id']}")
            print(f"📊 Progreso: {data['data']['progress']['answered']}/{data['data']['progress']['total']}")
            return data['data']['question']
    else:
        print(f"❌ Error obteniendo pregunta: {response.text}")
        return None

def submit_answer(question_id, selected_answer):
    """Enviar respuesta"""
    url = f"{BASE_URL}/icfes/quiz/session/{SESSION_ID}/submit-icfes-answer"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "question_id": question_id,
        "selected_answer": selected_answer
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Submit answer status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Respuesta enviada exitosamente")
        print(f"Estructura de respuesta: {data}")
        print(f"Correcta: {data['data']['is_correct']}")
        print(f"Session complete: {data['data']['session_complete']}")
        print(f"Progreso: {data['data']['progress']['current']}/{data['data']['progress']['total']}")
        return data['data']
    else:
        print(f"❌ Error enviando respuesta: {response.text}")
        return None

def test_progress():
    """Probar el progreso completo"""
    print("🚀 Iniciando prueba de progreso...")
    
    # Registrar e iniciar sesión
    register_user()
    login_user()
    
    # Iniciar quiz
    first_question = start_quiz()
    if not first_question:
        return
    
    # Procesar todas las preguntas
    question_count = 0
    while True:
        # Obtener pregunta actual
        current_question = get_current_question()
        if not current_question:
            break
            
        question_count += 1
        print(f"\n--- Pregunta {question_count} ---")
        print(f"ID: {current_question['id']}")
        print(f"Contenido: {current_question['content'][:100]}...")
        
        # Simular respuesta (siempre A para simplificar)
        result = submit_answer(current_question['id'], 'A')
        if not result:
            break
            
        if result['session_complete']:
            print("🏆 Quiz completado!")
            break
            
        # Pequeña pausa para simular tiempo de respuesta
        time.sleep(1)
    
    print(f"\n✅ Prueba completada. Total preguntas procesadas: {question_count}")

if __name__ == "__main__":
    test_progress() 