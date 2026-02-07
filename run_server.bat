@echo off
cd /d e:\E-Commerce_Arkanzax_KN\ecommerce
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
pause
