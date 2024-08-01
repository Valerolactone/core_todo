#!/bin/sh
cd core &&
poetry run python manage.py runserver 0.0.0.0:8000 --settings=core.settings.dev &&
poetry run celery -A core worker --loglevel=info &&
poetry run celery -A core beat --loglevel=info
