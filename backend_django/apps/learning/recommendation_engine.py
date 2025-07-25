"""
Motor de Recomendaciones Inteligente para Learning Paths
ACTUALIZADO: Usa templates YAML configurables
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from .models import (
    LearningPath, LearningPathUnit, LearningPathLesson, 
    UserPathEnrollment, UserLessonProgress
)
from apps.icfes.models import (
    ICFESResult, RespuestaUsuarioICFES, PreguntaICFES
)

class LearningRecommendationEngine:
    """
    Motor de recomendaciones que analiza resultados de quiz ICFES
    y genera planes de aprendizaje personalizados usando templates YAML
    """
    
    def __init__(self):
        """Inicializar motor con templates YAML"""
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict:
        """Cargar templates YAML desde archivo de configuración"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'learning_path_templates.yml'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                templates = yaml.safe_load(file)
                print(f"✅ Templates cargados exitosamente desde {config_path}")
                return templates
        except FileNotFoundError:
            print(f"⚠️ Archivo de templates no encontrado: {config_path}")
            # Fallback con templates básicos
            return self._get_fallback_templates()
        except Exception as e:
            print(f"❌ Error cargando templates: {str(e)}")
            return self._get_fallback_templates()
    
    def _get_fallback_templates(self) -> Dict:
        """Templates de respaldo si no se puede cargar el YAML"""
        return {
            'basic_mathematics_path': {
                'metadata': {
                    'name': 'Plan Básico de Matemáticas ICFES',
                    'description': 'Fortalece los fundamentos matemáticos',
                    'difficulty': 'BASICO',
                    'estimated_hours': 40,
                    'weekly_hours': 6,
                    'target_score_range': [0, 45]
                }
            }
        }
    
    def analyze_quiz_results(self, user: User, session_id: str = None) -> Dict:
        """
        Analizar resultados del quiz ICFES del usuario
        ACTUALIZADO: Mejor análisis y selección de template
        """
        try:
            print(f"🔍 Analizando resultados para usuario: {user.username}")
            
            # Obtener resultado más reciente si no se especifica sesión
            if session_id:
                icfes_result = ICFESResult.objects.filter(
                    user=user,
                    session__uuid=session_id
                ).first()
            else:
                icfes_result = ICFESResult.objects.filter(
                    user=user
                ).order_by('-created_at').first()
            
            if not icfes_result:
                print(f"⚠️ No se encontraron resultados ICFES para {user.username}")
                return None
                
            print(f"📊 Resultado encontrado: {icfes_result.mathematics_score}/100")
            
            # Obtener respuestas detalladas
            respuestas = RespuestaUsuarioICFES.objects.filter(
                user=user,
                session_id=str(icfes_result.session.uuid)
            ).select_related('pregunta', 'pregunta__area_tematica')
            
            print(f"📝 Analizando {respuestas.count()} respuestas")
            
            # Análisis por áreas temáticas
            area_analysis = self._analyze_by_areas(respuestas)
            
            # Análisis por dificultad
            difficulty_analysis = self._analyze_by_difficulty_corrected(user, respuestas)
            
            # Seleccionar template apropiado
            selected_template = self._select_template_by_score(icfes_result.mathematics_score)
            
            analysis = {
                'user': user.username,
                'session_id': session_id or str(icfes_result.session.uuid),
                'global_score': icfes_result.mathematics_score,
                'selected_template': selected_template,
                'area_analysis': area_analysis,
                'difficulty_analysis': difficulty_analysis,
                'recommendations': self._generate_recommendations(area_analysis, icfes_result.mathematics_score),
                'weak_areas': self._identify_weak_areas(area_analysis),
                'study_plan_type': self._determine_study_plan_type(icfes_result.mathematics_score, area_analysis)
            }
            
            print(f"✅ Análisis completado. Template seleccionado: {selected_template}")
            return analysis
            
        except Exception as e:
            print(f"❌ Error en analyze_quiz_results: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def _select_template_by_score(self, score: int) -> str:
        """Seleccionar template basado en el puntaje"""
        if 'assignment_rules' in self.templates:
            for rule in self.templates['assignment_rules']['score_based']:
                min_score, max_score = rule['range']
                if min_score <= score <= max_score:
                    return rule['template']
        
        # Fallback basado en score
        if score <= 45:
            return 'basic_mathematics_path'
        elif score <= 70:
            return 'intermediate_mathematics_path'
        else:
            return 'advanced_mathematics_path'
    
    def _analyze_by_areas(self, respuestas) -> Dict:
        """Analizar rendimiento por áreas temáticas"""
        area_stats = {}
        
        for respuesta in respuestas:
            if respuesta.pregunta.area_tematica:
                area_name = respuesta.pregunta.area_tematica.nombre
                if area_name not in area_stats:
                    area_stats[area_name] = {'total': 0, 'correct': 0}
                
                area_stats[area_name]['total'] += 1
                if respuesta.es_correcta:
                    area_stats[area_name]['correct'] += 1
        
        # Calcular porcentajes y clasificar
        area_analysis = {}
        for area, stats in area_stats.items():
            if stats['total'] > 0:
                percentage = (stats['correct'] / stats['total']) * 100
                area_analysis[area] = {
                    'score': round(percentage, 1),
                    'total_questions': stats['total'],
                    'correct_answers': stats['correct'],
                    'status': self._get_area_status(percentage)
                }
        
        return area_analysis
    
    def _analyze_by_difficulty_corrected(self, user: User, respuestas) -> Dict:
        """Analizar rendimiento por nivel de dificultad - CORREGIDO"""
        difficulty_stats = {}
        
        for respuesta in respuestas:
            if hasattr(respuesta.pregunta, 'dificultad') and respuesta.pregunta.dificultad:
                difficulty = respuesta.pregunta.dificultad
                if difficulty not in difficulty_stats:
                    difficulty_stats[difficulty] = {'total': 0, 'correct': 0}
                
                difficulty_stats[difficulty]['total'] += 1
                if respuesta.es_correcta:
                    difficulty_stats[difficulty]['correct'] += 1
        
        # Calcular porcentajes
        difficulty_analysis = {}
        for difficulty, stats in difficulty_stats.items():
            if stats['total'] > 0:
                percentage = (stats['correct'] / stats['total']) * 100
                difficulty_analysis[difficulty] = {
                    'score': round(percentage, 1),
                    'total_questions': stats['total'],
                    'correct_answers': stats['correct']
                }
        
        return difficulty_analysis
    
    def _get_area_status(self, percentage: float) -> str:
        """Determinar status del área basado en porcentaje"""
        if percentage >= 80:
            return 'excelente'
        elif percentage >= 60:
            return 'bueno'
        elif percentage >= 40:
            return 'regular'
        else:
            return 'necesita_refuerzo'
    
    def _identify_weak_areas(self, area_analysis: Dict) -> List[str]:
        """Identificar áreas que necesitan refuerzo"""
        weak_areas = []
        for area, stats in area_analysis.items():
            if stats['score'] < 60:  # Menos del 60% se considera débil
                weak_areas.append(area)
        return weak_areas
    
    def _determine_study_plan_type(self, score: int, area_analysis: Dict) -> str:
        """Determinar tipo de plan de estudio"""
        weak_areas_count = len(self._identify_weak_areas(area_analysis))
        
        if score <= 45 or weak_areas_count >= 4:
            return 'intensive_basic'
        elif score <= 70 or weak_areas_count >= 2:
            return 'focused_improvement'
        else:
            return 'advanced_mastery'
    
    def _generate_recommendations(self, area_analysis: Dict, global_score: int) -> List[Dict]:
        """Generar recomendaciones específicas"""
        recommendations = []
        
        # Recomendaciones basadas en áreas débiles
        weak_areas = self._identify_weak_areas(area_analysis)
        
        for area in weak_areas:
            recommendations.append({
                'type': 'area_focus',
                'area': area,
                'priority': 'high' if area_analysis[area]['score'] < 40 else 'medium',
                'description': f"Reforzar conocimientos en {area}",
                'estimated_time': '2-3 horas semanales'
            })
        
        # Recomendación de plan general
        if global_score <= 45:
            recommendations.append({
                'type': 'study_plan',
                'plan': 'basic',
                'description': 'Plan básico con fundamentos sólidos',
                'estimated_duration': '6-8 semanas'
            })
        elif global_score <= 70:
            recommendations.append({
                'type': 'study_plan',
                'plan': 'intermediate',
                'description': 'Plan intermedio para mejorar áreas específicas',
                'estimated_duration': '4-6 semanas'
            })
        else:
            recommendations.append({
                'type': 'study_plan',
                'plan': 'advanced',
                'description': 'Plan avanzado para perfeccionar habilidades',
                'estimated_duration': '3-4 semanas'
            })
        
        return recommendations
    
    def generate_personalized_path(self, user: User, analysis: Dict) -> LearningPath:
        """
        Generar plan de aprendizaje personalizado usando templates YAML
        ACTUALIZADO: Verifica si ya existe un path activo y evita duplicados
        """
        try:
            print(f"🎯 Generando plan personalizado para {user.username}")
            
            # VERIFICAR SI YA EXISTE UN PATH ACTIVO
            existing_enrollment = UserPathEnrollment.objects.filter(
                user=user,
                status='ACTIVE'
            ).first()
            
            if existing_enrollment:
                print(f"✅ Usuario ya tiene un path activo: {existing_enrollment.learning_path.name}")
                return existing_enrollment.learning_path
            
            # Seleccionar template
            template_name = analysis.get('selected_template', 'basic_mathematics_path')
            template = self.templates.get(template_name)
            
            if not template:
                print(f"⚠️ Template {template_name} no encontrado, usando básico")
                template = self.templates['basic_mathematics_path']
            
            metadata = template['metadata']
            print(f"📋 Usando template: {metadata['name']}")
            
            # GENERAR NOMBRE Y SLUG ÚNICOS
            base_name = f"{metadata['name']} - {user.first_name or user.username}"
            unique_name = base_name
            counter = 1
            
            # Verificar si ya existe un learning path con este nombre
            while LearningPath.objects.filter(name=unique_name).exists():
                unique_name = f"{base_name} (V{counter})"
                counter += 1
                print(f"📝 Generando nombre único: {unique_name}")
            
            # Crear LearningPath con nombre único
            learning_path = LearningPath.objects.create(
                name=unique_name,
                description=metadata['description'],
                path_type='PERSONALIZED',
                difficulty_level=metadata['difficulty'],
                estimated_duration_hours=metadata['estimated_hours'],
                recommended_weekly_hours=metadata['weekly_hours'],
                target_icfes_areas=analysis.get('weak_areas', []),
                adaptive_sequencing_enabled=True,
                personalized_feedback_enabled=True,
                created_by=user
            )
            
            print(f"✅ LearningPath creado con ID: {learning_path.id}")
            
            # Crear unidades desde template
            self._create_units_from_template(learning_path, template, analysis)
            
            # Crear inscripción automática
            enrollment = UserPathEnrollment.objects.create(
                user=user,
                learning_path=learning_path,
                status='ACTIVE',
                daily_goal_minutes=metadata.get('weekly_hours', 5) * 60 // 7,  # Distribuir horas semanales
                adaptive_difficulty_enabled=True
            )
            
            print(f"✅ Plan creado exitosamente: {learning_path.name}")
            return learning_path
            
        except Exception as e:
            print(f"❌ Error en generate_personalized_path: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise e
    
    def _create_units_from_template(self, learning_path: LearningPath, template: Dict, analysis: Dict):
        """Crear unidades basadas en template YAML - MEJORADO CON PERSONALIZACIÓN COMPLETA"""
        units_config = template.get('units', [])
        template_metadata = template.get('metadata', {})
        template_criteria_raw = template.get('criteria', {})
        
        # ✅ ARREGLAR: Manejar criteria como lista o diccionario
        template_criteria = {}
        if isinstance(template_criteria_raw, list):
            # Si criteria es una lista, convertir a diccionario
            for item in template_criteria_raw:
                if isinstance(item, dict):
                    template_criteria.update(item)
        elif isinstance(template_criteria_raw, dict):
            template_criteria = template_criteria_raw
        
        for unit_config in units_config:
            # ✅ MAPEO COMPLETO DE CAMPOS YAML → BD
            unit = LearningPathUnit.objects.create(
                learning_path=learning_path,
                
                # Campos básicos (ya funcionaban)
                title=unit_config['title'],
                description=unit_config['description'],
                order=unit_config['id'],
                estimated_duration_minutes=unit_config.get('estimated_duration', 240),
                xp_reward=unit_config.get('xp_reward', 100),
                
                # ✅ NUEVOS CAMPOS PERSONALIZADOS
                icon_emoji=unit_config.get('icon', template_metadata.get('icon', '📖')),
                unit_type=unit_config.get('unit_type', 'CORE'),
                difficulty_modifier=unit_config.get('difficulty_modifier', self._get_difficulty_modifier(template_metadata.get('difficulty', 'MEDIO'))),
                
                # ✅ METADATOS ENRIQUECIDOS
                metadata={
                    'template_name': learning_path.name.split(' - ')[0],  # Nombre del template
                    'focus_topics': unit_config.get('topics', []),
                    'learning_style': template_criteria.get('learning_style', 'balanced'),
                    'practice_intensity': template_criteria.get('practice_intensity', 'medium'),
                    'color_theme': template_metadata.get('color_theme', '#3B82F6'),
                    'difficulty_level': template_metadata.get('difficulty', 'MEDIO'),
                    'target_score_range': template_metadata.get('target_score_range', [0, 100]),
                    'estimated_duration_original': unit_config.get('estimated_duration', 240),
                    'weak_areas_focus': analysis.get('weak_areas', [])
                },
                
                # ✅ CONFIGURACIÓN ADAPTATIVA
                learning_objectives=unit_config.get('topics', []),
                unlock_criteria=self._generate_unlock_criteria(unit_config, template_metadata)
            )
            
            # ✅ CREAR LECCIONES ADAPTATIVAS
            lessons_config = unit_config.get('lessons', [])
            if lessons_config:
                self._create_lessons_from_yaml(unit, lessons_config, template_metadata, analysis)
            else:
                self._create_adaptive_lessons(unit, unit_config.get('topics', []), template_metadata, analysis)
                
    def _get_difficulty_modifier(self, difficulty_level: str) -> float:
        """Obtener modificador de dificultad basado en el nivel del template"""
        modifiers = {
            'BASICO': 0.8,      # 20% más fácil
            'BASIC': 0.8,
            'MEDIO': 1.0,       # Dificultad estándar
            'INTERMEDIATE': 1.0,
            'AVANZADO': 1.3,    # 30% más difícil
            'ADVANCED': 1.3,
            'EXPERT': 1.5       # 50% más difícil
        }
        return modifiers.get(difficulty_level.upper(), 1.0)
    
    def _generate_unlock_criteria(self, unit_config: Dict, template_metadata: Dict) -> Dict:
        """Generar criterios de desbloqueo basados en template y configuración"""
        base_criteria = {
            'previous_unit_completion': True,
            'min_score_percentage': 70,
            'hearts_required': 1
        }
        
        # Ajustar según dificultad
        difficulty = template_metadata.get('difficulty', 'MEDIO')
        if difficulty == 'BASICO':
            base_criteria['min_score_percentage'] = 60  # Más permisivo
        elif difficulty == 'AVANZADO':
            base_criteria['min_score_percentage'] = 80  # Más estricto
            base_criteria['hearts_required'] = 2
            
        return base_criteria
    
    def _create_lessons_from_yaml(self, unit: LearningPathUnit, lessons_config: List[Dict], template_metadata: Dict, analysis: Dict):
        """Crear lecciones desde configuración YAML con personalización"""
        for idx, lesson_config in enumerate(lessons_config):
            lesson_type = self._map_lesson_type(lesson_config.get('type', 'CONCEPT'))
            
            # ✅ PERSONALIZACIÓN POR TEMPLATE
            duration = lesson_config.get('duration', 25)
            if template_metadata.get('difficulty') == 'BASICO':
                duration = int(duration * 1.2)  # 20% más tiempo para básico
            elif template_metadata.get('difficulty') == 'AVANZADO':
                duration = int(duration * 0.8)  # 20% menos tiempo para avanzado
            
            LearningPathLesson.objects.create(
                path_unit=unit,
                title=lesson_config['title'],
                lesson_type=lesson_type,
                order=idx + 1,
                metadata={
                    'original_duration': lesson_config.get('duration', 25),
                    'adjusted_duration': duration,
                    'content_url': lesson_config.get('content_url', ''),
                    'questions_count': lesson_config.get('questions_count', 10),
                    'difficulty_level': template_metadata.get('difficulty', 'MEDIO'),
                    'focus_areas': analysis.get('weak_areas', [])
                }
            )
    
    def _create_adaptive_lessons(self, unit: LearningPathUnit, topics: List[str], template_metadata: Dict, analysis: Dict):
        """Crear lecciones adaptativas basadas en el análisis del usuario y template"""
        difficulty = template_metadata.get('difficulty', 'MEDIO')
        weak_areas = analysis.get('weak_areas', [])
        
        # ✅ TIPOS DE LECCIÓN SEGÚN TEMPLATE
        if difficulty == 'BASICO':
            lesson_pattern = ['CONCEPT', 'PRACTICE', 'PRACTICE', 'QUIZ']  # Más práctica
        elif difficulty == 'AVANZADO':
            lesson_pattern = ['CONCEPT', 'CHALLENGE', 'QUIZ', 'STORY']   # Más desafío
        else:
            lesson_pattern = ['CONCEPT', 'PRACTICE', 'QUIZ', 'CHALLENGE'] # Balanceado
        
        for idx, topic in enumerate(topics[:4]):  # Máximo 4 lecciones por unidad
            lesson_type = lesson_pattern[idx % len(lesson_pattern)]
            
            # ✅ AJUSTAR DURACIÓN POR DIFICULTAD
            base_duration = 25
            if difficulty == 'BASICO':
                duration = int(base_duration * 1.3)  # Más tiempo
            elif difficulty == 'AVANZADO':
                duration = int(base_duration * 0.7)  # Menos tiempo
            else:
                duration = base_duration
            
            # ✅ ENFOQUE ESPECIAL EN ÁREAS DÉBILES
            is_weak_area = any(weak_area.lower() in topic.lower() for weak_area in weak_areas)
            if is_weak_area and lesson_type == 'PRACTICE':
                lesson_type = 'PRACTICE'  # Doble práctica para áreas débiles
                duration = int(duration * 1.2)
            
            LearningPathLesson.objects.create(
                path_unit=unit,
                title=f"Lección {idx + 1}: {topic}",
                lesson_type=lesson_type,
                order=idx + 1,
                metadata={
                    'topic': topic,
                    'duration_minutes': duration,
                    'difficulty_level': difficulty,
                    'is_weak_area_focus': is_weak_area,
                    'template_origin': template_metadata.get('name', 'Unknown'),
                    'adaptive_adjustments': {
                        'duration_multiplier': duration / base_duration,
                        'extra_practice': is_weak_area,
                        'difficulty_modifier': unit.difficulty_modifier
                    }
                }
            )
    
    def _map_lesson_type(self, yaml_type: str) -> str:
        """Mapear tipos de lección de YAML a tipos válidos del modelo"""
        mapping = {
            'VIDEO': 'CONCEPT',
            'PRACTICE': 'PRACTICE', 
            'INTERACTIVE': 'CONCEPT',
            'ASSESSMENT': 'QUIZ',
            'GUIDED_PRACTICE': 'PRACTICE'
        }
        return mapping.get(yaml_type, 'CONCEPT')
    
    def _create_default_lessons(self, unit: LearningPathUnit, topics: List[str]):
        """Crear lecciones por defecto basadas en topics"""
        lesson_types = ['CONCEPT', 'PRACTICE', 'QUIZ', 'CHALLENGE']
        
        for idx, topic in enumerate(topics[:4]):  # Máximo 4 lecciones por unidad
            lesson_type = lesson_types[idx % len(lesson_types)]
            
            LearningPathLesson.objects.create(
                path_unit=unit,  # Campo correcto es path_unit
                title=f"Lección {idx + 1}: {topic}",
                lesson_type=lesson_type,
                order=idx + 1
            )
    
    def get_template_by_name(self, template_name: str) -> Dict:
        """Obtener template específico por nombre"""
        return self.templates.get(template_name, {})
    
    def get_ui_configuration(self, template_name: str) -> Dict:
        """Obtener configuración de UI para un template"""
        ui_config = self.templates.get('ui_configuration', {})
        
        # Mapear template a configuración UI
        template_ui_mapping = {
            'basic_mathematics_path': 'basic',
            'intermediate_mathematics_path': 'intermediate', 
            'advanced_mathematics_path': 'advanced'
        }
        
        ui_type = template_ui_mapping.get(template_name, 'basic')
        return ui_config.get('card_styles', {}).get(ui_type, {})
    
    def get_available_templates(self) -> List[Dict]:
        """Obtener lista de templates disponibles"""
        templates = []
        
        for template_name, template_data in self.templates.items():
            if template_name.endswith('_path') and 'metadata' in template_data:
                templates.append({
                    'name': template_name,
                    'display_name': template_data['metadata']['name'],
                    'description': template_data['metadata']['description'],
                    'difficulty': template_data['metadata']['difficulty'],
                    'estimated_hours': template_data['metadata']['estimated_hours'],
                    'target_score_range': template_data['metadata']['target_score_range']
                })
        
        return templates
    
    def get_personalization_config(self, template_name: str, analysis: Dict = None) -> Dict:
        """
        Obtener configuración completa de personalización para un template
        NUEVA FUNCIÓN: Para uso del frontend
        """
        template = self.get_template_by_name(template_name)
        if not template:
            return {}
            
        metadata = template.get('metadata', {})
        criteria = template.get('criteria', {})
        ui_config = self.get_ui_configuration(template_name)
        
        # Configuración visual personalizada
        personalization = {
            'visual': {
                'primary_color': metadata.get('color_theme', '#3B82F6'),
                'icon': metadata.get('icon', '📖'),
                'difficulty_label': metadata.get('difficulty', 'MEDIO'),
                'background_gradient': ui_config.get('background', 'gradient-to-br from-blue-500 to-purple-600'),
                'button_style': ui_config.get('button_style', 'bg-blue-600 hover:bg-blue-700'),
                'progress_color': ui_config.get('progress_color', 'bg-blue-400')
            },
            'learning': {
                'style': criteria.get('learning_style', 'balanced'),
                'intensity': criteria.get('practice_intensity', 'medium'),
                'focus_areas': criteria.get('focus_topics', []),
                'estimated_hours': metadata.get('estimated_hours', 40),
                'weekly_hours': metadata.get('weekly_hours', 5)
            },
            'difficulty': {
                'level': metadata.get('difficulty', 'MEDIO'),
                'modifier': self._get_difficulty_modifier(metadata.get('difficulty', 'MEDIO')),
                'target_score_range': metadata.get('target_score_range', [0, 100])
            },
            'adaptive': {
                'weak_areas': analysis.get('weak_areas', []) if analysis else [],
                'user_score': analysis.get('global_score', 0) if analysis else 0,
                'personalized_message': self._generate_personalized_message(template_name, analysis)
            }
        }
        
        return personalization
    
    def _generate_personalized_message(self, template_name: str, analysis: Dict = None) -> str:
        """Generar mensaje personalizado basado en template y análisis"""
        if not analysis:
            # Mensajes por defecto sin análisis
            messages = {
                'basic_mathematics_path': "Construyamos juntos bases sólidas en matemáticas",
                'intermediate_mathematics_path': "Perfeccionemos tus habilidades matemáticas existentes", 
                'advanced_mathematics_path': "Llevemos tu dominio matemático al siguiente nivel"
            }
            return messages.get(template_name, "Comencemos tu viaje de aprendizaje personalizado")
        
        # Mensajes personalizados con análisis
        score = analysis.get('global_score', 0)
        weak_areas = analysis.get('weak_areas', [])
        
        if template_name == 'basic_mathematics_path':
            if weak_areas:
                return f"Fortaleceremos especialmente {', '.join(weak_areas[:2])} paso a paso"
            return f"Con tu puntaje de {score}, construiremos fundamentos sólidos desde cero"
            
        elif template_name == 'intermediate_mathematics_path':
            if weak_areas:
                return f"Mejoraremos {', '.join(weak_areas[:2])} mientras consolidamos tus fortalezas"
            return f"Con tu puntaje de {score}, perfeccionaremos técnicas intermedias"
            
        elif template_name == 'advanced_mathematics_path':
            if weak_areas:
                return f"Dominaremos {', '.join(weak_areas[:2])} con estrategias avanzadas"
            return f"¡Excelente puntaje de {score}! Alcancemos la maestría matemática"
            
        return "Plan personalizado basado en tu perfil único" 