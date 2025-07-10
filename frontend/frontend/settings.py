"""
Configuration Django pour le projet d'interface bancaire.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Paramètres de sécurité
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Applications tierces
    'rest_framework',
    'rest_framework_simplejwt',
    'crispy_forms',
    'crispy_bootstrap5',
    # Applications du projet
    'dashboard',
    'bank_data',
    'ai_reports',
    'bankapp',  # Dashboard Celery
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Pour servir les fichiers statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dashboard.middleware.AgenceMiddleware',  # Middleware personnalisé pour l'agence
]

ROOT_URLCONF = 'frontend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'frontend.wsgi.application'

# Test de connexion PostgreSQL automatique
def test_postgres_connection():
    """Test la connexion PostgreSQL pour Django."""
    try:
        import psycopg2
    except ImportError:
        logger.info("🐘❌ psycopg2 non disponible - Django utilise SQLite")
        return False
    
    postgres_host = os.environ.get('POSTGRES_HOST')
    postgres_db = os.environ.get('POSTGRES_DB')
    postgres_user = os.environ.get('POSTGRES_USER')
    postgres_password = os.environ.get('POSTGRES_PASSWORD')
    
    if not all([postgres_host, postgres_db, postgres_user, postgres_password]):
        logger.info("🐘➡️🗄️ Variables PostgreSQL manquantes - Django utilise SQLite")
        return False
    
    try:
        # Test de connexion
        conn = psycopg2.connect(
            host=postgres_host,
            database=postgres_db,
            user=postgres_user,
            password=postgres_password,
            connect_timeout=5
        )
        conn.close()
        logger.info(f"🐘✅ Django: Connexion PostgreSQL réussie ({postgres_host})")
        return True
    except Exception as e:
        logger.warning(f"🐘❌ Django: Connexion PostgreSQL échouée: {e}")
        logger.info("🐘➡️🗄️ Django: Basculement automatique vers SQLite")
        return False

# Configuration automatique de la base de données
USE_POSTGRES = os.environ.get('USE_POSTGRES', 'true').lower() == 'true'

if USE_POSTGRES and test_postgres_connection():
    # PostgreSQL disponible
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            'OPTIONS': {
                'connect_timeout': 10,
            },
        }
    }
    DATABASE_TYPE = "PostgreSQL"
    logger.info(f"🐘 Django: Base de données PostgreSQL ({os.environ.get('POSTGRES_HOST')})")
else:
    # SQLite comme fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    DATABASE_TYPE = "SQLite"
    logger.info(f"🗄️ Django: Base de données SQLite ({BASE_DIR / 'db.sqlite3'})")

# Validation du mot de passe
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

# Internationalisation
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Fichiers statiques (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Fichiers média
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Type de champ par défaut pour les clés primaires
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration de Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Configuration du client REST pour l'API
API_URL = os.environ.get('API_URL', 'http://localhost:8001')
# Pour le développement local : http://localhost:8001 (uvicorn direct)
# Pour Docker : http://api:8000 dans le docker-compose.yml
API_SECRET_KEY = os.environ.get('API_SECRET_KEY', 'secret-key-change-in-production')

# Configuration de l'authentification
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Configuration REST Framework pour les appels API
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Configuration de Simple JWT pour l'authentification à l'API
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# Stockage et génération de sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db' 