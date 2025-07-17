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

from .models import (
    AreaTematica, PreguntaICFES, OpcionRespuesta, 
    RespuestaUsuarioICFES, UserICFESSession, ICFESExam
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz_session(request):
    """
    Iniciar una nueva sesión de quiz por área temática
    """
    try:
        area = request.data.get('area', 'matematicas')
        difficulty = request.data.get('difficulty', 'PRINCIPIANTE')
        question_count = request.data.get('question_count', 5)
        
        # Mapear área del frontend a áreas temáticas disponibles
        area_mapping = {
            'algebra-basica': 'Aritmética y Operaciones Básicas',
            'geometria': 'Geometría y Trigonometría',
            'trigonometria': 'Geometría y Trigonometría',
            'estadistica': 'Estadística y Probabilidad',
            'calculo': 'Álgebra y Funciones',
            'aritmetica': 'Aritmética y Operaciones Básicas',
            'algebra-funciones': 'Álgebra y Funciones',
            'problemas-aplicados': 'Problemas Aplicados y Análisis'
        }
        
        area_name = area_mapping.get(area, 'Álgebra')
        
        # Buscar área temática
        try:
            area_tematica = AreaTematica.objects.get(nombre=area_name)
        except AreaTematica.DoesNotExist:
            # Si no existe esa área específica, usar cualquier área disponible
            area_tematica = AreaTematica.objects.first()
            if not area_tematica:
                return Response({
                    'success': False,
                    'message': 'No hay áreas temáticas disponibles'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener preguntas del área temática (máximo 5 aleatorias)
        preguntas_disponibles = PreguntaICFES.objects.filter(
            area_tematica=area_tematica,
            activa=True
        )
        
        if preguntas_disponibles.count() == 0:
            return Response({
                'success': False,
                'message': f'No hay preguntas disponibles para el área {area_name}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Seleccionar hasta 5 preguntas aleatorias
        preguntas_count = min(question_count, preguntas_disponibles.count())
        preguntas_ids = list(preguntas_disponibles.values_list('id', flat=True))
        preguntas_seleccionadas = random.sample(preguntas_ids, preguntas_count)
        
        # Crear o obtener examen ICFES por defecto
        icfes_exam, _ = ICFESExam.objects.get_or_create(
            name=f'Quiz {area_name}',
            defaults={
                'exam_type': 'PRACTICE',
                'period': '2024-1',
                'duration_minutes': 30,
                'total_questions': preguntas_count,
                'is_active': True
            }
        )
        
        # Crear sesión de usuario
        with transaction.atomic():
            session = UserICFESSession.objects.create(
                user=request.user,
                icfes_exam=icfes_exam,
                session_type='BY_AREA',
                status='IN_PROGRESS',
                areas_filter=[area_name],
                total_questions=preguntas_count,
                custom_time_limit=30,
                started_at=timezone.now()
            )
            
            # Guardar preguntas en el orden aleatorio en la sesión
            # (Usaremos un campo JSON para almacenar el orden)
            session.areas_filter = {
                'area': area_name,
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
            'title': f'Pregunta 1 de {preguntas_count}',
            'content': primera_pregunta.pregunta_texto,
            'image_url': primera_pregunta.imagen_pregunta_url if primera_pregunta.imagen_pregunta_url else None,
            'options': opciones_dict,
            'area': area_name,
            'topic': primera_pregunta.tema_especifico.nombre if primera_pregunta.tema_especifico else area_name,
            'subtopic': '',
            'difficulty': primera_pregunta.nivel_dificultad,
            'points_value': primera_pregunta.puntos_xp,
            'requires_image': primera_pregunta.requiere_imagen
        }
        
        return Response({
            'success': True,
            'data': {
                'session_id': str(session.uuid),
                'area': area_name,
                'difficulty': difficulty,
                'total_questions': preguntas_count,
                'current_question': question_data,
                'progress': {
                    'answered': 0,
                    'total': preguntas_count,
                    'percentage': 0
                },
                'current_score': 0,
                'current_xp': 0
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al iniciar quiz: {str(e)}'
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
            'title': f'Pregunta {current_index + 1} de {len(preguntas_ids)}',
            'content': pregunta.pregunta_texto,
            'image_url': pregunta.imagen_pregunta_url if pregunta.imagen_pregunta_url else None,
            'options': opciones_dict,
            'area': session_data.get('area', ''),
            'topic': pregunta.tema_especifico.nombre if pregunta.tema_especifico else '',
            'difficulty': pregunta.nivel_dificultad,
            'points_value': pregunta.puntos_xp,
            'requires_image': pregunta.requiere_imagen
        }
        
        return Response({
            'success': True,
            'data': {
                'question': question_data,
                'progress': {
                    'answered': current_index,
                    'total': len(preguntas_ids),
                    'percentage': int((current_index / len(preguntas_ids)) * 100)
                },
                'session_complete': False
            }
        })
        
    except UserICFESSession.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Sesión no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener pregunta: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request, session_id):
    """
    Enviar respuesta a una pregunta
    """
    try:
        session = UserICFESSession.objects.get(
            uuid=session_id,
            user=request.user,
            status='IN_PROGRESS'
        )
        
        question_id = request.data.get('question_id')
        selected_answer = request.data.get('selected_answer')
        
        if not question_id or not selected_answer:
            return Response({
                'success': False,
                'message': 'Faltan datos requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener pregunta y opción seleccionada
        pregunta = PreguntaICFES.objects.get(id=question_id)
        opcion_seleccionada = OpcionRespuesta.objects.get(
            pregunta=pregunta,
            letra_opcion=selected_answer
        )
        
        # Obtener la respuesta correcta
        opcion_correcta = OpcionRespuesta.objects.get(
            pregunta=pregunta,
            es_correcta=True
        )
        
        is_correct = opcion_seleccionada.es_correcta
        points_earned = pregunta.puntos_xp if is_correct else 0
        xp_earned = points_earned
        
        # Guardar respuesta del usuario
        with transaction.atomic():
            respuesta = RespuestaUsuarioICFES.objects.create(
                user=request.user,
                pregunta=pregunta,
                opcion_seleccionada=selected_answer,
                es_correcta=is_correct,
                tiempo_respuesta_segundos=30,  # Por defecto
                xp_ganado=xp_earned,
                session_id=str(session.uuid)
            )
            
            # Actualizar progreso de la sesión
            session.answered_questions += 1
            session_data = session.areas_filter
            current_index = session_data.get('current_index', 0)
            session_data['current_index'] = current_index + 1
            session.areas_filter = session_data
            session.save()
        
        # Verificar si es la última pregunta
        preguntas_ids = session_data.get('preguntas_ids', [])
        session_complete = (current_index + 1) >= len(preguntas_ids)
        
        if session_complete:
            session.status = 'COMPLETED'
            session.completed_at = timezone.now()
            session.save()
        
        return Response({
            'success': True,
            'data': {
                'is_correct': is_correct,
                'correct_answer': opcion_correcta.letra_opcion,
                'explanation': opcion_correcta.explicacion_opcion or 'Respuesta correcta',
                'points_earned': points_earned,
                'xp_earned': xp_earned,
                'total_score': session.answered_questions,  # Simplificado
                'total_xp': points_earned,  # Simplificado
                'session_complete': session_complete
            }
        })
        
    except (UserICFESSession.DoesNotExist, PreguntaICFES.DoesNotExist, OpcionRespuesta.DoesNotExist):
        return Response({
            'success': False,
            'message': 'Sesión o pregunta no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar respuesta: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_feedback(request, session_id):
    """
    Obtener retroalimentación de la sesión completada
    """
    try:
        session = UserICFESSession.objects.get(
            uuid=session_id,
            user=request.user,
            status='COMPLETED'
        )
        
        # Obtener todas las respuestas de la sesión
        respuestas = RespuestaUsuarioICFES.objects.filter(
            usuario=request.user,
            sesion_id=str(session.uuid)
        )
        
        total_questions = respuestas.count()
        correct_answers = respuestas.filter(es_correcta=True).count()
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Generar feedback básico
        if accuracy >= 80:
            message = "¡Excelente trabajo! Dominas muy bien este tema."
            strengths = ["Comprensión sólida del tema", "Buena aplicación de conceptos"]
            improvements = ["Continúa practicando para mantener este nivel"]
        elif accuracy >= 60:
            message = "Buen trabajo, pero hay espacio para mejorar."
            strengths = ["Conocimiento básico del tema"]
            improvements = ["Revisar conceptos fundamentales", "Practicar más ejercicios"]
        else:
            message = "Es recomendable repasar los conceptos básicos."
            strengths = ["Iniciativa para practicar"]
            improvements = ["Estudiar teoría fundamental", "Practicar ejercicios básicos", "Buscar apoyo adicional"]
        
        return Response({
            'success': True,
            'data': {
                'accuracy': accuracy,
                'final_score': correct_answers,
                'total_questions': total_questions,
                'feedback': {
                    'message': message,
                    'strengths': strengths,
                    'improvements': improvements
                }
            }
        })
        
    except UserICFESSession.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Sesión no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener feedback: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 