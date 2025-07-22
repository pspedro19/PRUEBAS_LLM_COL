#!/usr/bin/env python
"""
Script de debugging para verificar los modelos
"""

from apps.questions.models import UserQuestionResponse, QuestionOption, Question

# Verificar el campo selected_option
field = UserQuestionResponse._meta.get_field('selected_option')
print(f"Tipo de campo: {type(field)}")
print(f"Es ForeignKey: {hasattr(field, 'related_model')}")

if hasattr(field, 'related_model'):
    print(f"Modelo relacionado: {field.related_model}")

# Buscar una pregunta y sus opciones para testing
try:
    question = Question.objects.first()
    if question:
        print(f"\nPregunta encontrada: {question.id}")
        options = QuestionOption.objects.filter(question=question)
        print(f"Opciones disponibles: {list(options.values_list('option_letter', flat=True))}")
        
        # Buscar opción B
        option_b = QuestionOption.objects.filter(question=question, option_letter='B').first()
        if option_b:
            print(f"Opción B encontrada: {option_b.id} - {option_b.option_text[:50]}")
        else:
            print("No se encontró opción B")
    else:
        print("No se encontraron preguntas")
except Exception as e:
    print(f"Error: {e}") 