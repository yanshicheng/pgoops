import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pgoops.settings")
pgoops_celery_app = Celery("pgoops_celery")
pgoops_celery_app.config_from_object("django.conf:settings", namespace="CELERY")
pgoops_celery_app.autodiscover_tasks()
