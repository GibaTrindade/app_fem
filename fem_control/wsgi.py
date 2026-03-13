"""
WSGI config for fem_control project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from fem_control.env import load_environment

load_environment()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fem_control.settings')

application = get_wsgi_application()
