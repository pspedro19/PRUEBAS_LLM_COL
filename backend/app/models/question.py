from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

# Temporarily commented out to avoid enum validation issues
# class DifficultyLevel(enum.Enum):
#     PRINCIPIANTE = "principiante"
#     INTERMEDIO = "intermedio"
#     AVANZADO = "avanzado"
#     EXPERTO = "experto"

# class ICFESArea(enum.Enum):
#     MATEMATICAS = "matematicas"
#     LECTURA_CRITICA = "lectura_critica"
#     CIENCIAS_NATURALES = "ciencias_naturales"
#     SOCIALES_CIUDADANAS = "sociales_ciudadanas"
#     INGLES = "ingles"

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Contenido de la pregunta
    title = Column(String(500), nullable=False)  # Título/enunciado principal
    content = Column(Text, nullable=False)  # Contenido completo de la pregunta
    explanation = Column(Text, nullable=True)  # Explicación de la respuesta correcta
    
    # Opciones múltiples (formato JSON en string)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)
    
    # Respuesta correcta (A, B, C, D)
    correct_answer = Column(String(1), nullable=False)
    
    # Metadatos para clasificación - Using String instead of Enum to avoid conflicts
    area = Column(String(50), nullable=False, default="matematicas")
    topic = Column(String(100), nullable=False)  # ej: "algebra_basica", "geometria"
    subtopic = Column(String(100), nullable=True)  # ej: "ecuaciones_lineales"
    difficulty = Column(String(20), nullable=False, default="intermedio")
    
    # Estadísticas de la pregunta
    times_answered = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # Porcentaje de aciertos
    
    # Configuración
    is_active = Column(Boolean, default=True)
    points_value = Column(Integer, default=10)  # Puntos que otorga
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    user_responses = relationship("UserResponse", back_populates="question")

    def update_statistics(self):
        """Actualiza las estadísticas de la pregunta basada en las respuestas"""
        if self.times_answered > 0:
            self.success_rate = (self.times_correct / self.times_answered) * 100
        else:
            self.success_rate = 0.0

    def get_difficulty_points(self):
        """Retorna puntos basados en dificultad"""
        difficulty_multiplier = {
            "principiante": 1.0,
            "intermedio": 1.5,
            "avanzado": 2.0,
            "experto": 3.0
        }
        return int(self.points_value * difficulty_multiplier.get(self.difficulty, 1.0))

    def __repr__(self):
        return f"<Question(id={self.id}, title='{self.title[:50]}...', area={self.area})>" 