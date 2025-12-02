"""
Local development settings override.
This file should NOT be committed to version control.
"""

from .settings import *

# Development overrides
DEBUG = True

# Disable HTTPS redirect for development
SECURE_SSL_REDIRECT = False

# Disable secure cookies for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Disable HSTS for development
SECURE_HSTS_SECONDS = 0

# Relax CSP for development
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")

# Development allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Development database (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development static files
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Development media files
MEDIA_ROOT = BASE_DIR / 'media_dev'

print("\n" + "="*60)
print("⚙️  DEVELOPMENT SETTINGS LOADED")
print("Security settings relaxed for development")
print("="*60 + "\n")