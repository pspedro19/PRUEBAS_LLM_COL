"""
LLM Service for AI explanations
"""

import os
from typing import Optional
from dotenv import load_dotenv
import openai
from anthropic import Anthropic

load_dotenv()

class LLMService:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "500"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        if self.provider == "openai":
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
            self.client = openai
        elif self.provider == "anthropic":
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    def generate_explanation(
        self,
        question: dict,
        user_answer: str,
        correct_answer: str
    ) -> str:
        """Generate an AI explanation for a wrong answer"""
        
        # Get the answer options
        options_text = "\n".join([
            f"{opt.option_letter}. {opt.option_text}"
            for opt in question.options
        ])
        
        prompt = f"""Eres un tutor de matemáticas experto preparando estudiantes para el examen ICFES.

Pregunta: {question.question_text}

Opciones:
{options_text}

El estudiante seleccionó: {user_answer}
La respuesta correcta es: {correct_answer}

Proporciona una explicación clara y pedagógica que:
1. Explique por qué la respuesta del estudiante es incorrecta (sin ser condescendiente)
2. Muestre el proceso paso a paso para llegar a la respuesta correcta
3. Identifique el concepto clave que el estudiante debe revisar
4. Dé un consejo para evitar este error en el futuro

Mantén un tono amigable y motivador. La explicación debe ser concisa pero completa."""

        try:
            if self.provider == "openai":
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Eres un tutor experto en matemáticas ICFES."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
        
        except Exception as e:
            print(f"Error generating AI explanation: {e}")
            # Fallback to basic explanation
            return f"""La respuesta correcta es {correct_answer}.

{question.explanation_text}

Recuerda revisar este tipo de problemas y practicar más ejercicios similares.""" 