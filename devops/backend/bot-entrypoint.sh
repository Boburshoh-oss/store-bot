#!/bin/sh

echo 'Waiting for postgres...'

while ! nc -z $DB_HOSTNAME $DB_PORT; do
    sleep 0.1
done

echo 'PostgreSQL started'

cd backend

# Web service migratsiya qilguncha kutish (5 soniya)
echo 'Waiting for migrations to complete...'
sleep 5

# Migratsiyalar bajarilganligini tekshirish
echo 'Checking migrations...'
python manage.py migrate --check || python manage.py migrate

echo 'Starting Telegram bot...'
python bot_runner.py
