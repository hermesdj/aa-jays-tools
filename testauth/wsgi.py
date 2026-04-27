"""WSGI config for testauth."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testauth.settings_aa4.local")

application = get_wsgi_application()

