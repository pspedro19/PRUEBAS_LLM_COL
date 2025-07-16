"""
Serializers para autenticación y gestión de usuarios
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, School, University


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer para instituciones educativas"""
    
    class Meta:
        model = School
        fields = ['id', 'code', 'name', 'city', 'department', 'school_type']


class UniversitySerializer(serializers.ModelSerializer):
    """Serializer para universidades"""
    
    class Meta:
        model = University
        fields = ['id', 'code', 'name', 'city', 'min_icfes_score']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de usuario"""
    
    accuracy = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = [
            'total_questions_answered', 'total_correct_answers', 
            'total_study_minutes', 'current_streak', 'max_streak',
            'current_vitality', 'learning_style', 'difficulty_preference',
            'average_response_time', 'improvement_rate', 'accuracy'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer para información básica del usuario"""
    
    profile = UserProfileSerializer(read_only=True)
    school_info = SchoolSerializer(source='school', read_only=True)
    university_info = UniversitySerializer(source='target_university', read_only=True)
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'uuid', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'birth_date', 'grade', 'target_career',
            'hero_class', 'level', 'experience_points', 'avatar_evolution_stage',
            'initial_assessment_completed', 'vocational_test_completed',
            'assigned_role', 'last_activity', 'display_name',
            'profile', 'school_info', 'university_info'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    school_id = serializers.IntegerField(required=False, allow_null=True)
    target_university_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'birth_date',
            'identification_number', 'grade', 'target_career',
            'school_id', 'target_university_id'
        ]
    
    def validate_email(self, value):
        """Validar que el email no esté en uso"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def validate_username(self, value):
        """Validar que el username no esté en uso"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value
    
    def validate_identification_number(self, value):
        """Validar que el número de identificación no esté en uso"""
        if value and User.objects.filter(identification_number=value).exists():
            raise serializers.ValidationError("Este número de identificación ya está registrado.")
        return value
    
    def validate(self, attrs):
        """Validaciones adicionales"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        
        # Validar grado
        grade = attrs.get('grade')
        if grade and (grade < 9 or grade > 11):
            raise serializers.ValidationError("El grado debe estar entre 9 y 11.")
        
        return attrs
    
    def create(self, validated_data):
        """Crear usuario con perfil"""
        # Remover campos que no son del modelo User
        validated_data.pop('password_confirm')
        school_id = validated_data.pop('school_id', None)
        target_university_id = validated_data.pop('target_university_id', None)
        password = validated_data.pop('password')
        
        # Asignar escuela y universidad si se proporcionaron
        if school_id:
            try:
                validated_data['school'] = School.objects.get(id=school_id)
            except School.DoesNotExist:
                raise serializers.ValidationError("La escuela seleccionada no existe.")
        
        if target_university_id:
            try:
                validated_data['target_university'] = University.objects.get(id=target_university_id)
            except University.DoesNotExist:
                raise serializers.ValidationError("La universidad seleccionada no existe.")
        
        # Crear usuario
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Crear perfil automáticamente
        UserProfile.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login de usuarios"""
    
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validar credenciales de login"""
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')
        
        if not username_or_email or not password:
            raise serializers.ValidationError("Username/email y contraseña son requeridos.")
        
        # Intentar autenticar por username o email
        user = None
        
        # Primero intentar por username
        if User.objects.filter(username=username_or_email).exists():
            user = authenticate(username=username_or_email, password=password)
        
        # Si no encontró por username, intentar por email
        if not user:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if not user:
            raise serializers.ValidationError("Credenciales inválidas.")
        
        if not user.is_active:
            raise serializers.ValidationError("Esta cuenta está desactivada.")
        
        attrs['user'] = user
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para JWT tokens"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar información personalizada al token
        token['username'] = user.username
        token['email'] = user.email
        token['hero_class'] = user.hero_class
        token['level'] = user.level
        token['is_staff'] = user.is_staff
        
        return token
    
    def validate(self, attrs):
        # Permitir login por email o username
        username_or_email = attrs.get('username')
        password = attrs.get('password')
        
        # Intentar encontrar usuario por email si no es username
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass
        
        data = super().validate(attrs)
        
        # Agregar información del usuario a la respuesta
        data['user'] = UserSerializer(self.user).data
        
        return data


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña"""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """Validar contraseña actual"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value
    
    def validate(self, attrs):
        """Validar que las nuevas contraseñas coincidan"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden.")
        return attrs
    
    def save(self):
        """Cambiar la contraseña"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar información del usuario"""
    
    school_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    target_university_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'birth_date',
            'grade', 'target_career', 'avatar_config', 'notification_preferences',
            'study_schedule', 'preferred_language', 'school_id', 'target_university_id'
        ]
    
    def update(self, instance, validated_data):
        """Actualizar usuario con relaciones"""
        school_id = validated_data.pop('school_id', None)
        target_university_id = validated_data.pop('target_university_id', None)
        
        # Actualizar escuela si se proporciona
        if school_id is not None:
            if school_id:
                try:
                    instance.school = School.objects.get(id=school_id)
                except School.DoesNotExist:
                    raise serializers.ValidationError("La escuela seleccionada no existe.")
            else:
                instance.school = None
        
        # Actualizar universidad objetivo si se proporciona
        if target_university_id is not None:
            if target_university_id:
                try:
                    instance.target_university = University.objects.get(id=target_university_id)
                except University.DoesNotExist:
                    raise serializers.ValidationError("La universidad seleccionada no existe.")
            else:
                instance.target_university = None
        
        # Actualizar otros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance 