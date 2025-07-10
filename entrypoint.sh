#!/bin/sh

echo "Waiting for postgres..."

    while ! nc -z db 5432; do
      sleep 0.1
    done

echo "PostgreSQL started"

python manage.py makemigrations accounts products cart orders
python manage.py migrate
gunicorn ecommerce_api.wsgi:application --bind 0.0.0.0:8000
