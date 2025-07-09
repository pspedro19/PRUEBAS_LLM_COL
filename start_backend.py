import subprocess
import sys
import os

def start_backend():
    # Cambiar al directorio del backend
    backend_dir = os.path.join(os.getcwd(), "backend")
    os.chdir(backend_dir)
    
    # Comando para iniciar el backend
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.api.main:app", 
        "--reload", 
        "--host", "127.0.0.1", 
        "--port", "8000"
    ]
    
    print("Iniciando backend...")
    print(f"Directorio: {backend_dir}")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        # Iniciar el proceso
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Mostrar algunos logs iniciales
        for i in range(10):  # Mostrar las primeras 10 líneas
            line = process.stdout.readline()
            if line:
                print(line.strip())
            else:
                break
                
        print("\n✅ Backend iniciado. Presiona Ctrl+C para detener.")
        print("🌐 Accede a http://127.0.0.1:8000/docs para ver la API")
        
        # Mantener el proceso corriendo
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo backend...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    start_backend() 