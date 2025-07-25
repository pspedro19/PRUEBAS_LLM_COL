"""
Motor de Análisis Inteligente para Asistente IA
Analiza datos del usuario y genera recomendaciones personalizadas
"""

from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
import statistics
import math

class UserAnalysisEngine:
    """Motor de análisis inteligente para generar recomendaciones personalizadas"""
    
    def __init__(self, user):
        self.user = user
        self.profile = getattr(user, 'profile', None)
        self.analysis_result = {}
        
    def analyze_complete_profile(self):
        """Análisis completo del perfil del usuario"""
        analysis = {
            'user_stats': self._get_user_stats(),
            'performance_analysis': self._analyze_performance(),
            'learning_patterns': self._analyze_learning_patterns(),
            'recommendations': self._generate_recommendations(),
            'required_tasks': self._identify_missing_data(),
            'strengths_weaknesses': self._identify_strengths_weaknesses(),
            'predictions': self._generate_predictions()
        }
        
        self.analysis_result = analysis
        return analysis
    
    def _get_user_stats(self):
        """Estadísticas básicas del usuario"""
        try:
            from apps.analytics.models import LearningAnalytics, SubjectAnalytics
            from apps.icfes.models import ICFESResult
            
            # Obtener learning analytics
            learning_analytics = getattr(self.user, 'learning_analytics', None)
            
            # Obtener último resultado ICFES
            latest_icfes = ICFESResult.objects.filter(user=self.user).order_by('-created_at').first()
            
            # Calcular precisión general
            accuracy = 0
            if self.profile and self.profile.total_questions_answered > 0:
                accuracy = (self.profile.total_correct_answers / self.profile.total_questions_answered) * 100
            
            # Obtener estadísticas por materia
            subject_stats = SubjectAnalytics.objects.filter(user=self.user)
            
            stats = {
                'level': self.user.level,
                'hero_class': self.user.get_hero_class_display(),
                'total_questions_answered': self.profile.total_questions_answered if self.profile else 0,
                'accuracy': round(accuracy, 1),
                'study_time': self.profile.total_study_minutes if self.profile else 0,
                'streak': self.profile.current_streak if self.profile else 0,
                'max_streak': self.profile.max_streak if self.profile else 0,
                'predicted_score': latest_icfes.global_score if latest_icfes else 0,
                'experience_points': self.user.experience_points,
                'vitality': self.profile.current_vitality if self.profile else 100,
                'improvement_rate': self.profile.improvement_rate if self.profile else 0,
                'subject_performance': self._get_subject_performance(subject_stats)
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return self._get_fallback_stats()
    
    def _get_subject_performance(self, subject_stats):
        """Performance por materia"""
        performance = {}
        for stat in subject_stats:
            performance[stat.subject.lower()] = {
                'accuracy': stat.accuracy_percentage,
                'questions_answered': stat.questions_answered,
                'improvement_rate': stat.improvement_rate,
                'weak_topics': stat.weakest_topics[:3] if stat.weakest_topics else [],
                'strong_topics': stat.strongest_topics[:3] if stat.strongest_topics else []
            }
        return performance
    
    def _analyze_performance(self):
        """Análisis detallado del rendimiento"""
        try:
            from apps.icfes.models import ICFESResult, RespuestaUsuarioICFES
            from apps.questions.models import UserQuestionResponse
            
            # Obtener resultados recientes
            recent_results = ICFESResult.objects.filter(
                user=self.user
            ).order_by('-created_at')[:5]
            
            # Obtener respuestas recientes
            recent_responses = UserQuestionResponse.objects.filter(
                user=self.user,
                created_at__gte=timezone.now() - timedelta(days=30)
            )
            
            analysis = {
                'recent_performance_trend': self._calculate_trend(recent_results),
                'response_time_analysis': self._analyze_response_times(recent_responses),
                'difficulty_performance': self._analyze_by_difficulty(recent_responses),
                'time_patterns': self._analyze_time_patterns(recent_responses),
                'consistency_score': self._calculate_consistency(recent_results)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error in performance analysis: {e}")
            return {}
    
    def _analyze_learning_patterns(self):
        """Análisis de patrones de aprendizaje"""
        try:
            from apps.analytics.models import UserEvent, SessionAnalytics
            
            # Obtener eventos recientes
            recent_events = UserEvent.objects.filter(
                user=self.user,
                timestamp__gte=timezone.now() - timedelta(days=30)
            )
            
            # Obtener sesiones de estudio
            study_sessions = SessionAnalytics.objects.filter(
                user=self.user,
                started_at__gte=timezone.now() - timedelta(days=30)
            )
            
            patterns = {
                'study_frequency': self._calculate_study_frequency(study_sessions),
                'preferred_study_times': self._find_preferred_times(recent_events),
                'session_duration_preference': self._analyze_session_durations(study_sessions),
                'learning_style': self._detect_learning_style(),
                'engagement_level': self._calculate_engagement(recent_events)
            }
            
            return patterns
            
        except Exception as e:
            print(f"Error in learning patterns analysis: {e}")
            return {}
    
    def _identify_strengths_weaknesses(self):
        """Identifica fortalezas y debilidades específicas"""
        try:
            from apps.analytics.models import SubjectAnalytics
            
            subject_analytics = SubjectAnalytics.objects.filter(user=self.user)
            
            strengths = []
            weaknesses = []
            
            for subject in subject_analytics:
                if subject.accuracy_percentage >= 80:
                    strengths.extend(subject.strongest_topics[:2] if subject.strongest_topics else [])
                elif subject.accuracy_percentage <= 60:
                    weaknesses.extend(subject.weakest_topics[:2] if subject.weakest_topics else [])
            
            # Si no hay datos específicos, usar datos generales
            if not strengths and not weaknesses:
                if self.profile and self.profile.total_questions_answered > 0:
                    accuracy = (self.profile.total_correct_answers / self.profile.total_questions_answered) * 100
                    if accuracy >= 75:
                        strengths = ['Resolución general de problemas']
                    elif accuracy <= 60:
                        weaknesses = ['Precisión general', 'Manejo de tiempo']
            
            return {
                'strengths': list(set(strengths))[:5],
                'weaknesses': list(set(weaknesses))[:5]
            }
            
        except Exception as e:
            print(f"Error identifying strengths/weaknesses: {e}")
            return {'strengths': [], 'weaknesses': []}
    
    def _generate_recommendations(self):
        """Genera recomendaciones personalizadas basadas en el análisis"""
        recommendations = []
        
        stats = self._get_user_stats()
        strengths_weaknesses = self._identify_strengths_weaknesses()
        
        # Recomendación basada en precisión
        if stats['accuracy'] < 70:
            recommendations.append({
                'type': 'focus',
                'title': 'Mejorar Precisión',
                'description': f'Tu precisión actual es {stats["accuracy"]}%. Enfócate en revisar conceptos fundamentales.',
                'priority': 'high',
                'estimated_improvement': 15,
                'icon': '🎯'
            })
        
        # Recomendación basada en debilidades
        if strengths_weaknesses['weaknesses']:
            main_weakness = strengths_weaknesses['weaknesses'][0]
            recommendations.append({
                'type': 'focus',
                'title': f'Fortalecer {main_weakness}',
                'description': f'Área identificada con menor rendimiento. Practica ejercicios específicos.',
                'priority': 'high',
                'estimated_improvement': 12,
                'icon': '📚'
            })
        
        # Recomendación basada en tiempo de estudio
        if stats['study_time'] < 300:  # Menos de 5 horas
            recommendations.append({
                'type': 'practice',
                'title': 'Aumentar Tiempo de Estudio',
                'description': 'Incrementa tu tiempo de estudio a al menos 1 hora diaria para mejores resultados.',
                'priority': 'medium',
                'estimated_improvement': 10,
                'icon': '⏰'
            })
        
        # Recomendación basada en racha
        if stats['streak'] < 3:
            recommendations.append({
                'type': 'practice',
                'title': 'Desarrollar Consistencia',
                'description': 'Mantén una racha de estudio diaria para mejorar la retención.',
                'priority': 'medium',
                'estimated_improvement': 8,
                'icon': '🔥'
            })
        
        # Recomendación de manejo de tiempo si la precisión es buena pero el nivel bajo
        if stats['accuracy'] > 75 and stats['level'] < 10:
            recommendations.append({
                'type': 'strategy',
                'title': 'Optimizar Velocidad',
                'description': 'Tu precisión es buena. Enfócate en resolver problemas más rápidamente.',
                'priority': 'medium',
                'estimated_improvement': 8,
                'icon': '⚡'
            })
        
        # Recomendación basada en fortalezas
        if strengths_weaknesses['strengths']:
            main_strength = strengths_weaknesses['strengths'][0]
            recommendations.append({
                'type': 'confidence',
                'title': f'Potenciar {main_strength}',
                'description': f'Excelente rendimiento en esta área. Úsala como base para mejorar otras.',
                'priority': 'low',
                'estimated_improvement': 5,
                'icon': '💪'
            })
        
        return recommendations[:4]  # Máximo 4 recomendaciones
    
    def _identify_missing_data(self):
        """Identifica qué datos faltan para hacer mejores recomendaciones"""
        required_tasks = []
        
        # Si nunca ha hecho evaluación inicial
        if not self.user.initial_assessment_completed:
            required_tasks.append({
                'id': 'initial_assessment',
                'title': 'Evaluación Diagnóstica',
                'description': 'Completa tu evaluación inicial para calibrar el sistema a tu nivel.',
                'type': 'assessment',
                'estimated_time': 20,
                'reward_xp': 200,
                'completed': False
            })
        
        # Si no ha respondido suficientes preguntas
        if self.profile and self.profile.total_questions_answered < 50:
            required_tasks.append({
                'id': 'practice_questions',
                'title': 'Práctica Inicial',
                'description': 'Responde al menos 20 preguntas más para análisis preciso.',
                'type': 'practice',
                'estimated_time': 15,
                'reward_xp': 150,
                'completed': False
            })
        
        # Si no ha completado test vocacional
        if not self.user.vocational_test_completed:
            required_tasks.append({
                'id': 'vocational_test',
                'title': 'Test Vocacional',
                'description': 'Define tu perfil de aprendizaje para recomendaciones personalizadas.',
                'type': 'assessment',
                'estimated_time': 10,
                'reward_xp': 100,
                'completed': False
            })
        
        return required_tasks
    
    def _generate_predictions(self):
        """Genera predicciones basadas en el progreso actual"""
        try:
            from apps.icfes.models import ICFESResult
            
            # Obtener resultados históricos
            historical_results = ICFESResult.objects.filter(
                user=self.user
            ).order_by('created_at')
            
            if len(historical_results) >= 2:
                scores = [result.global_score for result in historical_results]
                improvement_rate = self._calculate_improvement_rate(scores)
                
                return {
                    'projected_score': self._project_future_score(scores, improvement_rate),
                    'improvement_rate': improvement_rate,
                    'confidence_level': self._calculate_confidence(len(historical_results)),
                    'time_to_target': self._estimate_time_to_target(scores)
                }
            
            return {}
            
        except Exception as e:
            print(f"Error generating predictions: {e}")
            return {}
    
    # Métodos auxiliares
    def _calculate_trend(self, results):
        """Calcula tendencia de rendimiento"""
        if len(results) < 2:
            return 'insufficient_data'
        
        scores = [r.global_score for r in results]
        recent_avg = statistics.mean(scores[:3]) if len(scores) >= 3 else scores[0]
        older_avg = statistics.mean(scores[-3:]) if len(scores) >= 3 else scores[-1]
        
        if recent_avg > older_avg * 1.05:
            return 'improving'
        elif recent_avg < older_avg * 0.95:
            return 'declining'
        else:
            return 'stable'
    
    def _analyze_response_times(self, responses):
        """Analiza patrones de tiempo de respuesta"""
        if not responses.exists():
            return {}
        
        times = [r.response_time_seconds for r in responses if r.response_time_seconds]
        
        if not times:
            return {}
        
        return {
            'average_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'consistency': 1 - (statistics.stdev(times) / statistics.mean(times)) if len(times) > 1 else 1
        }
    
    def _analyze_by_difficulty(self, responses):
        """Analiza rendimiento por dificultad"""
        difficulty_stats = {}
        
        for response in responses:
            diff = response.question.difficulty
            if diff not in difficulty_stats:
                difficulty_stats[diff] = {'correct': 0, 'total': 0}
            
            difficulty_stats[diff]['total'] += 1
            if response.is_correct:
                difficulty_stats[diff]['correct'] += 1
        
        for diff in difficulty_stats:
            total = difficulty_stats[diff]['total']
            correct = difficulty_stats[diff]['correct']
            difficulty_stats[diff]['accuracy'] = (correct / total) * 100 if total > 0 else 0
        
        return difficulty_stats
    
    def _get_fallback_stats(self):
        """Estadísticas de fallback cuando no hay datos suficientes"""
        return {
            'level': self.user.level,
            'hero_class': self.user.get_hero_class_display(),
            'total_questions_answered': 0,
            'accuracy': 0,
            'study_time': 0,
            'streak': 0,
            'max_streak': 0,
            'predicted_score': 0,
            'experience_points': self.user.experience_points,
            'vitality': 100,
            'improvement_rate': 0,
            'subject_performance': {}
        }
    
    def _calculate_study_frequency(self, sessions):
        """Calcula frecuencia de estudio"""
        if not sessions.exists():
            return 0
        
        days_with_study = sessions.values('started_at__date').distinct().count()
        total_days = 30  # Últimos 30 días
        
        return (days_with_study / total_days) * 100
    
    def _find_preferred_times(self, events):
        """Encuentra horarios preferidos de estudio"""
        hours = [event.timestamp.hour for event in events]
        
        if not hours:
            return []
        
        # Agrupar por franjas horarias
        morning = sum(1 for h in hours if 6 <= h < 12)
        afternoon = sum(1 for h in hours if 12 <= h < 18)
        evening = sum(1 for h in hours if 18 <= h < 24)
        night = sum(1 for h in hours if 0 <= h < 6)
        
        preferences = [
            ('morning', morning),
            ('afternoon', afternoon),
            ('evening', evening),
            ('night', night)
        ]
        
        return sorted(preferences, key=lambda x: x[1], reverse=True)[:2]
    
    def _detect_learning_style(self):
        """Detecta estilo de aprendizaje predominante"""
        # Por ahora retornamos adaptativo, pero se puede implementar análisis más complejo
        return self.profile.learning_style if self.profile and self.profile.learning_style else 'adaptive'
    
    def _calculate_engagement(self, events):
        """Calcula nivel de engagement"""
        if not events.exists():
            return 0
        
        engagement_events = events.filter(
            event_type__in=['QUESTION_ANSWERED', 'QUIZ_COMPLETED', 'STUDY_SESSION']
        ).count()
        
        total_events = events.count()
        
        return (engagement_events / total_events) * 100 if total_events > 0 else 0
    
    def _calculate_improvement_rate(self, scores):
        """Calcula tasa de mejora"""
        if len(scores) < 2:
            return 0
        
        total_improvement = scores[-1] - scores[0]
        periods = len(scores) - 1
        
        return total_improvement / periods if periods > 0 else 0
    
    def _project_future_score(self, scores, improvement_rate):
        """Proyecta puntaje futuro"""
        current_score = scores[-1] if scores else 0
        projected = current_score + (improvement_rate * 3)  # 3 períodos futuros
        
        return min(max(projected, 0), 500)  # Clamp entre 0 y 500
    
    def _calculate_confidence(self, data_points):
        """Calcula nivel de confianza de las predicciones"""
        if data_points < 3:
            return 0.3
        elif data_points < 5:
            return 0.6
        elif data_points < 10:
            return 0.8
        else:
            return 0.9
    
    def _estimate_time_to_target(self, scores):
        """Estima tiempo para alcanzar objetivo"""
        if not scores or len(scores) < 2:
            return None
        
        current_score = scores[-1]
        target_score = 400  # Puntaje objetivo típico
        improvement_rate = self._calculate_improvement_rate(scores)
        
        if improvement_rate <= 0:
            return None
        
        periods_needed = (target_score - current_score) / improvement_rate
        weeks_needed = max(periods_needed * 2, 0)  # Asumiendo períodos de 2 semanas
        
        return min(weeks_needed, 52)  # Máximo 1 año 