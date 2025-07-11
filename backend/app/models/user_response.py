from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class UserResponse(Base):
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    
    # Respuesta del usuario
    selected_answer = Column(String(1), nullable=False)  # A, B, C, D
    is_correct = Column(Boolean, nullable=False)
    
    # Tiempo y contexto
    time_taken_seconds = Column(Integer, nullable=True)  # Tiempo que tardó en responder
    session_id = Column(String(100), nullable=True)  # ID de sesión para agrupar respuestas
    quiz_mode = Column(String(50), nullable=True)  # ej: "practice", "exam", "dungeon"
    
    # Metadatos adicionales
    points_earned = Column(Integer, default=0)
    difficulty_at_time = Column(String(20), nullable=True)  # Dificultad cuando se respondió
    hints_used = Column(Integer, default=0)  # Cantidad de pistas usadas
    
    # Análisis para recomendaciones
    confidence_level = Column(Integer, nullable=True)  # 1-5, qué tan seguro estaba el usuario
    error_type = Column(String(100), nullable=True)  # Tipo de error si fue incorrecta
    
    # Timestamps
    answered_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relaciones
    user = relationship("User", back_populates="responses")
    question = relationship("Question", back_populates="user_responses")

    def calculate_points(self):
        """Calcula puntos basado en corrección, dificultad y tiempo"""
        if not self.is_correct:
            return 0
            
        base_points = self.question.get_difficulty_points() if self.question else 10
        
        # Bonus por velocidad (si respondió en menos de 30 segundos)
        time_bonus = 1.0
        if self.time_taken_seconds and self.time_taken_seconds < 30:
            time_bonus = 1.2
        elif self.time_taken_seconds and self.time_taken_seconds < 60:
            time_bonus = 1.1
            
        # Penalización por pistas
        hint_penalty = max(0.5, 1.0 - (self.hints_used * 0.1))
        
        final_points = int(base_points * time_bonus * hint_penalty)
        return final_points

    def get_feedback_message(self):
        """Genera un mensaje de feedback personalizado"""
        if self.is_correct:
            if self.time_taken_seconds and self.time_taken_seconds < 30:
                return "¡Excelente! Respuesta rápida y correcta. 🚀"
            elif self.hints_used == 0:
                return "¡Muy bien! Respuesta correcta sin ayuda. 👏"
            else:
                return "¡Correcto! Sigue practicando para mayor velocidad. ✅"
        else:
            if self.question and self.question.explanation:
                return f"Incorrecto. La respuesta correcta es {self.question.correct_answer}. {self.question.explanation}"
            else:
                return f"Incorrecto. La respuesta correcta es {self.question.correct_answer if self.question else 'N/A'}."

    def __repr__(self):
        return f"<UserResponse(user_id={self.user_id}, question_id={self.question_id}, correct={self.is_correct})>" 