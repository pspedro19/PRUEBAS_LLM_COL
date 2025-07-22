#!/usr/bin/env python3
"""
Script para analizar el PDF de Cuadernillo de Matemáticas ICFES
y extraer información estructurada sobre las preguntas
"""

import PyPDF2
import re
import json
from pathlib import Path

def analyze_math_pdf(pdf_path):
    """Analiza el PDF de matemáticas y extrae preguntas estructuradas"""
    
    # Verificar que el archivo existe
    if not Path(pdf_path).exists():
        print(f"❌ Error: No se encontró el archivo {pdf_path}")
        return None
    
    extracted_data = {
        "total_pages": 0,
        "questions_found": [],
        "metadata": {
            "file_size_mb": round(Path(pdf_path).stat().st_size / (1024*1024), 2),
            "areas_detected": [],
            "question_types": []
        },
        "raw_text_sample": "",
        "analysis_summary": {}
    }
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            extracted_data["total_pages"] = len(pdf_reader.pages)
            
            print(f"📄 Analizando PDF: {pdf_path}")
            print(f"📊 Total de páginas: {extracted_data['total_pages']}")
            
            # Analizar cada página
            full_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    full_text += f"\n--- PÁGINA {page_num + 1} ---\n{page_text}\n"
                    
                    # Buscar patrones de preguntas
                    questions = extract_questions_from_text(page_text, page_num + 1)
                    extracted_data["questions_found"].extend(questions)
                    
                except Exception as e:
                    print(f"⚠️  Error al procesar página {page_num + 1}: {str(e)}")
                    continue
            
            # Guardar muestra de texto para análisis
            extracted_data["raw_text_sample"] = full_text[:2000] + "..." if len(full_text) > 2000 else full_text
            
            # Análisis general
            extracted_data["analysis_summary"] = analyze_content_patterns(full_text)
            
            print(f"✅ Análisis completado:")
            print(f"   📝 Preguntas encontradas: {len(extracted_data['questions_found'])}")
            print(f"   📏 Tamaño del archivo: {extracted_data['metadata']['file_size_mb']} MB")
            
            return extracted_data
            
    except Exception as e:
        print(f"❌ Error al procesar el PDF: {str(e)}")
        return None

def extract_questions_from_text(text, page_num):
    """Extrae preguntas individuales del texto de una página"""
    questions = []
    
    # Patrones para detectar preguntas
    patterns = [
        r'(\d+\.)\s*(.*?)(?=\d+\.|$)',  # Preguntas numeradas
        r'(Pregunta\s+\d+)',             # "Pregunta X"
        r'([A-D]\.)\s*([^\n]+)',         # Opciones A, B, C, D
    ]
    
    # Buscar preguntas numeradas
    question_pattern = r'(\d+\.)\s*(.*?)(?=\d+\.|A\.|$)'
    matches = re.findall(question_pattern, text, re.DOTALL)
    
    for i, (number, content) in enumerate(matches):
        if len(content.strip()) > 20:  # Filtrar contenido muy corto
            question_data = {
                "number": number.strip('.'),
                "page": page_num,
                "content": content.strip()[:500],  # Limitamos para muestra
                "has_options": bool(re.search(r'[A-D]\.', content)),
                "estimated_difficulty": estimate_difficulty(content),
                "topics_detected": detect_math_topics(content)
            }
            questions.append(question_data)
    
    return questions

def analyze_content_patterns(text):
    """Analiza patrones generales en el contenido"""
    analysis = {
        "total_chars": len(text),
        "has_images_references": bool(re.search(r'figura|imagen|gráfica|diagrama', text, re.IGNORECASE)),
        "has_mathematical_notation": bool(re.search(r'[∑∫√π°∠△]|x\^|log|sen|cos|tan', text)),
        "areas_mentioned": [],
        "question_indicators": len(re.findall(r'\d+\.', text)),
        "option_indicators": len(re.findall(r'[A-D]\.', text)),
    }
    
    # Detectar áreas mencionadas
    areas = [
        ("geometría", r'geometr[íi]a|triángulo|círculo|área|perímetro|volumen'),
        ("álgebra", r'álgebra|ecuación|variable|incógnita|polinomio'),
        ("estadística", r'estadística|probabilidad|media|mediana|moda'),
        ("aritmética", r'aritmética|números|fracción|decimal|porcentaje'),
        ("cálculo", r'derivada|integral|límite|función')
    ]
    
    for area, pattern in areas:
        if re.search(pattern, text, re.IGNORECASE):
            analysis["areas_mentioned"].append(area)
    
    return analysis

def estimate_difficulty(content):
    """Estima la dificultad basada en indicadores en el texto"""
    difficulty_indicators = {
        "básico": [r'suma|resta|número|simple'],
        "intermedio": [r'ecuación|gráfica|sistema|función'],
        "avanzado": [r'derivada|integral|complejo|demostrar']
    }
    
    scores = {"básico": 0, "intermedio": 0, "avanzado": 0}
    
    for level, patterns in difficulty_indicators.items():
        for pattern in patterns:
            scores[level] += len(re.findall(pattern, content, re.IGNORECASE))
    
    return max(scores, key=scores.get) if any(scores.values()) else "intermedio"

def detect_math_topics(content):
    """Detecta temas matemáticos específicos en el contenido"""
    topics = {
        "geometría": [r'triángulo|círculo|cuadrado|área|perímetro|volumen|ángulo'],
        "álgebra": [r'ecuación|variable|x|y|polinomio|factorización'],
        "estadística": [r'probabilidad|media|promedio|datos|gráfico|tabla'],
        "trigonometría": [r'seno|coseno|tangente|ángulo|grados'],
        "cálculo": [r'derivada|integral|límite|función|continua']
    }
    
    detected = []
    for topic, patterns in topics.items():
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                detected.append(topic)
                break
    
    return list(set(detected))

def main():
    pdf_path = "documentos/Cuadernillo-Matematicas-11-1.pdf"
    
    print("🔍 ANALIZADOR DE PDF - CUADERNILLO MATEMÁTICAS ICFES")
    print("=" * 50)
    
    result = analyze_math_pdf(pdf_path)
    
    if result:
        # Guardar resultados en JSON
        output_file = "pdf_analysis_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {output_file}")
        
        # Mostrar resumen
        print("\n📊 RESUMEN DEL ANÁLISIS:")
        print(f"   📄 Páginas: {result['total_pages']}")
        print(f"   📝 Preguntas detectadas: {len(result['questions_found'])}")
        print(f"   📏 Tamaño: {result['metadata']['file_size_mb']} MB")
        print(f"   🔢 Indicadores de pregunta: {result['analysis_summary']['question_indicators']}")
        print(f"   ✅ Indicadores de opciones: {result['analysis_summary']['option_indicators']}")
        print(f"   📊 Áreas detectadas: {', '.join(result['analysis_summary']['areas_mentioned'])}")
        
        if result['questions_found']:
            print(f"\n📝 MUESTRA DE PREGUNTAS:")
            for i, q in enumerate(result['questions_found'][:3]):
                print(f"   {q['number']}. {q['content'][:100]}...")
                print(f"      📍 Página: {q['page']}, Dificultad: {q['estimated_difficulty']}")
                print(f"      🏷️  Temas: {', '.join(q['topics_detected'])}")
                print()
        
    else:
        print("❌ No se pudo analizar el PDF")

if __name__ == "__main__":
    main() 