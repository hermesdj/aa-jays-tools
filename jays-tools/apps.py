from django.apps import AppConfig

from . import __version__


class JaysToolsConfig(AppConfig):
    name = "jays-tools"
    label = "jays-tools"
    verbose_name = f"Jay's Army Tools v{__version__}"