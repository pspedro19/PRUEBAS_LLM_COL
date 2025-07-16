"""
Comando Django para importar preguntas ICFES desde el análisis del PDF
"""

import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.questions.models import (
    Subject, Topic, ICFESCuadernillo, Question, QuestionOption, 
    QuestionExplanation, QuestionMultimedia
)


class Command(BaseCommand):
    help = 'Importa preguntas ICFES desde el análisis del PDF'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pdf-analysis',
            type=str,
            default='pdf_analysis_result.json',
            help='Ruta al archivo JSON con el análisis del PDF'
        )
        parser.add_argument(
            '--cuadernillo-name',
            type=str,
            default='Matemáticas 11° Cuadernillo 1',
            help='Nombre del cuadernillo'
        )
        parser.add_argument(
            '--period',
            type=str,
            default='2024-1',
            help='Período del cuadernillo (ej: 2024-1)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular la importación sin guardar en la base de datos'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Iniciando importación de preguntas ICFES...')
        )

        # Cargar archivo de análisis
        pdf_analysis_path = options['pdf_analysis']
        if not os.path.exists(pdf_analysis_path):
            raise CommandError(f'Archivo no encontrado: {pdf_analysis_path}')

        with open(pdf_analysis_path, 'r', encoding='utf-8') as f:
            pdf_data = json.load(f)

        # Crear o recuperar objetos base
        subject = self.get_or_create_subject()
        topics = self.get_or_create_topics(subject)
        cuadernillo = self.get_or_create_cuadernillo(
            options['cuadernillo_name'], 
            options['period'], 
            subject,
            pdf_data
        )

        # Procesar preguntas
        questions_imported = 0
        questions_skipped = 0

        for question_data in pdf_data.get('questions_found', []):
            try:
                if self.should_import_question(question_data):
                    question = self.create_question(
                        question_data, 
                        subject, 
                        topics, 
                        cuadernillo,
                        options['dry_run']
                    )
                    if question:
                        questions_imported += 1
                        self.stdout.write(f"✅ Pregunta {question_data.get('number')} importada")
                    else:
                        questions_skipped += 1
                        self.stdout.write(f"⏭️ Pregunta {question_data.get('number')} omitida")
                else:
                    questions_skipped += 1
                    self.stdout.write(f"⏭️ Pregunta {question_data.get('number')} omitida (incompleta)")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error en pregunta {question_data.get('number')}: {str(e)}")
                )
                questions_skipped += 1

        # Reporte final
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Importación completada!\n"
                f"📊 Preguntas importadas: {questions_imported}\n"
                f"⏭️ Preguntas omitidas: {questions_skipped}\n"
                f"📝 Cuadernillo: {cuadernillo.name if not options['dry_run'] else 'DRY RUN'}"
            )
        )

    def get_or_create_subject(self):
        """Obtiene o crea la materia de Matemáticas"""
        subject, created = Subject.objects.get_or_create(
            code='MATH_11',
            defaults={
                'name': 'Matemáticas',
                'area': 'MATHEMATICS',
                'description': 'Matemáticas para grado 11',
                'color_theme': '#FF6B35'
            }
        )
        if created:
            self.stdout.write(f"✅ Materia creada: {subject.name}")
        return subject

    def get_or_create_topics(self, subject):
        """Crea los temas matemáticos principales"""
        topics_data = [
            ('algebra', 'Álgebra', 'Ecuaciones, funciones y expresiones algebraicas'),
            ('geometria', 'Geometría', 'Figuras geométricas, áreas y volúmenes'),
            ('trigonometria', 'Trigonometría', 'Funciones trigonométricas y aplicaciones'),
            ('estadistica', 'Estadística', 'Análisis de datos, gráficas y probabilidad'),
            ('calculo', 'Cálculo', 'Límites, derivadas e integrales básicas'),
            ('aritmetica', 'Aritmética', 'Operaciones básicas y propiedades numéricas'),
        ]

        topics = {}
        for code, name, description in topics_data:
            topic, created = Topic.objects.get_or_create(
                subject=subject,
                name=name,
                defaults={
                    'description': description,
                    'keywords': [code, name.lower()],
                    'order': len(topics)
                }
            )
            topics[code] = topic
            if created:
                self.stdout.write(f"✅ Tema creado: {name}")

        return topics

    def get_or_create_cuadernillo(self, name, period, subject, pdf_data):
        """Crea el cuadernillo ICFES"""
        cuadernillo, created = ICFESCuadernillo.objects.get_or_create(
            code='M111_2024_1',
            defaults={
                'name': name,
                'cuadernillo_type': 'SABER_11',
                'period': period,
                'subject': subject,
                'grade_level': 11,
                'total_pages': pdf_data.get('total_pages', 0),
                'total_questions': len(pdf_data.get('questions_found', [])),
                'is_processed': True,
                'processing_notes': 'Importado automáticamente desde análisis PDF'
            }
        )
        if created:
            self.stdout.write(f"✅ Cuadernillo creado: {cuadernillo.name}")
        return cuadernillo

    def should_import_question(self, question_data):
        """Determina si una pregunta debe ser importada"""
        # Filtrar preguntas muy cortas o incompletas
        content = question_data.get('content', '')
        if len(content) < 20:
            return False
        
        # Debe tener un número de pregunta válido
        number = question_data.get('number')
        if not number or number in ['11', '°']:  # Filtrar encabezados
            return False
        
        return True

    def detect_question_topic(self, question_data, topics):
        """Detecta el tema de la pregunta basado en palabras clave"""
        content = question_data.get('content', '').lower()
        detected_topics = question_data.get('topics_detected', [])
        
        # Mapear temas detectados a nuestros temas
        topic_mapping = {
            'álgebra': 'algebra',
            'geometría': 'geometria', 
            'trigonometría': 'trigonometria',
            'estadística': 'estadistica',
            'cálculo': 'calculo'
        }
        
        for detected in detected_topics:
            if detected in topic_mapping:
                return topics[topic_mapping[detected]]
        
        # Detección por palabras clave en el contenido
        if any(word in content for word in ['función', 'ecuación', 'variable']):
            return topics['algebra']
        elif any(word in content for word in ['triángulo', 'círculo', 'área', 'volumen']):
            return topics['geometria']
        elif any(word in content for word in ['seno', 'coseno', 'tangente']):
            return topics['trigonometria']
        elif any(word in content for word in ['gráfica', 'tabla', 'datos', 'promedio']):
            return topics['estadistica']
        elif any(word in content for word in ['derivada', 'integral', 'límite']):
            return topics['calculo']
        
        # Por defecto, álgebra
        return topics['algebra']

    def detect_difficulty(self, question_data):
        """Detecta la dificultad de la pregunta"""
        difficulty_mapping = {
            'básico': 'EASY',
            'intermedio': 'MEDIUM',
            'avanzado': 'HARD'
        }
        
        estimated = question_data.get('estimated_difficulty', 'intermedio')
        return difficulty_mapping.get(estimated, 'MEDIUM')

    def detect_content_type(self, question_data):
        """Detecta el tipo de contenido de la pregunta"""
        content = question_data.get('content', '').lower()
        
        if 'tabla' in content:
            return 'WITH_TABLE'
        elif 'gráfica' in content or 'gráfico' in content:
            return 'WITH_GRAPH'
        elif 'figura' in content or 'diagrama' in content:
            return 'WITH_DIAGRAM'
        elif question_data.get('has_options', False):
            return 'WITH_IMAGE'  # Asumir que las opciones pueden tener imágenes
        
        return 'TEXT_ONLY'

    def create_question(self, question_data, subject, topics, cuadernillo, dry_run=False):
        """Crea una pregunta en la base de datos"""
        if dry_run:
            self.stdout.write(f"[DRY RUN] Crearía pregunta: {question_data.get('number')}")
            return True

        # Detectar tema y configuración
        topic = self.detect_question_topic(question_data, topics)
        difficulty = self.detect_difficulty(question_data)
        content_type = self.detect_content_type(question_data)
        
        # Crear pregunta
        question = Question.objects.create(
            question_text=question_data.get('content', ''),
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            content_type=content_type,
            cuadernillo=cuadernillo,
            question_number=str(question_data.get('number', '')),
            page_number=question_data.get('page'),
            source_type='CUADERNILLO',
            source_reference=f"{cuadernillo.name}, Página {question_data.get('page')}",
            mathematical_notation=any(word in question_data.get('content', '').lower() 
                                    for word in ['²', '√', '∑', 'π', 'x', 'y']),
            geometric_figures='geometría' in question_data.get('topics_detected', []),
            statistical_data='estadística' in question_data.get('topics_detected', []),
            word_problem=len(question_data.get('content', '')) > 100,
            extraction_confidence=0.8,  # Confianza media por análisis automático
            manual_review_required=True,  # Requiere revisión manual
            is_verified=False,
            tags=question_data.get('topics_detected', [])
        )

        # Crear opciones si están disponibles
        if question_data.get('has_options'):
            self.create_sample_options(question, topic)

        return question

    def create_sample_options(self, question, topic):
        """Crea opciones de ejemplo para la pregunta"""
        # Como el PDF no incluye opciones completas, creamos placeholders
        options_data = [
            ('A', 'Opción A (requiere revisión manual)'),
            ('B', 'Opción B (requiere revisión manual)'),
            ('C', 'Opción C (requiere revisión manual)'),
            ('D', 'Opción D (requiere revisión manual)'),
        ]

        for i, (letter, text) in enumerate(options_data):
            QuestionOption.objects.create(
                question=question,
                option_letter=letter,
                option_text=text,
                is_correct=(i == 0),  # Por defecto, la primera es correcta
                explanation=f"Explicación para opción {letter} (requiere completar)",
                extraction_confidence=0.3,  # Baja confianza para opciones placeholder
                order=i
            )

        # Crear explicación placeholder
        QuestionExplanation.objects.create(
            question=question,
            explanation_type='SOLUTION',
            target_role='ALL',
            title='Solución de la pregunta',
            content='Esta explicación requiere ser completada manualmente.',
            difficulty_level=question.difficulty,
            order=0
        ) 