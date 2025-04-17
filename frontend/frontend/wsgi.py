"""
Configuration WSGI pour le projet.

Il expose l'application WSGI comme une variable nommée "application".
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

application = get_wsgi_application() 