#!/usr/bin/bash

python manage.py on_run_check
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py create_default_admin
gunicorn wsgi:application --bind "${HOST:-0.0.0.0}:${PORT:-8000}"