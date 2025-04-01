import warnings
from cryptography.utils import CryptographyDeprecationWarning
from pathlib import Path
import os

# Ignore CryptographyDeprecationWarning
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_vaaj^mn0bka0wj8-hhw*+uv!(j3k!y6c=bn-)_v4zr(!$r-g-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Media configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'novel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'novel.middleware.AutoLogoutMiddleware',
]

ROOT_URLCONF = 'novel_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'novel.context_processors.base_data',
            ],
        },
    },
]

WSGI_APPLICATION = 'novel_project.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'novel_db',
        'ENFORCE_SCHEMA': True,  # Thêm tùy chọn này nếu cần
        'CLIENT': {
            'host': 'mongodb+srv://ngphi039:456123nhp@cluster0.jvf7l.mongodb.net/?retryWrites=true&w=majority',
            'authSource': 'admin',
        },
    }
}

# DJongo SQL Translator
DJONGO_SQL_TRANSLATOR = 'djongo.sql2mongo.SQLTranslator'

# Custom user model
AUTH_USER_MODEL = 'novel.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "iconictk2@gmail.com"
EMAIL_HOST_PASSWORD = "jthh fxnn qout ayld"  

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static", BASE_DIR / "novel/static"]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
