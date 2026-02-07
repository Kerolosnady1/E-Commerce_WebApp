# ERP E‑Commerce Arkanzax

An Arabic-first ERP interface for e‑commerce operations, built on Django with a comprehensive set of settings pages, dashboards, and management screens. The UI emphasizes a unified dark theme, consistent component styling, and interactive controls across all major sections of the system.

## Overview

This project contains:

- **Static UI pages** under E-Commerce_UI for design, layout, and interaction prototypes.
- **Django templates** under templates for server-rendered pages.
- **Static assets** under static for CSS/JS.
- **SQLite database** at db.sqlite3 (development).

The system includes core operational modules (sales, customers, inventory, tax, security, notifications) and multiple settings modules (general settings, language & time, account management, print templates, etc.).

## Key UX / UI Features

- **Unified dark theme** using:
  - rgb(15 23 42 / var(--tw-bg-opacity, 1))

- Dashboard
- Sales
- Users & Permissions
- Security & Permissions
- Notifications Center
- Print Templates
- General Settings
- Language & Time

## Project Structure

- ecommerce/ — Project configuration (settings, URLs, WSGI/ASGI)
- static/ — CSS/JS assets
- templates/ — Django HTML templates

## Requirements

- Python 3.10+
- pip

1. Create and activate a virtual environment
2. Install dependencies:
   - pip install -r requirements.txt

### 1) Create virtual environment

- python -m venv .venv
- python3 -m venv .venv

### 2) Activate virtual environment

- Windows (PowerShell):
  - .\.venv\Scripts\Activate.ps1
- Windows (CMD):
  - .\.venv\Scripts\activate.bat
- Linux/macOS:
  - source .venv/bin/activate

### 3) Install dependencies

- Windows/Linux/macOS:
  - pip install -r requirements.txt

### 4) Run migrations and create admin

- Windows/Linux/macOS:
  - python manage.py migrate
  - python manage.py createsuperuser

### 5) Run the server

- Windows/Linux/macOS:
  - python manage.py runserver

## One‑Click Run Scripts

From the project root, use the script that matches your OS:

- Windows (PowerShell):
  - scripts/run_dev.ps1
- Windows (CMD):
  - scripts/run_dev.bat
- Linux/macOS:
  - ./scripts/run_dev.sh

These scripts will:

- Create the virtual environment if missing
- Install requirements
- Run migrations
- Start the Django development server

## Quick Start (SQLite - Recommended for local dev)

1. Create and activate a virtual environment
2. Install dependencies:

- pip install -r requirements.txt

3. Run migrations:

- python manage.py migrate

4. Create an admin user:

- python manage.py createsuperuser

5. Run the server:

- python manage.py runserver

6. Open in browser:

- http://127.0.0.1:8000/

## MySQL (Optional)

If you want to use MySQL instead of SQLite, set the following environment variables before running migrations:

- USE_MYSQL=1
- MYSQL_DATABASE=ecommerce_db
- MYSQL_USER=root
- MYSQL_PASSWORD=your_password
- MYSQL_HOST=127.0.0.1
- MYSQL_PORT=3306

Then run:

- python manage.py migrate
- python manage.py createsuperuser
- python manage.py runserver

## Environment Variables (.env)

You can store your environment values in a .env file (not committed). Example:

- USE_MYSQL=1
- MYSQL_DATABASE=ecommerce_db
- MYSQL_USER=root
- MYSQL_PASSWORD=your_password
- MYSQL_HOST=127.0.0.1
- MYSQL_PORT=3306

## Run (Development)

- Start the Django server:
  - python manage.py runserver
- Open in browser:
  - http://127.0.0.1:8000/

## Production Deployment Example

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Configure environment**

- انسخ `.env.example` إلى `.env` وعدل القيم (خاصة SECRET_KEY, DB info, ALLOWED_HOSTS)

3. **Apply migrations**

```bash
python manage.py migrate --settings=settings_production
```

4. **Collect static files**

```bash
python manage.py collectstatic --settings=settings_production
```

5. **Create superuser**

```bash
python manage.py createsuperuser --settings=settings_production
```

6. **Run with Gunicorn (Linux/macOS)**

```bash
gunicorn ecommerce.wsgi:application --bind 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=settings_production
```

7. **(اختياري) إعداد Nginx لعكس الطلبات إلى Gunicorn**
8. **تأكد من صلاحيات staticfiles/ و mediafiles/**

> يمكنك استخدام أي سيرفر ويب يدعم WSGI (مثل uWSGI أو mod_wsgi)

---

-- The primary design system is the dark theme; keep new components aligned with the same palette.
-- When editing static UI pages, maintain the same typography and component spacing patterns.
-- Use consistent button behaviors (save/reset/preview/toggle) for a cohesive UX.
