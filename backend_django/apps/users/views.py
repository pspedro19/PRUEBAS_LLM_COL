"""
Vistas de autenticación y gestión de usuarios
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from .models import User, UserProfile, School, University
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    CustomTokenObtainPairSerializer, PasswordChangeSerializer,
    UserUpdateSerializer, SchoolSerializer, UniversitySerializer,
    UserProfileSerializer
)


class RegisterView(generics.CreateAPIView):
    """Vista para registro de nuevos usuarios"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Registro de usuario",
        description="Crear una nueva cuenta de usuario",
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Serializar usuario completo
        user_serializer = UserSerializer(user)
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'user': user_serializer.data,
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para login con JWT"""
    
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        summary="Login de usuario",
        description="Autenticar usuario y obtener tokens JWT"
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Actualizar última actividad
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid()
            user = serializer.user
            user.last_activity = timezone.now()
            user.save(update_fields=['last_activity'])
            
            response.data['message'] = 'Login exitoso'
        
        return response


class LogoutView(APIView):
    """Vista para logout (blacklist del refresh token)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Logout de usuario",
        description="Cerrar sesión y blacklistear refresh token"
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Logout exitoso'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Error al cerrar sesión'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Vista para ver y actualizar perfil del usuario"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Obtener perfil del usuario",
        description="Obtener información completa del usuario autenticado"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Actualizar perfil del usuario",
        description="Actualizar información del usuario autenticado"
    )
    def patch(self, request, *args, **kwargs):
        serializer = UserUpdateSerializer(
            self.get_object(), 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Retornar usuario completo
        response_serializer = UserSerializer(user)
        return Response({
            'message': 'Perfil actualizado exitosamente',
            'user': response_serializer.data
        })


class PasswordChangeView(APIView):
    """Vista para cambiar contraseña"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Cambiar contraseña",
        description="Cambiar la contraseña del usuario autenticado"
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Contraseña cambiada exitosamente'
        }, status=status.HTTP_200_OK)


class SchoolListView(generics.ListAPIView):
    """Vista para listar instituciones educativas"""
    
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Listar instituciones educativas",
        description="Obtener lista de todas las instituciones educativas disponibles",
        parameters=[
            OpenApiParameter('city', OpenApiTypes.STR, description='Filtrar por ciudad'),
            OpenApiParameter('school_type', OpenApiTypes.STR, description='Filtrar por tipo de institución'),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros opcionales
        city = self.request.query_params.get('city')
        school_type = self.request.query_params.get('school_type')
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        if school_type:
            queryset = queryset.filter(school_type=school_type)
        
        return queryset.order_by('name')


class UniversityListView(generics.ListAPIView):
    """Vista para listar universidades"""
    
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Listar universidades",
        description="Obtener lista de todas las universidades disponibles",
        parameters=[
            OpenApiParameter('city', OpenApiTypes.STR, description='Filtrar por ciudad'),
            OpenApiParameter('min_score', OpenApiTypes.INT, description='Filtrar por puntaje mínimo ICFES'),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros opcionales
        city = self.request.query_params.get('city')
        min_score = self.request.query_params.get('min_score')
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        if min_score:
            try:
                queryset = queryset.filter(min_icfes_score__lte=int(min_score))
            except ValueError:
                pass
        
        return queryset.order_by('name')


class UserStatsView(APIView):
    """Vista para estadísticas del usuario"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Estadísticas del usuario",
        description="Obtener estadísticas de progreso y gamificación del usuario"
    )
    def get(self, request):
        user = request.user
        profile = user.profile
        
        # Regenerar vitalidad
        profile.regenerate_vitality()
        
        # Obtener predicción ICFES más reciente
        latest_prediction = None
        predicted_icfes_score = 0
        try:
            from apps.icfes.models import ICFESPrediction, ICFESResult
            
            # Primero buscar resultado real más reciente
            latest_result = ICFESResult.objects.filter(user=user).order_by('-created_at').first()
            if latest_result:
                predicted_icfes_score = latest_result.global_score
            else:
                # Si no hay resultado real, buscar predicción más reciente
                latest_prediction = ICFESPrediction.objects.filter(user=user).order_by('-prediction_date').first()
                if latest_prediction:
                    predicted_icfes_score = latest_prediction.predicted_global
        except:
            # Si hay error en la importación o consulta, usar valor por defecto
            predicted_icfes_score = 0
        
        # Calcular calabozos completados (basado en preguntas contestadas correctamente)
        # Asumimos que cada "calabozo" tiene aprox 5-10 preguntas
        questions_per_dungeon = 8  # Promedio de preguntas por calabozo
        completed_dungeons = profile.total_correct_answers // questions_per_dungeon
        
        # Calcular nivel real basado en progreso (usuarios nuevos empiezan en 0)
        display_level = user.level
        if profile.total_questions_answered == 0:
            # Usuario nuevo sin preguntas respondidas = Nivel 0
            display_level = 0
        else:
            # Para usuarios con progreso, usar el nivel real del modelo
            display_level = user.level
        
        # Métricas del Dashboard (formato específico para el frontend)
        dashboard_metrics = {
            'torre_level': {
                'current': display_level,
                'max': 100,
                'percentage': (display_level / 100) * 100,
                'label': 'NIVEL TORRE',
                'subtitle': 'Pisos conquistados',
                'description': f'{display_level} / 100',
                'icon': '🏗️',
                'color': '#FFD700'
            },
            'puntos_icfes': {
                'current': predicted_icfes_score,
                'max': 500,
                'percentage': (predicted_icfes_score / 500) * 100 if predicted_icfes_score > 0 else 0,
                'label': 'PUNTOS ICFES',
                'subtitle': 'Puntuación proyectada',
                'description': f'{predicted_icfes_score} / 500',
                'icon': '📊',
                'color': '#39FF14'
            },
            'calabozos': {
                'current': completed_dungeons,
                'max': 100,
                'percentage': min((completed_dungeons / 100) * 100, 100),
                'label': 'CALABOZOS',
                'subtitle': 'Completados',
                'description': f'{completed_dungeons} / 100',
                'icon': '🏰',
                'color': '#FFA500'
            },
            'racha_actual': {
                'current': profile.current_streak,
                'max': 30,
                'percentage': min((profile.current_streak / 30) * 100, 100),
                'label': 'RACHA ACTUAL',
                'subtitle': 'Días consecutivos',
                'description': f'{profile.current_streak} días',
                'icon': '🔥',
                'color': '#9333EA'
            }
        }
        
        stats = {
            'user_info': {
                'username': user.username,
                'hero_class': user.hero_class,
                'level': display_level,  # Usar display_level en lugar de user.level
                'experience_points': user.experience_points,
                'avatar_evolution_stage': user.avatar_evolution_stage,
            },
            'academic_progress': {
                'questions_answered': profile.total_questions_answered,
                'correct_answers': profile.total_correct_answers,
                'accuracy': profile.accuracy,
                'study_minutes': profile.total_study_minutes,
                'current_streak': profile.current_streak,
                'max_streak': profile.max_streak,
            },
            'game_stats': {
                'current_vitality': profile.current_vitality,
                'improvement_rate': profile.improvement_rate,
                'learning_style': profile.learning_style,
                'difficulty_preference': profile.difficulty_preference,
            },
            'assessments': {
                'initial_completed': user.initial_assessment_completed,
                'vocational_completed': user.vocational_test_completed,
                'assigned_role': user.assigned_role,
            },
            # NUEVAS MÉTRICAS DEL DASHBOARD
            'dashboard_metrics': dashboard_metrics,
            'hunter_stats': [
                {
                    'label': dashboard_metrics['torre_level']['label'],
                    'value': str(dashboard_metrics['torre_level']['current']),
                    'maxValue': dashboard_metrics['torre_level']['max'],
                    'currentValue': dashboard_metrics['torre_level']['current'],
                    'color': dashboard_metrics['torre_level']['color'],
                    'icon': dashboard_metrics['torre_level']['icon'],
                    'description': dashboard_metrics['torre_level']['subtitle'],
                    'detail': f'Has conquistado {display_level} pisos de la Torre de Babel.' + 
                            (' ¡Responde preguntas para comenzar a escalar!' if display_level == 0 else ' ¡Sigue escalando!')
                },
                {
                    'label': dashboard_metrics['puntos_icfes']['label'],
                    'value': str(dashboard_metrics['puntos_icfes']['current']),
                    'maxValue': dashboard_metrics['puntos_icfes']['max'],
                    'currentValue': dashboard_metrics['puntos_icfes']['current'],
                    'color': dashboard_metrics['puntos_icfes']['color'],
                    'icon': dashboard_metrics['puntos_icfes']['icon'],
                    'description': dashboard_metrics['puntos_icfes']['subtitle'],
                    'detail': 'Tu puntuación ICFES proyectada basada en tu progreso actual.'
                },
                {
                    'label': dashboard_metrics['calabozos']['label'],
                    'value': str(dashboard_metrics['calabozos']['current']),
                    'maxValue': dashboard_metrics['calabozos']['max'],
                    'currentValue': dashboard_metrics['calabozos']['current'],
                    'color': dashboard_metrics['calabozos']['color'],
                    'icon': dashboard_metrics['calabozos']['icon'],
                    'description': dashboard_metrics['calabozos']['subtitle'],
                    'detail': 'Calabozos numéricos y de comprensión completados exitosamente.'
                },
                {
                    'label': dashboard_metrics['racha_actual']['label'],
                    'value': f"{dashboard_metrics['racha_actual']['current']} días",
                    'maxValue': dashboard_metrics['racha_actual']['max'],
                    'currentValue': dashboard_metrics['racha_actual']['current'],
                    'color': dashboard_metrics['racha_actual']['color'],
                    'icon': dashboard_metrics['racha_actual']['icon'],
                    'description': dashboard_metrics['racha_actual']['subtitle'],
                    'detail': '¡Mantén tu racha diaria para obtener bonificaciones!'
                }
            ]
        }
        
        return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_experience(request):
    """Endpoint para añadir experiencia al usuario"""
    
    try:
        amount = int(request.data.get('amount', 0))
        if amount <= 0:
            return Response({
                'error': 'La cantidad de experiencia debe ser positiva'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.add_experience(amount)
        
        return Response({
            'message': f'Se añadieron {amount} puntos de experiencia',
            'new_level': user.level,
            'new_xp': user.experience_points,
            'hero_class': user.hero_class
        })
    
    except (ValueError, TypeError):
        return Response({
            'error': 'Cantidad de experiencia inválida'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_assessment(request):
    """Endpoint para completar evaluaciones (inicial o vocacional)"""
    
    assessment_type = request.data.get('assessment_type', '')
    assigned_role = request.data.get('assigned_role', '')
    scores = request.data.get('scores', {})
    answers = request.data.get('answers', [])
    method = request.data.get('method', 'survey')  # survey, manual, random
    
    if not assessment_type or not assigned_role:
        return Response({
            'error': 'Faltan datos requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar rol asignado
    valid_roles = ['TANK', 'DPS', 'SUPPORT', 'SPECIALIST']
    if assigned_role not in valid_roles:
        return Response({
            'error': 'Rol asignado inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    try:
        # Actualizar usuario según el tipo de evaluación
        if assessment_type == 'initial':
            user.initial_assessment_completed = True
            user.initial_assessment_date = timezone.now()
        
        elif assessment_type in ['vocational', 'manual_selection']:
            user.vocational_test_completed = True
            user.assigned_role = assigned_role
            
            # ❌ REMOVED: No dar experiencia por evaluaciones vocacionales
            # Las evaluaciones son solo para determinar el rol, no para ganar XP
            # user.add_experience(200)  # Bonus por completar evaluación
        
        user.save()
        
        # Actualizar perfil si existe
        if hasattr(user, 'profile'):
            profile = user.profile
            
            # Si es una evaluación con encuesta, podemos ajustar preferencias
            if method == 'survey' and scores:
                # Determinar estilo de aprendizaje basado en las respuestas
                if scores.get('SUPPORT', 0) >= scores.get('TANK', 0):
                    profile.learning_style = 'Colaborativo'
                elif scores.get('DPS', 0) >= scores.get('SPECIALIST', 0):
                    profile.learning_style = 'Práctico'
                else:
                    profile.learning_style = 'Analítico'
                
                # Ajustar dificultad preferida
                if scores.get('SPECIALIST', 0) > scores.get('DPS', 0):
                    profile.difficulty_preference = 'hard'
                elif scores.get('TANK', 0) > scores.get('SUPPORT', 0):
                    profile.difficulty_preference = 'medium'
                else:
                    profile.difficulty_preference = 'adaptive'
                
                profile.save()
        
        # Respuesta de éxito
        response_data = {
            'message': 'Evaluación completada exitosamente',
            'user_info': {
                'assigned_role': user.assigned_role,
                'hero_class': user.hero_class,
                'level': user.level,
                'experience_points': user.experience_points,
            },
            'assessment_info': {
                'type': assessment_type,
                'method': method,
                'initial_completed': user.initial_assessment_completed,
                'vocational_completed': user.vocational_test_completed,
            }
        }
        
        if scores:
            response_data['scores'] = scores
            
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': f'Error al completar evaluación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_user_progress(request):
    """Actualiza el progreso del usuario después de responder una pregunta"""
    
    user = request.user
    profile = user.profile
    
    # Obtener datos de la pregunta respondida
    is_correct = request.data.get('is_correct', False)
    response_time = request.data.get('response_time', 0)  # En segundos
    difficulty = request.data.get('difficulty', 'MEDIUM')
    area = request.data.get('area', 'MATHEMATICS')
    xp_gained = request.data.get('xp_gained', 10)
    
    try:
        # Actualizar estadísticas básicas
        profile.total_questions_answered += 1
        if is_correct:
            profile.total_correct_answers += 1
            
            # Otorgar XP al usuario
            user.add_experience(xp_gained)
            
            # Consumir vitalidad (solo si responde correctamente usa menos)
            vitality_cost = 2 if is_correct else 5
            profile.consume_vitality(vitality_cost)
        
        # Actualizar tiempo promedio de respuesta
        if profile.total_questions_answered == 1:
            profile.average_response_time = response_time
        else:
            # Promedio ponderado
            total_time = profile.average_response_time * (profile.total_questions_answered - 1)
            profile.average_response_time = (total_time + response_time) / profile.total_questions_answered
        
        # Actualizar racha de estudio
        profile.update_streak()
        
        # Calcular tasa de mejora
        if profile.total_questions_answered >= 10:
            # Comparar últimas 10 respuestas con las 10 anteriores
            recent_accuracy = profile.accuracy
            # Simplificado: asumir mejora si accuracy > 70%
            if recent_accuracy > 70:
                profile.improvement_rate = min(profile.improvement_rate + 0.5, 100.0)
            elif recent_accuracy < 50:
                profile.improvement_rate = max(profile.improvement_rate - 0.2, 0.0)
        
        profile.save()
        
        # Respuesta con estadísticas actualizadas
        new_stats = {
            'xp_gained': xp_gained,
            'new_level': user.level,
            'new_hero_class': user.hero_class,
            'accuracy': profile.accuracy,
            'current_streak': profile.current_streak,
            'vitality_remaining': profile.current_vitality,
            'total_questions': profile.total_questions_answered,
            'improvement_rate': profile.improvement_rate
        }
        
        return Response({
            'success': True,
            'message': 'Progreso actualizado exitosamente',
            'stats': new_stats
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error actualizando progreso: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check para verificar que la API esté funcionando"""
    
    return Response({
        'status': 'OK',
        'message': 'API de usuarios funcionando correctamente',
        'timestamp': timezone.now(),
        'version': '1.0.0'
    })


class CheckUsernameView(APIView):
    """Vista para verificar disponibilidad de username"""
    
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Verificar disponibilidad de username",
        description="Verificar si un username está disponible para registro"
    )
    def post(self, request):
        username = request.data.get('username')
        if not username:
            return Response({
                'error': 'Username es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        is_available = not User.objects.filter(username=username).exists()
        
        return Response({
            'username': username,
            'available': is_available,
            'message': 'Username disponible' if is_available else 'Username ya está en uso'
        })


class CheckEmailView(APIView):
    """Vista para verificar disponibilidad de email"""
    
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Verificar disponibilidad de email",
        description="Verificar si un email está disponible para registro"
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'error': 'Email es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        is_available = not User.objects.filter(email=email).exists()
        
        return Response({
            'email': email,
            'available': is_available,
            'message': 'Email disponible' if is_available else 'Email ya está registrado'
        })


@extend_schema(
    summary="Obtener estadísticas del usuario",
    description="Obtiene las estadísticas actuales del usuario incluyendo XP, nivel y progreso",
    responses={200: {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean'},
            'data': {
                'type': 'object',
                'properties': {
                    'total_xp': {'type': 'integer'},
                    'level': {'type': 'integer'},
                    'hero_class': {'type': 'string'},
                    'xp_for_next_level': {'type': 'integer'},
                    'total_questions_answered': {'type': 'integer'},
                    'accuracy': {'type': 'number'},
                }
            }
        }
    }}
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_stats(request):
    """Obtiene las estadísticas del usuario"""
    print(f"🔍 get_user_stats called for user: {request.user}")
    
    try:
        user = request.user
        print(f"🔍 User details: id={user.id}, username={user.username}, xp={user.experience_points}, level={user.level}")
        
        # Obtener estadísticas básicas
        stats_data = {
            'total_xp': user.experience_points,
            'level': user.level,
            'hero_class': user.get_hero_class_display(),
            'hero_class_code': user.hero_class,
        }
        
        # Calcular XP necesaria para siguiente nivel (simplificado)
        xp_for_next_level = (user.level * 100) - user.experience_points
        if xp_for_next_level < 0:
            xp_for_next_level = 0
        stats_data['xp_for_next_level'] = xp_for_next_level
        
        # Obtener estadísticas de quiz si existen
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                # Contar total de preguntas respondidas
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM respuestas_usuarios_icfes 
                    WHERE user_id = %s
                """, [user.id])
                total_questions = cursor.fetchone()[0] or 0
                
                # Calcular precisión
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM respuestas_usuarios_icfes 
                    WHERE user_id = %s AND es_correcta = true
                """, [user.id])
                correct_answers = cursor.fetchone()[0] or 0
                
                accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
                
                stats_data.update({
                    'total_questions_answered': total_questions,
                    'correct_answers': correct_answers,
                    'accuracy': round(accuracy, 1)
                })
        except Exception as e:
            print(f"Error calculating quiz stats: {e}")
            stats_data.update({
                'total_questions_answered': 0,
                'correct_answers': 0,
                'accuracy': 0
            })
        
        print(f"✅ Returning stats_data: {stats_data}")
        return Response({
            'success': True,
            'data': stats_data
        })
        
    except Exception as e:
        print(f"❌ Error in get_user_stats: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error obteniendo estadísticas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Actualizar XP del usuario",
    description="Añade experiencia al usuario y actualiza nivel si es necesario",
    request={
        'type': 'object',
        'properties': {
            'xp_gained': {'type': 'integer', 'minimum': 1}
        },
        'required': ['xp_gained']
    },
    responses={200: {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean'},
            'data': {
                'type': 'object',
                'properties': {
                    'total_xp': {'type': 'integer'},
                    'level': {'type': 'integer'},
                    'xp_gained': {'type': 'integer'},
                    'level_up': {'type': 'boolean'},
                    'new_level': {'type': 'integer'},
                }
            }
        }
    }}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_user_xp(request):
    """Actualiza la experiencia del usuario"""
    print(f"🔍 update_user_xp called for user: {request.user}")
    print(f"🔍 Request data: {request.data}")
    
    try:
        user = request.user
        xp_gained = request.data.get('xp_gained')
        
        print(f"🔍 XP to add: {xp_gained}")
        
        if not xp_gained or xp_gained <= 0:
            return Response({
                'success': False,
                'message': 'xp_gained debe ser un número positivo'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Guardar nivel actual para detectar level up
        old_level = user.level
        old_xp = user.experience_points
        
        print(f"🔍 Before: level={old_level}, xp={old_xp}")
        
        # Añadir experiencia usando el método del modelo
        user.add_experience(xp_gained)
        user.save()  # ✨ IMPORTANTE: Guardar después de add_experience
        
        print(f"🔍 After: level={user.level}, xp={user.experience_points}")
        
        # Detectar si hubo level up
        level_up = user.level > old_level
        
        response_data = {
            'total_xp': user.experience_points,
            'level': user.level,
            'xp_gained': xp_gained,
            'level_up': level_up,
            'previous_level': old_level,
            'previous_xp': old_xp
        }
        
        if level_up:
            response_data['new_level'] = user.level
            response_data['message'] = f'¡Felicidades! Has subido al nivel {user.level}!'
        
        print(f"✅ Returning response_data: {response_data}")
        
        return Response({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        print(f"❌ Error in update_user_xp: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error actualizando XP: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 