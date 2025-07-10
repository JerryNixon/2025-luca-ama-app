# Backend Structure

This directory contains the Django backend for the Luca AMA application.

## Core Django Files

- `manage.py` - Django management script
- `requirements.txt` - Python dependencies
- `db.sqlite3` - Local SQLite database (development)
- `.env` - Environment variables (not in version control)

## Directory Structure

### `/ama_backend/`
Django project configuration:
- `settings.py` - Application settings and configuration
- `urls.py` - Root URL routing
- `wsgi.py` - WSGI application entry point
- `asgi.py` - ASGI application entry point

### `/api/`
Main application module:
- `models.py` - Database models (User, Event, Question, etc.)
- `views.py` - API endpoints and business logic
- `urls.py` - API URL routing
- `serializers.py` - Data serialization for REST API
- `authentication.py` - Custom authentication logic
- `admin.py` - Django admin configuration
- `migrations/` - Database migration files

### `/scripts/`
Database management and utility scripts:
- `create_test_users.py` - Generate test user accounts
- `populate_db.py` - Populate database with sample data

### `/tests/`
Backend-specific test files:
- `test_connection.py` - Database connectivity tests
- `test_django_connection.py` - Django ORM connection tests

### `/management/`
Database administration scripts:
- `add_auth_source_field.py` - Add authentication source field
- `add_new_fields.py` - Add new database fields
- `admin_user_management.py` - Manage admin users
- `initialize_fields.py` - Initialize database fields
- `reset_all_passwords.py` - Reset user passwords
- `set_password.py` - Set individual user password
- `optimize_fabric_sql.py` - Fabric SQL optimization
- `fix_is_public.py` - Fix public field issues

### `/config/`
Configuration files and certificates:
- `*.pfx` - SSL certificates for Fabric SQL connection

### `/docs/`
Backend-specific documentation:
- `README.md` - Backend documentation (this file)

## Running the Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## Database Configuration

The backend supports both SQLite (development) and Microsoft Fabric SQL (production). Configuration is handled through environment variables in `.env` file.

## Authentication

- Microsoft Entra ID integration
- Custom authentication backend
- JWT token-based API authentication
