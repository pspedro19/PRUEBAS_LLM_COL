#!/usr/bin/env python3
"""
Script para reemplazar submit_answer con versión que funciona
"""

# Leer el archivo
with open('/app/apps/icfes/views.py', 'r') as f:
    lines = f.readlines()

# Encontrar el inicio y fin de la función submit_answer
start_line = None
end_line = None

for i, line in enumerate(lines):
    if 'def submit_answer(request, session_id):' in line:
        start_line = i - 2  # Incluir decoradores
    elif start_line is not None and (line.startswith('def ') or line.startswith('@api_view')):
        end_line = i
        break

if start_line is None:
    print("❌ No se encontró la función submit_answer")
    exit(1)

if end_line is None:
    end_line = len(lines)

print(f"📍 Función encontrada en líneas {start_line+1} a {end_line}")

# Nueva función corregida
new_function = '''@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request, session_id):
    """
    Enviar respuesta a una pregunta - USANDO SOLO PREGUNTAICFES
    """
    try:
        # Obtener datos de la petición
        question_id = request.data.get('question_id')
        selected_answer = request.data.get('selected_answer')
        
        if not question_id or not selected_answer:
            return Response({
                'success': False,
                'message': 'question_id y selected_answer son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"✅ SUBMIT_ANSWER FUNCIONANDO: Session {session_id}, Question {question_id}, Answer {selected_answer}")
        
        # Obtener la sesión
        session = UserICFESSession.objects.get(
            uuid=session_id,
            user=request.user
        )
        print(f"✅ Sesión encontrada: {session.uuid}")
        
        # Obtener la pregunta usando el modelo que tiene datos
        pregunta = PreguntaICFES.objects.get(id=question_id)
        print(f"✅ Pregunta encontrada: {pregunta.pregunta_texto[:50]}...")
        print(f"✅ Respuesta correcta: {pregunta.respuesta_correcta}")
        
        # Verificar si la respuesta es correcta
        is_correct = selected_answer == pregunta.respuesta_correcta
        print(f"✅ Respuesta del usuario: {selected_answer} - {'CORRECTA' if is_correct else 'INCORRECTA'}")
        
        # Actualizar progreso de la sesión
        session_data = session.areas_filter or {}
        preguntas_ids = session_data.get('preguntas_ids', [])
        
        # Contar cuántas preguntas se han procesado
        current_response = 1
        
        # Simular progreso
        for i, pid in enumerate(preguntas_ids):
            if str(pid) == str(question_id):
                current_response = i + 1
                break
        
        # Actualizar sesión
        session.questions_answered = current_response
        
        # Verificar si completó todas las preguntas
        total_questions_in_session = len(preguntas_ids)
        
        if current_response >= total_questions_in_session:
            session.is_completed = True
            session.completion_time = timezone.now()
            
            # Calcular XP final
            total_xp = current_response * 10  # XP simple
            session.xp_earned = total_xp
            print(f"🏆 Sesión completada! XP: {total_xp}")
        
        session.save()
        print(f"📊 Progreso actualizado: {current_response}/{total_questions_in_session}")
        
        return Response({
            'success': True,
            'is_correct': is_correct,
            'correct_answer': pregunta.respuesta_correcta,
            'progress': {
                'current': current_response,
                'total': total_questions_in_session,
                'percentage': (current_response / total_questions_in_session) * 100
            },
            'is_completed': session.is_completed,
            'xp_earned': session.xp_earned if session.is_completed else 10
        })
        
    except UserICFESSession.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Sesión no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"❌ Error en submit_answer: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''

# Reemplazar la función
new_lines = lines[:start_line] + [new_function] + lines[end_line:]

# Escribir el archivo modificado
with open('/app/apps/icfes/views.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Función submit_answer reemplazada exitosamente con versión que funciona") 