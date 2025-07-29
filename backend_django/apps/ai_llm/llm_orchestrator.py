"""
LLM Orchestrator - Gestión inteligente de modelos de IA
Selecciona automáticamente el modelo correcto según contexto, área y usuario
"""

import asyncio
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from asgiref.sync import sync_to_async
from decimal import Decimal

from .models import (
    AIModel, AIPromptTemplate, AIConversation, AIMessage, 
    AIResponseCache, AIInteractionLog, AIUsageQuota, AIModerationLog,
    AIPerformanceMetric
)

logger = logging.getLogger(__name__)


class LLMOrchestrator:
    """
    Orchestrador principal para gestión inteligente de LLMs
    """
    
    def __init__(self):
        self.model_cache = {}
        self.template_cache = {}
        self._load_model_configurations()
    
    def _load_model_configurations(self):
        """Carga configuraciones predefinidas de modelos por área"""
        self.area_model_config = {
            'matematicas': {
                'primary_model': 'gpt-4',
                'fallback_model': 'gpt-3.5-turbo',
                'special_features': ['code_interpreter', 'mathematical_reasoning'],
                'temperature': 0.1,
                'max_tokens': 1500
            },
            'lectura_critica': {
                'primary_model': 'claude-3-opus',
                'fallback_model': 'gpt-4',
                'special_features': ['text_analysis', 'reading_comprehension'],
                'temperature': 0.3,
                'max_tokens': 1200
            },
            'ciencias_naturales': {
                'primary_model': 'gpt-4',
                'fallback_model': 'gpt-3.5-turbo',
                'special_features': ['scientific_reasoning', 'experimental_analysis'],
                'temperature': 0.2,
                'max_tokens': 1000
            },
            'sociales_ciudadanas': {
                'primary_model': 'claude-3-sonnet',
                'fallback_model': 'gpt-4',
                'special_features': ['social_analysis', 'cultural_context'],
                'temperature': 0.4,
                'max_tokens': 1000
            },
            'ingles': {
                'primary_model': 'gpt-3.5-turbo-fine-tuned',
                'fallback_model': 'gpt-3.5-turbo',
                'special_features': ['language_learning', 'grammar_analysis'],
                'temperature': 0.2,
                'max_tokens': 800
            }
        }
    
    async def generate_explanation(
        self, 
        question_data: Dict[str, Any],
        user_context: Dict[str, Any],
        explanation_type: str = 'explanation'
    ) -> Dict[str, Any]:
        """
        Genera explicación inteligente usando el modelo apropiado
        """
        try:
            # 1. Verificar cuotas del usuario
            if not await self._check_user_quota(user_context['user_id']):
                return self._generate_quota_exceeded_response()
            
            # 2. Determinar área y seleccionar modelo
            area = question_data.get('area', 'general')
            selected_model = await self._select_optimal_model(area, explanation_type, user_context)
            
            # 3. Obtener template apropiado
            template = await self._get_optimal_template(area, explanation_type, user_context)
            
            if not template:
                return self._generate_fallback_response(question_data, user_context)
            
            # 4. Verificar cache
            cache_key = self._generate_cache_key(template.id, question_data, user_context)
            cached_response = await self._get_cached_response(cache_key)
            
            if cached_response and await self._is_cache_valid(cached_response):
                await self._log_interaction(user_context['user_id'], 'cache_hit', template.id)
                return self._format_cached_response(cached_response)
            
            # 5. Generar prompt personalizado
            personalized_prompt = await self._build_personalized_prompt(
                template, question_data, user_context
            )
            
            # 6. Llamada a LLM (simulada - necesita API key)
            llm_response = await self._call_llm_with_fallback(
                selected_model, personalized_prompt, template.model_config
            )
            
            # 7. Post-procesar respuesta
            processed_response = await self._post_process_response(
                llm_response, question_data, user_context
            )
            
            # 8. Moderar contenido
            moderation_result = await self._moderate_content(processed_response)
            if not moderation_result['approved']:
                return self._generate_moderated_response(moderation_result)
            
            # 9. Cachear respuesta
            await self._cache_response(cache_key, processed_response, template)
            
            # 10. Registrar métricas
            await self._log_successful_interaction(
                user_context['user_id'], selected_model, template, processed_response
            )
            
            # 11. Incrementar uso del usuario
            await self._increment_user_quota(user_context['user_id'])
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Error en LLM Orchestrator: {str(e)}")
            return self._generate_error_response(str(e))
    
    async def _select_optimal_model(
        self, 
        area: str, 
        explanation_type: str, 
        user_context: Dict[str, Any]
    ) -> Optional[AIModel]:
        """Selecciona el modelo óptimo basado en área y contexto"""
        
        try:
            # Preferencia por área específica
            area_model_map = {
                'matematicas': 'gpt-4',
                'lectura_critica': 'claude-3-opus', 
                'ciencias_naturales': 'gpt-4',
                'sociales_ciudadanas': 'claude-3-sonnet',
                'ingles': 'gpt-3.5-turbo-16k'
            }
            
            model_identifier = area_model_map.get(area, 'gpt-3.5-turbo')
            
            # Buscar modelo en la base de datos usando sync_to_async
            model = await sync_to_async(
                AIModel.objects.filter(
                    model_identifier=model_identifier,
                    is_active=True
                ).first
            )()
            
            if not model:
                # Fallback al modelo por defecto
                model = await sync_to_async(
                    AIModel.objects.filter(
                        is_default=True,
                        is_active=True
                    ).first
                )()
            
            return model
            
        except Exception as e:
            logger.error(f"Error seleccionando modelo: {str(e)}")
            # Retornar modelo por defecto como último recurso
            return await sync_to_async(
                AIModel.objects.filter(is_active=True).first
            )()
    
    async def _get_optimal_template(
        self, 
        area: str, 
        explanation_type: str, 
        user_context: Dict[str, Any]
    ) -> Optional[AIPromptTemplate]:
        """Obtiene el template óptimo basado en área, tipo y rol del usuario"""
        
        try:
            user_role = user_context.get('assigned_role', 'ALL')
            
            # Buscar template específico por área y rol
            template_filters = {
                'category': explanation_type,
                'is_active': True
            }
            
            # Mapear área a código de template
            area_codes = {
                'matematicas': 'math',
                'lectura_critica': 'reading',
                'ciencias_naturales': 'science',
                'sociales_ciudadanas': 'social',
                'ingles': 'english'
            }
            
            area_code = area_codes.get(area, 'general')
            
            # Intentar template específico por rol
            specific_template = await sync_to_async(
                AIPromptTemplate.objects.filter(
                    code__icontains=f"{area_code}_{explanation_type}_{user_role.lower()}",
                    **template_filters
                ).first
            )()
            
            if specific_template:
                return specific_template
            
            # Fallback a template general del área
            area_template = await sync_to_async(
                AIPromptTemplate.objects.filter(
                    code__icontains=f"{area_code}_{explanation_type}",
                    **template_filters
                ).first
            )()
            
            if area_template:
                return area_template
            
            # Último fallback a template general
            general_template = await sync_to_async(
                AIPromptTemplate.objects.filter(
                    role_filter='ALL',
                    **template_filters
                ).first
            )()
            
            return general_template
            
        except Exception as e:
            logger.error(f"Error obteniendo template: {str(e)}")
            return None
    
    async def _build_personalized_prompt(
        self, 
        template: AIPromptTemplate, 
        question_data: Dict[str, Any], 
        user_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Construye prompt personalizado con variables del usuario"""
        
        try:
            # Variables base
            variables = {
                'question': question_data.get('question_text', ''),
                'selected_option': question_data.get('selected_option', ''),
                'correct_option': question_data.get('correct_option', ''),
                'user_level': user_context.get('level', 1),
                'user_accuracy': user_context.get('accuracy', 0),
                'user_role': user_context.get('assigned_role', 'ALL'),
                'response_time': question_data.get('response_time', 0)
            }
            
            # Variables específicas según el contexto
            if 'strengths' in user_context:
                variables['user_strengths'] = ', '.join(user_context['strengths'][:3])
            
            if 'weaknesses' in user_context:
                variables['user_weaknesses'] = ', '.join(user_context['weaknesses'][:3])
            
            if question_data.get('area') == 'ingles':
                variables['cefr_level'] = user_context.get('english_level', 'A1')
                variables['english_text'] = question_data.get('text_passage', '')
            
            if question_data.get('area') in ['lectura_critica', 'sociales_ciudadanas']:
                variables['text_passage'] = question_data.get('text_passage', '')
            
            # Renderizar el prompt
            user_prompt = template.render_prompt(**variables)
            
            return {
                'system': template.system_prompt,
                'user': user_prompt
            }
            
        except Exception as e:
            logger.error(f"Error construyendo prompt: {str(e)}")
            return {
                'system': "Eres un tutor educativo especializado en preparación ICFES.",
                'user': f"Explica esta pregunta: {question_data.get('question_text', '')}"
            }
    
    async def _call_llm_with_fallback(
        self, 
        model: AIModel, 
        prompt: Dict[str, str], 
        model_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simula llamada a LLM con fallback automático
        En producción, aquí iría la llamada real a OpenAI/Anthropic
        """
        
        try:
            # NOTA: Aquí iría la llamada real a la API
            # Por ahora, generamos una respuesta simulada inteligente
            
            model_name = model.model_identifier if model else 'gpt-3.5-turbo'
            
            # Simular diferentes estilos según el modelo
            if 'gpt-4' in model_name:
                # Respuesta más detallada y analítica
                simulated_response = await self._generate_gpt4_style_response(prompt)
            elif 'claude' in model_name:
                # Respuesta más conversacional y estructurada
                simulated_response = await self._generate_claude_style_response(prompt)
            else:
                # Respuesta estándar
                simulated_response = await self._generate_standard_response(prompt)
            
            return {
                'content': simulated_response,
                'model_used': model_name,
                'tokens_used': len(simulated_response.split()) * 1.3,  # Estimación
                'response_time_ms': 1500,  # Simulado
                'confidence_score': 0.85
            }
            
        except Exception as e:
            logger.error(f"Error en llamada LLM: {str(e)}")
            # Fallback a respuesta básica
            return {
                'content': await self._generate_fallback_llm_response(prompt),
                'model_used': 'fallback',
                'tokens_used': 100,
                'response_time_ms': 500,
                'confidence_score': 0.5
            }
    
    async def _generate_gpt4_style_response(self, prompt: Dict[str, str]) -> str:
        """Genera respuesta simulada estilo GPT-4 (detallada y analítica)"""
        return f"""Basándome en el análisis de esta pregunta, puedo proporcionar una explicación detallada:

**Análisis del Problema:**
{prompt['user'][:200]}...

**Explicación Paso a Paso:**
1. Primero, identifiquemos los conceptos clave involucrados
2. Analicemos la lógica del problema
3. Evaluemos cada opción sistemáticamente

**Estrategia Recomendada:**
Para problemas similares, te sugiero seguir este enfoque metodológico que te permitirá llegar a la respuesta correcta de manera consistente.

**Conexiones Conceptuales:**
Este tipo de problema se relaciona con otros conceptos fundamentales que hemos visto anteriormente.

*[Esta es una respuesta simulada. En producción se usaría la API real con la clave proporcionada]*"""

    async def _generate_claude_style_response(self, prompt: Dict[str, str]) -> str:
        """Genera respuesta simulada estilo Claude (conversacional y estructurada)"""
        return f"""Te ayudo a entender esta pregunta paso a paso:

Veo que has trabajado en este problema, y quiero asegurarme de que comprendas tanto la solución como el razonamiento detrás de ella.

**Desglosemos el problema:**
{prompt['user'][:150]}...

**Mi enfoque sería:**

• Primero, analizar qué nos están preguntando exactamente
• Identificar la información clave que nos dan
• Aplicar el concepto relevante de manera sistemática

**¿Por qué es importante entender esto?**
Este tipo de razonamiento te será útil no solo en el ICFES, sino en tu desarrollo académico general.

**Para la próxima vez:**
Te sugiero que cuando veas un problema similar, comiences identificando estos elementos clave...

*[Esta es una respuesta simulada. En producción se usaría la API real con la clave proporcionada]*"""

    async def _generate_standard_response(self, prompt: Dict[str, str]) -> str:
        """Genera respuesta simulada estándar"""
        return f"""Explicación de la pregunta:

{prompt['user'][:100]}...

**Solución:**
1. Análisis del problema
2. Aplicación del concepto
3. Verificación de la respuesta

**Concepto clave:** El tema central de esta pregunta involucra principios fundamentales que debes dominar.

**Recomendación:** Practica problemas similares para reforzar este concepto.

*[Esta es una respuesta simulada. En producción se usaría la API real con la clave proporcionada]*"""

    async def _generate_fallback_llm_response(self, prompt: Dict[str, str]) -> str:
        """Respuesta de fallback cuando hay errores"""
        return """Lo siento, experimentamos un problema temporal con el sistema de IA. 

**Mientras tanto, aquí tienes algunos consejos generales:**
- Revisa cuidadosamente cada opción
- Elimina las respuestas que claramente no son correctas
- Busca palabras clave en la pregunta
- Si no estás seguro, confía en tu primera intuición

**Recomendación:** Intenta nuevamente en unos minutos o consulta con tu tutor.

*[Respuesta de fallback - funcionalidad completa disponible con configuración de API]*"""

    # ===== MÉTODOS DE CACHE =====
    
    async def _get_cached_response(self, cache_key: str) -> Optional[AIResponseCache]:
        """Obtiene respuesta cacheada si existe"""
        try:
            # Primero buscar en Django cache (más rápido)
            cached_data = cache.get(f"ai_response_{cache_key}")
            if cached_data:
                return cached_data
            
            # Si no está en cache, buscar en base de datos
            cached_response = await sync_to_async(
                AIResponseCache.objects.filter(
                    cache_key=cache_key,
                    expires_at__gt=timezone.now()
                ).first
            )()
            
            if cached_response:
                # Almacenar en Django cache para próximas veces
                cache.set(f"ai_response_{cache_key}", cached_response, timeout=3600)  # 1 hora
                return cached_response
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo cache: {str(e)}")
            return None
    
    async def _is_cache_valid(self, cached_response: AIResponseCache) -> bool:
        """Verifica si la respuesta cacheada es válida"""
        try:
            # Verificar expiración
            if not cached_response.is_valid():
                return False
            
            # Verificar calidad (si hay suficientes serves y buena satisfacción)
            if cached_response.serve_count >= 5:
                if cached_response.user_satisfaction_avg < 3.0:  # Menos de 3/5 estrellas
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando cache: {str(e)}")
            return False
    
    async def _cache_response(
        self, 
        cache_key: str, 
        response: Dict[str, Any], 
        template: AIPromptTemplate
    ):
        """Cachea una respuesta para uso futuro"""
        try:
            # Determinar tiempo de expiración basado en el tipo de contenido
            expiration_hours = 24  # Por defecto 24 horas
            
            if template.category == 'hint':
                expiration_hours = 72  # Hints duran más
            elif template.category == 'explanation':
                expiration_hours = 48  # Explicaciones duran 2 días
            elif template.category == 'analysis':
                expiration_hours = 12  # Análisis se vuelven obsoletos más rápido
            
            expires_at = timezone.now() + timedelta(hours=expiration_hours)
            
            # Crear o actualizar cache en base de datos
            cache_obj, created = await sync_to_async(
                AIResponseCache.objects.update_or_create
            )(
                cache_key=cache_key,
                defaults={
                    'prompt_template': template,
                    'response_content': response.get('content', ''),
                    'model_used_id': response.get('model_id'),
                    'tokens_used': int(response.get('tokens_used', 0)),
                    'expires_at': expires_at,
                    'serve_count': 1
                }
            )
            
            # Si no es nuevo, incrementar contador
            if not created:
                cache_obj.serve_count += 1
                await sync_to_async(cache_obj.save)()
            
            # También almacenar en Django cache para acceso rápido
            cache.set(f"ai_response_{cache_key}", cache_obj, timeout=expiration_hours * 3600)
            
            logger.info(f"Respuesta cacheada: {cache_key} (expires: {expires_at})")
            
        except Exception as e:
            logger.error(f"Error cacheando respuesta: {str(e)}")
    
    def _format_cached_response(self, cached_response: AIResponseCache) -> Dict[str, Any]:
        """Formatea respuesta cacheada para el frontend"""
        try:
            # Incrementar contador de servidas
            cached_response.serve_count += 1
            cached_response.save(update_fields=['serve_count', 'last_served'])
            
            return {
                'success': True,
                'content': cached_response.response_content,
                'model_used': cached_response.model_used.model_identifier if cached_response.model_used else 'cached',
                'cached': True,
                'cache_age_hours': (timezone.now() - cached_response.created_at).total_seconds() / 3600,
                'serve_count': cached_response.serve_count,
                'tokens_used': cached_response.tokens_used,
                'processing_time_ms': 50,  # Cache es muy rápido
                'confidence_score': min(0.9, 0.7 + (cached_response.user_satisfaction_avg / 10))
            }
            
        except Exception as e:
            logger.error(f"Error formateando respuesta cacheada: {str(e)}")
            return {
                'success': True,
                'content': cached_response.response_content,
                'cached': True,
                'error': 'Error en formateo'
            }
    
    async def _post_process_response(
        self, 
        llm_response: Dict[str, Any], 
        question_data: Dict[str, Any], 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Post-procesa la respuesta del LLM para mejorarla"""
        try:
            processed_response = llm_response.copy()
            
            # Agregar recomendaciones relacionadas
            processed_response['recommendations'] = await self._generate_related_recommendations(
                question_data, user_context
            )
            
            # Agregar conceptos relacionados
            processed_response['related_concepts'] = await self._extract_related_concepts(
                question_data.get('area', ''), llm_response.get('content', '')
            )
            
            # Calcular score de personalización
            processed_response['personalized'] = await self._calculate_personalization_score(
                user_context, llm_response
            )
            
            # Añadir metadatos de procesamiento
            processed_response['processing_metadata'] = {
                'area': question_data.get('area'),
                'user_role': user_context.get('assigned_role'),
                'user_level': user_context.get('level'),
                'generated_at': timezone.now().isoformat()
            }
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Error en post-procesamiento: {str(e)}")
            return llm_response  # Retornar original en caso de error
    
    async def _generate_related_recommendations(
        self, 
        question_data: Dict[str, Any], 
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones relacionadas a la pregunta"""
        try:
            recommendations = []
            area = question_data.get('area', '')
            user_accuracy = user_context.get('accuracy', 0)
            
            if user_accuracy < 70:
                recommendations.append({
                    'type': 'practice',
                    'title': f'Practicar más {area.replace("_", " ").title()}',
                    'description': 'Refuerza este tema con ejercicios adicionales',
                    'priority': 'high',
                    'estimated_time': 20,
                    'icon': '📚'
                })
            
            recommendations.append({
                'type': 'strategy',
                'title': 'Revisar estrategia de resolución',
                'description': 'Analiza tu enfoque para este tipo de problemas',
                'priority': 'medium',
                'estimated_time': 10,
                'icon': '🔍'
            })
            
            return recommendations[:3]  # Máximo 3 recomendaciones
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {str(e)}")
            return []
    
    async def _extract_related_concepts(self, area: str, content: str) -> List[str]:
        """Extrae conceptos relacionados del contenido"""
        try:
            # Mapeo de conceptos por área
            area_concepts = {
                'matematicas': ['álgebra', 'geometría', 'trigonometría', 'cálculo', 'estadística'],
                'lectura_critica': ['comprensión lectora', 'análisis textual', 'inferencia', 'síntesis'],
                'ciencias_naturales': ['biología', 'química', 'física', 'método científico'],
                'sociales_ciudadanas': ['historia', 'geografía', 'civismo', 'economía'],
                'ingles': ['grammar', 'vocabulary', 'reading comprehension', 'writing']
            }
            
            concepts = area_concepts.get(area, [])
            
            # Filtrar conceptos que aparecen en el contenido
            related = [concept for concept in concepts if concept.lower() in content.lower()]
            
            return related[:5]  # Máximo 5 conceptos
            
        except Exception as e:
            logger.error(f"Error extrayendo conceptos: {str(e)}")
            return []
    
    async def _calculate_personalization_score(
        self, 
        user_context: Dict[str, Any], 
        llm_response: Dict[str, Any]
    ) -> bool:
        """Calcula si la respuesta está personalizada"""
        try:
            # Verificar si se usó información específica del usuario
            personalization_indicators = 0
            
            content = llm_response.get('content', '').lower()
            
            if user_context.get('assigned_role', '') != 'ALL':
                personalization_indicators += 1
            
            if user_context.get('level', 0) > 1:
                personalization_indicators += 1
            
            if user_context.get('weaknesses'):
                personalization_indicators += 1
            
            if user_context.get('strengths'):
                personalization_indicators += 1
            
            return personalization_indicators >= 2
            
        except Exception as e:
            logger.error(f"Error calculando personalización: {str(e)}")
            return False
    
    # Métodos auxiliares ya existentes
    
    def _generate_cache_key(self, template_id: int, question_data: Dict, user_context: Dict) -> str:
        """Genera clave única para el caché"""
        cache_data = {
            'template_id': template_id,
            'question_id': question_data.get('id'),
            'user_role': user_context.get('assigned_role'),
            'user_level_range': user_context.get('level', 0) // 5  # Agrupar por rangos
        }
        return hashlib.sha256(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    async def _check_user_quota(self, user_id: int) -> bool:
        """Verifica si el usuario puede usar IA"""
        try:
            from apps.ai_llm.models import AIUsageQuota
            quota, created = await sync_to_async(
                AIUsageQuota.objects.get_or_create
            )(
                user_id=user_id,
                defaults={'daily_limit': 50, 'monthly_limit': 1000}
            )
            return quota.can_use_ai()
        except Exception:
            return True  # Permitir por defecto en caso de error
    
    async def _increment_user_quota(self, user_id: int):
        """Incrementa el uso del usuario"""
        try:
            from apps.ai_llm.models import AIUsageQuota
            quota, created = await sync_to_async(
                AIUsageQuota.objects.get_or_create
            )(
                user_id=user_id,
                defaults={'daily_limit': 50, 'monthly_limit': 1000}
            )
            await sync_to_async(quota.increment_usage)()
        except Exception as e:
            logger.error(f"Error incrementando quota: {str(e)}")
    
    async def _moderate_content(self, response: Dict[str, Any]) -> Dict[str, bool]:
        """Moderación básica de contenido"""
        content = response.get('content', '')
        
        # Lista de palabras/frases problemáticas (expandir según necesidades)
        problematic_terms = [
            'contenido inapropiado', 'violencia', 'odio', 
            # Agregar más términos según políticas de moderación
        ]
        
        has_issues = any(term in content.lower() for term in problematic_terms)
        
        return {
            'approved': not has_issues,
            'issues': problematic_terms if has_issues else [],
            'confidence': 0.9 if not has_issues else 0.1
        }
    
    async def _log_interaction(self, user_id: int, interaction_type: str, template_id: int = None):
        """Registra interacción en logs"""
        try:
            await sync_to_async(
                AIInteractionLog.objects.create
            )(
                user_id=user_id,
                interaction_type=interaction_type,
                input_data={'template_id': template_id},
                processing_time_ms=100
            )
        except Exception as e:
            logger.error(f"Error logging interaction: {str(e)}")
    
    async def _log_successful_interaction(
        self, 
        user_id: int, 
        model: AIModel, 
        template: AIPromptTemplate, 
        response: Dict[str, Any]
    ):
        """Registra interacción exitosa con métricas"""
        try:
            await sync_to_async(
                AIInteractionLog.objects.create
            )(
                user_id=user_id,
                interaction_type='explanation_generated',
                input_data={
                    'template_id': template.id,
                    'model_id': model.id if model else None,
                    'template_code': template.code
                },
                output_data={
                    'content_length': len(response.get('content', '')),
                    'cached': response.get('cached', False),
                    'personalized': response.get('personalized', False)
                },
                model_used=model,
                total_tokens=int(response.get('tokens_used', 0)),
                processing_time_ms=response.get('response_time_ms', 0),
                cost=model.calculate_cost(
                    int(response.get('tokens_input', 0)),
                    int(response.get('tokens_output', 0))
                ) if model else 0
            )
        except Exception as e:
            logger.error(f"Error logging successful interaction: {str(e)}")
    
    def _generate_quota_exceeded_response(self) -> Dict[str, Any]:
        """Respuesta cuando se excede la cuota"""
        return {
            'success': False,
            'message': 'Has alcanzado tu límite diario de consultas IA. Intenta mañana o considera upgradearte.',
            'type': 'quota_exceeded',
            'retry_after': '24 hours'
        }
    
    def _generate_error_response(self, error_message: str) -> Dict[str, Any]:
        """Respuesta de error genérica"""
        return {
            'success': False,
            'message': 'Ocurrió un error procesando tu solicitud. Intenta nuevamente.',
            'type': 'error',
            'debug_info': error_message if settings.DEBUG else None
        }
    
    def _generate_fallback_response(self, question_data: Dict, user_context: Dict) -> Dict[str, Any]:
        """Respuesta de fallback cuando no hay templates"""
        return {
            'success': True,
            'content': f"""No pude generar una explicación personalizada, pero aquí tienes algunos consejos generales:

**Para esta pregunta:**
- Lee cuidadosamente cada opción
- Elimina las opciones claramente incorrectas
- Busca palabras clave que te guíen a la respuesta

**Estrategia general:**
- Maneja tu tiempo efectivamente
- Confía en tu preparación
- Si no estás seguro, ve con tu primera intuición

**Recomendación:** Practica más problemas similares para reforzar estos conceptos.""",
            'type': 'fallback',
            'personalized': False
        }
    
    def _generate_moderated_response(self, moderation_result: Dict) -> Dict[str, Any]:
        """Respuesta cuando el contenido fue moderado"""
        return {
            'success': False,
            'message': 'El contenido generado no cumple con nuestras políticas de seguridad.',
            'type': 'moderated',
            'issues': moderation_result.get('issues', [])
        }


# Instancia global del orchestrador
llm_orchestrator = LLMOrchestrator()