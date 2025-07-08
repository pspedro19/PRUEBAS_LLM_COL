import numpy as np
import logging
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from scipy.optimize import minimize_scalar
import math

from app.models.question import Question, IRTParameters
from app.models.response import UserResponse
from app.models.user import User, UserProfile
from app.core.config import settings

logger = logging.getLogger(__name__)

class IRTService:
    """
    Servicio de Item Response Theory para evaluación adaptativa
    Implementa modelo 3PL (Three Parameter Logistic)
    """
    
    def __init__(self):
        self.min_theta = -3.0
        self.max_theta = 3.0
        self.default_theta = settings.IRT_DEFAULT_THETA
        self.default_theta_sd = settings.IRT_DEFAULT_THETA_SD
        self.min_responses = settings.IRT_MIN_RESPONSES
    
    def probability_correct_3pl(
        self, 
        theta: float, 
        a: float, 
        b: float, 
        c: float = 0.0
    ) -> float:
        """
        Calcula probabilidad de respuesta correcta usando modelo 3PL
        P(θ) = c + (1 - c) / (1 + exp(-a(θ - b)))
        
        Args:
            theta: Habilidad del estudiante
            a: Discriminación del ítem
            b: Dificultad del ítem
            c: Adivinación (pseudo-guessing)
        """
        try:
            if a == 0:
                return 0.5
            
            exponent = -a * (theta - b)
            
            # Manejar overflow numérico
            if exponent > 700:  # exp(700) es muy grande
                return c
            elif exponent < -700:  # exp(-700) es muy pequeño
                return 1.0
            
            probability = c + (1 - c) / (1 + math.exp(exponent))
            return max(0.0, min(1.0, probability))
            
        except (OverflowError, ValueError) as e:
            logger.warning(f"Numerical error in 3PL calculation: {e}")
            return 0.5
    
    def information_function_3pl(
        self, 
        theta: float, 
        a: float, 
        b: float, 
        c: float = 0.0
    ) -> float:
        """
        Calcula la función de información de Fisher para un ítem
        I(θ) = a² * [P(θ) - c]² * [1 - P(θ)] / [(1 - c)² * P(θ)]
        """
        try:
            p_theta = self.probability_correct_3pl(theta, a, b, c)
            
            if p_theta <= 0 or p_theta >= 1 or c >= 1:
                return 0.0
            
            numerator = (a ** 2) * ((p_theta - c) ** 2) * (1 - p_theta)
            denominator = ((1 - c) ** 2) * p_theta
            
            if denominator == 0:
                return 0.0
            
            information = numerator / denominator
            return max(0.0, information)
            
        except (ZeroDivisionError, ValueError) as e:
            logger.warning(f"Error calculating information function: {e}")
            return 0.0
    
    def estimate_theta_mle(
        self, 
        responses: List[Tuple[bool, float, float, float]],
        initial_theta: float = 0.0
    ) -> Tuple[float, float]:
        """
        Estima theta usando Maximum Likelihood Estimation
        
        Args:
            responses: Lista de (is_correct, a, b, c) para cada respuesta
            initial_theta: Valor inicial de theta
            
        Returns:
            (theta_estimate, standard_error)
        """
        if not responses:
            return initial_theta, self.default_theta_sd
        
        def log_likelihood(theta):
            """Función de log-verosimilitud negativa"""
            ll = 0.0
            for is_correct, a, b, c in responses:
                p = self.probability_correct_3pl(theta, a, b, c)
                
                # Evitar log(0)
                p = max(1e-10, min(1 - 1e-10, p))
                
                if is_correct:
                    ll += math.log(p)
                else:
                    ll += math.log(1 - p)
            
            return -ll  # Negativo porque minimize busca mínimos
        
        try:
            # Optimización en rango [-3, 3]
            result = minimize_scalar(
                log_likelihood,
                bounds=(self.min_theta, self.max_theta),
                method='bounded'
            )
            
            theta_estimate = result.x
            
            # Calcular error estándar usando información de Fisher
            total_information = 0.0
            for is_correct, a, b, c in responses:
                total_information += self.information_function_3pl(theta_estimate, a, b, c)
            
            if total_information > 0:
                standard_error = 1.0 / math.sqrt(total_information)
            else:
                standard_error = self.default_theta_sd
            
            return theta_estimate, standard_error
            
        except Exception as e:
            logger.error(f"Error in theta estimation: {e}")
            return initial_theta, self.default_theta_sd
    
    def estimate_theta_eap(
        self,
        responses: List[Tuple[bool, float, float, float]],
        prior_mean: float = 0.0,
        prior_sd: float = 1.0
    ) -> Tuple[float, float]:
        """
        Estima theta usando Expected A Posteriori (EAP) con prior normal
        
        Args:
            responses: Lista de (is_correct, a, b, c)
            prior_mean: Media del prior
            prior_sd: Desviación estándar del prior
        """
        if not responses:
            return prior_mean, prior_sd
        
        # Discretización del espacio theta
        theta_points = np.linspace(self.min_theta, self.max_theta, 61)
        
        # Calcular verosimilitud para cada punto
        likelihoods = np.zeros_like(theta_points)
        
        for i, theta in enumerate(theta_points):
            likelihood = 1.0
            
            for is_correct, a, b, c in responses:
                p = self.probability_correct_3pl(theta, a, b, c)
                
                if is_correct:
                    likelihood *= p
                else:
                    likelihood *= (1 - p)
            
            likelihoods[i] = likelihood
        
        # Prior normal
        priors = np.exp(-0.5 * ((theta_points - prior_mean) / prior_sd) ** 2)
        priors /= (prior_sd * math.sqrt(2 * math.pi))
        
        # Posterior
        posteriors = likelihoods * priors
        
        # Normalizar
        if np.sum(posteriors) > 0:
            posteriors /= np.sum(posteriors)
        else:
            # Fallback al prior si no hay información
            posteriors = priors / np.sum(priors)
        
        # EAP estimate
        theta_eap = np.sum(theta_points * posteriors)
        
        # Posterior standard deviation
        theta_variance = np.sum((theta_points - theta_eap) ** 2 * posteriors)
        theta_sd = math.sqrt(theta_variance)
        
        return float(theta_eap), float(theta_sd)
    
    async def update_user_theta(
        self,
        user_id: str,
        subject_area: str,
        new_response: Tuple[bool, float, float, float],
        db: AsyncSession
    ) -> Tuple[float, float]:
        """
        Actualiza el theta de un usuario después de una nueva respuesta
        
        Args:
            user_id: ID del usuario
            subject_area: Área académica
            new_response: (is_correct, a, b, c) de la nueva respuesta
            db: Sesión de base de datos
            
        Returns:
            (new_theta, standard_error)
        """
        try:
            # Obtener perfil del usuario
            result = await db.execute(
                select(UserProfile).filter(UserProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                logger.error(f"No profile found for user {user_id}")
                return self.default_theta, self.default_theta_sd
            
            # Obtener theta actual
            current_theta = profile.get_theta_for_area(subject_area)
            
            # Obtener respuestas recientes del usuario en esta área
            recent_responses = await self.get_user_responses_for_area(
                user_id, subject_area, db, limit=20
            )
            
            # Agregar la nueva respuesta
            all_responses = recent_responses + [new_response]
            
            # Estimar nuevo theta
            if len(all_responses) < self.min_responses:
                # Usar EAP con prior fuerte si hay pocas respuestas
                new_theta, std_error = self.estimate_theta_eap(
                    all_responses,
                    prior_mean=current_theta,
                    prior_sd=1.0
                )
            else:
                # Usar MLE si hay suficientes respuestas
                new_theta, std_error = self.estimate_theta_mle(
                    all_responses,
                    initial_theta=current_theta
                )
            
            # Actualizar perfil
            profile.update_theta_for_area(subject_area, new_theta)
            
            # Actualizar errores estándar
            if not profile.theta_std_errors:
                profile.theta_std_errors = {}
            profile.theta_std_errors[subject_area] = std_error
            
            await db.commit()
            
            logger.info(f"Updated theta for user {user_id} in {subject_area}: {current_theta:.3f} -> {new_theta:.3f}")
            
            return new_theta, std_error
            
        except Exception as e:
            logger.error(f"Error updating user theta: {e}")
            await db.rollback()
            return current_theta, self.default_theta_sd
    
    async def get_user_responses_for_area(
        self,
        user_id: str,
        subject_area: str,
        db: AsyncSession,
        limit: int = 50
    ) -> List[Tuple[bool, float, float, float]]:
        """
        Obtiene las respuestas recientes del usuario para una área específica
        """
        try:
            # Query para obtener respuestas con parámetros IRT
            query = (
                select(UserResponse, IRTParameters)
                .join(Question, UserResponse.question_id == Question.id)
                .join(IRTParameters, Question.id == IRTParameters.question_id)
                .filter(
                    and_(
                        UserResponse.user_id == user_id,
                        Question.subject_area == subject_area,
                        IRTParameters.is_calibrated == True
                    )
                )
                .order_by(UserResponse.answered_at.desc())
                .limit(limit)
            )
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            responses = []
            for user_response, irt_params in rows:
                responses.append((
                    user_response.is_correct,
                    irt_params.discrimination_a,
                    irt_params.difficulty_b,
                    irt_params.guessing_c
                ))
            
            return responses
            
        except Exception as e:
            logger.error(f"Error getting user responses: {e}")
            return []
    
    async def select_next_question(
        self,
        user_id: str,
        subject_area: str,
        target_information: float = 0.5,
        db: AsyncSession = None
    ) -> Optional[Question]:
        """
        Selecciona la siguiente pregunta óptima usando CAT (Computer Adaptive Testing)
        
        Args:
            user_id: ID del usuario
            subject_area: Área académica
            target_information: Información objetivo (mayor = más preciso)
            db: Sesión de base de datos
            
        Returns:
            Pregunta seleccionada o None si no hay preguntas disponibles
        """
        try:
            # Obtener theta actual del usuario
            result = await db.execute(
                select(UserProfile).filter(UserProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                user_theta = self.default_theta
            else:
                user_theta = profile.get_theta_for_area(subject_area)
            
            # Obtener preguntas no respondidas por el usuario en esta área
            subquery = (
                select(UserResponse.question_id)
                .filter(UserResponse.user_id == user_id)
            )
            
            query = (
                select(Question, IRTParameters)
                .join(IRTParameters, Question.id == IRTParameters.question_id)
                .filter(
                    and_(
                        Question.subject_area == subject_area,
                        Question.status == "active",
                        IRTParameters.is_calibrated == True,
                        ~Question.id.in_(subquery)
                    )
                )
            )
            
            result = await db.execute(query)
            available_questions = result.fetchall()
            
            if not available_questions:
                logger.warning(f"No available questions for user {user_id} in {subject_area}")
                return None
            
            # Calcular información para cada pregunta
            best_question = None
            best_information = -1
            
            for question, irt_params in available_questions:
                information = self.information_function_3pl(
                    user_theta,
                    irt_params.discrimination_a,
                    irt_params.difficulty_b,
                    irt_params.guessing_c
                )
                
                # Seleccionar la pregunta con mayor información cerca del objetivo
                if information > best_information:
                    best_information = information
                    best_question = question
            
            if best_question:
                logger.info(f"Selected question {best_question.id} with information {best_information:.3f} for user {user_id}")
            
            return best_question
            
        except Exception as e:
            logger.error(f"Error selecting next question: {e}")
            return None
    
    def calculate_test_information(
        self,
        theta: float,
        item_parameters: List[Tuple[float, float, float]]
    ) -> float:
        """
        Calcula la información total del test en un punto theta dado
        """
        total_info = 0.0
        
        for a, b, c in item_parameters:
            total_info += self.information_function_3pl(theta, a, b, c)
        
        return total_info
    
    def calculate_sem(self, information: float) -> float:
        """
        Calcula el Standard Error of Measurement
        SEM = 1 / sqrt(Information)
        """
        if information <= 0:
            return float('inf')
        
        return 1.0 / math.sqrt(information)
    
    async def get_user_ability_profile(
        self,
        user_id: str,
        db: AsyncSession
    ) -> Dict[str, Dict[str, float]]:
        """
        Obtiene el perfil completo de habilidades del usuario
        """
        try:
            result = await db.execute(
                select(UserProfile).filter(UserProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                return {}
            
            areas = ["matematicas", "lectura_critica", "ciencias_naturales", "ciencias_sociales", "ingles"]
            ability_profile = {}
            
            for area in areas:
                theta = profile.get_theta_for_area(area)
                std_error = profile.theta_std_errors.get(area, self.default_theta_sd) if profile.theta_std_errors else self.default_theta_sd
                
                # Convertir theta a puntaje de 0-100
                percentile = self.theta_to_percentile(theta)
                
                ability_profile[area] = {
                    "theta": theta,
                    "standard_error": std_error,
                    "percentile": percentile,
                    "confidence_interval_95": [
                        self.theta_to_percentile(theta - 1.96 * std_error),
                        self.theta_to_percentile(theta + 1.96 * std_error)
                    ]
                }
            
            return ability_profile
            
        except Exception as e:
            logger.error(f"Error getting user ability profile: {e}")
            return {}
    
    def theta_to_percentile(self, theta: float) -> float:
        """
        Convierte theta a percentil (0-100) asumiendo distribución normal
        """
        from scipy.stats import norm
        
        # Usar distribución normal estándar
        percentile = norm.cdf(theta) * 100
        return max(0.0, min(100.0, percentile))
    
    def percentile_to_theta(self, percentile: float) -> float:
        """
        Convierte percentil (0-100) a theta
        """
        from scipy.stats import norm
        
        percentile = max(0.01, min(99.99, percentile)) / 100
        return norm.ppf(percentile) 