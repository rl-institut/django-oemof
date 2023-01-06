"""Settings for django_oemof"""

import pathlib
from django.conf import settings

OEMOF_DIR = pathlib.Path(settings.MEDIA_ROOT) / getattr(settings, "DJANGO_OEMOF_DIR", "oemof")
OEMOF_STATIC_DIR = pathlib.Path(settings.MEDIA_ROOT) / getattr(settings, "DJANGO_OEMOF_STATIC_DIR", "oemof_static")
