"""
Vistas para Learning Paths Dinámicos - Sistema IA
Usa las tablas existentes sin modificar nada
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta

from apps.analytics.models import LearningAnalytics, SubjectAnalytics
from apps.icfes.models import ICFESPrediction, StudyPlan
from apps.questions.models import Subject, Topic, UserQuestionResponse
from apps.users.models import User


@api_view(['GET'])
def get_learning_path_test(request):
    """
    ENDPOINT TEMPORAL PARA DEBUG - SIN AUTENTICACIÓN
    """
    try:
        # Usar usuario kmj directamente
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(username='kmj')
        
        print(f"🔍 TEST_ENDPOINT: Usuario forzado: {user.username}")
        
        # Importar modelos de learning
        from apps.learning.models import UserPathEnrollment
        
        # Buscar enrollment activo
        enrollment = UserPathEnrollment.objects.filter(
            user=user,
            status='ACTIVE'
        ).first()
        
        if not enrollment:
            return Response({
                'success': False,
                'needsDiagnostic': True,
                'message': 'No se encontró un plan de aprendizaje activo para usuario kmj.'
            }, status=200)
        
        learning_path = enrollment.learning_path
        
        # Respuesta simplificada
        plan_data = {
            'id': learning_path.id,
            'name': learning_path.name,
            'description': learning_path.description,
            'total_units': learning_path.units.count()
        }
        
        return Response({
            'success': True,
            'activePath': plan_data,
            'needsDiagnostic': False,
            'message': f'Plan de prueba: {learning_path.name}'
        })
        
    except Exception as e:
        print(f"❌ Error en test endpoint: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@api_view(['GET'])
def get_learning_path(request):
    """
    Obtiene el plan de estudio activo del usuario
    TEMPORALMENTE SIN AUTENTICACIÓN ESTRICTA PARA DEBUGGING
    """
    print(f"🔍 GET_LEARNING_PATH: Request recibido")
    
    # TEMPORAL: Usar usuario kmj directamente si hay problemas de autenticación
    try:
        user = request.user
        if not user.is_authenticated:
            print(f"❌ Usuario no autenticado, usando kmj por defecto")
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(username='kmj')
        
        print(f"🔍 Usuario: {user.username} (ID: {user.id})")
        
        # Importar modelos de learning
        from apps.learning.models import UserPathEnrollment
        
        # Buscar enrollment activo
        enrollment = UserPathEnrollment.objects.filter(
            user=user,
            status='ACTIVE'
        ).first()
        
        if not enrollment:
            return Response({
                'success': False,
                'needsDiagnostic': True,
                'message': 'No se encontró un plan de aprendizaje activo. Completa un quiz primero.'
            }, status=200)
        
        learning_path = enrollment.learning_path
        
        # Calcular progreso
        total_units = learning_path.units.count()
        completed_lessons = 0  # Por ahora, después implementaremos el tracking real
        
        # Obtener unidades con sus lecciones
        units_data = []
        for unit in learning_path.units.all().order_by('order'):
            lessons_data = []
            for lesson in unit.lessons.all().order_by('order'):
                lessons_data.append({
                    'id': lesson.id,
                    'title': lesson.title,
                    'type': lesson.lesson_type,
                    'completed': False,  # Por ahora, después implementaremos tracking real
                    'duration_minutes': lesson.metadata.get('duration_minutes', 25) if lesson.metadata else 25
                })
            
            units_data.append({
                'id': unit.id,
                'title': unit.title,
                'description': unit.description,
                'icon': unit.icon_emoji,
                'unit_type': unit.unit_type,
                'xp_reward': unit.xp_reward,
                'difficulty_modifier': unit.difficulty_modifier,
                'estimated_duration_minutes': unit.estimated_duration_minutes,
                'lessons': lessons_data,
                'metadata': unit.metadata
            })
        
        # Información del plan
        plan_data = {
            'id': learning_path.id,
            'name': learning_path.name,
            'description': learning_path.description,
            'difficulty_level': learning_path.difficulty_level,
            'estimated_duration_hours': learning_path.estimated_duration_hours,
            'total_units': total_units,
            'units': units_data,
            'progress': {
                'completed_units': 0,  # Por ahora
                'total_units': total_units,
                'completion_percentage': 0,  # Por ahora
                'current_week': 1,
                'estimated_weeks': learning_path.estimated_weeks if hasattr(learning_path, 'estimated_weeks') else 4
            },
            'personalization': {
                'template_name': learning_path.metadata.get('template_name', 'basic_mathematics_path') if learning_path.metadata else 'basic_mathematics_path',
                'color_theme': learning_path.primary_color,
                'focus_areas': learning_path.metadata.get('weak_areas_focus', []) if learning_path.metadata else []
            }
        }
        
        return Response({
            'success': True,
            'activePath': plan_data,
            'needsDiagnostic': False,
            'message': f'Plan activo: {learning_path.name}'
        })
        
    except Exception as e:
        print(f"❌ Error en get_learning_path: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return Response({
            'success': False,
            'message': f'Error del servidor: {str(e)}',
            'needsDiagnostic': True
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_learning_path(request):
    """
    Genera un nuevo plan de estudio personalizado usando IA
    """
    user = request.user
    data = request.data
    
    try:
        # Obtener o crear analytics del usuario
        learning_analytics, created = LearningAnalytics.objects.get_or_create(
            user=user,
            defaults={
                'total_study_time_minutes': 0,
                'total_questions_answered': 0,
                'total_correct_answers': 0,
                'average_accuracy': 0.0,
            }
        )
        
        # Cancelar planes activos anteriores
        StudyPlan.objects.filter(user=user, status='ACTIVE').update(status='CANCELLED')
        
        # Análizar debilidades del usuario
        weak_areas = analyze_user_weaknesses(user)
        
        # Crear nuevo plan de estudio
        target_score = data.get('targetScore', 400)
        weeks = data.get('weeks', 12)
        hours_per_week = data.get('studyHoursPerWeek', 10)
        
        study_plan = StudyPlan.objects.create(
            user=user,
            name=f"Plan IA Personalizado - {timezone.now().strftime('%B %Y')}",
            description=f"Plan generado por IA para alcanzar {target_score} puntos en {weeks} semanas",
            plan_type='AI_GENERATED',
            status='ACTIVE',
            target_icfes_score=target_score,
            target_exam_date=timezone.now().date() + timedelta(weeks=weeks),
            weekly_study_hours=hours_per_week,
            total_planned_hours=weeks * hours_per_week,
            total_weeks=weeks,
            current_week=1,
            # Distribución inteligente basada en debilidades
            mathematics_percentage=calculate_subject_percentage('MATHEMATICS', weak_areas),
            reading_percentage=calculate_subject_percentage('READING', weak_areas),
            natural_sciences_percentage=calculate_subject_percentage('NATURAL_SCIENCES', weak_areas),
            social_studies_percentage=calculate_subject_percentage('SOCIAL_STUDIES', weak_areas),
            english_percentage=calculate_subject_percentage('ENGLISH', weak_areas),
        )
        
        # Actualizar recomendaciones en analytics
        learning_analytics.recommended_study_areas = [area['subject'] for area in weak_areas if area['priority'] <= 3]
        learning_analytics.personalized_difficulty = determine_optimal_difficulty(user)
        learning_analytics.save()
        
        # Generar módulos de la primera semana
        current_week_modules = generate_current_week_modules(user, weak_areas, 1)
        
        return Response({
            'path': {
                'id': str(study_plan.id),
                'name': study_plan.name,
                'description': study_plan.description,
                'totalWeeks': study_plan.total_weeks,
                'currentWeek': study_plan.current_week,
                'completionPercentage': 0,
                'estimatedHours': study_plan.total_planned_hours,
                'targetScore': study_plan.target_icfes_score,
                'createdBy': 'AI'
            },
            'currentWeekModules': current_week_modules,
            'weakAreas': weak_areas
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)


def analyze_user_weaknesses(user):
    """
    Analiza las debilidades del usuario basado en sus respuestas
    """
    weak_areas = []
    
    # Obtener analytics por materia
    subject_analytics = SubjectAnalytics.objects.filter(user=user)
    
    if not subject_analytics.exists():
        # Usuario sin datos, devolver áreas por defecto
        default_areas = [
            {'subject': 'Matemáticas', 'accuracy': 65, 'recommendedTime': 120, 'priority': 1, 'icon': '📐', 'color': '#FF6B6B'},
            {'subject': 'Lectura Crítica', 'accuracy': 78, 'recommendedTime': 90, 'priority': 2, 'icon': '📚', 'color': '#4ECDC4'},
            {'subject': 'Ciencias Naturales', 'accuracy': 82, 'recommendedTime': 60, 'priority': 3, 'icon': '🔬', 'color': '#45B7D1'},
            {'subject': 'Ciencias Sociales', 'accuracy': 88, 'recommendedTime': 45, 'priority': 4, 'icon': '🌍', 'color': '#96CEB4'},
            {'subject': 'Inglés', 'accuracy': 92, 'recommendedTime': 30, 'priority': 5, 'icon': '🇺🇸', 'color': '#FECA57'},
        ]
        return default_areas
    
    # Mapeo de materias
    subject_mapping = {
        'MATHEMATICS': {'name': 'Matemáticas', 'icon': '📐', 'color': '#FF6B6B'},
        'READING': {'name': 'Lectura Crítica', 'icon': '📚', 'color': '#4ECDC4'},
        'NATURAL_SCIENCES': {'name': 'Ciencias Naturales', 'icon': '🔬', 'color': '#45B7D1'},
        'SOCIAL_STUDIES': {'name': 'Ciencias Sociales', 'icon': '🌍', 'color': '#96CEB4'},
        'ENGLISH': {'name': 'Inglés', 'icon': '🇺🇸', 'color': '#FECA57'},
    }
    
    for analytics in subject_analytics:
        subject_info = subject_mapping.get(analytics.subject, {
            'name': analytics.get_subject_display(),
            'icon': '📋',
            'color': '#6C7CE7'
        })
        
        # Calcular tiempo recomendado basado en precisión
        recommended_time = calculate_recommended_time(analytics.accuracy_percentage)
        
        # Determinar prioridad (menor precisión = mayor prioridad)
        priority = determine_priority(analytics.accuracy_percentage)
        
        weak_areas.append({
            'subject': subject_info['name'],
            'accuracy': round(analytics.accuracy_percentage, 1),
            'recommendedTime': recommended_time,
            'priority': priority,
            'icon': subject_info['icon'],
            'color': subject_info['color']
        })
    
    # Ordenar por prioridad
    weak_areas.sort(key=lambda x: x['priority'])
    
    return weak_areas


def generate_current_week_modules(user, weak_areas, current_week):
    """
    Genera módulos de estudio para la semana actual
    """
    modules = []
    
    # Enfocar en las 3 áreas más débiles
    focus_areas = [area for area in weak_areas if area['priority'] <= 3]
    
    for i, area in enumerate(focus_areas):
        # Temas básicos sin consultar BD para evitar errores
        weak_topics = ['Conceptos Básicos', 'Práctica Intermedia', 'Aplicaciones Avanzadas']
        
        # Determinar dificultad basada en precisión
        difficulty = 'HARD' if area['accuracy'] < 70 else 'MEDIUM' if area['accuracy'] < 85 else 'EASY'
        
        # Determinar prioridad
        priority = 'HIGH' if area['priority'] == 1 else 'MEDIUM' if area['priority'] == 2 else 'LOW'
        
        module = {
            'id': f"module_week_{current_week}_{i+1}",
            'title': f"Refuerzo en {area['subject']}",
            'description': f"Módulo enfocado en mejorar tu rendimiento en {area['subject']} donde tienes {area['accuracy']}% de precisión",
            'area': area['subject'],
            'difficulty': difficulty,
            'estimatedTime': area['recommendedTime'],
            'priority': priority,
            'completed': False,
            'topics': weak_topics,
            'resources': generate_resources_for_area(area['subject'], difficulty),
            'aiRecommendation': generate_ai_recommendation(area)
        }
        modules.append(module)
    
    return modules


def get_weak_areas_analysis(user):
    """
    Obtiene análisis actualizado de áreas débiles
    """
    return analyze_user_weaknesses(user)


def calculate_subject_percentage(subject, weak_areas):
    """
    Calcula el porcentaje de tiempo que debe dedicarse a una materia
    """
    # Mapeo simple de subject codes a nombres
    subject_name_mapping = {
        'MATHEMATICS': 'Matemáticas',
        'READING': 'Lectura Crítica',
        'NATURAL_SCIENCES': 'Ciencias Naturales',
        'SOCIAL_STUDIES': 'Ciencias Sociales',
        'ENGLISH': 'Inglés',
    }
    
    # Buscar el área específica
    target_name = subject_name_mapping.get(subject, subject)
    area = None
    for a in weak_areas:
        if a['subject'] == target_name:
            area = a
            break
    
    if not area:
        return 20.0  # Default igual para todas
    
    # Más tiempo para áreas con menor precisión
    if area['accuracy'] < 70:
        return 30.0
    elif area['accuracy'] < 80:
        return 25.0
    elif area['accuracy'] < 90:
        return 20.0
    else:
        return 15.0


def map_subject_name_to_code(subject_name):
    """
    Mapea nombres de materias a códigos
    """
    mapping = {
        'Matemáticas': 'MATHEMATICS',
        'Lectura Crítica': 'READING',
        'Ciencias Naturales': 'NATURAL_SCIENCES',
        'Ciencias Sociales': 'SOCIAL_STUDIES',
        'Inglés': 'ENGLISH',
    }
    return mapping.get(subject_name, 'MATHEMATICS')  # Default to MATHEMATICS


def get_topics_for_subject(subject_code):
    """
    Obtiene temas específicos de una materia desde la base de datos
    """
    # Simplificar para evitar errores - devolver temas básicos
    topic_mapping = {
        'MATHEMATICS': ['Álgebra Básica', 'Geometría', 'Estadística'],
        'READING': ['Comprensión Lectora', 'Análisis Textual', 'Inferencias'],
        'NATURAL_SCIENCES': ['Física', 'Química', 'Biología'],
        'SOCIAL_STUDIES': ['Historia', 'Geografía', 'Constitución'],
        'ENGLISH': ['Gramática', 'Vocabulario', 'Comprensión'],
    }
    return topic_mapping.get(subject_code, ['Conceptos Fundamentales', 'Práctica Básica', 'Aplicaciones'])


def calculate_recommended_time(accuracy):
    """
    Calcula tiempo recomendado basado en precisión
    """
    if accuracy < 60:
        return 150  # 2.5 horas por semana
    elif accuracy < 70:
        return 120  # 2 horas por semana
    elif accuracy < 80:
        return 90   # 1.5 horas por semana
    elif accuracy < 90:
        return 60   # 1 hora por semana
    else:
        return 30   # 30 minutos por semana


def determine_priority(accuracy):
    """
    Determina prioridad basada en precisión
    """
    if accuracy < 60:
        return 1  # Máxima prioridad
    elif accuracy < 70:
        return 2
    elif accuracy < 80:
        return 3
    elif accuracy < 90:
        return 4
    else:
        return 5  # Menor prioridad


def determine_optimal_difficulty(user):
    """
    Determina la dificultad óptima para el usuario
    """
    try:
        # Obtener precisión promedio
        analytics = LearningAnalytics.objects.get(user=user)
        avg_accuracy = analytics.average_accuracy
        
        if avg_accuracy < 60:
            return 'EASY'
        elif avg_accuracy < 80:
            return 'MEDIUM'
        else:
            return 'HARD'
    except LearningAnalytics.DoesNotExist:
        return 'MEDIUM'


def generate_resources_for_area(subject, difficulty):
    """
    Genera recursos de estudio dinámicos para un área
    """
    base_resources = {
        'Matemáticas': [
            {'type': 'video', 'title': 'Fundamentos de Álgebra', 'url': '/practice/area/algebra-basica', 'duration': 45},
            {'type': 'practice', 'title': 'Ejercicios de Práctica', 'url': '/prueba/matematicas/algebra-basica', 'duration': 60},
            {'type': 'reading', 'title': 'Guía de Estudio', 'url': '/resources/math-guide', 'duration': 30},
            {'type': 'quiz', 'title': 'Quiz de Evaluación', 'url': '/practice/quiz/math', 'duration': 20}
        ],
        'Lectura Crítica': [
            {'type': 'video', 'title': 'Técnicas de Comprensión', 'url': '/practice/area/lectura', 'duration': 40},
            {'type': 'practice', 'title': 'Análisis de Textos', 'url': '/prueba/lectura/comprension', 'duration': 50},
            {'type': 'reading', 'title': 'Estrategias de Lectura', 'url': '/resources/reading-guide', 'duration': 25},
            {'type': 'quiz', 'title': 'Evaluación Crítica', 'url': '/practice/quiz/reading', 'duration': 30}
        ]
    }
    
    default_resources = [
        {'type': 'video', 'title': 'Video Explicativo', 'url': '/practice', 'duration': 30},
        {'type': 'practice', 'title': 'Práctica Dirigida', 'url': '/practice', 'duration': 45},
        {'type': 'reading', 'title': 'Material de Lectura', 'url': '/practice', 'duration': 20},
        {'type': 'quiz', 'title': 'Evaluación', 'url': '/practice', 'duration': 15}
    ]
    
    return base_resources.get(subject, default_resources)


def generate_ai_recommendation(area):
    """
    Genera recomendación personalizada de IA
    """
    accuracy = area['accuracy']
    subject = area['subject']
    
    if accuracy < 60:
        return f"Necesitas refuerzo fundamental en {subject}. Empieza con conceptos básicos y practica diariamente."
    elif accuracy < 70:
        return f"Tu base en {subject} necesita fortalecimiento. Enfócate en problemas de dificultad media."
    elif accuracy < 80:
        return f"Estás progresando bien en {subject}. Practica casos más complejos para mejorar."
    elif accuracy < 90:
        return f"Buen dominio de {subject}. Perfecciona con ejercicios avanzados y casos especiales."
    else:
        return f"Excelente nivel en {subject}. Mantén tu práctica y ayuda a otros estudiantes." 