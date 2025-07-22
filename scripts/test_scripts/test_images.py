import requests
import json

def test_quiz_with_images():
    """Probar el quiz y verificar que las imágenes se muestran"""
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
    
    # Iniciar quiz
    quiz_data = {
        "area": "matematicas",
        "difficulty": "EASY",
        "question_count": 2
    }
    
    response = requests.post(f"{base_url}/icfes/quiz/start-session", json=quiz_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Error iniciando quiz: {response.status_code}")
        return
    
    session_data = response.json()['data']
    session_id = session_data['session_id']
    first_question = session_data['current_question']
    
    print(f"✅ Quiz iniciado: {session_id}")
    print(f"📝 Primera pregunta: {first_question['id']}")
    print(f"📄 Contenido: {first_question['content'][:100]}...")
    print(f"🖼️  Imagen: {first_question.get('image_url', 'No imagen')}")
    
    # Verificar si la imagen es accesible
    if first_question.get('image_url'):
        image_url = first_question['image_url']
        if image_url.startswith('http://localhost:8000'):
            # Probar acceso a la imagen
            img_response = requests.head(image_url)
            if img_response.status_code == 200:
                print(f"✅ Imagen accesible: {image_url}")
            else:
                print(f"❌ Imagen no accesible: {image_url} (Status: {img_response.status_code})")
        else:
            print(f"ℹ️  URL de imagen: {image_url}")
    
    # Obtener pregunta actual
    response = requests.get(f"{base_url}/icfes/quiz/session/{session_id}/current-question", headers=headers)
    if response.status_code == 200:
        question_data = response.json()['data']['question']
        print(f"\n📝 Pregunta actual: {question_data['id']}")
        print(f"📄 Contenido: {question_data['content'][:100]}...")
        print(f"🖼️  Imagen: {question_data.get('image_url', 'No imagen')}")
        
        # Verificar opciones
        options = question_data.get('options', {})
        print(f"📋 Opciones disponibles: {list(options.keys())}")
        
        # Enviar respuesta con la primera opción disponible
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
            else:
                print(f"❌ Error enviando respuesta: {response.text}")
        else:
            print("❌ No hay opciones disponibles para esta pregunta")

if __name__ == "__main__":
    print("🚀 Probando sistema de imágenes...")
    test_quiz_with_images()
    print("✅ Prueba completada") 