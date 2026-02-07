#!/bin/bash
# MySQL setup script for E-Commerce_Arkanzax_KN
# Usage: bash scripts/setup_mysql.sh

# Set these variables as needed
MYSQL_ROOT_PASSWORD="root"
DB_NAME="ecommerce_db"
DB_USER="ecommerce_user"
DB_PASS="ecommerce_pass"

# Create database and user
mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

echo "MySQL database and user created."
