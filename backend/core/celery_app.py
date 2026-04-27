import os
from celery import Celery
from celery.schedules import crontab

# Initialize Celery app
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("crm", broker=REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    task_track_started=True,
    timezone="UTC",
)

# Auto-discover tasks in our services
celery_app.autodiscover_tasks(["services.email.campaigns", "services.email.imap_worker"])

# Configure Periodic Tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "check_imap_replies_every_5_mins": {
        "task": "services.email.imap_worker.check_replies_task",
        "schedule": crontab(minute="*/5"),
    },
}
