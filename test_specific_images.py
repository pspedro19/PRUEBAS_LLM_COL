import requests
import json

def test_specific_question_with_image():
    """Probar una pregunta específica que tenga imagen"""
    base_url = "http://localhost:8000/api"
    
    # Login
    login_data = {
        "username": "testuser_progress",
        "password": "testpass123"
    }
    
    response = requests.post(f"{base_url}/auth/login/", json=login_data)
    if response.status_code != 200:
        print(f"❌ Error en login: {response.status_code}")
        return
    
    token = response.json().get('access')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Iniciar quiz con más preguntas para aumentar probabilidad de obtener una con imagen
    quiz_data = {
        "area": "matematicas",
        "difficulty": "EASY",
        "question_count": 10
    }
    
    response = requests.post(f"{base_url}/icfes/quiz/start-session", json=quiz_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Error iniciando quiz: {response.status_code}")
        return
    
    session_data = response.json()['data']
    session_id = session_data['session_id']
    
    print(f"✅ Quiz iniciado: {session_id}")
    print(f"📊 Total preguntas: {session_data['total_questions']}")
    
    # Procesar todas las preguntas hasta encontrar una con imagen
    for i in range(session_data['total_questions']):
        # Obtener pregunta actual
        response = requests.get(f"{base_url}/icfes/quiz/session/{session_id}/current-question", headers=headers)
        if response.status_code != 200:
            print(f"❌ Error obteniendo pregunta: {response.status_code}")
            break
        
        question_data = response.json()['data']['question']
        print(f"\n--- Pregunta {i+1} ---")
        print(f"📝 ID: {question_data['id']}")
        print(f"📄 Contenido: {question_data['content'][:100]}...")
        print(f"🖼️  Imagen: {question_data.get('image_url', 'No imagen')}")
        
        # Si tiene imagen, probar acceso
        if question_data.get('image_url'):
            image_url = question_data['image_url']
            print(f"🔍 Probando acceso a imagen: {image_url}")
            
            img_response = requests.head(image_url)
            if img_response.status_code == 200:
                print(f"✅ Imagen accesible (Status: {img_response.status_code})")
                print(f"📏 Tamaño: {img_response.headers.get('Content-Length', 'Desconocido')} bytes")
            else:
                print(f"❌ Imagen no accesible (Status: {img_response.status_code})")
        
        # Verificar opciones
        options = question_data.get('options', {})
        print(f"📋 Opciones disponibles: {list(options.keys())}")
        
        # Enviar respuesta
        if options:
            first_option = list(options.keys())[0]
            answer_data = {
                "question_id": question_data['id'],
                "selected_answer": first_option
            }
            
            response = requests.post(f"{base_url}/icfes/quiz/session/{session_id}/submit-icfes-answer", 
                                  json=answer_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Respuesta enviada: {first_option}")
                print(f"📊 Progreso: {result['data']['progress']['current']}/{result['data']['progress']['total']}")
                print(f"🎯 Correcta: {result['data']['is_correct']}")
                
                if result['data']['session_complete']:
                    print("🏆 Quiz completado!")
                    break
            else:
                print(f"❌ Error enviando respuesta: {response.text}")
                break
        else:
            print("❌ No hay opciones disponibles")
            break

if __name__ == "__main__":
    print("🚀 Probando sistema de imágenes con preguntas específicas...")
    test_specific_question_with_image()
    print("✅ Prueba completada") 