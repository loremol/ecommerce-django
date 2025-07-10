#!/bin/sh

echo "Waiting for postgres..."
if [ -n "$DATABASE_URL" ]; then
    echo "Using environment variable DATABASE_URL"
    sql_host="postgres.railway.internal"
else
    echo "Using default docker database URL"
    sql_host="db"
fi


while ! nc -z $sql_host 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py makemigrations accounts products cart orders
python manage.py migrate
gunicorn ecommerce_api.wsgi:application --bind 0.0.0.0:8000
