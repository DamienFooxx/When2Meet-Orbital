import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main.settings')

app = Celery('Main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
