"""Celery application configuration."""
from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "shangji",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.ocr_tasks",
        "app.tasks.llm_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600 * 24,  # 24 hours
    # All tasks use default "celery" queue
    # task_routes={
    #     "app.tasks.ocr_tasks.*": {"queue": "ocr"},
    #     "app.tasks.llm_tasks.*": {"queue": "llm"},
    # },
)

# Optional: Task result backend settings
celery_app.conf.result_backend_transport_options = {
    "master_name": "mymaster",
    "visibility_timeout": 3600,
}

if __name__ == "__main__":
    celery_app.start()
