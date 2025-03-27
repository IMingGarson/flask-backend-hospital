from celery.schedules import crontab
from app import celery

celery.conf.beat_schedule = {
    'send-notification-every-monday': {
        'task': 'app.tasks.send_periodical_push_notification',
        'schedule': crontab(hour=8, minute=30, day_of_week='mon-fri'),
    }
}