from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile
from apps.analytics.models import LearningAnalytics

@receiver(post_save, sender=User)
def create_user_profile_and_analytics(sender, instance, created, **kwargs):
    if created:
        # Usar get_or_create para evitar duplicados
        UserProfile.objects.get_or_create(user=instance)
        LearningAnalytics.objects.get_or_create(user=instance) 