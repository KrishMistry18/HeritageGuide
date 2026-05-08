#!/bin/bash
set -e

echo "==> Installing dependencies..."
pip install -r requirements.txt --break-system-packages

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Seeding cities and attractions..."
python manage.py setup_4cities

echo "==> Build complete!"
