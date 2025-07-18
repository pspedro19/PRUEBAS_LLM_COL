import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

def create_sample_image(text, filename, width=800, height=600):
    """Crear una imagen de ejemplo con texto"""
    # Crear imagen con fondo blanco
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Intentar usar una fuente del sistema, si no está disponible usar la predeterminada
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Dividir el texto en líneas
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        # Verificar si la línea actual es muy larga
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] > width - 40:  # Margen de 20px en cada lado
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Dibujar el texto centrado
    y_position = 50
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_position = (width - text_width) // 2
        draw.text((x_position, y_position), line, fill='black', font=font)
        y_position += 40
    
    # Agregar un borde
    draw.rectangle([(10, 10), (width-10, height-10)], outline='blue', width=3)
    
    # Guardar la imagen
    image.save(filename, 'PNG')
    print(f"✅ Imagen creada: {filename}")

def get_preguntas_with_images():
    """Obtener preguntas con imágenes desde el contenedor"""
    cmd = '''docker-compose exec backend python manage.py shell -c "
from apps.icfes.models_nuevo import PreguntaICFES
preguntas = PreguntaICFES.objects.filter(imagen_pregunta_url__isnull=False).exclude(imagen_pregunta_url='')
for p in preguntas:
    print(f'{p.id}|{p.imagen_pregunta_url}|{p.pregunta_texto[:100]}')
"'''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error obteniendo preguntas: {result.stderr}")
        return []
    
    preguntas = []
    for line in result.stdout.strip().split('\n'):
        if line and '|' in line:
            parts = line.split('|', 2)
            if len(parts) >= 3:
                preguntas.append({
                    'id': parts[0],
                    'imagen_url': parts[1],
                    'texto': parts[2]
                })
    
    return preguntas

def generate_images():
    """Generar imágenes para las preguntas"""
    print("🔍 Obteniendo preguntas con imágenes...")
    preguntas = get_preguntas_with_images()
    
    if not preguntas:
        print("❌ No se encontraron preguntas con imágenes")
        return
    
    print(f"📝 Encontradas {len(preguntas)} preguntas con imágenes")
    
    # Crear carpeta local
    os.makedirs("backend_django/media/icfes_images", exist_ok=True)
    
    # Generar imágenes
    for pregunta in preguntas:
        # Extraer nombre del archivo de la URL
        filename = pregunta['imagen_url'].split('/')[-1]
        local_path = f"backend_django/media/icfes_images/{filename}"
        
        # Crear imagen de ejemplo
        texto = pregunta['texto']
        create_sample_image(texto, local_path)
    
    print(f"✅ Generadas {len(preguntas)} imágenes")

def copy_to_container():
    """Copiar imágenes al contenedor"""
    print("📦 Copiando imágenes al contenedor...")
    
    # Copiar carpeta completa al contenedor
    cmd = 'docker cp backend_django/media/icfes_images mathquest-backend:/app/media/'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Imágenes copiadas al contenedor")
    else:
        print(f"❌ Error copiando imágenes: {result.stderr}")

def verify_images():
    """Verificar que las imágenes están en el contenedor"""
    print("🔍 Verificando imágenes en el contenedor...")
    
    cmd = 'docker-compose exec backend ls -la /app/media/icfes_images/'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Imágenes verificadas en el contenedor:")
        print(result.stdout)
    else:
        print(f"❌ Error verificando imágenes: {result.stderr}")

if __name__ == "__main__":
    print("🚀 Generando imágenes para preguntas ICFES...")
    
    # Generar imágenes
    generate_images()
    
    # Copiar al contenedor
    copy_to_container()
    
    # Verificar
    verify_images()
    
    print("✅ Proceso completado") 