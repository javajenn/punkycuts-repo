"""
Django settings for punkycuts project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import django_heroku, postman
from os import getenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-lj=l)3ypkdzvq715)9y0s%5ph7_%+h2teutt@^y^i7+ad^!62z'
# for prod VV 
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if DEBUG:
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)

ALLOWED_HOSTS = [
    getenv('APP_HOST'),
    '127.0.0.1'
]

INTERNAL_IPS = [
    '127.0.0.1'
]

CSRF_USE_SESSIONS = True

SITE_ID = 1

LANGUAGES = [
    ('en', 'English')
]

X_FRAME_OPTIONS = 'SAMEORIGIN'

CMS_TEMPLATES = [
    ('home.html', 'Home page template'),
]
# Application definition

INSTALLED_APPS = [
    #'djangocms_admin_style',
    'store_index',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'sekizai',
    'cms',
    'menus',
    'treebeard',
    #'channels',
    #'chat',
    'dj_pagination',
    'postman',
    'rest_framework',
    'PIL'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'dj_pagination.middleware.PaginationMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
]

ROOT_URLCONF = 'punkycuts.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            'C:/Users/jenni/Documents/SCHOOL/Fall2021_LASTSEMESTER!/CAPSTONE/punky-cuts/punkycuts/templates'
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                'django.template.context_processors.i18n'
            ],
        },
    },
]

WSGI_APPLICATION = 'punkycuts.wsgi.application'

# Channels
#ASGI_APPLICATION = "punkycuts.asgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'punky_cuts_db',
        'USER': 'root',
        'PASSWORD': '06911',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
        'TEST': {
            'NAME': 'test_db'
        }
    }
}
# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#True for prod VV
SECURE_SSL_REDIRECT = True 
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    "C:\\Users\\jenni\\Documents\\SCHOOL\\Fall2021_LASTSEMESTER!\\CAPSTONE\\punky-cuts\\punkycuts\\static",
    "C:\\Users\\jenni\\Documents\\SCHOOL\\Fall2021_LASTSEMESTER!\\CAPSTONE\\punky-cuts\\punkycuts\\store_index\\static\\store_index"
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Activate Django-Heroku.
django_heroku.settings(locals())

TEMPLATE_CONTEXT_PROCESSORS = [
    'postman.context_processors.inbox',
    ("django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request")
]

LOGIN_REDIRECT_URL = 'profile'

POSTMAN_AUTO_MODERATE_AS = True

SESSION_COOKIE_SECURE=True 
SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SECURE = True
#CSRF_COOKIE_SAMESITE = None

# EMAIL CONFIG 


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587

#for prod VV
EMAIL_FROM_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# Postman

POSTMAN_DISALLOW_MULTIRECIPIENTS = True
POSTMAN_DISALLOW_COPIES_ON_REPLY = True
POSTMAN_AUTO_MODERATE_AS = True

# twilio 


#for prod VV
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
