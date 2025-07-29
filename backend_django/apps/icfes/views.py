"""
Vistas para el sistema de Quiz ICFES
Maneja sesiones de quiz, preguntas y respuestas por área temática
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
import uuid
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import asyncio
import logging
from asgiref.sync import async_to_sync

# Importar los modelos correctos que tienen datos
from .models_nuevo import PreguntaICFES, OpcionRespuesta, AreaTematica, RespuestaUsuarioICFES
from .models import UserICFESSession, ICFESExam, ICFESResult

# NUEVO: Importar el motor de recomendaciones
from apps.learning.recommendation_engine import LearningRecommendationEngine
from apps.learning.models import UserPathEnrollment

# 🧠 NUEVO: Importar sistema AI/LLM para explicaciones automáticas
from apps.ai_llm.llm_orchestrator import llm_orchestrator
from apps.ai_llm.analysis_engine import UserAnalysisEngine
from apps.questions.models import UserQuestionResponse

logger = logging.getLogger(__name__)


# 🧠 FUNCIÓN SIMPLIFICADA: Generar explicación inmediata para respuestas incorrectas
def _generate_immediate_explanation_for_wrong_answer(user, pregunta, opcion_seleccionada, opcion_correcta):
    """
    Genera explicación inmediata inteligente cuando el usuario responde incorrectamente
    (Versión simplificada que funciona sin LLM - preparada para futura integración)
    """
    try:
        # Mapear área temática ICFES a área estándar
        area_mapping = {
            'Aritmética y Operaciones Básicas': 'matemáticas',
            'Álgebra y Funciones': 'matemáticas', 
            'Geometría y Trigonometría': 'matemáticas',
            'Estadística y Probabilidad': 'matemáticas',
            'Problemas Aplicados y Análisis': 'matemáticas'
        }
        
        area_icfes = pregunta.area_tematica.nombre if pregunta.area_tematica else 'General'
        area_estandar = area_mapping.get(area_icfes, 'matemáticas')
        
        # Generar explicación inteligente basada en el área y contenido
        explanation_content = f"""
## 🎯 Análisis de tu Respuesta

**Pregunta:** {pregunta.pregunta_texto[:100]}{'...' if len(pregunta.pregunta_texto) > 100 else ''}

**Tu respuesta:** Opción {opcion_seleccionada.letra_opcion} - {opcion_seleccionada.texto_opcion[:80]}{'...' if len(opcion_seleccionada.texto_opcion) > 80 else ''}

**Respuesta correcta:** Opción {pregunta.respuesta_correcta}

### 📚 Área Temática: {area_icfes}

### 💡 Explicación Detallada:
"""
        
        # Explicaciones específicas por área
        if 'Álgebra' in area_icfes:
            explanation_content += """
Este problema requiere aplicar conceptos algebraicos fundamentales. Revisa:
- **Operaciones con variables:** Asegúrate de seguir el orden correcto
- **Simplificación:** Reduce expresiones paso a paso
- **Ecuaciones:** Identifica la incógnita y despeja sistemáticamente
"""
        elif 'Geometría' in area_icfes:
            explanation_content += """
Este es un problema geométrico. Considera:
- **Figuras y propiedades:** Identifica qué tipo de figura estás analizando
- **Fórmulas:** Aplica las fórmulas correctas para área, perímetro o volumen
- **Relaciones espaciales:** Visualiza las relaciones entre los elementos
"""
        elif 'Estadística' in area_icfes:
            explanation_content += """
Este problema involucra análisis estadístico. Revisa:
- **Datos:** Organiza la información sistemáticamente
- **Medidas:** Diferencia entre media, mediana y moda
- **Probabilidad:** Calcula eventos considerando todos los casos posibles
"""
        elif 'Aritmética' in area_icfes:
            explanation_content += """
Este es un problema aritmético fundamental. Considera:
- **Operaciones básicas:** Verifica cálculos paso a paso
- **Orden de operaciones:** Sigue la jerarquía matemática (PEMDAS)
- **Números:** Presta atención a decimales, fracciones y porcentajes
"""
        else:
            explanation_content += """
Este problema requiere análisis matemático cuidadoso. Recuerda:
- **Lectura comprensiva:** Entiende completamente lo que se pregunta
- **Estrategia:** Identifica qué conocimientos matemáticos aplicar
- **Verificación:** Comprueba tu respuesta con el contexto del problema
"""
        
        # Consejos personalizados basados en el nivel del usuario
        user_level = getattr(user, 'level', 1)
        if user_level <= 3:
            explanation_content += """
### 🌟 Consejo para Principiantes:
- Tómate tiempo para leer cada pregunta dos veces
- Dibuja o esquematiza cuando sea posible
- Elimina opciones que claramente no tienen sentido
"""
        else:
            explanation_content += """
### 🚀 Consejo Avanzado:
- Analiza las opciones de respuesta para encontrar pistas
- Usa estimación para verificar si tu respuesta es razonable
- Conecta este problema con otros similares que hayas resuelto
"""
        
        explanation_content += """
### 📈 Plan de Mejora:
1. **Repasa** los conceptos fundamentales de esta área
2. **Practica** problemas similares
3. **Analiza** tus errores para evitar repetirlos

---
*Explicación generada automáticamente - Pronto disponible con IA personalizada*
"""
        
        # Datos de la explicación para almacenamiento
        explanation_data = {
            'content': explanation_content.strip(),
            'model_used': 'fallback_intelligent_v1',
            'confidence': 0.75,  # Confianza moderada para explicaciones de fallback
            'success': True,
            'tokens_used': len(explanation_content) // 4,  # Estimación de tokens
        }
        
        logger.info(f"✅ Explicación de fallback generada para pregunta {pregunta.id}")
        return explanation_data
        
    except Exception as e:
        logger.error(f"❌ Error generando explicación de fallback: {e}")
        # Explicación mínima de emergencia
        return {
            'content': f"""
## ❌ Respuesta Incorrecta

**Respuesta correcta:** Opción {pregunta.respuesta_correcta}

Te recomendamos revisar los conceptos de {area_icfes if 'area_icfes' in locals() else 'matemáticas'} y practicar problemas similares.

*Sistema de explicaciones en desarrollo*
""".strip(),
            'model_used': 'emergency_fallback',
            'confidence': 0.5,
            'success': True,
            'tokens_used': 50
        }


def _get_correct_option_text(pregunta):
    """Obtiene el texto de la opción correcta"""
    try:
        opcion_correcta = OpcionRespuesta.objects.get(
            pregunta=pregunta,
            letra_opcion=pregunta.respuesta_correcta
        )
        return opcion_correcta.texto_opcion[:100] + "..."
    except:
        return "Revisa las opciones disponibles"


def _generate_fallback_explanation(pregunta, opcion_seleccionada, area_icfes):
    """Genera explicación básica cuando falla la IA"""
    return {
        'success': True,
        'explanation': f"""
## 🎯 Análisis de tu Respuesta

**Tu respuesta:** {opcion_seleccionada.letra_opcion}) {opcion_seleccionada.texto_opcion[:100]}...

**Respuesta correcta:** {pregunta.respuesta_correcta}

## 📚 Explicación

Esta pregunta pertenece al área de **{area_icfes}** con dificultad **{pregunta.nivel_dificultad}**.

Para mejorar en este tipo de preguntas:

1. **Revisa los conceptos básicos** del tema
2. **Practica problemas similares** step by step  
3. **Identifica el patrón** de este tipo de ejercicios
4. **Consulta material adicional** si tienes dudas

## 💡 Recomendación

Dedica tiempo extra a repasar **{area_icfes.lower()}** y practica con ejercicios de dificultad **{pregunta.nivel_dificultad.lower()}**.
""",
        'ai_generated': False,
        'confidence': 0.6,
        'model_used': 'fallback'
    }


# 🧠 FUNCIÓN SIMPLIFICADA: Generar diagnóstico final inteligente
def _generate_immediate_final_diagnosis(user, session_responses):
    """
    Genera diagnóstico final personalizado inmediato basado en respuestas correctas/incorrectas
    (Versión simplificada que funciona sin LLM - preparada para futura integración)
    """
    try:
        if not session_responses:
            return "No se encontraron respuestas para generar diagnóstico."
            
        # Analizar patrones de respuestas
        total_questions = len(session_responses)
        correct_count = sum(1 for r in session_responses if r.es_correcta)
        incorrect_count = total_questions - correct_count
        accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Identificar áreas problemáticas y fortalezas
        area_performance = {}
        for response in session_responses:
            if response.pregunta.area_tematica:
                area_name = response.pregunta.area_tematica.nombre
                if area_name not in area_performance:
                    area_performance[area_name] = {'correct': 0, 'total': 0}
                
                area_performance[area_name]['total'] += 1
                if response.es_correcta:
                    area_performance[area_name]['correct'] += 1
        
        # Categorizar áreas
        weak_areas = []
        strong_areas = []
        average_areas = []
        
        for area, stats in area_performance.items():
            area_accuracy = (stats['correct'] / stats['total']) * 100
            if area_accuracy < 50:
                weak_areas.append({'name': area, 'accuracy': area_accuracy, 'correct': stats['correct'], 'total': stats['total']})
            elif area_accuracy >= 80:
                strong_areas.append({'name': area, 'accuracy': area_accuracy, 'correct': stats['correct'], 'total': stats['total']})
            else:
                average_areas.append({'name': area, 'accuracy': area_accuracy, 'correct': stats['correct'], 'total': stats['total']})
        
        # Generar diagnóstico personalizado inteligente
        diagnosis_content = f"""
# 📊 Diagnóstico Personalizado de tu Desempeño

¡Hola **{user.username}**! He analizado tu desempeño en este quiz y aquí tienes tu diagnóstico personalizado:

## 🎯 Resumen General
- **Precisión total:** {accuracy:.1f}%
- **Preguntas respondidas:** {total_questions}
- **Respuestas correctas:** {correct_count}
- **Respuestas incorrectas:** {incorrect_count}

"""
        
        # Evaluación del rendimiento general
        if accuracy >= 90:
            diagnosis_content += """
## 🏆 **¡EXCELENTE RENDIMIENTO!**
Tu desempeño es sobresaliente. Demuestras un dominio sólido de los conceptos matemáticos evaluados.
"""
        elif accuracy >= 75:
            diagnosis_content += """
## 🌟 **¡BUEN RENDIMIENTO!**
Tu desempeño es bueno. Tienes una base sólida, pero hay algunas áreas donde puedes mejorar.
"""
        elif accuracy >= 60:
            diagnosis_content += """
## 📈 **RENDIMIENTO PROMEDIO**
Tu desempeño está en nivel intermedio. Con práctica enfocada puedes mejorar significativamente.
"""
        else:
            diagnosis_content += """
## 💪 **OPORTUNIDAD DE CRECIMIENTO**
Este es un buen punto de partida. Con dedicación y práctica constante puedes mejorar mucho.
"""
        
        # Análisis por áreas - Fortalezas
        if strong_areas:
            diagnosis_content += "\n## 🌟 **TUS FORTALEZAS:**\n"
            for area in strong_areas:
                diagnosis_content += f"- **{area['name']}:** {area['accuracy']:.1f}% ({area['correct']}/{area['total']}) - ¡Excelente dominio!\n"
        
        # Análisis por áreas - Oportunidades de mejora
        if weak_areas:
            diagnosis_content += "\n## 🎯 **ÁREAS DE OPORTUNIDAD:**\n"
            for area in weak_areas:
                diagnosis_content += f"- **{area['name']}:** {area['accuracy']:.1f}% ({area['correct']}/{area['total']}) - Requiere atención\n"
        
        # Áreas promedio
        if average_areas:
            diagnosis_content += "\n## 📊 **ÁREAS INTERMEDIAS:**\n"
            for area in average_areas:
                diagnosis_content += f"- **{area['name']}:** {area['accuracy']:.1f}% ({area['correct']}/{area['total']}) - En desarrollo\n"
        
        # Recomendaciones personalizadas
        diagnosis_content += "\n## 💡 **RECOMENDACIONES PERSONALIZADAS:**\n"
        
        if weak_areas:
            diagnosis_content += f"### 🎯 Prioridad Alta:\n"
            for area in weak_areas[:2]:  # Top 2 áreas más débiles
                diagnosis_content += f"- **Estudia {area['name']}:** Dedica tiempo extra a repasar conceptos fundamentales\n"
        
        diagnosis_content += f"""
### 📚 Plan de Estudio:
1. **Repaso inmediato:** Revisa las preguntas incorrectas con sus explicaciones detalladas
2. **Práctica dirigida:** Enfócate en las áreas identificadas como débiles
3. **Consolidación:** Refuerza tus fortalezas con ejercicios más avanzados

### 🚀 Próximos Pasos:
- Realiza otro quiz en 2-3 días para medir tu progreso
- Practica diariamente 15-20 minutos en las áreas más débiles
- Revisa material teórico de los temas que más se te dificultan
"""
        
        # Motivación personalizada basada en el rendimiento
        if accuracy >= 75:
            diagnosis_content += """
## 🎉 **¡FELICITACIONES!**
Tu desempeño demuestra dedicación y comprensión. ¡Sigue así y alcanzarás la excelencia!
"""
        else:
            diagnosis_content += """
## 💪 **¡NO TE RINDAS!**
Cada error es una oportunidad de aprendizaje. Con práctica constante verás mejoras significativas.
"""
        
        diagnosis_content += """
---
*Diagnóstico generado automáticamente basado en tu rendimiento específico*
*Pronto disponible con análisis de IA más avanzado*
"""
        
        logger.info(f"✅ Diagnóstico de fallback generado para usuario {user.username}")
        return diagnosis_content.strip()
        
    except Exception as e:
        logger.error(f"❌ Error generando diagnóstico de fallback: {e}")
        return f"""
# 📊 Diagnóstico de tu Desempeño

¡Hola **{user.username if user else 'Estudiante'}**!

Has completado el quiz. Te recomendamos:

1. **Revisar** las preguntas incorrectas
2. **Practicar** más ejercicios similares  
3. **Estudiar** los conceptos fundamentales

¡Sigue practicando para mejorar tu rendimiento!

---
*Sistema de diagnóstico en desarrollo*
"""


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz_session(request):
    """
    Iniciar una nueva sesión de quiz por área temática usando datos ICFES reales
    """
    try:
        area = request.data.get('area', 'matematicas')
        difficulty = request.data.get('difficulty', 'EASY')
        question_count = request.data.get('question_count', 5)
        
        # Mapear área del frontend a áreas temáticas ICFES
        area_mapping = {
            'algebra-basica': 'Aritmética y Operaciones Básicas',
            'geometria': 'Geometría y Trigonometría',
            'trigonometria': 'Geometría y Trigonometría',
            'estadistica': 'Estadística y Probabilidad',
            'aritmetica': 'Aritmética y Operaciones Básicas',
            'algebra-funciones': 'Álgebra y Funciones',
            'problemas-aplicados': 'Problemas Aplicados y Análisis',
            'matematicas': None  # Todas las áreas
        }
        
        area_tematica_name = area_mapping.get(area)
        
        # Obtener preguntas ICFES según el área
        if area_tematica_name:
            try:
                area_tematica = AreaTematica.objects.get(nombre=area_tematica_name)
                preguntas_disponibles = PreguntaICFES.objects.filter(
                    area_tematica=area_tematica,
                    activa=True
                )
            except AreaTematica.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'Área temática {area_tematica_name} no encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Si es 'matematicas', usar todas las preguntas disponibles
            preguntas_disponibles = PreguntaICFES.objects.filter(activa=True)
            area_tematica_name = 'TODAS LAS ÁREAS'
            
        if preguntas_disponibles.count() == 0:
            return Response({
                'success': False,
                'message': f'No hay preguntas disponibles para {area_tematica_name}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Seleccionar preguntas aleatorias
        preguntas_count = min(question_count, preguntas_disponibles.count())
        preguntas_ids = list(preguntas_disponibles.values_list('id', flat=True))
        preguntas_seleccionadas = random.sample(preguntas_ids, preguntas_count)
        
        # Crear o obtener examen ICFES por defecto
        icfes_exam, _ = ICFESExam.objects.get_or_create(
            name=f'Quiz {area_tematica_name}',
            defaults={
                'exam_type': 'PRACTICE',
                'period': '2024-1',
                'duration_minutes': 30,
                'total_questions': preguntas_count,
                'is_active': True
            }
        )
        
        # Cerrar sesiones anteriores activas del usuario
        UserICFESSession.objects.filter(
            user=request.user,
            status__in=['PENDING', 'IN_PROGRESS']
        ).update(status='ABANDONED')
        
        # Crear sesión de usuario
        with transaction.atomic():
            session = UserICFESSession.objects.create(
                user=request.user,
                icfes_exam=icfes_exam,
                session_type='BY_AREA',
                status='IN_PROGRESS',
                areas_filter=[area_tematica_name],
                total_questions=preguntas_count,
                custom_time_limit=30,
                started_at=timezone.now()
            )
            
            # Guardar preguntas en el orden aleatorio en la sesión
            session.areas_filter = {
                'area': area_tematica_name,
                'preguntas_ids': preguntas_seleccionadas,
                'current_index': 0
            }
            session.save()
        
        # Obtener primera pregunta
        primera_pregunta = PreguntaICFES.objects.get(id=preguntas_seleccionadas[0])
        
        # Serializar pregunta con opciones
        opciones = OpcionRespuesta.objects.filter(pregunta=primera_pregunta).order_by('letra_opcion')
        opciones_dict = {}
        for opt in opciones:
            opciones_dict[opt.letra_opcion] = {
                'text': opt.texto_opcion,
                'image_url': opt.imagen_opcion_url if opt.imagen_opcion_url else None
            }
        
        question_data = {
            'id': str(primera_pregunta.id),
            'title': f"Pregunta {primera_pregunta.id}",
            'content': primera_pregunta.pregunta_texto,
            'image_url': primera_pregunta.imagen_pregunta_url,
            'options': opciones_dict,
            'area': 'Matemáticas',
            'topic': primera_pregunta.area_tematica.nombre if primera_pregunta.area_tematica else 'General',
            'subtopic': primera_pregunta.area_tematica.nombre if primera_pregunta.area_tematica else 'General',
            'difficulty': primera_pregunta.nivel_dificultad,
            'points_value': 2,
            'requires_image': bool(primera_pregunta.imagen_pregunta_url),
        }
        
        return Response({
            'success': True,
            'data': {
                'session_id': str(session.uuid),
                'area': area_tematica_name,
                'total_questions': preguntas_count,
                'current_question': question_data,
                'progress': {
                    'answered': 1,
                    'total': preguntas_count,
                    'percentage': (1 / preguntas_count) * 100
                }
            }
        })
        
    except Exception as e:
        print(f"Error en start_quiz_session: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_question(request, session_id):
    """
    Obtener la pregunta actual de una sesión
    """
    try:
        session = UserICFESSession.objects.get(
            uuid=session_id,
            user=request.user,
            status='IN_PROGRESS'
        )
        
        # Obtener datos de la sesión
        session_data = session.areas_filter
        preguntas_ids = session_data.get('preguntas_ids', [])
        current_index = session_data.get('current_index', 0)
        
        # Verificar si la sesión está completa
        if current_index >= len(preguntas_ids):
            session.status = 'COMPLETED'
            session.completed_at = timezone.now()
            session.save()
            
            return Response({
                'success': True,
                'data': {
                    'session_complete': True,
                    'message': 'Quiz completado'
                }
            })
        
        # Obtener pregunta actual
        pregunta_id = preguntas_ids[current_index]
        pregunta = PreguntaICFES.objects.get(id=pregunta_id)
        
        # Obtener opciones
        opciones = OpcionRespuesta.objects.filter(pregunta=pregunta).order_by('letra_opcion')
        opciones_dict = {}
        for opt in opciones:
            opciones_dict[opt.letra_opcion] = {
                'text': opt.texto_opcion,
                'image_url': opt.imagen_opcion_url if opt.imagen_opcion_url else None
            }
        
        question_data = {
            'id': str(pregunta.id),
            'title': f"Pregunta {pregunta.id}",
            'content': pregunta.pregunta_texto,
            'image_url': pregunta.imagen_pregunta_url,
            'options': opciones_dict,
            'area': 'Matemáticas',
            'topic': pregunta.area_tematica.nombre if pregunta.area_tematica else 'General',
            'subtopic': pregunta.area_tematica.nombre if pregunta.area_tematica else 'General',
            'difficulty': pregunta.nivel_dificultad,
            'points_value': 2,
            'requires_image': bool(pregunta.imagen_pregunta_url),
        }
        
        return Response({
            'success': True,
            'data': {
                'question': question_data,
                'progress': {
                    'answered': current_index + 1,
                    'total': len(preguntas_ids),
                    'percentage': ((current_index + 1) / len(preguntas_ids)) * 100
                }
            }
        })
        
    except UserICFESSession.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Sesión no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error en get_current_question: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_icfes_answer(request, session_id):
    """
    Enviar respuesta a una pregunta del quiz ICFES
    ACTUALIZADO: Ahora calcula XP basada en respuestas correctas y dificultad
    """
    try:
        # Obtener datos del request
        question_id = request.data.get('question_id')
        selected_answer = request.data.get('selected_answer')
        
        if not question_id or not selected_answer:
            return Response({
                'success': False,
                'message': 'question_id y selected_answer son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"🔍 SUBMIT_ICFES_ANSWER: Session {session_id}, Question {question_id}, Answer {selected_answer}")
        
        # Obtener la sesión
        try:
            session = UserICFESSession.objects.get(
                uuid=session_id,
                user=request.user
            )
            print(f"✅ Sesión encontrada: {session.uuid}")
        except UserICFESSession.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Sesión no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener la pregunta ICFES
        try:
            pregunta = PreguntaICFES.objects.get(id=question_id)
            print(f"✅ Pregunta encontrada: {pregunta.pregunta_texto[:50]}...")
        except PreguntaICFES.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Pregunta no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener la opción seleccionada
        try:
            opcion = OpcionRespuesta.objects.get(
                pregunta=pregunta,
                letra_opcion=selected_answer
            )
            print(f"✅ Opción encontrada: {opcion.letra_opcion} - {opcion.texto_opcion[:30]}...")
        except OpcionRespuesta.DoesNotExist:
            return Response({
                'success': False,
                'message': f'Opción {selected_answer} no existe para la pregunta {question_id}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si la respuesta es correcta
        is_correct = opcion.es_correcta
        print(f"✅ Respuesta correcta: {pregunta.respuesta_correcta}, Usuario respondió: {selected_answer}, Es correcta: {is_correct}")
        
        # 🧠 NUEVO: Generar explicación IA automática para respuestas incorrectas
        ai_explanation = None
        ai_explanation_data = None
        
        if not is_correct:
            print(f"🧠 Respuesta incorrecta detectada, generando explicación IA...")
            try:
                # Generar explicación inmediata (ya no async)
                ai_explanation_data = _generate_immediate_explanation_for_wrong_answer(
                    user=request.user,
                    pregunta=pregunta,
                    opcion_seleccionada=opcion,
                    opcion_correcta=None  # Se maneja internamente
                )
                
                if ai_explanation_data and ai_explanation_data.get('success'):
                    ai_explanation = ai_explanation_data.get('content', '')
                    print(f"✅ Explicación IA generada: {len(ai_explanation)} caracteres")
                else:
                    print(f"⚠️ Falló generación de IA, usando fallback")
                    
            except Exception as e:
                logger.error(f"❌ Error generando explicación IA: {str(e)}")
                print(f"❌ Error en explicación IA: {str(e)}")
        
        # 🆕 CALCULAR XP BASADA EN RESPUESTA CORRECTA Y DIFICULTAD
        xp_earned = 0
        points_earned = 0
        
        if is_correct:
            # Mapear dificultad ICFES a XP
            difficulty_xp_map = {
                'Fácil': 5,
                'Medio': 10,
                'Difícil': 15,
                'EASY': 5,
                'MEDIUM': 10,
                'HARD': 15,
            }
            
            # Obtener XP base según dificultad
            base_xp = difficulty_xp_map.get(pregunta.nivel_dificultad, 10)  # 10 por defecto
            
            # Bonificación adicional por área temática especial
            area_bonus = 0
            if pregunta.area_tematica and 'Álgebra' in pregunta.area_tematica.nombre:
                area_bonus = 2  # Bonificación para álgebra
            elif pregunta.area_tematica and 'Geometría' in pregunta.area_tematica.nombre:
                area_bonus = 3  # Bonificación para geometría
            
            xp_earned = base_xp + area_bonus
            points_earned = xp_earned * 2  # Puntos son el doble de XP
            
            print(f"💎 XP Ganada: {xp_earned} (Base: {base_xp}, Bonus: {area_bonus})")
        else:
            print(f"❌ Respuesta incorrecta, no se otorga XP")
        
        # Crear o actualizar UserQuestionResponse para trackear XP
        from apps.questions.models import UserQuestionResponse, Question, QuestionOption
        
        # Intentar crear/obtener una pregunta genérica para trackear la respuesta
        # (Esto es para mantener compatibilidad con el sistema de XP existente)
        try:
            # Crear entrada temporal en UserQuestionResponse para tracking de XP
            # Nota: Esto asume que tenemos Questions en el nuevo sistema, sino usamos el ID de ICFES
            temp_response_record = {
                'user_id': request.user.id,
                'question_id': int(question_id),  # Usar ID de pregunta ICFES
                'is_correct': is_correct,
                'response_time_seconds': 60.0,  # Valor temporal
                'session_id': str(session_id),
                'quiz_type': 'icfes_practice',
                'xp_gained': xp_earned,
            }
            print(f"📊 Response record: {temp_response_record}")
        except Exception as e:
            print(f"⚠️ Error creando response record: {str(e)}")
        
        # Verificar si ya existe una respuesta para esta pregunta en esta sesión
        existing_response = RespuestaUsuarioICFES.objects.filter(
            user=request.user,
            pregunta=pregunta,
            session_id=str(session_id)
        ).first()
        
        if existing_response:
            # Actualizar respuesta existente
            existing_response.opcion_seleccionada = opcion.letra_opcion
            existing_response.es_correcta = is_correct
            # 🧠 NUEVO: Agregar explicación IA si se generó
            if ai_explanation:
                existing_response.ai_explanation_requested = True
                existing_response.ai_explanation_provided = ai_explanation
                # Agregar metadatos de IA
                if ai_explanation_data:
                    existing_response.ai_model_used = ai_explanation_data.get('model_used', 'unknown')
                    existing_response.ai_confidence_score = ai_explanation_data.get('confidence', 0.8)
            existing_response.save()
            print(f"🔄 Respuesta actualizada para pregunta {question_id}")
        else:
            # Crear nueva respuesta
            respuesta_data = {
                'user': request.user,
                'pregunta': pregunta,
                'opcion_seleccionada': opcion.letra_opcion,
                'es_correcta': is_correct,
                'tiempo_respuesta_segundos': 60,  # Valor fijo por ahora
                'session_id': str(session_id),
                'tipo_evaluacion': 'PRACTICA',
            }
            
            # 🧠 NUEVO: Agregar campos de IA si se generó explicación
            if ai_explanation:
                respuesta_data['ai_explanation_requested'] = True
                respuesta_data['ai_explanation_provided'] = ai_explanation
                # Agregar metadatos de IA
                if ai_explanation_data:
                    respuesta_data['ai_model_used'] = ai_explanation_data.get('model_used', 'unknown')
                    respuesta_data['ai_confidence_score'] = ai_explanation_data.get('confidence', 0.8)
            
            respuesta = RespuestaUsuarioICFES.objects.create(**respuesta_data)
            print(f"✨ Nueva respuesta creada para pregunta {question_id}")
            if ai_explanation:
                print(f"🧠 Explicación IA guardada en base de datos")
                print(f"🤖 Modelo usado: {ai_explanation_data.get('model_used', 'unknown')}")
                print(f"📊 Confianza: {ai_explanation_data.get('confidence', 0.8)}")
        
        # 🆕 ACTUALIZAR XP DEL USUARIO SI GANÓ XP
        total_user_xp = request.user.experience_points
        if xp_earned > 0:
            # El XP se actualizará desde el frontend llamando a update_user_xp
            # Aquí solo calculamos cuál sería el total después de la actualización
            total_user_xp = request.user.experience_points + xp_earned
            print(f"🔥 XP será actualizada: {request.user.experience_points} -> {total_user_xp}")
        
        # Actualizar progreso de la sesión y avanzar al siguiente índice
        session_data = session.areas_filter or {}
        preguntas_ids = session_data.get('preguntas_ids', [])
        current_index = session_data.get('current_index', 0)
        total_questions_in_session = len(preguntas_ids) if preguntas_ids else session.total_questions
        
        # Avanzar al siguiente índice
        next_index = current_index + 1
        
        # Actualizar el índice en la sesión
        session_data['current_index'] = next_index
        session.areas_filter = session_data
        
        # Verificar si completó todas las preguntas
        is_completed = next_index >= total_questions_in_session
        if is_completed:
            session.status = 'COMPLETED'
            session.completed_at = timezone.now()
            print(f"🏆 Sesión completada!")
            
            # 🆕 NUEVA FUNCIONALIDAD: Generar plan de aprendizaje automáticamente
            try:
                learning_path_generated = _generate_learning_path_from_quiz(session, request.user)
                print(f"📚 Plan de aprendizaje generado: {learning_path_generated}")
            except Exception as e:
                print(f"⚠️ Error generando plan de aprendizaje: {str(e)}")
                # No fallar el quiz si hay error generando el plan
        
        session.save()
        print(f"📊 Progreso actualizado: {next_index}/{total_questions_in_session}")
        
        # 🆕 RESPUESTA CON XP Y PUNTUACIÓN
        response_data = {
            'is_correct': is_correct,
            'correct_answer': pregunta.respuesta_correcta,
            'explanation': f"{'¡Correcto!' if is_correct else 'Incorrecto.'} {f'Ganaste {xp_earned} XP.' if xp_earned > 0 else 'No se otorga XP por respuestas incorrectas.'}",
            'points_earned': points_earned,
            'xp_earned': xp_earned,  # ✨ NUEVO: XP ganada en esta pregunta
            'total_score': points_earned,  # Para compatibilidad
            'total_xp': total_user_xp,  # ✨ NUEVO: Total XP proyectada del usuario
            'progress': {
                'current': next_index,
                'total': total_questions_in_session,
                'percentage': (next_index / total_questions_in_session) * 100 if total_questions_in_session else 0
            },
            'session_complete': is_completed,
        }
        
        # Si se completó la sesión, agregar información del plan generado
        if is_completed:
            response_data['learning_path_generated'] = True
            response_data['redirect_to_learning_path'] = True
            
            # Calcular estadísticas finales
            total_correct = RespuestaUsuarioICFES.objects.filter(
                user=request.user,
                session_id=str(session_id),
                es_correcta=True
            ).count()
            
            total_answered = RespuestaUsuarioICFES.objects.filter(
                user=request.user,
                session_id=str(session_id)
            ).count()
            
            final_accuracy = (total_correct / total_answered * 100) if total_answered > 0 else 0
            
            response_data['final_results'] = {
                'total_questions': total_answered,
                'correct_answers': total_correct,
                'accuracy': round(final_accuracy, 1),
                'total_xp_earned': 'Calculada por el frontend',  # El frontend suma toda la XP de la sesión
            }
        
        print(f"📤 Enviando respuesta con XP: {response_data}")
        
        return Response({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        print(f"❌ Error en submit_icfes_answer: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _generate_learning_path_from_quiz(session, user):
    """
    Función interna para generar el plan de aprendizaje basado en los resultados del quiz
    MEJORADA: Más robusta contra errores y mejor manejo de duplicados
    """
    try:
        print(f"🧠 Iniciando generación de plan para usuario {user.username}")
        
        # 1. Verificar si el usuario ya tiene un plan activo
        existing_enrollment = UserPathEnrollment.objects.filter(
            user=user,
            status='ACTIVE'
        ).first()
        
        if existing_enrollment:
            print(f"✅ Usuario ya tiene un plan activo: {existing_enrollment.learning_path.name}")
            return True
        
        # 2. Calcular estadísticas del quiz
        respuestas_usuario = RespuestaUsuarioICFES.objects.filter(
            user=user,
            session_id=str(session.uuid)
        ).select_related('pregunta', 'pregunta__area_tematica')
        
        total_questions = respuestas_usuario.count()
        if total_questions == 0:
            print("⚠️ No se encontraron respuestas para esta sesión")
            return False
        
        correct_answers = respuestas_usuario.filter(es_correcta=True).count()
        accuracy = (correct_answers / total_questions) * 100
        
        print(f"📊 Estadísticas: {correct_answers}/{total_questions} ({accuracy:.1f}%)")
        
        # 3. Crear o actualizar ICFESResult
        try:
            result, created = ICFESResult.objects.get_or_create(
                user=user,
                session=session,
                defaults={
                    'icfes_exam': session.icfes_exam,
                    'total_questions': total_questions,
                    'correct_answers': correct_answers,
                    'incorrect_answers': total_questions - correct_answers,
                    'total_time_seconds': 60 * total_questions,  # Estimado
                    'mathematics_score': min(int(accuracy), 100),  # Por ahora solo matemáticas
                    'global_score': min(int(accuracy * 5), 500),  # Escala a 500
                }
            )
            
            if not created:
                # Actualizar resultado existente
                result.total_questions = total_questions
                result.correct_answers = correct_answers
                result.incorrect_answers = total_questions - correct_answers
                result.mathematics_score = min(int(accuracy), 100)
                result.global_score = min(int(accuracy * 5), 500)
                result.save()
            
            print(f"✅ ICFESResult {'creado' if created else 'actualizado'}: {result.mathematics_score}/100")
            
        except Exception as e:
            print(f"❌ Error creando ICFESResult: {str(e)}")
            return False
        
        # 4. Analizar áreas débiles
        try:
            respuestas_incorrectas = respuestas_usuario.filter(es_correcta=False)
            weak_areas = []
            
            for respuesta in respuestas_incorrectas:
                if respuesta.pregunta.area_tematica:
                    area_name = respuesta.pregunta.area_tematica.nombre
                    if area_name not in weak_areas:
                        weak_areas.append(area_name)
            
            # Mapear áreas ICFES a áreas estándar
            area_mapping = {
                'Aritmética y Operaciones Básicas': 'Álgebra Básica',
                'Álgebra y Funciones': 'Funciones y Álgebra',
                'Geometría y Trigonometría': 'Geometría',
                'Estadística y Probabilidad': 'Estadística',
                'Problemas Aplicados y Análisis': 'Problemas Aplicados'
            }
            
            mapped_weak_areas = []
            for area in weak_areas:
                mapped_area = area_mapping.get(area, area)
                if mapped_area not in mapped_weak_areas:
                    mapped_weak_areas.append(mapped_area)
            
            print(f"🎯 Áreas débiles identificadas: {mapped_weak_areas}")
            
        except Exception as e:
            print(f"⚠️ Error analizando áreas débiles: {str(e)}")
            mapped_weak_areas = ['Álgebra Básica']  # Fallback
        
        # 5. Generar plan usando el motor de recomendaciones
        try:
            from apps.learning.recommendation_engine import LearningRecommendationEngine
            engine = LearningRecommendationEngine()
            
            # Análisis básico para el motor
            analysis = {
                'global_score': result.mathematics_score,
                'selected_template': engine._select_template_by_score(result.mathematics_score),
                'critical_areas': mapped_weak_areas,
                'weak_areas': mapped_weak_areas,
                'area_analysis': {
                    'mathematics': {
                        'score': result.mathematics_score,
                        'weak_topics': [{'topic': area, 'score': 50} for area in mapped_weak_areas]
                    }
                },
                'recommendations': []
            }
            
            # Generar plan personalizado
            learning_path = engine.generate_personalized_path(user, analysis)
            
            print(f"🎓 Plan generado exitosamente: {learning_path.name}")
            print(f"📚 Unidades creadas: {learning_path.units.count()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generando plan con motor de recomendaciones: {str(e)}")
            print("🔄 Intentando crear plan básico de fallback...")
            
            # Fallback: crear plan básico sin el motor
            try:
                return _create_basic_fallback_plan(user, result.mathematics_score, mapped_weak_areas)
            except Exception as fallback_error:
                print(f"❌ Error en plan de fallback: {str(fallback_error)}")
                return False
        
    except Exception as e:
        print(f"❌ Error general en _generate_learning_path_from_quiz: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


def _create_basic_fallback_plan(user, score, weak_areas):
    """
    Crear un plan básico de fallback si falla el motor de recomendaciones
    """
    try:
        from apps.learning.models import LearningPath, UserPathEnrollment
        
        # Determinar nivel basado en score
        if score <= 45:
            plan_name = f"Plan Básico de Matemáticas - {user.username}"
            description = "Plan básico para fortalecer fundamentos matemáticos"
        elif score <= 70:
            plan_name = f"Plan Intermedio de Matemáticas - {user.username}"
            description = "Plan intermedio para mejorar habilidades matemáticas"
        else:
            plan_name = f"Plan Avanzado de Matemáticas - {user.username}"
            description = "Plan avanzado para dominar matemáticas"
        
        # Crear learning path básico
        learning_path = LearningPath.objects.create(
            name=plan_name,
            description=description,
            path_type='PERSONALIZED',
            difficulty_level='BASICO' if score <= 45 else 'MEDIO' if score <= 70 else 'AVANZADO',
            estimated_duration_hours=40 if score <= 45 else 35 if score <= 70 else 30,
            recommended_weekly_hours=6 if score <= 45 else 5 if score <= 70 else 4,
            target_icfes_areas=weak_areas,
            created_by=user
        )
        
        # Crear inscripción
        UserPathEnrollment.objects.create(
            user=user,
            learning_path=learning_path,
            status='ACTIVE',
            daily_goal_minutes=60
        )
        
        print(f"✅ Plan básico de fallback creado: {plan_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error en plan de fallback: {str(e)}")
        return False


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_feedback(request, session_id):
    """
    Obtener feedback del quiz completado
    """
    try:
        # Obtener la sesión
        session = UserICFESSession.objects.get(
            uuid=session_id,
            user=request.user
        )
        
        # Obtener preguntas de la sesión
        session_data = session.areas_filter or {}
        preguntas_ids = session_data.get('preguntas_ids', [])
        
        if not preguntas_ids:
            return Response({
                'success': False,
                'message': 'No se encontraron preguntas en la sesión'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener respuestas del usuario para esta sesión
        respuestas_usuario = RespuestaUsuarioICFES.objects.filter(
            user=request.user,
            session_id=str(session_id)  # Asegurar que es string
        ).select_related('pregunta', 'pregunta__area_tematica')
        
        # Calcular estadísticas
        total_questions = len(preguntas_ids)
        answered_questions = respuestas_usuario.count()
        correct_answers = respuestas_usuario.filter(es_correcta=True).count()
        
        # 🎯 NUEVO: Crear detalle de respuestas
        respuestas_detalle = []
        total_xp_ganado = 0
        
        for respuesta in respuestas_usuario:
            pregunta = respuesta.pregunta
            
            # Obtener opciones de la pregunta
            opciones = OpcionRespuesta.objects.filter(pregunta=pregunta).order_by('letra_opcion')
            opciones_dict = {}
            for opt in opciones:
                opciones_dict[opt.letra_opcion] = opt.texto_opcion
            
            respuesta_detalle = {
                'pregunta_id': pregunta.id,
                'pregunta_texto': pregunta.pregunta_texto,
                'pregunta_imagen': pregunta.imagen_pregunta_url,
                'area_tematica': pregunta.area_tematica.nombre if pregunta.area_tematica else 'General',
                'opciones': opciones_dict,
                'respuesta_usuario': respuesta.opcion_seleccionada,
                'respuesta_correcta': pregunta.respuesta_correcta,
                'es_correcta': respuesta.es_correcta,
                'tiempo_respuesta': respuesta.tiempo_respuesta_segundos,
                'xp_ganado': respuesta.xp_ganado,
                'dificultad': pregunta.nivel_dificultad,
                # 🧠 NUEVO: Agregar explicación IA si está disponible
                'ai_explanation': {
                    'available': respuesta.ai_explanation_requested,
                    'content': respuesta.ai_explanation_provided if respuesta.ai_explanation_provided else None,
                    'model_used': respuesta.ai_model_used if hasattr(respuesta, 'ai_model_used') else None,
                    'confidence': respuesta.ai_confidence_score if hasattr(respuesta, 'ai_confidence_score') else 0.0,
                    'generated': respuesta.ai_explanation_requested and respuesta.ai_explanation_provided
                } if hasattr(respuesta, 'ai_explanation_requested') else {
                    'available': False,
                    'content': None,
                    'model_used': None,
                    'confidence': 0.0,
                    'generated': False
                }
            }
            respuestas_detalle.append(respuesta_detalle)
            total_xp_ganado += respuesta.xp_ganado
        
        # Evitar división por cero
        if answered_questions > 0:
            accuracy = (correct_answers / answered_questions) * 100
        else:
            accuracy = 0
        
        # Determinar nivel de desempeño
        if accuracy >= 80:
            performance_level = 'Excelente'
            performance_message = '¡Felicitaciones! Tienes un dominio excelente del tema.'
        elif accuracy >= 60:
            performance_level = 'Bueno'
            performance_message = 'Buen trabajo. Continúa practicando para mejorar.'
        elif accuracy >= 40:
            performance_level = 'Regular'
            performance_message = 'Necesitas más práctica en este tema.'
        else:
            performance_level = 'Necesita Mejora'
            performance_message = 'Te recomendamos repasar los conceptos básicos.'
        
        # Generar recomendaciones
        recommendations = []
        if accuracy < 50:
            recommendations.extend([
                'Repasa los conceptos fundamentales del tema',
                'Practica con ejercicios básicos antes de avanzar'
            ])
        elif accuracy < 80:
            recommendations.extend([
                'Continúa practicando para consolidar conocimientos',
                'Revisa los errores cometidos para evitar repetirlos'
            ])
        else:
            recommendations.extend([
                '¡Excelente trabajo! Puedes avanzar al siguiente nivel',
                'Intenta problemas más desafiantes'
            ])
        
        recommendations.append('Consulta material adicional si tienes dudas')
        
        # 🧠 NUEVO: Generar diagnóstico personalizado con IA
        ai_diagnosis = None
        try:
            if respuestas_usuario.exists():
                print(f"🧠 Generando diagnóstico final con IA...")
                ai_diagnosis = _generate_immediate_final_diagnosis(request.user, respuestas_usuario)
                print(f"✅ Diagnóstico IA generado: {len(ai_diagnosis) if ai_diagnosis else 0} caracteres")
        except Exception as e:
            logger.error(f"❌ Error generando diagnóstico IA: {str(e)}")
            print(f"❌ Error en diagnóstico IA: {str(e)}")
        
        # 🎯 MEJORADO: Crear respuesta completa con detalle
        response_data = {
            'session_id': str(session.uuid),
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'correct_answers': correct_answers,
            'incorrect_answers': answered_questions - correct_answers,
            'accuracy': round(accuracy, 1),
            'final_score': correct_answers,
            'score_percentage': round(accuracy, 1),
            'performance_level': performance_level,
            'performance_message': performance_message,
            'time_spent': f'{answered_questions * 60} segundos',  # Estimado
            'xp_earned': total_xp_ganado,  # XP real calculado por dificultad
            'recommendations': recommendations,
            'respuestas_detalle': respuestas_detalle,  # ✨ NUEVO: Detalle completo
            'feedback': {
                'message': performance_message,
                'strengths': [
                    f'Respondiste {correct_answers} preguntas correctamente',
                    f'Obtuviste {total_xp_ganado} puntos de experiencia'
                ] if correct_answers > 0 else ['Completaste el quiz'],
                'improvements': [
                    f'Revisa las {answered_questions - correct_answers} preguntas incorrectas'
                ] if accuracy < 80 and (answered_questions - correct_answers) > 0 else []
            }
        }
        
        # 🧠 NUEVO: Agregar diagnóstico IA personalizado si está disponible
        if ai_diagnosis:
            response_data['ai_diagnosis'] = {
                'content': ai_diagnosis,
                'generated_at': timezone.now().isoformat(),
                'personalized': True,
                'confidence': 'high',
                'includes_recommendations': True
            }
            print(f"🎓 Diagnóstico IA agregado al response")
        
        return Response({
            'success': True,
            'data': response_data
        })
        
    except UserICFESSession.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Sesión no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        error_message = f"Error al obtener feedback: {str(e)}"
        print(f"Error en get_quiz_feedback: {error_message}")
        print(traceback.format_exc())
        return Response({
            'success': False,
            'message': error_message
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_areas_stats(request):
    """
    Obtiene estadísticas dinámicas del usuario por áreas ICFES
    TODO empezará en 0 para usuarios nuevos
    """
    try:
        user = request.user
        print(f"🔍 get_user_areas_stats called for user: {user.username}")
        
        # Mapeo de áreas ICFES
        areas_config = {
            'matematicas': {
                'name': 'Matemáticas',
                'description': 'Álgebra, geometría, trigonometría, cálculo y estadística',
                'icon': '🧮',
                'color': '#00D9FF',
                'area_filter': 'MATEMATICAS'
            },
            'ingles': {
                'name': 'Inglés', 
                'description': 'Reading comprehension, grammar, vocabulary and listening',
                'icon': '🗣️',
                'color': '#39FF14',
                'area_filter': 'INGLES'
            },
            'ciencias-naturales': {
                'name': 'Ciencias Naturales',
                'description': 'Física, química, biología y ciencias de la tierra',
                'icon': '🔬',
                'color': '#9333EA',
                'area_filter': 'CIENCIAS_NATURALES'
            },
            'sociales-ciudadanas': {
                'name': 'Sociales y Ciudadanas',
                'description': 'Historia, geografía, política, economía y competencias ciudadanas',
                'icon': '🏛️',
                'color': '#FFA500',
                'area_filter': 'SOCIALES_CIUDADANAS'
            },
            'lectura-critica': {
                'name': 'Lectura Crítica',
                'description': 'Comprensión lectora, análisis textual y competencias comunicativas',
                'icon': '📖',
                'color': '#FFD700',
                'area_filter': 'LECTURA_CRITICA'
            }
        }
        
        areas_stats = []
        
        for area_id, config in areas_config.items():
            print(f"📊 Calculando estadísticas para área: {area_id}")
            
            # Obtener respuestas del usuario en esta área (usando RespuestaUsuarioICFES)
            user_responses = RespuestaUsuarioICFES.objects.filter(user=user)
            
            # Filtrar por área temática si es posible
            # Por ahora contamos todas las respuestas ya que las áreas temáticas en ICFES
            # no están mapeadas directamente a las 5 grandes áreas
            total_questions = user_responses.count()
            correct_answers = user_responses.filter(es_correcta=True).count()
            
            # Calcular estadísticas básicas
            accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            progress = min(accuracy, 100)  # El progreso se basa en la precisión
            
            # Determinar dificultad basada en el rendimiento
            if accuracy >= 80:
                difficulty = 'Avanzado'
            elif accuracy >= 60:
                difficulty = 'Intermedio'
            else:
                difficulty = 'Básico'
            
            # Para usuarios nuevos, todo empieza en 0
            if total_questions == 0:
                difficulty = 'Básico'  # Empezar en básico
            
            # Estimar total de preguntas disponibles por área (esto podría venir de la BD)
            estimated_total_questions = {
                'matematicas': 150,
                'ingles': 120,
                'ciencias-naturales': 140,
                'sociales-ciudadanas': 130,
                'lectura-critica': 110
            }
            
            area_stat = {
                'id': area_id,
                'name': config['name'],
                'description': config['description'],
                'icon': config['icon'],
                'color': config['color'],
                'progress': round(progress, 1),
                'totalQuestions': estimated_total_questions.get(area_id, 100),
                'completedQuestions': total_questions,
                'averageScore': round(accuracy, 1),
                'difficulty': difficulty
            }
            
            areas_stats.append(area_stat)
            print(f"✅ {area_id}: {total_questions} preguntas, {accuracy:.1f}% precisión")
        
        # Calcular estadísticas generales
        all_responses = RespuestaUsuarioICFES.objects.filter(user=user)
        total_all_questions = all_responses.count()
        total_all_correct = all_responses.filter(es_correcta=True).count()
        
        overall_accuracy = (total_all_correct / total_all_questions * 100) if total_all_questions > 0 else 0
        overall_progress = sum(area['progress'] for area in areas_stats) / len(areas_stats) if areas_stats else 0
        
        # Obtener racha actual del usuario (desde UserProfile)
        user_streak = 0
        try:
            user_streak = user.profile.current_streak
        except:
            user_streak = 0
        
        # Estadísticas generales
        general_stats = {
            'overall_progress': round(overall_progress, 1),
            'total_questions_answered': total_all_questions,
            'overall_accuracy': round(overall_accuracy, 1),
            'current_streak': user_streak
        }
        
        print(f"📈 Estadísticas generales: {general_stats}")
        
        return Response({
            'success': True,
            'data': {
                'areas': areas_stats,
                'general_stats': general_stats
            }
        })
        
    except Exception as e:
        print(f"❌ Error en get_user_areas_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Error obteniendo estadísticas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dungeon_stats(request):
    """
    Obtiene estadísticas dinámicas por calabozo específico basado en área temática
    ACTUALIZADO: Solo usa las 5 áreas temáticas que realmente existen en la BD
    """
    try:
        user = request.user
        print(f"🔍 get_dungeon_stats called for user: {user.username}")
        
        # ✅ MAPEO CORREGIDO: Solo las 5 áreas temáticas que existen en la BD
        dungeon_mapping = {
            'algebra-basica': 'Aritmética y Operaciones Básicas',
            'estadistica': 'Estadística y Probabilidad',  
            'geometria': 'Geometría y Trigonometría',
            'algebra-funciones': 'Álgebra y Funciones',
            'problemas-aplicados': 'Problemas Aplicados y Análisis'
            # ❌ REMOVIDO: 'calculo' y 'trigonometria' porque no existen o son duplicados
        }
        
        dungeons_stats = []
        
        for dungeon_id, area_tematica_name in dungeon_mapping.items():
            print(f"📊 Calculando estadísticas para calabozo: {dungeon_id} -> {area_tematica_name}")
            
            try:
                # Buscar el área temática en la BD
                area_tematica = AreaTematica.objects.filter(nombre=area_tematica_name).first()
                
                if area_tematica:
                    print(f"✅ Área temática encontrada: {area_tematica.nombre}")
                    
                    # Obtener todas las preguntas de esta área temática
                    preguntas_area = PreguntaICFES.objects.filter(
                        area_tematica=area_tematica,
                        activa=True
                    )
                    
                    # Obtener respuestas del usuario para preguntas de esta área temática
                    respuestas_usuario = RespuestaUsuarioICFES.objects.filter(
                        user=user,
                        pregunta__area_tematica=area_tematica
                    )
                    
                    total_preguntas_respondidas = respuestas_usuario.count()
                    preguntas_correctas = respuestas_usuario.filter(es_correcta=True).count()
                    
                    # Calcular precisión
                    if total_preguntas_respondidas > 0:
                        accuracy = (preguntas_correctas / total_preguntas_respondidas) * 100
                        progress = min(accuracy, 100)  # El progreso se basa en la precisión
                    else:
                        accuracy = 0
                        progress = 0
                    
                    # Determinar dificultad basada en el rendimiento
                    if accuracy >= 80:
                        difficulty = 'Avanzado'
                    elif accuracy >= 60:
                        difficulty = 'Intermedio'
                    else:
                        difficulty = 'Principiante'
                    
                    # Para usuarios que no han respondido nada, empezar en Principiante
                    if total_preguntas_respondidas == 0:
                        difficulty = 'Principiante'
                    
                    # ✅ INFORMACIÓN ESPECÍFICA DEL CALABOZO (solo 5 calabozos reales)
                    dungeon_info = {
                        'algebra-basica': {
                            'name': 'ARITMÉTICA Y OPERACIONES',
                            'subtitle': 'Calabozo de los Números',
                            'icon': '🔢',
                            'color': 'from-blue-500 to-blue-700',
                            'questions': 5,
                            'duration': '15 min',
                            'description': 'Domina las operaciones básicas y conceptos aritméticos fundamentales',
                            'topics': ['Operaciones básicas', 'Números enteros', 'Fracciones', 'Decimales'],
                            'boss': 'El Guardian de los Números'
                        },
                        'estadistica': {
                            'name': 'ESTADÍSTICA Y PROBABILIDAD',
                            'subtitle': 'Oráculo de los Datos',
                            'icon': '📊',
                            'color': 'from-green-500 to-green-700',
                            'questions': 5,
                            'duration': '18 min',
                            'description': 'Interpreta datos, gráficas y calcula probabilidades',
                            'topics': ['Medidas de tendencia', 'Gráficos', 'Probabilidad', 'Análisis de datos'],
                            'boss': 'El Vidente de las Tendencias'
                        },
                        'geometria': {
                            'name': 'GEOMETRÍA Y TRIGONOMETRÍA',
                            'subtitle': 'Laberinto de las Formas',
                            'icon': '📐',
                            'color': 'from-purple-500 to-purple-700',
                            'questions': 5,
                            'duration': '20 min',
                            'description': 'Explora figuras geométricas y funciones trigonométricas',
                            'topics': ['Figuras planas', 'Volúmenes', 'Trigonometría', 'Teoremas'],
                            'boss': 'El Arquitecto de las Dimensiones'
                        },
                        'algebra-funciones': {
                            'name': 'ÁLGEBRA Y FUNCIONES',
                            'subtitle': 'Torre de las Ecuaciones',
                            'icon': '🧮',
                            'color': 'from-orange-500 to-orange-700',
                            'questions': 7,
                            'duration': '25 min',
                            'description': 'Resuelve ecuaciones y explora el mundo de las funciones',
                            'topics': ['Ecuaciones lineales', 'Sistemas', 'Funciones', 'Polinomios'],
                            'boss': 'El Maestro de las Variables'
                        },
                        'problemas-aplicados': {
                            'name': 'PROBLEMAS APLICADOS',
                            'subtitle': 'Desafíos del Mundo Real',
                            'icon': '🌍',
                            'color': 'from-red-500 to-red-700',
                            'questions': 8,
                            'duration': '30 min',
                            'description': 'Aplica matemáticas a situaciones de la vida real',
                            'topics': ['Modelado', 'Optimización', 'Análisis cuantitativo', 'Interpretación'],
                            'boss': 'El Sabio de las Aplicaciones'
                        }
                    }
                    
                    info = dungeon_info.get(dungeon_id, {
                        'name': area_tematica_name.upper(),
                        'subtitle': 'Calabozo Matemático',
                        'icon': '🎯',
                        'color': 'from-gray-500 to-gray-700',
                        'questions': 5,
                        'duration': '20 min',
                        'description': f'Domina los conceptos de {area_tematica_name}',
                        'topics': ['Conceptos básicos'],
                        'boss': 'El Guardian del Conocimiento'
                    })
                    
                    dungeon_stat = {
                        'id': dungeon_id,
                        'name': info['name'],
                        'subtitle': info['subtitle'],
                        'icon': info['icon'],
                        'difficulty': difficulty,
                        'color': info['color'],
                        'progress': round(progress, 1),
                        'questions': info['questions'],
                        'duration': info['duration'],
                        'description': info['description'],
                        'topics': info['topics'],
                        'boss': info['boss'],
                        # Estadísticas calculadas dinámicamente
                        'total_questions_answered': total_preguntas_respondidas,
                        'correct_answers': preguntas_correctas,
                        'accuracy': round(accuracy, 1),
                        'area_tematica_id': area_tematica.id,
                        'area_tematica_name': area_tematica.nombre
                    }
                    
                    dungeons_stats.append(dungeon_stat)
                    print(f"✅ {dungeon_id}: {total_preguntas_respondidas} preguntas, {accuracy:.1f}% precisión")
                    
                else:
                    print(f"❌ Área temática no encontrada: {area_tematica_name}")
                    # NO AGREGAR calabozos que no existen
                    continue
                    
            except Exception as e:
                print(f"❌ Error procesando calabozo {dungeon_id}: {str(e)}")
                continue
        
        print(f"📈 Total calabozos procesados: {len(dungeons_stats)}")
        
        return Response({
            'success': True,
            'data': {
                'dungeons': dungeons_stats
            }
        })
        
    except Exception as e:
        print(f"❌ Error en get_dungeon_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Error obteniendo estadísticas de calabozos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 