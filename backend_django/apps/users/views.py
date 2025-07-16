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
        
        stats = {
            'user_info': {
                'username': user.username,
                'hero_class': user.hero_class,
                'level': user.level,
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
            }
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
            
            # Dar experiencia por completar la evaluación
            user.add_experience(200)  # Bonus por completar evaluación
        
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