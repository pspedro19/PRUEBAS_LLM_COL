"""
Modelos de usuarios para Ciudadela del Conocimiento ICFES
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class School(models.Model):
    """Modelo de instituciones educativas"""
    
    SCHOOL_TYPES = [
        ('PUBLIC', 'Público'),
        ('PRIVATE', 'Privado'),
        ('CHARTER', 'Concesión'),
    ]
    
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    school_type = models.CharField(max_length=10, choices=SCHOOL_TYPES)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schools'
        indexes = [
            models.Index(fields=['school_type']),
            models.Index(fields=['city', 'department']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class University(models.Model):
    """Modelo de universidades objetivo"""
    
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    min_icfes_score = models.IntegerField(default=0)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    website = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'universities'
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class User(AbstractUser):
    """Modelo de usuario personalizado con gamificación"""
    
    HERO_CLASSES = [
        ('F', 'Novato F'),
        ('E', 'Bronce E'),
        ('D', 'Bronce D'),
        ('C', 'Plata C'),
        ('B', 'Plata B'),
        ('A', 'Oro A'),
        ('S', 'Platino S'),
        ('S+', 'Diamante S+'),
    ]
    
    ASSIGNED_ROLES = [
        ('TANK', 'Tanque'),
        ('DPS', 'Daño'),
        ('SUPPORT', 'Soporte'),
        ('SPECIALIST', 'Especialista'),
    ]
    
    # UUID para identificación externa
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Información personal
    identification_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # Información académica
    school = models.ForeignKey(School, on_delete=models.SET_NULL, blank=True, null=True)
    grade = models.IntegerField(
        validators=[MinValueValidator(9), MaxValueValidator(11)], 
        blank=True, null=True
    )
    target_university = models.ForeignKey(University, on_delete=models.SET_NULL, blank=True, null=True)
    target_career = models.CharField(max_length=200, blank=True, null=True)
    
    # Estado de gamificación
    hero_class = models.CharField(max_length=2, choices=HERO_CLASSES, default='F')
    level = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    experience_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Estado de evaluación
    initial_assessment_completed = models.BooleanField(default=False)
    initial_assessment_date = models.DateTimeField(blank=True, null=True)
    vocational_test_completed = models.BooleanField(default=False)
    assigned_role = models.CharField(max_length=10, choices=ASSIGNED_ROLES, blank=True, null=True)
    
    # Avatar y personalización (JSON fields)
    avatar_config = models.JSONField(default=dict, blank=True)
    avatar_evolution_stage = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Preferencias (JSON fields)
    notification_preferences = models.JSONField(default=dict, blank=True)
    study_schedule = models.JSONField(default=dict, blank=True)
    preferred_language = models.CharField(max_length=5, default='es')
    
    # Control de actividad
    last_activity = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['hero_class']),
            models.Index(fields=['school']),
            models.Index(fields=['level']),
            models.Index(fields=['is_active', 'last_activity']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.hero_class} - Nivel {self.level})"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def can_level_up(self):
        """Verifica si el usuario puede subir de nivel"""
        from django.conf import settings
        required_xp = settings.GAME_SETTINGS['LEVELS_REQUIRED_FOR_PROMOTION'].get(self.hero_class, 100)
        return self.experience_points >= (required_xp * self.level)
    
    def add_experience(self, amount):
        """Añade experiencia al usuario y verifica level up"""
        self.experience_points += amount
        
        # Verificar si puede subir de nivel
        while self.can_level_up():
            self.level += 1
            
            # Verificar si puede subir de clase
            if self.level >= 10:  # Lógica simplificada
                classes = ['F', 'E', 'D', 'C', 'B', 'A', 'S', 'S+']
                current_index = classes.index(self.hero_class)
                if current_index < len(classes) - 1:
                    self.hero_class = classes[current_index + 1]
                    self.level = 1  # Reset level para nueva clase
        
        self.save()
        return self
    
    @property
    def display_name(self):
        """Nombre para mostrar en la interfaz"""
        return self.get_full_name() or self.username


class UserProfile(models.Model):
    """Perfil extendido del usuario"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Estadísticas de juego
    total_questions_answered = models.IntegerField(default=0)
    total_correct_answers = models.IntegerField(default=0)
    total_study_minutes = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    
    # Vitalidad (energía del juego)
    current_vitality = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_vitality_update = models.DateTimeField(auto_now=True)
    
    # Configuración de personalidad (para IA)
    learning_style = models.CharField(max_length=50, blank=True, null=True)  # Visual, Auditivo, Kinestésico
    difficulty_preference = models.CharField(max_length=20, default='adaptive')  # easy, medium, hard, adaptive
    
    # Métricas de rendimiento
    average_response_time = models.FloatField(default=0.0)  # En segundos
    improvement_rate = models.FloatField(default=0.0)  # Porcentaje
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    @property
    def accuracy(self):
        """Calcula la precisión del usuario"""
        if self.total_questions_answered == 0:
            return 0.0
        return (self.total_correct_answers / self.total_questions_answered) * 100
    
    def regenerate_vitality(self):
        """Regenera vitalidad basada en el tiempo transcurrido"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        time_diff = now - self.last_vitality_update
        minutes_passed = time_diff.total_seconds() / 60
        
        # Regenerar 1 punto de vitalidad por minuto
        vitality_to_add = int(minutes_passed)
        if vitality_to_add > 0:
            self.current_vitality = min(100, self.current_vitality + vitality_to_add)
            self.last_vitality_update = now
            self.save()
        
        return self.current_vitality 