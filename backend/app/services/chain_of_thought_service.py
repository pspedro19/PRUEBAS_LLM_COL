import openai
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.question import Question, IRTParameters
from app.models.response import UserResponse, ChainOfThoughtStep
from app.models.user import User, UserProfile

logger = logging.getLogger(__name__)

class ChainOfThoughtService:
    """
    Servicio de razonamiento en cadena para generar explicaciones paso a paso
    de preguntas ICFES usando GPT-4
    """
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Configuración de prompts por área
        self.area_prompts = {
            "matematicas": self._get_math_system_prompt(),
            "lectura_critica": self._get_reading_system_prompt(),
            "ciencias_naturales": self._get_science_system_prompt(),
            "ciencias_sociales": self._get_social_system_prompt(),
            "ingles": self._get_english_system_prompt()
        }
    
    async def generate_explanation(
        self,
        question: Question,
        user_response: UserResponse,
        user: User,
        explanation_type: str = "detailed",
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Genera una explicación paso a paso usando razonamiento en cadena
        
        Args:
            question: La pregunta ICFES
            user_response: La respuesta del usuario
            user: El usuario que respondió
            explanation_type: Tipo de explicación (brief, detailed, comprehensive)
            db: Sesión de base de datos
            
        Returns:
            Dict con la explicación generada y pasos del razonamiento
        """
        try:
            logger.info(f"Generating CoT explanation for question {question.id}, user {user.id}")
            
            # Obtener contexto del usuario
            user_context = await self._get_user_context(user, question.subject_area, db)
            
            # Seleccionar el prompt apropiado
            system_prompt = self.area_prompts.get(
                question.subject_area.lower(), 
                self._get_general_system_prompt()
            )
            
            # Construir el prompt específico
            user_prompt = self._build_user_prompt(
                question=question,
                user_response=user_response,
                user_context=user_context,
                explanation_type=explanation_type
            )
            
            # Generar explicación con GPT-4
            explanation = await self._call_openai_api(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                explanation_type=explanation_type
            )
            
            # Procesar y estructurar la respuesta
            structured_explanation = self._structure_explanation(explanation)
            
            # Guardar pasos en la base de datos si se proporciona sesión
            if db:
                await self._save_cot_steps(
                    user_response_id=user_response.id,
                    steps=structured_explanation["steps"],
                    db=db
                )
            
            # Actualizar métricas
            user_response.explanation_generated = True
            user_response.explanation_type = explanation_type
            user_response.explanation_generated_at = datetime.utcnow()
            user_response.cot_quality_score = structured_explanation.get("quality_score", 0.8)
            
            return {
                "success": True,
                "explanation": structured_explanation,
                "metadata": {
                    "question_id": str(question.id),
                    "user_id": str(user.id),
                    "explanation_type": explanation_type,
                    "generated_at": datetime.utcnow().isoformat(),
                    "model_used": settings.OPENAI_MODEL
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating CoT explanation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback_explanation": self._get_fallback_explanation(question, user_response)
            }
    
    def _get_math_system_prompt(self) -> str:
        """Prompt del sistema para matemáticas"""
        return """
        Eres un tutor experto en matemáticas para estudiantes de grado 11 que se preparan para el ICFES.
        
        Tu trabajo es explicar problemas matemáticos usando razonamiento en cadena (Chain of Thought).
        
        MARCO PEDAGÓGICO:
        - Usa el framework de competencias ICFES: interpretación, formulación y ejecución, argumentación
        - Enfócate en los pensamientos: numérico-variacional, espacial-métrico, aleatorio
        - Conecta con contextos reales: personal, laboral, social, científico
        
        ESTRUCTURA DE EXPLICACIÓN:
        1. **Análisis del problema**: Identifica qué se pregunta y qué información se da
        2. **Estrategia de solución**: Explica el enfoque matemático a usar
        3. **Desarrollo paso a paso**: Muestra cada cálculo con justificación
        4. **Verificación**: Comprueba que la respuesta tiene sentido
        5. **Reflexión**: Conecta con conceptos más amplios y errores comunes
        
        PRINCIPIOS:
        - Explica el "por qué" de cada paso, no solo el "cómo"
        - Usa lenguaje claro y apropiado para grado 11
        - Incluye visualizaciones cuando sea útil
        - Anticipa errores comunes y explica por qué están mal
        - Conecta con conocimientos previos del estudiante
        """
    
    def _get_reading_system_prompt(self) -> str:
        """Prompt del sistema para lectura crítica"""
        return """
        Eres un tutor experto en lectura crítica para estudiantes que se preparan para el ICFES.
        
        Tu trabajo es enseñar comprensión lectora usando razonamiento en cadena.
        
        COMPETENCIAS ICFES:
        - Identificar y entender contenidos locales
        - Comprender estructura global del texto
        - Reflexionar y evaluar contenido y contexto
        
        ESTRUCTURA DE EXPLICACIÓN:
        1. **Análisis del texto**: Identifica tipo, propósito y estructura
        2. **Localización de información**: Encuentra datos específicos relevantes
        3. **Interpretación**: Explica significados explícitos e implícitos
        4. **Evaluación crítica**: Analiza argumentos, evidencias y perspectivas
        5. **Síntesis**: Conecta ideas para responder la pregunta
        
        PRINCIPIOS:
        - Enseña estrategias de lectura efectivas
        - Diferencia entre hechos y opiniones
        - Analiza el contexto y propósito del autor
        - Identifica sesgos y puntos de vista
        - Desarrolla pensamiento crítico
        """
    
    def _get_science_system_prompt(self) -> str:
        """Prompt del sistema para ciencias naturales"""
        return """
        Eres un tutor experto en ciencias naturales (física, química, biología) para el ICFES.
        
        COMPETENCIAS CIENTÍFICAS:
        - Uso comprensivo del conocimiento científico
        - Explicación de fenómenos
        - Indagación científica
        
        ESTRUCTURA DE EXPLICACIÓN:
        1. **Identificación del fenómeno**: Qué proceso científico se estudia
        2. **Conocimiento aplicable**: Qué principios científicos son relevantes
        3. **Análisis del problema**: Cómo aplicar el conocimiento
        4. **Desarrollo lógico**: Paso a paso científico
        5. **Validación**: Verificar coherencia científica
        
        PRINCIPIOS:
        - Conecta con el método científico
        - Usa evidencia experimental cuando sea relevante
        - Explica los principios subyacentes
        - Relaciona con ejemplos de la vida real
        - Fomenta el pensamiento científico
        """
    
    def _get_social_system_prompt(self) -> str:
        """Prompt del sistema para ciencias sociales"""
        return """
        Eres un tutor experto en ciencias sociales para el ICFES.
        
        COMPETENCIAS SOCIALES:
        - Pensamiento social
        - Interpretación y análisis de perspectivas
        - Pensamiento sistémico y reflexivo
        
        ESTRUCTURA DE EXPLICACIÓN:
        1. **Contextualización**: Ubicar el problema en tiempo y espacio
        2. **Análisis de perspectivas**: Identificar diferentes puntos de vista
        3. **Factores involucrados**: Económicos, políticos, sociales, culturales
        4. **Relaciones causales**: Cómo se conectan los elementos
        5. **Implicaciones**: Consecuencias y reflexiones críticas
        
        PRINCIPIOS:
        - Analiza múltiples perspectivas
        - Considera el contexto histórico y cultural
        - Evalúa fuentes de información
        - Desarrolla pensamiento crítico sobre la sociedad
        - Conecta pasado, presente y futuro
        """
    
    def _get_english_system_prompt(self) -> str:
        """Prompt del sistema para inglés"""
        return """
        You are an expert English tutor for Colombian students preparing for ICFES.
        
        LANGUAGE COMPETENCIES:
        - Reading comprehension
        - Grammar and vocabulary usage
        - Communication and pragmatics
        
        EXPLANATION STRUCTURE:
        1. **Text Analysis**: Identify text type, purpose, and main ideas
        2. **Language Focus**: Grammar/vocabulary points being tested
        3. **Context Clues**: How to use context for comprehension
        4. **Strategy Application**: Reading/language learning strategies
        5. **Communication Purpose**: Why this language use is effective
        
        PRINCIPLES:
        - Explain in Spanish when needed for clarity
        - Focus on practical communication
        - Connect to real English usage
        - Build confidence in English skills
        - Develop autonomous learning strategies
        """
    
    def _get_general_system_prompt(self) -> str:
        """Prompt general para áreas no especificadas"""
        return """
        Eres un tutor educativo experto que ayuda a estudiantes a prepararse para el ICFES.
        
        Usa razonamiento en cadena para explicar conceptos paso a paso.
        
        ESTRUCTURA GENERAL:
        1. **Análisis**: Entender qué se pregunta
        2. **Estrategia**: Planificar el enfoque de solución
        3. **Desarrollo**: Explicar paso a paso
        4. **Verificación**: Comprobar la respuesta
        5. **Conexión**: Relacionar con otros conceptos
        
        Siempre explica el razonamiento detrás de cada paso.
        """
    
    def _build_user_prompt(
        self,
        question: Question,
        user_response: UserResponse,
        user_context: Dict,
        explanation_type: str
    ) -> str:
        """Construye el prompt específico para el usuario"""
        
        # Determinar si la respuesta fue correcta
        result_text = "correctamente" if user_response.is_correct else "incorrectamente"
        
        # Información del contexto del usuario
        user_info = f"""
        CONTEXTO DEL ESTUDIANTE:
        - Nivel actual en {question.subject_area}: {user_context.get('theta', 0.0):.2f} (escala -3 a +3)
        - Grado: {user_context.get('grade', 'No especificado')}
        - Fortalezas: {', '.join(user_context.get('strengths', []))}
        - Áreas de mejora: {', '.join(user_context.get('weaknesses', []))}
        """
        
        # Configurar el nivel de detalle
        detail_instructions = {
            "brief": "Proporciona una explicación concisa en 3-4 pasos principales.",
            "detailed": "Proporciona una explicación completa con 5-7 pasos bien detallados.",
            "comprehensive": "Proporciona una explicación exhaustiva con múltiples enfoques y conexiones."
        }.get(explanation_type, "Proporciona una explicación detallada.")
        
        prompt = f"""
        {user_info}
        
        PREGUNTA ICFES:
        {question.question_text}
        
        OPCIONES:
        {json.dumps(question.options, ensure_ascii=False)}
        
        RESPUESTA CORRECTA: {question.correct_answer}
        RESPUESTA DEL ESTUDIANTE: {user_response.selected_answer}
        
        El estudiante respondió {result_text}.
        
        COMPETENCIA EVALUADA: {question.competencia}
        SUB-COMPETENCIA: {question.sub_competencia}
        CONTEXTO: {question.contexto}
        
        INSTRUCCIONES:
        {detail_instructions}
        
        IMPORTANTE:
        - Si el estudiante respondió correctamente, explica por qué su respuesta es correcta y cómo llegó a ella.
        - Si respondió incorrectamente, explica por qué su respuesta está mal y guía hacia la respuesta correcta.
        - Usa un tono pedagógico y motivador.
        - Incluye consejos para responder preguntas similares.
        - Si hay errores comunes, menciónalos y explica cómo evitarlos.
        
        FORMATO DE RESPUESTA (JSON):
        {{
            "resumen": "Breve resumen de la explicación",
            "pasos": [
                {{
                    "numero": 1,
                    "titulo": "Título del paso",
                    "contenido": "Explicación detallada del paso",
                    "tipo": "analisis|razonamiento|calculo|conclusion"
                }}
            ],
            "errores_comunes": ["Error común 1", "Error común 2"],
            "consejos": ["Consejo 1", "Consejo 2"],
            "conceptos_clave": ["Concepto 1", "Concepto 2"],
            "conexiones": "Cómo se conecta con otros temas del ICFES"
        }}
        """
        
        return prompt
    
    async def _call_openai_api(
        self,
        system_prompt: str,
        user_prompt: str,
        explanation_type: str
    ) -> Dict[str, Any]:
        """Llama a la API de OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing OpenAI response: {e}")
            # Fallback: intentar extraer JSON del contenido
            return self._extract_json_fallback(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
    
    def _structure_explanation(self, explanation_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Estructura y valida la explicación generada"""
        structured = {
            "summary": explanation_dict.get("resumen", ""),
            "steps": [],
            "common_errors": explanation_dict.get("errores_comunes", []),
            "tips": explanation_dict.get("consejos", []),
            "key_concepts": explanation_dict.get("conceptos_clave", []),
            "connections": explanation_dict.get("conexiones", ""),
            "quality_score": 0.8  # Score por defecto
        }
        
        # Procesar pasos
        steps = explanation_dict.get("pasos", [])
        for i, step in enumerate(steps):
            structured_step = {
                "step_number": step.get("numero", i + 1),
                "title": step.get("titulo", f"Paso {i + 1}"),
                "content": step.get("contenido", ""),
                "step_type": step.get("tipo", "razonamiento")
            }
            structured["steps"].append(structured_step)
        
        # Calcular score de calidad basado en completitud
        quality_factors = [
            len(structured["steps"]) >= 3,  # Al menos 3 pasos
            len(structured["summary"]) > 50,  # Resumen sustancial
            len(structured["common_errors"]) > 0,  # Incluye errores comunes
            len(structured["tips"]) > 0,  # Incluye consejos
            len(structured["key_concepts"]) > 0  # Incluye conceptos clave
        ]
        structured["quality_score"] = sum(quality_factors) / len(quality_factors)
        
        return structured
    
    async def _save_cot_steps(
        self,
        user_response_id: str,
        steps: List[Dict],
        db: AsyncSession
    ):
        """Guarda los pasos del razonamiento en la base de datos"""
        try:
            for step_data in steps:
                cot_step = ChainOfThoughtStep(
                    user_response_id=user_response_id,
                    step_number=step_data["step_number"],
                    step_type=step_data["step_type"],
                    title=step_data["title"],
                    content=step_data["content"],
                    ai_model_used=settings.OPENAI_MODEL,
                    ai_confidence=0.8  # Score por defecto
                )
                db.add(cot_step)
            
            await db.commit()
            logger.info(f"Saved {len(steps)} CoT steps for response {user_response_id}")
            
        except Exception as e:
            logger.error(f"Error saving CoT steps: {e}")
            await db.rollback()
            raise
    
    async def _get_user_context(
        self,
        user: User,
        subject_area: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Obtiene el contexto del usuario para personalizar la explicación"""
        try:
            # Obtener perfil del usuario
            result = await db.execute(
                select(UserProfile).filter(UserProfile.user_id == user.id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                return {
                    "theta": 0.0,
                    "grade": "No especificado",
                    "strengths": [],
                    "weaknesses": []
                }
            
            return {
                "theta": profile.get_theta_for_area(subject_area),
                "grade": profile.grade or "No especificado",
                "strengths": profile.strengths or [],
                "weaknesses": profile.weaknesses or [],
                "learning_style": profile.learning_style,
                "difficulty_preference": profile.difficulty_preference
            }
            
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {"theta": 0.0, "grade": "No especificado", "strengths": [], "weaknesses": []}
    
    def _get_fallback_explanation(
        self,
        question: Question,
        user_response: UserResponse
    ) -> Dict[str, Any]:
        """Genera una explicación de respaldo si falla la IA"""
        return {
            "summary": f"Explicación para pregunta de {question.subject_area}",
            "steps": [
                {
                    "step_number": 1,
                    "title": "Análisis de la pregunta",
                    "content": f"Esta pregunta evalúa la competencia: {question.competencia}",
                    "step_type": "analisis"
                },
                {
                    "step_number": 2,
                    "title": "Respuesta correcta",
                    "content": f"La respuesta correcta es {question.correct_answer}",
                    "step_type": "conclusion"
                }
            ],
            "common_errors": ["Lectura apresurada de la pregunta"],
            "tips": ["Lee cuidadosamente cada opción", "Elimina opciones obviamente incorrectas"],
            "key_concepts": [question.competencia or "Concepto principal"],
            "connections": "Relacionado con otros temas del área",
            "quality_score": 0.3
        }
    
    def _extract_json_fallback(self, content: str) -> Dict[str, Any]:
        """Intenta extraer JSON de contenido malformado"""
        try:
            # Buscar el primer { y el último }
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start != -1 and end > start:
                json_content = content[start:end]
                return json.loads(json_content)
            else:
                return self._create_minimal_response(content)
                
        except:
            return self._create_minimal_response(content)
    
    def _create_minimal_response(self, content: str) -> Dict[str, Any]:
        """Crea una respuesta mínima cuando falla el parsing"""
        return {
            "resumen": "Explicación generada",
            "pasos": [
                {
                    "numero": 1,
                    "titulo": "Explicación",
                    "contenido": content[:500] + "..." if len(content) > 500 else content,
                    "tipo": "explicacion"
                }
            ],
            "errores_comunes": [],
            "consejos": [],
            "conceptos_clave": [],
            "conexiones": ""
        } 