"""
Django settings for clopetracker project.

- Lit les variables depuis .env (via python-decouple)
- SQLite par défaut ; bascule automatique vers DATABASE_URL si défini (dj-database-url)
- Prêt pour un déploiement léger (Whitenoise pour les fichiers statiques)
"""

# ========= Dépendances requises =========
# pip install python-decouple dj-database-url whitenoise
# (et plus tard, si tu passes à Postgres : pip install psycopg2-binary)

from pathlib import Path
from decouple import config
import dj_database_url

# ========= Chemins de base =========
BASE_DIR = Path(__file__).resolve().parent.parent

# ========= Sécurité & debug =========
# SECRET_KEY doit toujours venir du .env (ne JAMAIS commiter une clé réelle ici)
SECRET_KEY = config("SECRET_KEY")

# DEBUG=True en dev ; DEBUG=False en prod
DEBUG = config("DEBUG", cast=bool, default=False)

# Liste des hôtes autorisés (séparés par des virgules dans .env)
ALLOWED_HOSTS = [h.strip() for h in config("ALLOWED_HOSTS", default="").split(",") if h.strip()]

# Origines de confiance pour CSRF (schéma + host + port requis)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in config("CSRF_TRUSTED_ORIGINS", default="").split(",") if o.strip()]

# ========= Applications =========
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps maison
    'accounts.apps.AccountsConfig', 
    'tracker',
]

# ========= Middleware =========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Whitenoise : sert les fichiers statiques en prod sans config Nginx complexe
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========= Routage =========
ROOT_URLCONF = 'clopetracker.urls'

# ========= Templates =========
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # On pointe sur le dossier "templates" à la racine du projet
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,  # cherche aussi dans <app>/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ========= WSGI =========
WSGI_APPLICATION = 'clopetracker.wsgi.application'

# ========= Base de données =========
# Par défaut : SQLite (fichier db.sqlite3).
# Si .env contient DATABASE_URL (ex: Postgres), on bascule automatiquement.
DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,  # pooling des connexions (utile pour Postgres)
        ssl_require=config("DB_SSL_REQUIRED", cast=bool, default=False),  # met True si l’hébergeur DB impose SSL
    )
}

# ========= Validation des mots de passe =========
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========= Internationalisation =========
# On lit langue & fuseau depuis .env ; valeurs par défaut FR/Bruxelles.
LANGUAGE_CODE = config("LANGUAGE_CODE", default="fr-fr")
TIME_ZONE = config("TIME_ZONE", default="Europe/Brussels")
USE_I18N = True
USE_TZ = True  # Stockage en UTC en base, conversion au fuseau local côté app

# ========= Fichiers statiques & médias =========
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]  # dossiers sources (dev)
STATIC_ROOT = BASE_DIR / config("STATIC_ROOT", default="staticfiles")  # cible collectstatic (prod)

# Option Whitenoise (compression & cache-busting)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / config("MEDIA_ROOT", default="media")

# ========= Email (via Gmail SMTP) =========
# ⚠️ Nécessite un mot de passe d’application généré dans Google.
# Toutes les valeurs sont dans ton fichier .env.

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend"
)  
# Par défaut : console backend → affiche les emails dans le terminal (utile en dev)

EMAIL_HOST = config("EMAIL_HOST", default="")
# Serveur SMTP (ici Gmail = smtp.gmail.com)

EMAIL_PORT = config("EMAIL_PORT", cast=int, default=0)
# Port du serveur SMTP (587 avec TLS)

EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=False)
# True → active TLS (recommandé pour Gmail, port 587)

EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
# Ton adresse Gmail (expéditeur)

EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
# Ton mot de passe d’application Gmail (16 caractères générés)

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
# Adresse utilisée par défaut comme expéditeur dans les emails

# ========= Utilisateur =========
# IMPORTANT : tu utilises ton modèle custom accounts.User
AUTH_USER_MODEL = "accounts.User"

# ========= Redirections login/logout =========
LOGIN_REDIRECT_URL = "home"   # après connexion
LOGOUT_REDIRECT_URL = "home"  # après déconnexion
LOGIN_URL = "accounts:login"  # URL de connexion
