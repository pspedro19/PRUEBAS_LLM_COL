import requests
import json

def test_ai_apis():
    """Probar las APIs del sistema de LLM"""
    base_url = "http://localhost:8000/api"
    
    # Login
    login_data = {
        "username": "test_ai_user",
        "password": "testpass123"
    }
    
    response = requests.post(f"{base_url}/auth/login/", json=login_data)
    if response.status_code != 200:
        print(f"❌ Error en login: {response.status_code}")
        return
    
    token = response.json().get('access')
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Probando APIs del sistema de LLM...")
    
    # Probar modelos de IA
    response = requests.get(f"{base_url}/ai-llm/models/", headers=headers)
    if response.status_code == 200:
        models = response.json()
        print(f"✅ Modelos de IA: {len(models)} modelos encontrados")
        for model in models:
            print(f"  - {model['name']} ({model['provider']}/{model['model_identifier']})")
    else:
        print(f"❌ Error obteniendo modelos: {response.status_code}")
    
    # Probar templates de prompts
    response = requests.get(f"{base_url}/ai-llm/prompt-templates/", headers=headers)
    if response.status_code == 200:
        templates = response.json()
        print(f"✅ Templates de prompts: {len(templates)} templates encontrados")
        for template in templates:
            print(f"  - {template['name']} ({template['code']})")
    else:
        print(f"❌ Error obteniendo templates: {response.status_code}")
    
    # Probar cuotas de uso
    response = requests.get(f"{base_url}/ai-llm/quotas/", headers=headers)
    if response.status_code == 200:
        quotas = response.json()
        print(f"✅ Cuotas de uso: {len(quotas)} cuotas encontradas")
        for quota in quotas:
            print(f"  - Usuario: {quota['user']}, Límite diario: {quota['daily_limit']}")
    else:
        print(f"❌ Error obteniendo cuotas: {response.status_code}")
    
    print("✅ Pruebas de APIs completadas")

if __name__ == "__main__":
    test_ai_apis() 