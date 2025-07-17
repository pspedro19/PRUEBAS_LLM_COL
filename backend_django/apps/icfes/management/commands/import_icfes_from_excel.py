"""
Comando Django para importar preguntas ICFES desde el archivo Excel oficial
Utiliza los nuevos modelos basados en la estructura real del Excel
"""

import pandas as pd
import os
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date

from apps.icfes.models import (
    AreaEvaluacion, CompetenciaICFES, ComponenteConocimiento,
    ProcesoCognitivo, TipoConocimiento, ContextoAplicacion,
    AreaTematica, TemaEspecifico, PeriodoAplicacion, CuadernilloICFES,
    PreguntaICFES, OpcionRespuesta, PistaPregunta, ExplicacionRespuesta,
    ErrorComun
)


class Command(BaseCommand):
    help = 'Importa preguntas ICFES desde el archivo Excel oficial'

    def add_arguments(self, parser):
        parser.add_argument(
            '--excel-file',
            type=str,
            default='Icfes/ICFES.xlsx',
            help='Ruta al archivo Excel con las preguntas ICFES'
        )
        parser.add_argument(
            '--sheet-name',
            type=str,
            default='icfes_dataset_completo',
            help='Nombre de la hoja a importar'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular la importación sin guardar en la base de datos'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Limpiar datos existentes antes de importar'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.excel_file = options['excel_file']
        self.sheet_name = options['sheet_name']
        
        self.stdout.write(
            self.style.SUCCESS('🎯 Iniciando importación de preguntas ICFES desde Excel...')
        )
        
        # Verificar archivo
        if not os.path.exists(self.excel_file):
            raise CommandError(f'Archivo no encontrado: {self.excel_file}')
        
        try:
            # Leer archivo Excel
            df = pd.read_excel(self.excel_file, sheet_name=self.sheet_name)
            self.stdout.write(f"📊 Archivo cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            # Limpiar datos existentes si se solicita
            if options['clear_existing'] and not self.dry_run:
                self.limpiar_datos_existentes()
            
            # Crear datos base
            self.crear_datos_base()
            
            # Importar preguntas
            preguntas_importadas = self.importar_preguntas(df)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 Importación completada!\n"
                    f"📊 Preguntas procesadas: {preguntas_importadas}\n"
                    f"🔄 Modo: {'DRY RUN' if self.dry_run else 'GUARDADO EN BD'}"
                )
            )
            
        except Exception as e:
            raise CommandError(f'Error durante la importación: {str(e)}')

    def limpiar_datos_existentes(self):
        """Limpia los datos existentes de ICFES"""
        self.stdout.write("🧹 Limpiando datos existentes...")
        
        # Eliminar en orden inverso por las dependencias
        PreguntaICFES.objects.all().delete()
        CuadernilloICFES.objects.all().delete()
        TemaEspecifico.objects.all().delete()
        AreaTematica.objects.all().delete()
        ComponenteConocimiento.objects.all().delete()
        CompetenciaICFES.objects.all().delete()
        
        self.stdout.write("✅ Datos existentes eliminados")

    def crear_datos_base(self):
        """Crea los datos base del sistema (taxonomía)"""
        self.stdout.write("📚 Creando taxonomía base...")
        
        if self.dry_run:
            self.stdout.write("[DRY RUN] Se crearían los datos base")
            return
        
        # 1. Área de Evaluación
        area_math, _ = AreaEvaluacion.objects.get_or_create(
            codigo='MATEMATICAS',
            defaults={
                'nombre': 'Matemáticas',
                'descripcion': 'Competencias matemáticas para educación media',
                'color_tema': '#FF6B35',
                'orden_visualizacion': 1
            }
        )
        
        # 2. Competencias ICFES
        competencias_data = [
            ('INTERPRETACION_REPRESENTACION', 'Interpretación y representación'),
            ('ARGUMENTACION', 'Argumentación'),
            ('FORMULACION_EJECUCION', 'Formulación y ejecución'),
        ]
        
        for codigo, nombre in competencias_data:
            CompetenciaICFES.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'area_evaluacion': area_math,
                    'nombre': nombre,
                    'descripcion': f'Competencia de {nombre.lower()}'
                }
            )
        
        # 3. Componentes de Conocimiento
        comp_interpretacion = CompetenciaICFES.objects.get(codigo='INTERPRETACION_REPRESENTACION')
        ComponenteConocimiento.objects.get_or_create(
            competencia=comp_interpretacion,
            codigo='CONOCIMIENTOS_GENERICOS',
            defaults={
                'nombre': 'Conocimientos genéricos',
                'descripcion': 'Conocimientos matemáticos generales'
            }
        )
        
        # 4. Procesos Cognitivos
        procesos_data = [
            ('INTERPRETACION', 'Interpretación', 2),
            ('ARGUMENTACION', 'Argumentación', 5),
            ('PROPOSICION', 'Proposición', 4),
        ]
        
        for codigo, nombre, nivel_bloom in procesos_data:
            ProcesoCognitivo.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': f'Proceso cognitivo de {nombre.lower()}',
                    'nivel_bloom': nivel_bloom
                }
            )
        
        # 5. Tipos de Conocimiento
        TipoConocimiento.objects.get_or_create(
            codigo='GENERICO',
            defaults={
                'nombre': 'Genérico',
                'descripcion': 'Conocimientos aplicables en diversos contextos'
            }
        )
        
        # 6. Contextos de Aplicación
        contextos_data = [
            ('COMUNITARIO_SOCIAL', 'Comunitario/social'),
            ('PERSONAL_FAMILIAR', 'Personal/familiar'),
            ('LABORAL_OCUPACIONAL', 'Laboral/ocupacional'),
        ]
        
        for codigo, nombre in contextos_data:
            ContextoAplicacion.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': f'Contexto {nombre.lower()}'
                }
            )
        
        # 7. Áreas Temáticas (Las 5 áreas reales del Excel)
        areas_tematicas_data = [
            ('ARITMETICA_OPERACIONES', 'Aritmética y Operaciones Básicas'),
            ('ESTADISTICA_PROBABILIDAD', 'Estadística y Probabilidad'),
            ('GEOMETRIA_TRIGONOMETRIA', 'Geometría y Trigonometría'),
            ('ALGEBRA_FUNCIONES', 'Álgebra y Funciones'),
            ('PROBLEMAS_APLICADOS', 'Problemas Aplicados y Análisis'),
        ]
        
        for codigo, nombre in areas_tematicas_data:
            AreaTematica.objects.get_or_create(
                area_evaluacion=area_math,
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': f'Área temática de {nombre.lower()}'
                }
            )
        
        # 8. Período de Aplicación
        PeriodoAplicacion.objects.get_or_create(
            codigo='2024-1',
            defaults={
                'nombre': '2024 Período 1',
                'fecha_inicio': parse_date('2024-02-01'),
                'fecha_fin': parse_date('2024-06-30')
            }
        )
        
        # 9. Cuadernillo
        area_math = AreaEvaluacion.objects.get(codigo='MATEMATICAS')
        periodo = PeriodoAplicacion.objects.get(codigo='2024-1')
        
        CuadernilloICFES.objects.get_or_create(
            codigo='MATH_2024_1_OFICIAL',
            defaults={
                'nombre': 'Matemáticas 11° - Dataset Oficial 2024-1',
                'area_evaluacion': area_math,
                'periodo_aplicacion': periodo,
                'tipo_cuadernillo': 'SABER_11',
                'grado_escolar': 11,
                'total_preguntas': 49,
                'procesado': True,
                'notas_procesamiento': 'Importado desde archivo Excel oficial'
            }
        )
        
        self.stdout.write("✅ Taxonomía base creada")

    def mapear_competencia(self, competencia_excel):
        """Mapea la competencia del Excel a nuestro modelo"""
        mapeo = {
            'Interpretación y representación': 'INTERPRETACION_REPRESENTACION',
            'Argumentación': 'ARGUMENTACION',
            'Formulación y ejecución': 'FORMULACION_EJECUCION',
        }
        return mapeo.get(competencia_excel, 'INTERPRETACION_REPRESENTACION')

    def mapear_proceso_cognitivo(self, proceso_excel):
        """Mapea el proceso cognitivo del Excel a nuestro modelo"""
        mapeo = {
            'Interpretación': 'INTERPRETACION',
            'Argumentación': 'ARGUMENTACION',
            'Proposición': 'PROPOSICION',
        }
        return mapeo.get(proceso_excel, 'INTERPRETACION')

    def mapear_contexto(self, contexto_excel):
        """Mapea el contexto del Excel a nuestro modelo"""
        mapeo = {
            'Comunitario/social': 'COMUNITARIO_SOCIAL',
            'Personal/familiar': 'PERSONAL_FAMILIAR',
            'Laboral/ocupacional': 'LABORAL_OCUPACIONAL',
        }
        return mapeo.get(contexto_excel, 'COMUNITARIO_SOCIAL')

    def mapear_area_tematica(self, area_excel):
        """Mapea el área temática del Excel a nuestro modelo"""
        mapeo = {
            'Aritmética y Operaciones Básicas': 'ARITMETICA_OPERACIONES',
            'Estadística y Probabilidad': 'ESTADISTICA_PROBABILIDAD',
            'Geometría y Trigonometría': 'GEOMETRIA_TRIGONOMETRIA',
            'Álgebra y Funciones': 'ALGEBRA_FUNCIONES',
            'Problemas Aplicados y Análisis': 'PROBLEMAS_APLICADOS',
        }
        return mapeo.get(area_excel, 'ARITMETICA_OPERACIONES')

    def mapear_nivel_desempeno(self, nivel_excel):
        """Mapea el nivel de desempeño del Excel a nuestro modelo"""
        mapeo = {
            'Mínimo': 'MINIMO',
            'Satisfactorio': 'SATISFACTORIO',
            'Avanzado': 'AVANZADO',
        }
        return mapeo.get(nivel_excel, 'MINIMO')

    @transaction.atomic
    def importar_preguntas(self, df):
        """Importa las preguntas del DataFrame"""
        self.stdout.write("📝 Importando preguntas...")
        
        preguntas_importadas = 0
        
        # Obtener objetos base para evitar consultas repetidas
        if not self.dry_run:
            area_math = AreaEvaluacion.objects.get(codigo='MATEMATICAS')
            cuadernillo = CuadernilloICFES.objects.get(codigo='MATH_2024_1_OFICIAL')
            tipo_conocimiento = TipoConocimiento.objects.get(codigo='GENERICO')
        
        for index, row in df.iterrows():
            try:
                if self.dry_run:
                    self.stdout.write(f"[DRY RUN] Procesaría pregunta {row['ID_Pregunta']}")
                    preguntas_importadas += 1
                    continue
                
                # Obtener referencias
                competencia = CompetenciaICFES.objects.get(
                    codigo=self.mapear_competencia(row['Competencia'])
                )
                proceso_cognitivo = ProcesoCognitivo.objects.get(
                    codigo=self.mapear_proceso_cognitivo(row['Proceso_Cognitivo'])
                )
                contexto = ContextoAplicacion.objects.get(
                    codigo=self.mapear_contexto(row['Contexto'])
                )
                area_tematica = AreaTematica.objects.get(
                    codigo=self.mapear_area_tematica(row['Area_Tematica'])
                )
                
                # Crear o actualizar pregunta
                pregunta, created = PreguntaICFES.objects.get_or_create(
                    id_pregunta_original=row['ID_Pregunta'],
                    defaults={
                        'cuadernillo': cuadernillo,
                        'numero_pregunta': str(row['ID_Pregunta']),
                        'area_evaluacion': area_math,
                        'competencia': competencia,
                        'proceso_cognitivo': proceso_cognitivo,
                        'tipo_conocimiento': tipo_conocimiento,
                        'contexto_aplicacion': contexto,
                        'pregunta_texto': row['Pregunta'],
                        'afirmacion': row.get('Afirmación', ''),
                        'evidencia': row.get('Evidencia', ''),
                        'nivel_dificultad': int(row['Nivel_Dificultad']),
                        'nivel_desempeno_esperado': self.mapear_nivel_desempeno(row['Nivel_Desempeño_Esperado']),
                        'tiempo_estimado_segundos': int(row['Tiempo_Estimado']),
                        'area_tematica': area_tematica,
                        'grado_escolar': int(row['Grado_Escolar']),
                        'respuesta_correcta': row['Respuesta_Correcta'],
                        'puntos_xp': int(row['Puntos_XP']),
                        'requiere_imagen': bool(row['Requiere_Imagen']),
                        'imagen_pregunta_url': row.get('Imagen_Pregunta_URL', ''),
                        'fecha_aplicacion': pd.to_datetime(row['Periodo_Aplicación']).date() if pd.notna(row['Periodo_Aplicación']) else None,
                        'verificada': False,  # Requiere revisión manual
                        'activa': True
                    }
                )
                
                if created:
                    # Crear opciones
                    self.crear_opciones(pregunta, row)
                    
                    # Crear pistas
                    self.crear_pistas(pregunta, row)
                    
                    # Crear explicación
                    self.crear_explicacion(pregunta, row)
                    
                    # Crear error común
                    self.crear_error_comun(pregunta, row)
                    
                    preguntas_importadas += 1
                    self.stdout.write(f"✅ Pregunta {row['ID_Pregunta']} importada")
                else:
                    self.stdout.write(f"⏭️ Pregunta {row['ID_Pregunta']} ya existe")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error en pregunta {row['ID_Pregunta']}: {str(e)}")
                )
                continue
        
        return preguntas_importadas

    def crear_opciones(self, pregunta, row):
        """Crea las opciones de respuesta"""
        opciones = ['A', 'B', 'C', 'D']
        
        for letra in opciones:
            texto_opcion = row.get(f'Opcion_{letra}', '')
            if pd.notna(texto_opcion) and texto_opcion.strip():
                OpcionRespuesta.objects.create(
                    pregunta=pregunta,
                    letra_opcion=letra,
                    texto_opcion=texto_opcion,
                    es_correcta=(letra == row['Respuesta_Correcta']),
                    imagen_opcion_url=row.get(f'Imagen_Opcion_{letra}_URL', ''),
                    orden=ord(letra) - ord('A')
                )

    def crear_pistas(self, pregunta, row):
        """Crea las pistas de la pregunta"""
        for i in range(1, 4):  # Pistas 1, 2, 3
            pista_texto = row.get(f'Pista_{i}', '')
            if pd.notna(pista_texto) and pista_texto.strip():
                PistaPregunta.objects.create(
                    pregunta=pregunta,
                    numero_pista=i,
                    texto_pista=pista_texto,
                    tipo_pista='CONCEPTUAL',
                    rol_objetivo='ALL',
                    orden=i
                )

    def crear_explicacion(self, pregunta, row):
        """Crea la explicación de la respuesta"""
        explicacion_texto = row.get('Explicación_Respuesta', '')
        if pd.notna(explicacion_texto) and explicacion_texto.strip():
            ExplicacionRespuesta.objects.create(
                pregunta=pregunta,
                tipo_explicacion='SOLUCION',
                titulo='Explicación de la respuesta',
                contenido=explicacion_texto,
                rol_objetivo='ALL',
                nivel_detalle='MEDIO',
                dificultad_explicacion=pregunta.nivel_dificultad,
                orden=1
            )

    def crear_error_comun(self, pregunta, row):
        """Crea el error común"""
        error_texto = row.get('Error_Común', '')
        if pd.notna(error_texto) and error_texto.strip():
            ErrorComun.objects.create(
                pregunta=pregunta,
                descripcion_error=error_texto,
                explicacion_error=f"Error común en pregunta {pregunta.id_pregunta_original}",
                frecuencia_error=25.0  # Valor por defecto
            ) 