@echo off
REM MySQL setup script for E-Commerce_Arkanzax_KN
REM Usage: scripts\setup_mysql.bat

set MYSQL_ROOT_PASSWORD=root
set DB_NAME=ecommerce_db
set DB_USER=ecommerce_user
set DB_PASS=ecommerce_pass

REM Create database and user
mysql -u root -p%MYSQL_ROOT_PASSWORD% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME% CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS '%DB_USER%'@'localhost' IDENTIFIED BY '%DB_PASS%'; GRANT ALL PRIVILEGES ON %DB_NAME%.* TO '%DB_USER%'@'localhost'; FLUSH PRIVILEGES;"

echo MySQL database and user created.
