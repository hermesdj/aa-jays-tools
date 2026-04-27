# flake8: noqa

from .base import *

ROOT_URLCONF = "testauth.urls"
WSGI_APPLICATION = "testauth.wsgi.application"
SECRET_KEY = "testauth-local-secret"

STATIC_ROOT = "/var/www/testauth/static/"
SITE_NAME = "testauth"
SITE_URL = "http://127.0.0.1:8000"
CSRF_TRUSTED_ORIGINS = [SITE_URL]
DEBUG = False

INSTALLED_APPS += ["eveuniverse", "jaystools"]

ESI_SSO_CLIENT_ID = "dummy"
ESI_SSO_CLIENT_SECRET = "dummy"
ESI_SSO_CALLBACK_URL = "http://localhost:8000"
ESI_USER_CONTACT_EMAIL = os.environ.get("ESI_USER_CONTACT_EMAIL", "ci@example.com")

REGISTRATION_VERIFY_EMAIL = False
EMAIL_HOST = ""
EMAIL_PORT = 587
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = ""

# Workarounds to suppress warnings in isolated test runs.
LOGGING = None
STATICFILES_DIRS = []
ANALYTICS_DISABLED = True
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

DISCORD_GUILD_ID = "1234567890"
DISCORD_CALLBACK_URL = ""
DISCORD_APP_ID = ""
DISCORD_APP_SECRET = ""
DISCORD_BOT_TOKEN = "test-token"
DISCORD_SYNC_NAMES = False
RECRUIT_CHANNEL_ID = 123456789
RECRUITER_GROUP_ID = 987654321

