#!/usr/bin/env python3
"""
Script para agregar las importaciones necesarias
"""

# Leer el archivo
with open('/app/apps/icfes/views.py', 'r') as f:
    content = f.read()

# Buscar la línea de imports de models para agregar después
if 'from apps.questions.models import' not in content:
    # Agregar la importación después de la línea de models
    content = content.replace(
        'from .models import UserICFESSession, ICFESExam',
        'from .models import UserICFESSession, ICFESExam\nfrom apps.questions.models import Question, QuestionOption, UserQuestionResponse'
    )
    
    # Escribir el archivo modificado
    with open('/app/apps/icfes/views.py', 'w') as f:
        f.write(content)
    
    print("✅ Importaciones agregadas exitosamente")
else:
    print("✅ Las importaciones ya existen") 