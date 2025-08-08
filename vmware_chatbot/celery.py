# vmware_chatbot/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vmware_chatbot.settings')

app = Celery('vmware_chatbot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()