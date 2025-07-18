"""
Comando Django para importar preguntas ICFES reales desde Excel
Dirigido al modelo Question/QuestionOption que ya tiene datos
"""

import pandas as pd
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.questions.models import Question, QuestionOption, Subject, Topic


class Command(BaseCommand):
    help = 'Importa preguntas ICFES reales desde Excel al modelo Question'

    def add_arguments(self, parser):
        parser.add_argument(
            '--excel-file',
            type=str,
            default='Icfes/ICFES.xlsx',
            help='Ruta al archivo Excel con las preguntas ICFES'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Limpiar preguntas existentes antes de importar'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular la importación sin guardar'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        excel_file = options['excel_file']
        
        self.stdout.write(
            self.style.SUCCESS('🎯 Iniciando importación de preguntas ICFES reales...')
        )
        
        # Verificar archivo
        if not os.path.exists(excel_file):
            raise CommandError(f'Archivo no encontrado: {excel_file}')
        
        try:
            # Leer archivo Excel - probar diferentes hojas
            try:
                df = pd.read_excel(excel_file, sheet_name='icfes_dataset_completo')
                self.stdout.write(f"📊 Usando hoja 'icfes_dataset_completo'")
            except:
                try:
                    df = pd.read_excel(excel_file, sheet_name=0)  # Primera hoja
                    self.stdout.write(f"📊 Usando primera hoja del Excel")
                except Exception as e:
                    raise CommandError(f'Error leyendo Excel: {str(e)}')
            
            self.stdout.write(f"📊 Archivo cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
            self.stdout.write(f"📋 Columnas disponibles: {list(df.columns)}")
            
            # Limpiar datos existentes si se solicita
            if options['clear_existing'] and not self.dry_run:
                self.limpiar_preguntas_existentes()
            
            # Crear datos base
            subject, topics = self.crear_datos_base()
            
            # Importar preguntas
            preguntas_importadas = self.importar_preguntas(df, subject, topics)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 Importación completada!\n"
                    f"📊 Preguntas importadas: {preguntas_importadas}\n"
                    f"🔄 Modo: {'DRY RUN' if self.dry_run else 'GUARDADO EN BD'}"
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            raise CommandError(f'Error durante la importación: {str(e)}')

    def limpiar_preguntas_existentes(self):
        """Limpia las preguntas existentes"""
        self.stdout.write("🧹 Limpiando preguntas existentes...")
        QuestionOption.objects.all().delete()
        Question.objects.all().delete()
        self.stdout.write("✅ Preguntas existentes eliminadas")

    def crear_datos_base(self):
        """Crea o recupera Subject y Topics base"""
        if self.dry_run:
            return None, {}
        
        # Crear subject Matemáticas
        subject, created = Subject.objects.get_or_create(
            name='Matemáticas',
            defaults={
                'description': 'Competencias matemáticas ICFES',
                'color': '#FF6B35',
                'is_active': True
            }
        )
        if created:
            self.stdout.write("✅ Subject 'Matemáticas' creado")
        
        # Crear topics
        topics_data = [
            ('Álgebra', 'Álgebra y ecuaciones'),
            ('Geometría', 'Geometría y figuras'),
            ('Trigonometría', 'Trigonometría y funciones'),
            ('Estadística', 'Estadística y probabilidad'),
            ('Cálculo', 'Cálculo y análisis'),
            ('Aritmética', 'Aritmética y operaciones'),
        ]
        
        topics = {}
        for name, description in topics_data:
            topic, created = Topic.objects.get_or_create(
                name=name,
                subject=subject,
                defaults={
                    'description': description,
                    'is_active': True
                }
            )
            topics[name] = topic
            if created:
                self.stdout.write(f"✅ Topic '{name}' creado")
        
        return subject, topics

    def mapear_dificultad(self, nivel_excel):
        """Mapea nivel de dificultad del Excel al modelo"""
        if pd.isna(nivel_excel):
            return 'EASY'
        
        nivel = str(nivel_excel).strip()
        if nivel in ['1', '1.0']:
            return 'EASY'
        elif nivel in ['2', '2.0']:
            return 'MEDIUM'
        elif nivel in ['3', '3.0', '4', '4.0']:
            return 'HARD'
        else:
            return 'MEDIUM'  # Por defecto

    def detectar_topic(self, pregunta_texto):
        """Detecta el topic basado en el contenido de la pregunta"""
        texto_lower = pregunta_texto.lower()
        
        # Palabras clave por topic
        keywords = {
            'Álgebra': ['ecuación', 'algebra', 'variable', 'función', 'x', 'y', 'expresión'],
            'Geometría': ['figura', 'área', 'perímetro', 'círculo', 'triángulo', 'rectangulo', 'cuadrado', 'volumen'],
            'Trigonometría': ['seno', 'coseno', 'tangente', 'ángulo', 'trigonometría'],
            'Estadística': ['promedio', 'media', 'mediana', 'moda', 'datos', 'gráfica', 'tabla', 'probabilidad'],
            'Cálculo': ['derivada', 'integral', 'límite', 'función'],
            'Aritmética': ['suma', 'resta', 'multiplicación', 'división', 'número', 'operación']
        }
        
        # Contar coincidencias por topic
        scores = {}
        for topic, words in keywords.items():
            score = sum(1 for word in words if word in texto_lower)
            scores[topic] = score
        
        # Retornar el topic con mayor score
        best_topic = max(scores, key=scores.get)
        return best_topic if scores[best_topic] > 0 else 'Álgebra'  # Por defecto

    @transaction.atomic
    def importar_preguntas(self, df, subject, topics):
        """Importa las preguntas del DataFrame"""
        self.stdout.write("📝 Importando preguntas...")
        
        preguntas_importadas = 0
        
        for index, row in df.iterrows():
            try:
                if self.dry_run:
                    self.stdout.write(f"[DRY RUN] Procesaría pregunta {index + 1}")
                    preguntas_importadas += 1
                    continue
                
                # Obtener datos básicos
                pregunta_texto = row.get('Pregunta', row.get('pregunta_texto', ''))
                if pd.isna(pregunta_texto) or not pregunta_texto.strip():
                    continue
                
                # Detectar topic
                topic_name = self.detectar_topic(pregunta_texto)
                topic = topics.get(topic_name, topics['Álgebra'])
                
                # Mapear dificultad
                dificultad = self.mapear_dificultad(row.get('Nivel_Dificultad', row.get('nivel_dificultad', 2)))
                
                # Crear pregunta
                question = Question.objects.create(
                    question_text=pregunta_texto,
                    subject=subject,
                    topic=topic,
                    difficulty=dificultad,
                    question_type='MULTIPLE_CHOICE',
                    source_type='ICFES_OFFICIAL',
                    content_type='TEXT_ONLY',
                    is_active=True,
                    is_verified=False,
                    times_asked=0,
                    times_correct=0,
                    average_time_seconds=120.0  # Tiempo promedio estimado
                )
                
                # Crear opciones
                opciones_creadas = self.crear_opciones(question, row)
                
                if opciones_creadas:
                    preguntas_importadas += 1
                    self.stdout.write(f"✅ Pregunta {index + 1} importada con {opciones_creadas} opciones")
                else:
                    question.delete()
                    self.stdout.write(f"⚠️ Pregunta {index + 1} eliminada - sin opciones válidas")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error en pregunta {index + 1}: {str(e)}")
                )
                continue
        
        return preguntas_importadas

    def crear_opciones(self, question, row):
        """Crea las opciones de respuesta para una pregunta"""
        opciones_creadas = 0
        respuesta_correcta = row.get('Respuesta_Correcta', row.get('respuesta_correcta', 'A')).upper()
        
        # Intentar diferentes formatos de columnas para opciones
        opciones_fields = [
            ['Opcion_A', 'Opcion_B', 'Opcion_C', 'Opcion_D'],
            ['opcion_a', 'opcion_b', 'opcion_c', 'opcion_d'],
            ['A', 'B', 'C', 'D'],
            ['Opción A', 'Opción B', 'Opción C', 'Opción D']
        ]
        
        opciones_data = None
        for fields in opciones_fields:
            if all(field in row.index for field in fields):
                opciones_data = {
                    'A': row[fields[0]],
                    'B': row[fields[1]], 
                    'C': row[fields[2]],
                    'D': row[fields[3]]
                }
                break
        
        # Si no se encontraron opciones específicas, crear opciones placeholder mejoradas
        if not opciones_data or all(pd.isna(val) or not str(val).strip() for val in opciones_data.values()):
            opciones_data = {
                'A': 'Primera opción de respuesta',
                'B': 'Segunda opción de respuesta', 
                'C': 'Tercera opción de respuesta',
                'D': 'Cuarta opción de respuesta'
            }
            self.stdout.write(f"⚠️ Usando opciones placeholder para pregunta {question.id}")
        
        # Crear las opciones
        for i, (letra, texto) in enumerate(opciones_data.items()):
            if pd.notna(texto) and str(texto).strip():
                QuestionOption.objects.create(
                    question=question,
                    option_letter=letra,
                    option_text=str(texto).strip(),
                    is_correct=(letra == respuesta_correcta),
                    explanation=f"Explicación para opción {letra}",
                    order=i,
                    is_active=True
                )
                opciones_creadas += 1
        
        return opciones_creadas 