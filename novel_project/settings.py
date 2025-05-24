import warnings
from pathlib import Path
import os

# Ignore CryptographyDeprecationWarning
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://avnadmin:AVNS_MwItjpFgLS4GPOMZU8f@pg-2318a3f0-iconictk2-0c57.j.aivencloud.com:12207/novel_db?sslmode=require'
    )
}
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
    'drf_yasg',
    'rest_framework',

]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Renderer để hiển thị tài liệu API
    ),
}

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

# # Database configuration - SỬ DỤNG POSTGRESQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'noveldb',          # Tên database PostgreSQL bạn tạo
#         'USER': 'postgres',          # User PostgreSQL
#         'PASSWORD': '', # Thay bằng mật khẩu của bạn
#         'HOST': 'localhost',         # Hoặc IP server DB
#         'PORT': '5432',              # Port mặc định PostgreSQL
#     }
# }

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
