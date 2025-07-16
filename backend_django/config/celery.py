"""
Configuración de Celery para Ciudadela del Conocimiento ICFES
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('ciudadela_icfes')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configuración de tareas periódicas
from celery.schedules import crontab

app.conf.beat_schedule = {
    # Regenerar vitalidad cada minuto
    'regenerate-vitality': {
        'task': 'apps.gamification.tasks.regenerate_vitality',
        'schedule': crontab(minute='*'),
    },
    # Actualizar predicciones ICFES cada día a las 3 AM
    'update-icfes-predictions': {
        'task': 'apps.icfes.tasks.update_predictions',
        'schedule': crontab(hour=3, minute=0),
    },
    # Limpiar sesiones expiradas cada día
    'cleanup-expired-sessions': {
        'task': 'apps.assessments.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),
    },
    # Enviar notificaciones de recordatorio de estudio
    'send-study-reminders': {
        'task': 'apps.notifications.tasks.send_study_reminders',
        'schedule': crontab(hour=18, minute=0),  # 6 PM todos los días
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 