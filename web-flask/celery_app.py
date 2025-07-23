from celery import Celery

celery = Celery(
    'your_project',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

from celery_tasks import coap_task
__all__ = ['celery']
