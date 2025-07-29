"""
Vistas API para el sistema de Asistente IA
Incluye todas las funcionalidades del sistema LLM integrado
"""

import asyncio
import logging
from typing import Dict, Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
from django.db.models import Q
from django.core.cache import cache

from .analysis_engine import UserAnalysisEngine
from .llm_orchestrator import llm_orchestrator
from .serializers import (
    ExplanationRequestSerializer, ExplanationResponseSerializer,
    ConversationCreateSerializer, MessageCreateSerializer,
    UserAnalysisRequestSerializer, UserAnalysisResponseSerializer,
    QuotaStatusSerializer, BatchExplanationRequestSerializer,
    AIConversationSerializer, AIMessageSerializer, AIUsageQuotaSerializer
)
from .models import (
    AIConversation, AIMessage, AIUsageQuota, AILearningInsight,
    AIInteractionLog, AIModel, AIPromptTemplate
)

logger = logging.getLogger(__name__)


class ExplanationView(APIView):
    """Vista principal para generar explicaciones inteligentes"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Generar explicación inteligente",
        description="Genera explicación personalizada usando IA para una pregunta específica",
        request=ExplanationRequestSerializer,
        responses={
            200: ExplanationResponseSerializer,
            400: OpenApiResponse(description="Datos inválidos"),
            429: OpenApiResponse(description="Límite de cuota excedido"),
            500: OpenApiResponse(description="Error interno")
        }
    )
    def post(self, request):
        """Genera explicación personalizada para una pregunta"""
        
        try:
            # Validar datos de entrada
            serializer = ExplanationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Datos inválidos',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Preparar contexto del usuario
            user_context = self._build_user_context(request.user, serializer.validated_data)
            
            # Preparar datos de la pregunta
            question_data = {
                'id': serializer.validated_data['question_id'],
                'question_text': serializer.validated_data['question_text'],
                'selected_option': serializer.validated_data['selected_option'],
                'correct_option': serializer.validated_data['correct_option'],
                'area': serializer.validated_data['area']
            }
            
            # Llamar al orchestrator
            result = asyncio.run(
                llm_orchestrator.generate_explanation(
                    question_data=question_data,
                    user_context=user_context,
                    explanation_type=serializer.validated_data['explanation_type']
                )
            )
            
            # Procesar resultado
            if result.get('success', True):
                response_data = {
                    'success': True,
                    'content': result.get('content', ''),
                    'explanation_type': serializer.validated_data['explanation_type'],
                    'model_used': result.get('model_used', 'unknown'),
                    'personalized': result.get('personalized', True),
                    'confidence_score': result.get('confidence_score'),
                    'processing_time_ms': result.get('response_time_ms', 0),
                    'cached': result.get('cached', False),
                    'tokens_used': result.get('tokens_used'),
                    'recommendations': result.get('recommendations', []),
                    'related_concepts': result.get('related_concepts', [])
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # Manejar errores específicos
                if result.get('type') == 'quota_exceeded':
                    return Response(result, status=status.HTTP_429_TOO_MANY_REQUESTS)
                else:
                    return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Error en ExplanationView: {str(e)}")
            return Response({
                'success': False,
                'message': 'Error interno del servidor',
                'error': str(e) if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _build_user_context(self, user, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construye contexto completo del usuario para la IA"""
        
        try:
            # Obtener análisis del usuario
            analysis_engine = UserAnalysisEngine(user)
            user_stats = analysis_engine._get_user_stats()
            strengths_weaknesses = analysis_engine._identify_strengths_weaknesses()
            
            context = {
                'user_id': user.id,
                'level': user.level,
                'hero_class': user.hero_class,
                'assigned_role': user.assigned_role or 'ALL',
                'accuracy': user_stats.get('accuracy', 0),
                'strengths': strengths_weaknesses.get('strengths', []),
                'weaknesses': strengths_weaknesses.get('weaknesses', []),
                'study_time': user_stats.get('study_time', 0),
                'streak': user_stats.get('streak', 0)
            }
            
            # Agregar contexto adicional del request
            user_context = validated_data.get('user_context', {})
            context.update(user_context)
            
            return context
            
        except Exception as e:
            logger.error(f"Error construyendo contexto de usuario: {str(e)}")
            # Contexto mínimo en caso de error
            return {
                'user_id': user.id,
                'level': user.level,
                'assigned_role': user.assigned_role or 'ALL',
                'accuracy': 0,
                'strengths': [],
                'weaknesses': []
            }


class ConversationView(APIView):
    """Vista para gestionar conversaciones AI"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Crear nueva conversación",
        request=ConversationCreateSerializer,
        responses={200: AIConversationSerializer}
    )
    def post(self, request):
        """Crea una nueva conversación con IA"""
        
        serializer = ConversationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Crear conversación
            conversation = AIConversation.objects.create(
                user=request.user,
                conversation_type=serializer.validated_data['conversation_type'],
                context_data=serializer.validated_data.get('context_data', {}),
                status='active'
            )
            
            # Procesar mensaje inicial si se proporciona
            initial_message = serializer.validated_data.get('initial_message')
            if initial_message:
                # Crear mensaje del usuario
                user_message = AIMessage.objects.create(
                    conversation=conversation,
                    role='user',
                    content=initial_message
                )
                
                # Generar respuesta automática de la IA
                # TODO: Integrar con orchestrator para respuesta automática
            
            # Serializar y retornar
            response_serializer = AIConversationSerializer(conversation)
            return Response({
                'success': True,
                'conversation': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creando conversación: {str(e)}")
            return Response({
                'success': False,
                'message': 'Error creando conversación'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Listar conversaciones del usuario",
        responses={200: AIConversationSerializer(many=True)}
    )
    def get(self, request):
        """Lista las conversaciones del usuario"""
        
        conversations = AIConversation.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]  # Últimas 20 conversaciones
        
        serializer = AIConversationSerializer(conversations, many=True)
        return Response({
            'success': True,
            'conversations': serializer.data
        })


class MessageView(APIView):
    """Vista para gestionar mensajes en conversaciones"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Enviar mensaje en conversación",
        request=MessageCreateSerializer,
        responses={200: AIMessageSerializer}
    )
    def post(self, request):
        """Envía un mensaje en una conversación y obtiene respuesta de IA"""
        
        serializer = MessageCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Obtener conversación
            conversation = AIConversation.objects.get(
                uuid=serializer.validated_data['conversation_id'],
                user=request.user
            )
            
            # Crear mensaje del usuario
            user_message = AIMessage.objects.create(
                conversation=conversation,
                role='user',
                content=serializer.validated_data['content']
            )
            
            # Generar respuesta de IA usando el orchestrator
            user_context = self._build_user_context_for_conversation(request.user, conversation)
            message_data = {
                'content': serializer.validated_data['content'],
                'conversation_type': conversation.conversation_type,
                'context_data': serializer.validated_data.get('context_data', {})
            }
            
            # TODO: Integrar completamente con orchestrator para conversaciones
            # Por ahora, respuesta simulada
            ai_response = "Esta es una respuesta simulada. El sistema completo estará disponible cuando se configure la API key."
            
            # Crear mensaje de respuesta de IA
            ai_message = AIMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=ai_response,
                tokens_input=50,
                tokens_output=100,
                response_time_ms=1500
            )
            
            # Actualizar conversación
            conversation.message_count += 2
            conversation.save()
            
            response_serializer = AIMessageSerializer(ai_message)
            return Response({
                'success': True,
                'message': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except AIConversation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Conversación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error enviando mensaje: {str(e)}")
            return Response({
                'success': False,
                'message': 'Error enviando mensaje'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _build_user_context_for_conversation(self, user, conversation):
        """Construye contexto para conversaciones"""
        return {
            'user_id': user.id,
            'level': user.level,
            'assigned_role': user.assigned_role or 'ALL',
            'conversation_history': conversation.context_data
        }


class UserAnalysisView(APIView):
    """Vista mejorada para análisis completo del usuario"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Obtener análisis básico del usuario",
        description="Obtiene análisis básico del usuario sin parámetros adicionales",
        responses={200: UserAnalysisResponseSerializer}
    )
    def get(self, request):
        """Análisis básico del usuario sin parámetros"""
        try:
            user = request.user
            
            # Crear instancia del motor de análisis
            analysis_engine = UserAnalysisEngine(user)
            
            # Realizar análisis básico
            analysis_result = analysis_engine.analyze_complete_profile()
            
            # Procesar resultados para el frontend
            processed_result = self._process_analysis_for_frontend(analysis_result)
            
            return Response({
                'success': True,
                'message': 'Análisis básico completado exitosamente',
                'data': processed_result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en análisis GET del usuario: {str(e)}")
            return Response({
                'success': False,
                'message': 'Error obteniendo análisis del usuario',
                'error': str(e) if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Análisis completo del usuario con IA",
        description="Analiza el perfil del usuario y genera recomendaciones personalizadas avanzadas",
        request=UserAnalysisRequestSerializer,
        responses={200: UserAnalysisResponseSerializer}
    )
    def post(self, request):
        try:
            # Validar parámetros
            serializer = UserAnalysisRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = request.user
            analysis_type = serializer.validated_data['analysis_type']
            
            # Crear instancia del motor de análisis
            analysis_engine = UserAnalysisEngine(user)
            
            # Realizar análisis según tipo solicitado
            if analysis_type == 'complete':
                analysis_result = analysis_engine.analyze_complete_profile()
            elif analysis_type == 'performance':
                analysis_result = {'performance_analysis': analysis_engine._analyze_performance()}
            elif analysis_type == 'learning_patterns':
                analysis_result = {'learning_patterns': analysis_engine._analyze_learning_patterns()}
            elif analysis_type == 'recommendations':
                analysis_result = {'recommendations': analysis_engine._generate_recommendations()}
            
            # Generar insights adicionales con IA si se solicita
            if serializer.validated_data['include_insights']:
                ai_insights = self._generate_ai_insights(user, analysis_result)
                analysis_result['ai_insights'] = ai_insights
            
            # Procesar resultados para el frontend
            processed_result = self._process_analysis_for_frontend(analysis_result)
            
            return Response({
                'success': True,
                'message': 'Análisis completado exitosamente',
                'data': processed_result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en análisis de usuario {request.user.id}: {str(e)}")
            
            # Datos de fallback en caso de error
            fallback_data = self._generate_fallback_analysis(request.user)
            
            return Response({
                'success': True,
                'message': 'Análisis completado con datos limitados',
                'data': fallback_data
            }, status=status.HTTP_200_OK)
    
    def _generate_ai_insights(self, user, analysis_result):
        """Genera insights adicionales usando IA"""
        try:
            # Preparar datos para análisis con IA
            insight_data = {
                'user_stats': analysis_result.get('user_stats', {}),
                'performance': analysis_result.get('performance_analysis', {}),
                'patterns': analysis_result.get('learning_patterns', {})
            }
            
            # TODO: Integrar con orchestrator para insights avanzados
            # Por ahora, insights simulados
            return {
                'learning_style_prediction': 'visual',
                'optimal_study_schedule': 'morning_sessions',
                'predicted_improvement_areas': ['algebra', 'geometry'],
                'confidence_level': 0.75
            }
            
        except Exception as e:
            logger.error(f"Error generando insights AI: {str(e)}")
            return {}
    
    def _process_analysis_for_frontend(self, analysis):
        """Procesa los datos del análisis para el frontend"""
        
        # Estadísticas del usuario
        user_stats = analysis.get('user_stats', {})
        strengths_weaknesses = analysis.get('strengths_weaknesses', {})
        
        # Combinar fortalezas y debilidades en user_stats
        user_stats['strengths'] = strengths_weaknesses.get('strengths', [])
        user_stats['weaknesses'] = strengths_weaknesses.get('weaknesses', [])
        
        # Predicciones
        predictions = analysis.get('predictions', {})
        if predictions:
            user_stats['predicted_score'] = predictions.get('projected_score', user_stats.get('predicted_score', 0))
        
        return {
            'user_stats': user_stats,
            'recommendations': analysis.get('recommendations', []),
            'required_tasks': analysis.get('required_tasks', []),
            'performance_analysis': analysis.get('performance_analysis', {}),
            'learning_patterns': analysis.get('learning_patterns', {}),
            'predictions': predictions,
            'ai_insights': analysis.get('ai_insights', {})
        }
    
    def _generate_fallback_analysis(self, user):
        """Genera análisis de fallback cuando hay errores"""
        
        # Estadísticas básicas del usuario
        profile = getattr(user, 'profile', None)
        
        # Calcular precisión básica
        accuracy = 0
        if profile and profile.total_questions_answered > 0:
            accuracy = (profile.total_correct_answers / profile.total_questions_answered) * 100
        
        # Determinar fortalezas y debilidades basadas en datos limitados
        strengths = []
        weaknesses = []
        
        if accuracy >= 80:
            strengths = ['Resolución de problemas', 'Comprensión conceptual']
        elif accuracy >= 60:
            strengths = ['Persistencia', 'Mejora continua']
            weaknesses = ['Precisión', 'Revisión de conceptos']
        else:
            weaknesses = ['Conceptos fundamentales', 'Práctica adicional', 'Manejo de tiempo']
        
        # Generar recomendaciones básicas
        recommendations = []
        
        if accuracy < 70:
            recommendations.append({
                'type': 'focus',
                'title': 'Reforzar Fundamentos',
                'description': 'Enfócate en revisar conceptos básicos para mejorar tu base de conocimientos.',
                'priority': 'high',
                'estimated_improvement': 15,
                'icon': '📚'
            })
        
        if profile and profile.current_streak < 3:
            recommendations.append({
                'type': 'practice',
                'title': 'Desarrollar Consistencia',
                'description': 'Mantén una rutina de estudio diaria para mejorar la retención.',
                'priority': 'medium',
                'estimated_improvement': 10,
                'icon': '🔥'
            })
        
        recommendations.append({
            'type': 'strategy',
            'title': 'Optimizar Estrategia',
            'description': 'Usa técnicas de eliminación y administra mejor tu tiempo en cada pregunta.',
            'priority': 'medium',
            'estimated_improvement': 8,
            'icon': '⚡'
        })
        
        # Tareas requeridas si faltan datos
        required_tasks = []
        
        if not user.initial_assessment_completed:
            required_tasks.append({
                'id': 'initial_assessment',
                'title': 'Evaluación Inicial',
                'description': 'Completa tu evaluación diagnóstica para personalizar tu experiencia.',
                'type': 'assessment',
                'estimated_time': 15,
                'reward_xp': 200,
                'completed': False
            })
        
        if profile and profile.total_questions_answered < 30:
            required_tasks.append({
                'id': 'practice_session',
                'title': 'Sesión de Práctica',
                'description': 'Responde más preguntas para mejorar el análisis de tu rendimiento.',
                'type': 'practice',
                'estimated_time': 20,
                'reward_xp': 150,
                'completed': False
            })
        
        return {
            'user_stats': {
                'level': user.level,
                'hero_class': user.get_hero_class_display(),
                'total_questions_answered': profile.total_questions_answered if profile else 0,
                'accuracy': round(accuracy, 1),
                'strengths': strengths,
                'weaknesses': weaknesses,
                'predicted_score': int(accuracy * 5) if accuracy > 0 else 200,  # Estimación básica
                'study_time': profile.total_study_minutes if profile else 0,
                'streak': profile.current_streak if profile else 0,
                'experience_points': user.experience_points,
                'vitality': profile.current_vitality if profile else 100
            },
            'recommendations': recommendations,
            'required_tasks': required_tasks,
            'performance_analysis': {
                'recent_performance_trend': 'stable',
                'consistency_score': 0.7
            },
            'learning_patterns': {
                'study_frequency': 50,
                'learning_style': 'adaptive'
            },
            'predictions': {
                'confidence_level': 0.5
            }
        }


class QuotaStatusView(APIView):
    """Vista para verificar estado de cuotas del usuario"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Estado de cuotas de IA del usuario",
        responses={200: QuotaStatusSerializer}
    )
    def get(self, request):
        """Obtiene el estado actual de las cuotas de IA del usuario"""
        
        try:
            quota, created = AIUsageQuota.objects.get_or_create(
                user=request.user,
                defaults={
                    'daily_limit': 50,
                    'monthly_limit': 1000,
                    'is_premium': False
                }
            )
            
            # Resetear si es necesario
            quota._reset_if_needed()
            
            data = {
                'daily_used': quota.used_today,
                'daily_limit': quota.daily_limit,
                'daily_remaining': max(0, quota.daily_limit - quota.used_today),
                'monthly_used': quota.used_this_month,
                'monthly_limit': quota.monthly_limit,
                'monthly_remaining': max(0, quota.monthly_limit - quota.used_this_month),
                'can_use_ai': quota.can_use_ai(),
                'is_premium': quota.is_premium,
                'reset_times': {
                    'next_daily_reset': quota.last_reset_daily.replace(hour=0, minute=0, second=0, microsecond=0) + timezone.timedelta(days=1),
                    'next_monthly_reset': quota.last_reset_monthly.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timezone.timedelta(days=32)
                }
            }
            
            return Response({
                'success': True,
                'quota_status': data
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo cuotas: {str(e)}")
            return Response({
                'success': False,
                'message': 'Error obteniendo estado de cuotas'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BatchExplanationView(APIView):
    """Vista para procesamiento batch de explicaciones"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Procesar múltiples explicaciones en lote",
        request=BatchExplanationRequestSerializer,
        responses={200: OpenApiResponse(description="Explicaciones procesadas")}
    )
    def post(self, request):
        """Procesa múltiples solicitudes de explicación en lote"""
        
        serializer = BatchExplanationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            questions = serializer.validated_data['questions']
            parallel_processing = serializer.validated_data['parallel_processing']
            
            results = []
            
            for question_data in questions:
                # Procesar cada pregunta individualmente
                # TODO: Implementar procesamiento paralelo real
                user_context = self._build_user_context(request.user, question_data)
                
                # Simular procesamiento
                result = {
                    'question_id': question_data['question_id'],
                    'success': True,
                    'content': f"Explicación simulada para pregunta {question_data['question_id']}",
                    'processing_time_ms': 1000
                }
                results.append(result)
            
            return Response({
                'success': True,
                'message': f'Procesadas {len(results)} explicaciones',
                'results': results,
                'processing_time_total_ms': sum(r['processing_time_ms'] for r in results)
            })
            
        except Exception as e:
            logger.error(f"Error en procesamiento batch: {str(e)}")
            return Response({
                'success': False,
                'message': 'Error en procesamiento batch'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _build_user_context(self, user, question_data):
        """Construye contexto básico del usuario"""
        return {
            'user_id': user.id,
            'level': user.level,
            'assigned_role': user.assigned_role or 'ALL'
        }


# Vistas auxiliares

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_models_list(request):
    """Lista modelos de IA disponibles"""
    models = AIModel.objects.filter(is_active=True)
    return Response({
        'success': True,
        'models': [
            {
                'id': model.id,
                'name': model.name,
                'provider': model.provider,
                'purpose': model.purpose,
                'is_default': model.is_default
            }
            for model in models
        ]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompt_templates_list(request):
    """Lista templates de prompts disponibles"""
    
    # Filtrar por área si se especifica
    area = request.GET.get('area')
    category = request.GET.get('category')
    
    templates = AIPromptTemplate.objects.filter(is_active=True)
    
    if area:
        templates = templates.filter(
            Q(code__icontains=area) | Q(area_filter__nombre=area)
        )
    
    if category:
        templates = templates.filter(category=category)
    
    return Response({
        'success': True,
        'templates': [
            {
                'id': template.id,
                'name': template.name,
                'code': template.code,
                'category': template.category,
                'role_filter': template.role_filter,
                'effectiveness_score': template.effectiveness_score
            }
            for template in templates[:20]  # Limitar resultado
        ]
    })


# Vistas que ya existían (mantenidas para compatibilidad)

class QuizRecommendationsView(APIView):
    """Vista para recomendaciones específicas de quiz (mantenida)"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Recomendaciones para quiz específico",
        description="Genera recomendaciones específicas para un quiz basado en área y dificultad"
    )
    def post(self, request):
        try:
            user = request.user
            quiz_area = request.data.get('area', 'matematicas')
            difficulty = request.data.get('difficulty', 'INTERMEDIO')
            question_count = request.data.get('question_count', 5)
            
            # Crear motor de análisis
            analysis_engine = UserAnalysisEngine(user)
            
            # Obtener estadísticas del usuario
            user_stats = analysis_engine._get_user_stats()
            
            # Generar recomendaciones específicas para el quiz
            quiz_recommendations = self._generate_quiz_specific_recommendations(
                user_stats, quiz_area, difficulty, question_count
            )
            
            return Response({
                'success': True,
                'data': {
                    'quiz_strategy': quiz_recommendations['strategy'],
                    'time_allocation': quiz_recommendations['time_allocation'],
                    'focus_areas': quiz_recommendations['focus_areas'],
                    'confidence_tips': quiz_recommendations['confidence_tips']
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones de quiz: {str(e)}")
            
            return Response({
                'success': False,
                'message': 'Error generando recomendaciones',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_quiz_specific_recommendations(self, user_stats, area, difficulty, question_count):
        """Genera recomendaciones específicas para el quiz"""
        
        accuracy = user_stats.get('accuracy', 0)
        
        # Estrategia basada en precisión
        if accuracy >= 80:
            strategy = "Tu precisión es excelente. Confía en tus conocimientos y mantén un ritmo constante."
        elif accuracy >= 60:
            strategy = "Tienes una base sólida. Lee cuidadosamente cada pregunta y usa el proceso de eliminación."
        else:
            strategy = "Enfócate en las preguntas que domines. No dudes en usar pistas y revisar conceptos clave."
        
        # Asignación de tiempo
        avg_time_per_question = max(1.5, min(3.0, 2.5 - (accuracy / 100)))
        total_time = question_count * avg_time_per_question
        
        time_allocation = {
            'recommended_time_per_question': round(avg_time_per_question, 1),
            'total_estimated_time': round(total_time, 1),
            'time_distribution': {
                'reading_question': 30,  # segundos
                'analyzing_options': 40,
                'selecting_answer': 20,
                'review_if_time': 30
            }
        }
        
        # Áreas de enfoque basadas en debilidades conocidas
        weaknesses = user_stats.get('weaknesses', [])
        focus_areas = []
        
        if weaknesses:
            focus_areas = [f"Presta especial atención a: {', '.join(weaknesses[:2])}"]
        
        focus_areas.extend([
            f"Nivel de dificultad: {difficulty}",
            f"Área: {area.replace('_', ' ').title()}"
        ])
        
        # Tips de confianza
        confidence_tips = [
            "Confía en tu primera respuesta si estás seguro",
            "Usa el proceso de eliminación en preguntas difíciles",
            "Administra tu tiempo, pero no te apresures",
            "Revisa tus respuestas si te sobra tiempo"
        ]
        
        return {
            'strategy': strategy,
            'time_allocation': time_allocation,
            'focus_areas': focus_areas,
            'confidence_tips': confidence_tips
        }


class PostQuizAnalysisView(APIView):
    """Vista para análisis post-quiz y feedback (mantenida)"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Análisis post-quiz",
        description="Analiza el rendimiento en un quiz completado y genera feedback"
    )
    def post(self, request):
        try:
            user = request.user
            session_id = request.data.get('session_id')
            
            if not session_id:
                return Response({
                    'success': False,
                    'message': 'session_id es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener resultados del quiz
            quiz_analysis = self._analyze_quiz_performance(user, session_id)
            
            # Generar feedback y actualización del plan
            feedback = self._generate_post_quiz_feedback(user, quiz_analysis)
            
            return Response({
                'success': True,
                'data': {
                    'performance_summary': quiz_analysis,
                    'feedback': feedback,
                    'updated_recommendations': feedback.get('updated_recommendations', []),
                    'next_steps': feedback.get('next_steps', [])
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en análisis post-quiz: {str(e)}")
            
            return Response({
                'success': False,
                'message': 'Error analizando quiz',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _analyze_quiz_performance(self, user, session_id):
        """Analiza el rendimiento en un quiz específico"""
        try:
            from apps.icfes.models import ICFESResult, RespuestaUsuarioICFES
            
            # Buscar resultado por session_id
            result = ICFESResult.objects.filter(
                user=user,
                session__uuid=session_id
            ).first()
            
            if not result:
                # Si no encontramos por UUID, buscar el más reciente
                result = ICFESResult.objects.filter(user=user).order_by('-created_at').first()
            
            if result:
                # Obtener respuestas detalladas usando session_id
                responses = RespuestaUsuarioICFES.objects.filter(
                    user=user,
                    session_id=str(session_id)
                )
                
                return {
                    'total_score': result.global_score,
                    'accuracy': result.accuracy_percentage,
                    'total_questions': result.total_questions,
                    'correct_answers': result.correct_answers,
                    'time_spent': result.total_time_seconds,
                    'areas_performance': {
                        'mathematics': result.mathematics_score,
                        'reading': result.reading_score,
                        'sciences': result.natural_sciences_score,
                        'social': result.social_studies_score,
                        'english': result.english_score
                    },
                    'improvement_areas': self._identify_improvement_areas(responses)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error analizando performance del quiz: {str(e)}")
            return {}
    
    def _identify_improvement_areas(self, responses):
        """Identifica áreas específicas de mejora basadas en respuestas"""
        improvement_areas = []
        
        try:
            # Agrupar por tema/concepto
            topics_performance = {}
            
            for response in responses:
                if hasattr(response.pregunta, 'tema') and response.pregunta.tema:
                    topic = response.pregunta.tema
                    if topic not in topics_performance:
                        topics_performance[topic] = {'correct': 0, 'total': 0}
                    
                    topics_performance[topic]['total'] += 1
                    if response.es_correcta:
                        topics_performance[topic]['correct'] += 1
            
            # Identificar temas con baja performance
            for topic, stats in topics_performance.items():
                accuracy = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
                if accuracy < 60 and stats['total'] >= 2:  # Al menos 2 preguntas y < 60% accuracy
                    improvement_areas.append({
                        'topic': topic,
                        'accuracy': round(accuracy, 1),
                        'questions_count': stats['total']
                    })
            
            return sorted(improvement_areas, key=lambda x: x['accuracy'])[:3]  # Top 3 áreas de mejora
            
        except Exception as e:
            logger.error(f"Error identificando áreas de mejora: {str(e)}")
            return []
    
    def _generate_post_quiz_feedback(self, user, quiz_analysis):
        """Genera feedback personalizado post-quiz"""
        
        feedback = {
            'overall_performance': '',
            'specific_insights': [],
            'updated_recommendations': [],
            'next_steps': []
        }
        
        if not quiz_analysis:
            return feedback
        
        accuracy = quiz_analysis.get('accuracy', 0)
        total_score = quiz_analysis.get('total_score', 0)
        
        # Feedback general
        if accuracy >= 80:
            feedback['overall_performance'] = f"¡Excelente trabajo! Obtuviste {accuracy}% de precisión. Tu dominio del tema es sólido."
        elif accuracy >= 60:
            feedback['overall_performance'] = f"Buen rendimiento con {accuracy}% de precisión. Hay oportunidades claras de mejora."
        else:
            feedback['overall_performance'] = f"Con {accuracy}% de precisión, es importante reforzar los conceptos fundamentales."
        
        # Insights específicos
        improvement_areas = quiz_analysis.get('improvement_areas', [])
        if improvement_areas:
            feedback['specific_insights'].append(
                f"Áreas prioritarias de mejora: {', '.join([area['topic'] for area in improvement_areas[:2]])}"
            )
        
        time_spent = quiz_analysis.get('time_spent', 0)
        total_questions = quiz_analysis.get('total_questions', 1)
        avg_time = time_spent / total_questions if total_questions > 0 else 0
        
        if avg_time > 180:  # Más de 3 minutos por pregunta
            feedback['specific_insights'].append("Considera optimizar tu tiempo de respuesta por pregunta")
        elif avg_time < 60:  # Menos de 1 minuto por pregunta
            feedback['specific_insights'].append("Podrías beneficiarte de revisar más cuidadosamente cada pregunta")
        
        # Recomendaciones actualizadas
        if improvement_areas:
            for area in improvement_areas[:2]:
                feedback['updated_recommendations'].append({
                    'type': 'focus',
                    'title': f"Practicar {area['topic']}",
                    'description': f"Refuerza este tema donde obtuviste {area['accuracy']}% de precisión",
                    'priority': 'high',
                    'estimated_improvement': 15,
                    'icon': '📚'
                })
        
        # Próximos pasos
        if accuracy < 70:
            feedback['next_steps'].append("Revisar conceptos fundamentales del área evaluada")
            feedback['next_steps'].append("Practicar con ejercicios similares a nivel básico")
        else:
            feedback['next_steps'].append("Continuar con práctica en nivel de dificultad actual o superior")
            feedback['next_steps'].append("Enfocarse en velocidad de resolución")
        
        feedback['next_steps'].append("Realizar otro quiz en 2-3 días para medir progreso")
        
        return feedback 