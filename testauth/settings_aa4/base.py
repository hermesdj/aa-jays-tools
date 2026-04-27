"""Base Django settings for running aa-jays-tools tests."""

import os

from celery.schedules import crontab
from django.contrib import messages

INSTALLED_APPS = [
    "allianceauth",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_celery_beat",
    "bootstrapform",
    "django_bootstrap5",
    "sortedm2m",
    "esi",
    "allianceauth.authentication",
    "allianceauth.services",
    "allianceauth.eveonline",
    "allianceauth.groupmanagement",
    "allianceauth.notifications",
    "allianceauth.thirdparty.navhelper",
    "allianceauth.analytics",
    "allianceauth.menu",
    "allianceauth.theme",
    "allianceauth.theme.darkly",
    "allianceauth.theme.flatly",
    "allianceauth.theme.materia",
    "allianceauth.custom_css",
    "allianceauth.crontab",
    "sri",
]

SRI_ALGORITHM = "sha512"
SECRET_KEY = "test-secret-key"

BROKER_URL = "redis://localhost:6379/0"
CELERYBEAT_SCHEDULER = "allianceauth.crontab.schedulers.OffsetDatabaseScheduler"
CELERYBEAT_SCHEDULE = {
    "esi_cleanup_callbackredirect": {
        "task": "esi.tasks.cleanup_callbackredirect",
        "schedule": crontab(minute="0", hour="*/4"),
    },
    "esi_cleanup_token": {
        "task": "esi.tasks.cleanup_token",
        "schedule": crontab(minute="0", hour="0"),
    },
    "run_model_update": {
        "task": "allianceauth.eveonline.tasks.run_model_update",
        "schedule": crontab(minute="0", hour="*/6"),
    },
}

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "allianceauth.authentication.middleware.UserSettingsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "allianceauth.urls"
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale/"),)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "allianceauth.context_processors.auth_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "allianceauth.wsgi.application"
AUTHENTICATION_BACKENDS = [
    "allianceauth.authentication.backends.StateBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(PROJECT_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MESSAGE_TAGS = {messages.ERROR: "danger error"}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

DEBUG = True
ALLOWED_HOSTS = ["*"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(os.path.join(BASE_DIR, "alliance_auth.sqlite3")),
    },
}

SITE_NAME = "Alliance Auth"
DEFAULT_THEME = "allianceauth.theme.flatly.auth_hooks.FlatlyThemeHook"
DEFAULT_THEME_DARK = "allianceauth.theme.darkly.auth_hooks.DarklyThemeHook"

LOGIN_URL = "auth_login_user"
LOGIN_REDIRECT_URL = "authentication:dashboard"
LOGOUT_REDIRECT_URL = "authentication:dashboard"
LOGIN_TOKEN_SCOPES = ["publicData"]
ACCOUNT_ACTIVATION_DAYS = 1
ESI_API_URL = "https://esi.evetech.net/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "allianceauth": {"handlers": ["console"], "level": "ERROR"},
        "django": {"handlers": ["console"], "level": "ERROR"},
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

