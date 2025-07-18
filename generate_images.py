import requests
from PIL import Image, ImageDraw, ImageFont
import os
import io

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

def generate_icfes_images():
    """Generar imágenes para las preguntas ICFES"""
    base_url = "http://localhost:8000/api"
    
    # Obtener preguntas con imágenes
    url = f"{base_url}/icfes/questions/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo preguntas: {response.status_code}")
        return
    
    preguntas = response.json()
    
    # Crear carpeta local si no existe
    os.makedirs("backend_django/media/icfes_images", exist_ok=True)
    
    for pregunta in preguntas:
        if pregunta.get('imagen_pregunta_url'):
            # Extraer nombre del archivo de la URL
            filename = pregunta['imagen_pregunta_url'].split('/')[-1]
            local_path = f"backend_django/media/icfes_images/{filename}"
            
            # Crear imagen de ejemplo
            texto = pregunta.get('pregunta_texto', 'Pregunta de ejemplo')
            create_sample_image(texto, local_path)
    
    print(f"✅ Generadas {len([p for p in preguntas if p.get('imagen_pregunta_url')])} imágenes")

def copy_images_to_container():
    """Copiar imágenes al contenedor"""
    import subprocess
    
    # Copiar carpeta completa al contenedor
    cmd = f'docker cp backend_django/media/icfes_images mathquest-backend:/app/media/'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Imágenes copiadas al contenedor")
    else:
        print(f"❌ Error copiando imágenes: {result.stderr}")

if __name__ == "__main__":
    print("🚀 Generando imágenes para preguntas ICFES...")
    
    # Generar imágenes localmente
    generate_icfes_images()
    
    # Copiar al contenedor
    copy_images_to_container()
    
    print("✅ Proceso completado") 