"""
Signals para la app de contenido educativo
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Avg, Count
from django.utils import timezone

from .models import (
    UserContentProgress, ContentRating, ContentUnit, 
    ContentBookmark, ContentLesson
)


@receiver(post_save, sender=UserContentProgress)
def update_content_unit_metrics(sender, instance, created, **kwargs):
    """Actualiza métricas de la unidad de contenido cuando cambia el progreso"""
    content_unit = instance.content_unit
    
    # Actualizar contador de intentos
    if created:
        content_unit.total_attempts += 1
    
    # Actualizar contador de completados
    if instance.is_completed and 'is_completed' in getattr(instance, '_dirty_fields', {}):
        content_unit.total_completions += 1
    
    # Actualizar tiempo promedio de completitud
    completed_progress = UserContentProgress.objects.filter(
        content_unit=content_unit,
        is_completed=True,
        completion_time_seconds__gt=0
    )
    
    if completed_progress.exists():
        avg_time = completed_progress.aggregate(
            avg_time=Avg('completion_time_seconds')
        )['avg_time']
        content_unit.average_completion_time = avg_time / 60.0 if avg_time else 0.0
    
    content_unit.save(update_fields=[
        'total_attempts', 'total_completions', 'average_completion_time'
    ])


@receiver(post_save, sender=ContentRating)
@receiver(post_delete, sender=ContentRating)
def update_content_unit_rating(sender, instance, **kwargs):
    """Actualiza el rating promedio de la unidad de contenido"""
    content_unit = instance.content_unit
    
    ratings = ContentRating.objects.filter(content_unit=content_unit)
    if ratings.exists():
        avg_rating = ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
        content_unit.average_rating = avg_rating or 0.0
    else:
        content_unit.average_rating = 0.0
    
    content_unit.save(update_fields=['average_rating'])


@receiver(post_save, sender=UserContentProgress)
def update_user_profile_stats(sender, instance, created, **kwargs):
    """Actualiza estadísticas del perfil del usuario"""
    if hasattr(instance.user, 'profile'):
        profile = instance.user.profile
        
        # Actualizar tiempo total de estudio
        total_time = UserContentProgress.objects.filter(
            user=instance.user
        ).aggregate(
            total=Avg('total_time_seconds')
        )['total'] or 0
        
        profile.total_study_minutes = int(total_time / 60)
        profile.save(update_fields=['total_study_minutes'])


@receiver(post_save, sender=UserContentProgress)
def award_xp_for_content_progress(sender, instance, created, **kwargs):
    """Otorga XP al usuario por progreso en contenido"""
    if instance.is_completed and 'is_completed' in getattr(instance, '_dirty_fields', {}):
        # Solo otorgar XP cuando se completa por primera vez
        xp_to_award = instance.content_unit.xp_reward
        instance.user.add_experience(xp_to_award)
        
        # Registrar XP ganado
        instance.xp_earned = xp_to_award
        instance.save(update_fields=['xp_earned'])


@receiver(pre_save, sender=UserContentProgress)
def track_dirty_fields(sender, instance, **kwargs):
    """Rastrea campos que han cambiado para optimizar signals"""
    if instance.pk:
        try:
            original = UserContentProgress.objects.get(pk=instance.pk)
            dirty_fields = []
            
            for field in instance._meta.fields:
                field_name = field.name
                if getattr(instance, field_name) != getattr(original, field_name):
                    dirty_fields.append(field_name)
            
            instance._dirty_fields = dirty_fields
        except UserContentProgress.DoesNotExist:
            instance._dirty_fields = [] 