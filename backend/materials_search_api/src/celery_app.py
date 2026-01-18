import os
from celery import Celery

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'materials_search',
    broker=redis_url,
    backend=redis_url,
    include=['src.tasks.sync_tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3300,
    worker_prefetch_multiplier=1,
    worker_concurrency=2,
)

celery_app.conf.beat_schedule = {
    'sync-volatile-materials-hourly': {
        'task': 'src.tasks.sync_tasks.sync_volatile_materials',
        'schedule': 3600.0,
    },
    'sync-full-catalog-daily': {
        'task': 'src.tasks.sync_tasks.sync_full_catalog',
        'schedule': 86400.0,
    },
    'cleanup-expired-prices': {
        'task': 'src.tasks.sync_tasks.cleanup_expired_prices',
        'schedule': 21600.0,
    },
}
