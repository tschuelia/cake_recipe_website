"""
WSGI config for baking_softwaredev project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from dj_static import MediaCling

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "baking_softwaredev.settings")


application = MediaCling(get_wsgi_application())
