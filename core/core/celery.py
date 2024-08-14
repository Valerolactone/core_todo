from __future__ import absolute_import, unicode_literals

import os
import sys

from celery import Celery

# sys.path.remove(os.path.dirname(__file__))


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.celery")
app = Celery('core')
app.autodiscover_tasks([])
