#!/usr/bin/env python3
"""
Script para arreglar la función submit_answer
"""

# Leer el archivo original
with open('/app/apps/icfes/views.py', 'r') as f:
    lines = f.readlines()

# Encontrar el inicio y fin de la función submit_answer
start_line = None
end_line = None

for i, line in enumerate(lines):
    if 'def submit_answer(request, session_id):' in line:
        start_line = i
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
    Enviar respuesta a una pregunta
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
        
        print(f"🔍 SUBMIT_ANSWER: Session {session_id}, Question {question_id}, Answer {selected_answer}")
        
        # Obtener la sesión
        session = UserICFESSession.objects.get(
            uuid=session_id,
            user=request.user
        )
        print(f"✅ Sesión encontrada: {session.uuid}")
        
        # Obtener la pregunta
        question = Question.objects.get(id=question_id)
        print(f"✅ Pregunta encontrada: {question.question_text[:50]}...")
        
        # Obtener la opción correcta
        try:
            selected_option = QuestionOption.objects.get(
                question=question, 
                option_letter=selected_answer
            )
            print(f"✅ Opción encontrada: {selected_option.option_letter} - {selected_option.option_text[:30]}...")
        except QuestionOption.DoesNotExist:
            return Response({
                'success': False,
                'message': f'Opción {selected_answer} no existe para la pregunta {question_id}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener la respuesta correcta
        correct_option = QuestionOption.objects.get(question=question, is_correct=True)
        is_correct = selected_option.is_correct
        print(f"✅ Respuesta correcta: {correct_option.option_letter}")
        
        # Verificar si ya existe una respuesta para esta pregunta en esta sesión
        existing_response = UserQuestionResponse.objects.filter(
            user=request.user,
            question=question,
            session_id=session_id
        ).first()
        
        if existing_response:
            # Actualizar respuesta existente
            existing_response.selected_option = selected_option
            existing_response.is_correct = is_correct
            existing_response.save()
            print(f"🔄 Respuesta actualizada para pregunta {question_id}")
        else:
            # Crear nueva respuesta
            response = UserQuestionResponse.objects.create(
                user=request.user,
                question=question,
                selected_option=selected_option,
                is_correct=is_correct,
                response_time_seconds=0.0,  # Por ahora fijo
                session_id=session_id,
                quiz_type='icfes_practice'
            )
            print(f"✨ Nueva respuesta creada para pregunta {question_id}")
        
        # Actualizar progreso de la sesión
        total_responses = UserQuestionResponse.objects.filter(
            session_id=session_id,
            user=request.user
        ).count()
        
        correct_responses = UserQuestionResponse.objects.filter(
            session_id=session_id,
            user=request.user,
            is_correct=True
        ).count()
        
        session.questions_answered = total_responses
        session.correct_answers = correct_responses
        
        # Verificar si completó todas las preguntas
        total_questions_in_session = 5  # Por defecto para ICFES
        
        if total_responses >= total_questions_in_session:
            session.is_completed = True
            session.completion_time = timezone.now()
            
            # Calcular XP
            xp_per_correct = 10
            bonus_xp = 5 if correct_responses == total_questions_in_session else 0
            total_xp = (correct_responses * xp_per_correct) + bonus_xp
            
            session.xp_earned = total_xp
            print(f"🏆 Sesión completada! XP: {total_xp}")
        
        session.save()
        print(f"📊 Progreso actualizado: {total_responses}/{total_questions_in_session}")
        
        return Response({
            'success': True,
            'is_correct': is_correct,
            'correct_answer': correct_option.option_letter,
            'progress': {
                'current': total_responses,
                'total': total_questions_in_session,
                'percentage': (total_responses / total_questions_in_session) * 100
            },
            'is_completed': session.is_completed,
            'xp_earned': session.xp_earned if session.is_completed else 0
        })
        
    except UserICFESSession.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Sesión no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Question.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Pregunta no encontrada'
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

print("✅ Función submit_answer reemplazada exitosamente") 