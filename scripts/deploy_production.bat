@echo off
REM Auto deployment script for Django project (Windows)
REM Usage: scripts\deploy_production.bat

REM 1. Activate virtualenv
IF NOT EXIST .venv (
    python -m venv .venv
)
CALL .venv\Scripts\activate.bat

REM 2. Install requirements
pip install -r requirements.txt

REM 3. Apply migrations
python manage.py migrate --settings=settings_production

REM 4. Collect static files
python manage.py collectstatic --noinput --settings=settings_production

REM 5. (Optional) Create superuser
REM python manage.py createsuperuser --settings=settings_production

REM 6. Start Gunicorn (if installed)
IF EXIST .venv\Scripts\gunicorn.exe (
    .venv\Scripts\gunicorn.exe ecommerce.wsgi:application --bind 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=settings_production
) ELSE (
    echo Run Gunicorn manually or use another WSGI server.
)
