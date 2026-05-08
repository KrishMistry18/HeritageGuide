#!/bin/bash
set -e

echo "==> Installing dependencies..."
pip install -r requirements.txt --break-system-packages

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Seeding 4 cities with attractions and images..."
python manage.py setup_4cities || echo "Seeding skipped (may already exist)"

echo "==> Build complete!"
