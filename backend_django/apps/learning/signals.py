"""
Signals para la app de Learning Paths
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Avg, Count, Sum
from django.utils import timezone

from .models import (
    UserPathEnrollment, UserLessonProgress, LearningPath,
    LearningPathReview, UserPathAchievement, PathAchievement
)


@receiver(post_save, sender=UserPathEnrollment)
def update_learning_path_metrics(sender, instance, created, **kwargs):
    """Actualiza métricas de la ruta de aprendizaje"""
    learning_path = instance.learning_path
    
    if created:
        learning_path.total_enrollments += 1
    
    # Actualizar contador de completados
    if instance.is_completed and 'status' in getattr(instance, '_dirty_fields', {}):
        learning_path.total_completions += 1
    
    # Actualizar tiempo promedio de completitud
    completed_enrollments = UserPathEnrollment.objects.filter(
        learning_path=learning_path,
        status='COMPLETED',
        total_time_minutes__gt=0
    )
    
    if completed_enrollments.exists():
        avg_time = completed_enrollments.aggregate(
            avg_time=Avg('total_time_minutes')
        )['avg_time']
        learning_path.average_completion_time_hours = (avg_time / 60.0) if avg_time else 0.0
    
    learning_path.save(update_fields=[
        'total_enrollments', 'total_completions', 'average_completion_time_hours'
    ])


@receiver(post_save, sender=LearningPathReview)
@receiver(post_delete, sender=LearningPathReview)
def update_learning_path_rating(sender, instance, **kwargs):
    """Actualiza el rating promedio de la ruta de aprendizaje"""
    learning_path = instance.learning_path
    
    reviews = LearningPathReview.objects.filter(learning_path=learning_path)
    if reviews.exists():
        avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        learning_path.average_rating = avg_rating or 0.0
    else:
        learning_path.average_rating = 0.0
    
    learning_path.save(update_fields=['average_rating'])


@receiver(post_save, sender=UserLessonProgress)
def update_enrollment_progress(sender, instance, created, **kwargs):
    """Actualiza el progreso de la inscripción cuando se completa una lección"""
    enrollment = instance.enrollment
    
    # Calcular progreso total
    total_lessons = enrollment.learning_path.units.aggregate(
        total=Count('lessons')
    )['total'] or 0
    
    completed_lessons = UserLessonProgress.objects.filter(
        enrollment=enrollment,
        status__in=['COMPLETED', 'PERFECT']
    ).count()
    
    if total_lessons > 0:
        progress_percentage = (completed_lessons / total_lessons) * 100
        enrollment.progress_percentage = min(progress_percentage, 100.0)
        enrollment.total_lessons_completed = completed_lessons
        
        # Verificar si se completó la ruta
        if enrollment.progress_percentage >= 100.0 and enrollment.status != 'COMPLETED':
            enrollment.status = 'COMPLETED'
            enrollment.completed_at = timezone.now()
        
        enrollment.save(update_fields=[
            'progress_percentage', 'total_lessons_completed', 'status', 'completed_at'
        ])


@receiver(post_save, sender=UserLessonProgress)
def award_xp_for_lesson_completion(sender, instance, created, **kwargs):
    """Otorga XP al usuario por completar lecciones"""
    if instance.status in ['COMPLETED', 'PERFECT'] and 'status' in getattr(instance, '_dirty_fields', {}):
        # Calcular XP a otorgar
        base_xp = instance.path_lesson.xp_reward
        perfect_bonus = instance.path_lesson.perfect_score_bonus if instance.status == 'PERFECT' else 0
        total_xp = base_xp + perfect_bonus
        
        # Otorgar XP al usuario
        instance.user.add_experience(total_xp)
        
        # Actualizar XP en el progreso de la lección
        instance.xp_earned = total_xp
        instance.save(update_fields=['xp_earned'])
        
        # Actualizar XP total en la inscripción
        enrollment = instance.enrollment
        enrollment.total_xp_earned += total_xp
        enrollment.save(update_fields=['total_xp_earned'])


@receiver(post_save, sender=UserPathEnrollment)
def award_completion_bonuses(sender, instance, created, **kwargs):
    """Otorga bonuses por completar rutas de aprendizaje"""
    if instance.status == 'COMPLETED' and 'status' in getattr(instance, '_dirty_fields', {}):
        learning_path = instance.learning_path
        
        # Bonus por completitud
        completion_bonus = learning_path.completion_xp_bonus
        instance.user.add_experience(completion_bonus)
        
        # Verificar si merece bonus de maestría (basado en puntuación promedio)
        if instance.average_score >= 95.0:
            mastery_bonus = learning_path.mastery_xp_bonus
            instance.user.add_experience(mastery_bonus)


@receiver(post_save, sender=UserPathEnrollment)
@receiver(post_save, sender=UserLessonProgress)
def check_path_achievements(sender, instance, **kwargs):
    """Verifica y otorga logros de rutas de aprendizaje"""
    if sender == UserPathEnrollment:
        user = instance.user
        enrollment = instance
    else:  # UserLessonProgress
        user = instance.user
        enrollment = instance.enrollment
    
    # Obtener logros disponibles para la ruta
    achievements = PathAchievement.objects.filter(
        learning_path=enrollment.learning_path,
        is_active=True
    ).exclude(
        id__in=user.path_achievements.values_list('achievement_id', flat=True)
    )
    
    for achievement in achievements:
        if _check_achievement_criteria(user, enrollment, achievement):
            # Otorgar logro
            UserPathAchievement.objects.create(
                user=user,
                achievement=achievement,
                enrollment=enrollment,
                progress_when_earned=enrollment.progress_percentage,
                xp_earned=achievement.xp_reward
            )
            
            # Otorgar XP del logro
            user.add_experience(achievement.xp_reward)


def _check_achievement_criteria(user, enrollment, achievement):
    """Verifica si el usuario cumple los criterios para un logro"""
    criteria = achievement.criteria
    
    if achievement.achievement_type == 'COMPLETION':
        return enrollment.progress_percentage >= criteria.get('completion_percentage', 100)
    
    elif achievement.achievement_type == 'SPEED':
        max_time_hours = criteria.get('max_time_hours', 0)
        actual_time_hours = enrollment.total_time_minutes / 60.0
        return actual_time_hours <= max_time_hours and enrollment.is_completed
    
    elif achievement.achievement_type == 'ACCURACY':
        min_accuracy = criteria.get('min_accuracy', 90)
        return enrollment.average_score >= min_accuracy and enrollment.is_completed
    
    elif achievement.achievement_type == 'STREAK':
        min_streak = criteria.get('min_streak_days', 7)
        return enrollment.current_streak_days >= min_streak
    
    elif achievement.achievement_type == 'PERFECT':
        perfect_lessons = UserLessonProgress.objects.filter(
            enrollment=enrollment,
            status='PERFECT'
        ).count()
        min_perfect = criteria.get('min_perfect_lessons', 5)
        return perfect_lessons >= min_perfect
    
    return False


@receiver(pre_save, sender=UserPathEnrollment)
@receiver(pre_save, sender=UserLessonProgress)
def track_dirty_fields(sender, instance, **kwargs):
    """Rastrea campos que han cambiado para optimizar signals"""
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            dirty_fields = []
            
            for field in instance._meta.fields:
                field_name = field.name
                if getattr(instance, field_name) != getattr(original, field_name):
                    dirty_fields.append(field_name)
            
            instance._dirty_fields = dirty_fields
        except sender.DoesNotExist:
            instance._dirty_fields = [] 