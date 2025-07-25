"""
Vistas API para el sistema de Asistente IA
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
from django.db.models import Q
import logging

from .analysis_engine import UserAnalysisEngine

logger = logging.getLogger(__name__)


class UserAnalysisView(APIView):
    """Vista para análisis completo del usuario por el Asistente IA"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Análisis completo del usuario",
        description="Analiza el perfil del usuario y genera recomendaciones personalizadas para el Asistente IA",
        responses={
            200: OpenApiResponse(description="Análisis completado exitosamente"),
            401: OpenApiResponse(description="No autorizado"),
            500: OpenApiResponse(description="Error interno del servidor")
        }
    )
    def get(self, request):
        try:
            user = request.user
            
            # Crear instancia del motor de análisis
            analysis_engine = UserAnalysisEngine(user)
            
            # Realizar análisis completo
            analysis_result = analysis_engine.analyze_complete_profile()
            
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
            'predictions': predictions
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


class QuizRecommendationsView(APIView):
    """Vista para recomendaciones específicas de quiz"""
    
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
    """Vista para análisis post-quiz y feedback"""
    
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
                # Obtener respuestas detalladas
                responses = RespuestaUsuarioICFES.objects.filter(
                    resultado_icfes=result
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