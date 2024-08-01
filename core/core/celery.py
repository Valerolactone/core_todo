from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.celery")
app = Celery('core')
app.autodiscover_tasks([])
