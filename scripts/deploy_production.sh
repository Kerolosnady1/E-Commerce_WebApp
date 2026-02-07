#!/bin/bash
# Auto deployment script for Django project (Linux/macOS)
# Usage: bash scripts/deploy_production.sh

set -e

# 1. Activate virtualenv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    python3 -m venv .venv
    source .venv/bin/activate
fi

# 2. Install requirements
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate --settings=settings_production

# 4. Collect static files
python manage.py collectstatic --noinput --settings=settings_production

# 5. (Optional) Create superuser
# python manage.py createsuperuser --settings=settings_production

# 6. Start Gunicorn
exec gunicorn ecommerce.wsgi:application --bind 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=settings_production
