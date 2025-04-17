"""
Vues principales du projet frontend.
"""

import requests
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

logger = logging.getLogger(__name__)

@csrf_protect
def custom_login_view(request):
    """
    Vue personnalisée pour la connexion qui obtient également un jeton JWT
    de l'API FastAPI pour les requêtes futures.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authentification Django
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Obtention du jeton JWT depuis l'API
            try:
                response = requests.post(
                    f"{settings.API_URL}/api/token",
                    data={"username": username, "password": password},
                    timeout=10
                )
                
                if response.status_code == 200:
                    # Stockage du jeton dans la session
                    token_data = response.json()
                    request.session['api_token'] = token_data.get('access_token')
                    logger.info(f"Jeton API obtenu avec succès pour l'utilisateur {username}")
                    return redirect('/')
                else:
                    # Si l'API est en échec mais que l'authentification Django a réussi,
                    # on continue quand même avec un avertissement
                    logger.warning(f"Échec d'obtention du jeton API: {response.status_code}, {response.text}")
                    messages.warning(request, "Connexion réussie, mais des fonctionnalités avancées pourraient ne pas être disponibles.")
                    return redirect('/')
                    
            except requests.RequestException as e:
                logger.error(f"Erreur lors de la communication avec l'API: {str(e)}")
                messages.warning(request, "Connexion réussie, mais la communication avec l'API a échoué.")
                return redirect('/')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'login.html') 