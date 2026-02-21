from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'remove_users': {
        'task': 'main.tasks.remove_users',
        'schedule': crontab(minute=0, hour=0),
    },
    'deactivate_users': {
        'task': 'main.tasks.deactivate_users',
        'schedule': crontab(minute=0, hour=0),
    },
    'update_users_sta': {
        'task': 'main.tasks.update_users_sta',
        'schedule': crontab(minute=0, hour=0),
    },
} 