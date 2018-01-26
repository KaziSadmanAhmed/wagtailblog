from __future__ import absolute_import, unicode_literals

import os

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "supersecretkey"


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(", ")

try:
    from .local import *
except ImportError:
    pass
