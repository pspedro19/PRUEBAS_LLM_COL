import requests
import time

def test_backend():
    url = "http://127.0.0.1:8000/docs"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Backend está funcionando correctamente!")
            print(f"URL: {url}")
            print("Puedes abrir esta URL en tu navegador para ver la documentación de la API")
        else:
            print(f"❌ Backend respondió con código: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al backend. Asegúrate de que esté corriendo.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Probando conexión al backend...")
    test_backend() 