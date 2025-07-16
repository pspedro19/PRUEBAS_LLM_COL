"""
Modelos de Notificaciones para Ciudadela del Conocimiento ICFES
Sistema de mensajes, alertas y comunicación
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class NotificationTemplate(models.Model):
    """Plantillas de notificaciones"""
    
    TEMPLATE_TYPES = [
        ('ACHIEVEMENT', 'Logro Desbloqueado'),
        ('LEVEL_UP', 'Subida de Nivel'),
        ('BATTLE_INVITE', 'Invitación a Batalla'),
        ('BATTLE_RESULT', 'Resultado de Batalla'),
        ('ACADEMY_INVITE', 'Invitación a Academia'),
        ('ACADEMY_NEWS', 'Noticias de Academia'),
        ('STUDY_REMINDER', 'Recordatorio de Estudio'),
        ('EXAM_REMINDER', 'Recordatorio de Examen'),
        ('WEEKLY_REPORT', 'Reporte Semanal'),
        ('FRIEND_ACTIVITY', 'Actividad de Amigos'),
        ('SYSTEM_UPDATE', 'Actualización del Sistema'),
        ('PROMOTION', 'Promoción'),
        ('WELCOME', 'Bienvenida'),
        ('GOAL_PROGRESS', 'Progreso de Objetivos'),
    ]
    
    DELIVERY_CHANNELS = [
        ('IN_APP', 'En la App'),
        ('EMAIL', 'Email'),
        ('PUSH', 'Push Notification'),
        ('SMS', 'SMS'),
        ('WHATSAPP', 'WhatsApp'),
    ]
    
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    
    # Contenido de la plantilla
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    action_button_text = models.CharField(max_length=50, blank=True, null=True)
    action_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Configuración visual
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    color_theme = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    priority_level = models.IntegerField(default=3)  # 1=crítico, 5=info
    
    # Canales de entrega
    supported_channels = models.JSONField(default=list)  # Lista de canales soportados
    default_channel = models.CharField(max_length=10, choices=DELIVERY_CHANNELS, default='IN_APP')
    
    # Configuración de timing
    immediate_send = models.BooleanField(default=True)
    delay_minutes = models.IntegerField(default=0)
    respect_quiet_hours = models.BooleanField(default=True)
    
    # Variables permitidas en template
    allowed_variables = models.JSONField(default=list)  # ['user_name', 'score', 'level']
    
    # Estado
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        indexes = [
            models.Index(fields=['template_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def render(self, variables=None):
        """Renderiza la plantilla con variables"""
        if not variables:
            variables = {}
        
        title = self.title_template
        message = self.message_template
        
        for var, value in variables.items():
            if var in self.allowed_variables:
                title = title.replace(f"{{{var}}}", str(value))
                message = message.replace(f"{{{var}}}", str(value))
        
        return {
            'title': title,
            'message': message,
            'action_button_text': self.action_button_text,
            'action_url': self.action_url,
        }


class Notification(models.Model):
    """Notificaciones para usuarios"""
    
    NOTIFICATION_TYPES = [
        ('INFO', 'Información'),
        ('SUCCESS', 'Éxito'),
        ('WARNING', 'Advertencia'),
        ('ERROR', 'Error'),
        ('ACHIEVEMENT', 'Logro'),
        ('SOCIAL', 'Social'),
        ('REMINDER', 'Recordatorio'),
        ('SYSTEM', 'Sistema'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('SENT', 'Enviada'),
        ('DELIVERED', 'Entregada'),
        ('READ', 'Leída'),
        ('CLICKED', 'Clickeada'),
        ('FAILED', 'Fallida'),
        ('EXPIRED', 'Expirada'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Contenido
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=15, choices=NOTIFICATION_TYPES)
    
    # Configuración visual
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    color_theme = models.CharField(max_length=7, default='#3B82F6')
    
    # Acción
    action_button_text = models.CharField(max_length=50, blank=True, null=True)
    action_url = models.URLField(max_length=500, blank=True, null=True)
    action_data = models.JSONField(default=dict)  # Datos adicionales para la acción
    
    # Estado y tracking
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    priority = models.IntegerField(default=3)  # 1=alta, 5=baja
    
    # Metadata
    template_used = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=10, default='IN_APP')
    source_id = models.CharField(max_length=100, blank=True, null=True)  # ID del evento que la generó
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    clicked_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
    
    def mark_as_read(self):
        """Marca la notificación como leída"""
        if self.status in ['SENT', 'DELIVERED']:
            self.status = 'READ'
            self.read_at = timezone.now()
            self.save()
    
    def mark_as_clicked(self):
        """Marca la notificación como clickeada"""
        if self.status == 'READ':
            self.status = 'clicked'
            self.clicked_at = timezone.now()
            self.save()
    
    @property
    def is_expired(self):
        """Verifica si la notificación ha expirado"""
        return self.expires_at and timezone.now() > self.expires_at


class UserNotificationSettings(models.Model):
    """Configuración de notificaciones por usuario"""
    
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Configuración por tipo de notificación
    achievements_enabled = models.BooleanField(default=True)
    battle_invites_enabled = models.BooleanField(default=True)
    academy_updates_enabled = models.BooleanField(default=True)
    study_reminders_enabled = models.BooleanField(default=True)
    weekly_reports_enabled = models.BooleanField(default=True)
    friend_activity_enabled = models.BooleanField(default=True)
    system_updates_enabled = models.BooleanField(default=True)
    promotions_enabled = models.BooleanField(default=False)
    
    # Configuración por canal
    in_app_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Configuración de horarios
    quiet_hours_enabled = models.BooleanField(default=True)
    quiet_start_time = models.TimeField(default='22:00:00')
    quiet_end_time = models.TimeField(default='08:00:00')
    
    # Configuración de frecuencia
    digest_frequency = models.CharField(
        max_length=10,
        choices=[
            ('IMMEDIATE', 'Inmediato'),
            ('HOURLY', 'Cada Hora'),
            ('DAILY', 'Diario'),
            ('WEEKLY', 'Semanal'),
        ],
        default='IMMEDIATE'
    )
    
    # Preferencias de contacto
    preferred_language = models.CharField(max_length=5, default='es')
    email_address = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_notification_settings'
    
    def __str__(self):
        return f"Configuración de {self.user.username}"
    
    def is_in_quiet_hours(self):
        """Verifica si está en horas de silencio"""
        if not self.quiet_hours_enabled:
            return False
        
        now = timezone.now().time()
        
        if self.quiet_start_time <= self.quiet_end_time:
            # Mismo día (ej: 22:00 - 08:00 del día siguiente)
            return now >= self.quiet_start_time or now <= self.quiet_end_time
        else:
            # Cruza medianoche (ej: 08:00 - 22:00)
            return self.quiet_start_time <= now <= self.quiet_end_time


class AnnouncementGlobal(models.Model):
    """Anuncios globales para todos los usuarios"""
    
    ANNOUNCEMENT_TYPES = [
        ('INFO', 'Información'),
        ('UPDATE', 'Actualización'),
        ('MAINTENANCE', 'Mantenimiento'),
        ('EVENT', 'Evento'),
        ('PROMOTION', 'Promoción'),
        ('EMERGENCY', 'Emergencia'),
    ]
    
    PRIORITY_LEVELS = [
        (1, 'Crítica'),
        (2, 'Alta'),
        (3, 'Media'),
        (4, 'Baja'),
        (5, 'Informativa'),
    ]
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    announcement_type = models.CharField(max_length=15, choices=ANNOUNCEMENT_TYPES)
    priority = models.IntegerField(choices=PRIORITY_LEVELS, default=3)
    
    # Configuración visual
    banner_image_url = models.URLField(max_length=500, blank=True, null=True)
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    color_theme = models.CharField(max_length=7, default='#3B82F6')
    
    # Acción
    action_button_text = models.CharField(max_length=50, blank=True, null=True)
    action_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Configuración de audiencia
    target_audience = models.JSONField(default=dict)  # Filtros de usuarios objetivo
    min_user_level = models.IntegerField(default=1)
    specific_user_groups = models.JSONField(default=list)  # Grupos específicos
    
    # Configuración de publicación
    is_active = models.BooleanField(default=True)
    show_in_banner = models.BooleanField(default=False)  # Mostrar en banner principal
    show_as_popup = models.BooleanField(default=False)   # Mostrar como popup
    
    # Fechas
    publish_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Estadísticas
    views_count = models.IntegerField(default=0)
    clicks_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'announcements_global'
        indexes = [
            models.Index(fields=['is_active', 'publish_at']),
            models.Index(fields=['announcement_type', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_announcement_type_display()})"
    
    @property
    def is_published(self):
        """Verifica si el anuncio está publicado"""
        now = timezone.now()
        return (
            self.is_active and
            self.publish_at <= now and
            (not self.expires_at or self.expires_at > now)
        )


class UserAnnouncementView(models.Model):
    """Registro de visualizaciones de anuncios por usuario"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcement_views')
    announcement = models.ForeignKey(AnnouncementGlobal, on_delete=models.CASCADE, related_name='user_views')
    
    # Tracking
    viewed_at = models.DateTimeField(auto_now_add=True)
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(blank=True, null=True)
    
    # Contexto
    view_source = models.CharField(max_length=50, default='banner')  # banner, popup, list
    device_type = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        db_table = 'user_announcement_views'
        unique_together = ['user', 'announcement']
        indexes = [
            models.Index(fields=['announcement', 'viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} vio {self.announcement.title}"


class MessageThread(models.Model):
    """Hilos de mensajes entre usuarios"""
    
    THREAD_TYPES = [
        ('DIRECT', 'Mensaje Directo'),
        ('ACADEMY', 'Academia'),
        ('BATTLE', 'Batalla'),
        ('GROUP', 'Grupo'),
        ('SUPPORT', 'Soporte'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    thread_type = models.CharField(max_length=10, choices=THREAD_TYPES)
    
    # Participantes
    participants = models.ManyToManyField(User, through='ThreadParticipant')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_threads')
    
    # Configuración
    title = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_muted = models.BooleanField(default=False)
    
    # Contexto
    related_object_type = models.CharField(max_length=50, blank=True, null=True)  # 'academy', 'battle'
    related_object_id = models.IntegerField(blank=True, null=True)
    
    # Metadata
    last_message_at = models.DateTimeField(blank=True, null=True)
    messages_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'message_threads'
        indexes = [
            models.Index(fields=['thread_type', 'is_active']),
            models.Index(fields=['last_message_at']),
        ]
    
    def __str__(self):
        return f"{self.get_thread_type_display()} - {self.title or f'Hilo {self.id}'}"


class ThreadParticipant(models.Model):
    """Participantes en hilos de mensajes"""
    
    PARTICIPANT_ROLES = [
        ('MEMBER', 'Miembro'),
        ('ADMIN', 'Administrador'),
        ('MODERATOR', 'Moderador'),
    ]
    
    id = models.AutoField(primary_key=True)
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=PARTICIPANT_ROLES, default='MEMBER')
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_muted = models.BooleanField(default=False)
    last_read_at = models.DateTimeField(blank=True, null=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'thread_participants'
        unique_together = ['thread', 'user']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} en {self.thread.title or f'Hilo {self.thread.id}'}"


class Message(models.Model):
    """Mensajes dentro de hilos"""
    
    MESSAGE_TYPES = [
        ('TEXT', 'Texto'),
        ('IMAGE', 'Imagen'),
        ('FILE', 'Archivo'),
        ('SYSTEM', 'Sistema'),
        ('ACHIEVEMENT', 'Logro'),
        ('BATTLE_RESULT', 'Resultado de Batalla'),
    ]
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Contenido
    message_type = models.CharField(max_length=15, choices=MESSAGE_TYPES, default='TEXT')
    content = models.TextField()
    
    # Multimedia
    image_url = models.URLField(max_length=500, blank=True, null=True)
    file_url = models.URLField(max_length=500, blank=True, null=True)
    file_name = models.CharField(max_length=200, blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)  # En bytes
    
    # Referencias
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    mentions = models.ManyToManyField(User, blank=True, related_name='mentioned_in_messages')
    
    # Estado
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)  # Datos adicionales del mensaje
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        indexes = [
            models.Index(fields=['thread', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..." 