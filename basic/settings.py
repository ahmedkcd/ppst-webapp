import os
from pathlib import Path

# 📁 Project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Secret key (safe for development, replace or secure for production)
SECRET_KEY = 'django-insecure-n6i2@+*zkc%k!rxlquk*jw1#=4t8+9ur2i9b*gu_z14v7$e02s'

# ⚠️ Set to False in production!
DEBUG = True

ALLOWED_HOSTS = []

# 📦 Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # ✅ Your main app
    'basic',
]

# ⚙️ Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 🔗 URL routing
ROOT_URLCONF = 'basic.urls'

# 🧱 Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'basic/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 🐍 WSGI entry point (update if project is named differently)
WSGI_APPLICATION = 'basic.wsgi.application'

# 🗃️ Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 🔐 Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌐 Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 🖼️ Static files (CSS, JS)
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "basic/static"),
]

# 🔐 Redirect unauthenticated users
LOGIN_URL = '/basic/login/'

# 🔧 Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
