# 🚀 Arkanzax ERP E-Commerce System

A modern Arabic-first ERP & E-Commerce Management Platform built with Django, designed to help businesses manage sales, inventory, customers, permissions, notifications, and operational settings through a unified and professional interface.

## 🌐 Live Demo

**Demo URL:**

```text
https://e-commerce-webapp-ay2l.onrender.com/
NOTE⚠️: This is free hosted web app so you will experience 50 second or more delay while using it.
```

---

# 📖 Overview

Arkanzax ERP is a business management system focused on e-commerce operations, providing a centralized platform for managing different areas of a business from a single dashboard.

The system includes:

- Dashboard & Analytics
- Sales Management
- Customer Management
- Inventory Management
- User Roles & Permissions
- Security Management
- Notifications Center
- Tax Management
- Print Templates
- Language & Localization Settings
- General System Settings

The project follows a scalable Django architecture and provides a modern dark-themed user experience optimized for business workflows.

---

# ✨ Features

## 📊 Dashboard

- Business overview
- Analytics widgets
- Quick navigation
- Operational monitoring

## 💰 Sales Management

- Manage sales records
- Track business transactions
- Customer order management

## 📦 Inventory Management

- Product management
- Inventory tracking
- Stock monitoring

## 👥 Customer Management

- Customer records
- Customer information management
- Sales history review

## 🔐 Users & Permissions

- Role-Based Access Control (RBAC)
- User management
- Permission assignment
- Security controls

## 🔔 Notifications Center

- System alerts
- Business notifications
- User notifications

## ⚙️ Settings System

- General settings
- Language & time settings
- Print templates
- System configurations
- Account settings

---

# 🛠️ Tech Stack

## Backend

- Python
- Django

## Frontend

- HTML5
- CSS3
- JavaScript

## Database

- SQLite (Development)
- MySQL (Production)

## Tools

- Git
- GitHub
- Render

---

# 📁 Project Structure

```text
E-Commerce_WebApp/
│
├── ecommerce/           # Project configuration
├── core/                # Core application logic
├── templates/           # Django templates
├── static/              # Static assets
├── scripts/             # Automation scripts
├── E-Commerce_UI/       # UI prototypes
├── requirements.txt
├── manage.py
└── README.md
```

---

# 📷 Project Preview

## Dashboard

![docs/screenshots/dashboard.png](https://github.com/Kerolosnady1/E-Commerce_WebApp/blob/master/docs/screenshots/dashboard.png?raw=true)


## Inventory Management

![docs/screenshots/inventory.png](https://github.com/Kerolosnady1/E-Commerce_WebApp/blob/master/docs/screenshots/inventory.png?raw=true)

## Sales Management

![docs/screenshots/sales.png]

## Users & Permissions

![docs/screenshots/users.png]

## System Settings

![docs/screenshots/settings.png]

> 🌐 Want to explore the full system?
>
> Visit the live demo:
>
> https://e-commerce-webapp-ay2l.onrender.com/
>
> ⚠️ Note: The application is hosted on Render's free tier, so the initial load may take up to 50 seconds.
``

---

# 🚀 Installation

## 1. Clone Repository

```bash
git clone https://github.com/Kerolosnady1/E-Commerce_WebApp.git

cd E-Commerce_WebApp
```

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

## 3. Activate Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Run Migrations

```bash
python manage.py migrate
```

## 6. Create Super User

```bash
python manage.py createsuperuser
```

## 7. Run Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
or
http://localhost:8000/
```

---

# 🗄️ Database Support

## SQLite (Default)

The project uses SQLite by default for development.

## MySQL (Optional)

Set the following environment variables:

```env
USE_MYSQL=1

MYSQL_DATABASE=ecommerce_db
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

Then run:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

# ⚡ Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key

DEBUG=False

USE_MYSQL=1

MYSQL_DATABASE=ecommerce_db
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

---

# 🎯 Key Highlights

- Arabic-First ERP Design
- Modern Dark Theme UI
- Business-Oriented Workflow
- Inventory Management System
- Sales Management Module
- Customer Management Module
- User Permissions & Security Controls
- Django-Based Architecture
- Production Deployment Ready
- Responsive Interface

---

# 📈 Future Improvements

- REST API Development
- Mobile Application Support
- Docker Support
- CI/CD Integration
- Advanced Analytics
- Multi-Tenant Architecture
- Real-Time Notifications
- Reporting System
- Data Export Features

---

# 🧪 Testing

Run tests using:

```bash
python manage.py test
```

---

# 🚀 Deployment

The application can be deployed on:

- Render
- Railway
- Azure App Service
- DigitalOcean
- AWS
- VPS Servers

---

# 🤝 Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the project
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

### Kerolos Nady

GitHub:
https://github.com/Kerolosnady1

LinkedIn:
https://www.linkedin.com/in/kerolos-farag-3a8378311

---

# ⭐ Support

If you found this project useful, consider giving it a star ⭐ on GitHub.

It helps showcase the project and supports future improvements.
