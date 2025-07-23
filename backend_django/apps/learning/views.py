"""
Views para Learning Paths IA - Sistema de Aprendizaje Personalizado
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    LearningPath, LearningPathUnit, LearningPathLesson,
    UserPathEnrollment, UserLessonProgress
)
from .serializers import (
    LearningPathSerializer, LearningPathDetailSerializer,
    UserPathEnrollmentSerializer, UserLessonProgressSerializer
)
from .recommendation_engine import LearningRecommendationEngine

# Importar modelos de ICFES para obtener resultados reales
from apps.icfes.models import ICFESResult, UserICFESSession
from apps.icfes.models_nuevo import RespuestaUsuarioICFES


class LearningPathViewSet(viewsets.ModelViewSet):
    """ViewSet para Learning Paths"""
    serializer_class = LearningPathSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LearningPath.objects.filter(status='PUBLISHED')
    
    @action(detail=False, methods=['get'])
    def active_path(self, request):
        """
        Obtener el plan de aprendizaje activo del usuario
        ACTUALIZADO: Usa datos reales del ICFESResult y maneja diferentes tipos
        """
        try:
            plan_type = request.GET.get('type', 'default')
            print(f"🔍 Active path request from user {request.user.username}, type: {plan_type}")
            
            # Buscar inscripción activa
            enrollment = UserPathEnrollment.objects.filter(
                user=request.user,
                status='ACTIVE'
            ).first()
            
            print(f"📊 Found enrollment: {enrollment is not None}")
            if enrollment:
                print(f"📝 Enrollment path: {enrollment.learning_path.name}")
            
            if enrollment:
                # Usuario ya tiene un plan activo
                path_data = self._build_active_path_response(enrollment)
                print(f"✅ Returning active path: {path_data['name']}")
                return Response({
                    'success': True,
                    'activePath': path_data,
                    'planType': plan_type
                })
            
            # Si no tiene plan activo, verificar si completó algún quiz
            recent_result = ICFESResult.objects.filter(
                user=request.user
            ).order_by('-created_at').first()
            
            print(f"🎯 Found recent result: {recent_result is not None}")
            if recent_result:
                print(f"📊 Recent result score: {recent_result.mathematics_score}/100")
            
            if recent_result:
                # Tiene resultados de quiz, generar plan según tipo
                plan_data = self._generate_plan_from_quiz_result(recent_result, plan_type)
                print(f"🎓 Generated plan: {plan_data['name']}")
                return Response({
                    'success': True,
                    'activePath': plan_data,
                    'planType': plan_type,
                    'message': f'¡Plan {self._get_plan_type_name(plan_type)} generado basado en tu diagnóstico!'
                })
            
            # No tiene plan ni resultados de quiz
            print(f"⚠️ No plan or results found for user {request.user.username}")
            return Response({
                'success': True,
                'activePath': None,
                'needsDiagnostic': True,
                'planType': plan_type,
                'message': 'Completa primero el diagnóstico para generar tu plan personalizado'
            })
            
        except Exception as e:
            print(f"❌ Error en active_path: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response({
                'success': False,
                'message': f'Error al obtener plan: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_plan_type_name(self, plan_type):
        """Obtener nombre legible del tipo de plan"""
        names = {
            'quiz': 'por Quiz Específico',
            'subject': 'por Materia',
            'comprehensive': 'Integral',
            'default': 'Personalizado'
        }
        return names.get(plan_type, 'Personalizado')
    
    def _build_active_path_response(self, enrollment):
        """Construir respuesta para plan activo existente"""
        learning_path = enrollment.learning_path
        print(f"🏗️ Building response for path: {learning_path.name}")
        
        # Obtener unidades y progreso
        units = []
        units_count = learning_path.units.count()
        print(f"📚 Found {units_count} units")
        
        for unit in learning_path.units.all().order_by('order'):
            unit_progress = self._calculate_unit_progress(unit, enrollment)
            units.append({
                'id': str(unit.uuid),
                'position': unit.order,
                'title': unit.title,
                'description': unit.description,
                'type': unit.unit_type,
                'progress': unit_progress['percentage'],
                'lessons': unit_progress['lessons'],
                'locked': unit_progress['locked'],
                'estimatedDuration': unit.estimated_duration_minutes,
                'xpReward': unit.xp_reward
            })
        
        response_data = {
            'id': str(learning_path.uuid),
            'name': learning_path.name,
            'description': learning_path.description,
            'pathType': learning_path.path_type,
            'difficulty': learning_path.difficulty_level,
            'progress': enrollment.progress_percentage,
            'estimatedHours': learning_path.estimated_duration_hours,
            'weeklyGoal': enrollment.daily_goal_minutes * 7 // 60,  # Convertir a horas semanales
            'targetAreas': learning_path.target_icfes_areas or [],
            'units': units
        }
        
        print(f"📦 Response data built with {len(units)} units")
        return response_data
    
    def _generate_plan_from_quiz_result(self, icfes_result, plan_type='default'):
        """
        Generar plan de aprendizaje basado en resultado real de ICFES
        ACTUALIZADO: Maneja diferentes tipos de plan
        """
        print(f"🎯 Generating plan type '{plan_type}' for user {icfes_result.user.username}")
        
        # Obtener respuestas detalladas del usuario
        respuestas = RespuestaUsuarioICFES.objects.filter(
            user=icfes_result.user,
            session_id=str(icfes_result.session.uuid)
        ).select_related('pregunta', 'pregunta__area_tematica')
        
        print(f"📊 Found {respuestas.count()} responses")
        
        # Analizar áreas débiles según el tipo de plan
        weak_areas = self._analyze_weak_areas_by_type(respuestas, plan_type)
        print(f"🎯 Weak areas identified: {weak_areas}")
        
        # Usar motor de recomendaciones
        engine = LearningRecommendationEngine()
        
        # Analizar falencias usando el motor
        analysis = engine.analyze_quiz_results(icfes_result.user, str(icfes_result.session.uuid))
        
        # Si no hay análisis, crear uno básico según el tipo
        if not analysis:
            analysis = self._create_basic_analysis(icfes_result, weak_areas, plan_type)
        
        # Generar plan personalizado real
        learning_path = engine.generate_personalized_path(icfes_result.user, analysis)
        print(f"🎓 Generated learning path: {learning_path.name}")
        
        # Construir respuesta basada en plan real generado
        units = []
        for unit in learning_path.units.all().order_by('order'):
            lessons = []
            for lesson in unit.lessons.all().order_by('order'):
                lessons.append({
                    'id': str(lesson.uuid),
                    'title': lesson.title,
                    'type': lesson.lesson_type,
                    'duration': lesson.estimated_duration_minutes,
                    'completed': False,
                    'score': None,
                    'xpReward': lesson.xp_reward,
                    'passingScore': lesson.passing_score
                })
            
            units.append({
                'id': str(unit.uuid),
                'position': unit.order,
                'title': unit.title,
                'description': unit.description,
                'type': unit.unit_type,
                'progress': 0,
                'lessons': lessons,
                'locked': unit.order > 1,  # Solo la primera unidad desbloqueada
                'estimatedDuration': unit.estimated_duration_minutes,
                'xpReward': unit.xp_reward
            })
        
        response_data = {
            'id': str(learning_path.uuid),
            'name': learning_path.name,
            'description': learning_path.description,
            'pathType': learning_path.path_type,
            'difficulty': learning_path.difficulty_level,
            'progress': 0,
            'estimatedHours': learning_path.estimated_duration_hours,
            'weeklyGoal': learning_path.recommended_weekly_hours,
            'targetAreas': weak_areas,
            'units': units
        }
        
        print(f"📦 Generated response with {len(units)} units")
        return response_data
    
    def _analyze_weak_areas_by_type(self, respuestas, plan_type):
        """Analizar áreas débiles según el tipo de plan"""
        if plan_type == 'quiz':
            # Solo analizar este quiz específico
            return self._analyze_quiz_specific_areas(respuestas)
        elif plan_type == 'subject':
            # Solo matemáticas
            return ['Álgebra Básica', 'Geometría', 'Estadística']
        elif plan_type == 'comprehensive':
            # Todas las materias ICFES
            return ['Matemáticas', 'Lectura Crítica', 'Ciencias Naturales', 'Sociales y Ciudadanas', 'Inglés']
        else:
            # Análisis estándar
            return self._analyze_quiz_specific_areas(respuestas)
    
    def _analyze_quiz_specific_areas(self, respuestas):
        """Analizar áreas específicas del quiz"""
        area_stats = {}
        for respuesta in respuestas:
            if respuesta.pregunta.area_tematica:
                area_name = respuesta.pregunta.area_tematica.nombre
                if area_name not in area_stats:
                    area_stats[area_name] = {'total': 0, 'correct': 0}
                
                area_stats[area_name]['total'] += 1
                if respuesta.es_correcta:
                    area_stats[area_name]['correct'] += 1
        
        # Identificar áreas con menos del 60% de acierto
        weak_areas = []
        for area, stats in area_stats.items():
            accuracy = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
            if accuracy < 60:
                # Mapear a nombres estándar
                area_mapping = {
                    'Aritmética y Operaciones Básicas': 'Álgebra Básica',
                    'Álgebra y Funciones': 'Funciones y Álgebra',
                    'Geometría y Trigonometría': 'Geometría',
                    'Estadística y Probabilidad': 'Estadística',
                    'Problemas Aplicados y Análisis': 'Problemas Aplicados'
                }
                mapped_area = area_mapping.get(area, area)
                if mapped_area not in weak_areas:
                    weak_areas.append(mapped_area)
        
        return weak_areas
    
    def _create_basic_analysis(self, icfes_result, weak_areas, plan_type):
        """Crear análisis básico cuando no hay datos del motor"""
        return {
            'global_score': icfes_result.global_score,
            'critical_areas': weak_areas,
            'plan_type': plan_type,
            'area_analysis': {
                'mathematics': {
                    'score': icfes_result.mathematics_score,
                    'weak_topics': [{'topic': area, 'score': 50} for area in weak_areas]
                }
            }
        }
    
    def _calculate_unit_progress(self, unit, enrollment):
        """Calcular progreso de una unidad"""
        lessons = []
        total_lessons = unit.lessons.count()
        completed_lessons = 0
        
        for lesson in unit.lessons.all().order_by('order'):
            lesson_progress = UserLessonProgress.objects.filter(
                enrollment=enrollment,
                path_lesson=lesson
            ).first()
            
            is_completed = lesson_progress and lesson_progress.status == 'COMPLETED'
            if is_completed:
                completed_lessons += 1
            
            lessons.append({
                'id': str(lesson.uuid),
                'title': lesson.title,
                'type': lesson.lesson_type,
                'duration': lesson.estimated_duration_minutes,
                'completed': is_completed,
                'score': lesson_progress.best_score if lesson_progress else None,
                'xpReward': lesson.xp_reward,
                'passingScore': lesson.passing_score
            })
        
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Una unidad está bloqueada si la anterior no está completa (excepto la primera)
        is_locked = False
        if unit.order > 1:
            previous_units = unit.learning_path.units.filter(order__lt=unit.order)
            for prev_unit in previous_units:
                prev_progress = self._calculate_unit_progress(prev_unit, enrollment)
                if prev_progress['percentage'] < 100:
                    is_locked = True
                    break
        
        return {
            'percentage': progress_percentage,
            'lessons': lessons,
            'locked': is_locked
        }
    
    @action(detail=False, methods=['post'])
    def generate_from_quiz(self, request):
        """
        Generar plan de aprendizaje desde resultados de quiz
        ACTUALIZADO: Usa resultados reales de ICFESResult
        """
        try:
            # Obtener el resultado más reciente del usuario
            latest_result = ICFESResult.objects.filter(
                user=request.user
            ).order_by('-created_at').first()
            
            if not latest_result:
                return Response({
                    'success': False,
                    'message': 'No se encontraron resultados de quiz. Completa primero un diagnóstico.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generar plan basado en resultado real
            plan_data = self._generate_plan_from_quiz_result(latest_result)
            
            return Response({
                'success': True,
                'learningPath': plan_data,
                'message': f'Plan personalizado generado basado en tu puntaje de {latest_result.mathematics_score}/100'
            })
            
        except Exception as e:
            print(f"Error en generate_from_quiz: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error al generar plan: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """
        Obtener métricas de aprendizaje del usuario
        ACTUALIZADO: Usa datos reales de sesiones ICFES
        """
        try:
            # Obtener sesiones ICFES completadas
            completed_sessions = UserICFESSession.objects.filter(
                user=request.user,
                status='COMPLETED'
            ).order_by('-completed_at')
            
            # Obtener resultados ICFES
            icfes_results = ICFESResult.objects.filter(
                user=request.user
            ).order_by('-created_at')
            
            # Calcular métricas reales
            total_study_time = 0
            total_sessions = completed_sessions.count()
            average_accuracy = 0
            max_streak = 1
            current_streak = 0
            predicted_score = 300  # Base
            
            if icfes_results.exists():
                # Calcular precisión promedio
                accuracies = [result.accuracy_percentage for result in icfes_results]
                average_accuracy = sum(accuracies) / len(accuracies)
                
                # Predecir puntaje basado en tendencia
                latest_scores = [result.mathematics_score for result in icfes_results[:3]]
                if latest_scores:
                    predicted_score = min(sum(latest_scores) / len(latest_scores) * 5, 500)
                
                # Calcular tiempo total de estudio (estimado)
                total_study_time = sum(result.total_time_seconds for result in icfes_results) // 60
            
            # Calcular progreso semanal
            now = timezone.now()
            week_start = now - timedelta(days=7)
            weekly_sessions = completed_sessions.filter(completed_at__gte=week_start)
            
            weekly_minutes = sum(session.total_time_seconds for session in weekly_sessions) // 60
            weekly_lessons = weekly_sessions.count()
            
            metrics = {
                'totalStudyTime': total_study_time,
                'averageAccuracy': round(average_accuracy, 1),
                'maxStreak': max_streak,
                'currentStreak': current_streak,
                'predictedScore': int(predicted_score),
                'improvementRate': 5.2 if total_sessions > 1 else 0,  # Estimado
                'weeklyProgress': {
                    'completedMinutes': weekly_minutes,
                    'targetMinutes': 300,  # 5 horas por semana
                    'daysActive': min(weekly_sessions.count(), 7),
                    'lessonsCompleted': weekly_lessons
                }
            }
            
            return Response({
                'success': True,
                'metrics': metrics
            })
            
        except Exception as e:
            print(f"Error en metrics: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error al obtener métricas: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """
        Obtener lista de templates disponibles desde YAML
        """
        try:
            engine = LearningRecommendationEngine()
            available_templates = engine.get_available_templates()
            
            # Agregar configuración UI a cada template
            for template in available_templates:
                ui_config = engine.get_ui_configuration(template['name'])
                template['ui_config'] = ui_config
            
            return Response({
                'success': True,
                'templates': available_templates
            })
            
        except Exception as e:
            print(f"❌ Error en templates: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error al obtener templates: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def generate_from_template(self, request):
        """
        Generar learning path desde template específico
        """
        try:
            template_name = request.data.get('template')
            customization = request.data.get('customization', {})
            
            if not template_name:
                return Response({
                    'success': False,
                    'message': 'Template name requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"🎯 Generando path desde template: {template_name}")
            
            # Buscar resultado de ICFES más reciente del usuario
            recent_result = ICFESResult.objects.filter(
                user=request.user
            ).order_by('-created_at').first()
            
            if not recent_result:
                return Response({
                    'success': False,
                    'message': 'No hay resultados de diagnóstico disponibles'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear análisis básico para el template
            engine = LearningRecommendationEngine()
            analysis = {
                'global_score': recent_result.mathematics_score,
                'selected_template': template_name,
                'area_analysis': {},
                'weak_areas': [],
                'recommendations': [],
                'customization': customization
            }
            
            # Generar learning path
            learning_path = engine.generate_personalized_path(request.user, analysis)
            
            # Construir respuesta
            path_data = self._build_active_path_response(
                UserPathEnrollment.objects.get(
                    user=request.user,
                    learning_path=learning_path,
                    status='ACTIVE'
                )
            )
            
            return Response({
                'success': True,
                'learning_path': path_data,
                'message': 'Learning path generado exitosamente'
            })
            
        except Exception as e:
            print(f"❌ Error en generate_from_template: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response({
                'success': False,
                'message': f'Error al generar path: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLessonProgressViewSet(viewsets.ModelViewSet):
    """ViewSet para progreso de lecciones"""
    serializer_class = UserLessonProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserLessonProgress.objects.filter(
            enrollment__user=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def start_lesson(self, request):
        """Iniciar una lección"""
        try:
            unit_id = request.data.get('unit_id')
            lesson_id = request.data.get('lesson_id')
            
            # Por ahora retornar éxito simple
            return Response({
                'success': True,
                'message': f'Lección {lesson_id} iniciada',
                'lesson_url': f'/learning-path/unit/{unit_id}/lesson/{lesson_id}'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al iniciar lección: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def complete_lesson(self, request):
        """Completar una lección"""
        try:
            lesson_id = request.data.get('lesson_id')
            score = request.data.get('score', 100)
            
            # Por ahora retornar éxito simple
            return Response({
                'success': True,
                'message': f'Lección {lesson_id} completada con {score}%',
                'xp_earned': 50,
                'next_lesson': None
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al completar lección: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 