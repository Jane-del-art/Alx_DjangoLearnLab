# Social Media API

A Django REST Framework-based Social Media API with user authentication.

## Features

- Custom User Model with additional fields (bio, profile_picture, followers)
- Token-based authentication
- User registration, login, logout
- User profile management
- Follow/Unfollow functionality

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- pip (Python package manager)

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd social_media_api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install django djangorestframework django-cors-headers

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser