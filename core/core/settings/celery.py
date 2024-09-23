from core.settings.base import *

DEBUG = True

INSTALLED_APPS += [
    "django_celery_beat",
]

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

CELERY_BEAT_SCHEDULE = {
    'send_one_hour_before_the_deadline': {
        'task': 'api.tasks.send_task_deadline_notification',
        'schedule': crontab(minute='*/2'),
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

TEST_EMAIL_FOR_CELERY = os.getenv('FIRST_EMAIL')
TEST_EMAIL_FOR_CELERY_1 = os.getenv('SECOND_EMAIL')

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
