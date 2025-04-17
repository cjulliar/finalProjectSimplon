"""
Configuration ASGI pour le projet.

Il expose l'application ASGI comme une variable nommée "application".
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

application = get_asgi_application() 