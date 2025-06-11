from dotenv import load_dotenv
from decouple import config
load_dotenv()

# Debug settings
DEBUG = True
SECRET_KEY = config("SECRET_KEY")

# Development-specific settings
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Email settings for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files
STATIC_ROOT = 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = 'media'

# Security settings for development
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

# Database settings for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
