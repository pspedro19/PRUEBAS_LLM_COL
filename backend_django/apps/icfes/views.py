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

# Importar los modelos correctos que tienen datos
from .models_nuevo import PreguntaICFES, OpcionRespuesta, AreaTematica, RespuestaUsuarioICFES
from .models import UserICFESSession, ICFESExam


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
        print(f"✅ Respuesta correcta: {pregunta.respuesta_correcta}")
        
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
            existing_response.save()
            print(f"🔄 Respuesta actualizada para pregunta {question_id}")
        else:
            # Crear nueva respuesta
            respuesta = RespuestaUsuarioICFES.objects.create(
                user=request.user,
                pregunta=pregunta,
                opcion_seleccionada=opcion.letra_opcion,
                es_correcta=is_correct,
                tiempo_respuesta_segundos=60,  # Valor fijo por ahora
                session_id=str(session_id),
                tipo_evaluacion='PRACTICA',
            )
            print(f"✨ Nueva respuesta creada para pregunta {question_id}")
        
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
        
        session.save()
        print(f"📊 Progreso actualizado: {next_index}/{total_questions_in_session}")
        
        return Response({
            'success': True,
            'data': {
                'is_correct': is_correct,
                'correct_answer': pregunta.respuesta_correcta,
                'progress': {
                    'current': next_index,
                    'total': total_questions_in_session,
                    'percentage': (next_index / total_questions_in_session) * 100 if total_questions_in_session else 0
                },
                'session_complete': is_completed,
            }
        })
        
    except Exception as e:
        print(f"❌ Error en submit_icfes_answer: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                'dificultad': pregunta.nivel_dificultad
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