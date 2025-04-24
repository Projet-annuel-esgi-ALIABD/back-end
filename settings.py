INSTALLED_APPS = [
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = False  # Change this to False for specific origins
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',  # Add your frontend's development URL
    'https://dev-meteo-du-sinj.apps.fgib.fr',  # Add your frontend's production URL
]
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['Content-Type', 'Authorization']

APPEND_SLASH = False  # Disable appending slashes to URLs