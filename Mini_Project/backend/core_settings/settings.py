# backend/core_settings/settings.py
# Django settings for core_settings project.

import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))  # Looks for .env in backend/

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-default-secret-key-for-dev')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',  # Add Django Rest Framework
    'rest_framework_simplejwt',
    'api',             # Add your api app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core_settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core_settings.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'student_dashboard_db'),  # Database name
        'USER': os.getenv('DB_USER', 'your_db_user'),         # Your PostgreSQL username
        'PASSWORD': os.getenv('DB_PASSWORD', 'your_db_password'),  # Your PostgreSQL password
        'HOST': os.getenv('DB_HOST', 'localhost'),           # Or IP/hostname if DB is remote
        'PORT': os.getenv('DB_PORT', '5432'),               # Default PostgreSQL port
    }
}

# Media files (User-uploaded content)
MEDIA_URL = '/media/'  # URL prefix for media files
# Define MEDIA_ROOT - where files will be stored on the server filesystem
# Go up one level from BASE_DIR (backend) to the project root
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media_files')

# Ensure the directory exists
os.makedirs(MEDIA_ROOT, exist_ok=True)

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # Optional: Keep SessionAuthentication for the browsable API during development
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # Make endpoints protected by default unless specified otherwise
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),  # How long access tokens are valid
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),     # How long refresh tokens are valid
    "ROTATE_REFRESH_TOKENS": False,  # Set to True if you want a new refresh token each time you use one
    "BLACKLIST_AFTER_ROTATION": False,  # Requires installing simplejwt blacklist app if True
    "UPDATE_LAST_LOGIN": True,  # Update user's last login timestamp on refresh
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv('DJANGO_SECRET_KEY'),  # Use your Django secret key
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),  # Expect "Bearer <token>" in Authorization header
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),  # Not typically used with standard refresh tokens
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),  # Not typically used
}
