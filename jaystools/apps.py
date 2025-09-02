from django.apps import AppConfig

from . import __version__


class JaysToolsConfig(AppConfig):
    name = "jaystools"
    label = "jaystools"
    verbose_name = f"Jay's Army Tools v{__version__}"