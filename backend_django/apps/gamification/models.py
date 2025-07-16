"""
Modelos de gamificación para Ciudadela del Conocimiento ICFES
Sistema RPG completo con distritos, academias, ligas y batallas
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
from datetime import timedelta

User = get_user_model()


class District(models.Model):
    """Distritos de la Ciudadela del Conocimiento"""
    
    DISTRICT_TYPES = [
        ('STARTER', 'Distrito Inicial'),
        ('ACADEMIC', 'Distrito Académico'),
        ('ADVANCED', 'Distrito Avanzado'),
        ('ELITE', 'Distrito Élite'),
        ('LEGENDARY', 'Distrito Legendario'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    district_type = models.CharField(max_length=20, choices=DISTRICT_TYPES)
    
    # Requisitos de acceso
    min_level_required = models.IntegerField(default=1)
    min_hero_class = models.CharField(max_length=2, default='F')  # F, E, D, C, B, A, S, S+
    min_icfes_score = models.IntegerField(default=0)
    
    # Visualización
    background_image_url = models.URLField(max_length=500, blank=True, null=True)
    theme_color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    unlock_order = models.IntegerField(default=0)
    
    # Recompensas del distrito
    xp_multiplier = models.FloatField(default=1.0)  # Multiplicador de XP
    vitality_bonus = models.IntegerField(default=0)  # Bonus de vitalidad
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'districts'
        ordering = ['unlock_order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_district_type_display()})"


class Academy(models.Model):
    """Academias dentro de cada distrito"""
    
    ACADEMY_SPECIALTIES = [
        ('MATHEMATICS', 'Academia de Matemáticas'),
        ('READING', 'Academia de Lectura Crítica'),
        ('NATURAL_SCIENCES', 'Academia de Ciencias Naturales'),
        ('SOCIAL_STUDIES', 'Academia de Ciencias Sociales'),
        ('ENGLISH', 'Academia de Inglés'),
        ('GENERAL', 'Academia General'),
        ('ELITE', 'Academia Élite'),
    ]
    
    id = models.AutoField(primary_key=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='academies')
    name = models.CharField(max_length=100)
    description = models.TextField()
    specialty = models.CharField(max_length=20, choices=ACADEMY_SPECIALTIES)
    
    # Configuración de acceso
    max_members = models.IntegerField(default=50)
    entry_fee_coins = models.IntegerField(default=0)
    min_level_required = models.IntegerField(default=1)
    
    # Configuración de líder
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_academies')
    co_leaders = models.ManyToManyField(User, blank=True, related_name='co_led_academies')
    
    # Estadísticas de la academia
    total_members = models.IntegerField(default=0)
    total_xp_earned = models.BigIntegerField(default=0)
    weekly_xp_earned = models.BigIntegerField(default=0)
    academy_level = models.IntegerField(default=1)
    
    # Configuración visual
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    banner_url = models.URLField(max_length=500, blank=True, null=True)
    theme_color = models.CharField(max_length=7, default='#3B82F6')
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_recruiting = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academies'
        ordering = ['district', 'name']
        indexes = [
            models.Index(fields=['district', 'specialty']),
            models.Index(fields=['is_active', 'is_recruiting']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.district.name}"
    
    @property
    def current_members_count(self):
        return self.memberships.filter(is_active=True).count()
    
    def can_join(self, user):
        """Verifica si un usuario puede unirse a la academia"""
        if not self.is_recruiting or not self.is_active:
            return False
        if self.current_members_count >= self.max_members:
            return False
        if user.level < self.min_level_required:
            return False
        return True


class AcademyMembership(models.Model):
    """Membresía de usuarios en academias"""
    
    MEMBERSHIP_ROLES = [
        ('MEMBER', 'Miembro'),
        ('ELDER', 'Veterano'),
        ('CO_LEADER', 'Co-Líder'),
        ('LEADER', 'Líder'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='academy_memberships')
    academy = models.ForeignKey(Academy, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=MEMBERSHIP_ROLES, default='MEMBER')
    
    # Estadísticas del miembro
    contribution_xp = models.BigIntegerField(default=0)
    weekly_contribution_xp = models.BigIntegerField(default=0)
    donation_coins = models.BigIntegerField(default=0)
    
    # Estado
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'academy_memberships'
        unique_together = ['user', 'academy']
        indexes = [
            models.Index(fields=['academy', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} en {self.academy.name} ({self.role})"


class League(models.Model):
    """Sistema de ligas para competencia"""
    
    LEAGUE_TYPES = [
        ('BRONZE', 'Liga de Bronce'),
        ('SILVER', 'Liga de Plata'),
        ('GOLD', 'Liga de Oro'),
        ('PLATINUM', 'Liga de Platino'),
        ('DIAMOND', 'Liga de Diamante'),
        ('MASTER', 'Liga de Maestros'),
        ('GRANDMASTER', 'Liga de Gran Maestros'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    league_type = models.CharField(max_length=20, choices=LEAGUE_TYPES)
    description = models.TextField()
    
    # Configuración de la liga
    min_trophies = models.IntegerField(default=0)
    max_trophies = models.IntegerField(default=1000)
    season_duration_days = models.IntegerField(default=30)
    
    # Recompensas
    weekly_reward_coins = models.IntegerField(default=100)
    weekly_reward_xp = models.IntegerField(default=500)
    season_end_bonus = models.JSONField(default=dict)  # Recompensas por posición final
    
    # Visualización
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    badge_url = models.URLField(max_length=500, blank=True, null=True)
    theme_color = models.CharField(max_length=7, default='#3B82F6')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'leagues'
        ordering = ['min_trophies']
    
    def __str__(self):
        return f"{self.name} ({self.min_trophies}-{self.max_trophies} trofeos)"


class UserLeagueStatus(models.Model):
    """Estado actual de usuario en ligas"""
    
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='league_status')
    current_league = models.ForeignKey(League, on_delete=models.CASCADE)
    
    # Puntuación actual
    current_trophies = models.IntegerField(default=0)
    season_trophies = models.IntegerField(default=0)  # Trofeos ganados esta temporada
    highest_trophies = models.IntegerField(default=0)  # Máximo histórico
    
    # Estadísticas de temporada
    season_wins = models.IntegerField(default=0)
    season_losses = models.IntegerField(default=0)
    season_battles_count = models.IntegerField(default=0)
    
    # Estado
    last_battle_at = models.DateTimeField(blank=True, null=True)
    season_start_at = models.DateTimeField(auto_now_add=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_league_status'
    
    def __str__(self):
        return f"{self.user.username} - {self.current_league.name} ({self.current_trophies} trofeos)"
    
    @property
    def win_rate(self):
        """Calcula la tasa de victorias"""
        if self.season_battles_count == 0:
            return 0.0
        return (self.season_wins / self.season_battles_count) * 100


class Achievement(models.Model):
    """Sistema de logros"""
    
    ACHIEVEMENT_CATEGORIES = [
        ('LEARNING', 'Aprendizaje'),
        ('SOCIAL', 'Social'),
        ('COMPETITIVE', 'Competitivo'),
        ('EXPLORATION', 'Exploración'),
        ('SPECIAL', 'Especial'),
        ('SEASONAL', 'Temporada'),
    ]
    
    ACHIEVEMENT_RARITIES = [
        ('COMMON', 'Común'),
        ('UNCOMMON', 'No Común'),
        ('RARE', 'Raro'),
        ('EPIC', 'Épico'),
        ('LEGENDARY', 'Legendario'),
    ]
    
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=ACHIEVEMENT_CATEGORIES)
    rarity = models.CharField(max_length=20, choices=ACHIEVEMENT_RARITIES)
    
    # Configuración del logro
    requirements = models.JSONField(default=dict)  # Requisitos para obtener el logro
    is_secret = models.BooleanField(default=False)  # Logros ocultos
    is_repeatable = models.BooleanField(default=False)
    
    # Recompensas
    reward_xp = models.IntegerField(default=0)
    reward_coins = models.IntegerField(default=0)
    reward_title = models.CharField(max_length=100, blank=True, null=True)
    reward_items = models.JSONField(default=list)  # Lista de items especiales
    
    # Visualización
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    badge_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    release_date = models.DateTimeField(default=timezone.now)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'achievements'
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['rarity', 'is_secret']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"


class UserAchievement(models.Model):
    """Logros obtenidos por usuarios"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    
    # Detalles del logro
    progress = models.JSONField(default=dict)  # Progreso hacia el logro
    completion_percentage = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'user_achievements'
        unique_together = ['user', 'achievement']
        indexes = [
            models.Index(fields=['user', 'is_completed']),
            models.Index(fields=['achievement', 'completed_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.is_completed else f"{self.completion_percentage:.1f}%"
        return f"{self.user.username} - {self.achievement.name} ({status})"


class Battle(models.Model):
    """Sistema de batallas entre usuarios"""
    
    BATTLE_TYPES = [
        ('FRIENDLY', 'Amistosa'),
        ('RANKED', 'Clasificatoria'),
        ('TOURNAMENT', 'Torneo'),
        ('ACADEMY_WAR', 'Guerra de Academias'),
    ]
    
    BATTLE_STATUS = [
        ('WAITING', 'Esperando'),
        ('IN_PROGRESS', 'En Progreso'),
        ('COMPLETED', 'Completada'),
        ('CANCELLED', 'Cancelada'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Participantes
    challenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battles_as_challenger')
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battles_as_opponent')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='battles_won')
    
    # Configuración de la batalla
    battle_type = models.CharField(max_length=20, choices=BATTLE_TYPES)
    status = models.CharField(max_length=20, choices=BATTLE_STATUS, default='WAITING')
    question_count = models.IntegerField(default=5)
    time_limit_minutes = models.IntegerField(default=10)
    
    # Filtros de preguntas
    subject_filter = models.CharField(max_length=20, blank=True, null=True)  # MATHEMATICS, etc.
    difficulty_filter = models.CharField(max_length=10, blank=True, null=True)  # EASY, MEDIUM, etc.
    
    # Resultados
    challenger_score = models.IntegerField(default=0)
    opponent_score = models.IntegerField(default=0)
    challenger_trophies_change = models.IntegerField(default=0)
    opponent_trophies_change = models.IntegerField(default=0)
    
    # Configuración de recompensas
    winner_xp_reward = models.IntegerField(default=50)
    winner_coins_reward = models.IntegerField(default=25)
    loser_xp_reward = models.IntegerField(default=10)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'battles'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['challenger', 'status']),
            models.Index(fields=['opponent', 'status']),
            models.Index(fields=['battle_type', 'completed_at']),
        ]
    
    def __str__(self):
        return f"Batalla {self.id}: {self.challenger.username} vs {self.opponent.username}"
    
    def is_expired(self):
        """Verifica si la batalla ha expirado"""
        if self.status != 'WAITING':
            return False
        expire_time = self.created_at + timedelta(minutes=30)  # 30 minutos para aceptar
        return timezone.now() > expire_time


class UserCurrency(models.Model):
    """Monedas y recursos del usuario"""
    
    CURRENCY_TYPES = [
        ('COINS', 'Monedas'),
        ('GEMS', 'Gemas'),
        ('TOKENS', 'Tokens Especiales'),
        ('ENERGY', 'Energía'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='currencies')
    currency_type = models.CharField(max_length=10, choices=CURRENCY_TYPES)
    amount = models.BigIntegerField(default=0)
    
    # Límites
    max_amount = models.BigIntegerField(default=999999)
    daily_earned = models.IntegerField(default=0)
    daily_limit = models.IntegerField(default=1000)
    
    # Timestamps
    last_daily_reset = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_currencies'
        unique_together = ['user', 'currency_type']
        indexes = [
            models.Index(fields=['user', 'currency_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_currency_type_display()}: {self.amount}"
    
    def add_amount(self, amount):
        """Añade cantidad verificando límites"""
        from django.utils import timezone
        today = timezone.now().date()
        
        # Reset diario si es necesario
        if self.last_daily_reset < today:
            self.daily_earned = 0
            self.last_daily_reset = today
        
        # Verificar límite diario
        if self.daily_earned + amount > self.daily_limit:
            amount = max(0, self.daily_limit - self.daily_earned)
        
        # Verificar límite máximo
        if self.amount + amount > self.max_amount:
            amount = max(0, self.max_amount - self.amount)
        
        self.amount += amount
        self.daily_earned += amount
        self.save()
        
        return amount


class PowerUp(models.Model):
    """Power-ups y mejoras disponibles"""
    
    POWERUP_TYPES = [
        ('XP_BOOST', 'Aumento XP'),
        ('TIME_FREEZE', 'Congelar Tiempo'),
        ('HINT', 'Pista'),
        ('SHIELD', 'Escudo'),
        ('VITALITY_RESTORE', 'Restaurar Vitalidad'),
        ('DOUBLE_COINS', 'Monedas Dobles'),
    ]
    
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    powerup_type = models.CharField(max_length=20, choices=POWERUP_TYPES)
    
    # Configuración del power-up
    effect_config = models.JSONField(default=dict)  # Configuración específica del efecto
    duration_minutes = models.IntegerField(default=0)  # 0 = instantáneo
    cooldown_minutes = models.IntegerField(default=0)
    
    # Costos
    cost_coins = models.IntegerField(default=0)
    cost_gems = models.IntegerField(default=0)
    
    # Disponibilidad
    is_purchasable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    min_level_required = models.IntegerField(default=1)
    
    # Visualización
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'powerups'
    
    def __str__(self):
        return f"{self.name} ({self.get_powerup_type_display()})"


class UserPowerUp(models.Model):
    """Power-ups en inventario del usuario"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='powerups')
    powerup = models.ForeignKey(PowerUp, on_delete=models.CASCADE)
    
    # Inventario
    quantity = models.IntegerField(default=1)
    
    # Estado de uso
    is_active = models.BooleanField(default=False)
    activated_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    
    acquired_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_powerups'
        unique_together = ['user', 'powerup']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.powerup.name} x{self.quantity}"
    
    def use(self):
        """Usar el power-up"""
        if self.quantity <= 0:
            return False
        
        from django.utils import timezone
        now = timezone.now()
        
        # Verificar cooldown
        if self.last_used_at and self.powerup.cooldown_minutes > 0:
            cooldown_end = self.last_used_at + timedelta(minutes=self.powerup.cooldown_minutes)
            if now < cooldown_end:
                return False
        
        self.quantity -= 1
        self.last_used_at = now
        
        # Si tiene duración, activarlo
        if self.powerup.duration_minutes > 0:
            self.is_active = True
            self.activated_at = now
            self.expires_at = now + timedelta(minutes=self.powerup.duration_minutes)
        
        self.save()
        return True 