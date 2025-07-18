import subprocess

def check_image_urls():
    """Verificar URLs de imágenes en la base de datos"""
    cmd = '''docker-compose exec backend python manage.py shell -c "
from apps.icfes.models_nuevo import PreguntaICFES
preguntas = PreguntaICFES.objects.filter(imagen_pregunta_url__isnull=False).exclude(imagen_pregunta_url='')
for p in preguntas[:5]:
    filename = p.imagen_pregunta_url.split('/')[-1]
    print(f'{p.id}|{filename}')
"'''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ URLs de imágenes en la base de datos:")
        for line in result.stdout.strip().split('\n'):
            if line and '|' in line:
                parts = line.split('|')
                print(f"Pregunta {parts[0]}: {parts[1]}")
    else:
        print(f"❌ Error: {result.stderr}")

def check_available_files():
    """Verificar archivos disponibles en el contenedor"""
    cmd = 'docker-compose exec backend ls /app/media/icfes_images/'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✅ Archivos disponibles en el contenedor:")
        files = result.stdout.strip().split('\n')
        for file in files[:10]:  # Mostrar solo los primeros 10
            if file:
                print(f"  {file}")
        if len(files) > 10:
            print(f"  ... y {len(files) - 10} archivos más")
    else:
        print(f"❌ Error: {result.stderr}")

def test_image_access():
    """Probar acceso a una imagen específica"""
    print("\n🔍 Probando acceso a imagen...")
    
    # Probar con curl desde el contenedor
    cmd = 'docker-compose exec backend curl -I http://localhost:8000/media/icfes_images/Math_1_1_Doc1.png'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Imagen accesible desde el servidor")
        print(result.stdout)
    else:
        print("❌ Error accediendo a la imagen")
        print(result.stderr)

if __name__ == "__main__":
    print("🚀 Verificando configuración de imágenes...")
    
    check_image_urls()
    check_available_files()
    test_image_access()
    
    print("\n✅ Verificación completada") 